# Arc Date picker and Calendar

Official free component sources verified on 30 October 2026:

- https://uiarc.dev/r/date-picker.json
- https://uiarc.dev/r/calendar.json

The public registry was opened directly in Chrome. Each source file matched the existing local registry cache by content length and FNV-1a before installation. `source-manifest.json` records the SHA-256 of every exact original source file. Calendar includes the official `lib/use-today.ts` dependency; existing Arc motion tokens, Motion and Lucide packages are reused. No package dependency was added.

The DatePicker keeps the official controlled `Date | undefined` value, `onChange`, label, disabled state, locale, format, disabledDates, showToday, minDate and maxDate API. It preserves Arc's calendar grid, roving focus, day/week/month/year keyboard navigation, month strip, selection motion, date-value transitions, reduced-motion support and CSS appearance.

Local accessibility and integration adaptations:

- The unchanged calendar surface renders through a body portal with fixed positioning. It tracks viewport and ancestor scroll changes, flips above the field when necessary, stays within 16px viewport margins, and scrolls on short screens. Its 1100 stacking level clears both the map controls and expanded map. This prevents clipping inside the satellite side panel.
- Outside-click and blur checks include the portal. Focus waits for visible portal placement; Escape restores it without scrolling, and tabbing past the portal follows the original field's tab order. Dialog/trigger controls are explicitly linked, and focus falls back safely if no selectable day is present. Exiting surfaces stop intercepting pointer events.
- Opening an empty or stale value clamps the initial month to minDate/maxDate. Disabling the field closes its open calendar. Calendar's Today action cannot navigate to a disabled or out-of-range date.
- The existing description-hiding selector uses the field's open state because the surface is now portalled. No alternate control skin was introduced.

Dates are local calendar dates. Integrators should parse `YYYY-MM-DD` with `new Date(year, month - 1, day)` and serialize its local date parts, avoiding UTC conversion shifts.
