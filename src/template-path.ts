export const templateIdFromUrl = (url: string) => url.split('/').pop()!.replace(/\.(txt|md)$/, '');
export const templatePath = (url: string) => `/templates/${templateIdFromUrl(url)}`;
