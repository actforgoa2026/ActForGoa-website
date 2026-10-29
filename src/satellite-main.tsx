import {installExternalLinks} from './external-links';
import {StrictMode, useEffect, useState, type FormEvent} from 'react';
import {createRoot} from 'react-dom/client';
import {BrowserRouter, Link, Navigate, Route, Routes, useLocation, useNavigate} from 'react-router-dom';
import '@fontsource-variable/figtree';
import './components/arc/foundation.css';
import './styles.css';
import './satellite-standalone.css';
import {SiteHeader} from './components/arc/site-header/site-header';
import {Button} from './components/arc/button/button';
import {Input} from './components/arc/input/input';
import {adminApi, type AdminSession} from './admin-api';
import Satellite from './Satellite';

function Account(){
  const navigate=useNavigate();
  const [session,setSession]=useState<AdminSession|null>(null),[checking,setChecking]=useState(true);
  const [email,setEmail]=useState(''),[password,setPassword]=useState(''),[pending,setPending]=useState(false),[error,setError]=useState('');
  useEffect(()=>{const abort=new AbortController();adminApi<AdminSession>('/api/admin/session',{signal:abort.signal}).then(setSession).catch(()=>{}).finally(()=>{if(!abort.signal.aborted)setChecking(false);});return()=>abort.abort();},[]);
  async function signIn(event:FormEvent){event.preventDefault();setPending(true);setError('');try{await adminApi<AdminSession>('/api/admin/login',{method:'POST',body:{email:email.trim(),password}});setPassword('');navigate('/map');}catch(e){setError(e instanceof Error?e.message:'Sign-in failed. Try again.');}finally{setPending(false);}}
  async function signOut(){if(!session)return;setPending(true);setError('');try{await adminApi('/api/admin/logout',{method:'POST',csrfToken:session.csrfToken});setSession(null);}catch(e){setError(e instanceof Error?e.message:'Sign-out failed. Try again.');}finally{setPending(false);}}
  return <main className="satellite-account shell"><h1>{session?'Your satellite workspace':'Sign in to investigate'}</h1>
    {checking?<p role="status">Checking your sign-in…</p>:session?<><p>Signed in as {session.user.name}. Saved investigations belong to your account.</p><p><Link to="/map">Open the satellite map</Link></p><Button variant="secondary" loading={pending} onClick={signOut}>Sign out</Button></>:<><p>Use your satellite workspace account to retrieve imagery and reopen your saved comparisons.</p><form onSubmit={signIn}><Input label="Email address" type="email" autoComplete="username" required maxLength={254} value={email} onChange={e=>setEmail(e.target.value)}/><Input label="Password" type="password" autoComplete="current-password" required maxLength={256} value={password} onChange={e=>setPassword(e.target.value)}/><Button type="submit" loading={pending}>Sign in</Button></form></>}
    {error&&<p role="alert" className="satellite-error">{error}</p>}
  </main>;
}
function App(){const location=useLocation();return <><SiteHeader variant="simple" brand={{name:'actforgoa.',href:'/map'}} items={[{value:'map',label:'Satellite map',href:'/map'}]} current={location.pathname==='/map'?'map':''} secondaryAction={{label:'Account',href:'/admin'}} primaryAction={null}/><Routes><Route path="/map" element={<Satellite/>}/><Route path="/admin" element={<Account/>}/><Route path="*" element={<Navigate to="/map" replace/>}/></Routes><footer className="satellite-standalone-footer shell"><p>ActForGoa satellite workspace · Experimental selected-area investigations.</p></footer></>;}
createRoot(document.getElementById('root')!).render(<StrictMode><BrowserRouter><App/></BrowserRouter></StrictMode>);

const stopExternalLinks = installExternalLinks(document.getElementById('root')!);
if (import.meta.hot) import.meta.hot.dispose(stopExternalLinks);
