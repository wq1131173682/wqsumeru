#!/usr/bin/env node
/**
 * UUMit Skill — 巡航 diff 脚本
 *
 * Usage:
 *   node cruise_tick.js [--dry-run] [--state-file FILE]
 *
 * Credentials: env vars UUMIT_API_KEY + UUMIT_USER_ID, or auth file
 * stdout: final JSON; stderr: progress and diagnostics
 */
const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

const BASE_URL = process.env.UUMIT_BASE_URL || 'https://api.uumit.com';
const baseUrlObj = new URL(BASE_URL);
const isHttps = baseUrlObj.protocol === 'https:';
const DEFAULT_STATE_FILE = path.join(__dirname, '..', 'memory', 'cruise-state.json');

function log(msg) { console.error(msg); }

function loadCredentials() {
  let apiKey = process.env.UUMIT_API_KEY || '';
  let userId = process.env.UUMIT_USER_ID || '';
  if (apiKey && userId) return { apiKey, userId };
  const authPath = path.join(__dirname, '..', 'memory', 'uumit-auth.json');
  try {
    if (fs.existsSync(authPath)) {
      const auth = JSON.parse(fs.readFileSync(authPath, 'utf-8'));
      apiKey = auth.cached_api_key || '';
      userId = auth.cached_user_id || '';
    }
  } catch (e) { /* ignore */ }
  return { apiKey, userId };
}

function makeRequest(method, urlPath, headers) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(BASE_URL + urlPath);
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port || (isHttps ? 443 : 80),
      path: urlObj.pathname + urlObj.search,
      method,
      headers,
      timeout: 30000,
    };
    const mod = isHttps ? https : http;
    const req = mod.request(options, (res) => {
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => {
        const raw = Buffer.concat(chunks).toString('utf-8');
        try { resolve({ statusCode: res.statusCode, data: JSON.parse(raw) }); }
        catch (e) { reject(new Error(`invalid JSON: ${raw.slice(0, 200)}`)); }
      });
    });
    req.on('error', (e) => reject(e));
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
    req.end();
  });
}

function readState(stateFile) {
  try {
    if (!fs.existsSync(stateFile)) return {};
    return JSON.parse(fs.readFileSync(stateFile, 'utf-8'));
  } catch (e) {
    return {};
  }
}

function writeState(stateFile, state) {
  const dir = path.dirname(stateFile);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2), 'utf-8');
}

function summarizeSnapshot(data) {
  const profile = data.profile || {};
  const profileInner = profile.profile || {};
  const todos = data.todos || {};
  const tasks = data.tasks || {};
  const wallet = data.wallet || {};
  return {
    profile: {
      nickname: profileInner.nickname || null,
      completeness: profileInner.completeness || 0,
    },
    wallet: {
      ut_available: wallet.ut && wallet.ut.available,
      ut_frozen: wallet.ut && wallet.ut.frozen,
    },
    counts: {
      todos: Array.isArray(todos.items) ? todos.items.length : null,
      active_tasks: Array.isArray(tasks.active) ? tasks.active.length : null,
      pending_transactions: Array.isArray(data.pending_transactions) ? data.pending_transactions.length : null,
    },
  };
}

function diffSummaries(previous, current) {
  const changes = [];
  const keys = [
    ['profile', 'nickname'],
    ['profile', 'completeness'],
    ['wallet', 'ut_available'],
    ['wallet', 'ut_frozen'],
    ['counts', 'todos'],
    ['counts', 'active_tasks'],
    ['counts', 'pending_transactions'],
  ];
  for (const [group, key] of keys) {
    const before = previous[group] && previous[group][key];
    const after = current[group] && current[group][key];
    if (before !== after) {
      changes.push({ field: `${group}.${key}`, before, after });
    }
  }
  return changes;
}

function buildAgentDecisionPrompt(status, changes) {
  if (status === 'initialized' || status === 'unchanged') {
    return 'No user notification is needed unless a separate pending workflow is already active.';
  }
  const changedFields = changes.map(c => c.field).join(', ');
  return [
    `Changed fields: ${changedFields}.`,
    'Review the changed snapshot internally and notify the user only if action is needed.',
    'For each pending task, order, transaction, booking, negotiation, or publish step, decide whether this Agent can complete the work itself and deliver safely.',
    'Self-complete only when required tools/data/permissions are available, the deliverable boundary is clear, no secrets/private files are exposed, and the action is allowed by SKILL.md/SAFETY.md.',
    'If self-completion is feasible, summarize the plan and ask for confirmation before writes, purchases, submissions, or delivery calls.',
    'If not feasible, explain the blocker and offer a UUMit route such as publishing a task, booking time, buying a Knowledge Store asset, calling a Data Plaza API, or waiting for platform review.',
  ].join(' ');
}

function failCli(message) {
  log(JSON.stringify({ error: message }));
  process.exit(2);
}

async function main() {
  const args = process.argv.slice(2);
  let dryRun = false;
  let stateFile = DEFAULT_STATE_FILE;

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--dry-run':
        dryRun = true;
        break;
      case '--state-file':
        if (i + 1 >= args.length || args[i + 1].startsWith('--')) {
          failCli('missing value for --state-file');
        }
        stateFile = args[++i];
        if (!stateFile.trim()) failCli('--state-file cannot be empty');
        break;
      default:
        failCli(`unknown argument: ${args[i]}`);
    }
  }

  const { apiKey, userId } = loadCredentials();
  if (!apiKey || !userId) {
    log(JSON.stringify({ error: 'Credentials not found. Run scripts/auth.js first.' }));
    process.exit(2);
  }

  const headers = {
    'Content-Type': 'application/json',
    'X-Api-Key': apiKey,
    'X-Platform-User-Id': userId,
  };

  log('获取巡航快照...');
  const { statusCode, data } = await makeRequest('GET', '/api/v1/agent/cruise?include=all', headers);
  if (statusCode !== 200 || data.code !== 0) {
    console.log(JSON.stringify({
      ok: false,
      status: 'snapshot_failed',
      error: data.message || `HTTP ${statusCode}`,
      retryable: statusCode >= 500 || statusCode === 429,
    }));
    return;
  }

  const previousState = readState(stateFile);
  const currentSummary = summarizeSnapshot(data.data || {});
  const hasBaseline = Object.prototype.hasOwnProperty.call(previousState, 'summary');
  const previousSummary = previousState.summary || {};
  const changes = hasBaseline ? diffSummaries(previousSummary, currentSummary) : [];
  const status = hasBaseline ? (changes.length ? 'changed' : 'unchanged') : 'initialized';
  const output = {
    ok: true,
    status,
    dry_run: dryRun,
    user_id: userId,
    checked_at: new Date().toISOString(),
    changes,
    summary: currentSummary,
    agent_decision_prompt: buildAgentDecisionPrompt(status, changes),
    self_delivery_checklist: [
      'Can this Agent finish the work with available tools, MCP servers, public data, or user-selected assets?',
      'Is the deliverable explicit and safe to send through UUMit delivery endpoints?',
      'Does the action require user confirmation, payment, publication, webhook/callback exposure, or external submission?',
      'Are secrets, private files, browser sessions, private repositories, and raw local data excluded?',
      'If any answer is uncertain, ask the user or route through UUMit human/task/asset/API flows.',
    ],
    next_actions: hasBaseline && changes.length
      ? [
        'Review changed fields and decide whether to notify the user or continue a pending workflow.',
        'For pending work, mark whether agent_can_self_complete and agent_can_self_deliver are true before taking action.',
      ]
      : [],
  };

  if (!dryRun) {
    writeState(stateFile, {
      updated_at: output.checked_at,
      summary: currentSummary,
    });
  }

  console.log(JSON.stringify(output));
}

main().catch(err => {
  console.log(JSON.stringify({ ok: false, status: 'failed', error: err.message, retryable: true }));
  process.exit(1);
});
