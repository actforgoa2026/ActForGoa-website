import { TOPICS } from './types';

const cataloguePaths = ['/search', '/directory', '/directory/archive', '/library', '/stories', '/blog'];
export function searchDestination(pathname: string, search: string, query: string) {
  const path = pathname.replace(/\/$/, '');
  const destination = cataloguePaths.includes(path) ? path : '/search';
  const params = new URLSearchParams(cataloguePaths.includes(path) ? search : '');
  // A new question keeps deliberate filters but starts a fresh relevance scope.
  params.delete('scope');
  query.trim() ? params.set('q', query.trim()) : params.delete('q');
  return destination + (params.size ? `?${params}` : '');
}

export function catalogueFilters(search: string) {
  const params = new URLSearchParams(search);
  const topic = params.get('topic') || '';
  const type = params.get('type') || 'all';
  return {
    topic: TOPICS.includes(topic) ? topic : '',
    type: ['all', 'organisation', 'resource', 'story', 'page'].includes(type) ? type : 'all',
  };
}

/** Offer a direct official helpline route; this does not diagnose an emergency. */
export function showEmergencyShortcut(query: string): boolean {
  const q = query.toLowerCase().replace(/[’']/g, '').replace(/[^a-z0-9]+/g, ' ');
  return /\b(emergency|emergencies|ambulance|helplines?|112|108|police|fire brigade|fire rescue|on fire|snakebite|snakebites|heart attack|unconscious)\b/.test(q)
    || /\b(snake|cobra|viper|dog)\b.*\b(bit|bite|bites|bitten)\b|\b(bit|bite|bites|bitten)\b.*\b(snake|cobra|viper|dog)\b/.test(q);
}
