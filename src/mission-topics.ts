import type { ActionLink, TopicAction, TopicFlow, TopicIconName } from './topic-flows';

const read = (label: string, id: string): ActionLink => ({ label, href: '/read/' + id, icon: 'book' });
const link = (label: string, href: string, icon: TopicIconName = 'book'): ActionLink => ({ label, href, icon });
const ask = (subject: string): ActionLink => link('Ask ActForGoa about ' + subject, '/contact?' + new URLSearchParams({ reason: 'Ask a question', subject }), 'message');
const people = (label = 'Find local organisations'): ActionLink => link(label, '#topic-people', 'community');
const plan = (topic = ''): ActionLink => link('Explore the climate action plan', '/climate-plan' + (topic ? '/' + topic : ''), 'nature');
const step = (id: string, label: string, icon: TopicIconName, query: string, links: ActionLink[], extra: Partial<TopicAction> = {}): TopicAction => ({ id, label, icon, query, links, ...extra });
const initiative = (id: string, label: string): TopicAction => step(id, label, 'community', label, [ask(label), link('Explore collaborative action', 'https://actforgoa.lovable.app/', 'community')], {
  description: 'Find out how to contribute and ask the team about current activities.',
  steps: ['Share your interests, skills and available time with ActForGoa.', 'Ask about the current coordinator, upcoming activities and how to join.'],
});
const greenViksit = (): TopicAction => step('green-viksit', 'Green Viksit Goa recommendations', 'book', 'Green Viksit Goa', [ask('the latest Green Viksit Goa recommendations'), read('Read the 2025 consultation archive', 'wp-9389')], {
  description: 'Ask for the latest recommendations. The linked consultation is the 2025 archive.', resourceIds: ['wp-9389'],
});
const support = (id: string, label: string, query: string, peopleIds: string[]): TopicAction => step(id, label, 'community', query, [people('Find groups to support'), ask(label)], {
  peopleIds, steps: ['Ask the group what help is needed now before collecting materials or arranging a visit.', 'Agree a useful role, the location and any costs or equipment with the organiser.'],
});
const circularStrategy = step('circular-strategy', 'Goa’s circular economy strategy', 'recycle', 'circular economy resource efficiency', [
  link('Read about the 2020 Goa strategy', 'https://www.eeas.europa.eu/delegations/india/goa-becomes-india%E2%80%99s-first-state-have-resource-efficiency-strategy-measures-suggested-tourism_und_en'),
  read('Explore circular economy ideas', 'wp-6444'), ask('the current circular economy strategy'),
], { description: 'Explore the resource-efficiency strategy launched in 2020, and ask about its current implementation.', resourceIds: ['wp-6444'] });

/** Keep established deep links while presenting the team's affirmative-action-first menus. */
export function buildMissionTopics(original: TopicFlow[]): TopicFlow[] {
  const base = (slug: string) => original.find(flow => flow.slug === slug)!;
  const old = (slug: string, id: string) => base(slug).actions.find(action => action.id === id)!;
  const revise = (slug: string, label: string, introduction: string, actions: TopicAction[]): TopicFlow => ({
    ...base(slug), label, introduction, actions,
    legacyActions: base(slug).actions.filter(action => !actions.some(next => next.id === action.id)),
  });
  const fresh = (slug: string, label: string, icon: TopicIconName, introduction: string, catalogueTopics: string[], actions: TopicAction[]): TopicFlow => ({ slug, topic: label, label, icon, introduction, catalogueTopics, actions });

  const waste = revise('waste', 'Waste and recycling', 'Goa has waste-management infrastructure. How can we care better for the materials we use, reduce waste and keep resources in use?', [
    step('segregation', 'Segregate waste and arrange collection', 'waste', 'waste segregation collection', [read('How to segregate your waste', 'resource-5731eea370'), link('Check Goa’s 2026 segregation guidance', 'https://www.pib.gov.in/PressReleasePage.aspx?PRID=2317910&lang=1&reg=1'), people('Find waste services')], { peopleIds: ['org-182','org-20'], description: 'Start at home: separate materials and check your local collection arrangements.', steps: ['Check current segregation categories and collection days with your Panchayat or municipality.', 'Keep materials separated for collection. Use the current government guidance alongside the archived infographic.'] }),
    old('waste','compost'),
    { ...old('waste','recycling'), links: [...old('waste','recycling').links!, link('Find pre-loved and second-hand options', '/topics/waste/pre-loved', 'recycle')] },
    step('reduce', 'How to create less waste', 'recycle', 'reduce reuse waste', [link('Find a zero-waste store or service', '/topics/waste/zero-waste'), link('Find pre-loved and second-hand options', '/topics/waste/pre-loved')], { steps: ['Use what you already own, repair what you can, and carry reusable bags and containers.', 'Borrow, share or buy second-hand where practical. Choose refill options and less packaging.'] }),
    step('zero-waste', 'Find a zero-waste store or service', 'recycle', 'zero waste refill', [people('Explore stores and services'), ask('zero-waste options near you')], { peopleIds: ['org-50','org-54','org-178'], description: 'Check current opening hours, services and refill arrangements directly.' }),
    { ...old('waste','clean-up'), label: 'Organise or join a clean-up', question: 'How would you like to take part?', choices: [
      { ...old('waste','clean-up'), id: 'organise', label: 'Organise a clean-up' },
      support('join','Join an existing clean-up','clean up waste community',['org-25','org-181','org-206']),
    ] },
    support('support', 'Support a local waste initiative', 'waste community recycling', ['org-20','org-54','org-206']),
    circularStrategy, initiative('innovation-lab', 'Waste and Circularity Innovation Lab'), greenViksit(),
    { id: 'report', label: 'Report a waste problem or request collection', icon: 'report', query: 'waste dumping collection', concern: true, question: 'What do you need help with?', choices: [
      old('waste','report-dumping'), old('waste','missed-collection'),
      step('extra-collection', 'Get extra waste collected', 'truck', 'waste collection', [link('Choose the materials to collect', '/topics/waste/collection', 'truck'), people('Find a collection service')], { peopleIds: ['org-165','org-20','org-182'] }),
    ] },
  ]);
  waste.legacyActions!.push(step('pre-loved', 'Find a pre-loved or second-hand store', 'recycle', 'second hand reuse pre loved', [ask('pre-loved stores and reuse services'), link('Suggest a second-hand store', '/contact?reason=List%20an%20organisation&subject=Second-hand%20store')], { description: 'Help build a current list of places to buy, donate or exchange used items.', steps: ['Tell the team your area and the items you want to find or pass on.', 'Confirm what a store accepts, its opening hours and collection arrangements before travelling.'] }));

  const water = revise('water', 'Water', 'Care for Goa’s water by recharging groundwater, reducing pollution and protecting the rivers, lakes and wetlands we share.', [
    { ...old('water','rainwater'), label: 'Groundwater recharge guidance', links: [plan('water'), people('Find rainwater and recharge advice'), ask('groundwater recharge')], steps: ['Ask a local water specialist to assess your roof, soil, drainage and water use.', 'Discuss suitable rainwater harvesting or recharge options, water quality, permissions and ongoing maintenance before work begins.'] },
    step('reduce-pollution','Reduce water pollution','water','water sewage pollution',[plan('water'),read('Understand environmental protections','guide-environmental-protection'),people('Find water-care advice')],{peopleIds:['org-29','org-183'],steps:['Keep waste, oils and chemicals out of drains and water bodies.', 'Ask a qualified local service about maintaining your wastewater system and preventing leaks or untreated discharge.']}),
    step('test','Test your water','water','water quality testing',[people('Find the responsible water agencies'),ask('water-testing services')],{peopleIds:['org-29','org-183'],steps:['Describe the source of the water and the reason for testing.', 'Ask the agency which laboratory can test it, and confirm sampling instructions, fees and how the results will be explained.']}),
    {...support('protect','Protect a river, lake or wetland','river wetland conservation',['org-29','org-18','org-206']), question: 'Which place would you like to care for?', choices: old('water','protect').choices!.map(action => ({...action, links: [people('Find groups caring for this place'), ask('local water-care projects'), ...action.links!], steps: ['Ask local groups how to contribute to habitat care and monitoring.', ...action.steps!]}))},
    support('support','Support a local water-care project','water conservation',['org-32','org-111','org-206']), greenViksit(), initiative('collective','Water Collective and Innovation Lab'),
    { id:'report',label:'Report a water or sewage problem',icon:'report',query:'water sewage pollution',concern:true,question:'What is happening?',choices:[...old('water','supply').choices!,old('water','pollution')] },
  ]);
  // The former protection branch remains available to existing links.
  water.legacyActions!.push({ ...old('water','protect'), id:'protection-guidance' });
  const nature = revise('nature', 'Ecosystems and biodiversity', 'Goa’s nature is part of its quality of life. How can you help protect biodiversity and the habitats that sustain our communities?', [
    step('heritage','Learn about Goa’s natural heritage','nature','biodiversity natural heritage',[read('Explore Goa’s biodiversity hotspots','resource-c18d98880a'),read('Learn about Mollem’s biodiversity','resource-e6d8526edb')],{resourceIds:['resource-c18d98880a','resource-e6d8526edb']}),
    { ...old('nature','conserve'), choices: [
      ...old('nature','conserve').choices!.map(action => ({...action,label:action.id==='land'?'Forests':'Coasts and marine life'})),
      support('rivers','Rivers','river conservation',['org-29','org-206']), support('plateaus','Plateaus','plateau biodiversity',['org-18','org-206']),
      support('khazans','Khazans','khazan conservation',['org-18','org-180']), support('wetlands','Wetlands','wetland conservation',['org-29','org-18']),
    ] },
    step('plant','Plant trees','grow','native trees plantation',[read('Explore the Biodiversity Board plantation scheme','resource-e35cbca4dd'),people('Find local planting advice')],{peopleIds:['org-27','org-206'],resourceIds:['resource-e35cbca4dd'],steps:['Ask local conservation groups which native species and sites are suitable, and obtain the landholder’s consent.', 'Plan watering and long-term care with the group before planting. Confirm current scheme eligibility with the Biodiversity Board.']}),
    step('experience','Experience Goa’s biodiversity','map','nature trips biodiversity',[read('Explore nature experiences in Goa','resource-f1b8a130bc'),people('Find nature guides and organisations')],{peopleIds:['org-3','org-95','org-173'],resourceIds:['resource-f1b8a130bc'],steps:['Ask the organiser about current trips, group size, access and costs.', 'Choose experiences that respect wildlife, habitats and the people who live there.']}),
    step('monitor','Contribute to monitoring wildlife','nature','wildlife monitoring biodiversity',[people('Find conservation groups'),ask('community wildlife monitoring')],{peopleIds:['org-27','org-206','org-25'],steps:['Ask a conservation group which observations are useful and how to record them.', 'Observe without handling wildlife or disturbing nests, and avoid publicly sharing sensitive locations.']}),
    support('support','Support a local wildlife initiative','wildlife conservation',['org-27','org-3','org-206']), greenViksit(), initiative('collective','Nature Conservation and Restoration Collective'),
    old('nature','animal'),old('nature','wildlife'),
    {...old('nature','trees'),concern:true,resourceIds:['resource-2e0696fe34','resource-8394182d5f','guide-environmental-protection'],links:[read('Read the tree-cutting process','resource-8394182d5f'),...old('nature','trees').links!],infographic:{src:'/assets/team-notes/report-tree-cutting.jpg',alt:'ActForGoa poster explaining how to report tree cutting. The linked guide provides a text-based process.',source:'https://actforgoa.org/wp-content/uploads/2019/11/REPORT-CUTTING-OF-TREE_poster-copy-1024x483.jpg',caption:'ActForGoa’s archived reporting infographic. Check current contacts and procedures with the Forest Department.'}},
  ]);
  const village = revise('community','Village planning and development','Take part in local decisions so development supports the people, landscapes and ecological limits of each village.',[
    step('panchayat','Know your Panchayat and committees','community','panchayat gram sabha committees',[read('Understand your Panchayat','resource-d93dcb1318'),read('Take part in a Gram Sabha','resource-1460f83efc'),people('Find Panchayat information')],{peopleIds:['org-185'],resourceIds:['resource-d93dcb1318','resource-1460f83efc']}),
    step('permissions','Village and town planning permissions','building','planning permissions',[link('Choose your building or repair project','/topics/planning/build'),read('Read the local permission flowchart','resource-f21fd0f1a3')],{resourceIds:['resource-f21fd0f1a3','guide-building']}),
    step('development-plan','Gram Panchayat development planning','community','gram panchayat development plan',[read('Explore Gram Panchayat development planning','resource-b63eeadb83'),read('Prepare for a Gram Sabha','resource-1460f83efc'),people('Find the Directorate of Panchayats')],{peopleIds:['org-185'],resourceIds:['resource-b63eeadb83','resource-1460f83efc'],steps:['Ask your Panchayat for the current development plan and meeting schedule.', 'Discuss local water, waste, access and habitat priorities with neighbours, then bring practical proposals to the Gram Sabha.']}),greenViksit(),initiative('innovation-lab','Conscious Planning Innovation Lab'),
    {...old('community','report'),concern:true},
  ]);
  const tourism = fresh('tourism','Responsible tourism and hospitality','map','Enjoy and host Goa in ways that respect local culture, use fewer resources and give back to communities.',['Culture & heritage','Waste & recycling'],[
    step('visitor','Be a responsible tourist','map','responsible tourism',[read('Explore responsible nature experiences','resource-f1b8a130bc'),link('Respect local culture','/topics/culture/respect'),link('Reduce waste while visiting','/topics/waste/reduce')],{resourceIds:['resource-f1b8a130bc'],steps:['Choose local guides and producers, carry reusable items and leave places as you found them.', 'Ask before photographing people or entering community spaces. Follow the local guidance for wildlife and heritage sites.']}),
    ...[['operator','operator'],['venue','venue'],['event','event']].map(([id,noun])=>step(id,'Be a responsible '+noun,'community','responsible tourism hospitality '+noun,[link('Plan waste segregation and collection','/topics/waste/segregation'),plan('tourism'),read('Explore Goa’s tourism policies','resource-0ef8d29c93')],{resourceIds:['resource-0ef8d29c93'],steps:['Plan water, energy, waste and accessible arrival arrangements before welcoming guests.', 'Work with local suppliers and neighbours. Give staff and visitors clear guidance on reducing their footprint.']})),greenViksit(),
  ]);
  const food = revise('food','Food and farming','Support local growers, care for soil and water, and help Goa’s food traditions thrive.',[
    support('producers','Support local producers','local produce farming',['org-142','org-57','org-160']),
    step('natural-produce','Find naturally farmed produce','grow','organic naturally farmed produce',[people('Explore growers and local markets'),ask('naturally farmed produce near you')],{peopleIds:['org-142','org-57','org-160'],steps:['Ask producers how their food is grown and what is seasonal.', 'Confirm current market times, delivery areas and any certification claims directly.']}),
    step('communidade','Know your comunidade','community','comunidade farming land',[read('Understand land and cultivation checks','guide-farming'),ask('learning about your comunidade')],{resourceIds:['guide-farming']}),
    support('club','Create a farming club','community farming',['org-142','org-180']),
    step('packaging','Reduce your food packaging','recycle','food packaging refill',[link('Find a zero-waste store','/topics/waste/zero-waste'),link('Start composting','/topics/waste/compost')],{steps:['Bring reusable containers where suppliers accept them and choose loose produce when available.', 'Buy what you can use and share surplus through arrangements agreed with neighbours or local groups.']}),
    step('buy-local','Buy local','grow','local food producers',[people('Find local producers and markets'),ask('buying locally')],{peopleIds:['org-57','org-142','org-160']}),
    old('food','grow'),old('food','advice'),old('food','register'),greenViksit(),{...old('food','damage'),concern:true},
  ]);
  const planning = revise('planning','Green building and transport','Reducing construction waste, material use and carbon emissions helps care for people and wildlife. How can we build and travel within each place’s ecological limits?',[
    {...old('planning','build'),label:'Build in a responsible way',description:'Reduce your construction footprint from the first design decision.'},
    step('construction-waste','Find construction-waste depots','truck','construction waste depot',[people('Ask the waste-management agencies'),ask('authorised construction-waste depots')],{peopleIds:['org-182','org-183'],steps:['Describe the material, quantity and site location to the waste authority.', 'Confirm the authorised receiving site, accepted materials, transport and fees before arranging removal.']}),
    step('cooling','Reduce your AC footprint','building','cooling energy buildings',[plan('homes'),people('Find greener building advice')],{peopleIds:['org-119','org-108'],steps:['Ask a building professional about shade, ventilation and roof insulation for your site.', 'Review cooling needs, efficient equipment and maintenance before investing.']}),
    step('car-pooling','Find car-pooling options','mobility','car pooling transport',[ask('current car-pooling options'),link('Explore transport choices','https://goatourism.gov.in/within-goa/')],{description:'Ask about current local options and confirm travel arrangements directly.'}),
    step('female-taxi','Find female taxi drivers','mobility','female women taxi drivers',[link('Read the official women’s taxi listing (2019)','https://goatourism.gov.in/wp-content/uploads/2018/12/Goa-Tourist-Directory-2019.pdf'),ask('current female taxi drivers')],{description:'The Tourism Department’s 2019 directory lists a women-driver service. Current operation and booking availability need confirmation.',steps:['Ask the tourism team or ActForGoa for a current women-driver service.', 'Confirm the driver, pickup, fare and availability before making travel plans.']}),
    {...old('planning','professionals'),label:'Find eco-building materials and professionals'},
    step('disability-access','Disability access support','access','disability access',[link('Choose disability support','/topics/health/disability','access'),people('Find access advice')],{peopleIds:['org-5']}),greenViksit(),initiative('innovation-lab','Wise Progress Hub and Innovation Lab'),
    {id:'report',label:'Report a building or transport problem',icon:'report',query:'construction road access concern',concern:true,question:'What needs attention?',choices:[old('planning','construction'),...old('planning','roads').choices!]},
  ]);
  const health = revise('health','Health and air pollution','Cleaner air and a healthy environment support our wellbeing. Find ways to reduce pollution and connect with care.',[
    step('air','Reduce air pollution','nature','air pollution burning waste',[read('Understand the dangers of burning waste','resource-5eb125389b'),link('Find alternatives to burning waste','/topics/waste/segregation')],{resourceIds:['resource-5eb125389b'],steps:['Keep waste out of fires and arrange suitable segregation, composting and collection.', 'Share the waste-burning infographic with your household or community.']}),
    {...old('health','health'),label:'Find health support and services',choices:[...old('health','health').choices!,...old('health','mental-health').choices!.map(a=>({...a,id:'mental-'+a.id,label:a.id==='support'?'Mental health support':'A mental health clinic'}))]},
    step('information','Find information about health in Goa','book','health climate air pollution',[read('The health impacts of burning waste','resource-5eb125389b'),read('Climate change and human health in Goa','resource-047548946f'),plan('health')],{resourceIds:['resource-5eb125389b','resource-047548946f']}),
    old('health','disability'),old('health','care'),
  ]);
  const culture = revise('culture','Culture and heritage','Celebrate the stories, places and traditions that make Goa home, and help pass them on with care.',[
    old('culture','learn'),
    step('respect','How to respect local culture','heritage','respect local culture',[read('Learn about heritage and tourism','resource-495fef2505'),people('Connect with local cultural groups')],{peopleIds:['org-10','org-174'],resourceIds:['resource-495fef2505'],steps:['Ask local hosts about customs, dress and access before visiting a community or sacred place.', 'Ask permission before taking or sharing photographs and stories. Credit the people whose knowledge you share.']}),
    step('celebrate','Celebrate Goan heritage','map','celebrate heritage story',[link('Pin a place and share its story','/heritage/share','map'),link('Explore community stories','/stories?topic=Culture%20%26%20heritage')],{description:'Share a place, tradition or cultural asset and the story that makes it matter.'}),
    {...old('culture','protect'),label:'Protect a heritage site',choices:[old('culture','protect').choices![1],old('culture','protect').choices![0]]},
  ]);
  const carbon = fresh('carbon','Carbon reduction and net zero','nature','Make everyday choices that use less energy and fewer materials, and understand Goa’s path towards lower emissions.',['Planning & mobility','Waste & recycling'],[
    step('everyday','Simple steps for everyday life','nature','carbon reduction energy',[link('Create less waste','/topics/waste/reduce'),link('Reduce cooling energy','/topics/planning/cooling'),plan('energy')],{steps:['Choose one practical change in how you travel, cool your home, buy or use materials.', 'Track what you use, review progress and bring neighbours or colleagues into the effort.']}),
    step('energy','Explore cleaner energy','building','solar energy efficiency',[people('Find energy specialists'),plan('energy')],{peopleIds:['org-91','org-129']}),
    step('understand','Understand Goa’s climate commitments','book','net zero climate',[plan(),read('Explore climate change in Goa','wp-5213')],{resourceIds:['wp-5213']}),
  ]);
  const flooding = fresh('flooding','Flooding and fires','water','Prepare together for climate risks, keep local routes clear and know where to find official help.',['Water & environment','Community & rights'],[
    step('prepare','Prepare your household and neighbourhood','community','flood fire preparedness',[plan('water'),link('Find official emergency helpline numbers','/emergency','health')],{steps:['Discuss local flood and fire risks and evacuation arrangements with your Panchayat or municipality.', 'Agree how neighbours will share official warnings and support people who need help moving safely.']}),
    step('waterways','Care for drains and waterways','water','drain flood water',[link('Protect a river, lake or wetland','/topics/water/protect'),link('Organise or join a clean-up','/topics/waste/clean-up')]),
    step('urgent','Get help in an emergency','health','emergency flood fire',[link('Emergency helpline numbers','/emergency','health'),plan('water')],{concern:true}),
  ]);
  const business = fresh('business','Green business','building','Build a business that uses resources carefully, supports local livelihoods and contributes to Goa’s future.',['Waste & recycling','Planning & mobility'],[
    step('basics','Being a responsible business: the basics','building','responsible green business',[link('Plan waste segregation','/topics/waste/segregation'),link('Reduce water pollution','/topics/water/reduce-pollution'),link('Explore resource efficiency','/topics/waste/circular-strategy')],{steps:['Review your water, energy, purchasing, packaging and waste arrangements with your team.', 'Choose achievable improvements, work with local suppliers and communicate progress honestly.']}),
    step('find','Find a green business','community','green business services',[people('Explore resource-saving services'),ask('local green businesses')],{peopleIds:['org-50','org-54','org-129','org-178'],description:'Explore source-listed businesses and ask about their practices and current services directly.'}),
    initiative('join','Contribute to collaborative action'),
  ]);
  const laws = fresh('laws','Green laws, rights and responsibilities','file','Understand the responsibilities that help protect Goa’s environment, and take part in decisions that affect your community.',['Community & rights','Water & environment'],[
    step('understand','Understand environmental responsibilities','book','environmental law permissions',[read('Explore environmental protection guidance','guide-environmental-protection'),read('Check building responsibilities','guide-building')],{resourceIds:['guide-environmental-protection','guide-building']}),
    old('community','records'),
    step('participate','Participate in local decisions','community','gram sabha public participation',[link('Know your Panchayat','/topics/community/panchayat'),read('Understand the Gram Sabha','resource-1460f83efc')],{resourceIds:['resource-1460f83efc']}),
    {...old('community','report'),concern:true},
  ]);
  const education = fresh('education','Green education and courses','book','Learn with local educators and community groups, then put that knowledge into action.',['Nature & wildlife','Community & rights'],[
    step('courses','Find green courses and workshops','book','environment education courses',[people('Explore environmental educators'),ask('current green courses and workshops')],{peopleIds:['org-184','org-206','org-142'],steps:['Ask the provider about current courses, dates, language, accessibility and fees.', 'Check what the course covers and whether it includes practical local work.']}),
    step('community','Bring learning into your community','community','environment education school',[people('Find learning partners'),ask('a community environmental workshop')],{peopleIds:['org-184','org-206']}),
    step('climate','Learn about Goa’s climate action plan','nature','climate education',[plan(),read('Explore Goa’s climate workshop archive','wp-8817')],{resourceIds:['wp-8817']}),
  ]);
  return [waste,water,nature,village,tourism,food,planning,health,culture,carbon,flooding,business,laws,education].map(flow => ({
    ...flow,
    legacyActions: [...flow.legacyActions ?? [], step('schemes','Government schemes','file',flow.label+' schemes',[
      link('Browse official Goa government schemes','https://www.goa.gov.in/government/schemes/','file'),plan('funding'),ask(flow.label+' schemes'),
    ],{description:'Check current eligibility, application windows and required approvals with the responsible department. The climate plan describes proposals, not a guarantee of funding.'})],
  }));
}
