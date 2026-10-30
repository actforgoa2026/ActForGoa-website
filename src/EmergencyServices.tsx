import { Link } from "react-router-dom";
import { ButtonLink } from "./components/arc/button/button-link";
import { Ambulance, ArrowLeft, ArrowUpRight, Baby, Flame, HeartHandshake, Phone, Shield, Siren, Users, Zap } from "lucide-react";
import "./emergency-services.css";
import { useLanguage } from "./language";
import { translatePriority } from "./priority-translations";

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
  const { language } = useLanguage();
  const t = (text: string) => translatePriority(text, language);
  return (
    <main className="emergency-page shell">
      <Link className="text-link" to="/"><ArrowLeft size={17} aria-hidden="true" /> <span lang={language}>{t("Back")}</span></Link>
      <h1 lang={language}>{t("Emergency helpline numbers")}</h1>
      <p className="emergency-intro"><span lang={language}>{t("Goa helplines. Tap a number to call.")}</span></p>
      <ButtonLink wrap className="emergency-number" href="tel:112" aria-label="Call all emergencies on 112">
        <Siren size={24} aria-hidden="true" />
        <span lang={language}>{t("All emergencies")}</span>
        <strong>112</strong>
        <Phone size={20} aria-hidden="true" />
      </ButtonLink>
      <ul className="emergency-services" aria-label="Emergency phone numbers">
        {services.map(({ name, number, icon: Icon }) => (
          <li key={name}>
            <ButtonLink wrap variant="secondary" className="emergency-number" href={`tel:${number}`} aria-label={`Call ${name.toLowerCase()} on ${number}`}>
              <Icon size={23} aria-hidden="true" />
              <span lang={language}>{t(name)}</span>
              <strong>{number}</strong>
              <Phone size={18} aria-hidden="true" />
            </ButtonLink>
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
