# Contributing to panopticon-diagrams

This repository holds the versioned diagram set for the Panopticon&Co
EDR/XDR capstone platform. Read this document and
[`DIAGRAM_SPECIFICATION.md`](DIAGRAM_SPECIFICATION.md) before changing
anything — the specification is the governing contract every diagram obeys,
and a change that isn't consistent with it will fail
`_tooling/validate.py` and CI.

## What is actually in this repository

Every diagram is a **hand-authored, self-contained `.html` file with inline
SVG**, produced with the `diagram-design` skill's editorial skin. Each
diagram's `.html` is the source of truth; its `.svg` and `.png` siblings are
**derived** files, regenerated from the `.html`, never edited directly.

There is **no diagram-generation pipeline** in the sense of a DSL compiled
into a picture — no Mermaid, no PlantUML, no Graphviz `.dot`, no `.drawio`
project files. The `.html` file *is* the diagram; editing it means editing
the inline SVG markup (or the skill's authoring workflow) by hand.

The only automation that exists is:

- `_tooling/export_svg.py` — extracts the `<svg>` from an `.html` file and
  writes it as a standalone, well-formed `.svg`.
- `_tooling/export_png.py` — renders an `.html` file in headless Chromium
  (via Playwright) and screenshots it to a `.png`.
- `_tooling/validate.py` — a consistency gate that checks every diagram's
  asserted facts (class/method/field names, counts, schema fields, banned
  terms, accessibility attributes) against the real source of the four other
  Panopticon-Co repositories it expects to find checked out as siblings. This
  runs in CI on every push and pull request
  (`.github/workflows/validate.yml`).

There is no build step that turns a diagram description into the `.html` —
if you want a new diagram, you author the HTML/SVG yourself.

## Adding or updating a diagram

1. Read [`DIAGRAM_SPECIFICATION.md`](DIAGRAM_SPECIFICATION.md) in full,
   especially §2 (implementation-status vocabulary), §5 (terminology), and
   §6 (cross-diagram consistency rules).
2. Edit the `.html` file directly, or author a new one following the
   existing files' structure: an accessible SVG with a `<title>`,
   `role="img"`, `aria-labelledby`, a `<desc>`, a single `viewBox`, no
   `<script>`, and no remote asset other than the pinned Google Fonts
   `@import`.
3. Tag every element honestly. An element that exists in code and is
   covered by a passing test is **Implemented** (solid stroke). An element
   that is only specified in an ADR or architecture document is
   **Designed** (dashed stroke, `DESIGNED` tag). An element whose code path
   runs but only performs bookkeeping instead of the real-world effect it
   names is **Simulated** (dashed accent stroke, `SIMULATED` tag). Never
   show a Designed, Planned, or Simulated element without its tag — a
   reader must never mistake intent for capability.
4. Re-export the derived files from the repository root:

   ```bash
   python _tooling/export_svg.py .
   python _tooling/export_png.py . 2
   ```

5. Open the resulting `.png` and look at it. Passing an automated check does
   not guarantee a label isn't sitting on a connector or a line isn't
   crossing a box — several defects in this set were caught only by
   inspecting the rendered output.
6. If your change affects a fact shared across diagrams (a class name, a
   field, a count, a direction of flow), update every other diagram listed
   against that fact in `DIAGRAM_SPECIFICATION.md` §11, and bump the
   specification's version and date.
7. Run the consistency validator before opening a pull request. It expects
   `panopticon-agent`, `panopticon-manager`, `panopticon-detection-engine`,
   `panopticon-console`, and `panopticon-linux-agent` checked out as
   siblings of this repository (or `PANOPTICON_WORKSPACE` pointed at the
   parent directory that holds them):

   ```bash
   python _tooling/validate.py
   ```

   CI runs this same script automatically on every push and pull request by
   checking out all five sibling repositories.

## Naming and terminology

Files are named `panopticon-<subject>.html`, kebab-case, matching the
in-file `<title>` slug and `aria-labelledby` prefix. Component names are
canonical and must never be paraphrased: **Officer** (the agent),
**eyedetect** (the detection engine), **Panopticon Console**, **Panopticon
Event**. See `DIAGRAM_SPECIFICATION.md` §5 for the full terminology table
and the list of banned synonyms.

## What not to do

- Do not invent a class, method, field, or count that doesn't exist in the
  source repositories — omission is allowed, invention is not.
- Do not show an unimplemented or simulated element without its dashed
  stroke and tag.
- Do not add a diagram-rendering toolchain (Mermaid, PlantUML, Graphviz,
  draw.io, or similar) — this set is intentionally hand-authored HTML/SVG,
  and mixing formats would break the visual consistency the set relies on.
- Do not add tracking scripts, remote fonts other than the pinned Google
  Fonts stylesheet, or any `<script>` tag to a diagram file.

## Pull requests

Use the pull request template. At minimum, state which diagram(s) changed,
which fact(s) motivated the change (a code change, a schema change, an ADR),
and confirm `_tooling/validate.py` passes against current sibling checkouts.
