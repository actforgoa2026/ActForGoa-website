# Field guide refinement verification

22 October 2026. Release targets the existing Vercel field-guide preview.

| Before | After | Why |
| --- | --- | --- |
| Boxed hero, repeated bordered cards, heavy input focus | Open paper layout, original photography, fill-only text-field focus | Let Goa and the actual content lead |
| Small topic links and serif headings | Larger bold topic targets and Manrope throughout | Follow the user's explicit typography and hierarchy preferences |
| Filters reset scroll and Back lost loaded results | Query changes preserve position; history restores loaded counts and position | Keep browsing continuous |
| Short homepage | Deterministic mixed feed of all 528 eligible records, 12 at a time, with pause and manual loading | Many useful ways into the collection |
| Reduced menu | Original nine sections, Take action/About dropdowns, responsive Arc menu | Preserve familiar navigation alongside existing shortcuts |
| Phone-heavy community cards | Source biographies, work areas and locality; phone fields and repeated prose numbers hidden | Explain what people do before offering contact details |
| Seven mapped content images | 221 illustrated entries, 864 unique original image files, 868 gallery placements | Keep original stories and their photographs together |

## Evidence

- 15 tests pass: query relevance, semantic index integrity, unique deterministic feed, source preservation, phone presentation including raw landlines, and local image provenance.
- Production build passes. Text and phone arrays in all 600 stored records match the original commit exactly; image fields were added separately.
- Desktop 1440px, desktop breakpoint 1200px, tablet 768px and phone 390px inspected during this refinement. No page overflow found.
- Desktop dropdown arrow navigation focuses its first link; Escape restores trigger focus. Mobile menu Escape closes and restores focus to Open menu. Text fields retain fill-only focus with no outline.
- Query filter click retained 781.5px; expanded search Back restored 21 records and 5437.5px during the initial pass. Latest phone feed article round trip retained exactly 1603.5px. Automatic loading, pause and manual loading were exercised.
- Latest snake detail DOM has zero tel links and no 7+ digit numbers in its text. Reviewer checked 395 known numbers across all 600 presentation records, including the two original prose leaks.
- Original Miramar article gallery inspected on phone with loaded source photos. Local gallery files all resolve; dimensions reserve image space.
- Impeccable final review disposition: ship. Detector has advisory design-system token findings only, including inherited Arc defaults; no hard findings. Changed source has no italic/oblique typography, serif face, or decorative side stripe.

## Limits

Five old act4goa.org image sources have no matching local archive file; their URLs are recorded in article-image-restoration.json. Missing organisation biographies are identified honestly. This is a presentation hide, not an access-control boundary: the original source catalogue and archive intentionally retain phone numbers. Contact forms still prepare email and do not submit to a server. Original actforgoa.org is unchanged.

Fresh review captures are in .impeccable/review/refinement: final-home-desktop.png, final-home-mobile.png, final-feed-desktop.png, final-feed-mobile.png, community-desktop.png, navigation-desktop.png, navigation-mobile.png, gallery-mobile.png.
