# Panopticon Diagram Specification

**Version:** 1.0
**Date:** 2026-09-04
**Status:** Authoritative for the diagram set in this directory
**Scope:** The complete UML and software-architecture diagram set for the Panopticon&Co
capstone platform, covering `panopticon-agent` (Officer), `panopticon-detection-engine`
(eyedetect), and `panopticon-console`.

This file is the contract every diagram in `docs/diagrams/` obeys. If a diagram and this
file disagree, one of them is wrong and must be corrected — the disagreement is never
tolerated silently.

---

## 1. Source-of-truth hierarchy

Diagrams were derived using this authority order. Where levels conflict, the higher level
wins and the conflict is recorded in §9.

| Rank | Source | Examples used |
|---|---|---|
| 1 | Approved ADRs | `panopticon-agent/docs/adr/003-process-entity-id.md` |
| 2 | Canonical schema / contract | `panopticon-agent/schema/event.schema.json` (Schema 0.3) |
| 3 | Architecture documents | `phase-1-contracts.md`, `phase-2-live-collection.md`, `detection-ingestion-boundary.md`, `V2_RELIABILITY.md`, `V3_TELEMETRY.md` (both repos), `PANOPTICON_V1.md` |
| 4 | Current implementation | C++ headers and sources, Python modules, rule YAML, console `app.py` / `static/app.js` |
| 5 | Component documentation | per-repo `README.md`, `CLAUDE.md`, `OFFICER_INTEGRATION.md` |
| 6 | Roadmap / future plans | `panopticon-agent/docs/roadmap.md`, §16 of `V2_RELIABILITY.md` |

**Verification performed on 2026-09-04.** All three test suites were executed against the
working tree before any diagram was drawn:

| Suite | Command | Result |
|---|---|---|
| Officer agent | `ctest --test-dir build-officer-x64` | 7 / 7 passed |
| Detection engine | `pytest tests/` | 151 passed, 2 skipped |
| Console | `python -m unittest discover -s tests` | 24 passed |

Working-tree branch for all three repositories at capture time: `v3/telemetry-expansion`.

---

## 2. Implementation-status vocabulary

Every element in every diagram carries exactly one of these statuses. The status is shown
visually (see §7) and stated in the diagram's accompanying note.

| Status | Meaning | Visual treatment |
|---|---|---|
| **Implemented** | Code exists in the working tree and is covered by a passing test. | Solid stroke, normal fill |
| **Designed** | Specified in an architecture document or ADR, with no implementing code. | Dashed stroke, 2% ink wash fill, `DESIGNED` tag |
| **Planned** | Named in the roadmap only, with no design document. | Excluded from current-state diagrams; appears only where a diagram is explicitly labelled a target-state view |
| **Simulated** | A code path exists and runs, but performs bookkeeping instead of the real-world effect it names. | Dashed accent stroke, `SIMULATED` tag |

**Rule:** no current-state diagram may show a Designed or Planned element without the
dashed treatment and the tag. A reader must never mistake intent for capability.

---

## 3. Verified system model

### 3.1 Actors

| Actor | Type | Reality in the current system |
|---|---|---|
| **Security Analyst** | Human, primary | Reads the console alert table. Cannot acknowledge, assign, comment, filter, or respond — the console is read-only. |
| **Detection Engineer** | Human | Authors and edits rule YAML under `rules/`; runs the engine over sample or captured NDJSON to test a rule; runs the MITRE coverage and taxonomy audit reports. |
| **Security Administrator** | Human | Installs and scopes Sysmon, builds the agent, launches the elevated agent and the engine, sets CLI flags (queue capacity, spool path, retry policy, output paths), inspects health and metrics files. |
| **Officer Agent** | System actor | Non-human initiator of telemetry collection on the endpoint. |

There is **no** authenticated user, no role assignment, no multi-tenancy and no access
control anywhere in the platform. In the current implementation all three human roles are
the same operating-system user on the same machine.

### 3.2 External systems

| External system | Interface used |
|---|---|
| **Windows ETW** — `Microsoft-Windows-Kernel-Process` (`{22fb2cd6-0e7b-422b-a0c7-2fad1fd0e716}`) | `StartTraceW`, `EnableTraceEx2`, `OpenTraceW`, `ProcessTrace`, TDH property decoding |
| **Sysmon** — `Microsoft-Windows-Sysmon/Operational` channel | `EvtSubscribe`, `EvtRender` push subscription |
| **Windows registry and host APIs** | `RegGetValueW` (MachineGuid, ProductName, CurrentBuildNumber), `GetComputerNameExW`, `OpenProcessToken` |
| **Windows CNG** (`bcrypt.dll`) | SHA-256 for entity and event identity derivation |
| **Web browser** | HTTP polling of the console on `127.0.0.1:8787` |

MITRE ATT&CK is a **classification vocabulary embedded in rule YAML**, not an integrated
external service. No network call is made to any MITRE endpoint.

### 3.3 Components — implemented

**Endpoint — Officer (`panopticon-agent`, C++20 / CMake / vcpkg)**

| Component | Type | Evidence |
|---|---|---|
| `TelemetryCollector` | Abstract interface | `include/panopticon/officer/collectors/telemetry_collector.hpp` |
| `EtwProcessCollector` | Collector, ETW event ID 1 | `src/collectors/etw_process_collector.cpp` |
| `SysmonEventCollector` | Collector, Sysmon event IDs 1, 3, 7, 11, 12, 13, 14, 23, 26 | `src/collectors/sysmon_event_collector.cpp` |
| `SysmonProcessDecoder` | XML decoder, event ID 1 only | `src/collectors/sysmon_process_decoder.cpp` |
| `SysmonTelemetryDecoder` | XML decoder, the eight non-process event IDs | `src/collectors/sysmon_telemetry_decoder.cpp` |
| Inline enrichment | Two free functions applied in a lambda, not a class | `src/main.cpp` — `file_name()`, `populate_user()` |
| Normalizer | `normalize_process_event` plus four family normalizers | `src/pipeline/normalizer.cpp` |
| Serializer | `serialize_event` / `deserialize_event` — the only JSON boundary | `src/pipeline/serializer.cpp` |
| Identity | `derive_process_entity_id`, `derive_process_event_id`, `derive_process_context_entity_id`, `derive_telemetry_event_id` | `src/core/entity_id.cpp` |
| `officer-query` | Separate historical Sysmon reader, outside the live path | `tools/query/` |

CMake targets: `officer-core` (static), `officer-collectors` (static), `officer-agent`
(executable), plus `officer-query`. Output is **one NDJSON line per event on stdout**.

**Detection engine — eyedetect (`panopticon-detection-engine`, Python)**

| Component | Role | Evidence |
|---|---|---|
| `LiveTelemetryStream` | Ingestion source: an NDJSON file, or spawn `officer-agent.exe` and read its stdout | `src/ingestion/live_stream.py` |
| `OfficerIngestionAdapter` | Schema 0.1 / 0.2 / 0.3 to engine-internal event dictionary | `src/ingestion/officer_adapter.py` |
| `src.ingestion.telemetry` | Category-dispatch registry for the four non-process families | `src/ingestion/telemetry.py` |
| `BoundedEventQueue` | Bounded FIFO with block / drop_newest / drop_oldest overflow | `src/reliability/queue.py` |
| `StreamingPipeline` | Producer thread, consumer thread, restart recovery, deterministic shutdown | `src/reliability/pipeline.py` |
| `DetectionRun` | Per-event driver running detection stages A to G | `src/pipeline_core.py` |
| `RuleEvaluator` and `ConditionMatcher` | Rule routing by `event_type`, boolean logic tree, 13 comparison operators plus 3 special operators | `src/evaluator/` |
| `ProcessTree` | Stateful process lineage and ancestry | `src/correlation/process_tree.py` |
| `CorrelationEngine`, `EntityRiskScorer`, `EnterpriseAttackGraph` | Multi-event correlation, risk accumulation, campaign graph | `src/correlation/` |
| `ThresholdEngine`, `C2BeaconDetector`, `PortScanDetector`, `RansomwareShield`, `IdentityAnalyticsEngine`, `CloudThreatEngine` | Behavioural detectors for stages B to G | various |
| `Alert` and `ActiveResponseEngine` | Alert construction, deterministic `ALT-XXXXXXXX` identifier, response **recommendation** | `src/alerting/` |
| `AlertSpool` | SQLite (WAL) durable alert spool with `pending` / `delivered` / `dead` states | `src/reliability/spool.py` |
| `IncrementalAlertWriter` | Append, flush and fsync to `alerts.ndjson`; torn-tail repair; cross-restart de-duplication | `src/reliability/alert_sink.py` |
| `EndpointRemediationEngine` | **Simulated** — records `RemediationAction` objects and executes nothing | `src/remediation/engine.py` |
| `HealthState`, `Metrics` | JSON health snapshot and Prometheus-text metrics, both written on exit | `src/reliability/` |

Rule corpus: **86 YAML files** across 15 directories (`cloud`, `collection`,
`credential_access`, `defense_evasion`, `exfiltration`, `file`, `identity`,
`initial_access`, `lateral_movement`, `malware`, `network`, `persistence`,
`privilege_escalation`, `process`, `web_api`).

**Console (`panopticon-console`, Python standard library)**

A `ThreadingHTTPServer` serving exactly three routes — `GET /`, `GET /app.js`, and
`GET /api/alerts`. `read_alerts()` parses the engine's alert NDJSON file, skipping blank
and malformed lines. `static/app.js` polls every 3000 ms, de-duplicates by `alert_id`, and
renders a table of timestamp, telemetry family, rule identifier, severity with level,
MITRE tactic and technique, title, and evidence pairs. Values reach the DOM only through
`textContent`. It binds `127.0.0.1:8787` by default. There is no authentication, no
database, no WebSocket, and no write path.

### 3.4 Components — designed but NOT implemented

These appear only in the target-state portion of the architecture diagram and in the
response sequence diagram, always dashed and tagged `DESIGNED`. Source:
`panopticon-agent/docs/architecture/detection-ingestion-boundary.md` and
`panopticon-agent/docs/roadmap.md` phases 3, 6, 7 and 8.

- Agent-side bounded event queue, backpressure policy and loss counters (roadmap phase 3)
- Agent-side durable SQLite spool with acknowledged batch deletion (roadmap phase 6)
- Agent enrollment, persistent installation identity, authenticated TLS batch delivery,
  signed configuration fetch (roadmap phase 7)
- Backend ingestion service: agent authentication, schema-version validation, size limits,
  per-event rejection results, immutable observation store
- Cross-source process-identity reconciliation on `host.id` plus `process.entity_id`
- Alert and case store, response service, command queue, endpoint response executor
- Windows service packaging (roadmap phase 8)

**No component in this list may appear as implemented in any diagram.**

### 3.5 Integration surfaces — the only three

```
panopticon-agent  --build-->  officer-agent.exe
officer-agent.exe --stdout NDJSON (Schema 0.3)-->  panopticon-detection-engine
panopticon-detection-engine --alerts.ndjson file-->  panopticon-console
```

There is no HTTP between agent and engine, no named pipe (despite a stale docstring, see
§9), no message broker, no database server, and no network hop between engine and console.
The engine either reads a captured NDJSON file or spawns the agent as a child process and
reads its stdout pipe.

---

## 4. Diagram inventory

15 diagrams. Every one is a hand-authored, self-contained HTML file with inline SVG,
produced with the `diagram-design` skill.

| # | Diagram | Directory | Visual type | Status shown |
|---|---|---|---|---|
| 1 | System context | `context/` | Architecture with context boundary | Current |
| 2 | High-level system architecture | `architecture/` | Architecture, zoned | Current plus designed backend |
| 3 | Use case | `uml/use-case/` | UML use case | Current |
| 4 | Component | `uml/component/` | UML component | Current |
| 5 | Agent class model | `uml/class/agent/` | UML class | Current |
| 6 | Detection engine class model | `uml/class/detection-engine/` | UML class | Current |
| 7 | Telemetry collection sequence | `uml/sequence/telemetry-collection/` | UML sequence | Current |
| 8 | Detection sequence | `uml/sequence/detection/` | UML sequence | Current |
| 9 | Response sequence | `uml/sequence/response/` | UML sequence | Current (simulated) plus designed |
| 10 | End-to-end activity | `uml/activity/` | UML activity | Current |
| 11 | Alert lifecycle state machine | `uml/state/` | UML state machine | Current |
| 12 | Deployment | `uml/deployment/` | UML deployment | Current |
| 13 | Event data model | `data/event-data-model/` | Entity relationship | Current, Schema 0.3 |
| 14 | Process entity relationships | `data/process-entity-relationships/` | Entity relationship | Current |
| 15 | Attack detection and investigation scenario | `investigation/` | Swimlane | Current scenario |

Each diagram's purpose, scope, represented elements and known limitations are recorded in
`README.md`, and each HTML file carries a `<desc>` sentence stating what it shows.

---

## 5. Terminology and naming conventions

These names are canonical. No diagram may use a synonym, an invented name, or a marketing
label.

| Canonical | Never write |
|---|---|
| **Officer** (the agent) | "the C++ agent", "the sensor", "EDR agent" |
| **eyedetect** (the detection engine) | "the backend", "the server" |
| **Panopticon Console** | "the dashboard", "the SOC portal" |
| **Panopticon Event** / **Schema 0.3** | "the JSON", "the telemetry record" |
| `process.entity_id` | "process GUID", "process id" |
| **Alert** | "incident" or "case" used interchangeably |
| **Detection** (a `DetectionResult`) | "alert" |
| **Response recommendation** (`ActiveResponseAction`) | "response", "remediation" |
| **Telemetry family** — process, network, file, registry, image load | "event type", "data source" |

`Officer`, `eyedetect` and `eyetrace` are deliberate project component names and are never
paraphrased or renamed.

Class and function names in class diagrams are reproduced **exactly** as they appear in
source, including case and underscores. C++ types show the `panopticon::officer::*`
namespace segment where it disambiguates. Python types show their module path in the
diagram note rather than in the class box.

File naming: `panopticon-<subject>.html`, kebab-case, matching the `<title>` slug and the
`aria-labelledby` identifier prefix used inside the file.

---

## 6. Cross-diagram consistency rules

1. **The primary flow runs left to right** in context, architecture, component and
   swimlane diagrams, and **top to bottom** in activity and state diagrams. Sequence
   diagrams run top to bottom in time with lifelines left to right in call order.
2. **The agent never receives telemetry.** No diagram may draw an arrow into Officer from
   eyedetect, the console, or a human. The only inbound control is process spawn and the
   CTRL_BREAK shutdown signal, both labelled as process control rather than telemetry.
3. **Detection never executes response.** `EndpointRemediationEngine` and
   `ActiveResponseEngine` produce records and recommendations. No diagram may draw an arrow
   from the detection engine to the endpoint representing an executed action.
4. **The spool holds alerts, not events.** `AlertSpool` sits after detection, never before
   it. Any diagram placing a store between ingestion and detection is wrong.
5. **The console is read-only.** No arrow leaves the console toward the engine, the agent,
   or the endpoint in any current-state diagram.
6. **Every field named in a data diagram exists** in `event.schema.json` or, for
   engine-internal fields, in `officer_adapter.py` or `telemetry.py`, and the diagram says
   which of the two.
7. **Every class and member named in a class diagram exists in source.** Members are
   selected, never invented; omission is allowed, invention is not.
8. **Schema version is 0.3 everywhere.** The agent emits 0.3; the engine accepts 0.1, 0.2
   and 0.3. Diagrams showing agent output say 0.3, and diagrams showing the engine's
   accepted range say the range.
9. **Counts are stated once and consistently:** 86 rules, 15 rule domains, 5 telemetry
   families, 7 detection stages (A to G), 3 console routes, 13 comparison operators.

---

## 7. Visual conventions

The set uses the `diagram-design` skill's shipped editorial skin, unmodified, as the
Panopticon visual identity. It is light and high-contrast, and it prints and projects
reliably.

| Token | Value | Applied to |
|---|---|---|
| `paper` | `#f5f5f5` | Page and diagram ground |
| `ink` | `#2d3142` | Primary text and stroke |
| `muted` | `#4f5d75` | Secondary text, default connectors |
| `soft` | `#7a8399` | Sublabels, boundary labels |
| `accent` | `#eb6c36` | One or two focal elements per diagram only |
| `link` | `#2e5aa8` | External-system and HTTP connectors |

Additional set-wide rules:

- **The focal choice is deliberate per diagram** and recorded in the README. It is usually
  the Panopticon Event (the contract) or the component the diagram is about.
- **A dashed `4,3` stroke plus a `DESIGNED` or `SIMULATED` tag** is the only way
  unimplemented or non-executing behaviour is drawn.
- **Connectors are orthogonal** with `r=8` quarter-arc bends. Arrow labels sit in a
  paper-coloured mask with a visible 6 to 10 px gap above the stroke.
- **Legends are a horizontal strip at the bottom**, never floating inside the drawing.
- Type tags use Geist Mono at 7 to 8 px, uppercase and tracked; node names use Geist sans
  at 12 px semibold; technical sublabels use Geist Mono at 9 px.

---

## 8. Assumptions

1. **The three human roles are modelled as distinct actors** even though the current system
   authenticates nobody and one operator performs all three. This is standard use-case
   practice and is stated on the diagram. It is a modelling choice, not a claim that the
   system distinguishes them.
2. **The alert lifecycle state machine models the alert record's delivery lifecycle** — the
   states actually persisted by `AlertSpool` (`pending`, `delivered`, `dead`) plus the
   pre-persistence construction step. The platform has **no** analyst triage lifecycle, so
   states such as Acknowledged, Investigating and Closed appear only as a clearly separated
   designed extension, never as current behaviour.
3. **Endpoint enrichment is modelled as a pipeline stage, not a class**, because the
   implementation is two free functions applied in a lambda in `main.cpp`. The stage is
   real; a component named "Enricher" is not.
4. **The investigation scenario uses `DET-PROC-011`**, the rule verified end to end on real
   Windows telemetry in `PANOPTICON_V1.md`. The diagram is labelled a scenario view.
5. **Deployment shows the single-host development topology**, the only topology the
   repositories support. A multi-host topology would require the designed backend.

---

## 9. Discrepancies found between documentation and implementation

Recorded during the audit on 2026-09-04. Diagrams follow the **implementation** in every
case below and mark the affected element accordingly.

| # | Claim | Location | Reality |
|---|---|---|---|
| 1 | "Automated Process Kill / Quarantine"; "Active Response / Process Termination Playbooks" | `docs/OFFICER_INTEGRATION.md`, engine `README.md` | `EndpointRemediationEngine` builds `RemediationAction` dataclasses and appends them to `action_history`. There is no `subprocess`, `os.kill`, `winreg` or socket call anywhere in `src/remediation/`. Response is **simulated bookkeeping**. |
| 2 | Remediation status is `"SUCCESS"` when `dry_run=False`, and `main.py` constructs `EndpointRemediationEngine(dry_run=False)` | `src/remediation/engine.py`, `src/main.py` | The label says SUCCESS while nothing executes. The honest status for every action in the current build is SIMULATED. Diagrams use the `SIMULATED` tag. |
| 3 | "Unbuffered NDJSON Pipe / Named Pipe"; the `LiveTelemetryStream` docstring says "subprocess, Named Pipe, or NDJSON file" | `docs/OFFICER_INTEGRATION.md`, `src/ingestion/live_stream.py` | Only two paths exist: `stream_from_file` and `stream_from_officer_process`. There is **no named-pipe implementation**. |
| 4 | "Schema 0.2" as the integration contract | `OFFICER_INTEGRATION.md` heading and body | The agent emits `schema_version` **0.3** (`kSchemaVersion` in `panopticon_event.hpp`) and the engine accepts `("0.1","0.2","0.3")`. The document's example payload is a valid but outdated 0.2 record. |
| 5 | "84+ Wazuh/Sigma Rules"; "Tests: 43 Passed" badge | engine `README.md` | Actual: **86** rule YAML files and **151 passed, 2 skipped**. The badges are stale. |
| 6 | Root `CLAUDE.md`: `--auto-remediate` "is `store_true, default=True` with no counterpart — impossible to disable" | root `CLAUDE.md` against `src/main.py` | Already fixed. The flag now uses `argparse.BooleanOptionalAction`, so `--no-auto-remediate` works. |
| 7 | Root `CLAUDE.md` describes a two-repository workspace, process-creation-only telemetry and Schema 0.2 | root `CLAUDE.md` | Stale. There are **three** repositories (the console exists), **five** telemetry families, and Schema **0.3**. |
| 8 | CMake `project(officer VERSION 0.2.0)` | `CMakeLists.txt` against `panopticon_event.hpp` | The emitted `agent.version` is `0.3.0` (`kAgentVersion`). The build-system version was not bumped. Cosmetic, but the two disagree. |
| 9 | `detection-ingestion-boundary.md` describes ingestion authentication, an immutable observation store and cross-source reconciliation | that document | Entirely **designed**, not implemented. Diagrams show it dashed and tagged. |
| 10 | Console `README` says 22 tests pass; the V2 document says 24 | console `README.md` | 24 tests pass today. The lower figure is stale. |

---

## 10. Known limitations of this diagram set

- **No runtime performance data is depicted.** The known agent event-loss behaviour under
  high Sysmon event ID 1 rates (agent `V3_TELEMETRY.md` §9) is a reliability property, not
  a structural one, and is noted in the README rather than drawn.
- **The 86 rules are represented by their structure, not enumerated.** A rule catalogue is
  a table, not a diagram.
- **ARM64 is not drawn separately.** The build is triplet-driven and structurally
  identical; only the validated x64 path is shown, with the ARM64 status noted.
- **`officer-query` appears once**, in the component diagram, marked auxiliary. It sits
  outside the live vertical slice and would distort the flow diagrams.
- **No sequence diagram shows error paths exhaustively.** Each shows the success path plus
  the one failure branch that changes system state (delivery failure, retry, dead).
- **Cloud, identity and enterprise-graph detection stages exist in code** but operate on
  event shapes Officer does not currently produce. They appear in the detection class
  diagram and the detection sequence as engine stages, with a note that Officer telemetry
  does not currently reach stages B, C and F.

---

## 11. Regeneration and change control

When the implementation changes, the diagrams change with it. The procedure is in
`README.md` under "Regenerating a diagram". A change to any of the following **requires** a
review of the whole set:

- `panopticon-agent/schema/event.schema.json` — affects diagrams 2, 4, 5, 7, 13 and 14
- `src/ingestion/officer_adapter.py` or `src/ingestion/telemetry.py` — affects 4, 6, 8, 13 and 14
- `src/reliability/pipeline.py` or `spool.py` — affects 2, 4, 8, 9 and 11
- `src/pipeline_core.py` detection stages — affects 6, 8, 10 and 15
- `panopticon-console/app.py` routes — affects 1, 2, 4, 12 and 15

Bump the version and date at the top of this file with every substantive change.
