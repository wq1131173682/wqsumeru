#!/usr/bin/env node
/**
 * UUMit Skill — package self-check.
 *
 * Checks:
 * - manifest files exist
 * - SKILL.md / metadata / manifest versions are consistent
 * - deprecated paths or old script names are not present
 * - documented REST endpoints are covered by rest_request.js allowlist
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const SKILL_DIR = path.resolve(__dirname, '..');
const MANIFEST_PATH = path.join(SKILL_DIR, 'manifest.json');
const SKILL_PATH = path.join(SKILL_DIR, 'SKILL.md');
const REST_PATH = path.join(SKILL_DIR, 'scripts', 'rest_request.js');

const DOC_FILES = [
  'SKILL.md',
  'SKILL.zh-CN.md',
  'PLAYBOOKS.md',
  'INTEROP.md',
  'API_REFERENCE.md',
  'DEEP_LINKS.md',
  'HOSTS.md',
  'SAFETY.md',
  'TROUBLESHOOTING.md',
];

const OPENAPI_SPEC_TOKEN = 'openapi-spec';
const NOT_IMPLEMENTED_ZH = '\u672a\u5b9e\u73b0';

const DEPRECATED_PATTERNS = [
  /1\.0\.4/,
  /exchange-rates\/latest/,
  /upload_file\.py/,
  /chunked_upload\.py/,
  /tasks\/pushes\/mine/,
  new RegExp(`${OPENAPI_SPEC_TOKEN}\`?\\s*.*${NOT_IMPLEMENTED_ZH}`),
];

const JWT_ONLY_SKILL_PATTERNS = [
  /\/api\/v1\/daily\/(checkin|lucky-flip|time-capsule)/,
  /\/api\/v1\/invite\/(codes\/refresh|chain|records|queue\/list|queue\/invite)/,
];

const JWT_ONLY_ALLOWLIST_PATTERNS = [
  /daily\\\/\(checkin\|lucky-flip\|time-capsule/,
  /invite\\\/\(codes\\\/refresh\|chain\|records\|queue\\\/list\|queue\\\/invite/,
];

function read(file) {
  return fs.readFileSync(path.join(SKILL_DIR, file), 'utf8');
}

function extractFrontmatterVersion(skillText) {
  const m = skillText.match(/^version:\s*([^\n\r]+)/m);
  return m ? m[1].trim() : null;
}

function extractMetadataVersion(skillText) {
  const line = skillText.split(/\r?\n/).find((l) => l.startsWith('metadata: '));
  if (!line) return null;
  try {
    const metadata = JSON.parse(line.slice('metadata: '.length));
    return metadata.agent_skill && metadata.agent_skill.version;
  } catch (e) {
    throw new Error(`metadata JSON parse failed: ${e.message}`);
  }
}

function loadAllowlist() {
  const code = fs.readFileSync(REST_PATH, 'utf8');
  const start = code.indexOf('const ALLOWED_ROUTES = [');
  const end = code.indexOf('];', start);
  if (start === -1 || end === -1) {
    throw new Error('ALLOWED_ROUTES block not found');
  }
  const snippet = code.slice(start, end + 2) + '\nALLOWED_ROUTES;';
  const script = new vm.Script(snippet);
  return script.runInNewContext({});
}

function normalizeEndpoint(raw) {
  let endpoint = raw.trim();
  endpoint = endpoint.replace(/^https?:\/\/[^/]+/, '');
  endpoint = endpoint.replace(/\?[^`\s|)]*/g, '');
  endpoint = endpoint.replace(/\{[a-zA-Z0-9_]+\}/g, '00000000-0000-0000-0000-000000000000');
  endpoint = endpoint.replace(/<[^>]+>/g, '00000000-0000-0000-0000-000000000000');
  return endpoint;
}

function collectDocumentedRoutes() {
  const routes = [];
  const seen = new Set();
  const re = /`(GET|POST|PUT|PATCH|DELETE)\s+([^`]+)`/g;

  function addRoute(file, method, rawEndpoint) {
    const endpoint = normalizeEndpoint(rawEndpoint.split(/\s+/)[0]);
    if (!endpoint.startsWith('/') || endpoint.includes('...')) return;

    const key = `${file}:${method}:${endpoint}`;
    if (seen.has(key)) return;
    seen.add(key);
    routes.push({ file, method, endpoint });
  }

  for (const file of DOC_FILES) {
    const filePath = path.join(SKILL_DIR, file);
    if (!fs.existsSync(filePath)) continue;
    const text = fs.readFileSync(filePath, 'utf8');
    let match;
    while ((match = re.exec(text)) !== null) {
      addRoute(file, match[1], match[2]);
    }

    for (const line of text.split(/\r?\n/)) {
      const codeSpans = [...line.matchAll(/`([^`]+)`/g)].map((m) => m[1].trim());
      for (let i = 0; i < codeSpans.length - 1; i++) {
        if (/^(GET|POST|PUT|PATCH|DELETE)$/.test(codeSpans[i])) {
          addRoute(file, codeSpans[i], codeSpans[i + 1]);
        }
      }
    }
  }
  return routes;
}

function routeAllowed(allowlist, method, endpoint) {
  const clean = endpoint.split('?')[0];
  return allowlist.some(([m, re]) => m === method && re.test(clean));
}

function main() {
  const errors = [];
  const warnings = [];

  let manifest;
  try {
    manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));
  } catch (e) {
    errors.push(`manifest parse failed: ${e.message}`);
    manifest = { files: {} };
  }

  for (const file of Object.keys(manifest.files || {})) {
    const fullPath = path.join(SKILL_DIR, file);
    if (!fs.existsSync(fullPath)) {
      errors.push(`manifest file missing: ${file}`);
    }
  }

  const skillText = fs.existsSync(SKILL_PATH) ? fs.readFileSync(SKILL_PATH, 'utf8') : '';
  const frontmatterVersion = extractFrontmatterVersion(skillText);
  let metadataVersion = null;
  try {
    metadataVersion = extractMetadataVersion(skillText);
  } catch (e) {
    errors.push(e.message);
  }

  const versions = [
    ['manifest', manifest.version],
    ['frontmatter', frontmatterVersion],
    ['metadata', metadataVersion],
  ];
  const distinctVersions = new Set(versions.map(([, v]) => v).filter(Boolean));
  if (distinctVersions.size !== 1) {
    errors.push(`version mismatch: ${versions.map(([k, v]) => `${k}=${v || 'missing'}`).join(', ')}`);
  }

  for (const file of DOC_FILES.concat([
    'scripts/rest_request.js',
    'scripts/upload_file.js',
  ])) {
    const fullPath = path.join(SKILL_DIR, file);
    if (!fs.existsSync(fullPath)) continue;
    const text = fs.readFileSync(fullPath, 'utf8');
    for (const pattern of DEPRECATED_PATTERNS) {
      if (pattern.test(text)) {
        errors.push(`deprecated pattern ${pattern} found in ${file}`);
      }
    }
  }

  for (const file of ['SKILL.md', 'API_REFERENCE.md']) {
    const fullPath = path.join(SKILL_DIR, file);
    if (!fs.existsSync(fullPath)) continue;
    const text = fs.readFileSync(fullPath, 'utf8');
    for (const pattern of JWT_ONLY_SKILL_PATTERNS) {
      if (pattern.test(text)) {
        errors.push(`JWT-only endpoint or marker found in Skill callable docs: ${pattern} (${file})`);
      }
    }
  }

  if (fs.existsSync(REST_PATH)) {
    const restText = fs.readFileSync(REST_PATH, 'utf8');
    for (const pattern of JWT_ONLY_ALLOWLIST_PATTERNS) {
      if (pattern.test(restText)) {
        errors.push(`JWT-only endpoint remains in rest_request allowlist: ${pattern}`);
      }
    }
  }

  let allowlist = [];
  try {
    allowlist = loadAllowlist();
  } catch (e) {
    errors.push(`allowlist load failed: ${e.message}`);
  }

  const documentedRoutes = collectDocumentedRoutes();
  for (const route of documentedRoutes) {
    if (!routeAllowed(allowlist, route.method, route.endpoint)) {
      warnings.push(`documented route not in allowlist: ${route.method} ${route.endpoint} (${route.file})`);
    }
  }

  const result = {
    ok: errors.length === 0,
    errors,
    warnings,
    checked: {
      manifest_files: Object.keys(manifest.files || {}).length,
      documented_routes: documentedRoutes.length,
    },
  };

  const output = JSON.stringify(result, null, 2);
  if (errors.length > 0) {
    console.error(output);
    process.exit(1);
  }
  console.log(output);
}

main();
