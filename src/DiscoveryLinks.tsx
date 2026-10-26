import { ArrowRight, FileText, Leaf, Recycle, Waves, Users, Sprout, Landmark, Route, Heart } from "lucide-react";
import { Link } from "react-router-dom";
import { TOPICS, type RecordItem } from "./types";
import { templatePath } from "./template-path";
import { topicHref } from "./topic-flows";

const topicDescriptions = [
  "Waste collection, segregation and reuse",
  "Wildlife, animal welfare and local habitats",
  "Rivers, coasts and environmental protection",
  "Village decisions, public records and your rights",
  "Growing food, soil and farming support",
  "Goan places, traditions and creative life",
  "Buildings, public spaces and getting around",
  "Care, support and community wellbeing",
];
const topicIcons = [Recycle, Leaf, Waves, Users, Sprout, Landmark, Route, Heart];

export function DiscoveryTopics({ records, second = false }: { records: RecordItem[]; second?: boolean }) {
  const start = second ? 4 : 0;
  return (
    <section className="discovery-section discovery-topics" aria-labelledby={`discovery-topics-${start}`}>
      <div className="discovery-section-heading">
        <div>
          <h2 id={`discovery-topics-${start}`}>{second ? "More of Goa to explore" : "Explore by what matters to you"}</h2>
          <p>Follow a topic to its guides, people and stories.</p>
        </div>
      </div>
      <div className="discovery-topic-grid">
        {TOPICS.slice(start, start + 4).map((topic, index) => {
          const Icon = topicIcons[start + index];
          const count = records.filter(record => record.topics.includes(topic)).length;
          return (
            <Link key={topic} to={topicHref(topic)} className="discovery-topic-link">
              <Icon size={24} aria-hidden="true" />
              <span><strong>{topic}</strong><span>{topicDescriptions[start + index]}</span><small>{count} entries to explore</small></span>
              <ArrowRight size={18} aria-hidden="true" />
            </Link>
          );
        })}
      </div>
    </section>
  );
}

const linkGroups = {
  tools: {
    title: "Templates & useful tools",
    description: "Start with a draft, fill in your details and keep a copy.",
    links: [
      { title: "Write a complaint", description: "Open the editable complaint letter.", href: templatePath("01-complaint.txt"), label: "Fill in a template" },
      { title: "Request public records", description: "Prepare an RTI records request.", href: templatePath("03-rti-records-request.txt"), label: "Fill in a template" },
      { title: "Keep a farm plan & log", description: "Organise your plans and farming notes.", href: templatePath("10-farm-plan-and-log.md"), label: "Open the worksheet" },
    ],
  },
  participate: {
    title: "Make a little time for Goa",
    description: "There are different ways to lend a hand.",
    links: [
      { title: "Volunteer with ActForGoa", description: "Read about taking part in the community.", href: "/read/wp-2249", label: "Explore volunteering" },
      { title: "Work with ActForGoa", description: "Get in touch about working together.", href: "/contact?reason=Work%20with%20ActForGoa", label: "Start a conversation" },
      { title: "Share a local resource", description: "Know a useful group, guide or community project?", href: "/contact", label: "Suggest something" },
    ],
  },
  checklists: {
    title: "From reading to doing",
    description: "A few more tools to help organise your next step.",
    links: [
      { title: "Record a local problem", description: "Gather the details in the incident form.", href: "/report", label: "Open the form" },
      { title: "Check a building project", description: "Work through the editable building checklist.", href: templatePath("07-building-checklist.md"), label: "Open the checklist" },
      { title: "Keep track of a case", description: "Put dates, correspondence and follow-ups in one log.", href: templatePath("05-case-log.md"), label: "Open the case log" },
    ],
  },
};

export function DiscoveryLinks({ group }: { group: keyof typeof linkGroups }) {
  const content = linkGroups[group];
  return (
    <section className={`discovery-section discovery-links discovery-links--${group}`} aria-labelledby={`discovery-${group}`}>
      <div className="discovery-section-heading">
        <div><h2 id={`discovery-${group}`}>{content.title}</h2><p>{content.description}</p></div>
        {group !== "participate" && <FileText size={28} aria-hidden="true" />}
      </div>
      <div className="discovery-link-grid">
        {content.links.map(link => (
          <Link key={link.href} to={link.href} className="discovery-action-link">
            <h3>{link.title}</h3>
            <p>{link.description}</p>
            <span>{link.label}<ArrowRight size={18} aria-hidden="true" /></span>
          </Link>
        ))}
      </div>
    </section>
  );
}
