import re, sys, pathlib

NAMED = {"&middot;": "&#183;", "&nbsp;": "&#160;", "&mdash;": "&#8212;",
         "&ndash;": "&#8211;", "&laquo;": "&#171;", "&raquo;": "&#187;",
         "&hellip;": "&#8230;", "&rsquo;": "&#8217;", "&ldquo;": "&#8220;",
         "&rdquo;": "&#8221;", "&times;": "&#215;", "&deg;": "&#176;"}

FONTS = ("<defs><style>@import url('https://fonts.googleapis.com/css2?"
         "family=Instrument+Serif:ital@0;1&amp;family=Geist:wght@400;500;600"
         "&amp;family=Geist+Mono:wght@400;500;600&amp;display=swap');</style>")

def convert(src: pathlib.Path) -> pathlib.Path:
    html = src.read_text(encoding="utf-8")
    m = re.search(r"<svg\b.*?</svg>", html, re.S)
    if not m:
        raise SystemExit(f"no <svg> in {src}")
    svg = m.group(0)
    for k, v in NAMED.items():
        svg = svg.replace(k, v)
    if "xmlns=" not in svg.split(">", 1)[0]:
        svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    if "<defs>" in svg:
        svg = svg.replace("<defs>", FONTS, 1)
    else:
        svg = re.sub(r"(</desc>)", r"\1\n" + FONTS + "</defs>", svg, count=1)
    out = src.with_suffix(".svg")
    out.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg + "\n", encoding="utf-8")
    return out

if __name__ == "__main__":
    root = pathlib.Path(sys.argv[1])
    for f in sorted(root.rglob("*.html")):
        o = convert(f)
        print("SVG", o.relative_to(root))
