import test from 'node:test';
import assert from 'node:assert/strict';
import {governmentContacts, governmentContact, contactPhoneHref} from '../src/government-contacts';

test('contact pages keep official provenance and explicit availability limitations', () => {
 for (const contact of Object.values(governmentContacts)) {
  assert(contact.sources.length);
  assert(contact.sources.every(source => new URL(source.href).hostname.endsWith('goa.gov.in')));
  assert.match(contact.reviewNote, /not been tested/);
  assert.match(contact.office.email, /^[^@]+@[^@]+$/);
  assert(contact.calls.every(call => /^tel:\+91\d{10}$/.test(contactPhoneHref(call.phone))));
 }
 assert.match(governmentContacts.veterinary.callNote, /not confirmed 24-hour/);
 assert.equal(contactPhoneHref('0832-2465443'), 'tel:+918322465443');
 assert.equal(contactPhoneHref('9607948546'), 'tel:+919607948546');
});

test('unknown contact routes cannot read inherited object properties', () => {
 assert.equal(governmentContact('toString'), undefined);
 assert.equal(governmentContact('missing-department'), undefined);
 assert.equal(governmentContact('forest')?.title, 'Forest Department contacts');
});
