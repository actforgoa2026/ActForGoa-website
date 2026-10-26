import { Link, useParams } from 'react-router-dom';
import { guideDocuments } from './guides';
import { PracticalGuide } from './PracticalGuide';

export default function GuideRoute() {
  const { id } = useParams();
  const guide = guideDocuments.find(item => item.id === id);
  return guide ? <PracticalGuide key={guide.id} guide={guide} />
    : <main className="empty-state shell"><h1>Guide not found</h1><Link to="/library">Browse the library</Link></main>;
}
