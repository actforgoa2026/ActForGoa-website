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
const officialReplacements: Record<string, {url: string; source: string; oldHost: string; kind?: 'reference'}> = {
  'goa-bb1b92ba4e69': {url:'https://goasacs.goa.gov.in/', oldHost:'goasacs.nic.in', source:'https://www.goa.gov.in/department/goa-state-aids-control-society/'},
  'goa-0d7dd8b631d2': {url:'https://www.goa.gov.in/department/indian-red-cross-society-goa-state-branch/', oldHost:'www.redcrossgoa.org', source:'https://www.goa.gov.in/department/indian-red-cross-society-goa-state-branch/', kind:'reference'},
  'goa-e888fee48910': {url:'https://www.goa.gov.in/department/women-and-child-development/', oldHost:'www.dwcd.goa.gov.in', source:'https://www.goa.gov.in/department/women-and-child-development/', kind:'reference'},
  'goa-b8e1df4327fd': {url:'https://www.goa.gov.in/department/institute-menezes-braganza/', oldHost:'www.imbgoa.com', source:'https://www.goa.gov.in/department/institute-menezes-braganza/', kind:'reference'},
  'goa-85acc07f0404': {url:'https://daa.goa.gov.in/', oldHost:'daa.goa.gov', source:'https://www.goa.gov.in/citizen/useful-links/'},
  'goa-8594c8748e6e': {url:'https://excise.goa.gov.in/', oldHost:'goaexcies.gov.in', source:'https://www.goa.gov.in/citizen/useful-links/'},
  'goa-fe7e9c7a7d57': {url:'https://dslr.goa.gov.in/', oldHost:'egov.goa.nic.in', source:'https://www.goa.gov.in/department/directorate-of-settlement-and-land-records/'},
  'goa-a01aac1366c9': {url:'https://sidcgl.goa.gov.in/', oldHost:'sidcgl.com', source:'https://sidcgl.goa.gov.in/about-sewerage-infrastructure-development-corporation-of-goa-ltd/'},
  'goa-a92188ca7c2a': {url:'https://citizen.goapolice.gov.in/', oldHost:'www.goapolice.gov.in', source:'https://www.goa.gov.in/department/goa-police/'},
  'goa-a46eacd59d7f': {url:'https://balbhavan.goa.gov.in/', oldHost:'www.goabalbhavan.org', source:'https://balbhavan.goa.gov.in/'},
  'goa-e6706bc446bb': {url:'https://tiatracademyofgoa.com/', oldHost:'www.tiatracdemygoa.com', source:'https://dip.goa.gov.in/tiatr-academy-of-goa-organizes-orientation-course-in-tiatr/'},
  'goa-bab2a38177ae': {url:'https://ccari.res.in/', oldHost:'www.asigoacircle.gov.in', source:'https://ccari.res.in/contact.html'},
  'goa-072a2cc92381': {url:'https://dpg.goa.gov.in/', oldHost:'www.grievances.goa.gov.in', source:'https://www.goa.gov.in/citizen/useful-links/'},
  'goa-dd3a470b269f': {url:'https://gedc.goa.gov.in/', oldHost:'www.gedc-goa.org', source:'https://dip.goa.gov.in/online-applications-invited-for-bursary-scheme-2025-26/'},
  'goa-ee25a03f7224': {url:'https://rescuemania.co.uk/our-projects/arc-animal-rescue-centre-south-goa/', oldHost:'www.arcgoa.in', source:'https://rescuemania.co.uk/our-projects/arc-animal-rescue-centre-south-goa/', kind:'reference'},
  'goa-41bf2a5c96ee': {url:'https://www.goa.gov.in/department/directorate-of-accounts/', oldHost:'www.accountsgoa', source:'https://www.goa.gov.in/department/directorate-of-accounts/', kind:'reference'},
  'goa-e3976c5acad6': {url:'https://www.goa.gov.in/department/health-services/', oldHost:'dhsgoa.gov.in', source:'https://www.goa.gov.in/department/health-services/', kind:'reference'},
  'goa-3a5105190961': {url:'https://www.goa.gov.in/department/goa-state-commission-for-protection-of-child-rights/', oldHost:'www.gscper.goa.gov.in', source:'https://www.goa.gov.in/department/goa-state-commission-for-protection-of-child-rights/', kind:'reference'},
  'goa-b24f71199ae9': {url:'https://www.goa.gov.in/department/industries-trade-and-commerce/', oldHost:'www.ditc.goa.gov.in', source:'https://www.goa.gov.in/department/industries-trade-and-commerce/', kind:'reference'},
  'goa-c62adfed31da': {url:'https://dsde.goa.gov.in/government-itis/', oldHost:'www.itibicholim.goa.gov.in', source:'https://dsde.goa.gov.in/government-itis/', kind:'reference'},
  'goa-b794088ac208': {url:'https://dsde.goa.gov.in/government-itis/', oldHost:'www.iticacora.goa.gov.in', source:'https://dsde.goa.gov.in/government-itis/', kind:'reference'},
  'goa-13d1d286bfbf': {url:'https://dsde.goa.gov.in/government-itis/', oldHost:'www.iticanacona.goa.gov.in', source:'https://dsde.goa.gov.in/government-itis/', kind:'reference'},
  'goa-e3620f4135fa': {url:'https://dsde.goa.gov.in/government-itis/', oldHost:'www.itifarmagudi.goa.gov.in', source:'https://dsde.goa.gov.in/government-itis/', kind:'reference'},
  'goa-d9d30aa36be0': {url:'https://dsde.goa.gov.in/government-itis/', oldHost:'www.itimargao.goa.gov.in', source:'https://dsde.goa.gov.in/government-itis/', kind:'reference'},
  'goa-ed7f5c067d58': {url:'https://dsde.goa.gov.in/government-itis/', oldHost:'www.itipanaji.goa.gov.in', source:'https://dsde.goa.gov.in/government-itis/', kind:'reference'},
  'goa-32006ec98cd7': {url:'https://dsde.goa.gov.in/government-itis/', oldHost:'www.itisattari.goa.gov.in', source:'https://dsde.goa.gov.in/government-itis/', kind:'reference'},
  'goa-f8c3a402e1c0': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-e98ddb99b2f1': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-afbcb5bc75c5': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-50f024bd1760': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-df11c9c40e66': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-fe6b7590c467': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-54604a10a3d2': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-2f899bd7603d': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-416cd7f68091': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-87b086f8a6fa': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-d51b731dc965': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-32a59e98ea43': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-7002e3e8001c': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-304c10de3340': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-65fa2d4bda16': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-1ea67880f02b': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-cb39df34047d': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-84c1c39dfcb0': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-09f5d250da6f': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-7ca3edac6163': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-2b4b1eea2511': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-53af6f9efab5': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-9ac2277f71cd': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-8250caafc67a': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-71a2a4480b6e': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-328769ee03f8': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-a73e8f9910b7': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-988c87e1ba8b': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-6bc459ed0054': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-3eedbf2224dd': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-3b4ccf0e9b91': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-8f90bc6ca390': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-f1164fca82ba': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-b70a59489cfe': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-b0de35a8b154': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-37f1f3620472': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-3557655e3fb7': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-0937ce1d323e': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-8844ea179ebb': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-d5f099b9c293': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-f9cf477389d9': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-24242e1cbf92': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-c0663d2f1ff5': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-923e701d8e2c': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-3de9af938ae8': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-aaedddac2bc3': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-d8b203fcc64f': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-0980101135ef': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-982d106dd519': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-a6941283c7d8': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-364199603c4f': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-18c0af7e6dca': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-e31bb6ea07cb': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-b287844c1d25': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-caa8a135ae21': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-02fc8be86d2f': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-60936e8446fd': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-6df3d27e4014': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-33693ff1098e': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-994dfe115d4b': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-b61d7d9e0edb': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-3de14bf4cfde': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-a0f5f1155ec6': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-bf01813fe3c3': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-d57837ea4d30': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-1b5461f21ac4': {url:'https://sec.goa.gov.in/', oldHost:'sec.goa.gov.in', source:'https://sec.goa.gov.in/', kind:'reference'},
  'goa-16c8928b2252': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
  'goa-10bc7522c797': {url:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', oldHost:'idc.goa.gov.in', source:'https://www.goa.gov.in/department/goa-industrial-development-corporation/', kind:'reference'},
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
    if (officialReplacements[id]?.oldHost === url.hostname && (url.hostname !== 'sec.goa.gov.in' || url.pathname === '/general-election-to-zilla-panchayat-2025/')) return officialReplacements[id].url;
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
  return { status: recovered ? 'responded' : checked?.status || 'not_checked', checked_on: recovered ? '2026-10-27' : checked?.checked_on || '', ...(source ? { source, kind: officialReplacements[id]?.kind || 'website' } : {}) };
}
