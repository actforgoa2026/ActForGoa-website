import {useEffect} from 'react';
import {Link, useParams} from 'react-router-dom';
import {ArrowLeft, Phone, Mail, MapPin} from 'lucide-react';
import {contactPhoneHref, governmentContact} from './government-contacts';
import './government-contacts.css';

export default function GovernmentContacts() {
 const {department = 'forest'} = useParams();
 const contact = governmentContact(department);
 useEffect(() => {if (contact) document.title = `${contact.title} | ActForGoa`;}, [contact]);
 if (!contact) return <main className="shell government-contacts"><h1>Contact page not found</h1><Link to="/directory">Find an office in the directory</Link></main>;
 return <main className="shell government-contacts">
  <Link className="back-link" to={contact.back.href}><ArrowLeft size={16}/>{contact.back.label}</Link>
  <header><h1>{contact.title}</h1><p>{contact.intro}</p>{department === 'veterinary' && <Link className="text-link" to="/contacts/forest">Forest Department contacts</Link>}</header>
  <section aria-labelledby="department-calls"><h2 id="department-calls">{contact.callHeading}</h2><p className="contact-note">{contact.callNote}</p>
   <div className="contact-helplines">{contact.calls.map(call => <a className="contact-call" href={contactPhoneHref(call.phone)} key={call.label}><Phone size={21}/><span><strong>{call.label}</strong><span>{call.phone}</span></span></a>)}</div>
  </section>
  <section aria-labelledby="department-office"><h2 id="department-office">{contact.office.label}</h2><dl className="contact-office"><div><dt><MapPin size={18}/>Address</dt><dd>{contact.office.address.map((line, index) => <span key={line}>{index > 0 && <br/>}{line}</span>)}</dd></div><div><dt><Phone size={18}/>Phone</dt><dd><a href={contactPhoneHref(contact.office.phone)}>{contact.office.phone}</a></dd></div><div><dt><Mail size={18}/>Email</dt><dd><a href={`mailto:${contact.office.email}`}>{contact.office.email}</a></dd></div></dl></section>
  <section className="contact-source" aria-labelledby="department-source"><h2 id="department-source">Official sources</h2><p>{contact.reviewNote}</p><div className="contact-source-links">{contact.sources.map(source => <a key={source.href} href={source.href} target="_blank" rel="noopener noreferrer">{source.label}</a>)}</div></section>
 </main>;
}
