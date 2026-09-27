"""
SKOM static site builder.

Assembles every page in _src/pages/*.html with the shared header/footer and
expands a few shorthand tags, then writes clean-URL folders into /website.

  [[img name|alt text|class|eager|sizes]]  -> responsive <img> (lg/sm WebP)
  [[icon name]]                            -> inline SVG icon
  [[form contact|partner|support]]         -> shared form partial

Run:  python _src/build.py
"""
import re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
OUT = ROOT / "website"
IMG = OUT / "assets" / "img"

# Set this once the domain is confirmed (e.g. "https://www.example.org").
# While empty, canonical/og:url tags are omitted rather than guessed.
SITE_URL = ""

SITE_NAME = "Ssesse Kids Outreach Ministries (SKOM)"

NAV = [
    ("home", "Home", "/"),
    ("about", "About", "/about/"),
    ("programs", "Programs", "/programs/"),
    ("impact", "Impact", "/impact/"),
    ("stories", "Stories", "/stories/"),
    ("partner", "Partner With Us", "/partner/"),
    ("contact", "Contact", "/contact/"),
]
PROGRAM_LINKS = [
    ("/programs/learning-skills/", "Learning &amp; Skills"),
    ("/programs/well-being/", "Well-being"),
    ("/programs/child-protection/", "Child Protection"),
    ("/programs/community-engagement/", "Family &amp; Community"),
]

# ---------------------------------------------------------------- icons ----
ICONS = {
    "book": '<path d="M2 4h6a4 4 0 0 1 4 4v12a3 3 0 0 0-3-3H2z"/><path d="M22 4h-6a4 4 0 0 0-4 4v12a3 3 0 0 1 3-3h7z"/>',
    "heart": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "waves": '<path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/>',
    "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "sprout": '<path d="M7 20h10"/><path d="M10 20c5.5-2.5.8-6.4 3-10"/><path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z"/><path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z"/>',
    "church": '<path d="M10 9h4"/><path d="M12 7v5"/><path d="M14 22v-4a2 2 0 0 0-4 0v4"/><path d="M18 22V5.6a1 1 0 0 0-.55-.9L12.9 2.45a2 2 0 0 0-1.8 0L6.55 4.7A1 1 0 0 0 6 5.6V22"/><path d="m18 7 3.45 1.7a1 1 0 0 1 .55.9V20a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-9.4a1 1 0 0 1 .55-.9L6 7"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/>',
    "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
    "apple": '<path d="M12 20.94c1.5 0 2.75 1.06 4 1.06 3 0 6-8 6-12.22A4.91 4.91 0 0 0 17 5c-2.22 0-4 1.44-5 2-1-.56-2.78-2-5-2a4.9 4.9 0 0 0-5 4.78C2 14 5 22 8 22c1.25 0 2.5-1.06 4-1.06Z"/><path d="M10 2c1 .5 2 2 2 5"/>',
    "droplet": '<path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z"/>',
    "smile": '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><path d="M9 9h.01M15 9h.01"/>',
    "ball": '<circle cx="12" cy="12" r="10"/><path d="m12 7 4 3-1.5 5h-5L8 10z"/><path d="M12 2v5M16 10l5-1.5M14.5 15l3 4.5M9.5 15l-3 4.5M8 10 3 8.5"/>',
    "pencil": '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
    "wrench": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>',
    "bulb": '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    "home": '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
    "scale": '<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>',
    "ban": '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/>',
    "anchor": '<circle cx="12" cy="5" r="3"/><path d="M12 22V8"/><path d="M5 12H2a10 10 0 0 0 20 0h-3"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M16 13H8M16 17H8M10 9H8"/>',
    "building": '<rect width="16" height="20" x="4" y="2" rx="2"/><path d="M9 22v-4h6v4M8 6h.01M16 6h.01M12 6h.01M12 10h.01M12 14h.01M16 10h.01M16 14h.01M8 10h.01M8 14h.01"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    "megaphone": '<path d="m3 11 18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/>',
    "calendar": '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "eye": '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4M12 17h.01"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "music": '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>',
    "cross": '<path d="M12 2v20M6 8h12"/>',
    "award": '<circle cx="12" cy="8" r="6"/><path d="M15.48 12.89 17 22l-5-3-5 3 1.52-9.11"/>',
    "checkcircle": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "hand": '<path d="M18 11V6a2 2 0 0 0-4 0v5"/><path d="M14 10V4a2 2 0 0 0-4 0v2"/><path d="M10 10.5V6a2 2 0 0 0-4 0v8"/><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/>',
    "island": '<path d="M2 20c2 0 2-1.5 4-1.5S8 20 10 20s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><path d="M12 17c0-4 .5-7 3-10"/><path d="M15 7c-2-1-5-1-7 1 2 0 4 0 5 1"/><path d="M15 7c1-2 4-3 6-2-1 1-3 2-4 2"/><path d="M7 17h10"/>',
    "quote": '<path d="M3 21c3 0 7-1 7-8V5c0-1.25-.76-2-2-2H4c-1.25 0-2 .75-2 1.97V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .01-1 1.03V20c0 1 0 1 1 1z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.76-2-2-2h-4c-1.25 0-2 .75-2 1.97V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z"/>',
}


def icon(name, cls="icon"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true" focusable="false">{ICONS[name]}</svg>')


# ---------------------------------------------------------------- images ---
_dims = {}


def dims(fn):
    if fn not in _dims:
        _dims[fn] = Image.open(IMG / fn).size
    return _dims[fn]


def img(name, alt, cls="", eager="", sizes=""):
    lg, sm = f"{name}-lg.webp", f"{name}-sm.webp"
    (lw, lh), (sw, _) = dims(lg), dims(sm)
    sizes = sizes or "(max-width: 900px) 100vw, 50vw"
    load = 'loading="eager" fetchpriority="high"' if eager == "eager" else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="/assets/img/{lg}" srcset="/assets/img/{sm} {sw}w, /assets/img/{lg} {lw}w" '
            f'sizes="{sizes}" width="{lw}" height="{lh}" alt="{alt}" {load} decoding="async">')


def expand(html):
    html = re.sub(r"\[\[img ([^\]]+)\]\]", lambda m: img(*[p.strip() for p in m.group(1).split("|")]), html)
    html = re.sub(r"\[\[icon ([a-z]+)(?: ([a-z-]+))?\]\]",
                  lambda m: icon(m.group(1), m.group(2) or "icon"), html)
    html = re.sub(r"\[\[wave ([#\w-]+)\]\]", lambda m: (
        '<div class="wave" aria-hidden="true"><svg viewBox="0 0 1440 90" preserveAspectRatio="none">'
        f'<path fill="{m.group(1)}" d="M0 58c120-26 240-40 360-30s240 44 360 44 240-34 360-44 240 4 360 30V90H0z"/>'
        '</svg></div>'), html)
    html = re.sub(r"\[\[form ([a-z]+)\]\]",
                  lambda m: expand((SRC / "partials" / f"form-{m.group(1)}.html").read_text(encoding="utf-8")), html)
    return html


# ---------------------------------------------------------------- layout ---
def header(active):
    items = []
    for key, label, href in NAV:
        cur = ' aria-current="page"' if key == active else ""
        if key == "programs":
            sub = "".join(f'<li><a href="{h}">{l}</a></li>' for h, l in PROGRAM_LINKS)
            items.append(
                f'<li class="has-sub"><a href="{href}"{cur}>{label}</a>'
                f'<button class="sub-toggle" type="button" aria-expanded="false" aria-controls="sub-programs">'
                f'<span class="sr-only">Show program pages</span>'
                f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m6 9 6 6 6-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>'
                f'<ul class="sub-menu" id="sub-programs">'
                f'<li><a href="/programs/">All four pillars</a></li>{sub}</ul></li>')
        else:
            items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    tpl = (SRC / "partials" / "header.html").read_text(encoding="utf-8")
    return tpl.replace("{{NAV_ITEMS}}", "\n        ".join(items))


def head(meta):
    title = meta["title"]
    desc = meta["description"]
    path = meta["path"]
    canon = f'\n  <link rel="canonical" href="{SITE_URL}/{path}">' if SITE_URL else ""
    ogurl = f'\n  <meta property="og:url" content="{SITE_URL}/{path}">' if SITE_URL else ""
    ogimg = f"{SITE_URL}/assets/img/og-skom-children-janna-island.jpg"
    return f"""<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <script>document.documentElement.classList.add("js")</script>
  <title>{title}</title>
  <meta name="description" content="{desc}">{canon}
  <meta name="theme-color" content="#0B2D63">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">{ogurl}
  <meta property="og:image" content="{ogimg}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Children and adult leaders gathered outdoors in the Ssese Islands, Uganda">
  <meta property="og:locale" content="en_GB">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/assets/img/skom-logo.png" type="image/png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,400&family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,500;1,9..144,600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/styles.css">
  <script src="/assets/js/main.js" defer></script>
</head>
<body class="page-{meta['nav']}">
<a class="skip-link" href="#main">Skip to main content</a>
"""


def parse(src):
    m = re.match(r"\s*<!--(.*?)-->\s*(.*)", src, re.S)
    meta = {}
    for line in m.group(1).strip().splitlines():
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    return meta, m.group(2)


def build():
    footer = expand((SRC / "partials" / "footer.html").read_text(encoding="utf-8"))
    for page in sorted((SRC / "pages").glob("*.html")):
        meta, body = parse(page.read_text(encoding="utf-8"))
        html = head(meta) + expand(header(meta["nav"])) + '\n<main id="main">\n' + expand(body) + "\n</main>\n" + footer + "\n</body>\n</html>\n"
        target = OUT / meta["path"] / "index.html" if meta["path"] else OUT / "index.html"
        if meta["path"].endswith(".html"):
            target = OUT / meta["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
        print("built", target.relative_to(ROOT))


if __name__ == "__main__":
    build()
