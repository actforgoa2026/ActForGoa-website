import type { ReactNode } from 'react';
import { ArrowUpRight, FileText, Globe, HandHeart, Mail, MapPin, MessageCircle, Phone } from 'lucide-react';

type LinkKind = 'email' | 'phone' | 'map' | 'website' | 'social' | 'participate' | 'source' | 'external';
const icons = { email: Mail, phone: Phone, map: MapPin, website: Globe, social: MessageCircle, participate: HandHeart, source: FileText, external: ArrowUpRight };

export function ListingIcon({ kind }: { kind: LinkKind }) {
  const Icon = icons[kind];
  return <Icon size={18} strokeWidth={1.7} aria-hidden="true" />;
}

export function ListingLink({ href, kind = 'external', children, label }: { href: string; kind?: LinkKind; children: ReactNode; label?: string }) {
  const local = /^(mailto:|tel:)/.test(href);
  const icon = href.startsWith('mailto:') ? 'email' : href.startsWith('tel:') ? 'phone' : kind;
  return <a className="listing-link" href={href} target={local ? undefined : '_blank'} rel={local ? undefined : 'noreferrer'} aria-label={label}>
    <ListingIcon kind={icon} /><span>{children}</span>
  </a>;
}

export function listingLinkKind(label: string): LinkKind {
  if (/website/i.test(label)) return 'website';
  if (/instagram|facebook|linkedin|youtube|^x$/i.test(label)) return 'social';
  if (/volunteer|involved|participat/i.test(label)) return 'participate';
  if (/source|record/i.test(label)) return 'source';
  return 'external';
}
