import { useEffect, useLayoutEffect, useRef, useState, type ReactNode } from 'react';
import { ArrowUpRight, ArrowDown, ArrowRight, Search, BookOpen, FileText, ShieldCheck, Leaf, MapPin, Waves, Check, Plus, Minus, Menu, X, Pause, Play, Users, Route, ExternalLink, Sparkles, Asterisk } from 'lucide-react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';
import { Button } from './arc/button/button';
import { ButtonLink } from './arc/button/button-link';
import { Input } from './arc/input/input';
const asset = (name: string) => `${import.meta.env.BASE_URL}assets/${name}`;

gsap.registerPlugin(ScrollTrigger);
const BASE = 'https://actforgoa-field-guide.vercel.app';
const AI = `${BASE}/ai`;
const link = (path: string) => `${BASE}${path}`;
type MotifName = 'palm' | 'cow' | 'temple' | 'wave';
function Motif({ name, className = '' }: { name: MotifName; className?: string }) {
  return <span aria-hidden="true" className={`motif motif-${name} ${className}`} />;
}
function Action({ children = 'Ask ActForGoa AI', href = AI, light = false, className = '' }: { children?: ReactNode; href?: string; light?: boolean; className?: string }) {
  return <ButtonLink aria-label={className.includes('nav-ai') ? 'Ask ActForGoa AI' : undefined} className={`action ${light ? 'action-light' : ''} ${className}`} href={href} target={href.startsWith('https') ? '_blank' : undefined} rel="noreferrer"><span>{children}</span><ArrowUpRight size={19} aria-hidden="true" /></ButtonLink>;
}
const examples = [
  { id: 'wetlands', label: 'Protect a wetland', question: 'How can we protect a wetland near our village?', title: 'Start with the place. Follow the evidence.', body: 'Explore how the wetland is recorded, which protections may apply, and where to take your concern. Ask the agent to find the relevant records and explain their context.', sources: ['Wetlands & conservation', 'Water & environment resources'], next: '/topics/water', motif: 'wave' as MotifName },
  { id: 'waste', label: 'Sort out waste', question: 'What can a village panchayat do about waste?', title: 'A local question deserves local context.', body: 'Explore the panchayat’s responsibilities, community waste resources and practical ways to get started. Follow the original documents before deciding your next step.', sources: ['Waste & recycling guidance', 'Panchayat & community resources'], next: '/topics/waste', motif: 'cow' as MotifName },
  { id: 'khazans', label: 'Understand khazans', question: 'How do khazans manage fresh and salt water?', title: 'Get to know the landscape that sustains us.', body: 'Explore Goa’s khazan landscapes through the ecological library. Ask how water, agriculture and local stewardship fit together, then follow the research for a deeper look.', sources: ['Ecology & land-use research', 'Food & farming resources'], next: '/topics/food', motif: 'palm' as MotifName },
];
const resources = [
  { title: 'Guided action plans', text: 'Find your next step for waste, water, nature, rights and everyday life in Goa.', href: '/topics/waste', icon: Route, motif: 'cow' as MotifName, items: ['Choose what matters', 'Follow practical steps', 'Find the right resources'] },
  { title: 'People who can help', text: 'Find community organisations and public services, with source context close at hand.', href: '/directory', icon: Users, motif: 'temple' as MotifName, items: ['Community organisations', 'Government services', 'Source and availability notes'] },
  { title: 'A living source library', text: 'Go straight to the documents, handbooks and research behind the conversation.', href: '/research-library', icon: BookOpen, motif: 'palm' as MotifName, items: ['Legal & ecological research', 'Original documents', 'A deeper understanding of Goa'] },
];
const faqs = [
  ['What makes this AI different?', 'The agent works with ActForGoa’s community-gathered source library and public directory. It searches and reads that collection, then cites its sources. Open-web search is not enabled for this agent.'],
  ['Does vetted mean every answer is guaranteed?', 'No. Source curation gives the agent a grounded starting point, but an AI answer still needs checking. Documents can be historical, text extraction can have gaps, and an interpretation can be wrong. Read the cited originals and confirm current requirements or contact availability.'],
  ['Can I explore without using AI?', 'Yes. Browse the research library, practical guides, directory, topic journeys and stories directly. AI is one way into the community’s knowledge.'],
  ['How can I contribute?', 'ActForGoa welcomes local knowledge and participation. Use the Get involved or Contact links to share a useful resource, connect with the community, or find a way to help.'],
];

function ExampleAnswer({ compact = false }: { compact?: boolean }) {
  const [selected, setSelected] = useState(0);
  const item = examples[selected];
  return <div className={`answer-window ${compact ? 'answer-compact' : ''}`}>
    <div className="window-top"><a href={AI} target="_blank" rel="noreferrer" className="mini-brand">actforgoa<span>.</span></a></div>
    <div className="example-tabs" aria-label="Choose an example question">{examples.map((example, i) => <Button variant="ghost" key={example.id} onClick={() => setSelected(i)} aria-pressed={selected === i}>{example.label}</Button>)}</div>
    <div className="example-content" aria-live="polite">
      <div className="question-bubble"><Search size={18}/><span>{item.question}</span></div>
      <div className="answer-copy"><span className="answer-symbol"><BookOpen size={20}/></span><div><h3>{item.title}</h3><p>{item.body}</p><div className="source-links">{item.sources.map((source, i) => <a key={source} href={link(i === 0 ? '/research-library' : item.next)} target="_blank" rel="noreferrer"><FileText size={15}/>{source}<ArrowUpRight size={14}/></a>)}</div></div></div>
      <div className="answer-bottom"><span>Illustrative walkthrough · explore the real sources</span><a href={link(`/ask?q=${encodeURIComponent(item.question)}&start=ai`)} target="_blank" rel="noreferrer">Ask this question <ArrowUpRight size={16}/></a></div>
    </div>
  </div>;
}

export default function App() {
  const root = useRef<HTMLDivElement>(null);
  const [menu, setMenu] = useState(false);
  const [activeResource, setActiveResource] = useState(0);
  const [faq, setFaq] = useState<number | null>(0);
  const [question, setQuestion] = useState('');
  const [scrolled, setScrolled] = useState(false);
  const [systemReduced, setSystemReduced] = useState(() => window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  const [paused, setPaused] = useState(() => { try { return localStorage.getItem('actforgoa-demo-motion') === 'paused'; } catch { return false; } });
  const captureSection = new URLSearchParams(window.location.search).get('capture');
  const reduced = paused || systemReduced || !!captureSection;
  useEffect(() => { if (captureSection) { document.documentElement.dataset.capture = captureSection; return () => { delete document.documentElement.dataset.capture; }; } }, [captureSection]);
  const menuButton = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    const change = () => setSystemReduced(mq.matches);
    mq.addEventListener('change', change);
    const scroll = () => setScrolled(window.scrollY > 180);
    window.addEventListener('scroll', scroll, { passive: true });
    const escape = (e: KeyboardEvent) => { if (e.key === 'Escape') { setMenu(false); menuButton.current?.focus({ preventScroll: true }); } };
    window.addEventListener('keydown', escape);
    return () => { mq.removeEventListener('change', change); window.removeEventListener('scroll', scroll); window.removeEventListener('keydown', escape); };
  }, []);
  useLayoutEffect(() => {
    if (reduced) return;
    const lenis = new Lenis({ lerp: .085, smoothWheel: true, anchors: { offset: -110 } });
    lenis.on('scroll', ScrollTrigger.update);
    const tick = (time: number) => lenis.raf(time * 1000);
    gsap.ticker.add(tick);
    const ctx = gsap.context(() => {
      gsap.from('.hero-title .line-inner', { yPercent: 105, duration: 1.2, stagger: .13, ease: 'power4.out' });
      gsap.from('.hero-detail', { y: 20, opacity: 0, duration: 1, delay: .35, stagger: .1, ease: 'power3.out' });
      gsap.from('.hero-creature', { y: -30, rotation: -5, duration: 1.6, ease: 'power3.out' });
      gsap.to('.hero-creature', { y: 105, rotation: 8, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: 1 } });
      gsap.to('.place-track', { xPercent: -18, ease: 'none', scrollTrigger: { trigger: '.place-strip', start: 'top bottom', end: 'bottom top', scrub: 1 } });
      const mm = gsap.matchMedia();
      mm.add('(min-width: 900px)', () => {
        const tl = gsap.timeline({ scrollTrigger: { trigger: '.knowledge', start: 'top top', end: '+=200%', pin: '.knowledge-stage', scrub: .8, invalidateOnRefresh: true } });
        tl.to('.knowledge-word', { color: '#193e32', stagger: .17, duration: .3 }, 0)
          .to({}, { duration: .6 })
          .to('.knowledge-statement', { y: -160, scale: .85, opacity: 0, duration: .8 }, 1.9)
          .fromTo('.source-fan', { y: 210, opacity: 0, scale: .8 }, { y: 0, opacity: 1, scale: 1, duration: .9 }, 2.1)
          .fromTo('.source-sheet', { rotation: 0 }, { rotation: (i: number) => (i - 1) * 9, stagger: .06, duration: .7 }, 2.3)
          .to({}, { duration: .55 })
          .to('.source-fan', { y: -140, scale: .65, opacity: 0, duration: .7 }, 3.7)
          .fromTo('.knowledge-answer', { y: 200, scale: .88, autoAlpha: 0 }, { y: 0, scale: 1, autoAlpha: 1, duration: .8 }, 4)
          .to({}, { duration: 1.3 });
        const track = document.querySelector<HTMLElement>('.journey-track')!;
        gsap.to(track, { x: () => -(track.scrollWidth - window.innerWidth), ease: 'none', scrollTrigger: { trigger: '.journey', start: 'top top', end: '+=180%', pin: true, scrub: 1, invalidateOnRefresh: true } });
      });
      gsap.utils.toArray<HTMLElement>('.reveal-heading').forEach(el => {
        gsap.from(el, { y: 45, opacity: .15, duration: .85, ease: 'power3.out', scrollTrigger: { trigger: el, start: 'top 90%', once: true } });
      });
      gsap.from('.truth-wave', { x: 120, rotation: -12, duration: 1.5, ease: 'power3.out', scrollTrigger: { trigger: '.truth', start: 'top 70%', once: true } });
      gsap.from('.live-screen', { scale: .88, rotation: -3, scrollTrigger: { trigger: '.live-showcase', start: 'top bottom', end: 'center center', scrub: 1 } });
      gsap.to('.closing-landscape', { yPercent: -8, ease: 'none', scrollTrigger: { trigger: '.closing', start: 'top bottom', end: 'bottom bottom', scrub: 1 } });
    }, root);
    document.fonts.ready.then(() => ScrollTrigger.refresh());
    const refresh = () => ScrollTrigger.refresh();
    window.addEventListener('load', refresh);
    return () => { window.removeEventListener('load', refresh); ctx.revert(); lenis.destroy(); gsap.ticker.remove(tick); };
  }, [reduced]);
  const toggleMotion = () => setPaused(value => { try { localStorage.setItem('actforgoa-demo-motion', !value ? 'paused' : 'playing'); } catch { /* Storage is optional. */ } return !value; });
  const resource = resources[activeResource];
  return <div ref={root} className={`site ${reduced ? 'motion-reduced' : ''}`}>
    <a className="skip-link" href="#main">Skip to content</a>
    <header className={`site-header ${scrolled ? 'is-scrolled' : ''}`}>
      <div className="nav-main"><a className="brand" href="#top" aria-label="ActForGoa home">actforgoa<span className="brand-dot">.</span></a>
        <nav className="desktop-nav" aria-label="Main navigation"><a href="#intelligence">The intelligence</a><a href="#in-action">See it in action</a><a href="#resources">The resources</a></nav>
        <Button variant="ghost" ref={menuButton} className="menu-toggle" aria-label={menu ? 'Close navigation' : 'Open navigation'} aria-expanded={menu} aria-controls="nav-menu" onClick={() => setMenu(!menu)}>{menu ? <X size={22}/> : <Menu size={22}/>}</Button>
      </div>
      <div className="nav-action"><a href={link('/explore')} target="_blank" rel="noreferrer" className="explore-nav">Explore ActForGoa</a><Action className="nav-ai"><span className="nav-ai-full">Ask ActForGoa AI</span><span className="nav-ai-short" aria-hidden="true">Ask AI</span></Action></div>
      {menu && <nav id="nav-menu" className="menu-panel" aria-label="Expanded navigation"><a onClick={() => setMenu(false)} href="#intelligence">The intelligence <ArrowRight/></a><a onClick={() => setMenu(false)} href="#in-action">See it in action <ArrowRight/></a><a onClick={() => setMenu(false)} href="#resources">The resources <ArrowRight/></a><a href={AI} target="_blank" rel="noreferrer" onClick={() => setMenu(false)}>Ask ActForGoa AI <ArrowUpRight/></a></nav>}
    </header>
    <main id="main">
      <section id="top" className="hero">
        <div className="hero-art" aria-hidden="true"><Motif name="cow" className="hero-creature"/><Motif name="palm" className="hero-palm"/><Motif name="temple" className="hero-temple"/></div>
        <div className="hero-copy"><h1 className="hero-title" aria-label="Answers for Goa. Backed by sources."><span className="line"><span className="line-inner">Answers for Goa.</span></span><span className="line"><span className="line-inner">Backed by sources.</span></span></h1>
          <p className="hero-detail">Ask AI about Goa’s laws, land and local issues.<br/> Get cited answers, find organisations, and follow practical action guides.</p>
          <div className="hero-actions hero-detail"><Action/><a className="text-action" href="#in-action">See how it works <ArrowDown size={17}/></a></div>
        </div>
        <img className="hero-landscape" src={asset('goa-panorama.webp')} width="2172" height="724" alt="" fetchPriority="high"/>
        <div className="hero-foot"><a href="#intelligence" aria-label="Scroll to how the AI works"><ArrowDown size={21}/></a></div>
      </section>
      <div className="place-strip" aria-label="Rooted in communities across Goa"><div className="place-track">Panaji <Asterisk aria-hidden="true"/> Mapusa <Asterisk aria-hidden="true"/> Margao <Asterisk aria-hidden="true"/> Ponda <Asterisk aria-hidden="true"/> Canacona <Asterisk aria-hidden="true"/> Bicholim <Asterisk aria-hidden="true"/> Pernem <Asterisk aria-hidden="true"/> Sanguem</div></div>
      <section id="ai-preview" className="live-showcase section-pad"><div className="live-copy"><h2 className="reveal-heading">Ask about Goa’s<br/>laws, land and life.</h2><p>Ask a question. The AI searches ActForGoa’s curated library, explains what it finds, and links you to the original documents. Follow up when you need more detail.</p><Action>Open the AI homepage</Action></div><a className="live-screen" href={AI} target="_blank" rel="noreferrer" aria-label="Open the live ActForGoa AI homepage"><div className="screen-bar"><span/><span/><span/><p>actforgoa · Explore with AI</p><ExternalLink size={15}/></div><img src={asset('ai-homepage.webp')} alt="The live ActForGoa AI homepage with a question composer and links to its source library" loading="lazy" width="1280" height="720"/></a></section>
      <section id="in-action" className="demo-section section-pad"><div className="section-intro"><h2 className="reveal-heading">See a question become<br/>a practical next step.</h2><div><p>Try example questions about wetlands,<br/>village waste and Goa’s khazan landscapes.</p><a className="text-action" href={AI} target="_blank" rel="noreferrer">Try the AI homepage <ArrowUpRight size={18}/></a></div></div><div className="demo-layout"><div className="demo-art"><Motif name="palm"/></div><ExampleAnswer/></div></section>
      <section id="map-analysis" className="map-showcase section-pad"><div className="section-intro"><h2 className="reveal-heading">See how Goa<br/>is changing.</h2><div className="map-description"><p>Compare satellite images of a place across two dates. Use AI-assisted image analysis to investigate changes in tree cover, wetlands and land use, with measurements and dated imagery to check.</p><Action href={link('/map')} light>Explore the map</Action><p className="map-caveat">Experimental analysis. Clouds and image resolution can limit what is visible. Review the images and confirm findings on the ground.</p></div></div><a className="map-screen" href={link('/map')} target="_blank" rel="noreferrer" aria-label="Open ActForGoa’s satellite map and image analysis"><img src={asset('map-homepage.webp')} width="1440" height="1000" alt="ActForGoa’s live map showing Sentinel-2 imagery of Goa, date controls and tools for analysing changes in tree cover" loading="lazy"/></a></section>
      <section id="resources" className="resources section-pad"><div className="section-intro"><h2 className="reveal-heading">Find a guide.<br/>Find someone to help.</h2><p>Browse practical action plans, local organisations<br/>and the documents behind the answers.</p></div><div className="resource-layout"><div className="resource-accordion">{resources.map((item,i)=><div className={`resource-row ${i === activeResource ? 'active' : ''}`} key={item.title}><h3><Button variant="ghost" onClick={()=>setActiveResource(i)} aria-expanded={i===activeResource} aria-controls={`resource-${i}`}><item.icon size={24}/><span>{item.title}</span>{i===activeResource?<Minus size={22}/>:<Plus size={22}/>}</Button></h3>{i===activeResource&&<div id={`resource-${i}`} className="resource-description"><p>{item.text}</p><a className="text-action" href={link(item.href)} target="_blank" rel="noreferrer">Explore {i===0?'the guides':i===1?'the directory':'the library'} <ArrowUpRight size={18}/></a></div>}</div>)}</div><div className={`resource-preview resource-preview-${activeResource}`}><Motif key={resource.motif} name={resource.motif}/><div><h3>{resource.title}</h3>{resource.items.map(item=><p key={item}><Check size={17}/>{item}</p>)}</div></div></div></section>
      <section id="source-promise" className="truth" aria-labelledby="truth-title"><div className="truth-content"><h2 id="truth-title" className="reveal-heading">AI grounded in<br/>Goa’s knowledge.</h2><p className="truth-lead">Community-vetted documents.<br/>A dedicated research agent.</p><div className="truth-bottom"><p>The AI searches a vetted source library gathered by the community, rather than roaming the open web. It reads the documents and cites them in its answers, so you can check the evidence yourself.</p><div><span><Check size={19}/> Dedicated to the local library</span><span><Check size={19}/> Citations you can follow</span><span><Check size={19}/> No open-web search</span></div></div><a href={link('/research-library')} target="_blank" rel="noreferrer" className="text-action">Explore the source library <ArrowUpRight size={19}/></a></div><Motif name="wave" className="truth-wave"/></section>
      <section id="intelligence" className="knowledge" aria-labelledby="knowledge-title">
        <div className="knowledge-stage">
          <div className="knowledge-statement"><h2 id="knowledge-title"><span className="knowledge-word">A dedicated AI agent.</span> <span className="inline-motif"><Motif name="palm"/></span><br/><span className="knowledge-word">A community-vetted</span><br/><span className="knowledge-word">source library.</span> <span className="inline-book"><BookOpen size={53}/></span><br/><span className="knowledge-word">Answers you can check.</span></h2><p>The agent reads local documents and cites the sources it uses.</p></div>
          <div className="source-fan" aria-label="The knowledge behind the answer"><div className="source-fan-title"><h3>Good answers start<br/>with good sources.</h3><p>Gathered by the community. Read by the agent. Open to you.</p></div><div className="source-sheets">{[{ icon: FileText, title:'Know the rules.', label:'Goa’s laws & rights', text:'Legislation, policy and original legal documents.' }, { icon: Leaf, title:'Know the land.', label:'Ecology & research', text:'Habitats, water, biodiversity and the places we share.' }, { icon: Users, title:'Know your people.', label:'Community knowledge', text:'Practical guides, public services and local organisations.' }].map(source => <div className="source-sheet" key={source.title}><source.icon size={30}/><span>{source.label}</span><h4>{source.title}</h4><p>{source.text}</p><div className="document-lines"><span/><span/><span/></div><ShieldCheck size={25}/></div>)}</div></div>
          <div className="knowledge-answer"><h3>The knowledge comes together.</h3><ExampleAnswer compact/><a className="text-action" href={AI} target="_blank" rel="noreferrer">Start your own conversation <ArrowUpRight size={18}/></a></div>
        </div>
      </section>
      <section id="ask-check-act" className="journey" aria-label="From question to action" onFocusCapture={event => { const box = event.target.getBoundingClientRect(); if (box.left < 0 || box.right > window.innerWidth) { setPaused(true); requestAnimationFrame(() => event.target.scrollIntoView({ block: 'center' })); } }}><div className="journey-track">
        <article className="journey-panel journey-ask"><div className="journey-copy"><h2>Ask.</h2><p>Describe your question about<br/>Goa’s environment, local laws<br/>or community services.</p><a className="text-action" href={AI} target="_blank" rel="noreferrer">Bring your question <ArrowUpRight size={19}/></a></div><div className="journey-art"><Motif name="cow"/><div className="floating-question">How can our village do more?<Search size={22}/></div></div></article>
        <article className="journey-panel journey-check"><div className="journey-copy"><h2>Check.</h2><p>Read the cited documents.<br/>Check their dates and context.<br/>Understand what is uncertain.</p><a className="text-action" href={link('/research-library')} target="_blank" rel="noreferrer">Open the originals <ArrowUpRight size={19}/></a></div><div className="journey-art"><div className="big-document"><BookOpen size={42}/><h3>Goa’s knowledge,<br/>in the open.</h3><p>Original sources<br/>Context & dates<br/>Links to read more</p><div className="document-lines"><span/><span/><span/><span/></div><span>Read. Understand. Verify. <ArrowUpRight/></span></div></div></article>
        <article className="journey-panel journey-act"><div className="journey-copy"><h2>Act.</h2><p>Follow a practical guide.<br/>Find relevant organisations.<br/>Take informed local action.</p><a className="text-action" href={link('/topics/community')} target="_blank" rel="noreferrer">Find a way forward <ArrowUpRight size={19}/></a></div><div className="journey-art"><Motif name="temple"/><div className="floating-question"><Users size={22}/>Local knowledge. Collective action.</div></div></article>
      </div></section>
      <section id="more" className="more-goa section-pad"><h2 className="reveal-heading">Explore more<br/>of ActForGoa.</h2><div className="topic-links">{[{title:'Goa’s climate plan',desc:'Understand the proposals. Explore the evidence.',path:'/climate-plan',icon:Leaf},{title:'Stories from the community',desc:'Meet the people and ideas making a difference.',path:'/stories',icon:BookOpen},{title:'Local action & participation',desc:'Find a way to give back to the place you love.',path:'/get-involved',icon:Users},{title:'Bring the library to your AI',desc:'Connect compatible assistants through MCP.',path:'/mcp',icon:Sparkles}].map(item=><a key={item.path} href={link(item.path)} target="_blank" rel="noreferrer"><item.icon size={26}/><div><h3>{item.title}</h3><p>{item.desc}</p></div><ArrowUpRight size={25}/></a>)}</div></section>
      <section id="questions" className="faq section-pad"><h2>A few good questions.</h2><div>{faqs.map(([q,a],i)=><div className="faq-row" key={q}><h3><Button variant="ghost" onClick={()=>setFaq(faq===i?null:i)} aria-expanded={faq===i} aria-controls={`faq-${i}`}>{q}{faq===i?<Minus size={20}/>:<Plus size={20}/>}</Button></h3>{faq===i&&<p id={`faq-${i}`}>{a}</p>}</div>)}</div></section>
      <section id="start" className="closing"><div className="closing-copy"><h2>For the Goa<br/>we all call home.</h2><p>Ask about a local issue. Find the evidence and your next step.</p><form action={link('/ask')} method="get" target="_blank" className="closing-search"><Search size={22}/><Input label="Your question about Goa" id="question" name="q" placeholder="Ask a question about Goa…" value={question} onChange={e=>setQuestion(e.target.value)} required maxLength={2000}/><input name="start" type="hidden" value="ai"/><Button variant="ghost" aria-label="Ask your question in ActForGoa AI" disabled={!question.trim()}><ArrowUpRight size={24}/></Button></form><a className="text-action" href={AI} target="_blank" rel="noreferrer">Or explore the AI homepage <ArrowUpRight size={18}/></a></div><img className="closing-landscape" src={asset('goa-panorama.webp')} alt="Stippled illustration of Goa’s coastline, palms, grazing cows and village places of worship" loading="lazy" width="2172" height="724"/></section>
    </main>
    <footer><div className="footer-top"><p>Love Goa.<br/>Give back to Goa.</p><div><span>Explore</span><a href={AI} target="_blank" rel="noreferrer">Ask ActForGoa AI</a><a href={link('/research-library')} target="_blank" rel="noreferrer">Source library</a><a href={link('/directory')} target="_blank" rel="noreferrer">Directory</a></div><div><span>Take part</span><a href={link('/get-involved')} target="_blank" rel="noreferrer">Get involved</a><a href={link('/about')} target="_blank" rel="noreferrer">About ActForGoa</a><a href={link('/contact')} target="_blank" rel="noreferrer">Share something</a></div></div><a className="footer-wordmark" href="#top" aria-label="ActForGoa back to top">actforgoa<span>.</span></a><div className="footer-bottom"><span>ActForGoa · 2026</span><a href={`${import.meta.env.BASE_URL}credits.html`} target="_blank" rel="noreferrer">Artwork & demo notes <ArrowUpRight size={13}/></a></div></footer>
    <Button variant="ghost" className="motion-toggle" onClick={toggleMotion} aria-label={reduced ? 'Motion reduced. Toggle motion preference' : 'Pause scroll animations'} aria-pressed={reduced} title={systemReduced?'System reduced-motion preference is active':reduced?'Enable animations':'Reduce animations'}>{reduced?<Play size={14}/>:<Pause size={14}/>}<span>{reduced?'Motion reduced':'Pause motion'}</span></Button>
  </div>;
}
