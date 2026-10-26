import {Trash2, Leaf, Droplets, Users, Sprout, Landmark, Bus, Heart, Flag, Truck, Recycle, BookOpen, PawPrint, House, Accessibility, Stethoscope, MessageCircle, FileText, MapPin} from 'lucide-react';
import type {TopicIconName} from '../topic-flows';
const icons = {waste:Trash2,nature:Leaf,water:Droplets,community:Users,grow:Sprout,heritage:Landmark,mobility:Bus,health:Heart,report:Flag,truck:Truck,recycle:Recycle,book:BookOpen,animal:PawPrint,building:House,access:Accessibility,stethoscope:Stethoscope,message:MessageCircle,file:FileText,map:MapPin};
export function TopicIcon({name,className=''}:{name:TopicIconName;className?:string}) {
 const Icon=icons[name];
 return <Icon className={'topic-icon '+className} aria-hidden="true" strokeWidth={1.7}/>;
}
