#!/usr/bin/env node
/**
 * UUMit Skill — REST Request Script (Node.js version)
 *
 * Usage:
 *   node rest_request.js <METHOD> <PATH> [--file JSON_FILE] [--param KEY VALUE] [--idempotency-key KEY] [--dry-run]
 *
 * Credentials (priority): env vars > auth file
 *   UUMIT_API_KEY=xxx UUMIT_USER_ID=yyy node rest_request.js GET /api/v1/wallet
 *
 * Features:
 *   - Connection reuse via keep-alive
 *   - Retry for 5xx / timeout / network errors (max 3)
 *   - Rate limit (429) handling with Retry-After
 *   - Dry-run mode via --dry-run
 *   - Idempotency key auto-generation for write operations
 *   - Search fallback for code=9999 (Data Plaza APIs / Knowledge Store assets)
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const BASE_URL = process.env.UUMIT_BASE_URL || 'https://api.uumit.com';
/** 防盗链 Referer 默认来源：须与平台 delivery.anti_hotlink_referer_whitelist 中的主机名匹配 */
const WEB_URL = process.env.UUMIT_WEB_URL || 'https://m.uumit.com';
const DELIVERABLES_REFERER =
  process.env.UUMIT_DELIVERABLES_REFERER || WEB_URL;
const TIMEOUT = 15000;
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;
const SKILL_DIR = path.resolve(__dirname, '..');

// Parse BASE_URL
const baseUrlObj = new URL(BASE_URL);
const isHttps = baseUrlObj.protocol === 'https:';

// Route allowlist (regex patterns)
const ALLOWED_ROUTES = [
  ['GET', /^\/\.well-known\/agent\.json$/],
  ['POST', /^\/a2a$/],
  ['POST', /^\/api\/v1\/auth\/device-auth(\/poll)?$/],
  ['GET', /^\/api\/v1\/agents\/[a-f0-9-]+\/(card|\.well-known\/agent\.json)$/],
  ['GET', /^\/api\/v1\/interop\/debug$/],
  ['GET', /^\/api\/v1\/skill-pack$/],
  ['GET', /^\/api\/v1\/marketplace\/search$/],
  ['GET', /^\/api\/v1\/external-agents(\/[a-f0-9-]+)?$/],
  ['POST', /^\/api\/v1\/external-agents$/],
  ['PATCH', /^\/api\/v1\/external-agents\/[a-f0-9-]+\/webhook$/],
  ['GET', /^\/api\/v1\/agent\/(cruise|bootstrap|negotiations)$/],
  ['GET', /^\/api\/v1\/agent\/agent-settings$/],
  ['PATCH', /^\/api\/v1\/agent\/agent-settings$/],
  ['GET', /^\/api\/v1\/agent\/agent-connections(\/quota)?$/],
  ['GET', /^\/api\/v1\/agent\/agent-connections\/[a-f0-9-]+$/],
  ['PATCH', /^\/api\/v1\/agent\/agent-connections\/[a-f0-9-]+\/rename$/],
  ['POST', /^\/api\/v1\/agent\/agent-connections\/[a-f0-9-]+\/revoke$/],
  ['GET', /^\/api\/v1\/users\/me(\/(profile-completeness|agent))?$/],
  ['PUT', /^\/api\/v1\/users\/me\/profile$/],
  ['POST', /^\/api\/v1\/users\/me\/bind-phone$/],
  ['GET', /^\/api\/v1\/users\/[a-f0-9-]+\/public-profile$/],
  ['GET', /^\/api\/v1\/bindings$/],
  ['POST', /^\/api\/v1\/bindings\/(social|media)$/],
  ['PUT', /^\/api\/v1\/bindings\/[a-f0-9-]+(\/unbind)?$/],
  ['GET', /^\/api\/v1\/wallet(\/transactions|\/stats|\/rates|\/withdraw-config)?$/],
  ['GET', /^\/api\/v1\/credit\/me(\/events)?$/],
  ['GET', /^\/api\/v1\/orders(\/[a-f0-9-]+)?$/],
  ['POST', /^\/api\/v1\/orders\/[a-f0-9-]+\/(deliverables|confirm|cancel|rating)$/],
  ['GET', /^\/api\/v1\/transactions(\/[a-f0-9-]+)?$/],
  ['POST', /^\/api\/v1\/transactions(\/[a-f0-9-]+\/(freeze|accept|reject|deliver|confirm|cancel)?)?$/],
  ['GET', /^\/api\/v1\/tasks(\/hall)?$/],
  ['POST', /^\/api\/v1\/tasks(\/ai-create)?$/],
  ['GET', /^\/api\/v1\/tasks\/[a-f0-9-]+$/],
  ['PUT', /^\/api\/v1\/tasks\/[a-f0-9-]+$/],
  ['PATCH', /^\/api\/v1\/tasks\/[a-f0-9-]+\/quantity$/],
  ['POST', /^\/api\/v1\/tasks\/[a-f0-9-]+\/(applications|close|publish-draft|reuse|push-skill|select-skill)$/],
  ['GET', /^\/api\/v1\/tasks\/applications\/mine$/],
  ['GET', /^\/api\/v1\/tasks\/[a-f0-9-]+\/applications$/],
  ['DELETE', /^\/api\/v1\/tasks\/[a-f0-9-]+\/applications\/[a-f0-9-]+$/],
  ['POST', /^\/api\/v1\/tasks\/[a-f0-9-]+\/applications\/[a-f0-9-]+\/(accept|reject)$/],
  ['GET', /^\/api\/v1\/tasks\/pushes$/],
  ['POST', /^\/api\/v1\/tasks\/pushes\/[a-f0-9-]+\/respond$/],
  ['GET', /^\/api\/v1\/skills(\/hall)?$/],
  ['POST', /^\/api\/v1\/skills(\/ai-create)?$/],
  ['GET', /^\/api\/v1\/skills\/[a-f0-9-]+$/],
  ['PUT', /^\/api\/v1\/skills\/[a-f0-9-]+$/],
  ['DELETE', /^\/api\/v1\/skills\/[a-f0-9-]+$/],
  ['GET', /^\/api\/v1\/capabilities(\/[a-f0-9-]+)?$/],
  ['POST', /^\/api\/v1\/capabilities(\/batch|\/match)?$/],
  ['POST', /^\/api\/v1\/capabilities\/[a-f0-9-]+\/(invoke|discover-demands)$/],
  ['PUT', /^\/api\/v1\/capabilities\/[a-f0-9-]+$/],
  ['DELETE', /^\/api\/v1\/capabilities\/[a-f0-9-]+$/],
  ['GET', /^\/api\/v1\/recommendations(\/feed)?$/],
  ['POST', /^\/api\/v1\/recommendations\/feedback(\/batch)?$/],
  ['POST', /^\/api\/v1\/upload\/(file|image|chunked\/(init|complete))$/],
  ['GET', /^\/api\/v1\/deliverables\/[a-zA-Z0-9_-]+\/download$/],
  ['POST', /^\/api\/v1\/deliverables\/upload(\/(init|complete))?$/],
  ['POST', /^\/api\/v1\/deliverables\/grant-access$/],
  ['GET', /^\/api\/v1\/red-packet\/(koi-counter|koi-activity-feed|my-batches|my-claims)$/],
  ['GET', /^\/api\/v1\/red-packet\/[a-f0-9-]+$/],
  ['POST', /^\/api\/v1\/red-packet\/(create|create-welcome-batch|welcome-claim)$/],
  ['POST', /^\/api\/v1\/red-packet\/claims\/[a-f0-9-]+\/settle$/],
  ['POST', /^\/api\/v1\/red-packet\/[a-f0-9-]+\/claim$/],
  ['GET', /^\/api\/v1\/daily\/box$/],
  ['GET', /^\/api\/v1\/invite\/(codes|stats|registration|milestones|rewards|queue\/stats|website-code)$/],
  ['POST', /^\/api\/v1\/invite\/queue\/join$/],
  ['POST', /^\/api\/v1\/inquiry\/chats$/],
  ['GET', /^\/api\/v1\/growth\/(path|level)$/],
  ['GET', /^\/api\/v1\/milestones\/progress$/],
  ['GET', /^\/api\/v1\/digital-assets(\/market\/list|\/purchased)?$/],
  ['GET', /^\/api\/v1\/digital-assets\/market\/[a-f0-9-]+$/],
  ['GET', /^\/api\/v1\/digital-assets\/[a-f0-9-]+(\/skill-eligibility|\/queries)?$/],
  ['POST', /^\/api\/v1\/digital-assets\/(quick-upload|register|register-link|generate-description|check-duplicate)$/],
  ['POST', /^\/api\/v1\/digital-assets\/[a-f0-9-]+\/(publish|unpublish|analyze|reanalyze|purchase|query)$/],
  ['DELETE', /^\/api\/v1\/digital-assets\/[a-f0-9-]+$/],
  ['POST', /^\/api\/v1\/digital-assets\/queries\/[a-f0-9-]+\/refund-request$/],
  ['GET', /^\/api\/v1\/time-market\/available$/],
  ['POST', /^\/api\/v1\/time-market\/book$/],
  ['POST', /^\/api\/v1\/time-market\/[a-f0-9-]+\/(accept|decline)$/],
  ['GET', /^\/api\/v1\/pricing\/suggestion$/],
  ['GET', /^\/api\/v1\/income-center\/(overview|opportunities)$/],
  ['GET', /^\/api\/v1\/micro-tasks\/(next|stats)$/],
  ['POST', /^\/api\/v1\/micro-tasks\/[a-f0-9-]+\/submit$/],
  ['GET', /^\/api\/v1\/feed\/live-activities$/],
  ['GET', /^\/api\/v1\/negotiation\/sessions(\/by-chat\/[a-f0-9-]+|\/[a-f0-9-]+)?$/],
  ['POST', /^\/api\/v1\/negotiation\/initiate$/],
  ['POST', /^\/api\/v1\/negotiation\/sessions\/[a-f0-9-]+\/(respond|cancel)$/],
  ['GET', /^\/api\/v1\/data-marketplace\/?$/],
  ['GET', /^\/api\/v1\/data-marketplace\/apis\/mine(\/overview)?$/],
  ['POST', /^\/api\/v1\/data-marketplace\/apis$/],
  ['POST', /^\/api\/v1\/data-marketplace\/apis\/import\/(fetch-url|parse-openapi)$/],
  ['GET', /^\/api\/v1\/data-marketplace\/apis\/[a-f0-9-]+\/(detail|stats)$/],
  ['POST', /^\/api\/v1\/data-marketplace\/apis\/[a-f0-9-]+\/test$/],
  ['PUT', /^\/api\/v1\/data-marketplace\/apis\/[a-f0-9-]+(\/offline|\/online)?$/],
  ['POST', /^\/api\/v1\/data-marketplace\/apis\/[a-f0-9-]+\/(submit|withdraw)$/],
  ['DELETE', /^\/api\/v1\/data-marketplace\/apis\/[a-f0-9-]+$/],
  ['GET', /^\/api\/v1\/data-marketplace\/products(\/mine|\/[a-f0-9-]+)?$/],
  ['POST', /^\/api\/v1\/data-marketplace\/products$/],
  ['PUT', /^\/api\/v1\/data-marketplace\/products\/[a-f0-9-]+(\/online|\/offline)?$/],
  ['POST', /^\/api\/v1\/data-marketplace\/products\/[a-f0-9-]+\/(submit|withdraw)$/],
  ['DELETE', /^\/api\/v1\/data-marketplace\/products\/[a-f0-9-]+(\/apis\/[a-f0-9-]+)?$/],
  ['POST', /^\/api\/v1\/data-marketplace\/products\/[a-f0-9-]+\/apis\/[a-f0-9-]+$/],
  ['GET', /^\/api\/v1\/data-marketplace\/llm\/providers(\/[^/]+\/models)?$/],
  ['GET', /^\/api\/v1\/data-marketplace\/llm\/pricing-suggestion$/],
  ['POST', /^\/api\/v1\/data-marketplace\/llm\/quick-create$/],
  ['GET', /^\/api\/v1\/data-marketplace\/[a-f0-9-]+\/openapi-spec$/],
  ['GET', /^\/api\/v1\/data-marketplace\/[a-f0-9-]+$/],
  ['POST', /^\/api\/v1\/data-marketplace\/[a-f0-9-]+\/call(\/stream)?$/],
  ['POST', /^\/api\/v1\/data-marketplace\/[a-f0-9-]+\/key-health-check$/],
  ['PUT', /^\/api\/v1\/data-marketplace\/[a-f0-9-]+\/keys$/],
  ['GET', /^\/api\/v1\/data-marketplace\/calls\/mine$/],
  ['GET', /^\/api\/v1\/demands(\/[a-f0-9-]+)?$/],
  ['POST', /^\/api\/v1\/demands(\/[a-f0-9-]+\/cancel)?$/],
];

const PUBLIC_ROUTES = [
  ['GET', /^\/\.well-known\/agent\.json$/],
  ['POST', /^\/api\/v1\/auth\/device-auth(\/poll)?$/],
  ['GET', /^\/api\/v1\/agents\/[a-f0-9-]+\/(card|\.well-known\/agent\.json)$/],
  ['GET', /^\/api\/v1\/skill-pack$/],
  ['GET', /^\/api\/v1\/marketplace\/search$/],
  ['GET', /^\/api\/v1\/invite\/(queue\/stats|website-code)$/],
];

function validateRoute(method, requestPath) {
  const clean = requestPath.split('?')[0];
  return ALLOWED_ROUTES.some(([m, re]) => method === m && re.test(clean));
}

function isPublicRoute(method, requestPath) {
  const clean = requestPath.split('?')[0];
  return PUBLIC_ROUTES.some(([m, re]) => method === m && re.test(clean));
}

/** 生成稳定的 Referer 根 URL（防盗链按 hostname 匹配白名单） */
function normalizeRefererOrigin(url) {
  try {
    const u = new URL(url.trim());
    return `${u.origin}/`;
  } catch {
    return 'https://m.uumit.com/';
  }
}

/**
 * 交付物下载：平台开启防盗链且配置了 Referer 白名单时，缺 Referer 会返回 HOTLINK_REJECTED。
 * 若调用方未显式传入 Referer，则自动补一条（默认 UUMIT_WEB_URL / UUMIT_DELIVERABLES_REFERER）。
 */
function applyDeliverablesDownloadReferer(method, urlPath, headers) {
  if (method !== 'GET') return;
  const clean = urlPath.split('?')[0];
  if (!/^\/api\/v1\/deliverables\/[^/]+\/download$/.test(clean)) return;
  const hasReferer = Object.keys(headers).some(
    (k) => k.toLowerCase() === 'referer',
  );
  if (hasReferer) return;
  headers.Referer = normalizeRefererOrigin(DELIVERABLES_REFERER);
}

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
  } catch (e) {
    // ignore
  }
  return { apiKey, userId };
}

function makeRequest(method, urlPath, headers, bodyData, timeoutMs) {
  return new Promise((resolve, reject) => {
    const url = BASE_URL + urlPath;
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port || (isHttps ? 443 : 80),
      path: urlObj.pathname + urlObj.search,
      method,
      headers,
      timeout: timeoutMs || TIMEOUT,
    };

    const mod = isHttps ? https : http;
    const req = mod.request(options, (res) => {
      // 3xx 重定向：不尝试 JSON 解析，直接返回 Location
      if (res.statusCode >= 300 && res.statusCode < 400) {
        const location = res.headers.location || '';
        if (res.statusCode === 302 && location) {
          return resolve({ statusCode: res.statusCode, headers: res.headers, data: { code: 0, data: { download_url: location, _redirected: true } } });
        }
        return resolve({ statusCode: res.statusCode, headers: res.headers, data: { code: 0, data: { redirect_location: location } } });
      }

      const chunks = [];
      res.on('data', (chunk) => chunks.push(chunk));
      res.on('end', () => {
        const raw = Buffer.concat(chunks).toString('utf-8');
        let data;
        try {
          data = JSON.parse(raw);
        } catch (e) {
          return reject(new Error(`invalid JSON response: HTTP ${res.statusCode}`));
        }
        resolve({ statusCode: res.statusCode, headers: res.headers, data });
      });
    });

    req.on('error', (e) => reject(e));
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });

    if (bodyData) {
      req.write(bodyData);
    }
    req.end();
  });
}

function parseJsonArg(raw, label) {
  try {
    return JSON.parse(raw);
  } catch (e) {
    console.error(JSON.stringify({ error: `invalid JSON (${label}): ${e.message}` }));
    process.exit(1);
  }
}

function failCli(message) {
  console.error(JSON.stringify({ error: message }));
  process.exit(2);
}

function resolveSkillRelativePath(filePath) {
  if (path.isAbsolute(filePath)) return filePath;

  const cwdPath = path.resolve(filePath);
  if (fs.existsSync(cwdPath)) return cwdPath;

  return path.join(SKILL_DIR, filePath);
}

function parseJsonFile(filePath) {
  const resolvedPath = resolveSkillRelativePath(filePath);
  try {
    return parseJsonArg(fs.readFileSync(resolvedPath, 'utf-8'), `--file ${filePath}`);
  } catch (e) {
    console.error(JSON.stringify({ error: `invalid JSON in file ${filePath}: ${e.message}` }));
    process.exit(1);
  }
}

function appendQueryParams(urlPath, queryParams) {
  const entries = Object.entries(queryParams).filter(([, v]) => v !== undefined && v !== null);
  if (entries.length === 0) return urlPath;

  const separator = urlPath.includes('?') ? '&' : '?';
  const encoded = new URLSearchParams();
  for (const [key, value] of entries) {
    if (Array.isArray(value)) {
      for (const item of value) encoded.append(key, String(item));
    } else {
      encoded.append(key, String(value));
    }
  }
  return urlPath + separator + encoded.toString();
}

function validateDataMarketplaceCallBody(method, urlPath, body) {
  const cleanPath = urlPath.split('?')[0];
  if (method !== 'POST' || !/^\/api\/v1\/data-marketplace\/[a-f0-9-]+\/call(\/stream)?$/.test(cleanPath)) {
    return;
  }
  if (!body || typeof body !== 'object' || Array.isArray(body)) {
    console.error(JSON.stringify({
      error: 'data-marketplace call body must be a JSON object: {"params": {...}}',
      example: { params: { city: '北京' } },
    }));
    process.exit(1);
  }
  if (!Object.prototype.hasOwnProperty.call(body, 'params')) {
    console.error(JSON.stringify({
      error: 'data-marketplace call body missing required wrapper field "params"',
      expected: { params: body },
      hint: 'Wrap API-specific arguments under params, e.g. {"params":{"city":"北京"}}.',
    }));
    process.exit(1);
  }
  if (!body.params || typeof body.params !== 'object' || Array.isArray(body.params)) {
    console.error(JSON.stringify({
      error: 'data-marketplace call body field "params" must be a JSON object',
      example: { params: { city: '北京' } },
    }));
    process.exit(1);
  }
}

function getIdempotencyKey(body) {
  if (!body || typeof body !== 'object' || Array.isArray(body)) return null;
  return (
    body.idempotency_key
    || (body.params && body.params.idempotency_key)
    || (
      body.params
      && body.params.metadata
      && body.params.metadata.uuagent
      && body.params.metadata.uuagent.idempotency_key
    )
    || null
  );
}

function getJsonRpcMethod(body) {
  if (!body || typeof body !== 'object' || Array.isArray(body)) return null;
  return typeof body.method === 'string' ? body.method : null;
}

function requiresExplicitIdempotency(method, urlPath, body) {
  if (!['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) return false;
  const clean = urlPath.split('?')[0];
  if (clean === '/a2a') {
    return getJsonRpcMethod(body) === 'tasks/send';
  }
  return [
    /^\/api\/v1\/transactions\/[a-f0-9-]+\/(freeze|accept|reject|deliver|confirm|cancel)$/,
    /^\/api\/v1\/data-marketplace\/[a-f0-9-]+\/call(\/stream)?$/,
    /^\/api\/v1\/digital-assets\/[a-f0-9-]+\/(purchase|query)$/,
    /^\/api\/v1\/tasks$/,
    /^\/api\/v1\/tasks\/[a-f0-9-]+\/(close|publish-draft|reuse|push-skill|select-skill)$/,
    /^\/api\/v1\/time-market\/book$/,
    /^\/api\/v1\/negotiation\/(initiate|sessions\/[a-f0-9-]+\/(respond|cancel))$/,
  ].some((re) => re.test(clean));
}

function getSearchTerm(urlPath, queryParams, body) {
  const fromBody = body && (body.search || body.keyword);
  if (fromBody) return String(fromBody).toLowerCase();

  const fromQuery = queryParams.search || queryParams.keyword;
  if (fromQuery) return String(fromQuery).toLowerCase();

  const parsed = new URL(urlPath, BASE_URL);
  return (parsed.searchParams.get('search') || parsed.searchParams.get('keyword') || '').toLowerCase();
}

function removeSearchParams(urlPath) {
  const parsed = new URL(urlPath, BASE_URL);
  parsed.searchParams.delete('search');
  parsed.searchParams.delete('keyword');
  return parsed.pathname + parsed.search;
}

function searchFallback(method, urlPath, headers, body, queryParams, responseData) {
  if (!responseData || responseData.code !== 9999) return null;

  const cleanPath = urlPath.split('?')[0];
  const isDataMarketplace = cleanPath === '/api/v1/data-marketplace/';
  const isDigitalAssets = cleanPath === '/api/v1/digital-assets/market/list';
  if (!isDataMarketplace && !isDigitalAssets) return null;

  const searchTerm = getSearchTerm(urlPath, queryParams, body);
  if (!searchTerm) return null;

  let fallbackPath = urlPath;
  let fallbackBody = null;

  if (body) {
    fallbackBody = { ...body };
    delete fallbackBody.search;
    delete fallbackBody.keyword;
  } else {
    fallbackPath = removeSearchParams(urlPath);
  }

  return makeRequest(method, fallbackPath, headers, fallbackBody ? JSON.stringify(fallbackBody) : null)
    .then(({ data: d }) => {
      if (d.code !== 0) return null;
      const items = (d.data && d.data.items) || [];
      const filtered = items.filter(item => {
        const text = [
          item.name, item.title, item.description, item.summary
        ].filter(Boolean).join(' ').toLowerCase();
        return text.includes(searchTerm);
      });
      if (d.data) {
        d.data.items = filtered;
        d.data._search_fallback = true;
        d.data._search_term = searchTerm;
      }
      return d;
    })
    .catch(() => null);
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error('Usage: node rest_request.js <METHOD> <PATH> [--file FILE] [--param KEY VALUE] [--idempotency-key KEY] [--dry-run]');
    process.exit(2);
  }

  const method = args[0].toUpperCase();
  let urlPath = args[1];
  const isDeviceAuth = urlPath.startsWith('/api/v1/auth/device-auth');

  let body = null;
  let hasBodyFile = false;
  let dryRun = false;
  let queryParams = {};
  let idempotencyKey = null;

  function requireValue(index, flag) {
    if (index >= args.length || args[index].startsWith('--')) {
      failCli(`missing value for ${flag}`);
    }
    return args[index];
  }

  function setBodyFile(value) {
    if (hasBodyFile) {
      failCli('duplicate --file is not allowed');
    }
    hasBodyFile = true;
    body = value;
  }

  for (let i = 2; i < args.length; i++) {
    switch (args[i]) {
      case '--file':
        setBodyFile(parseJsonFile(requireValue(++i, '--file')));
        break;
      case '--param':
        {
          const key = requireValue(i + 1, '--param KEY');
          const value = requireValue(i + 2, '--param VALUE');
          if (!key.trim()) failCli('--param key cannot be empty');
          queryParams[key] = value;
          i += 2;
        }
        break;
      case '--dry-run':
        dryRun = true;
        break;
      case '--idempotency-key':
        idempotencyKey = requireValue(++i, '--idempotency-key');
        if (!idempotencyKey.trim()) failCli('--idempotency-key cannot be empty');
        break;
      default:
        failCli(`unknown argument: ${args[i]}`);
    }
  }

  // Append query params with URLSearchParams so PowerShell/cmd callers can pass raw Unicode safely.
  const fallbackQueryParams = { ...queryParams };
  urlPath = appendQueryParams(urlPath, queryParams);

  const validateRoutes = process.env.UUMIT_REST_VALIDATE_ROUTES !== '0';
  if (validateRoutes && !validateRoute(method, urlPath)) {
    console.error(JSON.stringify({ error: `route not in allowlist: ${method} ${urlPath.split('?')[0]}` }));
    process.exit(1);
  }

  if (dryRun) {
    validateDataMarketplaceCallBody(method, urlPath, body);
    const effectiveIdempotencyKey = idempotencyKey || getIdempotencyKey(body);
    console.log(JSON.stringify({
      dry_run: true,
      method,
      path: urlPath,
      body,
      idempotency_key: effectiveIdempotencyKey,
      requires_explicit_idempotency_key: requiresExplicitIdempotency(method, urlPath, body),
      note: 'This is a dry-run preview. No actual request was sent.',
    }, null, 2));
    return;
  }

  const { apiKey, userId } = loadCredentials();
  const publicRoute = isPublicRoute(method, urlPath);
  if (!isDeviceAuth && !publicRoute && (!apiKey || !userId)) {
    console.error('Credentials not found. Set UUMIT_API_KEY and UUMIT_USER_ID env vars.');
    process.exit(2);
  }

  const headers = { 'Content-Type': 'application/json; charset=utf-8' };
  const effectiveIdempotencyKey = idempotencyKey || getIdempotencyKey(body);
  if (requiresExplicitIdempotency(method, urlPath, body) && !effectiveIdempotencyKey) {
    console.error(JSON.stringify({
      error: 'explicit idempotency key required',
      hint: 'Pass --idempotency-key KEY or include idempotency_key in the JSON body.',
      method,
      path: urlPath.split('?')[0],
    }));
    process.exit(2);
  }
  if (!isDeviceAuth && apiKey && userId) {
    headers['X-Api-Key'] = apiKey;
    headers['X-Platform-User-Id'] = userId;
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
      headers['Idempotency-Key'] = effectiveIdempotencyKey || crypto.randomUUID();
    }
  }

  // 交付物下载：自动补 Referer 以满足防盗链白名单
  applyDeliverablesDownloadReferer(method, urlPath, headers);

  const isDeliverablesDownload = /^\/api\/v1\/deliverables\/[^/]+\/download$/.test(urlPath.split('?')[0]);
  const maxRetries = isDeliverablesDownload ? 1 : MAX_RETRIES;

  validateDataMarketplaceCallBody(method, urlPath, body);
  const bodyStr = body ? JSON.stringify(body) : null;
  let lastError = null;
  let lastStatusCode = null;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      if (attempt > 0 && process.env.UUMIT_VERBOSE) {
        console.error(`[retry ${attempt + 1}/${maxRetries}]`);
      }

      const { statusCode, headers: respHeaders, data } = await makeRequest(method, urlPath, headers, bodyStr);
      lastStatusCode = statusCode;

      // 429 Rate Limited
      if (statusCode === 429) {
        const retryAfter = parseInt(respHeaders['retry-after'] || '5', 10);
        if (attempt < maxRetries - 1) {
          await new Promise(r => setTimeout(r, retryAfter * 1000));
          continue;
        }
        lastError = `HTTP 429: rate limited, Retry-After=${retryAfter}s`;
        break;
      }

      // 5xx retry
      if (statusCode >= 500 && attempt < maxRetries - 1) {
        lastError = `HTTP ${statusCode}: server error`;
        await new Promise(r => setTimeout(r, RETRY_DELAY * (attempt + 1)));
        continue;
      }
      if (statusCode >= 500) {
        lastError = `HTTP ${statusCode}: server error`;
      }

      // Search fallback for code=9999
      if (data && data.code === 9999) {
        const fallback = await searchFallback(method, urlPath, headers, body, fallbackQueryParams, data);
        if (fallback) {
          console.log(JSON.stringify(fallback));
          return;
        }
      }

      if (process.env.UUMIT_VERBOSE) {
        data._http_status = statusCode;
        data._request = { method, path: urlPath };
      }

      console.log(JSON.stringify(data));
      // 422：参数校验失败 —— stdout 仍为 JSON，stderr 提示勿盲目重试
      if (statusCode === 422) {
        console.error(
          '[uumit] HTTP 422：参数校验失败。'
        );
        process.exit(1);
      }
      if (statusCode >= 500) process.exit(1);
      return;

    } catch (err) {
      lastError = err.message;
      if (attempt < maxRetries - 1) {
        await new Promise(r => setTimeout(r, RETRY_DELAY * (attempt + 1)));
      }
    }
  }

  console.error(JSON.stringify({ error: lastError, retries: maxRetries }));
  process.exit(1);
}

main().catch(err => {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
});