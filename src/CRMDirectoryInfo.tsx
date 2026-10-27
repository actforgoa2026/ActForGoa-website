import { Link } from 'react-router-dom';
import { ListingLink, listingLinkKind } from './ListingLink';
import { CreditedPhoto } from './DirectoryInfo';
import { crmDirectoryDetails, crmDirectoryLinks, crmDirectoryMapUrl, crmDirectoryTags } from './crm-directory';
import { websiteEvidence } from './directory-quality';
import { safeUrl, type CRMRecord } from './crm-model';

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

export function CRMDirectoryActions({ record, full = false }: { record: CRMRecord; full?: boolean }) {
  if (record.activity_status === 'deceased_historical_record') return null;
  const map = crmDirectoryMapUrl(record);
  const emails = [...new Set((record.public_email || '').split(' | ').filter(e => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e)))];
  const phones = [...new Set((record.public_phone || '').split(' | ').filter(p => /^\+\d+$/.test(p)))];
  const links = crmDirectoryLinks(record);
  if (full) for (const [field, label] of Object.entries({ facebook_url: 'Facebook', linkedin_url: 'LinkedIn', x_url: 'X', youtube_url: 'YouTube' })) {
    const url = safeUrl(record[field] || '');
    if (url && !links.some(link => link.url === url)) links.push({ label, url });
  }
  const check = websiteEvidence(record.website_url, record.record_id);
  const address = crmDirectoryDetails(record)?.address;
  const primaryLinks = full ? links.filter(link => link.label === 'Website') : links;
  return <div className={`directory-actions${full ? ' listing-contact-actions' : ''}`} aria-label={`Links for ${record.name}`}>
    {record.website_url && check.status === 'unverified' && <span>Website could not be verified on {check.checked_on}.</span>}
    {record.website_url && check.status === 'intermittent' && <span>Website access was intermittent when checked on {check.checked_on}.</span>}
    {full && check.source && check.source !== primaryLinks[0]?.url && <ListingLink href={check.source} kind="source">Source for updated website</ListingLink>}
    {primaryLinks.map(link => <ListingLink key={link.url} href={link.url} kind={listingLinkKind(link.label)}>{link.label === 'Website' && check.kind === 'reference' ? 'Related reference page' : full && link.label === 'Website' ? 'Website or reference page' : link.label}</ListingLink>)}
    {check.reference_url && <ListingLink href={check.reference_url} kind="source">Official directory reference</ListingLink>}
    {(full ? emails : emails.slice(0, 1)).map(email => <ListingLink key={email} href={`mailto:${email}`} label={full ? undefined : `Email ${record.name}`}>{full ? email : 'Email'}</ListingLink>)}
    {full && phones.map(phone => <ListingLink key={phone} href={`tel:${phone}`}>{phone}</ListingLink>)}
    {map && <ListingLink href={map} kind="map">{full && address ? `Map: ${address}` : 'Find on Maps'}</ListingLink>}
    {full && links.filter(link => link.label !== 'Website').map(link => <ListingLink key={link.url} href={link.url} kind={listingLinkKind(link.label)}>{link.label}</ListingLink>)}
  </div>;
}
