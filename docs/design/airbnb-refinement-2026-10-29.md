# Airbnb research and ActForGoa adaptation

The user requested rounder buttons, soft drop shadows, better fonts and hierarchy while keeping green and cream. They selected roomier AI and satellite layouts with secondary details tucked away, and subsequently asked for substantially more map space.

## Primary evidence

- [Airbnb Design: Building a visual language](https://medium.com/airbnb-design/building-a-visual-language-behind-the-scenes-of-our-airbnb-design-system-224748775e4e), Karri Saarinen, 2016. The DLS uses shared, reusable components and unified, universal, iconic and conversational principles. The useful lesson here is consistency across tasks and screens rather than a collection of individually styled pages.
- [Airbnb Design: Working Type](https://medium.com/airbnb-design/working-type-81294544608b), 2018. Cereal was developed with Dalton Maag as functional brand typography. ActForGoa uses the openly licensed [Figtree](https://fontsource.org/fonts/figtree/about) instead of copying Airbnb's proprietary font.
- [Airbnb's current homepage](https://www.airbnb.co.in/?locale=en), visually inspected 29 October 2026. Observed: pill search, circular utility buttons, rounded imagery, generous spacing, restrained heading weights and elevation concentrated on search and floating controls. Computed samples: Cereal variable family, 14px controls at 400–500 weight, pill search radius around 50px, circular icons. These are observations, not a published Airbnb token specification.

## Translation

| Pattern | ActForGoa decision |
| --- | --- |
| Consistent reusable controls | Keep actual Arc and shadcn behavior; tune shared tokens. |
| Friendly functional type | Upright self-hosted Figtree, body 450, labels 600, headings 650. |
| Search as the main task | Raise the homepage and AI composer with a subtle offset shadow. |
| Clear surface hierarchy | Cream canvas, warm white interactive surfaces, green ink. |
| Rounded choices | 14px controls, 20px topic choices, 24px major surfaces; pills only for compact filters/search. |
| Selective depth | Small resting elevation, stronger floating/search shadows; open source/result rows stay open. |
| Content earns the space | Satellite map fills most of the viewport; floating tools, compact header, dates below. |
| Progressive disclosure | Keep provenance, library details, coordinate tools and limitations in labelled disclosures; never conceal current service failures or result caveats. |

Preserve the circular homepage animation and all eight topic icons. No new raster assets, external branding, provider calls or release are required by this visual refinement.
