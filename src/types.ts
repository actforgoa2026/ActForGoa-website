export type Kind='organisation'|'contact'|'resource'|'story'|'page';
export interface RecordItem {
 id:string;title:string;kind:Kind;source:string;sourceApi:string;sourceStatus:number|null;
 summary:string;text:string;documentText?:string;blocks:{type:string;text:string}[];topics:string[];
 image:string;imageSource:string;publishedAt:string;updatedAt:string;retrievedAt:string;
 phones:{display:string;href:string|null;verification:string}[];emails:string[];locations:string[];locality?:string;
 documents:{label:string;url:string;status:number|null;pages?:number}[];links:{label:string;url:string}[];
 verification:string;editorialStatus:string;
}
export const TOPICS=['Waste & recycling','Nature & wildlife','Water & environment','Community & rights','Food & farming','Culture & heritage','Planning & mobility','Health & wellbeing'];
export const kindLabel:Record<Kind,string>={organisation:'Organisation',contact:'Volunteer contact',resource:'Guide & resource',story:'Community story',page:'ActForGoa'};
