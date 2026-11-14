'use client';

import { track, type EventName, type EventParams } from '@/lib/analytics';

interface TrackedLinkProps extends React.AnchorHTMLAttributes<HTMLAnchorElement> {
  event: EventName;
  params?: EventParams;
}

// Link que registra un evento al hacer clic. Para CTAs, WhatsApp y links externos.
export function TrackedLink({ event, params, onClick, ...props }: TrackedLinkProps): React.ReactElement {
  return (
    <a
      {...props}
      onClick={(clickEvent) => {
        track(event, params);
        onClick?.(clickEvent);
      }}
    />
  );
}
