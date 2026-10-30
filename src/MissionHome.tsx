import { useState, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ArrowUpRight, ChevronDown, Siren } from 'lucide-react';
import { topicFlows } from './topic-flows';
import { useLanguage } from './language';
import { translatePriority } from './priority-translations';
import { Button } from './components/arc/button/button';
import { ButtonLink } from './components/arc/button/button-link';
import { TopicIcon } from './components/TopicIcon';
import HomeCarousel from './HomeCarousel';
import './mission.css';

const topicGroups = [
  { title: 'Climate', description: 'Care for Goa’s ecosystems, resources and climate.', slugs: ['nature', 'water', 'waste', 'food', 'carbon', 'flooding'], climatePlan: true },
  { title: 'Civic', description: 'Shape healthier communities and take part in local decisions.', slugs: ['community', 'planning', 'health', 'laws', 'business'] },
  { title: 'Culture', description: 'Celebrate Goan heritage, learn and welcome people responsibly.', slugs: ['culture', 'tourism', 'education'] },
];

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
  return <main className="mission-home" lang="en">
    <HomeCarousel>
      <h1 id="home-heading"><span className="mission-heading-lead">Helping people to</span> <span>Care for Goa</span></h1>
      <p className="mission-opener"><span>contribute to climate and cultural resilience</span><span>become more responsible residents and guests</span><span>Safeguard a green future for Goa</span></p>
    </HomeCarousel>
    <section className="mission-intro shell" aria-label="Find your next action" lang="en">
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
      <div className="mission-topic-groups">
      {topicGroups.map(group => <section className="mission-topic-group" key={group.title} aria-labelledby={'category-'+group.title.toLowerCase()}>
        <h3 id={'category-'+group.title.toLowerCase()}>{group.title}</h3>
        <p>{group.description}</p>
        <nav aria-label={group.title+' topics'} className="mission-topic-list">
        {group.slugs.map(slug => topicFlows.find(flow => flow.slug === slug)!).map(flow => <ButtonLink wrap variant="secondary" key={flow.slug} to={'/topics/'+flow.slug}>
          <TopicIcon name={flow.icon} />
          <span lang={translatePriority(flow.label, language) === flow.label ? 'en' : language}>{translatePriority(flow.label, language)}</span>
          <ArrowRight size={19} aria-hidden="true" />
        </ButtonLink>)}
        {group.climatePlan && <ButtonLink wrap variant="secondary" to="/climate-plan"><TopicIcon name="nature"/><span>Explore Goa’s Climate Action Plan</span><ArrowRight size={19} aria-hidden="true" /></ButtonLink>}
        </nav>
      </section>)}
      </div>
      <Link className="mission-emergency text-link" to="/emergency"><Siren size={18} aria-hidden="true" />Emergency helpline numbers <ArrowRight size={18} aria-hidden="true" /></Link>
    </section>
    <section className="mission-explore shell" aria-labelledby="explore-heading">
      <div className="mission-explore-heading"><div><h2 id="explore-heading">Explore the field guide</h2><p>Local knowledge, practical help and people making a difference.</p></div><ButtonLink to="/explore" variant="ghost" wrap>Browse everything <ArrowRight size={18} aria-hidden="true" /></ButtonLink></div>
      <div className="mission-collections">
        <section><h3>Guides & resources</h3><p>Find practical steps for everyday questions, from managing waste and growing food to understanding Goa’s environment and your rights.</p><ButtonLink to="/library" variant="secondary" wrap>Find a guide <ArrowRight size={18} aria-hidden="true" /></ButtonLink></section>
        <section><h3>People & services</h3><p>Look up community organisations, local initiatives and public offices. Find who works on the issues you care about and how to get in touch.</p><ButtonLink to="/directory" variant="secondary" wrap>Explore the directory <ArrowRight size={18} aria-hidden="true" /></ButtonLink></section>
        <section><h3>Stories</h3><p>Meet the people caring for Goa and explore the places, traditions and ideas they share. Find inspiration for what you could do in your own community.</p><ButtonLink to="/stories" variant="secondary" wrap>Read local stories <ArrowRight size={18} aria-hidden="true" /></ButtonLink></section>
        <section><h3>Collaborative Action</h3><p>Discover the team’s platform for connecting people and shared initiatives. Explore opportunities to contribute your time, skills or ideas.</p><ButtonLink href="https://actforgoa.lovable.app/" variant="secondary" wrap>Explore Collaborative Action <ArrowUpRight size={18} aria-hidden="true" /></ButtonLink></section>
      </div>
      <InstagramFeed />
    </section>
  </main>;
}
