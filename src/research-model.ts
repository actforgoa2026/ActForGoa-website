export type ResearchDomain = 'all' | 'legal' | 'ecology';
export type ResearchEvidence = {id:string;document_id:string;page:number;label:string;title:string;url:string;text:string;origin:string;warning:string;retrieved_at:string;format:string;matches:string[];reader_url:string;generation:string;domains?:string[];legal_currency?:string;publisher_class?:string};
export type ResearchParagraph = {text:string;citations:string[]};
export type ResearchAnswer = {status:'answered'|'insufficient_evidence';paragraphs:ResearchParagraph[];citations:ResearchEvidence[];notice?:string;library_notice?:string|null;outside_context?:{text:string;provenance:'model_knowledge';notice:string}|null;domain?:ResearchDomain};
export type ResearchStatus = {search_ready:boolean;chat_ready:boolean;stats:{documents?:number;pages?:number;chunks?:number};domains?:string[];domain_counts?:Partial<Record<ResearchDomain,number>>;provider?:string;outside_context_supported?:boolean};

export const researchDomains = {
  all: {path:'/ask', label:'All research', title:'Ask about Goa.', description:'Start with our legal and ecology library. Get a short answer, check its sources and find relevant people in the community.', placeholder:'How can we protect a wetland near our village?', starters:['How can we protect a wetland near our village?', 'What can a village panchayat do about waste?', 'How do khazans manage fresh and salt water?']},
  legal: {path:'/ask/legal', label:'Legal framework', title:'Understand your next step.', description:'Ask about Goa’s legal framework, permissions and civic action. Our library comes first, with its sources beside the answer.', placeholder:'What can a village panchayat do about illegal dumping?', starters:['What can a village panchayat do about illegal dumping?', 'How do I request building permission records?', 'What should I record before reporting tree cutting?']},
  ecology: {path:'/ask/ecology', label:'Environment & ecosystems', title:'Understand Goa’s ecosystems.', description:'Explore rivers, forests, coasts and the life they support. Ask a question, check the evidence and connect with local work.', placeholder:'How do Goa’s laterite plateaus store and release water?', starters:['How do khazans manage fresh and salt water?', 'What threatens Goa’s laterite plateaus?', 'Which animals are endemic to Goa?']},
} as const;

export function researchDomain(pathname: string): ResearchDomain {
  return pathname === '/ask/legal' ? 'legal' : pathname === '/ask/ecology' ? 'ecology' : 'all';
}
export function researchReturnPath(value: unknown): string {
  return typeof value === 'string' && /^\/ask(?:\/(?:legal|ecology))?(?:\?[^#]*)?$/.test(value) ? value : '/ask';
}
export function supportsResearchDomain(status: ResearchStatus|null, domain: ResearchDomain): boolean {
  return domain === 'all' || !!status?.domains?.includes(domain);
}
/** Never render an uncited provider paragraph under the library heading. */
export function citedLibraryParagraphs(answer: ResearchAnswer): ResearchParagraph[] {
  const ids = new Set(answer.citations.map(citation => citation.id));
  return answer.paragraphs.filter(paragraph => paragraph.text.trim() && paragraph.citations.length > 0 && paragraph.citations.every(id => ids.has(id)));
}
