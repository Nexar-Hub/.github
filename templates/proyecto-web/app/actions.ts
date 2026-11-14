'use server';

import { z } from 'zod';
import { site } from '@/content/site';

const RESEND_ENDPOINT = 'https://api.resend.com/emails';
const MAX_MESSAGE_LENGTH = 2000;

const ContactSchema = z.object({
  name: z.string().trim().min(2, 'Escribí tu nombre.').max(100, 'El nombre es demasiado largo.'),
  email: z.email('Revisá el email.'),
  message: z
    .string()
    .trim()
    .min(10, 'Contanos un poco más (mínimo 10 caracteres).')
    .max(MAX_MESSAGE_LENGTH, `Máximo ${MAX_MESSAGE_LENGTH} caracteres.`),
});

type ContactField = keyof z.infer<typeof ContactSchema>;

export interface ContactState {
  status: 'idle' | 'success' | 'error';
  message?: string;
  fieldErrors?: Partial<Record<ContactField, string>>;
  values?: Partial<Record<ContactField, string>>;
}

function text(formData: FormData, key: string): string {
  const value = formData.get(key);
  return typeof value === 'string' ? value : '';
}

export async function sendContact(_previous: ContactState, formData: FormData): Promise<ContactState> {
  // Honeypot: un humano no ve ni completa este campo. A un bot se le responde
  // "éxito" para que no reintente.
  if (text(formData, 'website').length > 0) return { status: 'success' };

  const values = { name: text(formData, 'name'), email: text(formData, 'email'), message: text(formData, 'message') };
  const parsed = ContactSchema.safeParse(values);
  if (!parsed.success) {
    const { fieldErrors } = z.flattenError(parsed.error);
    return {
      status: 'error',
      message: 'Revisá los campos marcados.',
      fieldErrors: {
        name: fieldErrors.name?.[0],
        email: fieldErrors.email?.[0],
        message: fieldErrors.message?.[0],
      },
      values,
    };
  }

  const apiKey = process.env.RESEND_API_KEY;
  const to = process.env.CONTACT_TO_EMAIL;
  const from = process.env.CONTACT_FROM_EMAIL;
  const fallback = `No pudimos enviar tu mensaje. Escribinos a ${site.contact.email}.`;
  if (!apiKey || !to || !from) return { status: 'error', message: fallback, values };

  const { name, email, message } = parsed.data;
  try {
    const response = await fetch(RESEND_ENDPOINT, {
      method: 'POST',
      headers: { Authorization: `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from,
        to: [to],
        reply_to: email,
        subject: `Nueva consulta de ${name} — ${site.name}`,
        text: `Nombre: ${name}\nEmail: ${email}\n\n${message}`,
      }),
    });
    if (!response.ok) return { status: 'error', message: fallback, values };
    return { status: 'success' };
  } catch {
    return { status: 'error', message: fallback, values };
  }
}
