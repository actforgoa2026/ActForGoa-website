import { Link, useLocation } from "react-router-dom";
import { Users, BookOpen, Leaf, FileText, ArrowUpRight } from "lucide-react";
import { communityDescription } from "../public-record";
import { kindLabel, type RecordItem } from "../types";
const recordPath = (r: RecordItem) => "/read/" + r.id;
const formatDate = (value: string) => {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
};

export function RecordCard({
  record: r,
  list = false,
  showImage = true,
}: {
  record: RecordItem;
  list?: boolean;
  showImage?: boolean;
}) {
  const location = useLocation();
  const fromCatalogue = [
    "/",
    "/search",
    "/library",
    "/directory",
    "/stories",
    "/blog",
  ].includes(location.pathname) || location.pathname.startsWith("/topics/");
  const community = r.kind === "organisation" || r.kind === "contact";
  const description = community ? communityDescription(r) : r.summary;
  const Icon =
    r.kind === "organisation" || r.kind === "contact"
      ? Users
      : r.kind === "resource"
        ? BookOpen
        : r.kind === "story"
          ? Leaf
          : FileText;
  return (
    <article data-record-id={r.id} className={"record-card " + (list ? "list-card " : "") + (community ? "community-entry" : "")}>
      {showImage && !list && r.image && (
        <Link
          to={recordPath(r)}
          state={{ fromCatalogue, fromHome: location.pathname === "/" }}
          tabIndex={-1}
          aria-hidden="true"
          className="card-image"
        >
          <img src={r.image} alt="" loading="lazy" />
        </Link>
      )}
      <div className="card-content">
        <div className="record-meta">
          <span>
            <Icon size={15} />
            {r.editorialStatus === "authored-practical-guide" ? "Practical guide · Draft" : kindLabel[r.kind]}
          </span>
          {r.locality && <span>{r.locality}</span>}
          {r.publishedAt && <time dateTime={r.publishedAt}>{formatDate(r.publishedAt)}</time>}
          {community && <span>Archived listing · availability unconfirmed</span>}
        </div>
        <h3>
          <Link
            to={recordPath(r)}
            state={{ fromCatalogue, fromHome: location.pathname === "/" }}
          >
            {r.title}
            <ArrowUpRight size={19} />
          </Link>
        </h3>
        {description && description !== "Read the original resource from ActForGoa." && (
          <p>
            {r.id === "resource-590480849c"
              ? "A locality-by-locality list of snake rescue volunteers, published in 2018. Contact details need current confirmation."
              : description}
          </p>
        )}
        <div className="card-bottom">
          <span>{community ? r.topics.join(" · ") : r.topics[0]}</span>
        </div>

      </div>
    </article>
  );
}
