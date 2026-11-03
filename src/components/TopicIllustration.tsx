import type { TopicIconName } from '../topic-flows';
import { TopicIcon } from './TopicIcon';
import './topic-illustration.css';

const illustrations: Record<string, string> = {
  nature: 'nature', water: 'water', waste: 'waste', food: 'food',
  carbon: 'carbon', flooding: 'flooding', community: 'community', planning: 'planning',
  health: 'health', laws: 'laws', business: 'business', culture: 'culture',
  tourism: 'tourism', education: 'education', 'climate-plan': 'climate-plan',
};

/** Illustrations supplement the existing label; new categories retain their original icon. */
export function TopicIllustration({ category, fallback }: { category: string; fallback: TopicIconName }) {
  const illustration = illustrations[category];
  if (!illustration) return <TopicIcon name={fallback} />;
  return <img className="topic-illustration" src={`/assets/topics/${illustration}.webp`}
    width={192} height={192} alt="" aria-hidden="true" loading="lazy" decoding="async" draggable={false} />;
}
