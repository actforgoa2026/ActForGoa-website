---
name: ActForGoa for iPhone
description: The Goan Field Guide adapted to native iPhone navigation, adaptive green and paper colours, and upright system text.
colors:
  paper-light: "rgb(96.9% 96.9% 93.3%)"
  paper-dark: "rgb(6.5% 10.5% 9%)"
  ink-light: "rgb(12.5% 23.9% 20.4%)"
  ink-dark: "rgb(92% 95% 90%)"
  tint-light: "rgb(8.6% 24.7% 21.2%)"
  tint-dark: "rgb(66% 85% 71%)"
  secondary-light: "rgb(36% 42% 39%)"
  secondary-dark: "rgb(67% 75% 70%)"
typography:
  display:
    fontFamily: "-apple-system"
    fontWeight: 600
  section:
    fontFamily: "-apple-system"
    fontWeight: 600
  body:
    fontFamily: "-apple-system"
  metadata:
    fontFamily: "-apple-system"
rounded:
  row-photo: "8pt"
  notice-photo: "12pt"
spacing:
  tight: "4pt"
  compact: "8pt"
  related: "12pt"
  notice: "16pt"
  inset: "20pt"
  section: "24pt"
components:
  source-notice:
    rounded: "{rounded.notice-photo}"
    padding: "{spacing.notice}"
  record-row:
    padding: "8pt 0"
  reading-container:
    padding: "{spacing.inset}"
  row-photo:
    rounded: "{rounded.row-photo}"
    height: "170pt"
  detail-photo:
    rounded: "{rounded.notice-photo}"
    height: "230pt"
---

# Design System: ActForGoa for iPhone

## Overview

**Creative North Star: "The Goan Field Guide"**

The native extension inherits the root `DESIGN.md` identity: warm paper, forest green, original Goan photography, calm reading and visible provenance. Native SF text styles, tabs, navigation stacks, search, lists, menus and sheets are the confirmed platform adaptation. The web's typography, yellow search button, hover styling and breakpoints remain web-specific.

This scan-mode record describes the implementation on 22 October 2026. Composition and Operate/Read modes remain in `.impeccable/surfaces/ios-actforgoa-ui-rootview-swift.md`. Root design files are preserved. Frontmatter colours reproduce `Theme.swift`'s UIKit channel values exactly; layout units are iOS points. Text sizes remain semantic and follow Dynamic Type.

## Colors

| `GuideTheme` role | Light / dark character | Application |
| --- | --- | --- |
| `paper` | Warm paper / deep green | Catalogue, reading, guide and template grounds. |
| `ink` | Green ink / pale green-white | Titles and primary reading content. |
| `tint` | Forest green / light leaf green | Actions, links and selected navigation. |
| `secondary` | Quiet green / pale muted green | Summaries, section labels, metadata and caveats. |

`surface` uses `UIColor.secondarySystemGroupedBackground`. Grouped rows, bars, separators and disabled states retain OS styling. The contact count uses system red above its limit. Custom roles branch on light/dark appearance; increased contrast has not been separately verified.

**The Source Proximity Rule.** Keep verification language beside the content it qualifies. Green signals interaction, not verified availability.

## Typography

System text styles and SF Symbols carry the interface. No custom native font is loaded.

| Style | Role |
| --- | --- |
| Large Title, semibold | Entry, guide and About content titles. |
| Title 2, semibold | Mission, article sections, guide major headings and template introduction. |
| Title 3 | Guide summaries; deeper guide headings add semibold weight. |
| Headline | Record names, counts, draft status and first table cells. |
| Body | Reading, template text and ordinary table cells. |
| Subheadline | Summaries, provenance, notices and form guidance. |
| Caption | Metadata, phone caveats and counts; table labels add semibold weight. |
| Footnote | About attribution. |

Titles grow vertically; record summaries stop at three lines. Reading paragraphs add 5 points of line spacing, guide lists and table cells 4. Native navigation titles follow the OS; the captured top-level title is compact.

**The Upright Type Rule.** Imported Markdown removes slanted emphasis while retaining strong emphasis, links and selection. Only actual code blocks use system body monospaced text. Keep all other text upright through weight, semantic size and spacing.

## Layout

Explore, Directory, Library and Community are persistent native tabs with navigation stacks. Details push; focused contact and file-preview tasks use sheets.

Catalogues use inset grouped lists over `paper`, preserving supplied section case. Search occupies the native navigation drawer. Show images enables an adaptive grid: minimum column width 280 points, horizontal spacing 20 and vertical spacing 24. Accessibility text sizes retain the list.

Reading stacks have 20-point padding within a centred maximum width of 680 points. Major groups generally use 24-point spacing and related items 12. The landscape reader retains that maximum width. Tables stack labelled cells vertically, using 20 points between records, 12 between cells and 4 between label and value.

Reading, sharing, phone and section-jump actions commonly set a 44-point minimum height. Starter/topic labels have a 32-point content minimum inside padded native list rows; that is not the complete tap target.

## Elevation & Depth

Custom content is flat, using whole-surface fills, spacing and horizontal separators. There are no custom shadows, blur layers or animation system in the reviewed UI. Bars, sheets and sharing use OS materials and transitions, whose appearance varies by iOS release.

## Shapes

Explicit radii distinguish row photographs from larger detail photographs and notices. Grouped rows, search, toolbar controls and sheets retain native shapes. The Explore river image fills a 190-point-high row; row/detail crops use the frontmatter heights.

**The Structural Line Rule.** Plain horizontal dividers express separation. Decorative side stripes are prohibited on every container.

## Components

### Search and navigation

`TabView`, `NavigationStack`, `.searchable`, `Menu`, `Picker` and `Toggle` supply native controls. Explore results group by People & organisations, Guides & reading, Stories & projects, and About & action, retaining totals and omitting empty groups. Keyword results appear immediately; explicit progress, success or fallback language describes on-device meaning matching. Clear filters, Browse all entries and Show more results provide recovery and continuation.

### Records and source context

`RecordRow` combines headline, caption metadata, summary and optional photograph. Authored results visibly say Practical guide · Draft. Phone actions retain source-age/confirmation notes. `SourceNotice` uses secondary text on a padded, rounded whole surface.

`RecordDetail` preserves original text, dates, documents, source links and related entries. Phone lists reveal five numbers before a disclosure. Original websites open in system Safari presentation; sharing uses the canonical web URL.

### Practical guides and registers

`PracticalGuideView` leads with heading, summary, Draft for review, source-check date and outstanding checks. On this page reveals level-two section jumps; Templates to use exposes local files. Inline citations resolve to native links. Tables repeat each column label above its cell, use headline text for the first cell and body for others, and separate records with plain dividers.

Sources and review links to the official source and verification registers, which share the reader. The documented bundle has five searchable guides beside 600 archived entries, two additional linked registers and 17 templates. Counts describe this build, not fixed layout constraints.

### Local file preview

`LocalGuideFileView` is a sheet with Done, Save a copy to edit, official-form guidance, selectable plain text and Save or share file. `ShareLink` opens the native review sheet. Editing happens after saving a copy; the app has no template editor. Missing files show a native unavailable state and recovery guidance.

### Contact and participation

`ContactView` uses a native form, labelled fields, reason picker and growing message field. Preparation remains disabled until valid, dismisses the keyboard and explicitly states that nothing has been sent. Mail review and copy/share remain user actions. Editing resets preparation; a dirty draft guards dismissal with a discard confirmation.

### Loading and recovery

Opening uses `ProgressView`. Failure offers Try again and Visit ActForGoa. Empty search combines the native unavailable view with broader queries and Browse all entries. Missing records and files have dedicated unavailable states. Implementation does not establish rendered verification for uncaptured states.

### Photography

`LocalPhoto` crops bundled original imagery to fill. Meaningful photos have accessibility labels; duplicate row imagery is hidden when its label is empty. The river appears after useful actions; Community uses the original story image. Preserve raster provenance. Photography below the fold was inspected in source, not the final captures.

## Do's and Don'ts

- Do preserve native controls, adaptive roles, semantic text sizes and vertical reading growth.
- Do keep source caveats, draft status and register links near their content.
- Do retain column labels in stacked table records.
- Do inspect light, dark and large-text renders after visual changes.
- Don't use italic/oblique styling or decorative side stripes.
- Don't imply verified availability, substantive review, completed saving or message delivery through styling.
- Don't replace native navigation with web-shaped controls or freeze text sizes to fit a screenshot.

The independent finish review returns `disposition: ship` for 18 named development-preview captures. `.impeccable/review/documentation.md` records the comparison, directly inspected evidence and preserved metadata drift. Physical installation, hardware accessibility, external handoffs and substantive guide verification remain separate work.
