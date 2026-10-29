"use client";

import { useEffect, useId, useLayoutEffect, useRef, useState } from "react";
import type { ButtonHTMLAttributes, CSSProperties, FocusEvent, KeyboardEvent } from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import type { Variants } from "motion/react";
import { CalendarDays, ChevronDown } from "lucide-react";
import { Calendar, type CalendarDateMatcher } from "../calendar/calendar";
import { motionTokens } from "../lib/motion-tokens";
import styles from "./date-picker.module.css";

export interface DatePickerProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, "value" | "onChange"> {
  label: string;
  value?: Date;
  onChange?: (date: Date | undefined) => void;
  description?: string;
  placeholder?: string;
  minDate?: Date;
  maxDate?: Date;
  disabledDates?: CalendarDateMatcher;
  locale?: string;
  format?: Intl.DateTimeFormatOptions;
  /** Adds a Today button to the calendar header. */
  showToday?: boolean;
}

const monthStart = (date: Date) => new Date(date.getFullYear(), date.getMonth(), 1);
/** Keep an empty or stale controlled value's opening month inside its permitted range. */
const openingDate = (value?: Date, minDate?: Date, maxDate?: Date) => {
  let date = value ?? new Date();
  if (minDate && date.getTime() < minDate.getTime()) date = minDate;
  if (maxDate && date.getTime() > maxDate.getTime()) date = maxDate;
  return monthStart(date);
};
const { spring, duration, ease, blur } = motionTokens;
const instant = { duration: duration.instant };
/** Each part of the date rolls with time: a later date rises from below, an earlier one drops from above. Parts that did not change stay still. */
const valueRoll: Variants = {
  enter: (direction: number) => ({ opacity: 0, y: `${direction * 0.35}em`, filter: `blur(${blur.soft}px)` }),
  center: { opacity: 1, y: 0, filter: "blur(0px)", transition: { duration: duration.standard, ease: ease.enter } },
  exit: (direction: number) => ({ opacity: 0, y: `${direction * -0.3}em`, filter: `blur(${blur.subtle}px)`, transition: { duration: 0.14, ease: ease.standard } }),
};
/** Reduced motion keeps a short crossfade; resting values match the roll so server and client markup agree. */
const valueFade: Variants = { enter: { opacity: 0 }, center: { opacity: 1, y: 0, filter: "blur(0px)", transition: instant }, exit: { opacity: 0, transition: instant } };
/** The footer confirms the pick: new copy rises in with a soft blur while the old line lifts away. */
const statusRise: Variants = {
  enter: { opacity: 0, y: "0.3em", filter: `blur(${blur.soft}px)` },
  center: { opacity: 1, y: 0, filter: "blur(0px)", transition: { duration: duration.standard, ease: ease.enter } },
  exit: { opacity: 0, y: "-0.3em", filter: `blur(${blur.subtle}px)`, transition: { duration: 0.14, ease: ease.standard } },
};

export function DatePicker({ label, value, onChange, description, placeholder = "Select a date", minDate, maxDate, disabledDates, locale = "en-US", format = { month: "short", day: "numeric", year: "numeric" }, showToday, id, className, disabled, ...buttonProps }: DatePickerProps) {
  const generatedId = useId();
  const controlId = id ?? generatedId;
  const dialogId = `${controlId}-calendar`;
  const hintId = description ? `${controlId}-description` : undefined;
  const [open, setOpen] = useState(false);
  const [month, setMonth] = useState(() => openingDate(value, minDate, maxDate));
  const [placement, setPlacement] = useState<CSSProperties>({ position: "fixed", visibility: "hidden" });
  const rootRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const popoverRef = useRef<HTMLDivElement>(null);
  const closeTimer = useRef<number | undefined>(undefined);
  const formatter = new Intl.DateTimeFormat(locale, format);
  const reduce = useReducedMotion() ?? false;
  const time = value?.getTime() ?? null;
  const [previousTime, setPreviousTime] = useState(time);
  const [direction, setDirection] = useState(1);
  if (previousTime !== time) { setPreviousTime(time); setDirection(time === null || previousTime === null || time >= previousTime ? 1 : -1); }
  const shown = value ? formatter.format(value) : placeholder;
  const parts = value ? formatter.formatToParts(value) : [];
  // Parts after a wider or narrower segment move on the same curve the new text arrives on, so they never overlap it.
  const partMotion = reduce ? { duration: 0 } : { duration: duration.standard, ease: ease.enter };

  useEffect(() => {
    const onPointerDown = (event: PointerEvent) => { if (!rootRef.current?.contains(event.target as Node) && !popoverRef.current?.contains(event.target as Node)) { window.clearTimeout(closeTimer.current); setOpen(false); } };
    document.addEventListener("pointerdown", onPointerDown);
    return () => { document.removeEventListener("pointerdown", onPointerDown); window.clearTimeout(closeTimer.current); };
  }, []);

  /** The native Arc surface is portalled so a scrolling parent cannot clip it. */
  useLayoutEffect(() => {
    if (!open) return;
    const place = () => {
      const trigger = triggerRef.current, popover = popoverRef.current;
      if (!trigger || !popover) return;
      const bounds = trigger.getBoundingClientRect();
      const viewportWidth = document.documentElement.clientWidth;
      const viewportHeight = window.innerHeight;
      const width = Math.min(320, viewportWidth - 32), height = popover.offsetHeight;
      const below = bounds.bottom + 8;
      const above = bounds.top - height - 8;
      const top = below + height <= viewportHeight - 16 ? below : above >= 16 ? above : Math.max(16, viewportHeight - height - 16);
      setPlacement({ position: "fixed", left: Math.max(16, Math.min(bounds.left, viewportWidth - width - 16)), right: "auto", top, width, maxHeight: viewportHeight - 32, overflowY: "auto", zIndex: 1100, visibility: "visible", transformOrigin: `22px ${top < bounds.top ? "calc(100% + 8px)" : "-8px"}` });
    };
    place();
    window.addEventListener("resize", place);
    window.addEventListener("scroll", place, true);
    const observer = new ResizeObserver(place);
    if (triggerRef.current) observer.observe(triggerRef.current);
    if (popoverRef.current) observer.observe(popoverRef.current);
    return () => { window.removeEventListener("resize", place); window.removeEventListener("scroll", place, true); observer.disconnect(); };
  }, [open]);

  useEffect(() => {
    if (disabled) { window.clearTimeout(closeTimer.current); setOpen(false); }
  }, [disabled]);

  /** Opening moves focus to the day that owns the tab stop, so arrows work at once; a pointer open shows no ring. */
  useEffect(() => {
    if (open && placement.visibility === "visible") {
      const popover = popoverRef.current;
      const first = popover?.querySelector<HTMLButtonElement>("[data-present] [data-date][tabindex=\"0\"]") ?? popover?.querySelector<HTMLButtonElement>("button:not(:disabled):not([aria-disabled=\"true\"])");
      (first ?? popover)?.focus({ preventScroll: true });
    }
  }, [open, placement.visibility]);

  /** Closing hands focus back to the trigger when it was inside the calendar, so keyboard users never land on the page body. */
  const close = () => {
    window.clearTimeout(closeTimer.current);
    if (popoverRef.current?.contains(document.activeElement)) triggerRef.current?.focus({ preventScroll: true });
    setOpen(false);
  };
  /** The calendar always opens on the month of the current value, or today's month. */
  const show = () => { if (disabled) return; window.clearTimeout(closeTimer.current); setMonth(openingDate(value, minDate, maxDate)); setPlacement({ position: "fixed", visibility: "hidden" }); setOpen(true); };
  /** A picked day lets the highlight glide onto it and the footer confirm it, then the calendar returns to the field. */
  const selectDate = (date: Date | undefined) => {
    onChange?.(date);
    window.clearTimeout(closeTimer.current);
    if (reduce || !date) close();
    else closeTimer.current = window.setTimeout(close, 300);
  };
  const onTriggerKeyDown = (event: KeyboardEvent<HTMLButtonElement>) => {
    if ((event.key === "ArrowDown" || event.key === "Enter" || event.key === " ") && !open) { event.preventDefault(); show(); }
    if (event.key === "Escape") close();
  };
  /** Keep the portal in the field's logical tab order without trapping focus. */
  const onPopoverKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Escape") { event.stopPropagation(); close(); return; }
    if (event.key !== "Tab") return;
    const items = [...(popoverRef.current?.querySelectorAll<HTMLButtonElement>("button:not(:disabled)") ?? [])].filter(item => item.tabIndex >= 0 && !item.closest("[inert]") && item.getClientRects().length > 0);
    if (event.shiftKey && document.activeElement === items[0]) { event.preventDefault(); close(); }
    else if (!event.shiftKey && document.activeElement === items.at(-1)) {
      const pageItems = [...document.querySelectorAll<HTMLElement>('a[href], button:not(:disabled), input:not(:disabled):not([type="hidden"]), select:not(:disabled), textarea:not(:disabled), [tabindex]')].filter(item => item.tabIndex >= 0 && !item.closest("[inert]") && !popoverRef.current?.contains(item) && item.getClientRects().length > 0);
      const index = pageItems.indexOf(triggerRef.current!);
      const next = index >= 0 ? pageItems[index + 1] : undefined;
      close();
      if (next) { event.preventDefault(); next.focus({ preventScroll: true }); }
    }
  };
  /** Tabbing past the popover closes it; focus moving within the field keeps it open. */
  const onBlur = (event: FocusEvent<HTMLDivElement>) => {
    const next = event.relatedTarget as Node | null;
    if (open && next && !rootRef.current?.contains(next) && !popoverRef.current?.contains(next)) { window.clearTimeout(closeTimer.current); setOpen(false); }
  };

  return <div className={[styles.field, className].filter(Boolean).join(" ")} ref={rootRef} onBlur={onBlur}>
    <label className={styles.label} htmlFor={controlId}>{label}</label>
    <div className={styles.anchor} data-open={open || undefined}>
      <button {...buttonProps} ref={triggerRef} id={controlId} type="button" disabled={disabled} aria-haspopup="dialog" aria-controls={open ? dialogId : undefined} aria-expanded={open} aria-describedby={hintId} className={styles.trigger} onClick={() => (open ? close() : show())} onKeyDown={onTriggerKeyDown}>
        <CalendarDays size={16} strokeWidth={1.75} aria-hidden="true" />
        <span className={styles.srOnly}>{shown}</span>
        <span className={styles.valueText} aria-hidden="true">
          <AnimatePresence mode="popLayout" initial={false} custom={1}>
            {value ? <motion.span key="value" className={styles.value} custom={1} variants={reduce ? valueFade : valueRoll} initial="enter" animate="center" exit="exit">
              {parts.map((part, index) => <motion.span key={`${index}-${part.type}`} className={styles.part} layout="position" layoutDependency={time} transition={partMotion}>
                {part.type === "literal" ? <span className={styles.partValue}>{part.value}</span> : <AnimatePresence mode="popLayout" initial={false} custom={direction}><motion.span key={part.value} className={styles.partValue} custom={direction} variants={reduce ? valueFade : valueRoll} initial="enter" animate="center" exit="exit">{part.value}</motion.span></AnimatePresence>}
              </motion.span>)}
            </motion.span> : <motion.span key="placeholder" className={styles.placeholder} custom={-1} variants={reduce ? valueFade : valueRoll} initial="enter" animate="center" exit="exit">{placeholder}</motion.span>}
          </AnimatePresence>
        </span>
        <ChevronDown className={styles.chevron} size={16} strokeWidth={1.75} aria-hidden="true" />
      </button>
      {typeof document !== "undefined" && createPortal(<AnimatePresence>
        {open && <motion.div ref={popoverRef} id={dialogId} className={styles.popover} style={placement} tabIndex={-1} role="dialog" aria-label={`${label} calendar`} onKeyDown={onPopoverKeyDown}
          initial={reduce ? { opacity: 0 } : { opacity: 0, y: -8, scale: .95 }}
          animate={{ opacity: 1, y: 0, scale: 1, transition: reduce ? instant : { ...spring.snappy, opacity: { duration: duration.fast, ease: ease.enter } } }}
          exit={{ opacity: 0, pointerEvents: "none", ...(reduce ? {} : { y: -6, scale: .97 }), transition: { duration: 0.14, ease: ease.standard } }}>
          <Calendar value={value} onChange={selectDate} month={month} onMonthChange={setMonth} minDate={minDate} maxDate={maxDate} disabledDates={disabledDates} locale={locale} showToday={showToday} />
          <div className={styles.footer}><button type="button" onClick={() => selectDate(undefined)} disabled={!value}>Clear</button><span className={styles.status}><AnimatePresence initial={false}><motion.span key={time ?? "none"} variants={reduce ? valueFade : statusRise} initial="enter" animate="center" exit="exit">{value ? `Selected ${formatter.format(value)}` : "Choose a day"}</motion.span></AnimatePresence></span></div>
        </motion.div>}
      </AnimatePresence>, document.body)}
    </div>
    {description && <span id={hintId} className={styles.description}>{description}</span>}
  </div>;
}
