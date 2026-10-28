export const templateIdFromUrl = (url: string) => url.split(/[?#]/)[0].split('/').pop()!.replace(/\.(txt|md)$/, '');
export const templatePath = (url: string) => `/templates/${templateIdFromUrl(url)}`;

export function templatePurpose(search: string): 'support' | 'damage' | undefined {
 const purpose = new URLSearchParams(search).get('purpose');
 return purpose === 'support' || purpose === 'damage' ? purpose : undefined;
}
