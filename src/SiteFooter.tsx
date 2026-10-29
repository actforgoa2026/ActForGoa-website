import {Link} from 'react-router-dom';
import './site-footer.css';

export default function SiteFooter() {
 return <footer className="site-footer">
  <div className="site-footer-landscape" aria-hidden="true">
   <img src="/assets/footer/goa-stippled-landscape.webp" alt="" width={2172} height={724} loading="lazy"/>
  </div>
  <div className="shell site-footer-content">
   <div className="site-footer-intro">
    <Link to="/" className="wordmark">act<span>for</span>goa.</Link>
    <p>A shared place for everyone who cares about Goa.</p>
    <a href="mailto:info@actforgoa.org">info@actforgoa.org</a>
   </div>
   <nav aria-label="Explore ActForGoa"><h2>Explore</h2><Link to="/#home-actions-heading">Take action</Link><Link to="/stories">Stories</Link><Link to="/library">Resources</Link><Link to="/directory">Directory</Link></nav>
   <nav aria-label="Stay connected"><h2>Stay connected</h2><Link to="/newsletters">Newsletters</Link><Link to="/get-involved">Get involved</Link><Link to="/contact">Contact us</Link><Link to="/about">About ActForGoa</Link></nav>
   <div className="site-footer-note"><p>Built from local knowledge and the work of people across Goa.</p><Link to="/contact">Share something with us</Link></div>
  </div>
  <div className="shell site-footer-bottom">
   <span>Kokum Trust is the legal managing entity for Act for Goa.</span>
   <nav aria-label="Site information"><a href="https://actforgoa.org/privacy-policy/" target="_blank" rel="noopener noreferrer">Privacy</a><a href="https://actforgoa.org/terms-and-conditions/" target="_blank" rel="noopener noreferrer">Terms</a><Link to="/about#sources">Sources</Link><Link to="/mcp">MCP</Link><Link to="/admin">Team dashboard</Link></nav>
  </div>
 </footer>;
}
