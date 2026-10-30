import { useEffect, useRef, useState, type ReactNode } from "react";
import { useReducedMotion } from "motion/react";
import { ChevronLeft, ChevronRight, Pause, Play } from "lucide-react";
import { Button } from "./components/arc/button/button";
import photos from "./content/hero-photos.json";

const PHOTO_INTERVAL_MS = 8000;

export default function HomeCarousel({ children }: { children: ReactNode }) {
  const [slide, setSlide] = useState(0);
  const [paused, setPaused] = useState(false);
  const [hovered, setHovered] = useState(false);
  const [visible, setVisible] = useState(true);
  const [inView, setInView] = useState(false);
  const [loaded, setLoaded] = useState<number[]>([]);
  const [failed, setFailed] = useState<number[]>([]);
  const reducedMotion = useReducedMotion();
  const root = useRef<HTMLElement>(null);
  const pointer = useRef<{ x: number; y: number } | null>(null);
  const available = photos.map((_, index) => index).filter((index) => !failed.includes(index));
  const wrap = (value: number, length: number) => ((value % length) + length) % length;
  const shown = available[wrap(slide, available.length)];
  const playing = !paused && !reducedMotion;
  const canAdvance = available.length > 1;

  useEffect(() => {
    const update = () => setVisible(document.visibilityState === "visible");
    update();
    document.addEventListener("visibilitychange", update);
    const observer = new IntersectionObserver(([entry]) => setInView(entry.isIntersecting), { threshold: 0.25 });
    if (root.current) observer.observe(root.current);
    return () => { document.removeEventListener("visibilitychange", update); observer.disconnect(); };
  }, []);

  useEffect(() => {
    if (!canAdvance || !playing || hovered || !visible || !inView) return;
    const next = available[wrap(slide + 1, available.length)];
    if (available.length && !loaded.includes(next)) return;
    const timer = window.setTimeout(() => setSlide((current) => current + 1), PHOTO_INTERVAL_MS);
    return () => window.clearTimeout(timer);
  }, [slide, playing, hovered, visible, inView, loaded, failed]);

  function advance(direction: number) {
    setPaused(true);
    if (canAdvance) setSlide((current) => current + direction);
  }

  return (
    <section ref={root} className="home-hero home-carousel shell" aria-label="For the Goa we love" aria-roledescription="carousel"
      onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)}
      onPointerDown={(event) => {
        if (event.pointerType === "touch" && !(event.target as HTMLElement).closest("input, textarea, button, a")) {
          pointer.current = { x: event.clientX, y: event.clientY };
        }
      }}
      onPointerCancel={() => { pointer.current = null; }}
      onPointerUp={(event) => {
        const start = pointer.current;
        pointer.current = null;
        if (start && Math.abs(event.clientX - start.x) > 40 && Math.abs(event.clientY - start.y) < 40) {
          advance(event.clientX < start.x ? 1 : -1);
        }
      }}
      onFocusCapture={(event) => {
        const target = event.target as HTMLElement;
        // Route announcements focus the heading programmatically. Only actual
        // interactive controls pause the hero, so arrival still starts it.
        if (target.closest("a, button, input, textarea, select") && !target.closest("[data-carousel-rotation]")) setPaused(true);
      }}>
      <div className="home-carousel-images">
        {photos.map((photo, index) => (
          <div key={photo.id} className="home-carousel-slide" data-active={index === shown}
            role="group" aria-roledescription="slide" aria-label={`${index + 1} of ${photos.length}`}
            aria-hidden={index !== shown}>
            <img src={photo.src} srcSet={photo.srcSet}
              sizes="(max-width: 620px) 100vw, (max-width: 1150px) calc(100vw - 64px), (max-width: 1416px) calc(100vw - 96px), 1320px"
              alt={photo.alt} width={photo.width} height={photo.height}
              fetchPriority={index === 0 ? "high" : "low"} decoding="async"
              style={{ objectPosition: photo.position }}
              onLoad={() => setLoaded((current) => current.includes(index) ? current : [...current, index])}
              onError={() => setFailed((current) => current.includes(index) ? current : [...current, index])} />
          </div>
        ))}
        {!available.length && <p className="home-carousel-unavailable">For the Goa we love.</p>}
      </div>
      <div className="home-hero-shade" aria-hidden="true" />
      <div className="home-hero-content">
        {children}
      </div>
      <div className="home-carousel-footer">
        <div className="home-carousel-caption" aria-live={playing ? "off" : "polite"} aria-atomic="true">
          {photos[shown] ? <>
            <a href={photos[shown].href}>{photos[shown].caption}</a>
            {photos[shown].licenseUrl && <span className="home-photo-credit">
              © {photos[shown].credit} · <a href={photos[shown].licenseUrl}>{photos[shown].license}</a> · cropped
            </span>}
          </> : <span>ActForGoa</span>}
        </div>
        <div className="home-carousel-controls">
          <Button variant="ghost" size="sm" onClick={() => advance(-1)} disabled={!canAdvance} aria-label="Previous photo"><ChevronLeft size={18} aria-hidden="true" /></Button>
          <span className="home-carousel-count" aria-hidden="true">{available.indexOf(shown) + 1} / {available.length}</span>
          <Button variant="ghost" size="sm" onClick={() => advance(1)} disabled={!canAdvance} aria-label="Next photo"><ChevronRight size={18} aria-hidden="true" /></Button>
          {!reducedMotion && <Button variant="ghost" size="sm" data-carousel-rotation onClick={() => setPaused(!paused)} disabled={!canAdvance}
            aria-label={playing ? "Pause photo carousel" : "Play photo carousel"}>
            {playing ? <Pause size={16} aria-hidden="true" /> : <Play size={16} aria-hidden="true" />}
          </Button>}
        </div>
      </div>
    </section>
  );
}
