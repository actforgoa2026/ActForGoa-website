export type TopicIconName = 'waste' | 'nature' | 'water' | 'community' | 'grow' | 'heritage' | 'mobility' | 'health' | 'report' | 'truck' | 'recycle' | 'book' | 'animal' | 'building';
export interface ActionLink { label: string; href: string; download?: boolean }
export interface TopicAction {
 id: string; label: string; icon: TopicIconName; query: string;
 question?: string; choices?: TopicAction[];
 steps?: string[]; links?: ActionLink[]; resourceIds?: string[]; peopleIds?: string[];
}
export interface TopicFlow { slug: string; topic: string; label: string; icon: TopicIconName; actions: TopicAction[] }
const guide = (label: string, id: string, section = ''): ActionLink => ({label, href: '/read/' + id + (section ? '#' + section : '')});
const report = (label = 'Open the government complaint service'): ActionLink => ({label, href:'https://cmhelpline.dpg.goa.gov.in/'});
const complaint: ActionLink = {label:'Download a complaint template',href:'/guides/templates/01-complaint.txt',download:true};
const services = (): ActionLink => ({label:'Find a collection service',href:'#topic-people'});
const collectSteps = ['Tell the service where you are, what you need removed, and roughly how much there is.', 'Ask whether they collect that type of waste, what it costs, and when they can come.'];

export const topicFlows: TopicFlow[] = [
 {slug:'waste',topic:'Waste & recycling',label:'Waste & recycling',icon:'waste',actions:[
  {id:'report-dumping',label:'Report illegal dumping',icon:'report',query:'waste dumping pollution',steps:['Note the location, date and what has been dumped. Add photos if you can take them safely.','Report it to the Panchayat or municipal council responsible for that location. The government complaint service can help route the issue.','Keep the complaint reference so you can follow up.'],links:[report(),complaint,guide('How to report and follow up','guide-reporting')],resourceIds:['guide-reporting','resource-4ff53417d5']},
  {id:'collection',label:'Get extra rubbish collected',icon:'truck',query:'waste collection disposal',peopleIds:['org-165','org-20','org-182'],question:'What do you need to get rid of?',choices:[
   {id:'household',label:'Household rubbish',icon:'waste',query:'waste collection disposal',peopleIds:['org-165','org-20','org-182'],steps:collectSteps,links:[services(),guide('How to separate your waste','resource-5731eea370')]},
   {id:'bulky',label:'Furniture or bulky items',icon:'truck',query:'waste collection recycling',peopleIds:['org-165','org-166','org-20'],steps:collectSteps,links:[services(),guide('Waste services in Goa','resource-4ff53417d5')]},
   {id:'garden',label:'Garden or food waste',icon:'grow',query:'compost garden waste',peopleIds:['org-20','org-165'],steps:collectSteps,links:[services(),guide('See what you can compost at home','resource-96e1739bcc')]},
   {id:'electronics',label:'Electronics or batteries',icon:'recycle',query:'e-waste recycling',peopleIds:['org-171','org-172'],steps:['Find a service that accepts your type of electronic item or battery.','Confirm accepted items, drop-off hours or collection options before travelling.'],links:[guide('Find e-waste collection information','resource-5a278571ec')]},
  ]},
  {id:'recycling',label:'Find a recycler',icon:'recycle',query:'recycling waste plastic paper',peopleIds:['org-166','org-164','org-20'],links:[guide('Where to take electronics','resource-5a278571ec'),guide('How to separate your waste','resource-5731eea370')],steps:['Choose a service below and check which materials it accepts.','Ask about collection, drop-off and any charges before taking your items.']},
  {id:'compost',label:'Start composting',icon:'grow',query:'composting compost food waste',links:[guide('Learn to compost at home','resource-96e1739bcc'),guide('Learn to separate food waste','resource-5731eea370')]},
  {id:'missed-collection',label:'Report a missed collection',icon:'report',query:'waste collection',steps:['Note your address and the date the collection was missed.','Ask your Panchayat or municipal council about the next collection. You can use the government complaint service if you need help reaching the right office.'],links:[report(),complaint]},
  {id:'clean-up',label:'Organise a clean-up',icon:'community',query:'clean up waste community',peopleIds:['org-25','org-181','org-206'],links:[guide('Plan a clean-up step by step','resource-7f75d245d3')],steps:['Choose a location and agree how the collected waste will be removed.','Find local groups below to discuss supplies, volunteers and collection.']},
 ]},
 {slug:'water',topic:'Water & environment',label:'Water & environment',icon:'water',actions:[
  {id:'supply',label:'Report a water problem',icon:'report',query:'water supply',links:[report(),guide('Find the right office','guide-reporting','choose-where-to-report')]},
  {id:'pollution',label:'Report pollution or sewage',icon:'water',query:'pollution water sewage',links:[{label:'Open the pollution complaint form',href:'https://goaspcb.gov.in/online-complaint-click-here/'},complaint,guide('What to include in your report','guide-reporting','prepare-the-evidence')],steps:['Note the location, time and what you observed.','Keep your complaint reference and any reply so you can follow up.']},
  {id:'rainwater',label:'Collect rainwater',icon:'water',query:'rain water harvesting',links:[{label:'Browse rainwater guides',href:'/search?q=rainwater&type=resource'}]},
  {id:'protect',label:'Protect a river, lake or coast',icon:'nature',query:'river wetland coast protection',links:[guide('Find the relevant authority','guide-environmental-protection')]},
 ]},
 {slug:'community',topic:'Community & rights',label:'Community & rights',icon:'community',actions:[
  {id:'report',label:'Report a local problem',icon:'report',query:'complaint community',links:[report(),complaint,guide('How to report and follow up','guide-reporting')]},
  {id:'records',label:'Request official records',icon:'book',query:'RTI information',links:[guide('How to make an RTI request','guide-reporting','use-rti-when-you-need-official-records'),{label:'Download a request template',href:'/guides/templates/03-rti-records-request.txt',download:true}]},
  {id:'volunteer',label:'Volunteer locally',icon:'community',query:'volunteer community',links:[guide('Explore volunteering','wp-2249'),{label:'Get involved with ActForGoa',href:'/get-involved'}]},
  {id:'support',label:'Find community support',icon:'health',query:'community rights support',links:[{label:'Browse community organisations',href:'/directory?topic=Community%20%26%20rights'}]},
 ]},
 {slug:'nature',topic:'Nature & wildlife',label:'Nature & wildlife',icon:'nature',actions:[
  {id:'animal',label:'Help an injured animal',icon:'animal',query:'animal welfare rescue',links:[guide('Find the right animal service','guide-animal-welfare','find-the-right-animal-service')]},
  {id:'trees',label:'Report tree cutting',icon:'report',query:'tree cutting forest',links:[guide('Check tree protection and permissions','guide-environmental-protection'),complaint]},
  {id:'wildlife',label:'Find wildlife or snake help',icon:'nature',query:'snake wildlife rescue',links:[guide('What to do around wildlife','guide-animal-welfare','find-the-right-animal-service'),guide('Browse wildlife rescue contacts','resource-590480849c')]},
  {id:'conserve',label:'Join a conservation project',icon:'community',query:'wildlife conservation nature',links:[{label:'Find conservation organisations',href:'/directory?topic=Nature%20%26%20wildlife'}]},
 ]},
 {slug:'food',topic:'Food & farming',label:'Food & farming',icon:'grow',actions:[
  {id:'grow',label:'Start growing food',icon:'grow',query:'farming garden growing',links:[guide('Choose your first step','guide-farming','choose-your-first-step')]},
  {id:'advice',label:'Get crop or soil advice',icon:'nature',query:'agriculture soil farming',links:[guide('Find farming advice','guide-farming')]},
  {id:'register',label:'Register or get farming support',icon:'book',query:'agriculture farming support',links:[guide('Registration and support','guide-farming'),{label:'Download a registration enquiry',href:'/guides/templates/09-farming-registration-enquiry.txt',download:true}]},
  {id:'damage',label:'Report crop damage',icon:'report',query:'agriculture crop damage',links:[guide('How to record and report damage','guide-farming')]},
 ]},
 {slug:'planning',topic:'Planning & mobility',label:'Building & transport',icon:'mobility',actions:[
  {id:'build',label:'Build or repair a property',icon:'building',query:'building architecture construction',links:[guide('Check the steps before building','guide-building')]},
  {id:'construction',label:'Report a construction concern',icon:'report',query:'construction planning',links:[guide('Find the right office','guide-reporting','choose-where-to-report'),complaint]},
  {id:'roads',label:'Report a road or access problem',icon:'mobility',query:'transport roads mobility',links:[report(),complaint]},
  {id:'professionals',label:'Find planning or design help',icon:'building',query:'architecture planning design',links:[{label:'Browse people and services',href:'/directory?topic=Planning%20%26%20mobility'}]},
 ]},
 {slug:'health',topic:'Health & wellbeing',label:'Health & wellbeing',icon:'health',actions:[
  {id:'health',label:'Find health organisations',icon:'health',query:'health wellbeing',links:[{label:'Browse health organisations',href:'/directory?topic=Health%20%26%20wellbeing'}]},
  {id:'disability',label:'Find disability support',icon:'community',query:'disability support',links:[{label:'Find disability services',href:'/search?q=disability&type=organisation'}]},
  {id:'mental-health',label:'Find mental health support',icon:'health',query:'mental health',links:[{label:'Find mental health organisations',href:'/search?q=mental%20health&type=organisation'}]},
  {id:'care',label:'Help someone in the community',icon:'community',query:'community care food support',links:[{label:'Explore ways to volunteer',href:'/get-involved'}]},
 ]},
 {slug:'culture',topic:'Culture & heritage',label:'Culture & heritage',icon:'heritage',actions:[
  {id:'learn',label:'Learn about Goan heritage',icon:'book',query:'heritage culture history',links:[{label:'Explore the reading library',href:'/library?topic=Culture%20%26%20heritage'}]},
  {id:'protect',label:'Protect a heritage place',icon:'heritage',query:'heritage conservation',links:[{label:'Find heritage organisations',href:'/directory?topic=Culture%20%26%20heritage'}]},
  {id:'stories',label:'Read local stories',icon:'book',query:'culture heritage',links:[{label:'Explore inspiring stories',href:'/stories?topic=Culture%20%26%20heritage'}]},
  {id:'share',label:'Share a story or project',icon:'community',query:'culture community',links:[{label:'Send your story to ActForGoa',href:'/contact?reason=Share%20a%20story%20or%20resource'}]},
 ]},
];

export const topicFor = (topic: string) => topicFlows.find(flow => flow.topic === topic);
export const topicHref = (topic: string) => '/topics/' + (topicFor(topic)?.slug ?? 'community');
export const actionHref = (flow: TopicFlow, action: TopicAction, parent?: TopicAction) => '/topics/' + flow.slug + '/' + (parent ? parent.id + '/' : '') + action.id;
