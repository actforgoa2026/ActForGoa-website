export interface HeritageStory {
  title: string; place: string; story: string; credit: string; name: string; email: string;
  latitude: string; longitude: string;
}
export const emptyHeritageStory: HeritageStory = { title:'', place:'', story:'', credit:'', name:'', email:'', latitude:'', longitude:'' };
export const heritageDraftKey = 'actforgoa-heritage-story-draft-v1';
export function heritageCoordinates(draft: HeritageStory): [number, number] | null {
  if (!draft.latitude.trim() || !draft.longitude.trim()) return null;
  const lat = Number(draft.latitude), lng = Number(draft.longitude);
  return Number.isFinite(lat) && Number.isFinite(lng) && lat >= 14.8 && lat <= 15.9 && lng >= 73.5 && lng <= 74.5 ? [lat, lng] : null;
}
export function readHeritageDraft(raw: string | null): HeritageStory {
  try {
    const parsed: unknown = JSON.parse(raw || 'null');
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return {...emptyHeritageStory};
    return Object.fromEntries(Object.entries(emptyHeritageStory).map(([key,value]) => [key, typeof (parsed as Record<string, unknown>)[key] === 'string' ? String((parsed as Record<string, unknown>)[key]).slice(0,4000) : value])) as unknown as HeritageStory;
  } catch { return {...emptyHeritageStory}; }
}
export function heritageStoryEmail(draft: HeritageStory): string {
  const coordinates = heritageCoordinates(draft);
  const map = coordinates ? `https://www.google.com/maps/search/?api=1&query=${coordinates[0]},${coordinates[1]}` : 'No pin added';
  const body = `Heritage story: ${draft.title}\nPlace or community: ${draft.place}\nMap: ${map}\n\n${draft.story}\n\nSources, photo links and credits: ${draft.credit || 'Not supplied'}\n\nShared by: ${draft.name}\nReply to: ${draft.email}\n\nPlease review this story for ActForGoa. I have permission to share the submitted material.`;
  return 'mailto:info@actforgoa.org?' + new URLSearchParams({subject:'Celebrate Goan heritage: '+draft.title,body}).toString().replace(/\+/g,'%20');
}
