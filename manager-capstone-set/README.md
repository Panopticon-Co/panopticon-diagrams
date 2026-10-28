# Panopticon — capstone diagram set

Six diagrams of the Panopticon EDR/XDR platform, updated to reflect the full
closed-loop detection, response authorization, multi-agent endpoints (Windows
& Linux), and Manager control plane architecture.

Built with the `cathrynlavery/diagram-design` plugin's editorial design system
(white-smoke paper `#f5f5f5`, jet-black ink `#2d3142`, atomic-tangerine accent
`#eb6c36`, slate muted `#4f5d75`; Instrument Serif / Geist / Geist Mono).

| # | File | Type | What it answers |
|---|---|---|---|
| 1 | `01-architecture` | Architecture | Running components across Windows, Linux, Manager and Console, crossing trust boundaries |
| 2 | `02-uml-class` | UML class | Static object model across agent C++, detection engine Python, and the closed-loop response contract |
| 3 | `03-data-flow` | Level-1 DFD | Full telemetry ingestion, SQLite WAL stores, alert/incident querying, and response command loop |
| 4 | `04-use-case` | UML use case | Platform use cases from telemetry streaming to analyst authorization and endpoint action execution |
| 5 | `05-sequence` | UML sequence | End-to-end trace: Ingest batch -> fast commit/ack -> async detection -> analyst approval -> command dispatch -> evidence |
| 6 | `06-activity` | UML activity (4 partitions) | Partitioned workflow of an event from endpoint collection through detection, triage, and response execution |

Each diagram ships in three forms:

- `NN-name.html` — the source. Self-contained; open it in any browser.
- `NN-name.svg` — standalone vector, diagram only. Strict XML compliant.
- `NN-name.png` — 2× raster, sized `viewBox × 2` for reports and presentations.

## Reading the diagrams

**The coral accent is editorial, not a severity flag.** Across the whole set it
marks the core trust and control boundaries:
- The **ingest boundary** (`Ingest API` / process 2.0 / `200 Ack`)
- The **detection core** (`DetectionRun` / process 3.0 / `Run detection`)
- The **closed-loop response authorization** (`Authorize Action` / process 5.0 / `Dispatch Command`)

**Every diagram carries its own legend** as a bottom strip. Diagram 2's legend is
the complete UML relationship vocabulary (all six forms).

## Facts pinned to source

These numbers and behaviors are verified against the source code:

| Claim on the diagrams | Source |
|---|---|
| Windows schema `0.3`, Linux schema `0.4`, Engine accepts `0.1`–`0.5` | `panopticon-agent/.../panopticon_event.hpp`, `panopticon-linux-agent`, `panopticon_detection/ingestion/officer_adapter.py` |
| 74 rules in 17 domains, 14 operators | `panopticon-detection-engine/rules/`, `panopticon_detection/evaluator/operators.py` |
| Provenance & graph engines | `panopticon_detection/provenance/` (`ProvenanceGraph`, `EventGraphBuilder`, `IncidentTracker`, `ProcessRegistry`) |
| Closed 7-action vocabulary | `panopticon-response-engine/response_engine/contract.py` (`KILL_PROCESS`, `COLLECT_PROCESS_INFO`, `COLLECT_NETWORK_CONNECTIONS`, `COLLECT_FILE`, `QUARANTINE_FILE`, `ISOLATE_HOST`, `RELEASE_HOST_ISOLATION`) |
| Tier classification | `response_engine/policy.py` (`AUTO_SAFE` for read-only collectors, `ANALYST_APPROVAL` for destructive actions) |
| Closed-loop authorization & dispatch | `manager/routers/response_actions.py`, `manager/routers/commands.py` |
| Privilege-separated isolation | `panopticon-linux-agent`: UNIX domain socket IPC to `CAP_NET_ADMIN` helper with exactly 2 opcodes (`isolate`, `release`) |
| PID reuse prevention | `response_engine/recommendation.py` requiring `pid`, `start_time_ticks`, and `boot_id` |
| Ingest ack precedes detection | `docs/adr/002-wire-protocol-ack-semantics.md`, `manager/routers/ingest.py` returning 200 before worker processes |
| Lease 60s, claim batch &le; 256 | `LEASE_SECONDS`, `CLAIM_LIMIT` in `manager/detection/worker.py` |
| Server-side decision proxy | `panopticon-console`: server attaches bearer token to `POST /api/response-actions`, never exposing tokens to client JS |
| Console polling 3000 ms | `POLL_INTERVAL_MS` in `panopticon-console/static/app.js` |

## Deliberate modelling choices

- **Multi-agent architecture:** Both Windows Officer Agent (ETW/Sysmon) and Linux Agent (procfs/eBPF) are drawn.
- **Closed-loop response:** Replaced obsolete "simulated remediation" with the real implemented response authorization workflow.
- **Diagram 3 is a classical Level-1 DFD:** External entities, numbered processes 1.0 to 6.0, open-ended stores D1 to D5.
- **Diagram 4 use cases:** Covers both telemetry streaming and active response authorization with endpoint evidence reporting.
- **Diagram 6 partitioned activity:** Shows all 4 system partitions (Endpoint Agent, Manager API, Detection Worker, SOC Analyst).

## Regenerating

The `.html` files are the source of truth. Standalone `.svg` and 2× `.png` files are exported via:

```bash
python _tooling/export_svg.py manager-capstone-set
python _tooling/export_png.py manager-capstone-set
python _tooling/validate.py
```