import {ButtonLink} from './components/arc/button/button-link';
import {MorphSelect} from './components/arc/morph-select/morph-select';
import SiteFooter from './SiteFooter';
import GoaLandscape from './GoaLandscape';
import { articlePhoto } from "./article-photos";
import {
  lazy,
  Suspense,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type FormEvent,
} from "react";
import {
  Link,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
  useSearchParams,
  useLoaderData,
  useNavigationType,
  ScrollRestoration,
  Navigate,
} from "react-router-dom";
import {
  ArrowRight,
  ArrowUp,
  Search,
  Leaf,
  Recycle,
  Waves,
  Users,
  Heart,
  Landmark,
  Sprout,
  Route as RouteIcon,
  BookOpen,
  Mail,
  MapPin,
  ExternalLink,
  ArrowLeft,
  Check,
  Copy,
  MessageSquare,
  X,
  FileText,
  SlidersHorizontal,
  Download,
  Siren,
} from "lucide-react";
import SiteHeader from "./components/arc/site-header/site-header";
import { LanguageSwitcher, useLanguage } from "./language";
import { translatePriority } from "./priority-translations";
import { RecordCard } from "./components/RecordCard";
import { TopicIcon } from "./components/TopicIcon";
import { TopicPage, TopicChoices } from "./TopicPage";
import { topicFlows, topicFor, topicHref } from "./topic-flows";
import "./topic-navigation.css";
import "./home-hero.css";
import { communityDescription } from "./public-record";
import { storyContent } from "./story-content";
import { directoryLinks, directoryTags } from "./directory";
import { DirectoryActions, DirectoryPhoto, DirectoryTags } from "./DirectoryInfo";
import { ListingLink } from "./ListingLink";
import type { RecordItem } from "./types";
import { TOPICS, kindLabel } from "./types";
import { hybridSearch } from "./search";
import { inferSearchIntent, focusSearchResults, groupIntentResults } from "./search-intent";
import { catalogueFilters, searchDestination, showEmergencyShortcut } from "./search-navigation";
import { homeSearchDestination } from "./home-search";
import EmergencyServices from "./EmergencyServices";
import { buildDiscoverySections } from "./discovery";
import "./discovery.css";
import { Research, ResearchDocument, ResearchMemoryProvider } from "./Research";
import { Button } from "./components/arc/button/button";
import { SearchField } from "./components/arc/search-field/search-field";
import { Input } from "./components/arc/input/input";
import { Textarea } from "./components/arc/textarea/textarea";
import SegmentedControl from "./components/arc/segmented-control/segmented-control";
import { browsingState, semanticCache, homeFeedState } from "./browsing-state";
import { useStarredIds } from './CurationProvider';
import { prioritizeStarred } from './curation';
import {CurationStar, TeamBrowsingBar} from './TeamAccess';
const AIHome = lazy(() => import("./AIHome"));
const OrbitLanding = lazy(() => import("./OrbitLanding"));
const CRM = lazy(() => import("./CRM"));
const McpPage = lazy(() => import("./McpPage"));
const GuideRoute = lazy(() => import("./GuideRoute"));
const ClimatePlan = lazy(() => import("./ClimatePlan"));
const TemplateEditor = lazy(() => import("./TemplateEditor"));
const ReportIncident = lazy(() => import("./ReportIncident"));
const ReportInbox = lazy(() => import("./ReportInbox"));
const Satellite = lazy(() => import('./Satellite'));
const AdminDashboard = lazy(() => import('./AdminDashboard'));
const Blog = lazy(() => import('./Blog'));
const Newsletters = lazy(() => import('./Newsletters'));
const ResearchLibrary = lazy(() => import('./ResearchLibrary'));
const GovernmentContacts = lazy(() => import('./GovernmentContacts'));

const topicIcons = [
  Recycle,
  Leaf,
  Waves,
  Users,
  Sprout,
  Landmark,
  RouteIcon,
  Heart,
];
const recordPath = (r: RecordItem) => "/read/" + r.id;
const formatDate = (s: string) => {
  const d = new Date(s);
  return Number.isNaN(d.getTime())
    ? s
    : d.toLocaleDateString("en-GB", {
        day: "numeric",
        month: "long",
        year: "numeric",
      });
};

function SearchBox({
  initial = "",
  large = false,
}: {
  initial?: string;
  large?: boolean;
}) {
  const [value, setValue] = useState(initial);
  const [needsTopic, setNeedsTopic] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  useEffect(() => setValue(initial), [initial]);
  function submit(e: FormEvent) {
    e.preventDefault();
    if (large && !value.trim()) return;
    const destination = large
      ? homeSearchDestination(value)
      : searchDestination(location.pathname, location.search, value);
    if (!destination) {
      setNeedsTopic(true);
      return;
    }
    navigate(destination, {
      preventScrollReset: location.pathname !== "/",
    });
  }
  if (large) return (
    <form className="ask-box" role="search" onSubmit={submit} aria-label="Ask ActForGoa">
      <Textarea
        id="home-search"
        label="What would you like help with in Goa?"
        placeholder="What would you like help with in Goa?"
        value={value}
        onChange={(event) => {
          setValue(event.target.value);
          setNeedsTopic(false);
        }}
        onKeyDown={(event) => {
          if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
            event.preventDefault();
            if (value.trim()) event.currentTarget.form?.requestSubmit();
          }
        }}
        rows={2}
        autoComplete="off"
        enterKeyHint="send"
        aria-describedby={needsTopic ? "ask-hint ask-topic-feedback" : "ask-hint"}
      />
      <div className="ask-toolbar">
        <span id="ask-hint">Find the right topic for your next step</span>
        <Button type="submit" size="sm" disabled={!value.trim()} aria-label="Ask ActForGoa">
          <ArrowUp size={21} aria-hidden="true" />
        </Button>
      </div>
      {needsTopic && <p id="ask-topic-feedback" className="ask-topic-feedback" role="status">
        I couldn’t find a clear topic. Try a little more detail, or <a href="#home-actions-heading">choose a topic below</a>.
      </p>}
    </form>
  );
  return (
    <form
      className={"search-box " + (large ? "large" : "")}
      role="search"
      onSubmit={submit}
    >
      <SearchField
        label="Search ActForGoa"
        id={large ? "home-search" : "guide-search"}
        value={value}
        onValueChange={setValue}
        placeholder={location.pathname === "/library" ? "Search articles and guides" : location.pathname === "/stories" ? "Search stories" : "Find local help"}
        autoComplete="off"
      />
      <Button type="submit" aria-label="Search the field guide">
        <span className="search-submit-label">Search</span>
      </Button>
    </form>
  );
}
const navigation = [
  { value: "home", label: "Home", href: "/" },
  { value: "action", label: "Take action", links: [
    { label: "Report an infraction", href: "/report", icon: <MapPin size={21} aria-hidden="true" /> },
    { label: "Emergency services", href: "/emergency", icon: <Siren size={21} aria-hidden="true" /> },
    { label: "Get involved", href: "/get-involved" },
    { label: "Green Viksit Goa", href: "/read/wp-9389" },
    { label: "Amche Mollem", href: "/read/wp-6263" },
    { label: "Work with us", href: "/contact?reason=Work%20with%20ActForGoa" },
    { label: "Volunteer", href: "/read/wp-2249" },
    { label: "Donations", href: "https://actforgoa.org/donation-form/" },
  ] },
  { value: "blog", label: "Blog", href: "/blog" },
  { value: "stories", label: "Inspiring stories", href: "/stories" },
  { value: "resources", label: "Resources", links: [{ label: "Legal questions", href: "/ask/legal" }, { label: "Environment & ecosystems", href: "/ask/ecology" }, { label: "Explore changes on the map", href: "/map" }, { label: "Reading library", href: "/library" }, { label: "Browse research library", href: "/research-library" }] },
  { value: "about", label: "About", links: [
    { label: "About ActForGoa", href: "/about" },
    { label: "Newsletters", href: "/newsletters" },
    { label: "Annual reports", href: "/read/wp-8903" },
    { label: "Press coverage", href: "/read/wp-7377" },
  ] },
  { value: "directory", label: "Directory", href: "/directory" },
];
function Header() {
  const { pathname } = useLocation();
  const { language } = useLanguage();
  const labels = language === "hi" ? ["मुखपृष्ठ", "कार्रवाई करें", "ब्लॉग", "प्रेरक कहानियाँ", "संसाधन", "हमारे बारे में", "निर्देशिका"] : language === "gom-Deva" ? ["मुखेल पान", "कृती करात", "ब्लॉग", "प्रेरणादायी कथा", "संसाधनां", "आमचे विशीं", "निर्देशिका"] : [];
  const items = navigation.map((item, index) => ({ ...item, label: labels[index] || item.label, lang: language }));
  const current = pathname === "/" ? "home" : (pathname.startsWith("/directory") || pathname.startsWith("/crm")) ? "directory" : (pathname === "/library" || pathname.startsWith("/ask") || pathname.startsWith("/documents/") || pathname === "/research-library" || pathname.startsWith("/climate-plan") || pathname === "/read/goa-sapcc") ? "resources" : ["/get-involved", "/emergency", "/report", "/reports/review"].includes(pathname) ? "action" : pathname.startsWith('/blog') ? 'blog' : pathname.slice(1);
  return <SiteHeader
    variant="mega" brand={{ name: "actforgoa.", href: "/", mark: <></> }}
    items={items} current={current} label="Main navigation" extraAction={<LanguageSwitcher />}
    secondaryAction={null} primaryAction={{ label: "Search", href: "/search" }}
    onNavigate={({href}) => { if (href === "/" && pathname === "/") window.scrollTo({top: 0, behavior: "instant"}); }}
  />;
}

function Home({ records }: { records: RecordItem[] }) {
  const { language } = useLanguage();
  return (
    <main>
      <OrbitLanding embedded />
      <GoaLandscape placement="horizon" />
      <section className="home-actions shell" aria-labelledby="home-actions-heading">
        <div className="section-heading">
          <h2 id="home-actions-heading" tabIndex={-1} lang={language}>{language === "hi" ? "आप किस विषय की परवाह करते हैं?" : language === "gom-Deva" ? "तुमकां खंयच्या विशयाची काळजी आसा?" : "What do you care about?"}</h2>
          <ButtonLink to="/emergency" className="emergency-entry">
            <Siren size={20} aria-hidden="true" />
            <span lang={language}>{translatePriority("Emergency services", language)}</span>
          </ButtonLink>
        </div>
        <nav className="home-topic-choices" aria-label="Choose a topic">
          {topicFlows.map(flow => (
            <ButtonLink wrap variant="secondary" key={flow.slug} className="home-topic-choice" to={topicHref(flow.topic)}>
              <TopicIcon name={flow.icon} />
              <span><strong lang={translatePriority(flow.label, language) === flow.label ? "en" : language}>{translatePriority(flow.label, language)}</strong></span>
            </ButtonLink>
          ))}
        </nav>
      </section>
      <DiscoveryFeed records={records} />
    </main>
  );
}

function DiscoveryFeed({ records }: { records: RecordItem[] }) {
  const starredIds = useStarredIds();
  const location = useLocation();
  const saved = homeFeedState.get(location.key);
  const [limit, setLimit] = useState(saved?.limit ?? 12);
  const [kind, setKind] = useState(saved?.kind ?? "all");
  const [automatic, setAutomatic] = useState(saved?.automatic ?? true);
  const marker = useRef<HTMLDivElement>(null);
  const feedRoot = useRef<HTMLDivElement>(null);
  const pendingFocus = useRef<number | null>(null);
  const [announcement, setAnnouncement] = useState("");
  const sections = useMemo(() => buildDiscoverySections(records, kind, starredIds), [records, kind, starredIds]);
  const entries = useMemo(() => sections.flatMap(section => section.records), [sections]);
  const shown = entries.slice(0, limit);
  const shownSections = sections.filter(section => section.start < limit).map(section => ({
    ...section, records: section.records.slice(0, limit - section.start),
  }));
  const hasMore = shown.length < entries.length;
  useLayoutEffect(() => {
    homeFeedState.set(location.key, { limit, kind, automatic });
    if (pendingFocus.current !== null) {
      feedRoot.current
        ?.querySelector<HTMLAnchorElement>(
          `[data-feed-index="${pendingFocus.current}"] h3 a`,
        )
        ?.focus({ preventScroll: true });
      pendingFocus.current = null;
    }
  }, [location.key, limit, kind, automatic]);
  useEffect(() => {
    if (
      !automatic ||
      !hasMore ||
      !marker.current ||
      typeof IntersectionObserver === "undefined"
    )
      return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting || document.visibilityState !== "visible")
          return;
        observer.disconnect();
        setLimit((current) => Math.min(current + 12, entries.length));
      },
      { rootMargin: "0px 0px 400px 0px" },
    );
    observer.observe(marker.current);
    return () => observer.disconnect();
  }, [automatic, hasMore, limit, entries.length, kind]);
  const changeKind = (value: string) => {
    setKind(value);
    setLimit(12);
    setAnnouncement("");
  };
  const loadMore = () => {
    pendingFocus.current = shown.length;
    setLimit((current) => Math.min(current + 12, entries.length));
    setAnnouncement(
      `${Math.min(12, entries.length - shown.length)} more entries added.`,
    );
  };
  return (
    <section className="discovery shell" aria-labelledby="discovery-heading">
      <div className="section-heading">
        <div>
          <h2 id="discovery-heading">Explore the field guide</h2>
        </div>
      </div>
      <div className="discovery-controls">
        <SegmentedControl
          label="Explore the collection"
          value={kind}
          onValueChange={changeKind}
          options={[
            { value: "all", label: "Everything" },
            { value: "resource", label: "Guides & resources" },
            { value: "organisation", label: "People & services" },
            { value: "story", label: "Stories" },
          ]}
        />
        <Button
          variant="ghost"
          className="auto-load-toggle"
          aria-pressed={automatic}
          onClick={() => setAutomatic(!automatic)}
        >
          {automatic ? "Pause auto-load" : "Resume auto-load"}
        </Button>
      </div>
      <div ref={feedRoot} className="discovery-feed">
        {shownSections.map(section => (
          <div key={section.id}>
            <section className={`discovery-section discovery-section--${section.type}`} aria-labelledby={`discovery-${section.id}`}>
              <div className="discovery-section-heading">
                <div>
                  <h2 id={`discovery-${section.id}`}>{section.title}</h2>
                </div>
                <Link className="text-link" to={section.href}>
                  {section.linkLabel} <ArrowRight size={18} aria-hidden="true" />
                </Link>
              </div>
              <div className={section.type === "people" ? "discovery-people-list" : "discovery-grid"}>
                {section.records.map((record, index) => (
                  <div data-feed-index={section.start + index} key={record.id}>
                    <RecordCard record={record} showImage={section.type !== "people"} />
                  </div>
                ))}
              </div>
            </section>
          </div>
        ))}
      </div>
      <div className="discovery-more" ref={marker}>
        <p className="sr-only" role="status">
          {announcement}
        </p>
        {hasMore ? (
          <>
            <Button variant="secondary" size="lg" onClick={loadMore}>
              Show more to explore <ArrowRight size={18} />
            </Button>
            <p>
              {shown.length} of {entries.length} entries ·{" "}
              {automatic ? "More loads as you scroll" : "Auto-load paused"}
            </p>
          </>
        ) : (
          <>
            <h3>You’ve explored the collection.</h3>
            <Link className="text-link" to="/contact">
              Know something we should add?
            </Link>
          </>
        )}
        <Link className="subtle-link" to="/get-involved">
          Take part in ActForGoa
        </Link>
      </div>
    </section>
  );
}

function Catalogue({
  records,
  mode = "search",
}: {
  records: RecordItem[];
  mode?: "search" | "directory" | "library" | "stories" | "blog";
}) {
  const starredIds = useStarredIds();
  const [params, setParams] = useSearchParams();
  const query = params.get("q") || "";
  const { topic, type: filter } = catalogueFilters(params.toString());
  const tag = params.get("tag") || "";
  const location = useLocation();
  const saved = browsingState.get(location.key);
  const [page, setPage] = useState({
    key: location.key,
    view:
      saved?.view ??
      (mode === "search" ? ("list" as const) : ("grid" as const)),
    limit: saved?.limit ?? 24,
  });
  if (page.key !== location.key) {
    setPage({
      key: location.key,
      view: saved?.view ?? page.view,
      limit: saved?.limit ?? (mode === "stories" || mode === "blog" || mode === "library" ? page.limit : 24),
    });
  }
  const { view, limit } = page;
  const resultsRoot = useRef<HTMLDivElement>(null);
  const filterScroll = useRef<number | null>(null);
  const nextResultFocus = useRef<string | null>(null);
  const [resultAnnouncement, setResultAnnouncement] = useState("");
  const setView = (view: "grid" | "list") =>
    setPage((current) => ({ ...current, view }));
  const setLimit = (limit: number) =>
    setPage((current) => ({ ...current, limit }));
  const [semantic, setSemantic] = useState<Map<string, number> | null>(
    () => semanticCache.get(query) ?? null,
  );
  const [status, setStatus] = useState<
    "idle" | "loading" | "ready" | "fallback"
  >(semantic ? "ready" : "idle");
  useLayoutEffect(() => {
    browsingState.set(location.key, { view, limit });
    if (filterScroll.current !== null) {
      window.scrollTo({top: filterScroll.current, behavior: "instant"});
      filterScroll.current = null;
    }
    if (nextResultFocus.current) {
      resultsRoot.current?.querySelector<HTMLAnchorElement>(`[data-record-id="${CSS.escape(nextResultFocus.current)}"] h3 a`)?.focus();
      nextResultFocus.current = null;
    }
  }, [location.key, view, limit]);
  const [semanticQuery, setSemanticQuery] = useState(query);
  if (semanticQuery !== query) {
    setSemanticQuery(query);
    setSemantic(semanticCache.get(query) ?? null);
  }
  const [meaningEnabled, setMeaningEnabled] = useState(false);
  const worker = useRef<Worker | null>(null);
  const seq = useRef(0);
  useEffect(() => () => worker.current?.terminate(), []);
  useEffect(() => {
    const id = ++seq.current;
    if (semanticCache.has(query)) {
      setStatus("ready");
      return;
    }
    if (!query.trim() || !meaningEnabled) {
      setStatus("idle");
      return;
    }
    setStatus("loading");
    const deadline = setTimeout(() => {
      if (id !== seq.current) return;
      worker.current?.terminate();
      worker.current = null;
      setStatus("fallback");
    }, 45000);
    const timer = setTimeout(() => {
      try {
        worker.current ||= new Worker(
          new URL("./semantic.worker.ts", import.meta.url),
          { type: "module" },
        );
        worker.current.onmessage = ({ data }) => {
          if (data.id !== seq.current) return;
          clearTimeout(deadline);
          if (data.error) {
            console.warn("Local search:", data.error);
            setStatus("fallback");
            return;
          }
          const scores = new Map<string, number>(data.scores);
          semanticCache.set(query, scores);
          setSemantic(scores);
          setStatus("ready");
        };
        worker.current.onerror = () => {
          clearTimeout(deadline);
          if (id === seq.current) setStatus("fallback");
        };
        worker.current.postMessage({ query, id });
      } catch {
        clearTimeout(deadline);
        setStatus("fallback");
      }
    }, 250);
    return () => { clearTimeout(timer); clearTimeout(deadline); };
  }, [query, meaningEnabled]);
  const base = useMemo(
    () =>
      records.filter((r) =>
        mode === "directory"
          ? r.kind === "organisation" || r.kind === "contact"
          : mode === "library"
            ? r.kind === "resource"
            : mode === "blog"
              ? r.kind === "story" && !r.source.includes("/portfolio/")
              : mode === "stories"
              ? r.kind === "story"
              : true,
      ),
    [records, mode],
  );
  const ranked = useMemo(
    () => {
      const ranked = hybridSearch(base, query, semantic);
      if (mode === "directory" && !query.trim()) ranked.sort((a, b) =>
        Number(b.record.kind === "organisation") - Number(a.record.kind === "organisation") ||
        Number(Boolean(b.record.directory?.photo)) - Number(Boolean(a.record.directory?.photo)) ||
        Number(b.record.text.trim().length > 80) - Number(a.record.text.trim().length > 80) ||
        a.record.title.localeCompare(b.record.title));
      return ranked;
    },
    [base, query, semantic, mode],
  );
  const relatedResults = ranked.filter(
    ({ record: r }) =>
      (!topic || r.topics.includes(topic)) &&
      (!tag || directoryTags(r).includes(tag)) &&
      (filter === "all" ||
        r.kind === filter ||
        (filter === "organisation" && r.kind === "contact")),
  );
  const intent = useMemo(() => inferSearchIntent(query), [query]);
  const focusedResults = useMemo(
    () => intent ? focusSearchResults(ranked, query, intent) : ranked,
    [ranked, query, intent],
  ).filter(({ record }) => (!topic || record.topics.includes(topic)) && (!tag || directoryTags(record).includes(tag)));
  const canFocus = mode === "search" && filter === "all" && intent !== null;
  const focused = canFocus && params.get("scope") !== "all" && focusedResults.length > 0;
  const results = prioritizeStarred(focused ? focusedResults : relatedResults, starredIds, item => item.record.id);
  const grouped = query.trim() && mode === "search" && filter === "all";
  const groups = focused ? groupIntentResults(results, query, intent) : [
    { title: "People & organisations", kinds: ["organisation", "contact"] },
    { title: "Guides & reading", kinds: ["resource"] },
    { title: "Stories & projects", kinds: ["story"] },
    { title: "About & action", kinds: ["page"] },
  ]
    .map((group) => ({
      ...group,
      items: results.filter(({ record }) => group.kinds.includes(record.kind)),
    }))
    .filter((group) => group.items.length)
    .sort((a, b) => results.indexOf(a.items[0]) - results.indexOf(b.items[0]));
  const perGroup = focused ? Math.max(3, Math.floor(limit / 8)) : Math.max(6, Math.floor(limit / 4));
  const moreAvailable = grouped
    ? groups.some((group) => group.items.length > perGroup)
    : limit < results.length;
  const title = mode === "directory" ? "Directory" : mode === "library" ? "Library" : mode === "blog" ? "Blog" : mode === "stories" ? "Stories" : "Search";
  const change = (key: string, value: string) => {
    filterScroll.current = window.scrollY;
    const next = new URLSearchParams(params);
    value ? next.set(key, value) : next.delete(key);
    setParams(next, { preventScrollReset: true });
  };
  return (
    <main className="catalogue shell">
      <div className="catalogue-heading catalogue-heading--landscape">
        <h1>{title}</h1>
        <GoaLandscape placement="heading" />

        {mode === "library" && <Link className="text-link" to="/climate-plan">Explore Goa’s climate action plan<ArrowRight size={18} aria-hidden="true" /></Link>}
      </div>
      <SearchBox initial={query} />
      {topic && !query && topicFor(topic) && (mode === "stories" || mode === "blog" ? <details className="topic-reading-help"><summary>Looking for practical help with this topic?</summary><TopicChoices flow={topicFor(topic)!} /></details> : <TopicChoices flow={topicFor(topic)!} />)}
      {showEmergencyShortcut(query) && <section className="search-emergency" aria-labelledby="emergency-search-heading">
        <h2 id="emergency-search-heading">Need urgent help?</h2>
        <p>For a police, fire or medical emergency, call <a href="tel:112">112</a>. Archived directory entries do not confirm live availability.</p>
        <Link className="text-link" to="/emergency">Open emergency services <ArrowRight size={18} /></Link>
      </section>}
      {query.trim() && <div className="meaning-search">
        {!meaningEnabled && !semantic ? <>
          <Button variant="ghost" onClick={() => setMeaningEnabled(true)}>Expand search by meaning</Button>
          <p>Optional download of about 50 MB, then runs on this device. Keyword search works without it.</p>
        </> : <p role="status">{status === "loading" ? "Loading optional meaning search. Keyword results are already available." : status === "fallback" ? "Meaning search could not load. Keyword results are still available." : semantic ? "Meaning search is ready on this device." : ""}</p>}
      </div>}
      <div className="catalogue-layout">
        <aside className="filter-rail">
          <h2>
            <SlidersHorizontal size={17} />
            Explore by topic
          </h2>
          <Button
            variant="ghost"
            aria-pressed={!topic}
            className={!topic ? "selected" : ""}
            onClick={() => change("topic", "")}
          >
            All topics <span>{base.length}</span>
          </Button>
          {TOPICS.map((t, i) => {
            const Icon = topicIcons[i];
            return (
              <Button
                variant="ghost"
                aria-pressed={topic === t}
                className={topic === t ? "selected" : ""}
                key={t}
                onClick={() => change("topic", t)}
              >
                <Icon size={17} />
                {t}
              </Button>
            );
          })}
          <p>
            Original resources and practical guides.
            <br />
            Every entry keeps its sources.
          </p>
        </aside>
        <div className="results-area" ref={resultsRoot}>
          {mode === "search" && (
            <SegmentedControl
              className="result-tabs"
              label="Result type"
              value={filter}
              options={[
                { value: "all", label: intent && params.get("scope") !== "all" && focusedResults.length > 0 ? "Best matches" : "Everything" },
                { value: "organisation", label: "People" },
                { value: "resource", label: "Guides" },
                { value: "story", label: "Stories" },
                { value: "page", label: "About" },
              ]}
              onValueChange={(value) =>
                change("type", value === "all" ? "" : value)
              }
            />
          )}
          <div className="results-bar">
            <div>
              <h2 aria-live="polite" className={focused ? "intent-heading" : undefined}>
                {focused ? intent.title : <>{results.length} {results.length === 1 ? "result" : "results"}{query && <> for “{query}”</>}</>}
              </h2>
              {query && (
                <p className="search-status" role="status">
                  {focused ? intent.description : canFocus && !focusedResults.length ? relatedResults.length ? "No focused matches yet. Showing related results." : "No matches within these filters. Try another topic or search." : status === "loading"
                    ? "Keyword results ready. Matching meaning on your device…"
                    : status === "ready"
                      ? "Matched by meaning and keywords."
                      : status === "fallback"
                        ? "Keyword search is available. Meaning search could not load."
                        : ""}
                </p>
              )}
            </div>
            <SegmentedControl
              className="view-toggle"
              label="Result layout"
              value={view}
              options={[
                { value: "grid", label: "Grid" },
                { value: "list", label: "List" },
              ]}
              onValueChange={(value) => setView(value as "grid" | "list")}
            />
          </div>
          {canFocus && focusedResults.length > 0 && (
            <div className="search-focus-options">
              {intent.id === "snake-rescue" && (
                <p>Start with the <Link className="text-link" to="/contacts/forest">Goa Forest Department contacts</Link>. Volunteer listings below date to 2018; availability needs confirmation.</p>
              )}
              {intent.id === "animal-rescue" && <p>Check the <a className="text-link" href="https://ahvs.goa.gov.in/emergency-contact/">official veterinary directory</a> and confirm which service can help.</p>}
              <Button variant="ghost" onClick={() => change("scope", focused ? "all" : "")}>
                {focused ? `See all related results (${relatedResults.length})` : "Back to best matches"}
                <ArrowRight size={16} />
              </Button>
            </div>
          )}
          {topic && (
            <Button
              variant="ghost"
              className="active-filter"
              onClick={() => change("topic", "")}
            >
              {topic}
              <X size={14} />
              <span className="sr-only">Remove topic filter</span>
            </Button>
          )}
          {tag && <Button variant="ghost" className="active-filter" onClick={() => change("tag", "")}><span>{tag}</span><X size={14} /><span className="sr-only">Remove keyword filter</span></Button>}
          {results.length ? (
            <>
              {grouped ? (
                <div className="grouped-results">
                  {groups.map((group) => (
                    <section
                      className="result-group"
                      key={group.title}
                      aria-label={group.title}
                    >
                      <div className="result-group-heading">
                        <h2>{group.title}</h2>
                        <span>
                          {group.items.length}{" "}
                          {group.items.length === 1 ? "match" : "matches"}
                        </span>
                      </div>
                      <div
                        className={
                          view === "grid" ? "results-grid" : "results-list"
                        }
                      >
                        {group.items.slice(0, perGroup).map(({ record }) => (
                          <RecordCard
                            key={record.id}
                            record={record}
                            list={view === "list"}
                          />
                        ))}
                      </div>
                    </section>
                  ))}
                </div>
              ) : (
                <div
                  className={view === "grid" ? "results-grid" : "results-list"}
                >
                  {results.slice(0, limit).map(({ record }) => (
                    <RecordCard
                      key={record.id}
                      record={record}
                      list={view === "list"}
                    />
                  ))}
                </div>
              )}
              {moreAvailable && (
                <Button
                  variant="ghost"
                  className="button load-more"
                  onClick={() => {
                    nextResultFocus.current = (grouped ? groups.find(group => group.items.length > perGroup)?.items[perGroup] : results[limit])?.record.id ?? null;
                    setLimit(limit + 24);
                    setResultAnnouncement("More results added.");
                  }}
                >
                  Show more results <ArrowRight size={18} />
                </Button>
              )}
            </>
          ) : (
            <div className="empty-state">
              <Search size={32} />
              <h3>No matches just yet.</h3>
              <p>
                Try a broader phrase such as “waste”, “wildlife” or “panchayat”,
                or remove a filter.
              </p>
              <ButtonLink to="/search">Browse all resources</ButtonLink>
              <Link to="/contact">Ask ActForGoa for help</Link>
            </div>
          )}
          <p className="sr-only" role="status">{resultAnnouncement}</p>
        </div>
      </div>
    </main>
  );
}

function Detail({ records }: { records: RecordItem[] }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams();
  const r = records.find((x) => x.id === id);
  const [copied, setCopied] = useState(false);
  if (id?.startsWith("guide-")) return <GuideRoute />;
  if (!r) return <NotFound />;
  const listing = r.kind === "organisation" || r.kind === "contact";
  const related = records
    .filter(
      (x) =>
        x.id !== r.id &&
        x.kind === r.kind &&
        x.topics.some((t) => r.topics.includes(t)),
    )
    .slice(0, 3);
  const content = storyContent(r);
  const cover = articlePhoto(r);
  const externalLinks = content.links.filter(
    (l) => !l.url.startsWith("mailto:") && !l.url.startsWith("tel:"),
  );
  return (
    <main className={`detail shell${listing ? " listing-detail" : ""}`}>
      {location.state?.fromCatalogue ? (
        <Button
          variant="ghost"
          className="back-link"
          onClick={() => navigate(-1)}
        >
          <ArrowLeft size={16} />
          {location.state?.fromHome ? "Back to exploring" : "Back to results"}
        </Button>
      ) : (
        <Link
          className="back-link"
          to={
            r.kind === "organisation" || r.kind === "contact"
              ? "/directory/archive"
              : r.kind === "story"
                ? "/stories"
                : "/library"
          }
        >
          <ArrowLeft size={16} />
          Back to{" "}
          {r.kind === "organisation" || r.kind === "contact"
            ? "directory"
            : r.kind === "story"
              ? "stories"
              : "library"}
        </Link>
      )}

      <div className="detail-layout">
        <article>
          {r.directory ? <DirectoryTags record={r} /> : <div className="record-meta">
            <span>{r.editorialStatus === "authored-practical-guide" ? "Practical guide · Draft" : kindLabel[r.kind]}</span>
            <span>{r.topics[0]}</span>
          </div>}
          <div className="curation-heading"><h1>{r.title}</h1>{r.kind !== "page" && <CurationStar recordId={r.id} title={r.title}/>}</div>
          <div className="detail-byline">
            From ActForGoa
            {r.publishedAt && <> · Published {formatDate(r.publishedAt)}</>}
          </div>
          {r.directory?.photo && <DirectoryPhoto key={r.id} record={r} detail />}
          {!r.directory?.photo && cover && <figure className="article-cover">
            <img className="detail-image" src={cover!.src} alt={cover!.alt} />
            {cover!.credit && <figcaption>Illustrative photo · <a href={cover!.source}>{cover!.credit}</a> · <a href={cover!.licenseUrl}>{cover!.license}</a> · resized & cropped</figcaption>}
          </figure>}
          {(r.kind === "contact" || r.kind === "organisation" || r.id === "resource-590480849c") && (
            <div className="verification-note">
              This is an archived source listing. Contact details and service
              availability need confirmation.{r.retrievedAt && <> Retrieved {formatDate(r.retrievedAt)}.</>}
            </div>
          )}
          {(r.kind === "story" || r.kind === "page") && <p className="verification-note">Archived source content. Dates, invitations and opportunities describe the original publication; check the source before acting.</p>}
          {r.kind === "resource" && <p className="verification-note">Archived reference material. Rules, schemes and service details may have changed since publication. Check the official sources before acting.</p>}
          {r.editorialCorrection && <div className="verification-note">
            <strong>Source correction.</strong> {r.editorialCorrection.note}{" "}
            <a className="text-link" href={r.editorialCorrection.source}>{r.kind === "story" ? "Read the original article" : "Read the official text"} <ExternalLink size={15} /></a>
          </div>}
          <div className="reading-body">
            {r.directory?.description && r.blocks.length > 0 && <p>{r.directory.description}</p>}
            {!r.blocks.length && (r.kind === "organisation" || r.kind === "contact") && <p>{communityDescription(r)}</p>}
            {content.blocks.map((b, i) =>
              b.href ? (
                <p key={i}>
                  <a href={b.href} target="_blank" rel="noreferrer">{b.text}</a>
                </p>
              ) : b.type === "heading" ? (
                <h2 key={i}>{b.text}</h2>
              ) : b.type === "list" ? (
                <p className="reading-list-item" key={i}>
                  {b.text}
                </p>
              ) : (
                <p key={i}>{b.text}</p>
              ),
            )}
          </div>
          {r.images && r.images.length > 1 && (
            <section className="article-gallery" aria-label="Photos from the original article">
              {r.images.slice(1).map(image => <figure key={image.src}>
                <img src={image.src} alt={image.alt} width={image.width} height={image.height} loading="lazy" />
                {image.alt && <figcaption>{image.alt}</figcaption>}
              </figure>)}
            </section>
          )}
          {r.documents.length > 0 && (
            <section className="document-list">
              <h2>Documents & downloads</h2>
              {r.documents.map((d, i) => (
                <a href={d.url} key={i} target="_blank" rel="noreferrer">
                  <FileText size={22} />
                  <span>
                    {d.label}
                    {d.pages && <small>{d.pages} pages</small>}
                    {d.status && d.status >= 400 && (
                      <small>
                        Original link returned {d.status}; it may be unavailable
                      </small>
                    )}
                  </span>
                  <Download size={18} />
                </a>
              ))}
            </section>
          )}
          {externalLinks.length > 0 && (
            <details className="source-links">
              <summary>
                Links from the original entry ({externalLinks.length})
              </summary>
              {externalLinks.map((l, i) => (
                /^https?:\/\/staging\./i.test(l.url) ? <p key={i}>{l.label}: historical staging link; a current destination has not been confirmed.</p> :
                <a key={i} href={l.url} target="_blank" rel="noreferrer">
                  {l.label}
                  <ExternalLink size={13} />
                </a>
              ))}
            </details>
          )}
        </article>
        <aside className="detail-aside">
          {listing && (r.emails.length > 0 || r.locations.length > 0 || directoryLinks(r).length > 0) && <section><h2>Contact & location</h2><DirectoryActions record={r} full /><small>Published contact information, not a confirmation of current availability. See the original entry for full context.</small></section>}
          {!listing && (r.emails.length > 0 ||
            r.locations.length > 0) && (
            <section>
              <h2>Get in touch</h2>
              {r.emails.map((e, i) => (
                <div className="contact-line" key={i}>
                  <Mail size={17} />
                  <a href={"mailto:" + e}>{e}</a>
                </div>
              ))}
              {r.locations.map((l, i) => (
                <div className="contact-line" key={i}>
                  <MapPin size={17} />
                  <span>{l}</span>
                </div>
              ))}
              <small>
                Published contact information, not a confirmation of current
                availability. See the original entry for full context.
              </small>
            </section>
          )}
          <section>
            <h2>Keep the source close.</h2>
            <p>Read this entry in its original context.</p>
            {r.sourceStatus !== null && r.sourceStatus >= 400 && <p>The original page returned an error when archived. Use the public directory record below where available.</p>}
            {listing ? <ListingLink href={r.source} kind="source">Original ActForGoa page</ListingLink> : <a
              className="text-link"
              href={r.source}
              target="_blank"
              rel="noreferrer"
            >
              Original ActForGoa page
            </a>}
            {r.sourceApi && (
              listing ? <ListingLink href={r.sourceApi} kind="source">Public directory record</ListingLink> : <a
                className="subtle-link"
                href={r.sourceApi}
                target="_blank"
                rel="noreferrer"
              >
                Public directory record <ExternalLink size={14} />
              </a>
            )}
            {r.directory?.sources.filter(source => source !== r.source && source !== r.sourceApi).map(source => <ListingLink key={source} href={source} kind="source">{new URL(source).hostname.replace(/^www\./, "")}</ListingLink>)}
            <Button
              variant="ghost"
              className={`subtle-link${listing ? " listing-copy-link" : ""}`}
              onClick={async () => {
                try {
                  await navigator.clipboard.writeText(window.location.href);
                  setCopied(true);
                } catch {
                  setCopied(false);
                }
              }}
            >
              {copied ? <Check size={18} strokeWidth={1.7} aria-hidden="true" /> : <Copy size={18} strokeWidth={1.7} aria-hidden="true" />}{" "}
              {copied ? "Link copied" : "Copy a link to this entry"}
            </Button>
          </section>
          <section>
            <h2>Know something we should?</h2>
            <p>Help keep this knowledge useful.</p>
            <Link
              className={listing ? "listing-link" : "text-link"}
              to={"/contact?entry=" + encodeURIComponent(r.title)}
            >
              {listing && <MessageSquare size={18} strokeWidth={1.7} aria-hidden="true" />}Suggest a correction {!listing && <ArrowRight size={16} />}
            </Link>
          </section>
        </aside>
      </div>
      {related.length > 0 && (
        <section className="related">
          <div className="section-heading">
            <h2>Keep exploring</h2>
          </div>
          <div className="card-grid">
            {related.map((record) => (
              <RecordCard key={record.id} record={record} />
            ))}
          </div>
        </section>
      )}
    </main>
  );
}
function About() {
  return (
    <main className="about shell">
      <div className="about-intro">
        <h1>
          A platform for everyone
          <br />
          who loves Goa.
        </h1>
        <p>Enabling people to care for Goa.</p>
      </div>
      <div className="about-layout">
        <div className="reading-body">
          <p>
            ActforGoa is envisioned as a platform belonging to everyone who loves
            Goa. The content you find here is the collective work of a vast array
            of people.
          </p>
          <p>
            ActforGoa will strive to promote content that is well meaning and
            factual, and will censor personal attacks, slander or attempts at
            defamation.
          </p>
          <p>Kokum Trust is the legal managing entity for Act for Goa.</p>
          <p>
            With deep gratitude to the numerous people who care for Goa and give
            back generously with their time, money, expertise, networks,
            influence, premises or other resources.
          </p>
          <a className="text-link" href="https://actforgoa.org/about-2/">
            Read the original About page
          </a>
        </div>
        <aside>
          <h2>Learn. Connect. Act.</h2>
          <Link to="/library">
            Find useful knowledge <ArrowRight size={17} />
          </Link>
          <Link to="/directory">
            Explore the directory <ArrowRight size={17} />
          </Link>
          <Link to="/get-involved">
            Take your next step <ArrowRight size={17} />
          </Link>
          <a href="https://actforgoa.org/about-2/annual-reports/">
            Annual reports
          </a>
          <a href="https://actforgoa.org/press-coverage/">
            Press coverage
          </a>
        </aside>
      </div>
      <section id="sources" className="about-sources">
        <h2>About this field guide</h2>
        <p>
          This preview brings together publicly available information from
          ActForGoa, retrieved on 22 October 2026. Original content and links
          have been preserved in a local archive. Five practical guides add official sources, forms you can fill in here and save as PDF, and visible verification flags. They remain drafts for legal and service review. Some records are historical;
          their publication date is shown where available.
        </p>
        <p>
          Directory and library search find entries without generating answers.
          Ask uses Anthropic to write answers from source passages: your question,
          relevant excerpts and recent conversation are sent to that provider.
          No account is needed. Check the cited passages and their dates; an AI
          answer does not verify current contact details or replace professional advice.
        </p>
        <p>
          Contact forms prepare an email for you to review and send without
          storing that message here. Private incident reports use a separate
          review inbox and are not published or automatically forwarded to authorities.
          The existing ActForGoa website remains the original source.
        </p>
      </section>
    </main>
  );
}
function Contact({ involve = false }: { involve?: boolean }) {
  const [params] = useSearchParams();
  const [prepared, setPrepared] = useState(false);
  const [mailUrl, setMailUrl] = useState("");
  function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const d = new FormData(e.currentTarget);
    const subject = String(d.get("reason"));
    const message = `${d.get("message")}\n\nName: ${d.get("name")}\nReply to: ${d.get("email")}${params.get("entry") ? "\nEntry: " + params.get("entry") : ""}`;
    setMailUrl(
      "mailto:info@actforgoa.org?subject=" +
        encodeURIComponent(subject) +
        "&body=" +
        encodeURIComponent(message),
    );
    setPrepared(true);
  }
  return (
    <main className="contact-page shell">
      <div className="catalogue-heading">
        <h1>
          {involve
            ? "A better Goa starts with us."
            : "Let’s keep Goa connected."}
        </h1>
        <p>
          {involve
            ? "Your time, your knowledge, your little corner of Goa. It all matters."
            : "Share a local initiative, update an entry, or tell us what you’re looking for."}
        </p>
      </div>
      {involve && (
        <div className="involvement-links">
          <a href="https://actforgoa.org/volunteer/">
            <Heart size={24} />
            <h2>Give your time</h2>
            <p>Explore volunteering with ActForGoa.</p>
          </a>
          <Link to="/directory">
            <Users size={24} />
            <h2>Find your people</h2>
            <p>Connect with an organisation near you.</p>
          </Link>
          <a href="https://actforgoa.org/greenviksitgoa/">
            <Leaf size={24} />
            <h2>Explore Goa’s future</h2>
            <p>Read the archived Green Viksit Goa consultation.</p>
          </a>
        </div>
      )}
      <div className="contact-layout">
        <div>
          <h2>
            {involve
              ? "Tell us how you’d like to help."
              : "Send a little local knowledge."}
          </h2>
          <p>
            This form prepares an email. You’ll review it in your email app and
            send it yourself.
          </p>
          <form
            onSubmit={submit}
            className="contact-form"
            onChange={() => setPrepared(false)}
          >
            <div className="form-pair">
              <Input
                label="Your name"
                name="name"
                autoComplete="name"
                required
                maxLength={100}
              />
              <Input
                label="Email address"
                name="email"
                type="email"
                autoComplete="email"
                required
                maxLength={160}
              />
            </div>
            <MorphSelect label="I’d like to" name="reason"
              defaultValue={params.get("entry") ? "Suggest a correction" : params.get("reason") === "Work with ActForGoa" ? "Work with ActForGoa" : involve ? "Volunteer with ActForGoa" : "Ask a question"}
              onValueChange={() => setPrepared(false)}
              items={["Ask a question", "Work with ActForGoa", "Suggest a correction", "List an organisation", "Share a story or resource", "Volunteer with ActForGoa"].map(value => ({value, label: value}))}
            />
            {params.get("entry") && (
              <p className="entry-reference">About: {params.get("entry")}</p>
            )}
            <Textarea
              label="Your message"
              name="message"
              rows={6}
              required
              maxLength={4000}
              placeholder="Tell us a little about it. Include useful links if you have them."
            />
            <Button className="button green" type="submit">
              Prepare email <ArrowRight size={18} />
            </Button>
            {prepared && (
              <div className="email-ready" role="status">
                <Check size={20} />
                <div>
                  <strong>Your email is ready to review.</strong>
                  <p>Nothing has been sent yet.</p>
                  <a href={mailUrl}>
                    Open your email app
                  </a>
                </div>
              </div>
            )}
          </form>
        </div>
        <aside>
          <h2>Prefer to get in touch directly?</h2>
          <a href="mailto:info@actforgoa.org">
            <Mail size={18} />
            info@actforgoa.org
          </a>
          <p>
            1 Design Valley
            <br />
            Alto Povorim 403521, Goa
          </p>
          <small>
            Contact details as published on the{" "}
            <a href="https://actforgoa.org/contact-us/">
              original contact page
            </a>
            . Please confirm they are current.
          </small>
        </aside>
      </div>
    </main>
  );
}
function NotFound() {
  return (
    <main className="empty-state shell">
      <h1>This path is still unexplored.</h1>
      <p>
        That entry isn’t in this guide. Search the collection or head back to
        the start.
      </p>
      <ButtonLink to="/">Explore ActForGoa</ButtonLink>
    </main>
  );
}
export default function App() {
  const { language } = useLanguage();
  const { pathname, search, hash } = useLocation();
  const navigationType = useNavigationType();
  const previousPath = useRef(pathname);
  const scrollPath = useRef(pathname);
  useLayoutEffect(() => {
    const moved = scrollPath.current !== pathname;
    scrollPath.current = pathname;
    if (moved && navigationType === "PUSH" && !window.location.hash) window.scrollTo({top: 0, behavior: "instant"});
  }, [pathname, navigationType]);
  useEffect(() => {
    if (!hash) return;
    let id: string;
    try { id = decodeURIComponent(hash.slice(1)); } catch { return; }
    let frame = 0;
    const jump = () => {
      const target = document.getElementById(id);
      if (!target) return;
      observer.disconnect();
      frame = requestAnimationFrame(() => target.scrollIntoView({block: "start", behavior: "instant"}));
    };
    // Hash destinations can arrive after the lazy page or catalogue has mounted.
    const observer = new MutationObserver(jump);
    observer.observe(document.getElementById("content") || document.body, {childList: true, subtree: true});
    jump();
    const timeout = window.setTimeout(() => observer.disconnect(), 5000);
    return () => { observer.disconnect(); cancelAnimationFrame(frame); clearTimeout(timeout); };
  }, [pathname, hash]);
  const orbitLanding = pathname.replace(/\/$/, "") === "/explore";
  const internal = pathname === "/admin" || pathname.startsWith("/admin/");
  const { records, error } = useLoaderData() as {
    records: RecordItem[];
    error: boolean;
  };
  useEffect(() => {
    const moved = previousPath.current !== pathname;
    previousPath.current = pathname;
    const content = document.getElementById("content");
    if (!content) return;
    let focused = false;
    const update = () => {
      const heading = content.querySelector<HTMLHeadingElement>("h1");
      if (!heading) return;
      const query = new URLSearchParams(search).get("q");
      const title = (heading.getAttribute("aria-label") || heading.innerText).replace(/\s+/g, " ").trim();
      document.title = `${title}${query ? `: ${query}` : ""} | ActForGoa`;
      if (moved && navigationType === "PUSH" && !focused && !window.location.hash) {
        heading.tabIndex = -1;
        heading.focus({ preventScroll: true });
        focused = true;
      }
    };
    update();
    // Lazy guide/editor headings arrive after the route shell.
    const observer = new MutationObserver(update);
    observer.observe(content, { childList: true, subtree: true, characterData: true });
    return () => observer.disconnect();
  }, [pathname, search, navigationType, error]);
  return (
    <ResearchMemoryProvider>
      <a href="#content" className="skip-link">
        Skip to content
      </a>
      {!internal && <>{pathname === "/" || pathname.toLowerCase() === "/ai" || orbitLanding ? <div className="goa-orbit-navigation"><Header /></div> : <Header />}{pathname !== "/" && !pathname.toLowerCase().startsWith("/ai") && !orbitLanding && pathname !== "/map" && !pathname.startsWith("/ask") && !pathname.startsWith("/templates/") && pathname !== "/report" && pathname !== "/research-library" && !pathname.startsWith("/documents/") && <TeamBrowsingBar />}</>}
      {!internal && language !== "en" && <div className="translation-notice" role="status"><span lang={language}>{language === "hi" ? "अनुवाद अभी तैयार हो रहा है। कुछ सामग्री अंग्रेज़ी में है; खोज अभी अंग्रेज़ी में उपलब्ध है।" : "भाशांतराचें काम चालू आसा. कांय मजकूर इंग्लिशांत आसा; सोद सध्या इंग्लिशांत उपलब्ध आसा."}</span><span lang="en"> Translation preview: some content and search are in English. Translations have not yet been locally reviewed.</span></div>}
      <div id="content" tabIndex={-1}>
        {pathname.replace(/\/$/, "") === "/emergency" ? <EmergencyServices /> : error ? (
          <main className="empty-state shell">
            <h1>The field guide couldn’t load.</h1>
            <p>
              Please refresh to try again, or visit the original ActForGoa
              website.
            </p>
            <Button
              variant="ghost"
              className="button green"
              onClick={() => window.location.reload()}
            >
              Try again
            </Button>
            <a href="https://actforgoa.org/">Visit ActForGoa</a>
          </main>
        ) : (
          <Suspense fallback={<main className="loading-state shell" role="status"><p>Opening this page…</p><Link to="/emergency">Emergency services</Link></main>}>
          <Routes>
            <Route path="/AI" element={<AIHome />} />
            <Route path="/explore" element={<Home records={records} />} />
            <Route path="/mcp" element={<McpPage />} />
            <Route path="/ask" element={<Research />} />
            <Route path="/ask/legal" element={<Research domain="legal" />} />
            <Route path="/ask/ecology" element={<Research domain="ecology" />} />
            <Route path="/documents/:id" element={<ResearchDocument />} />
            <Route path="/research-library" element={<ResearchLibrary />} />
            <Route path="/contacts/:department" element={<GovernmentContacts />} />
            <Route path="/" element={<Home records={records} />} />
            <Route path="/topics/:slug/:actionId?/:choiceId?" element={<TopicPage records={records} />} />
            <Route path="/search" element={<Catalogue records={records} />} />
            <Route path="/climate-plan/:topicId?" element={<ClimatePlan />} />
            <Route path="/read/goa-sapcc" element={<ClimatePlan />} />
            <Route path="/directory" element={<CRM />} />
            <Route path="/directory/:recordId" element={<CRM />} />
            <Route path="/crm" element={<CRM />} />
            <Route path="/crm/:recordId" element={<CRM />} />
            <Route
              path="/directory/archive"
              element={
                <Catalogue key="directory" records={records} mode="directory" />
              }
            />
            <Route
              path="/library"
              element={
                <Catalogue key="library" records={records} mode="library" />
              }
            />
            <Route
              path="/stories"
              element={
                <Catalogue key="stories" records={records} mode="stories" />
              }
            />
            <Route path="/blog" element={<Blog />} />
            <Route path="/blog/archive" element={<Catalogue key="blog-archive" records={records} mode="blog" />} />
            <Route path="/blog/:slug" element={<Blog />} />
            <Route path="/admin/*" element={<AdminDashboard />} />
            <Route path="/map" element={<Satellite />} />
            <Route path="/read/wp-8905" element={<Navigate to="/newsletters" replace />} />
            <Route path="/newsletters" element={<Newsletters />} />
            <Route path="/newsletters/:issueId" element={<Newsletters />} />
            <Route path="/read/:id" element={<Detail records={records} />} />
            <Route path="/templates/:id" element={<TemplateEditor />} />
            <Route path="/about" element={<About />} />
            <Route path="/get-involved" element={<Contact involve />} />
            <Route path="/report" element={<ReportIncident />} />
            <Route path="/reports/review" element={<ReportInbox />} />
            <Route path="/contact" element={<Contact key={pathname + search} />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
          </Suspense>
        )}
      </div>
      <ScrollRestoration />
      {!internal && !orbitLanding && pathname !== "/map" && <SiteFooter />}
      {!internal && !orbitLanding && pathname !== "/map" && <div className="preview-note">
        A new field guide, in progress.{" "}
        <a href="https://actforgoa.org/">
          Visit the original site
        </a>
      </div>}
    </ResearchMemoryProvider>
  );
}
