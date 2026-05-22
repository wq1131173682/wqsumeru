#!/usr/bin/env node
/**
 * UUMit Skill — Auth Script (Node.js version)
 *
 * Usage:
 *   node auth.js [--platform <type>]   # 发起设备授权并自动轮询；platform 见 API_REFERENCE.md（默认 openclaw）
 *   node auth.js --poll <device_code>  # Poll for approval (called by cron)
 *   node auth.js --wait <device_code>  # Poll until approval, then continue post-auth onboarding
 *   node auth.js --no-wait          # Only print device code and poll command
 *   node auth.js --reset            # Clear credentials and re-auth
 *   node auth.js --cron-active      # Mark cruise schedule as active
 *   node auth.js --cruise-unavailable  # Mark cruise as unavailable
 *   node auth.js --check            # Check existing credentials
 *
 * Design: auth.js polls internally by default so the Agent can continue the
 * post-auth onboarding flow without asking the user to run another command.
 * Hosts that need non-blocking behavior can pass `--no-wait`.
 *
 * Output: JSON to stdout, diagnostics to stderr
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

const BASE_URL = process.env.UUMIT_BASE_URL || 'https://api.uumit.com';
const TIMEOUT = 15000;
const DEFAULT_AUTH_TIMEOUT_SECONDS = 600; // 10 minutes
const CRUISE_INTERVAL_SECONDS = 30 * 60; // 30 minutes

const SKILL_DIR = path.resolve(__dirname, '..');
const AUTH_FILE = path.join(SKILL_DIR, 'memory', 'uumit-auth.json');
const STATE_FILE = path.join(SKILL_DIR, 'memory', 'uumit-state.json');

/** 须与 API_REFERENCE.md「认证与互通」中 `agent_platform_type` 枚举一致 */
const ALLOWED_AGENT_PLATFORM_TYPES = new Set([
  'openclaw',
  'claude_desktop',
  'cursor',
  'custom_mcp',
  'hermes_agent',
]);

const baseUrlObj = new URL(BASE_URL);
const isHttps = baseUrlObj.protocol === 'https:';

function log(msg) {
  console.error(msg);
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function emitJson(payload, error = false) {
  const stream = error ? process.stderr : process.stdout;
  stream.write(JSON.stringify(payload) + '\n');
}

function makeRequest(method, urlPath, headers = null, bodyData = null) {
  return new Promise((resolve, reject) => {
    const url = BASE_URL + urlPath;
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port || (isHttps ? 443 : 80),
      path: urlObj.pathname + urlObj.search,
      method,
      headers: headers || { 'Content-Type': 'application/json' },
      timeout: TIMEOUT,
    };

    const mod = isHttps ? https : http;
    const req = mod.request(options, (res) => {
      const chunks = [];
      res.on('data', (chunk) => chunks.push(chunk));
      res.on('end', () => {
        const raw = Buffer.concat(chunks).toString('utf-8');
        try {
          resolve(JSON.parse(raw));
        } catch (e) {
          reject(new Error(`invalid JSON: ${raw.slice(0, 200)}`));
        }
      });
    });
    req.on('error', (e) => reject(e));
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
    if (bodyData) req.write(bodyData);
    req.end();
  });
}

function apiRequest(method, urlPath, body = null, headers = null) {
  const h = headers || { 'Content-Type': 'application/json' };
  const bodyStr = body ? JSON.stringify(body) : null;
  return makeRequest(method, urlPath, h, bodyStr);
}

/** 解析授权绑定的宿主类型：CLI `--platform` 优先，其次 UUMIT_AGENT_PLATFORM_TYPE，默认 openclaw */
function resolveAgentPlatformType(argv) {
  const platIdx = argv.indexOf('--platform');
  const next = platIdx !== -1 ? argv[platIdx + 1] : '';
  const fromCli = next && !next.startsWith('--') ? next : '';
  const raw = (fromCli || process.env.UUMIT_AGENT_PLATFORM_TYPE || 'openclaw').trim();
  if (ALLOWED_AGENT_PLATFORM_TYPES.has(raw)) return raw;
  log(`警告: agent_platform_type="${raw}" 不在白名单，改用 custom_mcp`);
  return 'custom_mcp';
}

async function deviceAuth(agentPlatformType) {
  const resp = await apiRequest('POST', '/api/v1/auth/device-auth', {
    agent_platform_type: agentPlatformType,
  });
  if (resp.code !== 0) {
    log(`授权失败: ${resp.message}`);
    return null;
  }
  return resp.data;
}

async function pollAuth(deviceCode) {
  const resp = await apiRequest('POST', '/api/v1/auth/device-auth/poll', { device_code: deviceCode });
  const data = resp.data || {};
  const status = data.status || '';
  if (status === 'approved') return { status: 'approved', ...data };
  if (status === 'expired') { log('授权码已过期'); return { status: 'expired' }; }
  if (status === 'denied') { log('用户拒绝授权'); return { status: 'denied' }; }
  return { status: 'pending' }; // still waiting
}

async function handleApprovedAuth(result, agentPlatformType = process.env.UUMIT_AGENT_PLATFORM_TYPE || 'openclaw') {
  const apiKey = result.api_key;
  const userId = result.user_id;
  saveCredentials(apiKey, userId);
  const scheduleRequest = registerCruiseSchedule();
  const mcpRequest = buildMcpRegistrationRequest(apiKey, userId);
  const postAuth = buildPostAuthOnboarding(apiKey, userId, agentPlatformType);
  savePostAuthOnboarding(postAuth);

  log('获取账户信息...');
  let wallet = {};
  let cruise = {};
  let snapshotError = null;
  try {
    ({ wallet, cruise } = await getAccountInfo(apiKey, userId));
  } catch (e) {
    snapshotError = e.message;
    log(`账户快照获取失败，但授权凭证已保存: ${snapshotError}`);
  }
  const ut = (wallet && wallet.ut) || {};
  const profile = (cruise && cruise.profile && cruise.profile.profile) || {};
  return {
    ok: true,
    status: snapshotError ? 'authorized_with_snapshot_error' : 'authorized',
    user_id: userId,
    wallet: { ut },
    profile: {
      nickname: profile.nickname || 'unknown',
      completeness: profile.completeness || 0,
    },
    cruise: {
      registered: true,
      host_schedule_required: true,
      host_schedule_status: 'pending',
      interval_seconds: CRUISE_INTERVAL_SECONDS,
      schedule_name: 'uumit-half-hourly-cruise',
      schedule_request: scheduleRequest,
    },
    mcp_request: mcpRequest,
    schedule_request: scheduleRequest,
    post_auth: postAuth,
    next_actions: postAuth.next_actions,
    snapshot_error: snapshotError,
  };
}

async function waitForApprovedAuth(deviceCode, agentPlatformType) {
  log('正在自动轮询授权状态；无需等待用户回复“已授权”。');
  const startTime = Date.now();
  const expiresMs = DEFAULT_AUTH_TIMEOUT_SECONDS * 1000;
  const intervalMs = 5000;

  while (Date.now() - startTime < expiresMs) {
    const result = await pollAuth(deviceCode);
    if (result.status === 'approved') {
      return handleApprovedAuth(result, agentPlatformType);
    }
    if (result.status === 'expired' || result.status === 'denied') {
      return { ok: false, status: result.status, error: 'authorization_failed' };
    }
    await sleep(intervalMs);
  }
  return { ok: false, error: 'timeout', status: 'expired' };
}

function saveCredentials(apiKey, userId) {
  const dir = path.dirname(AUTH_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(AUTH_FILE, JSON.stringify({
    cached_api_key: apiKey,
    cached_user_id: userId,
    updated_at: new Date().toISOString(),
  }, null, 2), 'utf-8');
  process.env.UUMIT_API_KEY = apiKey;
  process.env.UUMIT_USER_ID = userId;
  log('凭证已保存');
}

function buildCruiseScheduleRequest() {
  return {
    action: 'register_schedule',
    name: 'UUMit 巡航',
    dedupe_key: 'uumit-half-hourly-cruise',
    interval_seconds: CRUISE_INTERVAL_SECONDS,
    run_immediately: false,
    description: 'UUMit 每半小时自动巡航，由 Agent 按 SKILL.md §4.1 执行。',
    agent_prompt: [
      'Run node {UUMIT_SKILL_DIR}/scripts/cruise_tick.js and parse the JSON internally.',
      'Only notify the user when something changed and user attention, confirmation, or delivery is needed.',
      'For pending tasks/orders/transactions, decide whether this Agent can complete the work itself using its available tools, skills, MCP servers, and safe local/public assets.',
      'If the Agent can complete and deliver safely, prepare a concise delivery plan and ask for confirmation before any write, paid action, or external submission.',
      'If the Agent cannot complete safely, explain the blocker and suggest a UUMit route: publish a task, book time, buy a Knowledge Store asset, call a Data Plaza API, or wait for review.',
      'Never expose secrets, private files, shell access, private repositories, browser sessions, or raw local data as a capability or deliverable.',
    ].join(' '),
  };
}

function buildMcpRegistrationRequest(apiKey, userId) {
  return {
    action: 'register_mcp',
    name: 'UUMit',
    url: `${BASE_URL}/mcp/sse`,
    bridge_url: `${BASE_URL}/api/v1/mcp/bridge`,
    headers: {
      'X-Api-Key': apiKey,
      'X-Platform-User-Id': userId,
    },
  };
}

function buildPostAuthOnboarding(apiKey, userId, agentPlatformType) {
  return {
    required: true,
    blocking_after_auth: true,
    final_response_allowed_after: 'monetizable candidate scan is completed and candidate summaries are shown to the user, or a clear scan blocker is reported',
    action: 'continue_post_auth_onboarding',
    description: '授权成功后 Agent 必须在同一工作流继续执行宿主能力与可变现资产扫描、A2A/MCP 接入信息读取；不得只回复“已授权”就停止。扫描只生成隔离候选清单，并输出给用户选择。用户逐项选择并确认后，才可上架知识商店、技能、能力或数据 API。',
    interop_debug_request: {
      action: 'fetch_interop_debug',
      command: `node "${path.join(SKILL_DIR, 'scripts', 'rest_request.js')}" GET /api/v1/interop/debug`,
      endpoint: '/api/v1/interop/debug',
    },
    host_capability_scan_request: {
      action: 'scan_host_capabilities',
      agent_platform_type: agentPlatformType,
      required: true,
      required_before_final_user_reply: true,
      scan_targets: [
        'host_tools',
        'installed_non_basic_skills',
        'mcp_servers',
        'agent_card_or_public_url',
        'safe_workflows',
        'local_documents_metadata',
        'local_reports_metadata',
        'local_templates_metadata',
        'local_datasets_metadata',
        'project_docs_metadata',
        'public_templates_or_datasets',
        'digital_assets_or_templates',
        'credential_backed_account_assets_metadata_only',
      ],
      scan_goal: 'Discover monetizable skills and documents/assets owned by the user, including but not limited to reports, documents, templates, datasets, playbooks, guides, reusable workflows, public APIs, MCP servers, and non-basic agent skills.',
      isolation_policy: {
        metadata_only: true,
        session_scoped_candidates_file: 'memory/sessions/<session_id>/monetizable-candidates.json',
        never_store_secret_values: true,
        require_user_selection_before_publish: true,
        show_candidates_to_user: true,
      },
      basic_skill_filters: [
        'generic_chat',
        'generic_search',
        'local_shell',
        'filesystem_read_write',
        'browser_control',
        'terminal_operations',
        'package_management',
        'git_operations',
        'mcp_bridge_itself',
        'system_or_debug_tools',
        'uumit_skill_self',
      ],
      basic_skill_judgement_rule: 'Agent must judge basic skills by capability boundary, not by name alone. Exclude generic host abilities such as chat, search, shell, filesystem, browser, package/git operations, system/debug helpers, and wrapper-only MCP bridges. Keep only differentiated, user-owned, auditable abilities with a clear buyer value and deliverable boundary.',
      safety_exclusions: [
        'local_shell',
        'private_files',
        'private_repositories',
        'secrets',
        'credentials',
        'passwords',
        'api_keys',
        'cookies',
        'oauth_tokens',
        'private_keys',
        'environment_variables',
        'browser_session',
        'personal_identity_information',
        'contacts_or_chat_history',
        'unredacted_customer_data',
      ],
      candidate_schema: {
        id: '<stable-local-candidate-id>',
        title: '<short user-facing name>',
        type: 'skill|knowledge_store_asset|data_api|capability|workflow|account_asset',
        source: '<host|mcp|local_metadata|public_url|user_provided>',
        suggested_listing_path: 'knowledge_store|skill|capability|data_marketplace|do_not_list',
        summary: '<what can be sold or delivered>',
        buyer_value: '<why someone would pay>',
        deliverable_boundary: '<exact output buyer receives>',
        agent_can_self_complete: true,
        agent_can_self_deliver: true,
        self_completion_reason: '<tools/data/permissions that make it feasible, or blocker>',
        privacy_risk: 'low|medium|high',
        needs_desensitization: false,
        needs_user_file_selection: false,
        suggested_price_ut: '<optional>',
        excluded_reason: '<only when filtered or unsafe>',
      },
      user_output_requirement: 'After scanning, present a short candidate list to the user with title, type, suggested listing path, privacy risk, whether the Agent can self-complete and self-deliver, and next required confirmation. Prefer Knowledge Store for monetizable documents/assets. Do not publish anything automatically.',
      after_scan: 'Show only non-sensitive candidate summaries, filter out basic skills by judgement rule, mark agent_can_self_complete/agent_can_self_deliver for each candidate, and ask the user which discovered capabilities/assets may be listed on UUMit before any publish/register write call.',
    },
    a2a_onboarding_request: {
      action: 'inspect_a2a_and_mcp_entrypoints',
      a2a_url: `${BASE_URL}/a2a`,
      agent_card_url: `${BASE_URL}/.well-known/agent.json`,
      mcp_sse_url: `${BASE_URL}/mcp/sse`,
      mcp_bridge_url: `${BASE_URL}/api/v1/mcp/bridge`,
      auth_headers: {
        'X-Api-Key': apiKey,
        'X-Platform-User-Id': userId,
      },
    },
    publish_options: {
      capabilities_endpoint: '/api/v1/capabilities',
      skills_endpoint: '/api/v1/skills',
      knowledge_store_endpoint: '/api/v1/digital-assets/quick-upload',
      data_apis_endpoint: '/api/v1/data-marketplace/apis',
      require_user_confirmation: true,
      default_document_listing_path: 'knowledge_store',
    },
    next_actions: [
      'register_cruise_schedule_from_schedule_request',
      'register_mcp_from_mcp_request',
      'fetch_interop_debug',
      'scan_host_capabilities',
      'inspect_a2a_and_mcp_entrypoints',
      'present_monetizable_candidate_summaries_to_user',
      'ask_user_which_candidates_to_publish_or_skip',
    ],
  };
}

function savePostAuthOnboarding(postAuth) {
  const dir = path.dirname(STATE_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

  let state = {};
  try {
    if (fs.existsSync(STATE_FILE)) {
      state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
    }
  } catch (e) { /* ignore */ }

  state.post_auth = {
    ...postAuth,
    status: 'pending',
    updated_at: new Date().toISOString(),
  };
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
}

function registerCruiseSchedule() {
  const dir = path.dirname(STATE_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

  let state = {};
  try {
    if (fs.existsSync(STATE_FILE)) {
      state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
    }
  } catch (e) { /* ignore */ }

  const scheduleRequest = buildCruiseScheduleRequest();
  state.cruise = {
    registered: true,
    local_state_registered: true,
    host_schedule_required: true,
    host_schedule_status: 'pending',
    schedule_name: 'UUMit 巡航',
    interval_seconds: CRUISE_INTERVAL_SECONDS,
    schedule_request: scheduleRequest,
    updated_at: new Date().toISOString(),
  };

  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
  log('已生成巡航定时任务注册元信息: 每 30 分钟执行一次。请按 SKILL.md §4.2 用 openclaw cron 注册。');
  return scheduleRequest;
}

function updateCruiseStatus(status) {
  const dir = path.dirname(STATE_FILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

  let state = {};
  try {
    if (fs.existsSync(STATE_FILE)) {
      state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
    }
  } catch (e) { /* ignore */ }

  state.cruise = state.cruise || {};
  state.cruise.host_schedule_status = status;
  state.cruise.updated_at = new Date().toISOString();

  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
  const label = { active: '已激活', unavailable: '不可用' }[status] || status;
  log(`巡航定时任务状态已更新: ${label} (${status})`);
  emitJson({ ok: true, cruise: { host_schedule_status: status } });
}

async function getAccountInfo(apiKey, userId) {
  const headers = {
    'Content-Type': 'application/json',
    'X-Api-Key': apiKey,
    'X-Platform-User-Id': userId,
  };
  const wallet = await apiRequest('GET', '/api/v1/wallet', null, headers);
  const cruise = await apiRequest('GET', '/api/v1/agent/cruise?include=all', null, headers);
  return { wallet: wallet.data || {}, cruise: cruise.data || {} };
}

async function main() {
  log('UUMit 授权流程');

  const args = process.argv.slice(2);

  // --cron-active
  if (args.includes('--cron-active') || args.includes('--cruise-registered')) {
    updateCruiseStatus('active');
    return 0;
  }

  // --cruise-unavailable
  if (args.includes('--cruise-unavailable')) {
    updateCruiseStatus('unavailable');
    return 0;
  }

  // --poll <device_code>
  const pollIdx = args.indexOf('--poll');
  if (pollIdx !== -1 && args[pollIdx + 1]) {
    const deviceCode = args[pollIdx + 1];
    const agentPlatformType = resolveAgentPlatformType(args);
    const result = await pollAuth(deviceCode);
    if (!result) {
      emitJson({ ok: false, status: 'failed', error: 'authorization_not_approved' }, true);
      return 1;
    }
    if (result.status === 'pending') {
      emitJson({ ok: true, status: 'pending' });
      return 0;
    }

    if (result.status === 'approved') {
      const output = await handleApprovedAuth(result, agentPlatformType);
      emitJson(output);
      return 0;
    }

    emitJson({ ok: false, status: result.status, error: 'authorization_failed' }, true);
    return 1;
  }

  // --wait <device_code>
  const waitIdx = args.indexOf('--wait');
  if (waitIdx !== -1 && args[waitIdx + 1]) {
    const deviceCode = args[waitIdx + 1];
    const agentPlatformType = resolveAgentPlatformType(args);
    const output = await waitForApprovedAuth(deviceCode, agentPlatformType);
    if (output.ok === false) {
      emitJson(output, true);
      return 1;
    }
    emitJson(output);
    return 0;
  }

  // --check
  if (args.includes('--check')) {
    if (fs.existsSync(AUTH_FILE)) {
      const auth = JSON.parse(fs.readFileSync(AUTH_FILE, 'utf-8'));
      log(`已有凭证: ${auth.cached_user_id || 'unknown'}`);
      const apiKey = auth.cached_api_key;
      const userId = auth.cached_user_id;
      if (apiKey && userId) {
        try {
          const { wallet, cruise } = await getAccountInfo(apiKey, userId);
          if (wallet && wallet.ut) {
            const agentPlatformType = resolveAgentPlatformType(args);
            const scheduleRequest = registerCruiseSchedule();
            const mcpRequest = buildMcpRegistrationRequest(apiKey, userId);
            const postAuth = buildPostAuthOnboarding(apiKey, userId, agentPlatformType);
            savePostAuthOnboarding(postAuth);
            const ut = wallet.ut || {};
            const profile = (cruise.profile && cruise.profile.profile) || {};
            emitJson({
              ok: true,
              status: 'already_authorized',
              user_id: userId,
              wallet: { ut },
              profile: {
                nickname: profile.nickname || 'unknown',
                completeness: profile.completeness || 0,
              },
              cruise: {
                registered: true,
                host_schedule_required: true,
                host_schedule_status: 'pending',
                interval_seconds: CRUISE_INTERVAL_SECONDS,
                schedule_name: 'uumit-half-hourly-cruise',
                schedule_request: scheduleRequest,
              },
              mcp_request: mcpRequest,
              schedule_request: scheduleRequest,
              post_auth: postAuth,
              next_actions: postAuth.next_actions,
            });
            return 0;
          }
        } catch (e) {
          log(`凭证验证失败: ${e.message}`);
          emitJson({ ok: false, error: 'credential_check_failed' }, true);
          return 1;
        }
      }
    } else {
      log('未找到凭证');
      emitJson({ ok: false, error: 'no_credentials' }, true);
      return 1;
    }
  }

  // --reset / --force / --reauth
  if (args.some(a => ['--reset', '--force', '--reauth'].includes(a))) {
    if (fs.existsSync(AUTH_FILE)) {
      fs.unlinkSync(AUTH_FILE);
      log('已清除旧凭证，开始重新授权');
    }
  }

  // Check existing credentials first (unless --reset was used)
  if (fs.existsSync(AUTH_FILE) && !args.some(a => ['--reset', '--force', '--reauth'].includes(a))) {
    const auth = JSON.parse(fs.readFileSync(AUTH_FILE, 'utf-8'));
    log(`已有凭证: ${auth.cached_user_id || 'unknown'}`);
    log('如需重新授权，请运行 node scripts/auth.js --reset');

    const apiKey = auth.cached_api_key;
    const userId = auth.cached_user_id;
    if (apiKey && userId) {
      try {
        const { wallet, cruise } = await getAccountInfo(apiKey, userId);
        if (wallet && wallet.ut) {
          const agentPlatformType = resolveAgentPlatformType(args);
          const scheduleRequest = registerCruiseSchedule();
          const mcpRequest = buildMcpRegistrationRequest(apiKey, userId);
          const postAuth = buildPostAuthOnboarding(apiKey, userId, agentPlatformType);
          savePostAuthOnboarding(postAuth);
          const ut = wallet.ut || {};
          const profile = (cruise.profile && cruise.profile.profile) || {};
          emitJson({
            ok: true,
            status: 'already_authorized',
            user_id: userId,
            wallet: { ut },
            profile: {
              nickname: profile.nickname || 'unknown',
              completeness: profile.completeness || 0,
            },
            cruise: {
              registered: true,
              host_schedule_required: true,
              host_schedule_status: 'pending',
              interval_seconds: CRUISE_INTERVAL_SECONDS,
              schedule_name: 'uumit-half-hourly-cruise',
              schedule_request: scheduleRequest,
            },
            mcp_request: mcpRequest,
            schedule_request: scheduleRequest,
            post_auth: postAuth,
            next_actions: postAuth.next_actions,
          });
          return 0;
        }
      } catch (e) {
        log(`凭证验证失败: ${e.message}，重新授权`);
      }
    }
  }

  const agentPlatformType = resolveAgentPlatformType(args);

  // Initiate device auth. By default this waits and polls so the Agent can
  // continue post-auth onboarding without a separate user action.
  const authData = await deviceAuth(agentPlatformType);
  if (!authData) {
    emitJson({ ok: false, error: 'device_auth_failed' }, true);
    return 1;
  }

  log('请完成授权:');
  log(`1. 打开: ${authData.verification_url}`);
  log(`2. 输入授权码: ${authData.user_code}`);
  log(`有效期 ${authData.expires_in || DEFAULT_AUTH_TIMEOUT_SECONDS} 秒`);
  log('授权码展示后脚本会自动轮询；Agent 不应结束本轮回复，授权成功后必须继续执行 post_auth.next_actions。');

  const shouldWait = !args.includes('--no-wait') && !args.includes('--code-only');
  if (shouldWait) {
    log('正在等待授权完成 (超时 10 分钟)...');
    const startTime = Date.now();
    const expiresMs = (authData.expires_in || DEFAULT_AUTH_TIMEOUT_SECONDS) * 1000;
    const intervalMs = (authData.interval || 5) * 1000;

    while (Date.now() - startTime < expiresMs) {
      const result = await pollAuth(authData.device_code);
      if (result.status === 'approved') {
        const output = await handleApprovedAuth(result, agentPlatformType);
        emitJson(output);
        return 0;
      }
      if (result.status === 'expired' || result.status === 'denied') {
        emitJson({ ok: false, status: result.status, error: 'authorization_failed' }, true);
        return 1;
      }
      // status: pending
      await sleep(intervalMs);
    }
    log('授权超时');
    emitJson({ ok: false, error: 'timeout', status: 'expired' }, true);
    return 1;
  }

  // Output device code for external polling (cron or manual)
  emitJson({
    ok: true,
    status: 'awaiting_approval',
    agent_platform_type: agentPlatformType,
    device_code: authData.device_code,
    user_code: authData.user_code,
    verification_url: authData.verification_url,
    expires_in: authData.expires_in || DEFAULT_AUTH_TIMEOUT_SECONDS,
    interval: authData.interval || 5,
    auto_poll_required: true,
    agent_must_poll_in_same_turn: true,
    do_not_final_reply_before_polling: true,
    poll_interval_seconds: authData.interval || 5,
    must_continue_post_auth: true,
    next_step: 'Show verification_url and user_code as an interim message only, immediately run poll_command every poll_interval_seconds until authorized, then execute post_auth.next_actions from the poll result before giving a final user reply.',
    interim_user_message_template: '请打开 {verification_url} 并输入授权码 {user_code}。我会在这里自动等待授权完成，然后继续扫描可上架的技能和文档候选。',
    poll_command: `node "${path.join(SKILL_DIR, 'scripts', 'auth.js')}" --poll ${authData.device_code}`,
    wait_command: `node "${path.join(SKILL_DIR, 'scripts', 'auth.js')}" --wait ${authData.device_code}`,
    required_next_command: `node "${path.join(SKILL_DIR, 'scripts', 'auth.js')}" --wait ${authData.device_code}`,
    required_next_command_purpose: 'Run this immediately after showing the code. It blocks and polls automatically until authorization succeeds, then returns post_auth.next_actions.',
  });

  return 0;
}

main().catch(err => {
  emitJson({ ok: false, error: err.message }, true);
  process.exit(1);
});