import { site } from '@/content/site';

// /llms.txt: resumen legible para motores de IA (GEO). Se genera desde content/site.ts.
export const dynamic = 'force-static';

export function GET(): Response {
  const lines = [
    `# ${site.name}`,
    '',
    `> ${site.description}`,
    '',
    '## Páginas',
    `- [Inicio](${site.url}/): ${site.tagline}`,
    '',
    '## Contacto',
    `- Email: ${site.contact.email}`,
    ...(site.contact.whatsapp ? [`- WhatsApp: https://wa.me/${site.contact.whatsapp}`] : []),
    `- Formulario: ${site.url}/#contacto`,
    '',
  ];
  return new Response(lines.join('\n'), {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
}
