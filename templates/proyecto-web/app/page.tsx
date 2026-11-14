import type { Metadata } from 'next';
import { TrackedLink } from '@/components/analytics/TrackedLink';
import { ContactForm } from '@/components/contact/ContactForm';
import { site } from '@/content/site';
import { EVENTS } from '@/lib/analytics';

export const metadata: Metadata = {
  alternates: { canonical: '/' },
};

export default function HomePage(): React.ReactElement {
  const whatsappHref = site.contact.whatsapp ? `https://wa.me/${site.contact.whatsapp}` : null;

  return (
    <main id="contenido">
      <section className="mx-auto max-w-6xl px-4 pb-24 pt-16 md:px-8 md:pt-28">
        <h1 className="max-w-4xl text-5xl font-semibold tracking-tight md:text-7xl">{site.tagline}</h1>
        <p className="mt-6 max-w-2xl text-lg text-muted-foreground md:text-xl">{site.description}</p>
        <div className="mt-10 flex flex-wrap gap-3">
          <TrackedLink
            href="#contacto"
            event={EVENTS.ctaClick}
            params={{ location: 'hero' }}
            className="inline-flex h-11 items-center rounded-md bg-primary px-6 font-medium text-primary-foreground"
          >
            Contanos tu proyecto
          </TrackedLink>
          {whatsappHref ? (
            <TrackedLink
              href={whatsappHref}
              event={EVENTS.whatsappClick}
              params={{ location: 'hero' }}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex h-11 items-center rounded-md border border-border px-6 font-medium"
            >
              WhatsApp
            </TrackedLink>
          ) : null}
        </div>
      </section>

      {/* Las secciones del proyecto se construyen acá, una por una (WORKFLOW.md, fase 2). */}

      <section id="contacto" aria-labelledby="contacto-titulo" className="border-t border-border">
        <div className="mx-auto grid max-w-6xl gap-10 px-4 py-20 md:grid-cols-2 md:px-8">
          <div>
            <h2 id="contacto-titulo" className="text-3xl font-semibold tracking-tight md:text-4xl">
              Contanos tu proyecto
            </h2>
            <p className="mt-4 text-muted-foreground">
              Te respondemos en menos de 48 horas hábiles. También podés escribir a{' '}
              <a href={`mailto:${site.contact.email}`} className="underline underline-offset-4">
                {site.contact.email}
              </a>
              .
            </p>
          </div>
          <ContactForm />
        </div>
      </section>
    </main>
  );
}
