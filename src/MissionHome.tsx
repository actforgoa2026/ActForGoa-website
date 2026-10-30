import { useState, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ArrowUpRight, ChevronDown, Siren } from 'lucide-react';
import { topicFlows } from './topic-flows';
import { useLanguage } from './language';
import { translatePriority } from './priority-translations';
import { Button } from './components/arc/button/button';
import { ButtonLink } from './components/arc/button/button-link';
import { TopicIcon } from './components/TopicIcon';
import './mission.css';

export function InstagramFeed() {
  const [loaded, setLoaded] = useState(false);
  return <section className="instagram-feed" aria-label="Instagram updates">
    <Button variant="ghost" aria-expanded={loaded} aria-controls="instagram-updates" onClick={()=>setLoaded(!loaded)}>From ActForGoa on Instagram <ChevronDown size={18} aria-hidden="true" /></Button>
    {loaded && <div id="instagram-updates"><p>Updates from our community. Instagram may ask you to sign in.</p>
      <iframe title="ActForGoa Instagram profile" src="https://www.instagram.com/actforgoa/embed/" loading="lazy" referrerPolicy="strict-origin-when-cross-origin" />
      <ButtonLink wrap variant="ghost" href="https://www.instagram.com/actforgoa/">Visit @actforgoa on Instagram <ArrowUpRight size={18} aria-hidden="true" /></ButtonLink>
    </div>}
  </section>;
}

export default function MissionHome({ search }: { search: ReactNode }) {
  const { language } = useLanguage();
  return <main className="mission-home">
    <section className="mission-intro shell" aria-labelledby="home-heading" lang="en">
      <h1 id="home-heading"><span className="mission-heading-lead">Helping people to</span> <span>Care for Goa</span></h1>
      <p className="mission-opener"><span>contribute to climate and cultural resilience</span><span>become more responsible residents and guests</span><span>Safeguard a green future for Goa</span></p>
      {search}
      <ButtonLink className="mission-ai-link" wrap to="/ai">Use AI to explore our vetted library of surveys and guides <ArrowRight size={18} aria-hidden="true" /></ButtonLink>
      <nav className="mission-shortcuts" aria-label="Start here">
        <ButtonLink wrap variant="secondary" to="/climate-plan">Goa’s Climate Action Plan <ArrowRight size={18} aria-hidden="true" /></ButtonLink>
        <ButtonLink wrap variant="secondary" to="/topics/waste/segregation">How do I segregate my waste? <ArrowRight size={18} aria-hidden="true" /></ButtonLink>
        <ButtonLink wrap variant="secondary" to="/topics/community/panchayat">Understand my village Panchayat <ArrowRight size={18} aria-hidden="true" /></ButtonLink>
      </nav>
    </section>
    <section className="mission-topics shell" aria-labelledby="home-actions-heading">
      <h2 id="home-actions-heading" tabIndex={-1}>What do you care about?</h2>
      <nav aria-label="Choose a topic" className="mission-topic-list">
        {topicFlows.map(flow => <ButtonLink wrap variant="secondary" key={flow.slug} to={'/topics/'+flow.slug}>
          <TopicIcon name={flow.icon} />
          <span lang={translatePriority(flow.label, language) === flow.label ? 'en' : language}>{translatePriority(flow.label, language)}</span>
          <ArrowRight size={19} aria-hidden="true" />
        </ButtonLink>)}
        <ButtonLink wrap variant="secondary" to="/climate-plan"><TopicIcon name="nature"/><span>Explore Goa’s Climate Action Plan</span><ArrowRight size={19} aria-hidden="true" /></ButtonLink>
      </nav>
      <Link className="mission-emergency text-link" to="/emergency"><Siren size={18} aria-hidden="true" />Emergency helpline numbers <ArrowRight size={18} aria-hidden="true" /></Link>
    </section>
    <section className="mission-explore shell" aria-labelledby="explore-heading">
      <h2 id="explore-heading">Explore the field guide</h2>
      <nav className="mission-collections" aria-label="Explore the collection">
        <ButtonLink to="/explore" variant="ghost" wrap>Everything <ArrowRight size={18} aria-hidden="true" /></ButtonLink>
        <ButtonLink to="/library" variant="ghost" wrap>Guides & resources <ArrowRight size={18} aria-hidden="true" /></ButtonLink>
        <ButtonLink to="/directory" variant="ghost" wrap>People & services <ArrowRight size={18} aria-hidden="true" /></ButtonLink>
        <ButtonLink to="/stories" variant="ghost" wrap>Stories <ArrowRight size={18} aria-hidden="true" /></ButtonLink>
        <ButtonLink href="https://actforgoa.lovable.app/" variant="ghost" wrap>Collaborative Action <ArrowUpRight size={18} aria-hidden="true" /></ButtonLink>
      </nav>
      <InstagramFeed />
    </section>
  </main>;
}
