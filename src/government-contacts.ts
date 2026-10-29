export type DepartmentContact = {
 title: string; back: {href: string; label: string}; intro: string;
 callHeading: string; callNote: string; calls: {label: string; phone: string}[];
 office: {label: string; address: string[]; phone: string; email: string};
 reviewNote: string; sources: {label: string; href: string}[];
};
const forestPage = 'https://forest.goa.gov.in/contact-us';
const agriculturePage = 'https://www.goa.gov.in/department/agriculture/';
const veterinaryPage = 'https://www.goa.gov.in/department/department-of-animal-husbandry-and-veterinary-services/';
export const governmentContacts: Record<string, DepartmentContact> = {
 forest: {
  title:'Forest Department contacts',back:{href:'/topics/nature',label:'Nature & wildlife'},
  intro:'Call a published helpline or contact the head office to find the office serving your area.',
  callHeading:'Forest helplines',callNote:'The department lists these as 24-hour helplines.',
  calls:[{label:'North Goa',phone:'0832-2228772'},{label:'South Goa',phone:'0832-2750246'}],
  office:{label:'Head office',address:['Office of the Principal Chief Conservator of Forest','Goa Van Bhavan, Forest Department','Altinho, Panaji, Goa 403001'],phone:'0832-2492533',email:'dcfhq-forest.goa@nic.in'},
  reviewNote:'Published contact details reviewed on 29 October 2026 against the Goa government portal and the Forest Department’s indexed contact page. Phone and email response have not been tested.',
  sources:[{label:'Forest Department contact page',href:forestPage},{label:'Goa government department listing',href:'https://www.goa.gov.in/department/department-of-forest/'},{label:'Full Forest Department directory (PDF)',href:'https://forest.goa.gov.in/sites/default/files/2026-01/Forest-Dept-Telephone-Directory-08-Jan-26.pdf'}],
 },
 agriculture: {
  title:'Agriculture Department contacts',back:{href:'/topics/food',label:'Food & farming'},
  intro:'Ask the Directorate to direct you to the Zonal Agriculture Office serving your holding.',
  callHeading:'Speak to the Directorate',callNote:'Have your village, taluka and the purpose of your enquiry ready. Confirm the receiving office before sending documents.',
  calls:[{label:'Directorate of Agriculture',phone:'0832-2465443'}],
  office:{label:'Head office',address:['Directorate of Agriculture','Krishi Bhavan, Tonca','Caranzalem, Goa 403002'],phone:'0832-2465443',email:'dir-agri.goa@nic.in'},
  reviewNote:'Published contact details reviewed on 29 October 2026 against the indexed Goa government department listing. Phone and email response and office hours have not been tested.',
  sources:[{label:'Official Agriculture Department listing',href:agriculturePage}],
 },
 veterinary: {
  title:'Government veterinary contacts',back:{href:'/topics/nature',label:'Nature & wildlife'},
  intro:'Call a veterinary hospital to ask about care for the animal and the service available near you. For wildlife, use Forest Department contacts.',
  callHeading:'Veterinary hospitals',callNote:'These are published hospital contacts, not confirmed 24-hour helplines. Call to confirm opening hours, the animals they can treat and whether they can attend or receive the animal.',
  calls:[{label:'Tonca, Caranzalem',phone:'0832-2462423'},{label:'Mapusa',phone:'0832-2257237'},{label:'Sonsodo, Margao',phone:'0832-2759392'},{label:'Honda',phone:'0832-2370918'}],
  office:{label:'Department enquiries',address:['Department of Animal Husbandry & Veterinary Services','Offices 401–404, 4th floor; 502 & 504, 5th floor','SPACES Building, Patto, Panaji, Goa'],phone:'9607948546',email:'dir-ahvs.goa@nic.in'},
  reviewNote:'Published details reviewed on 29 October 2026. Hospital numbers come from the department’s published citizen charter; department enquiries come from the indexed Goa government portal. These listings are not a live availability check. Phone and email response have not been tested.',
  sources:[{label:'Veterinary department listing',href:veterinaryPage},{label:'Published citizen charter and hospital contacts (PDF)',href:'https://ahvs.goa.gov.in/wp-content/uploads/2025/03/Citizen-Charter-1.pdf'},{label:'Official emergency contact page',href:'https://ahvs.goa.gov.in/emergency-contact/'}],
 },
};
export const contactPhoneHref = (phone: string) => `tel:+91${phone.replace(/\D/g, '').replace(/^0/, '')}`;

export const governmentContact = (slug: string): DepartmentContact | undefined => Object.hasOwn(governmentContacts, slug) ? governmentContacts[slug] : undefined;
