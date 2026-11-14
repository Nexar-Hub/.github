'use client';

import { useActionState, useEffect } from 'react';
import { sendContact, type ContactState } from '@/app/actions';
import { EVENTS, track } from '@/lib/analytics';
import { cn } from '@/lib/utils';

const INITIAL_STATE: ContactState = { status: 'idle' };

const inputClass =
  'w-full rounded-md border border-border bg-background px-3 py-2 text-base text-foreground placeholder:text-muted-foreground aria-[invalid=true]:border-destructive';

export function ContactForm(): React.ReactElement {
  const [state, formAction, pending] = useActionState(sendContact, INITIAL_STATE);

  useEffect(() => {
    if (state.status === 'success') track(EVENTS.lead, { form: 'contacto' });
  }, [state.status]);

  if (state.status === 'success') {
    return (
      <p role="status" className="text-lg">
        Gracias. Te respondemos en menos de 48 horas hábiles.
      </p>
    );
  }

  const error = (field: 'name' | 'email' | 'message'): string | undefined => state.fieldErrors?.[field];

  return (
    <form action={formAction} noValidate className="grid gap-5">
      <div className="grid gap-2">
        <label htmlFor="name" className="text-sm font-medium">Nombre</label>
        <input
          id="name"
          name="name"
          autoComplete="name"
          required
          defaultValue={state.values?.name}
          aria-invalid={error('name') ? true : undefined}
          aria-describedby={error('name') ? 'name-error' : undefined}
          className={inputClass}
        />
        {error('name') ? <p id="name-error" className="text-sm text-destructive">{error('name')}</p> : null}
      </div>

      <div className="grid gap-2">
        <label htmlFor="email" className="text-sm font-medium">Email</label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          required
          defaultValue={state.values?.email}
          aria-invalid={error('email') ? true : undefined}
          aria-describedby={error('email') ? 'email-error' : undefined}
          className={inputClass}
        />
        {error('email') ? <p id="email-error" className="text-sm text-destructive">{error('email')}</p> : null}
      </div>

      <div className="grid gap-2">
        <label htmlFor="message" className="text-sm font-medium">¿Qué necesitás?</label>
        <textarea
          id="message"
          name="message"
          rows={5}
          required
          defaultValue={state.values?.message}
          aria-invalid={error('message') ? true : undefined}
          aria-describedby={error('message') ? 'message-error' : undefined}
          className={inputClass}
        />
        {error('message') ? <p id="message-error" className="text-sm text-destructive">{error('message')}</p> : null}
      </div>

      {/* Honeypot anti-spam: invisible para personas y lectores de pantalla. */}
      <div aria-hidden="true" className="absolute -left-[9999px] h-px w-px overflow-hidden">
        <label htmlFor="website">No completar</label>
        <input id="website" name="website" type="text" tabIndex={-1} autoComplete="off" />
      </div>

      {state.status === 'error' && state.message ? (
        <p role="alert" className="text-sm text-destructive">{state.message}</p>
      ) : null}

      <button
        type="submit"
        aria-disabled={pending}
        className={cn(
          'inline-flex h-11 items-center justify-center rounded-md bg-primary px-6 font-medium text-primary-foreground transition-opacity',
          pending && 'pointer-events-none opacity-60',
        )}
      >
        {pending ? 'Enviando…' : 'Enviar'}
      </button>
    </form>
  );
}
