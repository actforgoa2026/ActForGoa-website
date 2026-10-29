import type { RecordItem } from './types';

export interface ArticlePhoto {
  src: string;
  alt: string;
  source: string;
  credit?: string;
  license?: string;
  licenseUrl?: string;
}

// Supplemental covers illustrate a topic, never an article's people or events.
// Original article and directory images always take precedence.
const coast: ArticlePhoto = {
  src: '/assets/hero/vagator-1600.webp',
  alt: 'Coconut palms above the coast at Vagator, Goa',
  source: 'https://commons.wikimedia.org/wiki/File:Vagator,_Goa,_India,_Palms.jpg',
  credit: 'Vyacheslav Argenberg', license: 'CC BY 4.0',
  licenseUrl: 'https://creativecommons.org/licenses/by/4.0/',
};
const fields: ArticlePhoto = {
  src: '/assets/commons/paddy.webp', alt: 'Green paddy fields in Goa',
  source: 'https://commons.wikimedia.org/wiki/File:Paddy_fields_of_Goa_01.jpg',
  credit: 'Ganesh Mohan T', license: 'CC BY-SA 4.0',
  licenseUrl: 'https://creativecommons.org/licenses/by-sa/4.0/',
};
const wetland: ArticlePhoto = {
  src: '/assets/commons/mangrove.webp', alt: 'Mangroves and a waterway at Candolim–Nerul, Goa',
  source: 'https://commons.wikimedia.org/wiki/File:Mangrove_Landscape_at_Mangrove_Walk.jpg',
  credit: 'ArBay11', license: 'CC BY 4.0',
  licenseUrl: 'https://creativecommons.org/licenses/by/4.0/',
};
const street: ArticlePhoto = {
  src: '/assets/commons/panaji.webp', alt: 'Colourful buildings along a street in Panaji, Goa',
  source: 'https://commons.wikimedia.org/wiki/File:Street_in_Panaji,_Goa.jpg',
  credit: 'Radosław Botev / Fundacja Nomos', license: 'CC BY 3.0 PL',
  licenseUrl: 'https://creativecommons.org/licenses/by/3.0/pl/deed.en',
};
export function articlePhoto(record: RecordItem): ArticlePhoto | undefined {
  if (record.image) return { src: record.image, alt: record.images?.[0]?.alt || record.title, source: record.imageSource };
  if (record.images?.[0]?.src) return { src: record.images[0].src, alt: record.images[0].alt, source: record.images[0].source };
  if (record.kind === 'organisation' || record.kind === 'contact' || record.directory?.photo) return undefined;
  return supplementalPhoto(record.title, record.topics);
}

export function supplementalPhoto(title: string, topics: string[] = []): ArticlePhoto {
  const subject = `${title} ${topics.join(' ')}`.toLowerCase();
  if (/farm|food|compost|agricultur|garden/.test(subject)) return fields;
  if (/water|river|forest|wildlife|nature|biodiversity|mangrove/.test(subject)) return wetland;
  if (/cultur|heritage|planning|mobility|community|rights|health|education/.test(subject)) return street;
  return coast;
}
