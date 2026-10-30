import test from 'node:test';
import assert from 'node:assert/strict';
import { homeSearchDestination } from '../src/home-search.ts';
import { searchDestination } from '../src/search-navigation.ts';
import { topicFlows, topicHref } from '../src/topic-flows.ts';

test('each homepage label and catalogue topic opens exactly the same page as its button', () => {
  for (const flow of topicFlows) {
    for (const query of [flow.label, flow.topic, `  ${flow.label.toUpperCase()}  `]) {
      assert.equal(homeSearchDestination(query), topicHref(flow.topic), query);
    }
  }
});

const journeys: Record<string, string[]> = {
  waste: [
    'Where can I take my rubbish?', "Our garbage hasn't been collected",
    'How do I compost at home?', 'Recycle old electronics and batteries',
    'Organise a beach clean-up', 'How do I dispose of food waste?',
    'Report illegal dumping near the river',
  ],
  water: [
    'My tap water is dirty', 'There is no water supply', 'Water is not coming from the tap',
    'Report sewage in the river', 'Rainwater harvesting', 'A leaking pipe in my road',
    'Noise pollution in our neighbourhood',
  ],
  community: [
    'I want to volunteer', 'How can I get involved?', 'Request official records',
    'I need legal aid', 'Follow up a complaint', 'Find a food bank', 'Child and family support',
  ],
  nature: [
    'Oh, there’s a snake in my front yard', 'Snake in my garden',
    'There is an injured dog on the road', 'A sick cow on my farm',
    'Someone is cutting down trees', 'Tree cutting for construction',
    'I want to volunteer for animal rescue', 'Find a veterinary clinic', 'How do I plant trees?',
  ],
  food: [
    'I want to grow vegetables', 'How do I get a Krishi Card?', 'Need soil advice for farming',
    'Snake plants for my garden', 'Crop damage after flooding',
  ],
  planning: [
    'Building permission for my house', 'Report illegal construction',
    'Help with bus routes', 'Fix a pothole in my road', 'Find an architect',
  ],
  health: [
    'Air pollution', 'Mental health support', 'Find a doctor', 'Help with disability rights',
    'Support for sight loss', 'Child development assessment',
  ],
  tourism: ['How can I be a responsible tourist?', 'Responsible hospitality'],
  carbon: ['Reduce my carbon footprint', 'Going net zero'],
  flooding: ['Flood preparedness', 'Fire prevention'],
  business: ['Find a green business'],
  laws: ['Environmental responsibilities', 'Green laws'],
  education: ['Green courses', 'Environmental education workshops'],
  culture: [
    'Explore Goan heritage', 'Arts workshops', 'Local stories',
    'Restore a heritage building', 'Music and cultural activities',
  ],
};

for (const [slug, queries] of Object.entries(journeys)) {
  test(`natural-language questions enter the ${slug} menu, without skipping to articles or submenus`, () => {
    for (const query of queries) assert.equal(homeSearchDestination(query), `/topics/${slug}`, query);
  });
}

test('emergency requests use the existing emergency button destination', () => {
  for (const query of ['Emergency services', 'I need an ambulance', 'snake bit me', 'bitten by a cobra', 'house on fire', '112']) {
    assert.equal(homeSearchDestination(query), '/emergency', query);
  }
});

test('unclear or competing needs ask the visitor to choose instead of returning articles', () => {
  for (const query of ['', '   ', 'hello', 'help me', 'Goa', 'zzzxqvplm', '🎉', 'कृपया मदद करें',
    'water and building permits', 'health and heritage', 'I do not want animal rescue', 'This is not about recycling']) {
    assert.equal(homeSearchDestination(query), null, query);
  }
});

test('punctuation, line breaks and repeated keywords do not change the chosen topic', () => {
  assert.equal(homeSearchDestination('WASTE!!!\nrecycling?'), '/topics/waste');
  assert.equal(homeSearchDestination('garbage '.repeat(500)), '/topics/waste');
  assert.equal(homeSearchDestination('arts '.repeat(500) + 'health'), null);
});

test('record search within catalogues keeps its query and selected filters', () => {
  assert.equal(searchDestination('/search', '?topic=Nature+%26+wildlife', 'snake in my garden'), '/search?topic=Nature+%26+wildlife&q=snake+in+my+garden');
  assert.equal(searchDestination('/library', '?type=resource', 'compost'), '/library?type=resource&q=compost');
});


test('homepage ecosystem suggestion enters the nature topic', () => {
  assert.equal(homeSearchDestination('Explore Goa’s ecosystems'), '/topics/nature');
});
