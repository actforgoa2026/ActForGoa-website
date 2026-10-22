// The source guides and review register remain unchanged. This is reader-facing copy.
const checks: Record<string,string> = {
 AG01:'Check which office serves your village, its opening hours, and whether you need an appointment.',
 AG02:'Get advice on the actual land and transaction before buying, leasing or changing its use. Inherited or tenanted land may have additional restrictions.',
 AG03:'Ask the receiving office which form, documents and fees apply to you, and how long the process takes.',
 AG04:'Ask an agriculture specialist about the crop, approved inputs, harvest intervals and laboratory services for your site.',
 AG05:'Check the current scheme’s eligibility, amounts, application dates and spending rules before paying for anything.',
 AG06:'Confirm the land and water rights, repair scheme and required permissions before starting physical work.',
 AG07:'Compensation is not automatic. Ask which crops and events qualify, what evidence is needed and when to report the loss.',
 AW01:'Seek medical care promptly after possible rabies exposure. Confirm treatment availability with the healthcare service.',
 AW02:'Confirm who can attend, which species they handle, transport arrangements and any fees. If they cannot help, ask for another veterinary or Forest Department contact. Use emergency services for immediate danger to people.',
 AW03:'Ask police or a qualified lawyer which law and procedure apply to the incident. Do not take custody of an animal without the appropriate authority.',
 AW04:'Ask the responsible authority about current court directions for the location before acting on feeding, capture or release advice. Veterinary and legal decisions need the appropriate professionals.',
 AW05:'Check the requirements for the species and activity before transport, adoption, breeding or commercial care.',
 EP01:'Ask each office which part of the problem it can address, and get a separate acknowledgement from each office you contact.',
 EP02:'Confirm the current tree-felling and transport permissions, fees and conditions. Do not treat silence or elapsed time as permission to cut a tree.',
 EP03:'Obtain the current approved map and applicable coastal rules for the actual site. Get qualified help with disputed boundaries.',
 EP04:'Check the final notification, boundaries and any court protection for the wetland. A draft notification is not final approval.',
 EP05:'Confirm which office handles the complaint and ask for a reference number. Response times and outcomes depend on the case.',
 EP06:'Check the current project notice, deadline, consultation requirements and submission process before sending comments.',
 EP07:'Ask the current biodiversity committee about records access and any permission needed for collection, research or commercial use.',
 EP08:'Seek legal advice promptly about the correct forum, filing requirements and deadlines for your case. Do not assume a complaint will stop the work.',
 R03:'Confirm which office covers the location and problem. For animal-cruelty cases, ask police or a lawyer about current law and procedure.',
 R01:'Use the government service’s own website to confirm how to submit and track your complaint. Keep the acknowledgement; a published response estimate is not a legal deadline.',
 R04:'Ask about the correct appeal route and deadline for your case. Village and municipal procedures differ. Do not wait for a grievance response if an appeal deadline is running.',
 R05:'Check the current RTI rules and calculate deadlines for your own application, including any fee notices or transfers.',
 B01:'Confirm which planning authority and local body cover your property. Ask whether any special application route applies; do not assume you qualify.',
 B02:'Ask the local authority whether the work counts as a repair or needs a building application. Structural changes and extensions can require a different route.',
 B03:'Check the property’s zoning, tenure, environmental boundaries and any court cases. Use final approved maps and notifications.',
 'B03 and B04':'Confirm which approvals your site and project need, and in what order. Settle restrictions before starting the affected work.',
 B04:'Ask your designer to use the current rules and amendments that apply to your project, including relevant court directions.',
 B05:'Confirm the accepted form, documents, fees and submission method with the receiving authority. Reach online services through the official TCP website.',
 B06:'Ask for the applicable fee calculation and deadlines in writing. Get qualified advice before relying on an appeal or a deemed approval.',
 B07:'Check construction-worker registration, cess, safety and waste obligations for your project with the relevant authority.',
 B08:'Confirm the completion and occupancy process for your project. Business activities may need separate operating licences.',
};

export function guideForReaders(markdown:string):string {
 return markdown.split(/\n\s*\n/).flatMap(block=>{
  if(/^\*\*Draft (?:for|reviewed|status:)/.test(block)) return [];
  const check=block.match(/^\*\*Verification needed ([\w ]+):\*\*/);
  if(check && checks[check[1]]) return '**Before you act:** '+checks[check[1]];
  return block;
 }).join('\n\n')
 .replace(/## Templates and review/g, '## Useful templates')
 .replace(/## Sources and review notes/g, '## Sources')
 .replace(/- \[Verification register\]\([^)]*\) and \[source register\]\([^)]*\)/g, '- [Official sources](/read/guide-sources)')
 .replace(/\*\*Verification needed\*\* notes identify unresolved legal or service details in the \[verification register\]\([^)]*\)\. /g,'')
 .replace(/\*\*Verification needed R02:\*\* direct retrieval of the portal failed during this review, so confirm the live authority list, upload limits, fee\/payment route and paper alternative before publication\./g,'Check the current authority list, document limits, fees and payment options on the portal. If it is unavailable, ask the office about submitting on paper.')
 .replace(/The corpus contains a central CRZ 2019 compilation, but its existence does not establish which approved Goa plan applies to a particular parcel\./g,'The central CRZ 2019 compilation does not establish which approved Goa plan applies to a particular parcel.')
 .replace(/The corpus's March 2023 Goa gazette/g,'The March 2023 Goa gazette')
 .replace(/Direct retrieval failed during review\. If it remains unavailable,/g,'If the page is unavailable,')
 .replace(/The Goa fee rules in the corpus/g,'The Goa fee rules')
 .replace(/## Sources[\s\S]*?(?=\n\[R1\]:)/,'## Sources\n\nSee the [official sources](/read/guide-sources) for the documents behind this guide.\n')
 .replace(/The \[source register\]\([^)]*\) links the official sources to saved corpus copies and exact sections\/pages\.[\s\S]*?remain useful starting points; the official forms above avoid relying on inaccessible legacy-domain links\./,'See the [official sources](/read/guide-sources) and use the current forms linked by the relevant authority.');
}
