import {Link, useLocation} from "react-router-dom";
import {Users, BookOpen, Leaf, FileText, ArrowUpRight, MapPin} from "lucide-react";
import {communityDescription} from "../public-record";
import {kindLabel, type RecordItem} from "../types";
import {DirectoryActions, DirectoryPhoto, DirectoryTags} from "../DirectoryInfo";
const recordPath = (r:RecordItem) => "/read/" + r.id;
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
    "/directory/archive",
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
    <article className={"record-card " + (list ? "list-card " : "") + (community ? "community-entry" : "")}>
      {showImage && r.directory?.photo && <DirectoryPhoto key={r.id} record={r} />}
      {showImage && !list && r.image && !r.directory?.photo && (
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
        
        {community ? <DirectoryTags record={r} /> : <div className="record-meta">
          <span>
            <Icon size={15} />
            {r.editorialStatus === "authored-practical-guide" ? "Practical guide" : kindLabel[r.kind]}
          </span>
          {r.locality && <span>{r.locality}</span>}
        </div>}
        <h3>
          <Link
            to={recordPath(r)}
            state={{ fromCatalogue, fromHome: location.pathname === "/" }}
          >
            {r.title}
            <ArrowUpRight size={19} />
          </Link>
        </h3>
        {community && (r.locations[0] || r.locality) && <div className="directory-location"><MapPin size={15} aria-hidden="true" /><span>{r.locations[0] || r.locality}</span></div>}
        {description && description !== "Read the original resource from ActForGoa." && (
          <p>
            {r.id === "resource-590480849c"
              ? "A locality-by-locality list of snake rescue volunteers, published in 2018. Contact details need current confirmation."
              : description}
          </p>
        )}
        {community ? <DirectoryActions record={r} /> : <div className="card-bottom">
          <span>{r.topics[0]}</span>
        </div>}

      </div>
    </article>
  );
}
