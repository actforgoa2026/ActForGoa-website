import test from 'node:test';
import assert from 'node:assert/strict';
import {findLocalOffices, recipientForOffice, recipientHelp} from '../src/recipient-guide';
import {appendDictation} from '../src/dictation-text';

test('office finder matches the stated place without guessing a fallback jurisdiction', () => {
 assert.deepEqual(findLocalOffices(''), []);
 assert.deepEqual(findLocalOffices('not-a-goa-village-xyz'), []);
 const offices = findLocalOffices('Agonda');
 assert.equal(offices.length, 1);
 assert.equal(offices[0].name, 'Village Panchayat Agonda');
 assert.match(offices[0].source, /^https:\/\//);
 assert.equal(recipientForOffice(offices[0], '01-complaint'), 'The Secretary, Village Panchayat Agonda');
});

test('municipal and RTI recipients preserve the correct type of office and template designation', () => {
 const margao = findLocalOffices('Margao')[0];
 assert.equal(recipientForOffice(margao, '01-complaint'), 'The Chief Officer, Margao Municipal Council');
 assert.equal(recipientForOffice(margao, '03-rti-records-request'), 'Margao Municipal Council');
 assert.equal(recipientForOffice(margao, '04-rti-first-appeal'), 'Margao Municipal Council');
 assert.match(recipientHelp('04-rti-first-appeal').text, /not automatically the appellate authority/);
 assert.match(recipientHelp('16-environment-records-and-inspection').text, /not responsible for every environmental issue/);
});

test('dictation appends to typed text without merging words or exceeding the form limit', () => {
 assert.equal(appendDictation('I saw', ' plastic burning ', 3000), 'I saw plastic burning');
 assert.equal(appendDictation('I saw\n', 'plastic burning', 3000), 'I saw\nplastic burning');
 assert.equal(appendDictation('Keep this', '   ', 3000), 'Keep this');
 assert.equal(appendDictation('12345', '67890', 8), '12345 67');
});
