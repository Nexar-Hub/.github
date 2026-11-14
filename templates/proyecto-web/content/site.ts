// Datos del sitio. Se completan desde BRIEF.md. Es la única fuente para metadata,
// sitemap, robots, llms.txt y JSON-LD: no repetir estos datos en otros archivos.

export interface SiteConfig {
  name: string;
  tagline: string;
  description: string;
  url: string;
  lang: string;
  locale: string;
  ogImage: string;
  contact: {
    email: string;
    whatsapp: string | null;
  };
  social: string[];
}

export const site: SiteConfig = {
  name: 'Marca',
  tagline: 'Reemplazar por el claim del hero',
  description:
    'Reemplazar por la frase del brief: qué hace la marca, para quién y por qué elegirla, en 70 a 160 caracteres.',
  url: (process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000').replace(/\/$/, ''),
  lang: 'es',
  locale: 'es_AR',
  ogImage: '/og.png',
  contact: {
    email: 'hola@dominio.com',
    // Formato internacional sin "+" ni espacios, ej: 5491100000000. null = sin WhatsApp.
    whatsapp: null,
  },
  social: [],
};
