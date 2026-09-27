# skom
SKOM is a Christ-centred, community-based organisation working to nurture, protect and empower children aged 5–15 across the islands of Lake Victoria — so every child can learn, grow, stay safe and reach their God-given potential.

## Website (static HTML, Elementor-ready)

- `website/` — the finished static site (deploy this folder). Clean URLs: `/about/`, `/programs/…`, etc.
- `_src/` — page sources. Edit `_src/pages/*.html` or `_src/partials/*`, then run `python _src/build.py`.
- `website/assets/css/styles.css` — all styles (flexbox only, no CSS Grid). The `:root` tokens map to Elementor Global Colors and Fonts.
- `content/` — original photos and videos. Kept locally only, not in this repository: too large for GitHub, and the originals may contain location metadata. Web images are in `website/assets/img/` as WebP, in `-lg` and `-sm` sizes.

Preview locally: `python -m http.server 8765 --directory website`, then open http://localhost:8765

## Elementor mapping
| Site pattern | Elementor |
|---|---|
| `.hero` (photo + gradient + wave) | Container, background image, background overlay, Shape Divider "Waves" |
| `.split`, `.cards` | Flex container (row, wrap, gap) |
| `.stat` | Counter widget |
| `.icon-box`, `.challenge`, `.value` | Icon Box widget |
| `.pillar-card`, `.leader` | Container with heading, text and button |
| `.accordion` | Accordion widget |
| `.gallery` | Basic Gallery or Image widgets |
| `.skom-form` | Elementor Form |
| `.reveal` | Motion Effects → Fade In Up |

Fonts: **Fraunces** (headings) and **DM Sans** (body), both from Google Fonts.
Colours: Deep Blue `#0B2D63`, Vibrant Green `#1C7A3E` / `#2FA85A`, Warm Yellow `#F7B924`, Lake Blue `#1F6FB5`, Cream `#FBF8F1`.

## Waiting on SKOM (search the HTML for `PLACEHOLDER`)
- Phone / WhatsApp number. (Email is live: ssesekidsoutreachministries@gmail.com. Forms currently open the visitor's email app addressed to it; set `data-endpoint` in `_src/partials/form-*.html` to a form service, or use Elementor Forms, for direct sending.)
- Domain. Set `SITE_URL` in `_src/build.py` to enable canonical and og:url tags.
- Social media links, and donation methods.
- Founding year and founding story; target islands and landing sites.
- Designated safeguarding contact; the Child Protection Policy PDF.
- Parent/guardian consent for the published photos of children.
- Real stories for the Stories page.
