// Eventos que se miden en todas las webs Nexar. Nombres de GA4 cuando existe uno
// recomendado (generate_lead), propios cuando no.
export const EVENTS = {
  ctaClick: 'cta_click',
  whatsappClick: 'whatsapp_click',
  lead: 'generate_lead',
} as const;

export type EventName = (typeof EVENTS)[keyof typeof EVENTS];
export type EventParams = Record<string, string | number | boolean>;

declare global {
  interface Window {
    gtag?: (...args: unknown[]) => void;
    clarity?: (...args: unknown[]) => void;
  }
}

// La medición nunca puede romper el sitio: si una herramienta no cargó o falla,
// el evento se pierde en silencio.
export function track(event: EventName, params: EventParams = {}): void {
  if (typeof window === 'undefined') return;
  try {
    if (typeof window.gtag === 'function') window.gtag('event', event, params);
    if (typeof window.clarity === 'function') window.clarity('event', event);
  } catch {
    // Sin acción: perder un evento es preferible a romper la interacción.
  }
}
