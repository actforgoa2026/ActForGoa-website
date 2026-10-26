import { Link } from "react-router-dom";
import { Ambulance, ArrowLeft, ArrowUpRight, Baby, Flame, HeartHandshake, Phone, Shield, Siren, Users, Zap } from "lucide-react";
import "./emergency-services.css";

const services = [
  { name: "Ambulance", number: "108", icon: Ambulance },
  { name: "Police", number: "112", icon: Shield },
  { name: "Fire & rescue", number: "112", icon: Flame },
  { name: "Women’s helpline", number: "1091", icon: HeartHandshake },
  { name: "Child helpline", number: "1098", icon: Baby },
  { name: "Senior citizens", number: "1090", icon: Users },
  { name: "Electricity helpline", number: "1912", icon: Zap },
];

export default function EmergencyServices() {
  return (
    <main className="emergency-page shell">
      <Link className="text-link" to="/"><ArrowLeft size={17} aria-hidden="true" /> Back</Link>
      <h1>Emergency services</h1>
      <p className="emergency-intro">Goa helplines. Tap a number to call.</p>
      <a className="emergency-number emergency-primary" href="tel:112" aria-label="Call all emergencies on 112">
        <Siren size={24} aria-hidden="true" />
        <span>All emergencies</span>
        <strong>112</strong>
        <Phone size={20} aria-hidden="true" />
      </a>
      <ul className="emergency-services" aria-label="Emergency phone numbers">
        {services.map(({ name, number, icon: Icon }) => (
          <li key={name}>
            <a className="emergency-number" href={`tel:${number}`} aria-label={`Call ${name.toLowerCase()} on ${number}`}>
              <Icon size={23} aria-hidden="true" />
              <span>{name}</span>
              <strong>{number}</strong>
              <Phone size={18} aria-hidden="true" />
            </a>
          </li>
        ))}
      </ul>
      <p className="emergency-sources">
        Sources: <a href="https://northgoa.gov.in/helpline/">North Goa helplines <ArrowUpRight size={13} aria-hidden="true" /></a>
        {" · "}<a href="https://goa-tourism.com/important-numbers/">Goa Tourism helplines <ArrowUpRight size={13} aria-hidden="true" /></a>
        {" · "}<a href="https://www.112.gov.in/about">112 India <ArrowUpRight size={13} aria-hidden="true" /></a>
        <span>Official listings checked 26 October 2026. Calls and service response have not been tested.</span>
      </p>
    </main>
  );
}
