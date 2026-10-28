import {useEffect, useRef, useState, type CSSProperties, type FormEvent} from 'react';
import {Link, useLocation, useNavigate} from 'react-router-dom';
import {ArrowUp, ArrowUpRight, Pause, Play, Search} from 'lucide-react';
import {createOrbitPath, orbitEntranceSpeed} from './orbit-motion';
import {searchDestination} from './search-navigation';
import photos from './content/orbit-photos.json';
import './orbit-landing.css';

const rings = [
  {radius: 355, count: 9, duration: 90, start: 12},
  {radius: 535, count: 13, duration: 150, start: 2},
  {radius: 725, count: 17, duration: 240, start: 8},
];
const headlineExamples = ['find local help.', 'protect nature.', 'know your rights.', 'take local action.', 'care for Goa.'];
const suggestions = ['How can I protect a wetland?', 'Understand my village panchayat', 'Explore Goa’s ecosystems'];
export default function OrbitLanding({embedded = false}: {embedded?: boolean}){
  const Container = embedded ? 'section' : 'main';
  const location = useLocation();
  const scene = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const root = scene.current;
    if (!root) return;
    const path = createOrbitPath();
    const tiles = Array.from(root.querySelectorAll<HTMLElement>('.goa-photo-position'));
    let previous = performance.now(), elapsed = 0, offset = 0, frame = 0, disposed = false;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    const draw = () => tiles.forEach((tile, index) => {
      const progress = (index / tiles.length + offset + .037) % 1;
      const point = path.point(progress);
      const depth = Math.min(Math.hypot(point.x, point.y) / path.radius, 1);
      const scale = .45 + .75 * depth ** .65;
      tile.style.transform = `translate3d(${point.x}px, ${point.y}px, 0) scale(${scale})`;
      tile.style.opacity = String(Math.min(progress / .035, (1 - progress) / .07, 1));
    });
    const flow = (now:number) => {
      const delta = Math.min(now - previous, 50);
      previous = now;
      if (!root.closest('.is-paused') && !document.hidden) {
        elapsed += delta;
        offset = (offset + 25 * orbitEntranceSpeed(elapsed) * delta / 1000 / path.length) % 1;
        draw();
      }
      frame = requestAnimationFrame(flow);
    };
    draw();
    root.style.opacity = '0';
    // Start the arrival clock when the photos can actually be seen.
    const images = Array.from(root.querySelectorAll('img'));
    void Promise.all(images.map(image => image.decode().catch(() => {}))).then(() => {
      if (disposed) return;
      root.style.opacity = '1';
      previous = performance.now();
      if (!reduced.matches) frame = requestAnimationFrame(flow);
    });
    return () => { disposed = true; cancelAnimationFrame(frame); };
  }, []);
  const [question,setQuestion]=useState('');
  const [paused,setPaused]=useState(false);
  const navigate=useNavigate();
  function search(value:string){if(value.trim())navigate(searchDestination(location.pathname, location.search, value));}
  function ask(event:FormEvent){event.preventDefault();search(question);}
  return <Container className={'goa-orbit-page'+(embedded?' goa-orbit-home-hero':'')+(paused?' is-paused':'')} aria-label={embedded?'Explore Goa':undefined}>
    <div ref={scene} className="goa-orbit-scene" aria-hidden="true">
      {rings.map((ring,ri)=><div key={ri} className={'goa-photo-ring goa-photo-ring-'+ri} style={{'--radius':ring.radius+'px','--duration':ring.duration+'s'} as CSSProperties}>
        {Array.from({length:ring.count},(_,i)=>{const photo=photos[rings.slice(0,ri).reduce((total, ring) => total + ring.count, 0) + i];const angle=360/ring.count*i+ring.start;return <div className="goa-photo-position" key={i} style={{'--angle':angle+'deg','--tilt':'0deg','--photo-size':'112px'} as CSSProperties}><div className="goa-photo-counter"><img src={photo.src} alt="" draggable={false} width="120" height="120" loading="eager"/></div></div>;})}
      </div>)}
    </div>
    <section className="goa-orbit-center" aria-labelledby="orbit-title">
      <h1 id="orbit-title" className="goa-rotating-headline" aria-label="A place to find local help, protect nature, know your rights and take local action in Goa.">
        <span className="goa-headline-fixed" aria-hidden="true">A place to</span>
        <span className="goa-headline-window" aria-hidden="true">{headlineExamples.map((text, index) =>
          <span key={text} className="goa-headline-phrase" style={{animationDelay: `${index * 4 - .6}s`}}>{text}</span>
        )}</span>
      </h1>
      <p className="goa-orbit-intro">Big questions. Local knowledge. A place to begin.</p>
      <form className="goa-orbit-composer" onSubmit={ask} role="search" aria-label="Search ActForGoa">
        <Search size={23} aria-hidden="true"/>
        <input id={embedded?"home-search":"explore-search"} aria-label="What would you like to know about Goa?" placeholder="What would you like to know about Goa?" value={question} onChange={e=>setQuestion(e.target.value)} maxLength={2000}/>
        <button type="submit" disabled={!question.trim()} aria-label="Search ActForGoa"><ArrowUp size={23}/></button>
      </form>
      <div className="goa-orbit-suggestions" aria-label="Suggested questions">{suggestions.map((text)=><button key={text} onClick={()=>search(text)}>{text}<ArrowUpRight size={13}/></button>)}</div>
      <Link className="goa-orbit-chat-link" to="/ask">Or start a conversation <ArrowUpRight size={15}/></Link>
    </section>
    <footer className="goa-orbit-footer"><span>Rooted in Goa. Made for all of us.</span><button onClick={()=>setPaused(!paused)} aria-pressed={paused} aria-label={paused?'Resume motion':'Pause motion'}>{paused?<Play size={13}/>:<Pause size={13}/>}<span>{paused?'Resume motion':'Pause motion'}</span></button>{embedded?<a href="#home-actions-heading">Find your next step <ArrowUpRight size={13}/></a>:<Link to="/about">About ActForGoa <ArrowUpRight size={13}/></Link>}</footer>
  </Container>;
}
