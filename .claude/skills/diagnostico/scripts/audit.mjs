#!/usr/bin/env node
// Nexar — diagnóstico de presencia digital.
// Junta evidencia objetiva de una URL (sin juicio): SEO técnico, GEO, medición,
// velocidad, mobile, conversión, accesibilidad básica, seguridad y screenshots.
// El juicio y el informe los hace el agente siguiendo ../SKILL.md.
//
// Uso:  node audit.mjs <url> [--out <carpeta>]
// Requiere Playwright con Chromium: npm i -D playwright && npx playwright install chromium

import { createRequire } from 'node:module';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join, resolve } from 'node:path';

const require = createRequire(import.meta.url);
let chromium;
try {
  ({ chromium } = require('playwright'));
} catch {
  console.error('Falta Playwright. Instalalo con: npm i -D playwright && npx playwright install chromium');
  process.exit(1);
}

// Umbrales de las métricas de laboratorio. Las de Google (Core Web Vitals) son
// de campo; acá se mide en laboratorio, así que sirven como señal, no como veredicto.
const LCP_GOOD_MS = 2500;
const LCP_POOR_MS = 4000;
const CLS_GOOD = 0.1;
const CLS_POOR = 0.25;
const PAGE_WEIGHT_GOOD_BYTES = 2 * 1024 * 1024;
const PAGE_WEIGHT_POOR_BYTES = 4 * 1024 * 1024;
const HEAVY_IMAGE_BYTES = 300 * 1024;
const SETTLE_MS = 2500;
const NAV_TIMEOUT_MS = 45000;
const MAX_SCROLL_SHOTS = 12;
const SCROLL_STEP_MS = 700;

// Mismos anchos que la QA de Nexar (brain/workflows/website.md).
const VIEWPORTS = [
  { name: 'mobile-390', width: 390, height: 844, mobile: true },
  { name: 'tablet-768', width: 768, height: 1024, mobile: true },
  { name: 'laptop-1280', width: 1280, height: 800, mobile: false },
  { name: 'desktop-1440', width: 1440, height: 900, mobile: false },
];

// Perfil parecido al "Slow 4G" de Lighthouse para la medición mobile.
const MOBILE_NETWORK = { latency: 150, downloadThroughput: (1.6 * 1024 * 1024) / 8, uploadThroughput: (750 * 1024) / 8 };
const MOBILE_CPU_SLOWDOWN = 4;

const TRACKERS = [
  { name: 'Google Analytics 4', test: /googletagmanager\.com\/gtag\/js\?id=G-|gtag\(\s*['"]config['"]\s*,\s*['"]G-/ },
  { name: 'Google Tag Manager', test: /googletagmanager\.com\/gtm\.js|GTM-[A-Z0-9]+/ },
  { name: 'Meta Pixel', test: /connect\.facebook\.net\/[^"']*fbevents\.js|fbq\(\s*['"]init/ },
  { name: 'Microsoft Clarity', test: /clarity\.ms\/tag/ },
  { name: 'PostHog', test: /posthog/i },
  { name: 'Hotjar', test: /static\.hotjar\.com|hotjar/i },
  { name: 'TikTok Pixel', test: /analytics\.tiktok\.com/ },
  { name: 'LinkedIn Insight', test: /snap\.licdn\.com/ },
  { name: 'Plausible', test: /plausible\.io\/js/ },
  { name: 'Vercel Analytics', test: /\/_vercel\/insights|va\.vercel-scripts\.com/ },
];

const PLATFORMS = [
  { name: 'Webflow', test: /webflow/i },
  { name: 'WordPress', test: /wp-content|wp-includes|wordpress/i },
  { name: 'Wix', test: /wix\.com|wixstatic|_wix/i },
  { name: 'Squarespace', test: /squarespace/i },
  { name: 'Shopify', test: /cdn\.shopify\.com|shopify/i },
  { name: 'Tienda Nube', test: /tiendanube|nuvemshop/i },
  { name: 'Framer', test: /framerusercontent|framer\.com/i },
  { name: 'Next.js', test: /\/_next\/|__NEXT_DATA__|__next_f/ },
  { name: 'Astro', test: /astro-island|\/_astro\//i },
];

// Se buscan solo en URLs de scripts y requests, para no confundir texto del sitio con librerías.
const LIBRARIES = [
  { name: 'GSAP', test: /gsap(\.min)?\.js|\/gsap@|\/gsap\//i },
  { name: 'ScrollTrigger', test: /ScrollTrigger(\.min)?\.js/i },
  { name: 'Lenis', test: /lenis(\.min)?\.js|\/lenis@/i },
  { name: 'Three.js', test: /three(\.module)?(\.min)?\.js|\/three@/i },
  { name: 'Lottie', test: /lottie/i },
  { name: 'jQuery', test: /jquery(\.min)?\.js|\/jquery@/i },
  { name: 'React', test: /react(-dom)?(\.production)?(\.min)?\.js|\/react@/i },
];

function parseArgs(argv) {
  const args = { url: null, out: null };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === '--out') args.out = argv[++i];
    else if (!args.url) args.url = argv[i];
  }
  if (!args.url) {
    console.error('Uso: node audit.mjs <url> [--out <carpeta>]');
    process.exit(1);
  }
  if (!/^https?:\/\//i.test(args.url)) args.url = `https://${args.url}`;
  return args;
}

function rate(value, good, poor) {
  if (value == null) return 'unknown';
  if (value <= good) return 'ok';
  if (value <= poor) return 'warn';
  return 'fail';
}

function kb(bytes) {
  return Math.round(bytes / 1024);
}

// Se inyecta antes de cargar la página para capturar LCP y CLS desde el inicio.
const VITALS_INIT_SCRIPT = `
  window.__nexarVitals = { lcp: null, lcpElement: null, cls: 0 };
  try {
    new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const last = entries[entries.length - 1];
      if (last) {
        window.__nexarVitals.lcp = last.startTime;
        const el = last.element;
        window.__nexarVitals.lcpElement = el ? (el.tagName + (el.id ? '#' + el.id : '') + (el.currentSrc ? ' ' + el.currentSrc : '')) : null;
      }
    }).observe({ type: 'largest-contentful-paint', buffered: true });
    new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (!entry.hadRecentInput) window.__nexarVitals.cls += entry.value;
      }
    }).observe({ type: 'layout-shift', buffered: true });
  } catch (e) {}
`;

async function measureVisit(browser, url, viewport, { throttle }) {
  const context = await browser.newContext({
    viewport: { width: viewport.width, height: viewport.height },
    isMobile: viewport.mobile,
    hasTouch: viewport.mobile,
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  await page.addInitScript(VITALS_INIT_SCRIPT);

  if (throttle) {
    const cdp = await context.newCDPSession(page);
    await cdp.send('Network.enable');
    await cdp.send('Network.emulateNetworkConditions', { offline: false, ...MOBILE_NETWORK });
    await cdp.send('Emulation.setCPUThrottlingRate', { rate: MOBILE_CPU_SLOWDOWN });
  }

  const requests = [];
  page.on('requestfinished', (request) => requests.push(request));

  const started = Date.now();
  const response = await page.goto(url, { waitUntil: 'load', timeout: NAV_TIMEOUT_MS });
  const loadMs = Date.now() - started;
  await page.waitForTimeout(SETTLE_MS);

  const vitals = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0];
    return {
      ...window.__nexarVitals,
      ttfb: nav ? nav.responseStart : null,
      domContentLoaded: nav ? nav.domContentLoadedEventEnd : null,
      horizontalOverflowPx: Math.max(0, document.documentElement.scrollWidth - document.documentElement.clientWidth),
    };
  });

  const sizes = await Promise.all(requests.map(async (request) => {
    try {
      const s = await request.sizes();
      return { type: request.resourceType(), url: request.url(), bytes: s.responseBodySize + s.responseHeadersSize };
    } catch {
      return { type: request.resourceType(), url: request.url(), bytes: 0 };
    }
  }));

  return { context, page, response, loadMs, vitals, sizes };
}

async function extractDom(page) {
  return page.evaluate(() => {
    const meta = (selector) => document.querySelector(selector)?.getAttribute('content') ?? null;
    const viewportHeight = window.innerHeight;
    const visible = (el) => {
      const r = el.getBoundingClientRect();
      const style = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && style.visibility !== 'hidden' && style.display !== 'none';
    };

    const jsonLdTypes = [];
    for (const script of document.querySelectorAll('script[type="application/ld+json"]')) {
      try {
        const data = JSON.parse(script.textContent);
        const items = Array.isArray(data) ? data : (data['@graph'] ?? [data]);
        for (const item of items) if (item && item['@type']) jsonLdTypes.push([].concat(item['@type']).join('/'));
      } catch { jsonLdTypes.push('JSON-LD inválido'); }
    }

    const images = [...document.images].map((img) => {
      const src = img.currentSrc || img.src || '';
      const ext = (src.split('?')[0].match(/\.(avif|webp|png|jpe?g|gif|svg)$/i)?.[1] ?? 'otro').toLowerCase();
      const rect = img.getBoundingClientRect();
      return {
        src,
        format: ext === 'jpeg' ? 'jpg' : ext,
        alt: img.getAttribute('alt'),
        hasDimensions: img.hasAttribute('width') && img.hasAttribute('height'),
        lazy: img.loading === 'lazy',
        naturalWidth: img.naturalWidth,
        renderedWidth: Math.round(rect.width),
        aboveFold: rect.top < viewportHeight && rect.bottom > 0,
      };
    });

    const links = [...document.querySelectorAll('a[href]')].map((a) => a.getAttribute('href'));
    const interactive = [...document.querySelectorAll('a[href], button, [role="button"], input[type="submit"]')];
    const aboveFoldCtas = interactive
      .filter((el) => visible(el) && el.getBoundingClientRect().top < viewportHeight)
      .filter((el) => !(el.getAttribute('href') || '').startsWith('#main') && !/saltar al contenido|skip to/i.test(el.innerText || ''))
      .map((el) => (el.innerText || el.value || el.getAttribute('aria-label') || '').trim().replace(/\s+/g, ' '))
      .filter(Boolean)
      .slice(0, 15);
    const unnamedButtons = [...document.querySelectorAll('button, [role="button"]')]
      .filter((el) => visible(el) && !(el.innerText.trim() || el.getAttribute('aria-label') || el.getAttribute('title'))).length;

    const html = document.documentElement.outerHTML;
    return {
      title: document.title || null,
      metaDescription: meta('meta[name="description"]'),
      canonical: document.querySelector('link[rel="canonical"]')?.href ?? null,
      robotsMeta: meta('meta[name="robots"]'),
      lang: document.documentElement.getAttribute('lang'),
      viewportMeta: meta('meta[name="viewport"]'),
      generator: meta('meta[name="generator"]'),
      favicon: !!document.querySelector('link[rel~="icon"]'),
      hreflang: [...document.querySelectorAll('link[rel="alternate"][hreflang]')].map((l) => l.getAttribute('hreflang')),
      h1: [...document.querySelectorAll('h1')].map((h) => h.innerText.trim().replace(/\s+/g, ' ')).slice(0, 5),
      headingCounts: Object.fromEntries(['h1', 'h2', 'h3'].map((t) => [t, document.querySelectorAll(t).length])),
      openGraph: {
        title: meta('meta[property="og:title"]'),
        description: meta('meta[property="og:description"]'),
        image: meta('meta[property="og:image"]'),
        type: meta('meta[property="og:type"]'),
      },
      twitterCard: meta('meta[name="twitter:card"]'),
      jsonLdTypes,
      images,
      forms: document.forms.length,
      whatsappLinks: links.filter((h) => /wa\.me|whatsapp/i.test(h)).length,
      mailtoLinks: links.filter((h) => /^mailto:/i.test(h)).length,
      telLinks: links.filter((h) => /^tel:/i.test(h)).length,
      aboveFoldCtas,
      unnamedButtons,
      wordCount: document.body ? document.body.innerText.split(/\s+/).filter(Boolean).length : 0,
      htmlSample: html.length > 400000 ? html.slice(0, 400000) : html,
    };
  });
}

// Primero desde el navegador (misma red, proxy y certificados que la visita real);
// si falla (p. ej. un sitemap en otro dominio bloqueado por CORS), por la API de Playwright.
async function fetchStatus(page, url) {
  try {
    const result = await page.evaluate(async (target) => {
      const res = await fetch(target, { redirect: 'follow', cache: 'no-store' });
      const text = res.ok ? await res.text() : '';
      return { status: res.status, bytes: text.length, sample: text.slice(0, 600) };
    }, url);
    return { url, ...result };
  } catch {
    try {
      const res = await page.context().request.get(url, { timeout: 15000, maxRedirects: 5 });
      const text = res.ok() ? await res.text() : '';
      return { url, status: res.status(), bytes: text.length, sample: text.slice(0, 600) };
    } catch (error) {
      return { url, status: null, error: String(error.message || error).split('\n')[0] };
    }
  }
}

function buildChecks(evidence) {
  const checks = [];
  const add = (area, check, status, detail) => checks.push({ area, check, status, detail });
  const { dom, desktop, mobile, files, security, tracking } = evidence;

  // Visibilidad: SEO técnico
  const titleLen = dom.title?.length ?? 0;
  add('visibilidad', 'Title', titleLen === 0 ? 'fail' : (titleLen >= 30 && titleLen <= 60 ? 'ok' : 'warn'), `${titleLen} caracteres: ${dom.title ?? '—'}`);
  const descLen = dom.metaDescription?.length ?? 0;
  add('visibilidad', 'Meta description', descLen === 0 ? 'fail' : (descLen >= 70 && descLen <= 160 ? 'ok' : 'warn'), `${descLen} caracteres`);
  add('visibilidad', 'Un solo H1', dom.headingCounts.h1 === 1 ? 'ok' : (dom.headingCounts.h1 === 0 ? 'fail' : 'warn'), `${dom.headingCounts.h1} H1: ${dom.h1.join(' | ') || '—'}`);
  add('visibilidad', 'Canonical', dom.canonical ? 'ok' : 'warn', dom.canonical ?? 'sin canonical');
  add('visibilidad', 'Idioma declarado (lang)', dom.lang ? 'ok' : 'warn', dom.lang ?? 'sin atributo lang');
  add('visibilidad', 'Open Graph (preview al compartir)', dom.openGraph.title && dom.openGraph.image ? 'ok' : 'fail', `og:title ${dom.openGraph.title ? 'sí' : 'no'} · og:image ${dom.openGraph.image ? 'sí' : 'no'}`);
  add('visibilidad', 'Datos estructurados (JSON-LD)', dom.jsonLdTypes.length ? 'ok' : 'warn', dom.jsonLdTypes.join(', ') || 'ninguno');
  add('visibilidad', 'robots.txt', files.robots.status === 200 ? 'ok' : 'warn', `HTTP ${files.robots.status ?? 'error'}`);
  add('visibilidad', 'sitemap.xml', files.sitemap.status === 200 ? 'ok' : 'warn', `${files.sitemap.url} → HTTP ${files.sitemap.status ?? 'error'}`);
  add('visibilidad', 'Página 404 real', files.notFound.status === 404 ? 'ok' : 'fail', `URL inexistente → HTTP ${files.notFound.status ?? 'error'}${files.notFound.status === 200 ? ' (soft 404: Google puede indexar páginas vacías)' : ''}`);
  add('visibilidad', 'llms.txt (legibilidad para IA / GEO)', files.llms.status === 200 ? 'ok' : 'warn', `HTTP ${files.llms.status ?? 'error'}`);
  if (dom.robotsMeta && /noindex/i.test(dom.robotsMeta)) add('visibilidad', 'Indexable', 'fail', `meta robots: ${dom.robotsMeta}`);

  // Medición
  add('medicion', 'Analytics instalado', tracking.length ? 'ok' : 'fail', tracking.join(', ') || 'no se detectó ninguna herramienta de medición');
  add('medicion', 'Comportamiento (heatmaps / grabaciones)', tracking.some((t) => /Clarity|Hotjar|PostHog/.test(t)) ? 'ok' : 'warn', tracking.filter((t) => /Clarity|Hotjar|PostHog/.test(t)).join(', ') || 'sin Clarity / Hotjar / PostHog');

  // Velocidad
  const mLcp = mobile.vitals.lcp;
  add('velocidad', 'LCP mobile (lab, Slow 4G + CPU 4x)', rate(mLcp, LCP_GOOD_MS, LCP_POOR_MS), mLcp != null ? `${(mLcp / 1000).toFixed(1)} s · elemento: ${mobile.vitals.lcpElement ?? '—'}` : 'no medido');
  add('velocidad', 'LCP desktop (lab, sin throttling)', rate(desktop.vitals.lcp, LCP_GOOD_MS, LCP_POOR_MS), desktop.vitals.lcp != null ? `${(desktop.vitals.lcp / 1000).toFixed(1)} s` : 'no medido');
  add('velocidad', 'CLS (estabilidad visual)', rate(Math.max(mobile.vitals.cls, desktop.vitals.cls), CLS_GOOD, CLS_POOR), `mobile ${mobile.vitals.cls.toFixed(3)} · desktop ${desktop.vitals.cls.toFixed(3)}`);
  add('velocidad', 'Peso de la página', rate(desktop.weight.total, PAGE_WEIGHT_GOOD_BYTES, PAGE_WEIGHT_POOR_BYTES), `${kb(desktop.weight.total)} KB en ${desktop.weight.requests} requests (JS ${kb(desktop.weight.byType.script ?? 0)} KB · imágenes ${kb(desktop.weight.byType.image ?? 0)} KB)`);
  add('velocidad', 'Imágenes pesadas (> 300 KB)', desktop.heavyImages.length ? 'warn' : 'ok', desktop.heavyImages.map((i) => `${kb(i.bytes)} KB ${i.url}`).slice(0, 5).join(' · ') || 'ninguna');
  const legacy = dom.images.filter((i) => ['jpg', 'png', 'gif'].includes(i.format)).length;
  add('velocidad', 'Formatos modernos (AVIF / WebP)', legacy === 0 ? 'ok' : 'warn', `${legacy} de ${dom.images.length} imágenes en JPG/PNG/GIF`);
  const oversized = dom.images.filter((i) => i.renderedWidth > 0 && i.naturalWidth > i.renderedWidth * 2.5).length;
  add('velocidad', 'Imágenes sobredimensionadas', oversized ? 'warn' : 'ok', `${oversized} imágenes con más del 2,5× del ancho en que se muestran`);

  // Mobile
  add('mobile', 'Meta viewport', dom.viewportMeta ? 'ok' : 'fail', dom.viewportMeta ?? 'sin meta viewport');
  add('mobile', 'Sin scroll horizontal en 390 px', mobile.vitals.horizontalOverflowPx === 0 ? 'ok' : 'fail', `${mobile.vitals.horizontalOverflowPx} px de desborde`);

  // Conversión
  const contactPaths = dom.forms + dom.whatsappLinks + dom.mailtoLinks + dom.telLinks;
  add('conversion', 'Vías de contacto', contactPaths ? 'ok' : 'fail', `forms ${dom.forms} · WhatsApp ${dom.whatsappLinks} · mail ${dom.mailtoLinks} · tel ${dom.telLinks}`);
  add('conversion', 'Acciones visibles sin scrollear (desktop)', dom.aboveFoldCtas.length ? 'ok' : 'warn', dom.aboveFoldCtas.slice(0, 8).join(' | ') || 'ninguno');

  // Accesibilidad básica
  const noAlt = dom.images.filter((i) => i.alt === null).length;
  add('accesibilidad', 'Imágenes con alt', noAlt === 0 ? 'ok' : 'warn', `${noAlt} de ${dom.images.length} sin atributo alt`);
  add('accesibilidad', 'Botones con nombre accesible', dom.unnamedButtons === 0 ? 'ok' : 'warn', `${dom.unnamedButtons} botones sin texto ni aria-label`);
  const noDims = dom.images.filter((i) => !i.hasDimensions).length;
  add('accesibilidad', 'Imágenes con width/height (evita saltos)', noDims === 0 ? 'ok' : 'warn', `${noDims} de ${dom.images.length} sin dimensiones`);

  // Seguridad / base técnica
  add('base', 'HTTPS', evidence.finalUrl.startsWith('https://') ? 'ok' : 'fail', evidence.finalUrl);
  add('base', 'HSTS', security['strict-transport-security'] ? 'ok' : 'warn', security['strict-transport-security'] ?? 'ausente');
  add('base', 'Content-Security-Policy', security['content-security-policy'] ? 'ok' : 'warn', security['content-security-policy'] ? 'presente' : 'ausente');
  add('base', 'X-Content-Type-Options', security['x-content-type-options'] ? 'ok' : 'warn', security['x-content-type-options'] ?? 'ausente');
  add('base', 'Favicon', dom.favicon ? 'ok' : 'warn', dom.favicon ? 'presente' : 'ausente');

  return checks;
}

// Recorre la página de a una pantalla, como un visitante, para disparar reveals y
// animaciones por scroll. Si recibe un prefijo, guarda una captura por pantalla.
async function scrollThrough(page, capturePrefix) {
  const viewportHeight = page.viewportSize().height;
  const totalHeight = await page.evaluate(() => document.documentElement.scrollHeight);
  const steps = Math.min(MAX_SCROLL_SHOTS, Math.ceil(totalHeight / viewportHeight));
  const shots = [];
  for (let i = 0; i < steps; i += 1) {
    await page.evaluate((y) => window.scrollTo(0, y), i * viewportHeight);
    await page.waitForTimeout(SCROLL_STEP_MS);
    if (capturePrefix) {
      const path = `${capturePrefix}-${String(i + 1).padStart(2, '0')}.png`;
      await page.screenshot({ path });
      shots.push(path);
    }
  }
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(SCROLL_STEP_MS);
  return shots;
}

function weightOf(sizes) {
  const byType = {};
  let total = 0;
  for (const s of sizes) {
    byType[s.type] = (byType[s.type] ?? 0) + s.bytes;
    total += s.bytes;
  }
  return { total, requests: sizes.length, byType };
}

async function main() {
  const { url, out } = parseArgs(process.argv);
  const host = new URL(url).hostname.replace(/^www\./, '');
  const date = new Date().toISOString().slice(0, 10);
  const outDir = resolve(out ?? join(process.cwd(), 'diagnosticos', `${host}-${date}`));
  mkdirSync(join(outDir, 'screens'), { recursive: true });

  const browser = await chromium.launch();
  try {
    // 1. Visita desktop sin throttling: DOM, headers, peso, métricas.
    const desktopVisit = await measureVisit(browser, url, VIEWPORTS[3], { throttle: false });
    const finalUrl = desktopVisit.page.url();
    const headers = desktopVisit.response ? await desktopVisit.response.allHeaders() : {};
    const dom = await extractDom(desktopVisit.page);
    const scriptSources = await desktopVisit.page.evaluate(() => [...document.scripts].map((s) => s.src || s.textContent.slice(0, 2000)).join('\n'));
    const haystack = `${dom.htmlSample}\n${scriptSources}\n${desktopVisit.sizes.map((s) => s.url).join('\n')}`;
    const tracking = TRACKERS.filter((t) => t.test.test(haystack)).map((t) => t.name);
    const platform = PLATFORMS.filter((p) => p.test.test(`${dom.generator ?? ''}\n${haystack}`)).map((p) => p.name);
    const assetUrls = desktopVisit.sizes.filter((s) => s.type === 'script').map((s) => s.url).join('\n');
    const libraries = LIBRARIES.filter((l) => l.test.test(assetUrls)).map((l) => l.name);
    const heavyImages = desktopVisit.sizes.filter((s) => s.type === 'image' && s.bytes > HEAVY_IMAGE_BYTES).sort((a, b) => b.bytes - a.bytes);

    // 2. Archivos de visibilidad (robots, sitemap, llms.txt, 404).
    const origin = new URL(finalUrl).origin;
    const page = desktopVisit.page;
    const robots = await fetchStatus(page, `${origin}/robots.txt`);
    const sitemapFromRobots = robots.sample?.match(/^\s*sitemap:\s*(\S+)/im)?.[1];
    const sitemap = await fetchStatus(page, sitemapFromRobots ?? `${origin}/sitemap.xml`);
    const llms = await fetchStatus(page, `${origin}/llms.txt`);
    const notFound = await fetchStatus(page, `${origin}/nexar-diagnostico-${Date.now()}`);
    await desktopVisit.context.close();

    // 3. Visita mobile con throttling: métricas reales de un celular promedio.
    const mobileVisit = await measureVisit(browser, url, VIEWPORTS[0], { throttle: true });
    await mobileVisit.context.close();

    // 4. Screenshots en los 4 anchos de la QA Nexar: primer pantallazo, recorrido
    // scrolleando (mobile y desktop) y página completa. El recorrido importa en webs
    // con animaciones por scroll, donde la captura de página completa sale vacía.
    const screens = [];
    for (const viewport of VIEWPORTS) {
      const context = await browser.newContext({ viewport: { width: viewport.width, height: viewport.height }, isMobile: viewport.mobile, hasTouch: viewport.mobile, deviceScaleFactor: 1 });
      const shotPage = await context.newPage();
      await shotPage.goto(url, { waitUntil: 'load', timeout: NAV_TIMEOUT_MS });
      await shotPage.waitForTimeout(SETTLE_MS);
      const fold = join(outDir, 'screens', `${viewport.name}-fold.png`);
      const full = join(outDir, 'screens', `${viewport.name}-full.png`);
      await shotPage.screenshot({ path: fold });
      const withScroll = viewport.name === 'mobile-390' || viewport.name === 'desktop-1440';
      const scroll = await scrollThrough(shotPage, withScroll ? join(outDir, 'screens', `${viewport.name}-scroll`) : null);
      await shotPage.screenshot({ path: full, fullPage: true });
      screens.push({ viewport: viewport.name, fold, scroll, full });
      await context.close();
    }

    const pick = (h, k) => h[k] ?? null;
    const security = Object.fromEntries(['strict-transport-security', 'content-security-policy', 'x-content-type-options', 'x-frame-options', 'referrer-policy', 'server'].map((k) => [k, pick(headers, k)]));
    const evidence = {
      url,
      finalUrl,
      auditedAt: new Date().toISOString(),
      status: desktopVisit.response?.status() ?? null,
      platform,
      libraries,
      tracking,
      security,
      files: { robots, sitemap, llms, notFound },
      desktop: { loadMs: desktopVisit.loadMs, vitals: desktopVisit.vitals, weight: weightOf(desktopVisit.sizes), heavyImages: heavyImages.map(({ url: u, bytes }) => ({ url: u, bytes })) },
      mobile: { loadMs: mobileVisit.loadMs, vitals: mobileVisit.vitals, weight: weightOf(mobileVisit.sizes), conditions: { ...MOBILE_NETWORK, cpuSlowdown: MOBILE_CPU_SLOWDOWN } },
      dom: { ...dom, htmlSample: undefined, images: dom.images.slice(0, 60) },
      screens,
    };
    evidence.checks = buildChecks({ ...evidence, dom });

    writeFileSync(join(outDir, 'evidence.json'), JSON.stringify(evidence, null, 2));

    const icon = { ok: 'OK  ', warn: 'WARN', fail: 'FAIL', unknown: '??  ' };
    const lines = [`Diagnóstico Nexar · ${finalUrl} · ${evidence.auditedAt}`, `Plataforma: ${platform.join(', ') || 'no identificada'} · Librerías: ${libraries.join(', ') || 'ninguna detectada'} · Hosting: ${security.server ?? 'no informado'} · Medición: ${tracking.join(', ') || 'ninguna'}`, ''];
    for (const c of evidence.checks) lines.push(`${icon[c.status]} [${c.area}] ${c.check}: ${c.detail}`);
    const counts = evidence.checks.reduce((acc, c) => ({ ...acc, [c.status]: (acc[c.status] ?? 0) + 1 }), {});
    lines.push('', `Total: ${counts.ok ?? 0} ok · ${counts.warn ?? 0} warn · ${counts.fail ?? 0} fail`, `Evidencia: ${join(outDir, 'evidence.json')}`, `Screenshots: ${join(outDir, 'screens')}`);
    writeFileSync(join(outDir, 'checks.txt'), lines.join('\n'));
    console.log(lines.join('\n'));
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(`Error: ${error.message}`);
  process.exit(1);
});
