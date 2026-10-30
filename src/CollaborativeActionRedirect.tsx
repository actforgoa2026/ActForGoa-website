import { useEffect } from 'react';
import { ArrowUpRight } from 'lucide-react';
import { ButtonLink } from './components/arc/button/button-link';

export default function CollaborativeActionRedirect() {
  useEffect(() => { window.location.replace('https://actforgoa.lovable.app/'); }, []);
  return <main className="shell topic-page"><h1>Collaborative Action</h1><p>Opening the ActForGoa collective’s website.</p><ButtonLink href="https://actforgoa.lovable.app/">Continue to Collaborative Action <ArrowUpRight size={18}/></ButtonLink></main>;
}
