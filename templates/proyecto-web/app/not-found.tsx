import Link from 'next/link';

export default function NotFound(): React.ReactElement {
  return (
    <main id="contenido" className="mx-auto max-w-6xl px-4 py-32 md:px-8">
      <p className="font-mono text-sm text-muted-foreground">404</p>
      <h1 className="mt-4 text-4xl font-semibold tracking-tight">Esta página no existe.</h1>
      <p className="mt-4 text-muted-foreground">Puede que el link esté mal o que la página se haya movido.</p>
      <Link href="/" className="mt-8 inline-flex underline underline-offset-4">
        Volver al inicio
      </Link>
    </main>
  );
}
