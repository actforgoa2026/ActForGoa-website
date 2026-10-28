import {templatePath} from './template-path';

export type TopicIconName = 'waste' | 'nature' | 'water' | 'community' | 'grow' | 'heritage' | 'mobility' | 'health' | 'report' | 'truck' | 'recycle' | 'book' | 'animal' | 'building' | 'access' | 'stethoscope' | 'message' | 'file' | 'map';
export interface ActionLink { label: string; href: string; download?: boolean; icon?: TopicIconName }
export interface TopicAction {
 id: string; label: string; icon: TopicIconName; query: string;
 question?: string; choices?: TopicAction[];
 steps?: string[]; links?: ActionLink[]; resourceIds?: string[]; peopleIds?: string[];
}
export interface TopicFlow { slug: string; topic: string; label: string; icon: TopicIconName; actions: TopicAction[] }
export const topicDescriptions: Record<string, string> = {
 waste: 'Collection, recycling & dumping',
 nature: 'Animal help & conservation',
 water: 'Water supply & pollution',
 community: 'Youth care & community support',
 food: 'Growing food & farm support',
 culture: 'Heritage, arts & local groups',
 planning: 'Building work & getting around',
 health: 'Care, support & accessibility',
};
const guide = (label: string, id: string, section = ''): ActionLink => ({label, href: '/read/' + id + (section ? '#' + section : '')});
const report = (label = 'Open the government complaint service'): ActionLink => ({label, href:'https://cmhelpline.dpg.goa.gov.in/'});
const complaint: ActionLink = {label:'Write a complaint',href:'/templates/01-complaint',icon:'file'};
const services = (): ActionLink => ({label:'Find a collection service',href:'#topic-people'});
const collectSteps = ['Tell the service where you are, what you need removed, and roughly how much there is.', 'Ask whether they collect that type of waste, what it costs, and when they can come.'];

const people = (label: string): ActionLink => ({label,href:'#topic-people',icon:'community'});
const reading = (label: string): ActionLink => ({label,href:'#topic-reading',icon:'book'});
const form = (label: string, file: string, purpose?: 'support' | 'damage'): ActionLink => ({label,href:templatePath(file)+(purpose ? `?purpose=${purpose}` : ''),icon:'file'});
const serviceEnquiry = form('Write a service enquiry','18-service-enquiry.txt');
const inspection = form('Request an inspection','16-environment-records-and-inspection.txt');
const agriculture: ActionLink = {label:'Find the agriculture office',href:'https://www.goa.gov.in/department/agriculture/',icon:'grow'};
const buildingEnquiry = form('Ask about building permissions','06-project-enquiry.txt');
const vets: ActionLink = {label:'Find a government veterinary service',href:'https://ahvs.goa.gov.in/emergency-contact/',icon:'animal'};
const forest: ActionLink = {label:'Find Forest Department contacts',href:'https://forest.goa.gov.in/contact-us',icon:'nature'};
const animalSteps = ['Note the location, the animal’s condition and any nearby hazards without putting yourself at risk.','Ask the service whether it can attend or receive the animal, and how to arrange safe transport.'];
const wildlifeSteps = ['Keep a safe distance and keep people and pets away. Do not try to catch or move the animal.','Tell the Forest Department the location and what you can see. Ask for an authorised response.'];
const volunteer = (id: string, label: string, icon: TopicIconName, query: string, peopleIds: string[]): TopicAction => ({
 id,label,icon,query,peopleIds,links:[people('Find groups to help'),{label:'Ask ActForGoa about volunteering',href:'/get-involved',icon:'message'}],
 steps:['Choose a group and tell them your interests, skills and available time.','Ask what help is needed now and agree the role and arrangements before going.'],
});

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
  {id:'supply',label:'Report a water problem',icon:'water',query:'water supply',question:'What is happening?',choices:[
   {id:'no-water',label:'No water or low pressure',icon:'water',query:'water supply',links:[report('Report a water supply problem'),complaint],steps:['Have your address, nearest landmark and the dates of the problem ready.','Include your water connection number if you have it. Keep the complaint reference.']},
   {id:'leak',label:'A leaking or broken pipe',icon:'report',query:'water pipe leak',links:[report('Report the leak'),complaint],steps:['Note the exact location and when you noticed the leak. Add a photo taken from a safe place.','Keep the reference so you can follow up if the leak continues.']},
   {id:'quality',label:'Dirty or unusual tap water',icon:'water',query:'water quality pollution',links:[report('Report the water quality problem'),complaint],steps:['Describe the colour, smell or other change and when it started. Include the address and connection number if available.','Ask the water supplier what to do while the problem is checked.']},
  ]},
  {id:'pollution',label:'Report pollution or sewage',icon:'report',query:'pollution water sewage',peopleIds:['org-183'],links:[{label:'Open the pollution complaint form',href:'https://goaspcb.gov.in/online-complaint-click-here/',icon:'report'},complaint],steps:['Note the location, time and what you observed. Add photos only if it is safe.','Keep your complaint reference and any reply so you can follow up.'],resourceIds:['guide-reporting']},
  {id:'rainwater',label:'Collect rainwater',icon:'water',query:'rain water harvesting',peopleIds:['org-111','org-32'],links:[people('Find rainwater harvesting help'),serviceEnquiry],steps:['Tell the service about your roof, available space and what you want to use the water for.','Ask about a site visit, installation costs, maintenance and any permissions before agreeing to work.']},
  {id:'protect',label:'Protect a river, lake or coast',icon:'nature',query:'river wetland coast protection',question:'Which place needs help?',choices:[
   {id:'river-lake',label:'A river, lake or wetland',icon:'water',query:'river wetland water',peopleIds:['org-29','org-18'],links:[report('Report damage or obstruction'),inspection],steps:['Record the location and what has changed. Keep dated photographs and any documents you already have.','Ask the authority to identify the protections and permissions that apply to this place.'],resourceIds:['guide-environmental-protection']},
   {id:'coast',label:'A beach or coastal area',icon:'nature',query:'coast marine conservation',peopleIds:['org-3','org-18'],links:[{label:'Find the coastal authority',href:'https://www.czma.goa.gov.in/Default.aspx',icon:'heritage'},inspection],steps:['Note the location and the activity you are concerned about.','Ask the coastal authority to check the site and the relevant clearance.'],resourceIds:['guide-environmental-protection']},
  ]},
 ]},
 {slug:'community',topic:'Community & rights',label:'Community and Youth',icon:'community',actions:[
  {id:'report',label:'Report a local problem',icon:'report',query:'complaint community',question:'Where are you in the process?',choices:[
   {id:'new',label:'Make a new complaint',icon:'report',query:'complaint community',links:[report('Start a government complaint'),complaint],steps:['Describe what happened, where and when. Include what you would like the office to do.','Save a copy and the complaint reference.'],resourceIds:['guide-reporting']},
   {id:'follow-up',label:'Follow up a complaint',icon:'file',query:'complaint follow up',links:[report('Open the complaint tracking service'),form('Write a follow-up letter','02-follow-up.txt')],steps:['Find your original complaint reference, submission date and any reply.','Ask for the current status and the next action, and keep a copy of your follow-up.'],resourceIds:['guide-reporting']},
  ]},
  {id:'records',label:'Request official records',icon:'file',query:'RTI information',links:[form('Write an RTI request','03-rti-records-request.txt'),{label:'Find the public information officer',href:'https://dip.goa.gov.in/details-of-pio-apio-faa/',icon:'community'}],steps:['Name the records, office and time period you need.','Check the receiving officer, current fee and accepted submission method before sending.'],resourceIds:['guide-reporting']},
  {id:'volunteer',label:'Volunteer locally',icon:'community',query:'volunteer community',question:'What would you like to help with?',choices:[
   volunteer('environment','Nature and clean-ups','nature','environment clean up',['org-206','org-181','org-3']),
   volunteer('animals','Animal care','animal','animal welfare',['org-2','org-52']),
   volunteer('people','People in the community','community','community support',['org-7','org-12','org-176']),
   volunteer('arts','Arts and local culture','heritage','arts culture',['org-10','org-174']),
  ]},
  {id:'support',label:'Find community support',icon:'community',query:'community support',question:'What kind of help do you need?',choices:[
   {id:'rights',label:'Legal advice or rights',icon:'file',query:'rights legal',peopleIds:['org-168','org-13','org-5'],links:[{label:'Find legal aid in Goa',href:'https://goa.nalsa.gov.in/legal-aid/',icon:'file'},people('See rights organisations')],steps:['Explain the help you need and ask about eligibility and the next step.','Keep relevant letters or documents ready to discuss privately.']},
   {id:'family',label:'Child or family support',icon:'community',query:'child development family',peopleIds:['org-12','org-16','org-201'],links:[people('See child and family services'),serviceEnquiry],steps:['Tell the organisation the age of the child and the kind of support you are looking for.','Ask about an appointment, fees and what to bring before visiting.']},
   {id:'food-shelter',label:'Food or shelter',icon:'building',query:'food homeless shelter',peopleIds:['org-157','org-199','org-200'],links:[people('See food and shelter organisations'),serviceEnquiry],steps:['Explain where help is needed and whether it is food, temporary shelter or another need.','Ask what support is currently available and how to access it.']},
   {id:'disability',label:'Disability support',icon:'access',query:'disability support',links:[{label:'Choose the support you need',href:'/topics/health/disability',icon:'access'},people('See disability organisations')],peopleIds:['org-5','org-16','org-15','org-14']},
  ]},
 ]},
 {slug:'nature',topic:'Nature & wildlife',label:'Biodiversity',icon:'nature',actions:[
  {id:'animal',label:'Help an injured animal',icon:'animal',query:'animal welfare rescue',question:'What kind of animal needs help?',choices:[
   {id:'pet',label:'A dog, cat or other pet',icon:'animal',query:'animal veterinary clinic',peopleIds:['org-2','org-52'],links:[vets,people('See animal welfare organisations'),form('Prepare an animal assistance note','12-animal-assistance.txt')],steps:animalSteps,resourceIds:['guide-animal-welfare']},
   {id:'livestock',label:'Cattle or a farm animal',icon:'animal',query:'cattle animal veterinary',peopleIds:['org-2'],links:[vets,people('See animal welfare organisations')],steps:animalSteps,resourceIds:['guide-animal-welfare']},
   {id:'wild',label:'A wild animal or bird',icon:'nature',query:'wildlife rescue',peopleIds:['org-27'],links:[forest,form('Prepare an animal assistance note','12-animal-assistance.txt')],steps:wildlifeSteps,resourceIds:['guide-animal-welfare']},
  ]},
  {id:'trees',label:'Report tree cutting',icon:'nature',query:'tree cutting forest',peopleIds:['org-18','org-27'],links:[{...forest,label:'Find the Forest Department office'},inspection],steps:['Record the location, time and observed activity from a safe place.','Ask the Forest Department to check which permissions and protections apply.'],resourceIds:['guide-environmental-protection']},
  {id:'wildlife',label:'Get help with wildlife',icon:'nature',query:'wildlife snake rescue',links:[forest,form('Prepare an animal assistance note','12-animal-assistance.txt')],steps:wildlifeSteps,peopleIds:['org-27'],resourceIds:['guide-animal-welfare','resource-590480849c']},
  {id:'conserve',label:'Join a conservation project',icon:'community',query:'wildlife conservation nature',question:'Where would you like to help?',choices:[
   volunteer('land','Forests and local wildlife','nature','forest biodiversity',['org-27','org-206','org-18']),
   volunteer('sea','Coasts and marine life','water','marine coast conservation',['org-3','org-25']),
  ]},
 ]},
 {slug:'food',topic:'Food & farming',label:'Food & farming',icon:'grow',actions:[
  {id:'grow',label:'Start growing food',icon:'grow',query:'farming garden growing',question:'Where do you want to grow?',choices:[
   {id:'home',label:'At home or in a garden',icon:'grow',query:'kitchen garden organic',peopleIds:['org-142'],links:[people('Find kitchen-garden help'),serviceEnquiry],steps:['Note how much space and sunlight you have, and what you would like to grow.','Ask about a beginner workshop or advice for your space.'],resourceIds:['resource-96e1739bcc']},
   {id:'farm',label:'On a farm or shared plot',icon:'nature',query:'agriculture farming',peopleIds:['org-180'],links:[form('Fill in a farm plan','10-farm-plan-and-log.md'),agriculture],steps:['Confirm your right to cultivate the land before starting work.','Discuss the crop, water, soil and any permissions with the relevant agriculture office.'],resourceIds:['guide-farming']},
  ]},
  {id:'advice',label:'Get crop or soil advice',icon:'grow',query:'agriculture soil farming',question:'What do you need help with?',choices:[
   {id:'soil',label:'Test my soil',icon:'grow',query:'soil agriculture',peopleIds:['org-180'],links:[{label:'Find a soil-testing laboratory',href:'https://ccari.res.in/soilgoa/where.php',icon:'map'},form('Fill in a farm plan','10-farm-plan-and-log.md')],steps:['Ask the laboratory how to collect and label a sample before taking one.','Confirm fees, opening hours and how you will receive the results.'],resourceIds:['guide-farming']},
   {id:'crop',label:'Get help with crops or pests',icon:'nature',query:'crop agriculture',peopleIds:['org-180'],links:[{label:'Contact ICAR for crop advice',href:'https://ccari.res.in/atdcnew.html',icon:'grow'},agriculture],steps:['Have the crop name, location and photographs ready, along with when the problem began.','Tell the adviser about any treatment already used.'],resourceIds:['guide-farming']},
  ]},
  {id:'register',label:'Register or get farming support',icon:'file',query:'agriculture farming support',question:'What would you like to do?',choices:[
   {id:'krishi',label:'Apply for or update a Krishi Card',icon:'file',query:'Krishi agriculture',peopleIds:['org-180'],links:[form('Write a registration enquiry','09-farming-registration-enquiry.txt'),agriculture],steps:['Tell the agriculture office whether this is a new registration or a change to an existing card.','Ask for the current application, documents and submission method.'],resourceIds:['guide-farming']},
   {id:'scheme',label:'Ask about farming schemes',icon:'grow',query:'agriculture farming schemes',peopleIds:['org-180'],links:[form('Ask about farming support','11-farming-support-or-damage.txt','support'),agriculture],steps:['Describe the activity you want support for and its estimated cost.','Check eligibility, deadlines and whether approval is needed before spending.'],resourceIds:['guide-farming']},
  ]},
  {id:'damage',label:'Report crop damage',icon:'report',query:'agriculture crop damage',peopleIds:['org-180'],links:[form('Prepare a crop damage report','11-farming-support-or-damage.txt','damage'),agriculture],steps:['Record the date, affected crop and area. Keep photographs and relevant receipts.','Contact the agriculture office promptly to ask about inspection, deadlines and the correct claim form.'],resourceIds:['guide-farming']},
 ]},
 {slug:'planning',topic:'Planning & mobility',label:'Building & transport',icon:'mobility',actions:[
  {id:'build',label:'Build or repair a property',icon:'building',query:'building architecture construction',question:'What work are you planning?',choices:[
   {id:'new',label:'A new building or extension',icon:'building',query:'building architecture',peopleIds:['org-119','org-108'],links:[form('Fill in the building checklist','07-building-checklist.md'),buildingEnquiry],steps:['Identify the planning authority and local licensing office for the property.','Confirm required permissions with them before starting work.'],resourceIds:['guide-building']},
   {id:'repair',label:'Repairs or restoration',icon:'heritage',query:'architecture restoration',peopleIds:['org-119'],links:[form('Ask about building permissions','06-project-enquiry.txt'),people('Find restoration and design help')],steps:['Describe the proposed repairs and include photographs and existing approvals if available.','Ask the responsible offices which permissions are needed before starting.'],resourceIds:['guide-building']},
   {id:'complete',label:'Completion or occupancy',icon:'file',query:'building completion occupancy',links:[form('Ask about completion or occupancy','08-completion-enquiry.txt'),buildingEnquiry],steps:['Gather the approved plans, permissions and completion records.','Ask the planning and local licensing offices which certificates and inspections remain.'],resourceIds:['guide-building']},
  ]},
  {id:'construction',label:'Report a construction concern',icon:'report',query:'construction planning',links:[report('Report a construction concern'),complaint,form('Request the project records','03-rti-records-request.txt')],steps:['Note the location and what you observed without entering the site.','Ask the relevant authority to check the permissions and activity; keep the complaint reference.'],resourceIds:['guide-building','guide-reporting']},
  {id:'roads',label:'Report a road or access problem',icon:'mobility',query:'transport roads mobility',question:'What needs attention?',choices:[
   {id:'damage',label:'Potholes or a damaged road',icon:'mobility',query:'roads transport',links:[report('Report the road damage'),complaint],steps:['Give the road name, nearest landmark and a clear description of the damage.','Add photographs only if you can take them without stepping into traffic.']},
   {id:'access',label:'A blocked or inaccessible path',icon:'access',query:'access disability',peopleIds:['org-5'],links:[report('Report the access problem'),complaint],steps:['Explain where the route is blocked and who is affected.','Describe the change needed and keep the complaint reference.']},
   {id:'lights',label:'Street lights not working',icon:'report',query:'road street lighting',links:[report('Report a street light problem'),complaint],steps:['Note the location, nearby landmark and pole number if visible.','Do not touch exposed wiring; describe any visible hazard in the report.']},
  ]},
  {id:'professionals',label:'Find planning or design help',icon:'building',query:'architecture planning design',question:'What kind of help do you need?',choices:[
   {id:'design',label:'Building design or restoration',icon:'building',query:'architecture restoration design',peopleIds:['org-119','org-108'],links:[people('See design professionals'),serviceEnquiry],steps:['Describe your property, proposed work and budget.','Ask about relevant experience, fees and the permissions the work needs.']},
   {id:'systems',label:'Solar, water or greener systems',icon:'water',query:'solar water environmental systems',peopleIds:['org-91','org-32','org-129'],links:[people('See local system specialists'),serviceEnquiry],steps:['Describe the system you need and your site.','Ask for a site assessment, itemised costs and maintenance requirements.']},
  ]},
 ]},
 {slug:'health',topic:'Health & wellbeing',label:'Health & wellbeing',icon:'health',actions:[
  {id:'health',label:'Find health services',icon:'stethoscope',query:'health wellbeing',question:'What care are you looking for?',choices:[
   {id:'clinic',label:'A health centre or hospital',icon:'stethoscope',query:'health services',peopleIds:['org-9'],links:[{label:'Find hospitals and health centres',href:'https://www.goa.gov.in/department/health-services/',icon:'map'},people('See community health organisations')],steps:['Use the official health directory to find a centre near you.','Check the service, opening hours and registration arrangements before visiting.']},
   {id:'child',label:'Child development and family care',icon:'community',query:'child development family',peopleIds:['org-12','org-16'],links:[people('See child development services'),serviceEnquiry],steps:['Explain the child’s age and what support you are looking for.','Ask about an assessment, appointment, fees and what to bring.']},
  ]},
  {id:'disability',label:'Find disability support',icon:'access',query:'disability support',question:'What would be useful?',choices:[
   {id:'learning',label:'Learning and daily-living support',icon:'community',query:'disability education support',peopleIds:['org-16','org-15','org-175'],links:[people('See learning and support services'),serviceEnquiry],steps:['Describe the person’s age and the type of support needed.','Ask about current programmes, accessibility, costs and assessment requirements.']},
   {id:'rights',label:'Access and disability rights',icon:'access',query:'disability rights access',peopleIds:['org-5'],links:[people('Find disability rights support'),{label:'Ask about legal aid',href:'https://goa.nalsa.gov.in/legal-aid/',icon:'file'}],steps:['Explain the barrier or rights concern and the support you need.','Ask what information or documents would help with the next step.']},
   {id:'vision',label:'Support for sight loss',icon:'access',query:'blind vision support',peopleIds:['org-14','org-15'],links:[people('See sight-loss support organisations'),serviceEnquiry],steps:['Ask about the specific support you need, such as learning, mobility or daily living.','Confirm availability and visit arrangements directly with the organisation.']},
  ]},
  {id:'mental-health',label:'Find mental health support',icon:'message',query:'mental health',question:'What would help you take the next step?',choices:[
   {id:'support',label:'Talk to a support organisation',icon:'message',query:'mental health support',peopleIds:['org-17'],links:[{label:'Email COOJ about support',href:'mailto:coojtrust@yahoo.co.in',icon:'message'},people('See the organisation’s listing')],steps:['Ask about the support currently offered and how to arrange a first conversation.','You can ask about language, privacy and costs before sharing personal details.']},
   {id:'clinic',label:'Find a mental health clinic',icon:'stethoscope',query:'psychiatry mental health',peopleIds:['org-186'],links:[{label:'Check IPHB outpatient services',href:'https://iphb.goa.gov.in/services/',icon:'stethoscope'},people('See the institute’s listing')],steps:['Check the institute’s current registration arrangements before visiting.','Ask what records to bring and whether you need an appointment.']},
  ]},
  {id:'care',label:'Help someone in the community',icon:'community',query:'community care food support',question:'How would you like to help?',choices:[
   {id:'food',label:'Help with food or basic needs',icon:'community',query:'food homeless community',peopleIds:['org-157','org-176'],links:[people('See local support initiatives'),serviceEnquiry],steps:['Ask what items or help are needed now before collecting donations.','Agree how and when to deliver them with the organisation.']},
   volunteer('time','Offer my time or skills','health','community health volunteer',['org-9','org-12','org-17']),
  ]},
 ]},
 {slug:'culture',topic:'Culture & heritage',label:'Culture & heritage',icon:'heritage',actions:[
  {id:'learn',label:'Explore Goan heritage',icon:'heritage',query:'heritage culture history',question:'What would you like to explore?',choices:[
   {id:'places',label:'Places and their history',icon:'map',query:'heritage places history',links:[reading('Explore local heritage places'),guide('Explore Goa’s World Heritage sites','resource-280a403dc9')],resourceIds:['resource-7995182e59','resource-280a403dc9','resource-d7baf87251']},
   {id:'arts',label:'Arts and community activities',icon:'community',query:'art culture workshops',peopleIds:['org-10','org-174'],links:[people('Find arts and culture groups'),serviceEnquiry],steps:['Ask which workshops or activities are coming up.','Confirm the date, location, language and cost before making plans.']},
  ]},
  {id:'protect',label:'Protect a heritage place',icon:'heritage',query:'heritage conservation',question:'What do you need to do?',choices:[
   {id:'damage',label:'Report damage or a threat',icon:'report',query:'heritage conservation',peopleIds:['org-119'],links:[{label:'Find the Archaeology Department',href:'https://www.goa.gov.in/department/department-of-archaeology/',icon:'heritage'},inspection],steps:['Record the location and what has happened, with photographs if safe.','Ask the department to confirm the site’s protection and the responsible authority.'],resourceIds:['resource-34ba0deb26','resource-1de9c0a1b1']},
   {id:'restore',label:'Care for or restore a building',icon:'building',query:'heritage restoration architecture',peopleIds:['org-119','org-108'],links:[people('Find restoration professionals'),form('Ask about building permissions','06-project-enquiry.txt')],steps:['Gather photographs, existing approvals and a description of the proposed work.','Check permissions with the responsible authorities before beginning restoration.'],resourceIds:['guide-building']},
  ]},
  {id:'stories',label:'Read local stories',icon:'book',query:'culture heritage stories',links:[reading('Choose a story below'),{label:'Explore all local stories',href:'/stories?topic=Culture%20%26%20heritage',icon:'book'}],resourceIds:['wp-4662','wp-9323','resource-d7baf87251']},
  {id:'share',label:'Share a story or project',icon:'message',query:'culture community',question:'What would you like to share?',choices:[
   {id:'story',label:'A local story or resource',icon:'book',query:'culture stories',links:[{label:'Prepare an email to ActForGoa',href:'/contact?reason=Share%20a%20story%20or%20resource',icon:'message'},reading('See examples from the community')],steps:['Include a short summary, useful links and photo credits. Share only material you have permission to share.','You can review the email in your email app before sending it.'],resourceIds:['wp-4662','wp-9323']},
   {id:'organisation',label:'An organisation or project',icon:'community',query:'culture community',links:[{label:'Suggest a directory listing',href:'/contact?reason=List%20an%20organisation',icon:'message'},people('See existing community listings')],peopleIds:['org-174','org-10'],steps:['Include the name, location, what the group does and a public website or contact.','The form prepares an email for you to review and send.']},
  ]},
 ]},
];

export const topicFor = (topic: string) => topicFlows.find(flow => flow.topic === topic);
export const topicHref = (topic: string) => '/topics/' + (topicFor(topic)?.slug ?? 'community');
export const actionHref = (flow: TopicFlow, action: TopicAction, parent?: TopicAction) => '/topics/' + flow.slug + '/' + (parent ? parent.id + '/' : '') + action.id;
