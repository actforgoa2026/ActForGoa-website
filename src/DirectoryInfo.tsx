import { useState } from 'react';
import './directory.css';
import { Link, useLocation } from 'react-router-dom';
import { ArrowUpRight, Mail, MapPin } from 'lucide-react';
import { directoryLinks, directoryMapUrl, directoryTags } from './directory';
import type { DirectoryDetails, RecordItem } from './types';

export function DirectoryTags({ record }: { record: RecordItem }) {
  return <div className="directory-tags" aria-label="Areas of work">
    {directoryTags(record).slice(0, 3).map(tag => <Link key={tag} to={`/directory/archive?tag=${encodeURIComponent(tag)}`}>{tag}</Link>)}
  </div>;
}

export function DirectoryActions({ record, full = false }: { record: RecordItem; full?: boolean }) {
  const links = directoryLinks(record);
  const map = directoryMapUrl(record);
  const website = links.find(link => link.label === 'Website');
  const other = links.filter(link => link !== website);
  const email = record.emails[0];
  return <div className="directory-actions" aria-label={`Links for ${record.title}`}>
    {website && <a href={website.url} target="_blank" rel="noreferrer">Website <ArrowUpRight size={15} /></a>}
    {map && <a href={map} target="_blank" rel="noreferrer"><MapPin size={15} /> Find on Maps</a>}
    {email && <a href={`mailto:${email}`} aria-label={`Email ${record.title}`}><Mail size={15} /> Email</a>}
    {(full ? other : other.slice(0, 2)).map(link => <a key={link.url} href={link.url} target="_blank" rel="noreferrer">{link.label} <ArrowUpRight size={15} /></a>)}
    {!links.length && !email && <a href={record.source} target="_blank" rel="noreferrer">Source listing <ArrowUpRight size={15} /></a>}
  </div>;
}

export function DirectoryPhoto({ record, detail = false }: { record: RecordItem; detail?: boolean }) {
  const location = useLocation();
  const photo = record.directory?.photo;
  return photo ? <CreditedPhoto key={record.id} photo={photo} detail={detail} href={`/read/${record.id}`} state={{ fromCatalogue: true, fromHome: location.pathname === '/' }} /> : null;
}

export function CreditedPhoto({ photo, detail = false, href, state }: { photo: NonNullable<DirectoryDetails['photo']>; detail?: boolean; href?: string; state?: { fromCatalogue: boolean; fromHome: boolean } }) {
  const [failed, setFailed] = useState(false);
  if (failed) return null;
  const img = <img src={photo.src} alt={photo.alt} loading={detail ? 'eager' : 'lazy'} style={{ objectPosition: photo.position }} onError={() => setFailed(true)} />;
  return <figure className={`directory-photo${detail ? ' directory-photo-detail' : ''}`}>
    {detail || !href ? img : <Link to={href} state={state} tabIndex={-1} aria-hidden="true">{img}</Link>}
    <figcaption><a href={photo.sourcePage} target="_blank" rel="noreferrer">Photo: {photo.credit}</a></figcaption>
  </figure>;
}
