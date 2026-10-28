# Panopticon — capstone diagram set

Six diagrams of the Panopticon EDR/XDR platform, drawn from the actual code in
this workspace rather than from the design docs (several of which are stale —
`docs/MANAGER_ARCHITECTURE.md` and `docs/API_CONTRACT.md` still describe
`/api/v1/ingest` as unimplemented, but `manager/routers/ingest.py` exists and is
tested).

Built with the `cathrynlavery/diagram-design` plugin's editorial design system
(default skin: white-smoke paper, jet-black ink, atomic-tangerine accent,
blue-slate muted; Instrument Serif / Geist / Geist Mono).

| # | File | Type | What it answers |
|---|---|---|---|
| 1 | `01-architecture` | Architecture | What the running components are and how telemetry crosses the trust boundary |
| 2 | `02-uml-class` | UML class | The static object model from collector interface to `Alert`, across the two language packages |
| 3 | `03-data-flow` | Level-1 DFD | Which processes read and write which stores, including the store nothing reads yet |
| 4 | `04-use-case` | UML use case | Who asks the platform for what, and which behaviour is deliberately simulated |
| 5 | `05-sequence` | UML sequence | One batch from `POST` to alert, and why the ack precedes detection |
| 6 | `06-activity` | UML activity (4 partitions) | The end-to-end control flow of a single event, with its two decisions |

Each diagram ships in three forms:

- `NN-name.html` — the source. Self-contained; open it in any browser.
- `NN-name.svg` — standalone vector, diagram only (no page header/legend chrome
  beyond what is inside the `<svg>`). Fonts load from Google Fonts at render time.
- `NN-name.png` — 2× raster, sized `viewBox × 2`. Use this in the report/slides;
  it is portable and needs no font resolution.

## Reading the diagrams

**The coral accent is editorial, not a severity flag.** Across the whole set it
marks the same two things: the **ingest boundary** (`Ingest API` / process 2.0 /
`Ack 200`) and the **detection core** (`DetectionRun` / process 3.0 / `Run
detection`). Diagram 2 is the exception — there the accent marks the
`TelemetryCollector` interface and its realizations, because that diagram's
subject is the type hierarchy. Diagram 4 additionally uses a dashed coral
outline for `Simulate Remediation`, which is a policy boundary, not a focal point.

**Every diagram carries its own legend** as a bottom strip. Diagram 2's legend is
the complete UML relationship vocabulary (all six forms), including the two the
diagram body does not use — it doubles as a reference.

## Facts pinned to source

These numbers are checked against the code, not the docs:

| Claim on the diagrams | Source |
|---|---|
| Schema `0.3`, agent `0.3.0` | `panopticon-agent/include/panopticon/officer/telemetry/panopticon_event.hpp` |
| 86 rules | `vendor/eyedetect/rules/**/*.yaml` (one `Rule` per file) |
| 11 detection engines | `DetectionRun.__init__` keyword-only args in `vendor/eyedetect/src/pipeline_core.py`, minus `auto_remediate` / `emit` / `emit_remediation` |
| lease 60s, claim ≤ 256 | `LEASE_SECONDS`, `CLAIM_LIMIT` in `manager/detection/worker.py` |
| console polls every 3s | `POLL_INTERVAL_MS` in `panopticon-console/static/app.js` |
| ack precedes detection | `docs/adr/002-wire-protocol-ack-semantics.md`, and `routers/ingest.py` returning before the worker ever sees the row |
| `alerts` table has no reader | nothing selects from `alerts`; the query API is Phase 7 in `docs/ROADMAP.md` |
| remediation is simulated | `EndpointRemediationEngine(dry_run=True)` in `manager/detection/factory.py` |

## Deliberate modelling choices

- **Diagram 3 is a classical Yourdon/DeMarco level-1 DFD** (external entities,
  numbered processes, open-ended stores), not the plugin's parametric
  "data flow" type — that type is a role-scoped swimlane and would have
  answered a different question.
- **Diagram 3 shows one planned flow** (`D2 alerts → 4.0`, dashed, "PHASE 7").
  The alerts table genuinely has no reader today; drawing that gap is more
  useful than hiding it.
- **Diagram 4 uses a `«time»` actor** (`Detection Scheduler`) for the worker's
  claim loop, because detection has no human or external initiator — the
  1-second poll in `DetectionWorker._run` is the trigger.
- **Diagram 6 exceeds the plugin's default 9-node budget** (24 nodes). It is
  drawn at `faithful` detail, zoned into four partitions, which is the
  documented exemption. Every other diagram is inside its type's budget.
- **Diagram 2 spans two repos in one figure.** The `PanopticonEvent` →
  `OfficerIngestionAdapter` dependency is the cross-repo contract; splitting it
  into two diagrams would have hidden the one relationship that matters most.

## Regenerating

The `.html` files are the source of truth. After editing one:

```bash
# geometry + accessibility gate
python3 ~/.claude/plugins/marketplaces/diagram-design/skills/diagram-design/scripts/self_check.py 01-architecture.html

# re-export SVG + PNG
/diagram-design:export-diagram 01-architecture.html
```

Two authoring traps worth knowing, both hit during the first build:

- **Named HTML entities are illegal inside the SVG.** `&middot;` parses fine in
  the browser but breaks the standalone `.svg` export, which is strict XML. Use
  numeric entities (`&#183;`, `&#171;`, `&#8230;`).
- **`--` is illegal inside an XML comment.** `<!-- A -- B -->` renders but makes
  the exported `.svg` unparseable.
