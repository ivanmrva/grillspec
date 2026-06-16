#!/usr/bin/env python3
# gen_docsite.py - deterministic projection of spec/ into a browsable static HTML site.
# Pure transform, stdlib only, no model: parse markdown -> HTML, anchor & cross-link every stable ID,
# render Mermaid fences and GFM tables nicely, build a navigable sidebar. Byte-stable across runs
# (sorted ordering, no timestamps) so it slots into CI and produces reviewable diffs.
#
# It reuses lint_spec.py's TYPES + PREFIX_OWNER at runtime (like gen_depgraph.py) so ID detection and
# the "where is an ID defined" rules can never drift from the linter.
#
#   python3 tools/gen_docsite.py [spec_dir] [out_dir]      # default: spec  docs-site
#
# Exit 0 on success. Stdlib only.
import os, re, sys, ast, html, posixpath, pathlib, shutil

HERE = pathlib.Path(__file__).resolve().parent
SPEC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "spec")
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "docs-site")
MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.esm.min.mjs"

if not SPEC.exists():
    print("no spec/ dir at", SPEC); sys.exit(2)

# ── conventions, read from the linter so they can't drift ──────────────────────────────────────────
def load_linter_tables():
    lint = HERE / "lint_spec.py"
    src = lint.read_text(encoding="utf-8")
    types = re.search(r'^TYPES\s*=\s*"([^"]+)"', src, re.M).group(1)
    owner = ast.literal_eval(re.search(r"^PREFIX_OWNER\s*=\s*(\{.*?\})", src, re.S | re.M).group(1))
    return types, owner

TYPES, PREFIX_OWNER = load_linter_tables()
IDCORE = r"(?:" + TYPES + r")-[A-Za-z0-9._-]*[A-Za-z0-9]"
ID_RE = re.compile(r"(?<![A-Za-z0-9-])" + IDCORE)
# definition surfaces (ported verbatim from lint_spec.py so anchors land where the linter says an ID is defined)
DEF1 = re.compile(r"^\s*[-*#]*\s*\|?\s*\**(" + IDCORE + r")\b")
DEF2 = re.compile(r"\bid:\s*(" + IDCORE + r")\b", re.I)
DEF3 = re.compile(r"(?:^|[·;:,|←→⟵⟶])\s*[*`_]*\s*(" + IDCORE + r")\s+[A-Z]")

# friendly labels for the nav tree (path -> title). Mirrors repo-layout.md.
AREA_TITLES = {
    "01-discovery": "Discovery", "02-product": "Product", "02-product/vision": "Vision",
    "02-product/customers": "Customers", "02-product/market": "Market", "02-product/goals": "Goals",
    "03-constraints": "Constraints", "03-system-context": "System context", "04-domain": "Domain",
    "04-domain/ddd": "Domain model (DDD)", "05-requirements": "Requirements",
    "05-requirements/functional": "Functional", "05-requirements/quality": "Quality (NFR/ASR)",
    "05-requirements/data": "Data", "05-requirements/integration": "Integration",
    "05-requirements/security": "Security", "05-requirements/ux": "UX",
    "05-requirements/design-system": "Design system", "05-requirements/compliance": "Compliance",
    "05-requirements/ml": "ML", "06-commercial": "Commercial", "07-gtm": "Go-to-market",
    "08-growth": "Growth", "09-solution": "Solution", "09-solution/arch": "Architecture",
    "09-solution/data": "Data architecture", "09-solution/api": "API contracts",
    "09-solution/security": "Security architecture", "09-solution/infra-ops": "Infra & ops",
    "09-solution/observability": "Observability", "09-solution/test": "Test strategy",
    "09-solution/impl": "Implementation design", "09-solution/ml": "ML architecture",
    "10-delivery": "Delivery", "10-delivery/conventions": "Conventions", "10-delivery/tasks": "Tasks",
    "10-delivery/verification": "Verification", "10-delivery/operations": "Operations", "adr": "ADRs",
}

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def slug(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"[^A-Za-z0-9 _-]", "", s).strip().lower()
    return re.sub(r"[\s_]+", "-", s) or "section"

def relhref(here_dir, target):
    return posixpath.relpath(target, here_dir) if here_dir else target

def out_path(rel_md):
    return rel_md[:-3] + ".html" if rel_md.endswith(".md") else rel_md + ".html"

# ── pass 1: index every file, its title, and where each ID is authoritatively defined ──────────────
def in_owner_area(tok, r):
    owner = PREFIX_OWNER.get(tok.split("-")[0].upper())
    return bool(owner) and (r == owner or r.startswith(owner + "/"))

md_files = sorted(p for p in SPEC.rglob("*.md") if p.is_file() and p.name != ".gitkeep")
rel = lambda p: p.relative_to(SPEC).as_posix()

pages = []        # list of (rel_md, out_html, title, text)
defs = {}         # ID -> out_html where it is defined
titles = {}       # out_html -> title

for p in md_files:
    r = rel(p)
    txt = p.read_text(encoding="utf-8")
    out_html = out_path(r)
    # title = first ATX H1, else a humanized filename
    title = None
    for ln in txt.splitlines():
        m = re.match(r"^#\s+(.*)", ln)
        if m:
            title = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            break
    if not title:
        title = re.sub(r"[-_]", " ", os.path.basename(r)[:-3]).strip().title()
    pages.append((r, out_html, title, txt))
    titles[out_html] = title
    if os.path.basename(r) == "traceability.md":
        continue  # the matrix references IDs, never defines them
    for ln in txt.splitlines():
        m = DEF1.match(ln)
        if m:
            defs.setdefault(m.group(1), out_html)
        for m in DEF2.finditer(ln):
            defs.setdefault(m.group(1), out_html)
        for m in DEF3.finditer(ln):
            if in_owner_area(m.group(1), r):
                defs.setdefault(m.group(1), out_html)
    # ADR ids are defined by their filename
    mb = re.match(r"(ADR-[A-Za-z][A-Za-z0-9]*-\d+)", os.path.basename(r))
    if (r.startswith("adr/") or "/adr/" in r) and mb:
        defs.setdefault(mb.group(1), out_html)

# ── markdown -> HTML (focused on the constructs the spec format actually uses) ──────────────────────
def inline(text, ctx):
    prot = []
    def stash(h):
        prot.append(h); return "\x00%d\x00" % (len(prot) - 1)
    s = esc(text)
    s = re.sub(r"`([^`]+)`", lambda m: stash("<code>%s</code>" % m.group(1)), s)
    def link(m):
        label, url = m.group(1), m.group(2).strip()
        a, _, anchor = url.partition("#")
        if not (a.startswith(("http://", "https://", "mailto:")) or a == ""):
            if a.endswith(".md"):
                a = a[:-3] + ".html"
        href = a + (("#" + anchor) if anchor else "")
        return stash('<a href="%s">%s</a>' % (href, label))
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, s)
    # stable-ID linkification (skips the stashed code spans / links — IDs need a TYPE- prefix)
    placed, here = ctx["placed"], ctx["dir"]
    def idrepl(m):
        tok = m.group(0)
        tgt = defs.get(tok)
        if tgt is None:
            return '<span class="id id-unknown" title="not defined in spec">%s</span>' % tok
        if tgt == ctx["page"] and tok not in placed:
            placed.add(tok)
            return '<a id="%s" class="id id-def" href="#%s">%s</a>' % (tok, tok, tok)
        href = ("#" + tok) if tgt == ctx["page"] else (relhref(here, tgt) + "#" + tok)
        return '<a class="id id-ref" href="%s">%s</a>' % (href, tok)
    s = ID_RE.sub(lambda m: stash(idrepl(m)), s)
    s = re.sub(r"\*\*([^*]+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*\s][^*]*?)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r'(?<![">\w])(https?://[^\s<]+)', lambda m: '<a href="%s">%s</a>' % (m.group(1), m.group(1)), s)
    return re.sub(r"\x00(\d+)\x00", lambda m: prot[int(m.group(1))], s)

LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
TABLE_SEP = re.compile(r"^\s*\|?(\s*:?-{1,}:?\s*\|)+\s*:?-{1,}:?\s*\|?\s*$")
HR_RE = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")

def parse_blocks(lines, ctx):
    out, i, n = [], 0, len(lines)
    while i < n:
        ln = lines[i]
        # blank
        if ln.strip() == "":
            i += 1; continue
        # HTML comment (scope header -> badges; others dropped)
        if ln.lstrip().startswith("<!--"):
            buf = []
            while i < n:
                buf.append(lines[i])
                if "-->" in lines[i]:
                    i += 1; break
                i += 1
            block = "\n".join(buf)
            m = re.search(r"scope:(.*?)\|\s*excludes:(.*?)\|\s*format:(.*?)-->", block, re.S | re.I)
            if m:
                badges = "".join(
                    '<span class="badge"><b>%s</b> %s</span>' % (k, esc(v.strip()))
                    for k, v in zip(("scope", "excludes", "format"), m.groups()))
                out.append('<div class="scopebar">%s</div>' % badges)
            continue
        # fenced code
        mf = re.match(r"^(\s*)(`{3,}|~{3,})(.*)$", ln)
        if mf:
            fence, info = mf.group(2), mf.group(3).strip()
            i += 1; body = []
            while i < n and not re.match(r"^\s*" + fence[0] + r"{%d,}\s*$" % len(fence), lines[i]):
                body.append(lines[i]); i += 1
            i += 1  # closing fence
            code = "\n".join(body)
            if info.lower().startswith("mermaid"):
                out.append('<div class="mermaid">%s</div>' % esc(code))
            else:
                cls = ' class="language-%s"' % esc(info) if info else ""
                out.append("<pre><code%s>%s</code></pre>" % (cls, esc(code)))
            continue
        # heading
        mh = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if mh:
            lvl, body = len(mh.group(1)), inline(mh.group(2).strip(), ctx)
            sid = slug(mh.group(2))
            out.append('<h%d id="%s">%s<a class="anchor" href="#%s">#</a></h%d>'
                       % (lvl, sid, body, sid, lvl))
            i += 1; continue
        # horizontal rule
        if HR_RE.match(ln):
            out.append("<hr>"); i += 1; continue
        # table: a pipe row immediately followed by a separator row
        if "|" in ln and i + 1 < n and TABLE_SEP.match(lines[i + 1]):
            header = [c.strip() for c in ln.strip().strip("|").split("|")]
            aligns = []
            for c in lines[i + 1].strip().strip("|").split("|"):
                c = c.strip()
                aligns.append("center" if c.startswith(":") and c.endswith(":")
                              else "right" if c.endswith(":") else "left")
            i += 2; rows = []
            while i < n and "|" in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            t = ['<div class="tablewrap"><table><thead><tr>']
            for k, c in enumerate(header):
                a = aligns[k] if k < len(aligns) else "left"
                t.append('<th style="text-align:%s">%s</th>' % (a, inline(c, ctx)))
            t.append("</tr></thead><tbody>")
            for row in rows:
                t.append("<tr>")
                for k in range(len(header)):
                    c = row[k] if k < len(row) else ""
                    a = aligns[k] if k < len(aligns) else "left"
                    t.append('<td style="text-align:%s">%s</td>' % (a, inline(c, ctx)))
                t.append("</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t)); continue
        # blockquote
        if ln.lstrip().startswith(">"):
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            out.append("<blockquote>%s</blockquote>" % parse_blocks(buf, ctx))
            continue
        # list (gather consecutive item lines, build nested by indent)
        if LIST_RE.match(ln):
            items = []
            while i < n and LIST_RE.match(lines[i]):
                m = LIST_RE.match(lines[i])
                items.append((len(m.group(1)), bool(re.match(r"\d", m.group(2))), m.group(3)))
                i += 1
            def build(j, indent):
                tag = "ol" if items[j][1] else "ul"
                buf = ["<%s>" % tag]
                while j < len(items) and items[j][0] >= indent:
                    if items[j][0] > indent:
                        j -= 1  # safety; treat as same level
                    buf.append("<li>%s" % inline(items[j][2], ctx))
                    if j + 1 < len(items) and items[j + 1][0] > indent:
                        child, j = build(j + 1, items[j + 1][0])
                        buf.append(child)
                    else:
                        j += 1
                    buf.append("</li>")
                buf.append("</%s>" % tag)
                return "".join(buf), j
            html_list, _ = build(0, items[0][0])
            out.append(html_list); continue
        # paragraph
        buf = []
        while i < n and lines[i].strip() and not (
            re.match(r"^(#{1,6})\s", lines[i]) or LIST_RE.match(lines[i]) or HR_RE.match(lines[i])
            or lines[i].lstrip().startswith((">", "<!--")) or re.match(r"^\s*(`{3,}|~{3,})", lines[i])
            or ("|" in lines[i] and i + 1 < n and TABLE_SEP.match(lines[i + 1]))):
            buf.append(lines[i]); i += 1
        out.append("<p>%s</p>" % inline(" ".join(b.strip() for b in buf), ctx))
    return "\n".join(out)

def render_markdown(text, out_html):
    ctx = {"page": out_html, "dir": posixpath.dirname(out_html), "placed": set()}
    return parse_blocks(text.splitlines(), ctx)

# ── nav (flat grouping keyed by directory — clearer than a recursive tree for a spec) ───────────────
def nav_html(here_dir, current):
    groups = {}  # dirpath -> list of (out_html, title)
    for r, out_html, title, _ in pages:
        groups.setdefault(posixpath.dirname(out_html), []).append((out_html, title))
    out = ['<a class="brand" href="%s">📘 Spec</a>' % relhref(here_dir, "index.html"),
           '<input id="navsearch" placeholder="Filter…" autocomplete="off">']
    for d in sorted(groups):
        label = AREA_TITLES.get(d, d if d else "Overview")
        out.append('<div class="navgroup"><div class="navhdr">%s</div><ul>' % esc(label))
        for out_html, title in sorted(groups[d], key=lambda x: x[0]):
            cls = ' class="active"' if out_html == current else ""
            out.append('<li%s><a href="%s">%s</a></li>' % (cls, relhref(here_dir, out_html), esc(title)))
        out.append("</ul></div>")
    return "\n".join(out)

def breadcrumb(here_dir, out_html):
    parts = out_html.split("/")
    crumbs = ['<a href="%s">Overview</a>' % relhref(here_dir, "index.html")]
    acc = ""
    for d in parts[:-1]:
        acc = (acc + "/" + d) if acc else d
        crumbs.append(esc(AREA_TITLES.get(acc, d)))
    crumbs.append(esc(titles.get(out_html, parts[-1])))
    return ' <span class="sep">›</span> '.join(crumbs)

# ── page template ───────────────────────────────────────────────────────────────────────────────────
def page(out_html, title, content):
    here = posixpath.dirname(out_html)
    return """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<link rel="stylesheet" href="%(css)s">
</head><body>
<nav class="sidebar">%(nav)s</nav>
<main>
<div class="crumbs">%(crumb)s</div>
<article class="prose">%(content)s</article>
<footer>Generated from <code>spec/</code> by <code>tools/gen_docsite.py</code> — a pure projection; edit the spec, not this page.</footer>
</main>
<button id="navtoggle" aria-label="Menu">☰</button>
<script src="%(js)s"></script>
<script type="module">
import mermaid from "%(mermaid)s";
mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
</script>
</body></html>""" % {
        "title": esc(title), "css": relhref(here, "assets/site.css"),
        "js": relhref(here, "assets/site.js"), "mermaid": MERMAID,
        "nav": nav_html(here, out_html), "crumb": breadcrumb(here, out_html), "content": content,
    }

# ── home page (deterministic overview + full ID index) ───────────────────────────────────────────────
def home_page():
    out_html = "index.html"
    top = {}  # top-level area -> file count
    for r, oh, t, _ in pages:
        top.setdefault(oh.split("/")[0] if "/" in oh else "(root)", 0)
        top[oh.split("/")[0] if "/" in oh else "(root)"] += 1
    cards = []
    for d in sorted(top):
        label = AREA_TITLES.get(d, "Overview" if d == "(root)" else d)
        first = next((oh for r, oh, t, _ in sorted(pages, key=lambda x: x[1])
                      if (oh.split("/")[0] if "/" in oh else "(root)") == d), "index.html")
        cards.append('<a class="card" href="%s"><b>%s</b><span>%d file%s</span></a>'
                     % (first, esc(label), top[d], "" if top[d] == 1 else "s"))
    # ID index grouped by type
    by_type = {}
    for tok, oh in defs.items():
        by_type.setdefault(tok.split("-")[0].upper(), []).append((tok, oh))
    idx = []
    for ty in sorted(by_type):
        items = sorted(by_type[ty], key=lambda x: x[0])
        chips = "".join('<a class="id id-ref" href="%s#%s">%s</a>' % (oh, tok, tok) for tok, oh in items)
        idx.append('<div class="idgroup"><div class="navhdr">%s <small>(%d)</small></div>%s</div>'
                   % (ty, len(items), chips))
    content = (
        "<h1>Project specification</h1>"
        "<p>A browsable projection of the <code>spec/</code> tree. Every stable ID is a link to where "
        "it is defined; diagrams and tables are rendered inline. This site is regenerated wholesale "
        "from the spec — it is a view, not a source of truth.</p>"
        "<h2>Areas</h2><div class=\"cards\">" + "".join(cards) + "</div>"
        "<h2>Stable IDs <small>(%d)</small></h2>" % len(defs) + "".join(idx))
    return page(out_html, "Project specification", content)

# ── assets ───────────────────────────────────────────────────────────────────────────────────────────
SITE_CSS = """:root{--fg:#1d2733;--muted:#5b6b7b;--bg:#fff;--side:#f6f8fa;--line:#e3e8ee;--accent:#2563eb;
--code:#f2f4f7;--th:#eef2f7;--zebra:#fafbfc;--defbg:#e7f5ec;--deffg:#1a7f43;--refbg:#eef2ff;--reffg:#2742c7;--unkbg:#fdeaea;--unkfg:#b42318}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:1rem}
body{margin:0;display:flex;color:var(--fg);background:var(--bg);
font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
code,pre,.id{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace}
.sidebar{width:280px;min-width:280px;height:100vh;position:sticky;top:0;overflow-y:auto;
background:var(--side);border-right:1px solid var(--line);padding:1rem .9rem;font-size:14px}
.brand{display:block;font-weight:700;font-size:17px;color:var(--fg);text-decoration:none;margin-bottom:.7rem}
#navsearch{width:100%;padding:.45rem .6rem;border:1px solid var(--line);border-radius:7px;margin-bottom:.8rem;font-size:13px}
.navgroup{margin-bottom:.5rem}
.navhdr{font-weight:700;font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);margin:.6rem 0 .25rem}
.sidebar ul{list-style:none;margin:0;padding:0}
.sidebar li a{display:block;padding:.22rem .5rem;color:var(--fg);text-decoration:none;border-radius:6px;line-height:1.35}
.sidebar li a:hover{background:#e9edf2}
.sidebar li.active a{background:var(--accent);color:#fff}
main{flex:1;min-width:0;max-width:920px;margin:0 auto;padding:2.2rem 2.6rem 4rem}
.crumbs{font-size:13px;color:var(--muted);margin-bottom:1.4rem}
.crumbs a{color:var(--muted);text-decoration:none}.crumbs a:hover{color:var(--accent)}.crumbs .sep{margin:0 .15rem}
.prose h1,.prose h2,.prose h3,.prose h4{line-height:1.25;margin:1.8rem 0 .7rem;font-weight:680}
.prose h1{font-size:1.95rem;margin-top:0}.prose h2{font-size:1.5rem;border-bottom:1px solid var(--line);padding-bottom:.3rem}
.prose h3{font-size:1.2rem}.prose h4{font-size:1.02rem}
.prose p{margin:.7rem 0}.prose a{color:var(--accent);text-decoration:none}.prose a:hover{text-decoration:underline}
.anchor{opacity:0;margin-left:.4rem;color:var(--muted);text-decoration:none;font-weight:400}
h1:hover .anchor,h2:hover .anchor,h3:hover .anchor,h4:hover .anchor{opacity:.6}
.prose ul,.prose ol{margin:.5rem 0;padding-left:1.4rem}.prose li{margin:.2rem 0}
.prose code{background:var(--code);padding:.12em .38em;border-radius:5px;font-size:.88em}
.prose pre{background:var(--code);padding:1rem;border-radius:9px;overflow-x:auto;border:1px solid var(--line)}
.prose pre code{background:none;padding:0;font-size:.85em}
blockquote{margin:.8rem 0;padding:.5rem 1rem;border-left:4px solid var(--accent);background:var(--side);color:var(--muted)}
hr{border:0;border-top:1px solid var(--line);margin:2rem 0}
.tablewrap{overflow-x:auto;margin:1rem 0}
table{border-collapse:collapse;width:100%;font-size:.92em}
th,td{border:1px solid var(--line);padding:.5rem .7rem;vertical-align:top}
th{background:var(--th);font-weight:680}tbody tr:nth-child(even){background:var(--zebra)}
.scopebar{display:flex;flex-wrap:wrap;gap:.4rem;margin:0 0 1.4rem;font-size:12px}
.badge{background:var(--side);border:1px solid var(--line);border-radius:999px;padding:.18rem .65rem;color:var(--muted)}
.badge b{color:var(--fg);text-transform:uppercase;font-size:10px;letter-spacing:.04em;margin-right:.3rem}
.id{font-size:.85em;border-radius:5px;padding:.05em .35em;text-decoration:none;white-space:nowrap}
.id-def{background:var(--defbg);color:var(--deffg);font-weight:700}
.id-ref{background:var(--refbg);color:var(--reffg)}.id-ref:hover{text-decoration:underline}
.id-unknown{background:var(--unkbg);color:var(--unkfg)}
.mermaid{margin:1.2rem 0;text-align:center}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:.7rem;margin:1rem 0}
.card{display:flex;flex-direction:column;gap:.2rem;padding:.8rem 1rem;border:1px solid var(--line);
border-radius:10px;text-decoration:none;color:var(--fg);background:var(--side)}
.card:hover{border-color:var(--accent)}.card span{font-size:12px;color:var(--muted)}
.idgroup{margin:1rem 0;display:flex;flex-wrap:wrap;gap:.35rem;align-items:baseline}
.idgroup .navhdr{width:100%}.idgroup .id{margin:.1rem}
footer{margin-top:3rem;padding-top:1.2rem;border-top:1px solid var(--line);font-size:12px;color:var(--muted)}
footer code{background:var(--code);padding:.1em .35em;border-radius:4px}
#navtoggle{display:none;position:fixed;bottom:1rem;right:1rem;z-index:20;border:0;background:var(--accent);
color:#fff;width:48px;height:48px;border-radius:50%;font-size:20px;box-shadow:0 2px 10px rgba(0,0,0,.2)}
small{color:var(--muted);font-weight:400}
@media(max-width:820px){.sidebar{position:fixed;left:0;top:0;z-index:10;transform:translateX(-100%);transition:.2s}
body.navopen .sidebar{transform:none}#navtoggle{display:block}main{padding:1.4rem}}
"""

SITE_JS = """// sidebar filter + responsive menu (no deps)
(function(){
  var q=document.getElementById('navsearch');
  if(q){q.addEventListener('input',function(){
    var v=q.value.toLowerCase();
    document.querySelectorAll('.sidebar li').forEach(function(li){
      li.style.display=li.textContent.toLowerCase().indexOf(v)>-1?'':'none';});
    document.querySelectorAll('.navgroup').forEach(function(g){
      var any=Array.prototype.some.call(g.querySelectorAll('li'),function(li){return li.style.display!=='none';});
      g.style.display=any?'':'none';});
  });}
  var t=document.getElementById('navtoggle');
  if(t){t.addEventListener('click',function(){document.body.classList.toggle('navopen');});}
  var a=document.querySelector('.sidebar li.active');
  if(a)a.scrollIntoView({block:'center'});
})();
"""

# ── write ────────────────────────────────────────────────────────────────────────────────────────────
if OUT.exists():
    shutil.rmtree(OUT)
(OUT / "assets").mkdir(parents=True)
(OUT / "assets" / "site.css").write_text(SITE_CSS, encoding="utf-8")
(OUT / "assets" / "site.js").write_text(SITE_JS, encoding="utf-8")
(OUT / "index.html").write_text(home_page(), encoding="utf-8")
for r, out_html, title, txt in pages:
    dest = OUT / out_html
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page(out_html, title, render_markdown(txt, out_html)), encoding="utf-8")

print("docs-site: wrote %d page(s) + index to %s (%d stable IDs indexed)"
      % (len(pages), OUT, len(defs)))
