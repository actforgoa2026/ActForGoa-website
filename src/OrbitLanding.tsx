import {useEffect, useRef, useState, type CSSProperties, type FormEvent} from 'react';
import {Link, useNavigate} from 'react-router-dom';
import {ArrowUp, ArrowUpRight, Pause, Play, Search} from 'lucide-react';
import photos from './content/orbit-photos.json';
import './orbit-landing.css';

const rings = [
  {radius: 355, count: 9, duration: 90, start: 12},
  {radius: 535, count: 13, duration: 150, start: 2},
  {radius: 725, count: 17, duration: 240, start: 8},
];
const headlineExamples = ['find local help.', 'protect nature.', 'know your rights.', 'take local action.', 'care for Goa.'];
const suggestions = ['How can I protect a wetland?', 'Understand my village panchayat', 'Explore Goa’s ecosystems'];
export default function OrbitLanding(){
  const scene = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const animations = Array.from(scene.current?.querySelectorAll('.goa-photo-ring') || [])
      .flatMap((ring, index) => {
        // Integral of (1 - progress)^2 over three seconds is one second:
        // duration × revolutions adds 3 / 2.5 / 2 full entrance turns.
        const revolutions = 3 - index * .5;
        return [ring, ...ring.querySelectorAll('.goa-photo-counter')].flatMap(element =>
          element.getAnimations().map(animation => ({animation,
            boost: Number(animation.effect?.getTiming().duration) / 1000 * revolutions})));
      });
    let previous = performance.now();
    let elapsed = 0;
    let frame = 0;
    const settle = (now: number) => {
      if (!scene.current?.closest('.is-paused')) elapsed += now - previous;
      previous = now;
      const progress = Math.min(1, elapsed / 3000);
      // Match ring/counter time exactly, keeping photographs upright throughout.
      animations.forEach(({animation, boost}) => {
        animation.currentTime = elapsed + boost * 1000 * (1 - (1 - progress) ** 3);
      });
      if (progress < 1) frame = requestAnimationFrame(settle);
    };
    settle(previous);
    return () => { cancelAnimationFrame(frame); animations.forEach(({animation}) => { animation.playbackRate = 1; }); };
  }, []);
  const [question,setQuestion]=useState('');
  const [paused,setPaused]=useState(false);
  const navigate=useNavigate();
  function ask(event:FormEvent){event.preventDefault();if(question.trim())navigate('/ask',{state:{draftQuestion:question.trim()}});}
  return <main className={'goa-orbit-page'+(paused?' is-paused':'')}>
    <div ref={scene} className="goa-orbit-scene" aria-hidden="true">
      {rings.map((ring,ri)=><div key={ri} className={'goa-photo-ring goa-photo-ring-'+ri} style={{'--radius':ring.radius+'px','--duration':ring.duration+'s'} as CSSProperties}>
        {Array.from({length:ring.count},(_,i)=>{const photo=photos[(i*5+ri*3)%photos.length];const angle=360/ring.count*i+ring.start;return <div className="goa-photo-position" key={i} style={{'--angle':angle+'deg','--tilt':'0deg','--photo-size':([70,94,124][ri] + (i%3-1)*8)+'px'} as CSSProperties}><div className="goa-photo-counter"><img src={photo.src} alt="" draggable={false} width="120" height="120" loading="eager"/></div></div>;})}
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
      <form className="goa-orbit-composer" onSubmit={ask} role="search" aria-label="Start a conversation about Goa">
        <Search size={23} aria-hidden="true"/>
        <input aria-label="What would you like to know about Goa?" placeholder="What would you like to know about Goa?" value={question} onChange={e=>setQuestion(e.target.value)} maxLength={2000}/>
        <button type="submit" disabled={!question.trim()} aria-label="Continue to chat"><ArrowUp size={23}/></button>
      </form>
      <div className="goa-orbit-suggestions" aria-label="Suggested questions">{suggestions.map((text,i)=><button key={text} onClick={()=>navigate(i===2?'/ask/ecology':'/ask',{state:{draftQuestion:text}})}>{text}<ArrowUpRight size={13}/></button>)}</div>
      <Link className="goa-orbit-chat-link" to="/ask">Or start a conversation <ArrowUpRight size={15}/></Link>
    </section>
    <footer className="goa-orbit-footer"><span>Rooted in Goa. Made for all of us.</span><button onClick={()=>setPaused(!paused)} aria-pressed={paused} aria-label={paused?'Resume motion':'Pause motion'}>{paused?<Play size={13}/>:<Pause size={13}/>}<span>{paused?'Resume motion':'Pause motion'}</span></button><Link to="/about">About ActForGoa <ArrowUpRight size={13}/></Link></footer>
  </main>;
}
