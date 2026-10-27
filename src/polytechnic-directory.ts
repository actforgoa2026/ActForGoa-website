import type { CRMRecord, CRMSnapshot } from './crm-model.js';

// Preserve the original iGOOD snapshot; apply a dated, source-specific review to
// both the public directory and the MCP. Do not rewrite a newer source identity.
const officeId = 'goa-64e8456a16a7';
const previousId = 'goa-553c2b1f141c';
const currentId = 'goa-polytechnic-mayem-pramodini-naik';
const government = 'https://www.goa.gov.in/department/government-polytechnic-bicholim/';
const original = 'https://dip.goa.gov.in/igood/viewSubCategoryOneDetails/MjI1';
const college = 'https://gpb.goa.gov.in/principal/';
const evidence = `${government} | ${original} | ${college}`;
export function reviewPolytechnicSnapshot(snapshot: CRMSnapshot): CRMSnapshot {
  const old = snapshot.records.find(r => r.record_id === previousId && /Subhash P\. Borkar/i.test(r.name));
  const office = snapshot.records.find(r => r.record_id === officeId && r.name === 'GOVERNMENT POLYTECHNIC MAYEM');
  if (!old || !office) return snapshot;
  const updates: Record<string, Record<string, string>> = {
    [officeId]: {
      summary: 'Government Polytechnic Mayem, also known as Government Polytechnic Bicholim. The Polytechnic website and Goa government page name Dr. Pramodini S. Naik as principal; an older directory listing differs.',
      public_phone: '+918322361235 | +918322360240', public_email: 'principalgpbicholim@gmail.com | gpbicholim.goa@gov.in',
      contact_source_urls: `${government} | ${college}`, source_urls: evidence, checked_on: '2026-10-28',
      verification_status: 'official_sources_reviewed; principal_sources_conflict; contact_delivery_untested',
      activity_verification_notes: 'The Polytechnic principal page, reviewed 27 October 2026, and the Goa government department page name Dr. Pramodini S. Naik. The iGOOD listing names Subhash P. Borkar without an appointment date. Contact delivery and continued tenure have not been independently confirmed.',
      notes: 'The government department page lists the principal Gmail address and office phone. The institution website lists the gov.in email. Both are public listings; delivery is untested.',
    },
    [previousId]: {
      role: 'Principal in older official listings',
      summary: 'Subhash P. Borkar is named as principal in the undated iGOOD listing. The Polytechnic and Goa government department pages now name Dr. Pramodini S. Naik; current tenure is not independently confirmed.',
      public_phone: '', public_email: '', activity_status: 'historical_official_listing',
      verification_status: 'older_official_listing; principal_sources_conflict; current_tenure_unconfirmed',
      source_urls: evidence, contact_source_urls: `${government} | ${college}`, checked_on: '2026-10-28',
      activity_verification_notes: 'The undated iGOOD directory names Borkar, while the Polytechnic principal page reviewed 27 October 2026 and the government department page name Naik. Do not treat the older listing as confirmation of a current appointment.',
      notes: 'Individual telephone numbers from the historical directory are withheld as a current contact route. Use the institution listing.',
    },
  };
  const records = snapshot.records.map(r => updates[r.record_id] ? { ...r, ...updates[r.record_id] } : r);
  if (!records.some(r => r.record_id === currentId)) records.push({
    ...old, record_id: currentId, name: 'Dr. Pramodini S. Naik', role: 'Principal, listed by Goa government',
    summary: 'Named as Government Polytechnic Mayem/Bicholim principal on the Polytechnic website and the Goa government department page. The undated iGOOD listing names Subhash P. Borkar; confirm current tenure with the institution.',
    public_phone: '', public_email: '', contact_kind: 'government_published_institution',
    source_urls: evidence, contact_source_urls: `${government} | ${college}`, checked_on: '2026-10-28',
    verification_status: 'government_and_institution_listings; conflicting_older_listing; appointment_and_contact_delivery_unconfirmed',
    activity_status: 'recent_public_reference_only', activity_evidence_date: '2026-10-27', activity_evidence_url: college,
    activity_verification_notes: 'The Polytechnic principal page, reviewed 27 October 2026, and the Goa government department page name Naik as principal. The undated iGOOD listing names Borkar. Current tenure is not independently confirmed.',
    notes: 'Contact the institution using its publicly listed office routes; delivery is untested.',
    website_url: government, related_record_ids: officeId,
  });
  return { ...snapshot, records };
}
