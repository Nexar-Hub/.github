import Link from 'next/link';
import { TrackedLink } from '@/components/analytics/TrackedLink';
import { site } from '@/content/site';
import { EVENTS } from '@/lib/analytics';

export function Header(): React.ReactElement {
  return (
    <header className="mx-auto flex max-w-6xl items-center justify-between px-4 py-5 md:px-8">
      <Link href="/" className="font-semibold tracking-tight">
        {site.name}
      </Link>
      <TrackedLink
        href="/#contacto"
        event={EVENTS.ctaClick}
        params={{ location: 'header' }}
        className="inline-flex h-10 items-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground"
      >
        Hablemos
      </TrackedLink>
    </header>
  );
}
