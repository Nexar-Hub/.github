// Capturas reales de la interfaz de OpenTodo (Día / Semana) y la Replanificación nativa.
// Uso: node capturas.mjs <nombre> <ruta> [replan]
//   ruta: /week/2026-11-23, /day/2026-11-24, /day ...
//   replan: además pulsa «Replanificar», captura la vista previa, aplica y captura el resultado.
import { createRequire } from 'node:module'
const require = createRequire(import.meta.url)
const { chromium } = require('playwright')

const [, , nombre, ruta, modo] = process.argv
const B = process.env.B || 'http://127.0.0.1:8080'
const OUT = process.env.CAPTURAS || '.'

const browser = await chromium.launch()
const ctx = await browser.newContext({
  baseURL: B, locale: 'es-AR', timezoneId: 'America/Argentina/Buenos_Aires',
  viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2, colorScheme: 'light',
})
const r = await ctx.request.post('/api/v1/auth/login', {
  headers: { Origin: B }, data: { email: 'persona@sandbox.local', password: 'Sandbox-Pass-2026!' },
})
if (!r.ok()) { console.error('login', r.status(), await r.text()); process.exit(1) }
const page = await ctx.newPage()
// grilla de 8 a 20 h para que entre la jornada (ajuste por dispositivo de OpenTodo)
await page.addInitScript(() => {
  try { localStorage.setItem('opentodo.onboarding.done', '1') } catch {}
})
await page.goto(ruta, { waitUntil: 'networkidle' })
await page.waitForTimeout(2500)
for (const t of ['Ahora no', 'Not now', 'Omitir', 'Skip', 'Cerrar', 'Entendido']) {
  const b = page.getByRole('button', { name: t, exact: true })
  if (await b.count()) { await b.first().click().catch(() => {}) }
}
await page.keyboard.press('Escape').catch(() => {})
await page.waitForTimeout(800)
if (modo && modo.startsWith('filtro:')) {
  // Filtro nativo del calendario: Más acciones → Filtrar… → consulta (se guarda en este dispositivo)
  await page.getByRole('button', { name: 'Más acciones' }).first().click()
  await page.getByRole('menuitem', { name: /Filtrar/ }).first().click()
  const q = page.getByRole('textbox', { name: /Consulta/ }).or(page.getByRole('textbox')).first()
  await q.fill(modo.slice('filtro:'.length))
  await page.waitForTimeout(1200)
  await page.keyboard.press('Escape')
  await page.waitForTimeout(800)
}
await page.screenshot({ path: `${OUT}/${nombre}.png`, fullPage: false })
console.log(`${OUT}/${nombre}.png`)

if (modo === 'replan') {
  const btn = page.getByRole('button', { name: /Replanificar/ }).first()
  await btn.waitFor({ timeout: 15000 })
  await btn.click()
  await page.waitForTimeout(1500)
  await page.screenshot({ path: `${OUT}/${nombre}-vista-previa.png` })
  console.log(`${OUT}/${nombre}-vista-previa.png`)
  await page.getByRole('button', { name: /^Aplicar/ }).first().click()
  await page.waitForTimeout(2000)
  await page.screenshot({ path: `${OUT}/${nombre}-aplicado.png` })
  console.log(`${OUT}/${nombre}-aplicado.png`)
}
await browser.close()
