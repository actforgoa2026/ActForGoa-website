import {useState} from 'react';
import {Link} from 'react-router-dom';
import {MapPin, Check} from 'lucide-react';
import {Button} from './components/arc/button/button';
import {Input} from './components/arc/input/input';
import {findLocalOffices, recipientForOffice, recipientHelp} from './recipient-guide';

export default function RecipientGuide({templateId, onChoose}: {templateId: string; onChoose: (value: string) => void}) {
 const [query, setQuery] = useState('');
 const [selected, setSelected] = useState('');
 const results = findLocalOffices(query);
 const help = recipientHelp(templateId);
 return <details className="recipient-guide">
  <summary>Help me choose the receiving office</summary>
  <div className="recipient-guide-content">
   <p>{help.text}</p>
   {help.link.startsWith('/') ? <Link to={help.link}>{help.label}</Link> : <a href={help.link} target="_blank" rel="noopener noreferrer">{help.label}</a>}
   <Input label="Find a local office by village or town" value={query} onChange={event => {setQuery(event.target.value); setSelected('');}} placeholder="For example, Agonda or Margao" description="Choose the office serving the site, which may differ from where you live." />
   {query.trim() && <div className="recipient-results" aria-live="polite">
    {results.length ? results.map(office => <div className="recipient-result" key={office.id}>
     <div><strong>{office.name}</strong><p>{office.location !== 'Goa' ? office.location : 'Goa'} · Directory checked {office.checkedOn}</p><a href={office.source} target="_blank" rel="noopener noreferrer">Published office listing</a></div>
     <Button type="button" size="sm" variant="secondary" onClick={() => {onChoose(recipientForOffice(office, templateId)); setSelected(office.id);}}>{selected === office.id ? <Check size={16}/> : <MapPin size={16}/>}<span>{selected === office.id ? 'Added to form' : 'Use this office'}</span></Button>
    </div>) : <p>No matching office in our current directory. This does not mean there is no office for your area.</p>}
   </div>}
   <p className="recipient-note">Our local-office coverage is incomplete. Confirm the office’s jurisdiction, designation and postal address before sending. You can edit the recipient above.</p>
   <div className="recipient-links"><a href="https://panchayatsgoa.gov.in/" target="_blank" rel="noopener noreferrer">All village panchayats</a><a href="https://goaulbservice.gov.in/munCouncil.aspx" target="_blank" rel="noopener noreferrer">Municipal councils</a><Link to={`/directory?collection=government&q=${encodeURIComponent(query)}`}>Search the directory</Link></div>
  </div>
 </details>;
}
