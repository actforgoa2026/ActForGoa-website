import { articlePhoto } from "../article-photos";
import { Link, useLocation } from "react-router-dom";
import { MapPin } from "lucide-react";
import { communityDescription } from "../public-record";
import { type RecordItem } from "../types";
import {DirectoryActions, DirectoryPhoto, DirectoryTags} from "../DirectoryInfo";
import {CurationStar} from "../TeamAccess";
const recordPath = (r: RecordItem) => "/read/" + r.id;
const formatDate = (value: string) => {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
};

export function RecordCard({
  record: r,
  list = false,
  showImage = true,
  compact = false,
}: {
  record: RecordItem;
  list?: boolean;
  showImage?: boolean;
  compact?: boolean;
}) {
  const location = useLocation();
  const fromCatalogue = [
    "/",
    "/search",
    "/library",
    "/directory",
    "/directory/archive",
    "/stories",
    "/blog",
  ].includes(location.pathname) || location.pathname.startsWith("/topics/");
  const community = r.kind === "organisation" || r.kind === "contact";
  const description = community ? communityDescription(r) : (!articlePhoto(r) ? r.summary : "");
  const photo = articlePhoto(r);
  if (community && compact) return <article data-record-id={r.id} className="record-card compact-contact">
    <h3><Link to={recordPath(r)} state={{fromCatalogue:true}}>{r.title}</Link></h3>
    {(r.locality || r.locations[0]) && <span className="directory-location"><MapPin size={15} aria-hidden="true"/>{r.locality || r.locations[0]}</span>}
  </article>;
  return (
    <article data-record-id={r.id} className={"record-card " + (list ? "list-card " : "") + (community ? "community-entry" : "")}>
      {showImage && r.directory?.photo && <DirectoryPhoto key={r.id} record={r} />}
      {showImage && !list && photo && !r.directory?.photo && (
        <Link
          to={recordPath(r)}
          state={{ fromCatalogue, fromHome: location.pathname === "/" }}
          tabIndex={-1}
          aria-hidden="true"
          className="card-image"
        >
          <img src={photo!.src} alt="" loading="lazy" width={800} height={500} />
        </Link>
      )}
      <div className="card-content">
        {showImage && !list && photo?.credit && <div className="card-photo-credit"><a href={photo.source}>{photo.credit}</a> · <a href={photo.licenseUrl}>{photo.license}</a></div>}
        {community ? <DirectoryTags record={r} /> : r.editorialStatus === "authored-practical-guide" ? <div className="record-meta"><span>Practical guide · Draft</span></div> : null}
        {community && <div className="record-meta">{r.publishedAt && <time dateTime={r.publishedAt}>{formatDate(r.publishedAt)}</time>}<span>Archived listing · availability unconfirmed</span></div>}
        <div className="curation-heading"><h3>
          <Link
            to={recordPath(r)}
            state={{ fromCatalogue, fromHome: location.pathname === "/" }}
          >
            {r.title}
          </Link>
        </h3>{r.kind !== "page" && <CurationStar recordId={r.id} title={r.title}/>}</div>
        {community && (r.locations[0] || r.locality) && <div className="directory-location"><MapPin size={15} aria-hidden="true" /><span>{r.locations[0] || r.locality}</span></div>}
        {description && description !== "Read the original resource from ActForGoa." && (
          <p>
            {r.id === "resource-590480849c"
              ? "A locality-by-locality list of snake rescue volunteers, published in 2018. Contact details need current confirmation."
              : description}
          </p>
        )}
        {community ? <DirectoryActions record={r} /> : null}

      </div>
    </article>
  );
}
