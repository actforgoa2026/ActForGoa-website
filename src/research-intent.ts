/** Intent hints guide retrieval; they never establish legal requirements. */
export function premisesIntent(question: string): {venue:string;construction:boolean}|null {
 const text=question.toLowerCase();
 if (/\b(sand ?bars?|pressure|steel bars?|bar association|bar exam)\b/.test(text)) return null;
 const venue=text.match(/\b(bar|pub|restaurant|cafe|café|shop|hotel|guesthouse|office|warehouse|factory|school|clinic)\b/)?.[1];
 const action=/\b(build|building|construct\w*|erect|renovat\w*|convert\w*|rebuild\w*)\b/.test(text);
 if(!action&&!(venue&&/\b(open|start|set up|operate)\b/.test(text)))return null;
 return {venue:venue||'commercial premises',construction:action};
}
export function relatedResearchFollowups(question:string): {label:string;question:string}[] {
 const intent=premisesIntent(question);
 if(intent)return [
  {label:'Build a new structure',question:`What does the library establish about building permission and planning approval to construct a new building for a ${intent.venue} in Goa? Separate general construction rules from any use-specific conditions the evidence does not establish.`},
  {label:'Use an existing building',question:`What does the library establish about change of use and permissions for opening a ${intent.venue} in an existing building in Goa?`},
  {label:'Licences to operate',question:`What evidence does the library contain about operating licences for a ${intent.venue} in Goa? Distinguish operating licences from building permission and state any specific gaps.`},
 ];
 if(/\b(tree|felling|cutting)\b/i.test(question))return [
  {label:'Check permission requirements',question:'What does the Goa library establish about permission to cut a tree, including exceptions?'},
  {label:'What should I record?',question:'What evidence should I record before reporting suspected unlawful tree cutting in Goa?'},
 ];
 return [
  {label:'Explain more simply',question:`Explain this question in simpler language, keeping the important conditions: ${question}`},
  {label:'What can I do next?',question:`What practical next steps are supported by the library for this question: ${question}`},
 ];
}
