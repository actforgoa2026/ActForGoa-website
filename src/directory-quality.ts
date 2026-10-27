import checks from './content/directory-website-checks.json' with { type: 'json' };
// Reviewed duplicate source listings. The first ID is the preferred listing;
// distinct offices, jurisdictions and appointments deliberately remain separate.
export const duplicateGroups: readonly (readonly string[])[] = [
  ['goa-3be8492c5821', 'goa-b3f711f6b7f3'],
  ['goa-a1f1014604fa', 'goa-b8b44e35e553'],
  ['goa-4262a74b8bc6', 'goa-5f419858330f'],
  ['goa-6ef0c6c588d1', 'goa-f6c7eb3c4530'],
  ['goa-8ad573037ef3', 'goa-85db10d81c72'],
  ['goa-eca0fefca9f2', 'goa-f80172c68298'],
  ['goa-c811c662f54e', 'goa-8a5883212e77'],
  ['goa-3608ca65e217', 'goa-4d14ae461ea5'],
  ['goa-1b857171cc0f', 'goa-a6c05b39a615'],
  ['goa-7ecf6cfa543b', 'goa-d71f0fd2aa82'],
  ['goa-388cfbba2875', 'goa-48a4d55cc5ca'],
  ['goa-c7df2e3a74fc', 'goa-4c9a60ec1654'],
  ['goa-68013df9afaf', 'goa-aaf3ed1aa834'],
  ['goa-7f75759969f8', 'goa-dbdbb7279529'],
  ['goa-1cf3dab63f6b', 'goa-a442d6cfbff4'],
  ['goa-e8ccc9619bc7', 'goa-0f87d3e97cce'],
  ['goa-5eee8f4e003a', 'goa-fb2f071a7b34'],
  ['goa-26fd995a1431', 'goa-19625d0155b7'],
  ['goa-2e05ee42c04c', 'goa-0e91ff91d656'],
  ['goa-c4e38c7205b6', 'goa-dd6e982be3e6'],
  ['goa-ad25de045f71', 'goa-5d1c3a975d0e'],
  ['goa-7bd842bd7b34', 'goa-019b5005802e'],
  ['goa-a8f87d42c73d', 'goa-4cbc48cc10b6'],
  ['goa-1e19630b1784', 'goa-e7ba4bbddfc5'],
  ['goa-3d121cbe5d86', 'goa-f7b335a48a01'],
  ['goa-d403bc9b4a6d', 'goa-3ad5bc7d45f3'],
  ['goa-c7163d6bafbc', 'goa-afb0337842fa'],
  ['goa-b29ff250b544', 'goa-57c2323877e0'],
  ['goa-f59a5c3c0b0c', 'goa-bff8b097b5d9'],
  ['goa-a5d7e53e8948', 'goa-5ebd8790e105'],
  ['goa-e8f7888476f4', 'goa-1a51c857c331'],
  ['goa-c962b37329f5', 'goa-86cf0d8a891c'],
  ['goa-085b2b5beada', 'goa-eedcaf276912'],
  ['goa-43adfe995211', 'goa-3ba789926164'],
  ['goa-a01db34b6066', 'goa-bee0696e7597'],
  ['goa-ce73f2ff3d57', 'goa-36ffe9ade986'],
  ['goa-eb49241b3a79', 'goa-326ba163b8b9'],
  ['goa-9282778a0e0e', 'goa-08e64df3f141'],
];
const groupsById = new Map(duplicateGroups.flatMap(group => group.map(id => [id, group] as const)));
export function duplicateGroup(id: string): readonly string[] { return groupsById.get(id) || [id]; }
export function directoryIdentity(id: string): string { return duplicateGroup(id)[0]; }

// Correct known transcription artifacts only; never infer a host or accept
// non-HTTP links. Original source data stays available for provenance.
const officialReplacements: Record<string, {url: string; source: string; oldHost: string}> = {
  'goa-80732e1537a8': {url:'https://dstwm.goa.gov.in/', oldHost:'www.dstegoa.goa.gov.in', source:'https://www.goa.gov.in/department/department-of-science-and-technology-and-waste-management/'},
  'goa-7d260420a7fe': {url:'https://rera.goa.gov.in/reraApp/', oldHost:'www.rera.goa.gov.in', source:'https://rera.goa.gov.in/aboutUs'},
  'goa-e4e90e319052': {url:'https://goawrd.gov.in/', oldHost:'www.goawrd.in', source:'https://www.goa.gov.in/citizen/useful-links/'},
  'goa-fbf92575aff0': {url:'https://goaulbservice.gov.in/', oldHost:'www.urban.goa.gov.in', source:'https://www.goa.gov.in/citizen/useful-links/'},
};
const workingBareHosts = new Set(['forest.goa.gov.in','ahvs.goa.gov.in','statetax.goa.gov.in','dfda.goa.gov.in','gdch.goa.gov.in','gfdc.goa.gov.in','gazetteer.goa.gov.in','ghb.goa.gov.in','gssc.goa.gov.in','gsic.goa.gov.in','gcascs.ac.in','infotech.goa.gov.in','iphb.goa.gov.in','dmg.goa.gov.in','rnd.goa.gov.in','dsya.goa.gov.in','scert.goa.gov.in','dte.goa.gov.in','itivasco.goa.gov.in']);
export function directoryWebsite(value = '', id = ''): string {
  const repaired = value.trim().replace(/\s+/g, '').replace(/^https?:\/\/(?=https?:\/\/)/i, '').replace(/^https?:\/\/http\/\/:/i, 'https://');
  try {
    const url = new URL(repaired);
    if (!['http:', 'https:'].includes(url.protocol) || !url.hostname.includes('.') || url.username || url.password) return '';
    if (officialReplacements[id]?.oldHost === url.hostname) return officialReplacements[id].url;
    if (url.hostname.startsWith('www.') && workingBareHosts.has(url.hostname.slice(4))) return repaired.replace('://www.', '://');
    return repaired;
  } catch { return ''; }
}

export function websiteEvidence(value = '', id = '') {
  const fixed = directoryWebsite(value, id);
  const source = fixed === officialReplacements[id]?.url ? officialReplacements[id]?.source : undefined;
  const raw = value.trim().replace(/\s+/g, '').replace(/^https?:\/\/(?=https?:\/\/)/i, '').replace(/^https?:\/\/http\/\/:/i, 'https://');
  const checked = (checks as Record<string, {status: string; checked_on: string}>)[raw];
  const recovered = Boolean(source || (raw !== fixed && fixed && workingBareHosts.has(new URL(fixed).hostname)));
  return { status: recovered ? 'responded' : checked?.status || 'not_checked', checked_on: checked?.checked_on || (recovered ? '2026-10-27' : ''), ...(source ? { source } : {}) };
}
