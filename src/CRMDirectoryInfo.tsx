import { Link } from 'react-router-dom';
import { ArrowUpRight, Mail, MapPin } from 'lucide-react';
import { CreditedPhoto } from './DirectoryInfo';
import { crmDirectoryDetails, crmDirectoryLinks, crmDirectoryMapUrl, crmDirectoryTags } from './crm-directory';
import type { CRMRecord } from './crm-model';

export function CRMDirectoryTags({ record, full = false }: { record: CRMRecord; full?: boolean }) {
  const tags = crmDirectoryTags(record);
  return <div className="directory-tags" aria-label="Areas of work">
    {(full ? tags : tags.slice(0, 3)).map(tag => <Link key={tag} to={`/directory?collection=all&q=${encodeURIComponent(tag)}`}>{tag}</Link>)}
  </div>;
}

export function CRMDirectoryPhoto({ record, href, detail = false }: { record: CRMRecord; href?: string; detail?: boolean }) {
  const photo = crmDirectoryDetails(record)?.photo;
  return photo ? <CreditedPhoto key={record.record_id} photo={photo} href={href} detail={detail} /> : null;
}

export function CRMDirectoryActions({ record }: { record: CRMRecord }) {
  if (record.activity_status === 'deceased_historical_record') return null;
  const map = crmDirectoryMapUrl(record);
  const email = (record.public_email || '').split(' | ').find(e => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e));
  return <div className="directory-actions" aria-label={`Links for ${record.name}`}>
    {crmDirectoryLinks(record).map(link => <a key={link.url} href={link.url} target="_blank" rel="noreferrer">{link.label}<ArrowUpRight size={15} aria-hidden="true" /></a>)}
    {map && <a href={map} target="_blank" rel="noreferrer"><MapPin size={15} aria-hidden="true" />Find on Maps</a>}
    {email && <a href={`mailto:${email}`} aria-label={`Email ${record.name}`}><Mail size={15} aria-hidden="true" />Email</a>}
  </div>;
}
