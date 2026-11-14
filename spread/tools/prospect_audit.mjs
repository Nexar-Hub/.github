#!/usr/bin/env node
/**
 * Spread · Auditoría de evidencia por prospecto.
 *
 * La biblia exige que el encuadre de pérdida (palanca 2) se apoye en datos del
 * propio prospecto. Esta herramienta los mide: abre la web del prospecto en un
 * navegador real (escritorio y celular), revisa robots.txt, links, velocidad,
 * llamadas a la acción, metadatos y el copy (con copy_audit.py), y devuelve:
 *
 *   report.md      reporte en castellano con evidencia, capturas e hipótesis
 *   findings.json  los mismos datos, para automatizar
 *   desktop.png    primera pantalla en escritorio (1440 × 900)
 *   mobile.png     primera pantalla en celular (iPhone 13)
 *
 * y un primer mensaje de outbound (ES/EN) armado SOLO con hallazgos medidos.
 * Si no hay pérdidas medibles, no propone mensaje: sin evidencia no hay
 * encuadre de pérdida.
 *
 * Uso:
 *   node spread/tools/prospect_audit.mjs https://prospecto.com
 *   node spread/tools/prospect_audit.mjs https://prospecto.com --out audits/prospecto --max-links 20
 *   node spread/tools/prospect_audit.mjs https://prospecto.com --no-links
 *
 * Requiere Node 18+ y Playwright con Chromium (npm i playwright && npx playwright install chromium)
 * y acceso directo a internet hacia el sitio auditado.
 */

import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const require = createRequire(import.meta.url);
const HERE = path.dirname(fileURLToPath(import.meta.url));
const COPY_AUDIT = path.join(HERE, 'copy_audit.py');
const PLAYBOOK = 'spread/bible/PLAYBOOK.md';

// Rastreadores de asistentes de IA. "search" y "user" alimentan respuestas en vivo;
// "training" alimenta el entrenamiento de modelos.
export const AI_BOTS = [
  { ua: 'OAI-SearchBot', owner: 'OpenAI', purpose: 'search' },
  { ua: 'ChatGPT-User', owner: 'OpenAI', purpose: 'user' },
  { ua: 'GPTBot', owner: 'OpenAI', purpose: 'training' },
  { ua: 'Claude-SearchBot', owner: 'Anthropic', purpose: 'search' },
  { ua: 'Claude-User', owner: 'Anthropic', purpose: 'user' },
  { ua: 'ClaudeBot', owner: 'Anthropic', purpose: 'training' },
  { ua: 'PerplexityBot', owner: 'Perplexity', purpose: 'search' },
  { ua: 'Google-Extended', owner: 'Google', purpose: 'training' },
  { ua: 'CCBot', owner: 'Common Crawl', purpose: 'training' },
];

const SEVERITY = { alta: 3, media: 2, baja: 1 };
const LCP_GOOD_MS = 2500; // umbral de Core Web Vitals para "bueno"
const LCP_POOR_MS = 4000; // umbral para "malo"
const MAX_FORM_FIELDS = 6;

// --------------------------------------------------------------------------
// robots.txt
// --------------------------------------------------------------------------
export function parseRobots(text) {
  const groups = [];
  let cur = null;
  let lastWasAgent = false;
  for (const raw of String(text || '').split(/\r?\n/)) {
    const line = raw.replace(/#.*$/, '').trim();
    const m = line.match(/^([A-Za-z-]+)\s*:\s*(.*)$/);
    if (!m) continue;
    const key = m[1].toLowerCase();
    const val = m[2].trim();
    if (key === 'user-agent') {
      if (!cur || !lastWasAgent) {
        cur = { agents: [], rules: [] };
        groups.push(cur);
      }
      cur.agents.push(val.toLowerCase());
      lastWasAgent = true;
    } else {
      lastWasAgent = false;
      if (cur && (key === 'allow' || key === 'disallow')) cur.rules.push({ type: key, path: val });
    }
  }
  return groups;
}

/** True when the agent may not fetch the site root ("/"). */
export function rootBlocked(groups, ua) {
  const token = ua.toLowerCase();
  let matched = groups.filter((g) => g.agents.includes(token));
  if (!matched.length) matched = groups.filter((g) => g.agents.includes('*'));
  const rules = matched.flatMap((g) => g.rules);
  const disallowed = rules.some((r) => r.type === 'disallow' && r.path === '/');
  const allowed = rules.some((r) => r.type === 'allow' && r.path === '/');
  return disallowed && !allowed;
}

// --------------------------------------------------------------------------
// Findings (pure: raw measurements in, findings out)
// --------------------------------------------------------------------------
const listEs = (xs) => (xs.length < 2 ? xs.join('') : `${xs.slice(0, -1).join(', ')} y ${xs.at(-1)}`);
const listEn = (xs) => (xs.length < 2 ? xs.join('') : `${xs.slice(0, -1).join(', ')} and ${xs.at(-1)}`);
const secs = (ms) => (ms / 1000).toFixed(1);

export function buildFindings(raw) {
  const f = [];
  const add = (x) => f.push(x);
  const d = raw.desktop || {};
  const m = raw.mobile || {};

  // robots.txt
  const groups = raw.robots && raw.robots.status === 200 ? parseRobots(raw.robots.text) : [];
  if (rootBlocked(groups, 'Googlebot') && rootBlocked(groups, 'Bingbot')) {
    add({
      id: 'ROBOTS_BLOCK_ALL', severity: 'alta', lever: '2 · Punto de referencia',
      title: 'robots.txt bloquea a todos los buscadores',
      evidence: 'robots.txt: `User-agent: *` con `Disallow: /`',
      loss: {
        es: 'Tu robots.txt le pide a todos los buscadores que no lean tu sitio.',
        en: 'Your robots.txt asks every search engine not to read your site.',
      },
      fix: 'Revisar si es intencional (sitio de staging publicado por error es el caso típico).',
    });
  } else {
    const blocked = AI_BOTS.filter((b) => rootBlocked(groups, b.ua));
    if (blocked.length) {
      const live = blocked.filter((b) => b.purpose !== 'training');
      const owners = [...new Set((live.length ? live : blocked).map((b) => b.owner))];
      add({
        id: 'AI_BOTS_BLOCKED', severity: live.length ? 'alta' : 'media', lever: '2 · Punto de referencia',
        title: 'robots.txt bloquea rastreadores de asistentes de IA',
        evidence: `Bloqueados en la raíz: ${blocked.map((b) => `${b.ua} (${b.purpose})`).join(', ')}`,
        loss: live.length
          ? {
            es: `Tu robots.txt bloquea a ${listEs(live.map((b) => b.ua))}, ${live.length === 1 ? 'el rastreador' : 'los rastreadores'} que ${owners.length === 1 ? 'usa' : 'usan'} ${listEs(owners)} para responder búsquedas en vivo.`,
            en: `Your robots.txt blocks ${listEn(live.map((b) => b.ua))}, ${live.length === 1 ? 'the crawler' : 'the crawlers'} ${listEn(owners)} ${owners.length === 1 ? 'uses' : 'use'} to answer live searches.`,
          }
          : {
            es: `Tu robots.txt bloquea a ${listEs(blocked.map((b) => b.ua))} (${listEs(owners)}).`,
            en: `Your robots.txt blocks ${listEn(blocked.map((b) => b.ua))} (${listEn(owners)}).`,
          },
        fix: 'Decidir con el cliente qué rastreadores de IA quiere permitir; los de búsqueda definen si puede ser citado.',
      });
    }
  }

  if (raw.status && raw.status >= 400) {
    add({
      id: 'HOME_ERROR', severity: 'alta', lever: '2 · Punto de referencia',
      title: `La home responde ${raw.status}`, evidence: `HTTP ${raw.status} en ${raw.finalUrl || raw.url}`,
      loss: { es: `Tu home responde con error ${raw.status}.`, en: `Your homepage returns a ${raw.status} error.` },
      fix: 'Revisar el servidor o el dominio.',
    });
  }

  // Mobile layout
  if (m.viewportMeta === false) {
    add({
      id: 'NO_MOBILE_VIEWPORT', severity: 'alta', lever: '2 · Punto de referencia',
      title: 'La home no está adaptada a celular',
      evidence: 'No hay `<meta name="viewport">`: el celular muestra la versión de escritorio achicada (ver mobile.png)',
      loss: {
        es: 'Tu home no está adaptada a celular: en el teléfono se ve la versión de escritorio achicada.',
        en: "Your homepage isn't set up for phones: on mobile it shows a shrunken desktop version.",
      },
      fix: 'Agregar meta viewport y revisar el layout responsive.',
    });
  } else if (m.scrollW && m.viewportW && m.scrollW > m.viewportW + 2) {
    add({
      id: 'MOBILE_OVERFLOW', severity: 'alta', lever: '2 · Punto de referencia',
      title: 'En celular la página se corre de costado',
      evidence: `Ancho del documento ${m.scrollW} px en una pantalla de ${m.viewportW} px (ver mobile.png)`,
      loss: {
        es: `En un celular (${m.viewportW} px de ancho) tu home mide ${m.scrollW} px: el contenido se corre de costado.`,
        en: `On a phone (${m.viewportW} px wide) your homepage is ${m.scrollW} px wide, so content spills sideways.`,
      },
      fix: 'Encontrar el elemento con ancho fijo y hacerlo fluido.',
    });
  }

  // Calls to action
  const fold = (v) => (v.ctas || []).filter((c) => c.top < (v.viewportH || 0));
  const anyCta = (d.ctas || []).length || (m.ctas || []).length;
  if (!anyCta) {
    add({
      id: 'NO_CTA', severity: 'alta', lever: '2 + certeza',
      title: 'No hay llamada a la acción en la home',
      evidence: 'Ningún botón o link visible con texto de demo, contacto, empezar o similar',
      loss: {
        es: 'Tu home no tiene ningún botón para pedir una demo o contactarte.',
        en: "Your homepage has no button to book a demo or get in touch.",
      },
      fix: 'Un CTA principal claro, repetido arriba y al final.',
    });
  } else {
    if (!fold(m).length) {
      add({
        id: 'NO_CTA_MOBILE_FOLD', severity: 'media', lever: '2 + certeza',
        title: 'Sin llamada a la acción en la primera pantalla del celular',
        evidence: `Primer CTA en celular: «${(m.ctas || [])[0]?.text || '—'}» a ${Math.round((m.ctas || [])[0]?.top ?? 0)} px (pantalla de ${m.viewportH} px)`,
        loss: {
          es: 'En la primera pantalla del celular no hay ningún botón para avanzar.',
          en: "On a phone, the first screen has no button to take the next step.",
        },
        fix: 'Llevar el CTA principal a la primera pantalla en mobile.',
      });
    }
    if (!fold(d).length) {
      add({
        id: 'NO_CTA_DESKTOP_FOLD', severity: 'media', lever: '2 + certeza',
        title: 'Sin llamada a la acción en la primera pantalla de escritorio',
        evidence: `Primer CTA en escritorio: «${(d.ctas || [])[0]?.text || '—'}» a ${Math.round((d.ctas || [])[0]?.top ?? 0)} px (pantalla de ${d.viewportH} px)`,
        loss: {
          es: 'En la primera pantalla de tu home no hay ningún botón para avanzar.',
          en: "Your homepage's first screen has no button to take the next step.",
        },
        fix: 'Llevar el CTA principal al hero.',
      });
    }
  }

  // Speed
  if (typeof d.lcp === 'number' && d.lcp > LCP_GOOD_MS) {
    add({
      id: 'SLOW_LCP', severity: d.lcp > LCP_POOR_MS ? 'alta' : 'media', lever: '2 · Punto de referencia',
      title: 'El contenido principal tarda en aparecer',
      evidence: `LCP ${secs(d.lcp)} s en escritorio (medición de laboratorio; umbral "bueno" de Google: ${secs(LCP_GOOD_MS)} s)`,
      loss: {
        es: `El contenido principal de tu home tarda ${secs(d.lcp)} s en aparecer; Google considera bueno hasta ${secs(LCP_GOOD_MS)} s.`,
        en: `Your homepage's main content takes ${secs(d.lcp)} s to appear; Google rates up to ${secs(LCP_GOOD_MS)} s as good.`,
      },
      fix: 'Optimizar la imagen o el bloque más grande del hero y el JavaScript que lo bloquea.',
    });
  }

  // Broken links
  const broken = raw.brokenLinks || [];
  if (broken.length) {
    const ex = broken.slice(0, 3).map((b) => `${b.url.replace(/^https?:\/\/[^/]+/, '') || '/'} → ${b.status}`);
    add({
      id: 'BROKEN_LINKS', severity: 'alta', lever: '2 · Punto de referencia',
      title: 'Links rotos en la home',
      evidence: `${broken.length} de ${raw.checkedLinks} links internos revisados dan error: ${ex.join(', ')}`,
      loss: {
        es: `${broken.length} ${broken.length === 1 ? 'link' : 'links'} de tu home ${broken.length === 1 ? 'da' : 'dan'} error (${ex.join(', ')}).`,
        en: `${broken.length} ${broken.length === 1 ? 'link' : 'links'} on your homepage ${broken.length === 1 ? 'is' : 'are'} broken (${ex.join(', ')}).`,
      },
      fix: 'Corregir o redirigir cada URL.',
    });
  }

  // JavaScript errors
  const errs = raw.consoleErrors || [];
  if (errs.length) {
    add({
      id: 'CONSOLE_ERRORS', severity: 'media', lever: '2 · Punto de referencia',
      title: 'Errores de JavaScript al cargar',
      evidence: `${errs.length} ${errs.length === 1 ? 'error' : 'errores'}; primero: ${errs[0]}`,
      loss: {
        es: `Tu home tira ${errs.length} ${errs.length === 1 ? 'error' : 'errores'} de JavaScript al cargar.`,
        en: `Your homepage throws ${errs.length} JavaScript ${errs.length === 1 ? 'error' : 'errors'} on load.`,
      },
      fix: 'Revisar la consola y priorizar los errores que rompen formularios o tracking.',
    });
  }

  // Resources that fail to load (images, scripts, styles)
  const failed = raw.failedResources || [];
  if (failed.length) {
    const ex = failed.slice(0, 3).map((r) => `${r.url.replace(/^https?:\/\/[^/]+/, '')} → ${r.status}`);
    add({
      id: 'FAILED_RESOURCES', severity: 'media', lever: '2 · Punto de referencia',
      title: 'Recursos que no cargan',
      evidence: `${failed.length} ${failed.length === 1 ? 'recurso falla' : 'recursos fallan'} al cargar la home: ${ex.join(', ')}`,
      loss: {
        es: `${failed.length} ${failed.length === 1 ? 'archivo' : 'archivos'} de tu home (imágenes, scripts o estilos) no ${failed.length === 1 ? 'carga' : 'cargan'}.`,
        en: `${failed.length} ${failed.length === 1 ? 'file' : 'files'} on your homepage (images, scripts or styles) ${failed.length === 1 ? 'fails' : 'fail'} to load.`,
      },
      fix: 'Restaurar o quitar cada recurso roto.',
    });
  }

  // Sharing and search metadata
  if (!d.ogImage) {
    add({
      id: 'MISSING_OG_IMAGE', severity: 'media', lever: '2 · Punto de referencia',
      title: 'Sin imagen de vista previa para compartir',
      evidence: 'No hay `<meta property="og:image">`',
      loss: {
        es: 'Tu home no define imagen de vista previa: en LinkedIn, X o WhatsApp tu link puede aparecer sin imagen.',
        en: "Your homepage defines no preview image, so your link can show up without one on LinkedIn, X or WhatsApp.",
      },
      fix: 'Agregar og:image (1200 × 630) y og:title.',
    });
  }
  if (!d.title) {
    add({
      id: 'MISSING_TITLE', severity: 'media', lever: '—', title: 'Sin título de página',
      evidence: '`<title>` vacío o ausente', loss: null, fix: 'Agregar un título con la categoría y el beneficio.',
    });
  }
  if (!d.description) {
    add({
      id: 'MISSING_META_DESCRIPTION', severity: 'baja', lever: '—', title: 'Sin meta description',
      evidence: 'No hay `<meta name="description">`', loss: null, fix: 'Escribir una descripción con el beneficio principal.',
    });
  }
  if (d.h1 !== undefined && d.h1 !== 1) {
    add({
      id: 'H1_COUNT', severity: 'baja', lever: '—', title: d.h1 ? `${d.h1} títulos H1` : 'Sin título H1',
      evidence: `${d.h1} elementos \`<h1>\``, loss: null, fix: 'Un único H1 con la propuesta principal.',
    });
  }
  if (d.jsonLd === 0) {
    add({
      id: 'NO_STRUCTURED_DATA', severity: 'baja', lever: '—', title: 'Sin datos estructurados',
      evidence: 'No hay `<script type="application/ld+json">`', loss: null,
      fix: 'Agregar Organization y, si aplica, Product o SoftwareApplication.',
    });
  }

  // Forms
  const longest = Math.max(0, ...(d.forms || []));
  if (longest > MAX_FORM_FIELDS) {
    add({
      id: 'LONG_FORM', severity: 'media', lever: 'R2 · Juntá las pérdidas',
      title: 'Formulario largo',
      evidence: `El formulario más largo pide ${longest} campos`,
      loss: {
        es: `Tu formulario pide ${longest} campos antes de que alguien pueda hablar con ustedes.`,
        en: `Your form asks for ${longest} fields before anyone can talk to you.`,
      },
      fix: 'Pedir solo lo necesario para agendar; enriquecer el resto después.',
    });
  }

  return f.sort((a, b) => SEVERITY[b.severity] - SEVERITY[a.severity]);
}

export function buildOpener(findings, host) {
  const usable = findings.filter((x) => x.loss).slice(0, 2);
  if (!usable.length) return null;
  return {
    es: `Hola {nombre}: revisé ${host}. ${usable.map((x) => x.loss.es).join(' ')} Armé un reporte corto con capturas y cómo resolverlo. ¿Te lo paso?`,
    en: `Hi {name}, I ran ${host} through a quick check. ${usable.map((x) => x.loss.en).join(' ')} I put together a short report with screenshots and fixes. Want me to send it over?`,
    basedOn: usable.map((x) => x.id),
  };
}

// --------------------------------------------------------------------------
// Copy hypotheses (reuses the bible's auditor)
// --------------------------------------------------------------------------
export function runCopyAudit(text) {
  if (!text || !text.trim()) return [];
  const py = process.env.PYTHON || 'python3';
  const r = spawnSync(py, [COPY_AUDIT, '-', '--format', 'json'], { input: text, encoding: 'utf-8' });
  if (r.status !== 0 || !r.stdout) return [];
  try {
    const seen = new Set();
    return JSON.parse(r.stdout).findings.filter((x) => {
      const key = `${x.rule}|${x.excerpt}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  } catch {
    return [];
  }
}

// --------------------------------------------------------------------------
// Report
// --------------------------------------------------------------------------
export function renderReport(audit) {
  const { url, host, date, findings, opener, copy, checkedLinks } = audit;
  const counts = Object.keys(SEVERITY).map((s) => `${findings.filter((x) => x.severity === s).length} ${s}`).join(' · ');
  const out = [
    `# Auditoría de evidencia · ${host}`,
    '',
    `- **URL:** ${url}`,
    `- **Fecha:** ${date}`,
    `- **Hallazgos:** ${findings.length} (${counts})`,
    `- **Links internos revisados:** ${checkedLinks}`,
    '',
    '> Mediciones de laboratorio desde un solo entorno; pueden variar con la red y el dispositivo.',
    '> Verificá cada dato antes de usarlo con el prospecto (biblia de Spread, límites éticos).',
    '',
    '## Lo que está perdiendo',
    '',
  ];
  if (!findings.length) {
    out.push('No encontramos pérdidas medibles. **No uses encuadre de pérdida con este prospecto**: sin evidencia, no hay palanca 2.', '');
  } else {
    out.push('| Severidad | Hallazgo | Evidencia | Palanca |', '|---|---|---|---|');
    for (const x of findings) out.push(`| ${x.severity} | ${x.title} | ${x.evidence.replace(/\|/g, '\\|')} | ${x.lever} |`);
    out.push('');
    for (const x of findings) {
      out.push(`### ${x.title}`, '', `- **Evidencia:** ${x.evidence}`);
      if (x.loss) out.push(`- **Cómo decirlo:** ${x.loss.es}`, `- **In English:** ${x.loss.en}`);
      out.push(`- **Arreglo:** ${x.fix}`, '');
    }
  }
  out.push('## Capturas', '', '| Escritorio (1440 × 900) | Celular (iPhone 13) |', '|---|---|',
    '| ![Escritorio](desktop.png) | ![Celular](mobile.png) |', '');
  out.push('## Hipótesis sobre su copy', '');
  if (!copy.length) {
    out.push('El auditor de copy no encontró hipótesis en el texto visible de la home.', '');
  } else {
    out.push(`Del auditor de la biblia (\`spread/tools/copy_audit.py\`) sobre el texto visible. Son hipótesis para su web, no errores.`, '');
    for (const c of copy.slice(0, 8)) out.push(`- **${c.rule} · ${c.title}:** «${c.excerpt}». ${c.suggestion}`);
    out.push('');
  }
  out.push('## Primer mensaje de outbound', '');
  if (!opener) {
    out.push('Sin hallazgos con pérdida medible: no hay mensaje sugerido.', '');
  } else {
    out.push(`Basado solo en: ${opener.basedOn.join(', ')}. Reemplazá {nombre} y revisá el tono antes de enviar.`, '',
      '**ES**', '', `> ${opener.es}`, '', '**EN**', '', `> ${opener.en}`, '',
      'El reporte completo se ofrece como regalo aparte (R4) y es la prueba del trabajo: no hace falta ningún caso inventado.', '');
  }
  out.push('---', '', `Generado con \`spread/tools/prospect_audit.mjs\`. Marco: \`${PLAYBOOK}\`.`, '');
  return out.join('\n');
}

// --------------------------------------------------------------------------
// Browser measurements
// --------------------------------------------------------------------------
const LCP_SCRIPT = `
  window.__lcp = null;
  try {
    new PerformanceObserver((list) => {
      for (const e of list.getEntries()) window.__lcp = e.startTime;
    }).observe({ type: 'largest-contentful-paint', buffered: true });
  } catch (e) {}
`;

/* Runs inside the page. */
function collectInPage() {
  const q = (s) => document.querySelector(s);
  const meta = (n) => (q(`meta[name="${n}"]`)?.content || '').trim();
  const prop = (p) => (q(`meta[property="${p}"]`)?.content || '').trim();
  const EN = /\b(book a demo|demo|contact(?: us)?|book|schedule|get started|start(?: now| free| today)?|try(?: it)?(?: free)?|sign ?up|join|request|talk to (?:us|sales)|let'?s talk)\b/i;
  const ES = /(^|\s)(agend[aá]|contact[aá]|contacto|empez[aá]|prob[aá]|registr[aá]te|habl[aá]|solicit[aá]|cotiz[aá]|reserv[aá]|ped[ií])/i;
  const label = (el) => (el.innerText || el.value || el.getAttribute('aria-label') || '').trim();
  const visible = (el) => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && Number(s.opacity) !== 0;
  };
  const ctas = [...document.querySelectorAll('a, button, [role="button"], input[type="submit"]')]
    .filter((el) => { const t = label(el); return t && (EN.test(t) || ES.test(t)) && visible(el); })
    .map((el) => ({ text: label(el).slice(0, 60), top: el.getBoundingClientRect().top + window.scrollY }))
    .sort((a, b) => a.top - b.top);
  const forms = [...document.forms]
    .map((f) => [...f.querySelectorAll('input, select, textarea')]
      .filter((i) => !['hidden', 'submit', 'button', 'reset', 'image'].includes((i.type || '').toLowerCase()) && visible(i)).length)
    .filter((n) => n > 0);
  const here = location.href.split('#')[0];
  const links = [...new Set([...document.querySelectorAll('a[href]')].map((a) => a.href.split('#')[0])
    .filter((h) => { try { const u = new URL(h); return u.origin === location.origin && /^https?:$/.test(u.protocol) && h !== here; } catch (e) { return false; } }))];
  const nav = performance.getEntriesByType('navigation')[0];
  return {
    title: document.title.trim(),
    description: meta('description'),
    ogImage: prop('og:image'),
    ogTitle: prop('og:title'),
    viewportMeta: Boolean(q('meta[name="viewport"]')),
    h1: document.querySelectorAll('h1').length,
    jsonLd: document.querySelectorAll('script[type="application/ld+json"]').length,
    ctas, forms, links,
    // Layout viewport: on mobile, innerWidth grows to fit overflowing content.
    viewportW: document.documentElement.clientWidth,
    viewportH: document.documentElement.clientHeight,
    scrollW: document.documentElement.scrollWidth,
    lcp: typeof window.__lcp === 'number' ? Math.round(window.__lcp) : null,
    load: nav ? Math.round(nav.loadEventEnd) : null,
    text: document.body ? document.body.innerText.slice(0, 20000) : '',
  };
}

async function checkLinks(request, links, max) {
  const broken = [];
  const sample = links.slice(0, max);
  for (const link of sample) {
    let status = 0;
    try {
      let r = await request.head(link, { timeout: 10000, maxRedirects: 5 });
      if ([405, 501].includes(r.status())) r = await request.get(link, { timeout: 10000, maxRedirects: 5 });
      status = r.status();
    } catch {
      status = 0;
    }
    if (status === 0 || status >= 400) broken.push({ url: link, status: status || 'sin respuesta' });
  }
  return { broken, checked: sample.length };
}

export async function runAudit(url, { outDir, maxLinks = 15, links = true, timeout = 30000 } = {}) {
  let playwright;
  try {
    playwright = require('playwright');
  } catch {
    throw new Error('Falta Playwright: npm i playwright && npx playwright install chromium');
  }
  const { chromium, devices } = playwright;
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  try {
    const desktopCtx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    await desktopCtx.addInitScript(LCP_SCRIPT);
    const page = await desktopCtx.newPage();
    const consoleErrors = [];
    const failedResources = [];
    page.on('console', (msg) => {
      // Failed network loads are reported separately as FAILED_RESOURCES.
      if (msg.type() === 'error' && !/^Failed to load resource/.test(msg.text())) consoleErrors.push(msg.text().slice(0, 200));
    });
    page.on('response', (r) => { if (r.status() >= 400 && r.request().resourceType() !== 'document') failedResources.push({ url: r.url(), status: r.status() }); });
    page.on('requestfailed', (req) => { if (req.resourceType() !== 'document') failedResources.push({ url: req.url(), status: 'falló' }); });
    page.on('pageerror', (err) => consoleErrors.push(String(err && err.message ? err.message : err).slice(0, 200)));
    const resp = await page.goto(url, { waitUntil: 'load', timeout });
    await page.waitForTimeout(1500);
    const desktop = await page.evaluate(collectInPage);
    await page.screenshot({ path: path.join(outDir, 'desktop.png') });
    const finalUrl = page.url();

    const mobileCtx = await browser.newContext({ ...devices['iPhone 13'] });
    const mPage = await mobileCtx.newPage();
    await mPage.goto(finalUrl, { waitUntil: 'load', timeout });
    await mPage.waitForTimeout(800);
    const mobile = await mPage.evaluate(collectInPage);
    await mPage.screenshot({ path: path.join(outDir, 'mobile.png') });

    let robots = { status: 0, text: '' };
    try {
      const r = await desktopCtx.request.get(new URL('/robots.txt', finalUrl).href, { timeout: 10000 });
      robots = { status: r.status(), text: r.status() === 200 ? await r.text() : '' };
    } catch { /* sin robots.txt */ }

    const linkResult = links ? await checkLinks(desktopCtx.request, desktop.links, maxLinks) : { broken: [], checked: 0 };
    const { text, ...desktopRest } = desktop;
    return {
      url, finalUrl, status: resp ? resp.status() : 0, date: new Date().toISOString().slice(0, 10),
      host: new URL(finalUrl).host,
      desktop: desktopRest, mobile: { ...mobile, text: undefined }, consoleErrors, failedResources, robots,
      brokenLinks: linkResult.broken, checkedLinks: linkResult.checked, text,
    };
  } finally {
    await browser.close();
  }
}

export async function audit(url, opts) {
  const raw = await runAudit(url, opts);
  const findings = buildFindings(raw);
  const copy = runCopyAudit(raw.text);
  const result = {
    url: raw.url, finalUrl: raw.finalUrl, host: raw.host, date: raw.date, status: raw.status,
    checkedLinks: raw.checkedLinks, findings, opener: buildOpener(findings, raw.host), copy,
    measurements: {
      desktop: raw.desktop, mobile: raw.mobile, consoleErrors: raw.consoleErrors,
      failedResources: raw.failedResources, robotsStatus: raw.robots.status,
    },
  };
  fs.writeFileSync(path.join(opts.outDir, 'findings.json'), JSON.stringify(result, null, 2));
  fs.writeFileSync(path.join(opts.outDir, 'report.md'), renderReport(result));
  return result;
}

// --------------------------------------------------------------------------
// CLI
// --------------------------------------------------------------------------
function parseArgs(argv) {
  const a = { links: true, maxLinks: 15 };
  for (let i = 0; i < argv.length; i++) {
    const v = argv[i];
    if (v === '--out') a.outDir = argv[++i];
    else if (v === '--max-links') a.maxLinks = Number(argv[++i]);
    else if (v === '--no-links') a.links = false;
    else if (v === '--timeout') a.timeout = Number(argv[++i]) * 1000;
    else if (v === '-h' || v === '--help') a.help = true;
    else a.url = v;
  }
  return a;
}

async function main() {
  const a = parseArgs(process.argv.slice(2));
  if (a.help || !a.url) {
    console.log('Uso: node spread/tools/prospect_audit.mjs URL [--out DIR] [--max-links N] [--no-links] [--timeout SEG]');
    return a.help ? 0 : 2;
  }
  if (!/^https?:\/\//.test(a.url)) a.url = `https://${a.url}`;
  const host = new URL(a.url).host;
  a.outDir = a.outDir || path.join('audits', `${host}-${new Date().toISOString().slice(0, 10)}`);
  try {
    const r = await audit(a.url, a);
    const top = r.findings.filter((x) => x.loss).slice(0, 3).map((x) => `  - [${x.severity}] ${x.title}`);
    console.log(`${r.findings.length} hallazgos, ${r.copy.length} hipótesis de copy · ${path.join(a.outDir, 'report.md')}`);
    if (top.length) console.log(top.join('\n'));
    return 0;
  } catch (e) {
    console.error(`No se pudo auditar ${a.url}: ${e.message}`);
    return 1;
  }
}

if (import.meta.url === pathToFileURL(process.argv[1] || '').href) {
  main().then((code) => { process.exitCode = code; });
}
