import { useCallback, useRef, useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, ArrowRight, MapPin } from 'lucide-react';
import GooglePlaceMap from './GooglePlaceMap';
import { ButtonLink } from './components/arc/button/button-link';
import { Alert } from './components/arc/alert/alert';
import { ConfirmMorph } from './components/arc/confirm-morph/confirm-morph';
import { Button } from './components/arc/button/button';
import { Input } from './components/arc/input/input';
import { Textarea } from './components/arc/textarea/textarea';
import { emptyHeritageStory, heritageCoordinates, heritageDraftKey, heritageStoryEmail, readHeritageDraft, type HeritageStory as Story } from './heritage-story';
import './heritage-story.css';

export default function HeritageStory() {
  const [draft,setDraft]=useState<Story>(()=>{try{return readHeritageDraft(localStorage.getItem(heritageDraftKey));}catch{return {...emptyHeritageStory};}});
  const [message,setMessage]=useState(''),[email,setEmail]=useState(''),[mapOpen,setMapOpen]=useState(false),[permission,setPermission]=useState(false);
  const coordinates=heritageCoordinates(draft);
  const removedDraft=useRef<string|null>(null);
  const [hasSaved,setHasSaved]=useState(()=>{try{return !!localStorage.getItem(heritageDraftKey);}catch{return false;}});
  function update(key:keyof Story,value:string){setDraft(previous=>({...previous,[key]:value}));setEmail('');setMessage('');}
  const pin=useCallback((lat:number,lng:number)=>{
    if(!Number.isFinite(lat)||!Number.isFinite(lng)||lat<14.8||lat>15.9||lng<73.5||lng>74.5){setMessage('Choose a place within Goa, or describe the place in words.');return false;}
    setDraft(previous=>({...previous,latitude:lat.toFixed(6),longitude:lng.toFixed(6)}));setEmail('');setMessage('Place pinned. Your story is still a draft.');return true;
  },[]);
  function save(){try{localStorage.setItem(heritageDraftKey,JSON.stringify(draft));setHasSaved(true);setMessage('Draft saved in this browser. It has not been shared.');}catch{setMessage('This browser could not save the draft. Keep this page open or prepare the email to keep a copy.');}}
  function prepare(event:FormEvent<HTMLFormElement>){event.preventDefault();if((draft.latitude||draft.longitude)&&!coordinates){setMessage('Choose a place on the map again, or remove the pin to share without it.');return;}setEmail(heritageStoryEmail(draft));setMessage('Your story is ready to review in your email app. Nothing has been sent or published.');}
  return <main className="shell heritage-story">
    <Link className="text-link" to="/topics/culture/celebrate"><ArrowLeft size={18}/>Celebrate Goan heritage</Link>
    <h1>Pin a place. Share its story.</h1>
    <p>Celebrate a place, tradition or cultural asset that matters to you. Add its story and an optional map pin for the ActForGoa team to review.</p>
    <form onSubmit={prepare}>
      <Input label="Story title" name="title" value={draft.title} onChange={e=>update('title',e.target.value)} required maxLength={160}/>
      <Input label="Place, village or community" name="place" value={draft.place} onChange={e=>update('place',e.target.value)} required maxLength={200}/>
      <section className="heritage-location" aria-labelledby="heritage-location-heading">
        <h2 id="heritage-location-heading">Add a place on the map</h2>
        <p>Optional. Choose a public place and avoid sharing private homes or sensitive sites.</p>
        {mapOpen ? <GooglePlaceMap coordinates={coordinates} onPin={pin}/> : <Button type="button" variant="secondary" onClick={()=>setMapOpen(true)}>Choose a place on the map <MapPin size={18}/></Button>}
        {coordinates && <p className="heritage-pin" role="status"><MapPin size={18}/>Place pinned. You can move it on the map.</p>}
        {(draft.latitude||draft.longitude) && <Button type="button" variant="ghost" onClick={()=>{setDraft(previous=>({...previous,latitude:'',longitude:''}));setEmail('');setMessage('Map pin removed.');}}>Remove pin</Button>}
      </section>
      <Textarea label="Tell the story" name="story" value={draft.story} onChange={e=>update('story',e.target.value)} required rows={7} maxLength={4000} placeholder="What makes this special? Who shared this knowledge? How can people care for it?"/>
      <Textarea label="Sources, photo links and credits" name="credit" value={draft.credit} onChange={e=>update('credit',e.target.value)} rows={3} maxLength={1000} placeholder="Add public links and credit the people whose stories or photographs you are sharing."/>
      <div className="form-pair"><Input label="Your name" name="name" value={draft.name} onChange={e=>update('name',e.target.value)} required autoComplete="name" maxLength={100}/><Input label="Your email" type="email" name="email" value={draft.email} onChange={e=>update('email',e.target.value)} required autoComplete="email" maxLength={160}/></div>
      <label className="heritage-consent"><input type="checkbox" checked={permission} onChange={event=>{setPermission(event.target.checked);setEmail('');}} required/>I have permission to share this story and any linked material with ActForGoa for review.</label>
      <div className="heritage-actions"><Button type="submit">Prepare story email <ArrowRight size={18}/></Button><Button type="button" variant="secondary" onClick={save}>Save draft in this browser</Button></div>
      {hasSaved && <ConfirmMorph label="Remove saved draft" prompt="Remove the saved copy?" confirmLabel="Remove" doneLabel="Saved copy removed" onConfirm={()=>{removedDraft.current=localStorage.getItem(heritageDraftKey);localStorage.removeItem(heritageDraftKey);setMessage('Saved copy removed. The open form is still here.');}} onUndo={()=>{if(removedDraft.current)localStorage.setItem(heritageDraftKey,removedDraft.current);setMessage('Saved copy restored.');}}/>}
      <p>This prepares an email to ActForGoa. You review and send it yourself; it does not publish a public map pin.</p>
      {message && <Alert title={message}/>}
      {email && <ButtonLink variant="primary" wrap href={email}>Review in your email app <ArrowRight size={18}/></ButtonLink>}
    </form>
  </main>;
}
