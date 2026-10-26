import { useLayoutEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";

// Adapted from Dizko's HomeHeroWordWheel: one shared beat, a measured word
// slot, a vertical roll, and enough baseline room to keep descenders intact.
export const HERO_WORDS = ["Volunteer", "Build", "Create", "Recycle", "Culture", "Health"];
export const HERO_BEAT_MS = 4000;
export const HERO_ROLL_MS = 620;

export default function HomeHeroWordWheel({ beat }: { beat: number }) {
  const reducedMotion = useReducedMotion();
  const word = HERO_WORDS[((beat % HERO_WORDS.length) + HERO_WORDS.length) % HERO_WORDS.length];
  const ruler = useRef<HTMLSpanElement>(null);
  const widthRef = useRef(0);
  const [width, setWidth] = useState<number>();

  useLayoutEffect(() => {
    let shrinkTimer: number;
    let live = true;
    const measure = (animate: boolean) => {
      if (!live || !ruler.current) return;
      const next = Math.ceil(ruler.current.getBoundingClientRect().width);
      if (!next) return;
      window.clearTimeout(shrinkTimer);
      // Both words fit while the old one exits. Shrink only after the roll.
      setWidth(animate ? Math.max(next, widthRef.current) : next);
      widthRef.current = next;
      shrinkTimer = window.setTimeout(() => setWidth(next), animate ? HERO_ROLL_MS : 0);
    };
    measure(!reducedMotion);
    const remeasure = () => measure(false);
    if (document.fonts.status !== "loaded") void document.fonts.ready.then(remeasure);
    window.addEventListener("resize", remeasure);
    return () => { live = false; window.clearTimeout(shrinkTimer); window.removeEventListener("resize", remeasure); };
  }, [word, reducedMotion]);

  return <span className="hero-word-slot" aria-hidden="true"
    style={{ width, transitionDuration: reducedMotion ? "0ms" : `${HERO_ROLL_MS}ms` }}>
    <span className="hero-word-ruler" ref={ruler}>{word}</span>
    <AnimatePresence initial={false}>
      <motion.span key={word} className="hero-word"
        initial={{ opacity: 0, y: reducedMotion ? 0 : "0.62em" }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: reducedMotion ? 0 : "-0.62em" }}
        transition={{ duration: reducedMotion ? 0 : HERO_ROLL_MS / 1000, ease: [0.76, 0, 0.24, 1] }}>
        {word}
      </motion.span>
    </AnimatePresence>
  </span>;
}
