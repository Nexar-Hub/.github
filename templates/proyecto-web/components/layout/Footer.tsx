import { site } from '@/content/site';

export function Footer(): React.ReactElement {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto flex max-w-6xl flex-wrap justify-between gap-4 px-4 py-8 text-sm text-muted-foreground md:px-8">
        <p>
          © {new Date().getFullYear()} {site.name}
        </p>
        <a href={`mailto:${site.contact.email}`} className="underline-offset-4 hover:underline">
          {site.contact.email}
        </a>
      </div>
    </footer>
  );
}
