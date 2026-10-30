import {installExternalLinks} from './external-links';
import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import {BrowserRouter, Navigate, Route, Routes, useLocation} from 'react-router-dom';
import '@fontsource-variable/figtree';
import './components/arc/foundation.css';
import './styles.css';
import './satellite-standalone.css';
import {SiteHeader} from './components/arc/site-header/site-header';
import Satellite from './SatelliteWorkspace';

function App(){const location=useLocation();return <><SiteHeader variant="simple" brand={{name:'actforgoa.',href:'/map'}} items={[{value:'map',label:'Satellite map',href:'/map'}]} current={location.pathname==='/map'?'map':''} secondaryAction={null} primaryAction={null}/><Routes><Route path="/map" element={<Satellite/>}/><Route path="*" element={<Navigate to="/map" replace/>}/></Routes><footer className="satellite-standalone-footer shell"><p>ActForGoa satellite workspace · Experimental selected-area investigations.</p></footer></>;}
createRoot(document.getElementById('root')!).render(<StrictMode><BrowserRouter><App/></BrowserRouter></StrictMode>);

const stopExternalLinks = installExternalLinks(document.getElementById('root')!);
if (import.meta.hot) import.meta.hot.dispose(stopExternalLinks);
