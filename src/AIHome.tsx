import {useEffect} from 'react';
import {ArrowRight, BookOpen, Leaf, Scale, Globe, Map, MessagesSquare} from 'lucide-react';
import {Link} from 'react-router-dom';
import OrbitLanding from './OrbitLanding';
import {ButtonLink} from './components/arc/button/button-link';
import {TopicIcon} from './components/TopicIcon';
import {topicFlows, topicDescriptions, topicHref} from './topic-flows';
import './ai-home.css';

/** Reuse the main site's topic destinations and their existing submenus. */
export function AITopicPaths() {
 return <section className="ai-paths shell" aria-labelledby="home-actions-heading">
  <div className="ai-section-heading"><div><h2 id="home-actions-heading" tabIndex={-1}>What do you care about?</h2><p>Choose a topic. Find the tools and knowledge to take your next step.</p></div><Link to="/research-library">Browse the library <ArrowRight size={18}/></Link></div>
  <nav className="ai-topic-grid" aria-label="Choose a topic">{topicFlows.map(item=><ButtonLink wrap variant="secondary" key={item.slug} className="ai-topic-button" to={topicHref(item.topic)}><TopicIcon name={item.icon}/><span><strong>{item.label}</strong><small>{topicDescriptions[item.slug]}</small></span></ButtonLink>)}</nav>
 </section>;
}

export default function AIHome(){
 useEffect(()=>{document.title='Explore Goa with AI | ActForGoa';},[]);
 return <main className="ai-home"><OrbitLanding embedded ai/><AITopicPaths/><section className="ai-resources shell" aria-labelledby="ai-resources-title"><div className="ai-section-heading"><div><h2 id="ai-resources-title">Local knowledge. A clearer way forward.</h2><p>Go deeper into the evidence behind your answer.</p></div></div><div className="ai-resource-grid"><ButtonLink wrap variant="secondary" to="/ask/legal"><Scale/><strong>Know your rights</strong><span>Explore Goa’s laws, rules and legal resources.</span><ArrowRight/></ButtonLink><ButtonLink wrap variant="secondary" to="/ask/ecology"><Leaf/><strong>Understand the landscape</strong><span>Research ecosystems, habitats and environmental change.</span><ArrowRight/></ButtonLink><ButtonLink wrap variant="secondary" to="/research-library"><BookOpen/><strong>Read the originals</strong><span>Follow citations back to the documents and their context.</span><ArrowRight/></ButtonLink><ButtonLink wrap variant="secondary" to="/climate-plan"><Globe/><strong>Explore the climate plan</strong><span>Understand Goa’s climate proposals and ask questions about the plan.</span><ArrowRight/></ButtonLink><ButtonLink wrap variant="secondary" to="/map"><Map/><strong>See the landscape change</strong><span>Explore the existing satellite workspace and its analysis tools.</span><ArrowRight/></ButtonLink><ButtonLink wrap variant="secondary" to="/mcp"><MessagesSquare/><strong>Bring Goa into your AI tools</strong><span>Connect the research library to compatible AI assistants.</span><ArrowRight/></ButtonLink></div><p className="ai-provenance">Powered by Claude, grounded in the ActForGoa legal and ecological library. Answers include sources so you can check the evidence.</p></section></main>;
}
