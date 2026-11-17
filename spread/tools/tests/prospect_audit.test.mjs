// Run: node --test spread/tools/tests/
import assert from 'node:assert/strict';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { after, before, describe, test } from 'node:test';

import {
  audit, buildFindings, buildOpener, classifyFailure, classifyLinks, parseRobots, renderReport, rootBlocked, siteOf,
} from '../prospect_audit.mjs';

// ---------------------------------------------------------------- pure logic
describe('robots.txt', () => {
  const groups = parseRobots(`
# comment
User-agent: GPTBot
User-agent: OAI-SearchBot
Disallow: /

User-agent: ClaudeBot
Disallow: /private

User-agent: *
Allow: /
`);

  test('a group can list several agents', () => {
    assert.equal(rootBlocked(groups, 'GPTBot'), true);
    assert.equal(rootBlocked(groups, 'OAI-SearchBot'), true);
  });

  test('a partial disallow does not block the root', () => {
    assert.equal(rootBlocked(groups, 'ClaudeBot'), false);
  });

  test('unknown agents fall back to *', () => {
    assert.equal(rootBlocked(groups, 'PerplexityBot'), false);
    assert.equal(rootBlocked(parseRobots('User-agent: *\nDisallow: /'), 'PerplexityBot'), true);
  });

  test('empty Disallow allows everything', () => {
    assert.equal(rootBlocked(parseRobots('User-agent: *\nDisallow:'), 'GPTBot'), false);
  });
});

describe('resource failures', () => {
  test('site grouping', () => {
    assert.equal(siteOf('www.acme.com'), 'acme.com');
    assert.equal(siteOf('cdn.acme.com'), 'acme.com');
    assert.equal(siteOf('www.acme.com.ar'), 'acme.com.ar');
    assert.equal(siteOf('127.0.0.1:8080'), '127.0.0.1');
  });

  test('only the prospect\'s own assets count, and auditor-side errors are not evidence', () => {
    const host = 'www.acme.com';
    assert.equal(classifyFailure({ url: 'https://cdn.acme.com/a.png', type: 'image', status: 404 }, host), 'own');
    assert.equal(classifyFailure({ url: 'https://www.acme.com/a.js', type: 'script', errorText: 'net::ERR_NAME_NOT_RESOLVED' }, host), 'own');
    assert.equal(classifyFailure({ url: 'https://www.acme.com/a.js', type: 'script', errorText: 'net::ERR_ABORTED' }, host), 'auditor');
    assert.equal(classifyFailure({ url: 'https://www.acme.com/a.js', type: 'script', errorText: 'net::ERR_TUNNEL_CONNECTION_FAILED' }, host), 'auditor');
    assert.equal(classifyFailure({ url: 'https://tracker.example/p.gif', type: 'image', status: 403 }, host), null);
    assert.equal(classifyFailure({ url: 'https://www.acme.com/api', type: 'fetch', status: 500 }, host), null);
  });
});

describe('links', () => {
  test('bot walls and network errors are not broken links', () => {
    const r = classifyLinks([
      { url: 'a', status: 404 }, { url: 'b', status: 500 }, { url: 'c', status: 403 },
      { url: 'd', status: 429 }, { url: 'e', status: 0 }, { url: 'f', status: 200 },
    ]);
    assert.deepEqual(r.broken.map((x) => x.url), ['a', 'b']);
    assert.deepEqual(r.unmeasured.map((x) => x.url), ['c', 'd', 'e']);
  });
});

describe('findings', () => {
  const clean = {
    status: 200, url: 'https://x.test/', host: 'x.test',
    robots: { status: 200, text: 'User-agent: *\nAllow: /' },
    desktop: { title: 'X', description: 'd', ogImage: '/og.png', h1: 1, jsonLd: 1, forms: [], viewportH: 900, ctas: [{ text: 'Book a demo', top: 300 }], lcp: 900 },
    mobile: { viewportMeta: true, viewportW: 390, viewportH: 664, scrollW: 390, ctas: [{ text: 'Book a demo', top: 400 }] },
    consoleErrors: [], brokenLinks: [], checkedLinks: 3,
  };

  test('a clean site yields no findings and no opener', () => {
    const f = buildFindings(clean);
    assert.deepEqual(f, []);
    assert.equal(buildOpener(f, 'x.test'), null);
    assert.match(renderReport({ ...clean, date: '2026-11-14', findings: f, opener: null, copy: [] }), /No uses encuadre de pérdida/);
  });

  test('training-only AI blocks are medium, live-search blocks are high', () => {
    const training = buildFindings({ ...clean, robots: { status: 200, text: 'User-agent: GPTBot\nDisallow: /' } });
    assert.equal(training.find((x) => x.id === 'AI_BOTS_BLOCKED').severity, 'media');
    const live = buildFindings({ ...clean, robots: { status: 200, text: 'User-agent: PerplexityBot\nDisallow: /' } });
    assert.equal(live.find((x) => x.id === 'AI_BOTS_BLOCKED').severity, 'alta');
  });

  test('blocking everyone is reported once, not as an AI issue', () => {
    const f = buildFindings({ ...clean, robots: { status: 200, text: 'User-agent: *\nDisallow: /' } });
    assert.deepEqual(f.map((x) => x.id), ['ROBOTS_BLOCK_ALL']);
  });

  test('slow LCP thresholds follow Core Web Vitals', () => {
    assert.equal(buildFindings({ ...clean, desktop: { ...clean.desktop, lcp: 3000 } })[0].severity, 'media');
    assert.equal(buildFindings({ ...clean, desktop: { ...clean.desktop, lcp: 4500 } })[0].severity, 'alta');
  });

  test('clipped overflow (innerWidth unchanged) is not a mobile problem', () => {
    const clipped = { ...clean, mobile: { ...clean.mobile, scrollW: 3889, innerW: 390 } };
    assert.deepEqual(buildFindings(clipped), []);
    const real = { ...clean, mobile: { ...clean.mobile, scrollW: 808, innerW: 809 } };
    assert.equal(buildFindings(real)[0].id, 'MOBILE_OVERFLOW');
  });

  test('render-dependent findings become partial when resources were not measured', () => {
    const raw = { ...clean, desktop: { ...clean.desktop, lcp: 4500 }, brokenLinks: [{ url: 'https://x.test/a', status: 404 }],
      unmeasured: [{ url: 'https://cdn.x.test/app.js', error: 'net::ERR_TUNNEL_CONNECTION_FAILED' }] };
    const f = buildFindings(raw);
    assert.equal(f.find((x) => x.id === 'SLOW_LCP').partial, true);
    assert.equal(f.find((x) => x.id === 'BROKEN_LINKS').partial, undefined);
    assert.deepEqual(buildOpener(f, 'x.test').basedOn, ['BROKEN_LINKS']);
  });

  test('CTA findings are heuristic and never reach the opener', () => {
    const noCta = { ...clean, mobile: { ...clean.mobile, ctas: [] } };
    const f = buildFindings(noCta);
    assert.equal(f[0].id, 'NO_CTA_MOBILE_FOLD');
    assert.equal(f[0].heuristic, true);
    assert.equal(buildOpener(f, 'x.test'), null);
  });

  test('the opener uses only measured losses, highest severity first', () => {
    const f = buildFindings({ ...clean, consoleErrors: ['x'], brokenLinks: [{ url: 'https://x.test/a', status: 404 }] });
    const o = buildOpener(f, 'x.test');
    assert.deepEqual(o.basedOn, ['BROKEN_LINKS', 'CONSOLE_ERRORS']);
    assert.match(o.es, /1 link de tu home da error \(\/a → 404\)/);
    assert.match(o.en, /1 link on your homepage is broken/);
  });
});

// ------------------------------------------------------- end to end, real browser
function serve(routes) {
  const server = http.createServer((req, res) => {
    const route = routes[req.url.split('?')[0]];
    if (!route) {
      res.writeHead(404, { 'content-type': 'text/plain' });
      return res.end(req.method === 'HEAD' ? undefined : 'not found');
    }
    res.writeHead(200, { 'content-type': route.type || 'text/html; charset=utf-8' });
    res.end(req.method === 'HEAD' ? undefined : route.body);
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server)));
}

const BAD = {
  '/': {
    body: `<!doctype html><html><head><title>Acme</title>
<meta name="viewport" content="width=device-width, initial-scale=1"></head><body>
<h1>Acme</h1><h1>Also Acme</h1>
<p>Increase your conversion rate with Acme.</p>
<div style="width:800px;background:#eee">A fixed-width block</div>
<script>console.error('boom')</script>
<img src="/missing.png" alt="">
<a href="/about">About</a> <a href="/pricing">Pricing</a>
<div style="height:1600px"></div>
<a href="/contact">Book a demo</a>
<form>${'<input name="f">'.repeat(8)}<button>Send</button></form>
</body></html>`,
  },
  '/robots.txt': { type: 'text/plain', body: 'User-agent: GPTBot\nDisallow: /\n\nUser-agent: OAI-SearchBot\nDisallow: /\n\nUser-agent: *\nAllow: /\n' },
  '/about': { body: '<p>about</p>' },
  '/contact': { body: '<p>contact</p>' },
};

const GOOD = {
  '/': {
    body: `<!doctype html><html><head><title>Good Co · Pipeline for B2B SaaS</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="We build the system that generates qualified pipeline.">
<meta property="og:image" content="/og.png">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"Good Co"}</script>
</head><body><h1>Great products don't distribute themselves.</h1>
<a href="/demo">Get a strategy call</a> <a href="/about">About</a></body></html>`,
  },
  '/robots.txt': { type: 'text/plain', body: 'User-agent: *\nAllow: /\n' },
  '/demo': { body: '<p>demo</p>' },
  '/about': { body: '<p>about</p>' },
};

describe('end to end', () => {
  let bad;
  let good;
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'spread-audit-'));
  before(async () => { [bad, good] = await Promise.all([serve(BAD), serve(GOOD)]); });
  after(() => { bad.close(); good.close(); fs.rmSync(tmp, { recursive: true, force: true }); });

  test('finds every planted problem on a broken site', { timeout: 90000 }, async () => {
    const out = path.join(tmp, 'bad');
    const r = await audit(`http://127.0.0.1:${bad.address().port}/`, { outDir: out });
    const ids = new Set(r.findings.map((x) => x.id));
    for (const id of ['AI_BOTS_BLOCKED', 'MOBILE_OVERFLOW', 'NO_CTA_MOBILE_FOLD', 'NO_CTA_DESKTOP_FOLD',
      'BROKEN_LINKS', 'CONSOLE_ERRORS', 'FAILED_RESOURCES', 'MISSING_OG_IMAGE', 'MISSING_META_DESCRIPTION', 'H1_COUNT',
      'NO_STRUCTURED_DATA', 'LONG_FORM']) {
      assert.ok(ids.has(id), `missing ${id}; got ${[...ids].join(', ')}`);
    }
    assert.equal(r.findings.find((x) => x.id === 'AI_BOTS_BLOCKED').severity, 'alta');
    assert.match(r.findings.find((x) => x.id === 'BROKEN_LINKS').evidence, /\/pricing → 404/);
    assert.match(r.findings.find((x) => x.id === 'FAILED_RESOURCES').evidence, /\/missing\.png → 404/);
    assert.match(r.findings.find((x) => x.id === 'CONSOLE_ERRORS').evidence, /boom/);
    assert.match(r.findings.find((x) => x.id === 'AI_BOTS_BLOCKED').loss.es, /el rastreador que usa OpenAI/);
    assert.ok(r.copy.some((c) => c.rule === 'PT08'), 'copy audit should flag the gain promise');
    assert.ok(r.opener && r.opener.basedOn.length === 2);
    for (const f of ['report.md', 'findings.json', 'desktop.png', 'mobile.png']) {
      assert.ok(fs.statSync(path.join(out, f)).size > 0, `${f} written`);
    }
    assert.match(fs.readFileSync(path.join(out, 'report.md'), 'utf-8'), /## Primer mensaje de outbound/);
  });

  test('a healthy site gets no findings and no loss-framed opener', { timeout: 90000 }, async () => {
    const r = await audit(`http://127.0.0.1:${good.address().port}/`, { outDir: path.join(tmp, 'good') });
    assert.deepEqual(r.findings.map((x) => x.id), []);
    assert.equal(r.opener, null);
  });
});
