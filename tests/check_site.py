"""
Automated checks for mirandabaumann.com.

Run from the repository root:
    python3 -m pip install playwright && python3 -m playwright install chromium
    python3 tests/check_site.py            # local checks only
    python3 tests/check_site.py --links    # also checks that outside links respond
    python3 tests/check_site.py --url https://preview.mirandabaumann-com.pages.dev   # test a deployed copy

Starts a temporary local web server, opens the page in a headless browser,
and reports PASS/FAIL for each check. Screenshots are saved to tests/screenshots/.
"""
import contextlib, functools, http.server, json, os, re, socketserver, sys, threading, urllib.request
from html.parser import HTMLParser
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(ROOT, "tests", "screenshots")
results = []

def check(name, ok, detail=""):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))

def luminance(rgb):
    def ch(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)

def contrast(a, b):
    la, lb = sorted([luminance(a), luminance(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)

def parse_rgb(s):
    return tuple(int(x) for x in re.findall(r"\d+", s)[:3])

@contextlib.contextmanager
def server():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    handler = functools.partial(Quiet, directory=ROOT)
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        t = threading.Thread(target=httpd.serve_forever, daemon=True); t.start()
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
        httpd.shutdown()

def static_checks():
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    lower = html.lower()
    for bad in ["placeholder", "todo", "lorem", "tbd", "academia.edu", "ratemyprofessors", "tel:"]:
        check(f"no '{bad}' in page", bad not in lower)
    check("no phone numbers", not re.search(r"(?<![\w/-])\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)", html))
    check("no street address", not re.search(r"\d+\s+\w+\s+(avenue|street|road|suite|floor)", lower))
    check("fellow dates corrected", "Research Fellow</p>\n        <p class=\"entry-org\">Georgia Department of Behavioral Health and Developmental Disabilities</p>\n        <p class=\"entry-date\">2024–2026" in html)
    check("no dissertation", "dissertation" not in lower)
    check("no Profiles section", 'id="profiles"' not in html)
    check("director start date", "August 2026–present" in html)
    data = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
    check("structured data name matches", data["name"] in html)
    check("structured data title matches", data["jobTitle"] in html)
    check("structured data employer matches", data["worksFor"]["name"] in html)
    check("structured data profiles all visible", all(u.replace("&", "&amp;") in html for u in data["sameAs"]))
    for f in ["favicon.svg", "robots.txt", "sitemap.xml", "_headers", "404.html", "styles.css", "theme.js"]:
        check(f"file present: {f}", os.path.exists(os.path.join(ROOT, f)))

class LinkParser(HTMLParser):
    def __init__(self): super().__init__(); self.links = []; self.ids = set()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a: self.ids.add(a["id"])
        if tag == "a" and "href" in a: self.links.append(a["href"])

def link_checks(external):
    p = LinkParser(); p.feed(open(os.path.join(ROOT, "index.html"), encoding="utf-8").read())
    for href in p.links:
        if href.startswith("#"):
            check(f"anchor target exists {href}", href[1:] in p.ids)
        elif href.startswith("mailto:"):
            check(f"plain mailto {href}", "?" not in href)
    if not external: return
    for href in sorted({h for h in p.links if h.startswith("http")}):
        try:
            req = urllib.request.Request(href, headers={"User-Agent": "Mozilla/5.0 (link check)"})
            code = urllib.request.urlopen(req, timeout=20).status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as e:
            code = str(e)
        # LinkedIn (999), Google Scholar and some publishers (403) refuse automated requests; check those by hand.
        ok = code == 200 or (code in (403, 999) and any(d in href for d in ("linkedin", "doi.org", "scholar.google")))
        check(f"link responds {href}", ok, str(code))

def browser_checks(base):
    os.makedirs(SHOTS, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        for scheme in ["light", "dark"]:
            for name, vp in [("desktop", {"width": 1280, "height": 900}), ("mobile", {"width": 375, "height": 740})]:
                ctx = b.new_context(viewport=vp, color_scheme=scheme)
                pg = ctx.new_page(); errors = []
                pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
                pg.goto(base + "/"); pg.wait_for_load_state("networkidle")
                theme_now = pg.evaluate("getComputedStyle(document.documentElement).backgroundColor")
                expected = "rgb(255, 255, 255)" if scheme == "light" else "rgb(30, 30, 31)"
                check(f"{scheme}/{name}: follows device theme", theme_now == expected, theme_now)
                sw = pg.evaluate("document.documentElement.scrollWidth"); cw = pg.evaluate("document.documentElement.clientWidth")
                check(f"{scheme}/{name}: no horizontal overflow", sw <= cw, f"{sw}>{cw}")
                check(f"{scheme}/{name}: no console errors", not errors, "; ".join(errors))
                bg = parse_rgb(theme_now)
                for sel, minimum in [("body", 7), ("main a", 4.5), (".entry-date", 4.5), (".site-footer", 4.5), (".theme-toggle", 4.5)]:
                    col = parse_rgb(pg.eval_on_selector(sel, "e => getComputedStyle(e).color"))
                    c = contrast(col, bg)
                    check(f"{scheme}/{name}: contrast {sel} ≥ {minimum}", c >= minimum, f"{c:.1f}:1")
                pg.screenshot(path=os.path.join(SHOTS, f"{scheme}-{name}.png"), full_page=True)
                ctx.close()

        # Toggle, keyboard operation, and persistence
        ctx = b.new_context(color_scheme="light"); pg = ctx.new_page(); pg.goto(base + "/")
        btn = pg.locator("#theme-toggle")
        check("toggle visible with JavaScript", btn.is_visible())
        check("toggle has visible label", "Dark theme" in btn.inner_text())
        check("toggle initially off in light", btn.get_attribute("aria-pressed") == "false")
        pg.keyboard.press("Tab")
        check("first Tab reaches skip link", pg.evaluate("document.activeElement.className") == "skip-link")
        btn.focus(); pg.keyboard.press("Enter")
        check("Enter switches to dark", pg.evaluate("document.documentElement.dataset.theme") == "dark" and btn.get_attribute("aria-pressed") == "true")
        outline = pg.evaluate("getComputedStyle(document.activeElement).outlineStyle")
        check("visible focus outline on toggle", outline != "none", outline)
        pg.reload(); pg.wait_for_load_state("domcontentloaded")
        check("dark choice remembered after reload", pg.evaluate("document.documentElement.dataset.theme") == "dark")
        pg.keyboard.press("Tab"); pg.keyboard.press("Tab")
        btn.focus(); pg.keyboard.press("Space")
        check("Space switches back to light", pg.evaluate("document.documentElement.dataset.theme") == "light")
        ctx.close()

        # No flash: saved dark theme applies before first paint
        ctx = b.new_context(color_scheme="light"); pg = ctx.new_page()
        pg.add_init_script("try{localStorage.setItem('theme','dark')}catch(e){}")
        pg.goto(base + "/", wait_until="commit")
        pg.wait_for_selector("body", state="attached")
        check("saved theme set before body renders", pg.evaluate("document.documentElement.dataset.theme") == "dark")
        ctx.close()

        # Storage blocked
        ctx = b.new_context(color_scheme="dark"); pg = ctx.new_page()
        pg.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}})")
        errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(base + "/"); pg.locator("#theme-toggle").click()
        check("works without storage", not errs and pg.evaluate("document.documentElement.dataset.theme") == "light", "; ".join(errs))
        ctx.close()

        # No JavaScript
        ctx = b.new_context(java_script_enabled=False, color_scheme="dark"); pg = ctx.new_page(); pg.goto(base + "/")
        check("no-JS: toggle hidden", not pg.locator("#theme-toggle").is_visible())
        bgc = pg.evaluate("getComputedStyle(document.documentElement).backgroundColor")
        check("no-JS: follows device dark theme", bgc == "rgb(30, 30, 31)", bgc)
        pg.screenshot(path=os.path.join(SHOTS, "nojs-dark.png"))
        ctx.close()

        # Headings
        ctx = b.new_context(); pg = ctx.new_page(); pg.goto(base + "/")
        levels = pg.eval_on_selector_all("h1,h2,h3", "els => els.map(e => +e.tagName[1])")
        check("one h1", levels.count(1) == 1)
        check("no skipped heading levels", all(b2 - a2 <= 1 for a2, b2 in zip(levels, levels[1:])), str(levels))
        ctx.close()
        b.close()

if __name__ == "__main__":
    static_checks()
    link_checks("--links" in sys.argv)
    if "--url" in sys.argv:
        browser_checks(sys.argv[sys.argv.index("--url") + 1].rstrip("/"))
    else:
        with server() as base:
            browser_checks(base)
    failed = results.count(False)
    print(f"\n{len(results) - failed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
