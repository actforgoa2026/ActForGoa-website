import {
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
  ScrollRestoration,
} from "react-router-dom";
import {
  ArrowRight,
  ArrowUpRight,
  Search,
  Leaf,
  Users,
  Heart,
  BookOpen,
  Mail,
  MapPin,
  ExternalLink,
  ArrowLeft,
  Check,
  X,
  FileText,
  SlidersHorizontal,
  Download,
} from "lucide-react";
import SiteHeader from "./components/arc/site-header/site-header";
import { communityDescription } from "./public-record";
import type { RecordItem } from "./types";
import { TOPICS, kindLabel } from "./types";
import { hybridSearch } from "./search";
import { guideDocuments } from "./guides";
import { PracticalGuide } from "./PracticalGuide";
import {TopicIcon} from "./components/TopicIcon";
import {topicFlows, topicFor, topicHref} from "./topic-flows";
import {TopicPage, TopicChoices} from "./TopicPage";
import {RecordCard} from "./components/RecordCard";
import { buildDiscoveryFeed } from "./discovery";
import { Button } from "./components/arc/button/button";
import { SearchField } from "./components/arc/search-field/search-field";
import { Input } from "./components/arc/input/input";
import { Textarea } from "./components/arc/textarea/textarea";
import SegmentedControl from "./components/arc/segmented-control/segmented-control";
import { browsingState, semanticCache, homeFeedState } from "./browsing-state";
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
  const navigate = useNavigate();
  const location = useLocation();
  useEffect(() => setValue(initial), [initial]);
  function submit(e: FormEvent) {
    e.preventDefault();
    navigate("/search?q=" + encodeURIComponent(value.trim()), {
      preventScrollReset: location.pathname === "/search",
    });
  }
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
        placeholder="Find local help"
        autoComplete="off"
      />
      <Button size="lg" type="submit" aria-label="Search the field guide">
        <span className="search-submit-label">Search</span>
        <ArrowRight size={20} />
      </Button>
    </form>
  );
}
const navigation = [
  { value: "home", label: "Home", href: "/" },
  { value: "action", label: "Take action", links: [
    { label: "Take action", description: "Find your way to contribute to Goa.", href: "/get-involved" },
    { label: "Green Viksit Goa", description: "Explore the shared vision for Goa’s future.", href: "/read/wp-9389" },
    { label: "Amche Mollem", description: "Learn about the campaign for Mollem.", href: "/read/wp-6263" },
    { label: "Donations", description: "Support ActForGoa through the original site.", href: "https://actforgoa.org/donation-form/" },
  ] },
  { value: "blog", label: "Blog", href: "/blog" },
  { value: "stories", label: "Inspiring stories", href: "/stories" },
  { value: "resources", label: "Resources", href: "/library" },
  { value: "about", label: "About", links: [
    { label: "About ActForGoa", description: "Enabling people to care for Goa.", href: "/about" },
    { label: "Newsletters", description: "Updates from the ActForGoa community.", href: "/read/wp-8905" },
    { label: "Annual reports", description: "Read about the work over the years.", href: "/read/wp-8903" },
    { label: "Press coverage", description: "ActForGoa in the news.", href: "/read/wp-7377" },
  ] },
  { value: "work", label: "Work with us", href: "/contact?reason=Work%20with%20ActForGoa" },
  { value: "volunteer", label: "Volunteer", href: "/read/wp-2249" },
  { value: "community", label: "Community", href: "/directory" },
];
function Header() {
  const { pathname } = useLocation();
  const current = pathname === "/" ? "home" : pathname === "/directory" ? "community" : pathname === "/library" ? "resources" : pathname === "/get-involved" ? "action" : pathname.slice(1);
  return <SiteHeader
    variant="mega" brand={{ name: "actforgoa.", href: "/", mark: <></> }}
    items={navigation} current={current} label="Main navigation"
    secondaryAction={null} primaryAction={{ label: "Search", href: "/search" }}
  />;
}
function Footer() {
  return (
    <footer className="footer">
      <div className="footer-top">
        <div>
          <Link to="/" className="wordmark">
            act<span>for</span>goa.
          </Link>
          <p>Enabling people to care for Goa.</p>
        </div>
        <p>
          A platform belonging to everyone who loves Goa.
          <br />
          Built on the collective work of people who care.
        </p>
        <Link to="/contact">
          Let’s stay connected <ArrowUpRight size={18} />
        </Link>
      </div>
      <div className="footer-bottom">
        <span>Kokum Trust is the legal managing entity for Act for Goa.</span>
        <div>
          <a href="https://actforgoa.org/privacy-policy/">Privacy</a>
          <a href="https://actforgoa.org/terms-and-conditions/">Terms</a>
          <Link to="/about#sources">About this guide</Link>
        </div>
      </div>
    </footer>
  );
}

function Home({ records }: { records: RecordItem[] }) {
  return <main>
    <section className="home-intro shell">
      <h1>Enabling people to care for Goa.</h1>
      <p>Find practical help, local people, and your next step.</p>
      <SearchBox large />
    </section>
    <section className="home-topics shell" aria-labelledby="home-topics-heading">
      <h2 id="home-topics-heading">What do you need help with?</h2>
      <nav className="choice-grid home-choice-grid" aria-label="Choose a topic">
        {topicFlows.map(flow => <Link className="choice-link" key={flow.slug} to={topicHref(flow.topic)}>
          <TopicIcon name={flow.icon}/><span>{flow.label}</span><ArrowRight size={22}/>
        </Link>)}
      </nav>
    </section>
    <DiscoveryFeed records={records}/>
  </main>;
}

function DiscoveryFeed({ records }: { records: RecordItem[] }) {
  const location = useLocation();
  const saved = homeFeedState.get(location.key);
  const [limit, setLimit] = useState(saved?.limit ?? 12);
  const [kind, setKind] = useState(saved?.kind ?? "all");
  const [automatic, setAutomatic] = useState(saved?.automatic ?? true);
  const marker = useRef<HTMLDivElement>(null);
  const feedRoot = useRef<HTMLDivElement>(null);
  const pendingFocus = useRef<number | null>(null);
  const [announcement, setAnnouncement] = useState("");
  const mixed = useMemo(() => buildDiscoveryFeed(records), [records]);
  const entries = useMemo(
    () =>
      mixed.filter(
        (r) =>
          kind === "all" ||
          r.kind === kind ||
          (kind === "organisation" && r.kind === "contact"),
      ),
    [mixed, kind],
  );
  const shown = entries.slice(0, limit);
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
  const batches = Array.from({ length: Math.ceil(shown.length / 12) }, (_, i) =>
    shown.slice(i * 12, (i + 1) * 12),
  );
  return (
    <section className="discovery shell" aria-labelledby="discovery-heading">
      <div className="section-heading">
        <div>
          <h2 id="discovery-heading">A little knowledge goes a long way.</h2>
          <p>Guides to read. People to meet. More ways to care for Goa.</p>
        </div>
        <Link className="text-link" to="/directory">
          Explore the directory <ArrowUpRight size={18} />
        </Link>
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
        {batches.map((batch, batchIndex) => (
          <div className="discovery-batch" key={batchIndex}>
            <div
              className={kind === "all" ? "discovery-lead" : "discovery-grid"}
            >
              {batch.slice(0, 3).map((record, index) => (
                <div data-feed-index={batchIndex * 12 + index} key={record.id}>
                  <RecordCard record={record} />
                </div>
              ))}
            </div>
            {batch.length > 3 && (
              <div className="discovery-grid">
                {batch.slice(3).map((record, index) => (
                  <div
                    data-feed-index={batchIndex * 12 + index + 3}
                    key={record.id}
                  >
                    <RecordCard record={record} />
                  </div>
                ))}
              </div>
            )}
            {batchIndex < TOPICS.length && (
              <div className="discovery-way-in">
                <h3>Explore {TOPICS[batchIndex].toLowerCase()}</h3>
                <Link
                  className="text-link"
                  to={topicHref(TOPICS[batchIndex])}
                >
                  Find guides, people and local projects{" "}
                  <ArrowRight size={18} />
                </Link>
              </div>
            )}
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
              Know something we should add? <ArrowUpRight size={18} />
            </Link>
          </>
        )}
        <Link className="subtle-link" to="/get-involved">
          Take part in ActForGoa <ArrowUpRight size={16} />
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
  const [params, setParams] = useSearchParams();
  const query = params.get("q") || "";
  const topic = params.get("topic") || "";
  const filter = params.get("type") || "all";
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
      limit: saved?.limit ?? 24,
    });
  }
  const { view, limit } = page;
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
  }, [location.key, view, limit]);
  const [semanticQuery, setSemanticQuery] = useState(query);
  if (semanticQuery !== query) {
    setSemanticQuery(query);
    setSemantic(semanticCache.get(query) ?? null);
  }
  const worker = useRef<Worker | null>(null);
  const seq = useRef(0);
  useEffect(() => () => worker.current?.terminate(), []);
  useEffect(() => {
    const id = ++seq.current;
    if (semanticCache.has(query)) {
      setStatus("ready");
      return;
    }
    if (!query.trim()) {
      setStatus("idle");
      return;
    }
    setStatus("loading");
    const timer = setTimeout(() => {
      try {
        worker.current ||= new Worker(
          new URL("./semantic.worker.ts", import.meta.url),
          { type: "module" },
        );
        worker.current.onmessage = ({ data }) => {
          if (data.id !== seq.current) return;
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
          if (id === seq.current) setStatus("fallback");
        };
        worker.current.postMessage({ query, id });
      } catch {
        setStatus("fallback");
      }
    }, 250);
    return () => clearTimeout(timer);
  }, [query]);
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
        Number(b.record.text.trim().length > 80) - Number(a.record.text.trim().length > 80) ||
        a.record.title.localeCompare(b.record.title));
      return ranked;
    },
    [base, query, semantic, mode],
  );
  const results = ranked.filter(
    ({ record: r }) =>
      (!topic || r.topics.includes(topic)) &&
      (filter === "all" ||
        r.kind === filter ||
        (filter === "organisation" && r.kind === "contact")),
  );
  const grouped = query.trim() && mode === "search" && filter === "all";
  const groups = [
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
  const perGroup = Math.max(6, Math.floor(limit / 4));
  const moreAvailable = grouped
    ? groups.some((group) => group.items.length > perGroup)
    : limit < results.length;
  const [title, description] =
    mode === "directory"
      ? [
          "People who care.",
          "Find organisations, local initiatives, and people working for a better Goa.",
        ]
      : mode === "library"
        ? [
            "A library for everyday action.",
            "Practical guides, civic information, and ideas worth putting into practice.",
          ]
        : mode === "blog"
          ? ["Notes from Goa.", "Articles, updates, and ideas from ActForGoa."]
          : mode === "stories"
          ? [
              "Good things start with people.",
              "Stories of local action, shared effort, and a Goa worth caring for.",
            ]
          : [
              "Find your next step.",
              "Local people, practical resources, and community knowledge, all in one place.",
            ];
  const change = (key: string, value: string) => {
    const next = new URLSearchParams(params);
    value ? next.set(key, value) : next.delete(key);
    setParams(next, { preventScrollReset: true });
  };
  return (
    <main className="catalogue shell">
      <div className="catalogue-heading">
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
      <SearchBox initial={query} />
      {topic && !query && topicFor(topic) && <TopicChoices flow={topicFor(topic)!} />}
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
          {TOPICS.map((t) => {
            return (
              <Button
                variant="ghost"
                aria-pressed={topic === t}
                className={topic === t ? "selected" : ""}
                key={t}
                onClick={() => change("topic", t)}
              >
                <TopicIcon name={topicFor(t)?.icon || "community"} />
                <span className="filter-topic-label">{t}</span>
              </Button>
            );
          })}
          <p>
            Choose a topic to narrow your results.
          </p>
        </aside>
        <div className="results-area">
          {mode === "search" && (
            <SegmentedControl
              className="result-tabs"
              label="Result type"
              value={filter}
              options={[
                { value: "all", label: "Everything" },
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
              <h2 aria-live="polite">
                {results.length} {results.length === 1 ? "result" : "results"}
                {query && <> for “{query}”</>}
              </h2>
              {query && (
                <p className="search-status" role="status">
                  {status === "loading"
                    ? "Finding more results…"
                    : status === "ready"
                      ? ""
                      : status === "fallback"
                        ? ""
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
                  onClick={() => setLimit(limit + 24)}
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
              <Link className="button green" to="/search">
                Browse all resources <ArrowRight size={17} />
              </Link>
              <Link to="/contact">Ask ActForGoa for help</Link>
            </div>
          )}
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
  const guide = guideDocuments.find(g => g.id === id);
  if (guide) return <PracticalGuide key={guide.id} guide={guide} />;
  if (!r) return <NotFound />;
  const related = records
    .filter(
      (x) =>
        x.id !== r.id &&
        x.kind === r.kind &&
        x.topics.some((t) => r.topics.includes(t)),
    )
    .slice(0, 3);
  const externalLinks = r.links.filter(
    (l) => !l.url.startsWith("mailto:") && !l.url.startsWith("tel:"),
  );
  return (
    <main className="detail shell">
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
              ? "/directory"
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
          <div className="record-meta">
            <span>{r.editorialStatus === "authored-practical-guide" ? "Practical guide" : kindLabel[r.kind]}</span>
            <span>{r.topics[0]}</span>
          </div>
          <h1>{r.title}</h1>
          <div className="detail-byline">
            From ActForGoa
            {r.publishedAt && <> · Published {formatDate(r.publishedAt)}</>}
          </div>
          {r.image && (
            <img className="detail-image" src={r.image} alt={r.title} />
          )}
          <div className="reading-body">
            {!r.blocks.length && (r.kind === "organisation" || r.kind === "contact") && <p>{communityDescription(r)}</p>}
            {r.blocks.map((b, i) =>
              b.type === "heading" ? (
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
                        This download may no longer be available
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
                Useful links ({externalLinks.length})
              </summary>
              {externalLinks.map((l, i) => (
                <a key={i} href={l.url} target="_blank" rel="noreferrer">
                  {l.label}
                  <ExternalLink size={13} />
                </a>
              ))}
            </details>
          )}
        </article>
        <aside className="detail-aside">
          {(r.emails.length > 0 ||
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
                Check opening hours and availability before visiting.
              </small>
            </section>
          )}
          <section>
            <h2>More information</h2>
            <a
              className="text-link"
              href={r.source}
              target="_blank"
              rel="noreferrer"
            >
              Original ActForGoa page <ArrowUpRight size={16} />
            </a>
            <Button
              variant="ghost"
              className="subtle-link"
              onClick={async () => {
                try {
                  await navigator.clipboard.writeText(window.location.href);
                  setCopied(true);
                } catch {
                  setCopied(false);
                }
              }}
            >
              {copied ? <Check size={15} /> : <ExternalLink size={15} />}{" "}
              {copied ? "Link copied" : "Copy a link to this entry"}
            </Button>
          </section>
          <section>
            <h2>Know something we should?</h2>
            <p>Help keep this knowledge useful.</p>
            <Link
              className="text-link"
              to={"/contact?entry=" + encodeURIComponent(r.title)}
            >
              Suggest a correction <ArrowRight size={16} />
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
function About({ records }: { records: RecordItem[] }) {
  const r = records.find((r) => r.id === "wp-2059");
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
          <h2>Why ActForGoa exists</h2>
          <p>
            ACTforGOA is a new platform to help sustainable development take
            root in Goa.
          </p>
          <p>
            What future could be possible if we all worked together to keep Goa
            Clean and Green now and for the future?
          </p>
          {r ? (
            <>
              <h2>In ActForGoa’s own words</h2>
              {r.blocks
                .filter(
                  (b) =>
                    b.text.length > 75 &&
                    !b.text.includes("ACTforGOA is a new platform"),
                )
                .map((b, i) => (
                  <p key={i}>{b.text}</p>
                ))}
            </>
          ) : (
            <p>
              <a href="https://actforgoa.org/about-2/">
                Read the full original About page.
              </a>
            </p>
          )}
          <a className="text-link" href="https://actforgoa.org/about-2/">
            Read the original About page <ArrowUpRight size={16} />
          </a>
        </div>
        <aside>
          <h2>Learn. Connect. Act.</h2>
          <Link to="/library">
            Find useful knowledge <ArrowRight size={17} />
          </Link>
          <Link to="/directory">
            Meet the community <ArrowRight size={17} />
          </Link>
          <Link to="/get-involved">
            Take your next step <ArrowRight size={17} />
          </Link>
          <a href="https://actforgoa.org/about-2/annual-reports/">
            Annual reports <ArrowUpRight size={17} />
          </a>
          <a href="https://actforgoa.org/press-coverage/">
            Press coverage <ArrowUpRight size={17} />
          </a>
        </aside>
      </div>
      <section id="sources" className="about-sources">
        <h2>About this field guide</h2>
        <p>Find local organisations, practical guides and stories from people caring for Goa. You do not need an account.</p>
        <p>Some articles and listings are older. Check current services and requirements with the relevant organisation before making plans.</p>
        <p>The contact form opens an email for you to review and send.</p>
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
            <ArrowUpRight size={21} />
          </a>
          <Link to="/directory">
            <Users size={24} />
            <h2>Find your people</h2>
            <p>Connect with an organisation near you.</p>
            <ArrowUpRight size={21} />
          </Link>
          <a href="https://actforgoa.org/greenviksitgoa/">
            <Leaf size={24} />
            <h2>Shape Goa’s future</h2>
            <p>Explore the Green Viksit Goa initiative.</p>
            <ArrowUpRight size={21} />
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
            <label>
              I’d like to
              <select
                name="reason"
                defaultValue={
                  params.get("entry")
                    ? "Suggest a correction"
                    : ["Ask a question", "Work with ActForGoa", "Suggest a correction", "List an organisation", "Share a story or resource", "Volunteer with ActForGoa"].includes(params.get("reason") || "") ? params.get("reason")!
                    : involve
                      ? "Volunteer with ActForGoa"
                      : "Ask a question"
                }
              >
                <option>Ask a question</option>
                <option>Work with ActForGoa</option>
                <option>Suggest a correction</option>
                <option>List an organisation</option>
                <option>Share a story or resource</option>
                <option>Volunteer with ActForGoa</option>
              </select>
            </label>
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
                    Open your email app <ArrowUpRight size={16} />
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
      <Link className="button green" to="/">
        Explore ActForGoa <ArrowRight size={18} />
      </Link>
    </main>
  );
}
export default function App() {
  const { records, error } = useLoaderData() as {
    records: RecordItem[];
    error: boolean;
  };
  return (
    <>
      <a href="#content" className="skip-link">
        Skip to content
      </a>
      <Header />
      <div id="content">
        {error ? (
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
          <Routes>
            <Route path="/" element={<Home records={records} />} />
            <Route path="/topics/:slug/:actionId?/:choiceId?" element={<TopicPage records={records}/>} />
            <Route path="/search" element={<Catalogue records={records} />} />
            <Route
              path="/directory"
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
            <Route path="/blog" element={<Catalogue key="blog" records={records} mode="blog" />} />
            <Route path="/read/:id" element={<Detail records={records} />} />
            <Route path="/about" element={<About records={records} />} />
            <Route path="/get-involved" element={<Contact involve />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        )}
      </div>
      <ScrollRestoration />
      <Footer />
    </>
  );
}
