import { useState } from 'react';
import './directory.css';
import { Link, useLocation } from 'react-router-dom';
import { ButtonLink } from './components/arc/button/button-link';
import { ListingIcon, ListingLink, listingLinkKind } from './ListingLink';
import { directoryLinks, directoryMapUrl, directoryTags } from './directory';
import type { DirectoryDetails, RecordItem } from './types';

export function DirectoryTags({ record }: { record: RecordItem }) {
  return <div className="directory-tags" aria-label="Areas of work">
    {directoryTags(record).slice(0, 3).map(tag => <ButtonLink wrap variant="secondary" size="sm" key={tag} to={`/directory/archive?tag=${encodeURIComponent(tag)}`}>{tag}</ButtonLink>)}
  </div>;
}

export function DirectoryActions({ record, full = false }: { record: RecordItem; full?: boolean }) {
  const links = directoryLinks(record);
  const map = directoryMapUrl(record);
  const website = links.find(link => link.label === 'Website');
  const other = links.filter(link => link !== website);
  const emails = [...new Set(record.emails)];
  const mapAddress = map ? record.locations.find(value => value.trim().length > 5 && !/^goa(?:,? india)?$/i.test(value.trim())) : undefined;
  return <div className={`directory-actions${full ? ' listing-contact-actions' : ''}`} aria-label={`Links for ${record.title}`}>
    {website && <ListingLink href={website.url} kind="website">Website</ListingLink>}
    {(full ? emails : emails.slice(0, 1)).map(email => <ListingLink key={email} href={`mailto:${email}`} label={full ? undefined : `Email ${record.title}`}>{full ? email : 'Email'}</ListingLink>)}
    {map && <ListingLink href={map} kind="map">{full && mapAddress ? `Map: ${mapAddress}` : 'Find on Maps'}</ListingLink>}
    {full && [...new Set(record.locations)].filter(location => location !== mapAddress).map(location => <div className="listing-location" key={location}><ListingIcon kind="map" /><span>{location}</span></div>)}
    {(full ? other : other.slice(0, 2)).map(link => <ListingLink key={link.url} href={link.url} kind={listingLinkKind(link.label)}>{link.label}</ListingLink>)}
    {!full && !links.length && !emails.length && <ListingLink href={record.source} kind="source">Source listing</ListingLink>}
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
