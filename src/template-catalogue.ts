import {guideDocuments} from './guides';
import {parseTemplate} from './template-model';
import sources from './content/templates.json';
import {templateIdFromUrl} from './template-path';
export {templateIdFromUrl, templatePath} from './template-path';

export const templates = Object.entries(sources).map(([path, source]) => {
 const id = templateIdFromUrl(path);
 const guide = guideDocuments.find(g => g.listed && g.templates.some(t => templateIdFromUrl(t.url) === id));
 const label = guide?.templates.find(t => templateIdFromUrl(t.url) === id)?.label;
 const template = parseTemplate(id, source);
 return {...template, label: label || template.title, guideId: guide?.id, guideTitle: guide?.title};
});
