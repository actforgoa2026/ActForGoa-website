import offices from './content/local-offices.json';

export type LocalOffice = (typeof offices)[number];
export function findLocalOffices(query: string): LocalOffice[] {
 const terms = query.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
 if (!terms.length) return [];
 return offices.filter(office => terms.every(term => `${office.name} ${office.location}`.toLocaleLowerCase().includes(term))).slice(0, 8);
}
export function recipientForOffice(office: LocalOffice, templateId: string): string {
 // RTI templates already include the officer's designation before this field.
 if (/^0[34]-/.test(templateId)) return office.name;
 const role = office.name.startsWith('Village Panchayat') ? 'The Secretary' : office.name.includes('City Of Panaji') ? 'The Commissioner' : 'The Chief Officer';
 return `${role}, ${office.name}`;
}
export function recipientHelp(templateId: string) {
 if (templateId.startsWith('03-')) return {text:'Choose the public authority that holds the records. Confirm its designated State Public Information Officer and postal address before sending.', link:'https://dip.goa.gov.in/details-of-pio-apio-faa/', label:'Find the authority’s PIO'};
 if (templateId.startsWith('04-')) return {text:'Use the First Appellate Authority of the same public authority as your original RTI request. The local office secretary is not automatically the appellate authority.', link:'https://dip.goa.gov.in/details-of-pio-apio-faa/', label:'Find the First Appellate Authority'};
 if (templateId.startsWith('17-')) return {text:'Use the receiving authority and submission channel named in the consultation notice. Check the notice’s closing date and any updates.', link:'https://www.goa.gov.in/documents/', label:'Browse government notices'};
 if (/^(09|11)-/.test(templateId)) return {text:'Start with the Zonal Agriculture Office serving the holding. Ask it to confirm the office, current form and accepted submission channel.', link:'/contacts/agriculture', label:'Find Agriculture Department contacts'};
 if (templateId.startsWith('13-')) return {text:'Confirm the police station responsible for the incident location. Veterinary or Forest Department contacts may be relevant for assistance or a copy.', link:'https://citizen.goapolice.gov.in/', label:'Goa Police citizen portal'};
 if (/^(06|08)-/.test(templateId)) return {text:'Check the authority shown on the permission or application first. Planning approvals and local building or occupancy permissions can involve different offices.', link:'https://tcp.goa.gov.in/', label:'Town and Country Planning Department'};
 if (templateId.startsWith('16-')) return {text:'Use the office responsible for the activity or the records you are asking about. A panchayat is not responsible for every environmental issue. For tree cutting or wildlife, start with Forest Department contacts.', link:'/contacts/forest', label:'Forest Department contacts'};
 if (templateId.startsWith('02-')) return {text:'Start with the office on your original acknowledgement, or the named supervisory or grievance officer. Keep your earlier reference number.', link:'https://dpg.goa.gov.in/public-grievances-officers/', label:'Find a public grievance officer'};
 return {text:'For a local service or local-body matter, identify the village panchayat or municipal office serving the site. For specialist matters, confirm the responsible department before sending.', link:'https://www.goa.gov.in/department/panchayats/', label:'Official panchayat guide'};
}
