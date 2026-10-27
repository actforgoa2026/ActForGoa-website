// Reviewed duplicate source listings. The first ID is the preferred listing;
// distinct offices, jurisdictions and appointments deliberately remain separate.
export const duplicateGroups: readonly (readonly string[])[] = [
  ['goa-3be8492c5821', 'goa-b3f711f6b7f3'],
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
export function directoryWebsite(value = ''): string {
  const repaired = value.trim().replace(/\s+/g, '').replace(/^https?:\/\/(?=https?:\/\/)/i, '').replace(/^https?:\/\/http\/\/:/i, 'https://');
  try {
    const url = new URL(repaired);
    if (!['http:', 'https:'].includes(url.protocol) || !url.hostname.includes('.') || url.username || url.password) return '';
    return repaired;
  } catch { return ''; }
}
