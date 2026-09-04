# Panopticon Diagram Set

The complete UML and software-architecture diagram set for the **Panopticon&Co** endpoint
detection platform. Fifteen diagrams, each one derived from the code and documents in
`panopticon-agent`, `panopticon-detection-engine` and `panopticon-console`, and each one
checked against the working tree on **2026-09-04**.

The governing contract for this set is [`DIAGRAM_SPECIFICATION.md`](DIAGRAM_SPECIFICATION.md).
Read it before changing any diagram. It records the source-of-truth hierarchy, the
terminology, the consistency rules every diagram obeys, the assumptions, and the ten
discrepancies found between the repositories' documentation and their implementation.

---

## Why this is a separate repository

This diagram set lives in its own repository, sibling to `panopticon-agent`,
`panopticon-detection-engine` and `panopticon-console`, because it spans all three. Putting
the detection-engine class model inside `panopticon-agent`, for instance, would violate the
project's one-way polyrepo boundary. Nothing here is imported by any of those repositories'
builds; the relationship runs the other way — every diagram here is derived from their code
and documentation.

---

## What is in the set

Every diagram ships as three files with the same basename: a self-contained **`.html`**
source, a standalone **`.svg`**, and a 2x **`.png`**.

### Context and architecture

| Diagram | File | What it answers |
|---|---|---|
| System context | [`context/panopticon-system-context.html`](context/panopticon-system-context.html) | Who uses Panopticon, what it observes, and where its boundary is. Three human roles, one system actor, three external Windows systems. |
| High-level architecture | [`architecture/panopticon-high-level-architecture.html`](architecture/panopticon-high-level-architecture.html) | How a Windows event becomes a visible alert, in nine components across two zones. Also states, in a dashed panel, the backend that is designed but not built. |

### UML

| Diagram | File | What it answers |
|---|---|---|
| Use case | [`uml/use-case/panopticon-use-case.html`](uml/use-case/panopticon-use-case.html) | What each role can actually do. Seven use cases, two `«include»` and one conditional `«extend»`. Lists, in the footer, the eight use cases deliberately **not** modelled because they are not implemented. |
| Component | [`uml/component/panopticon-component.html`](uml/component/panopticon-component.html) | The nine deployable components and the two ball-and-socket interfaces that are the only cross-repository surfaces. |
| Agent class model | [`uml/class/agent/panopticon-agent-class-model.html`](uml/class/agent/panopticon-agent-class-model.html) | The Officer object model: one collector interface, two realizations, and the raw to enriched to normalized contract chain. |
| Detection engine class model | [`uml/class/detection-engine/panopticon-detection-engine-class-model.html`](uml/class/detection-engine/panopticon-detection-engine-class-model.html) | How a rule's recursive condition tree becomes a detection and then an alert, and where the response recommendation is attached. |
| Telemetry collection sequence | [`uml/sequence/telemetry-collection/panopticon-telemetry-collection-sequence.html`](uml/sequence/telemetry-collection/panopticon-telemetry-collection-sequence.html) | One Sysmon event from the Windows callback to the consumer's bounded queue, including the backpressure case. |
| Detection sequence | [`uml/sequence/detection/panopticon-detection-sequence.html`](uml/sequence/detection/panopticon-detection-sequence.html) | One event dict through rule routing, alert construction, durable persistence and append, with the delivery-failure branch. |
| Response sequence | [`uml/sequence/response/panopticon-response-sequence.html`](uml/sequence/response/panopticon-response-sequence.html) | Where response stops today. Shows the endpoint call that is **never made**, and the designed chain that has no code. |
| End-to-end activity | [`uml/activity/panopticon-end-to-end-activity.html`](uml/activity/panopticon-end-to-end-activity.html) | The whole workflow with its real fork, its real decisions, and an honest ending. |
| Alert lifecycle state machine | [`uml/state/panopticon-alert-lifecycle-state.html`](uml/state/panopticon-alert-lifecycle-state.html) | The states the SQLite spool actually persists, and the transitions between them. |
| Deployment | [`uml/deployment/panopticon-deployment.html`](uml/deployment/panopticon-deployment.html) | One elevated Windows host, five execution environments, seven artifacts, four communication paths. |

### Data and investigation

| Diagram | File | What it answers |
|---|---|---|
| Event data model | [`data/event-data-model/panopticon-event-data-model.html`](data/event-data-model/panopticon-event-data-model.html) | Every block Schema 0.3 defines, with types and nullability, and the rule that exactly one family block must match the event category. |
| Process entity relationships | [`data/process-entity-relationships/panopticon-process-entity-relationships.html`](data/process-entity-relationships/panopticon-process-entity-relationships.html) | What can be joined to what during an investigation, and which join is strong versus heuristic. |
| Attack detection and investigation | [`investigation/panopticon-attack-detection-investigation.html`](investigation/panopticon-attack-detection-investigation.html) | One obfuscated PowerShell launch followed end to end across five lanes, with the exact rule logic that matched. |

---

## Which diagrams describe what

| Status | Where it appears |
|---|---|
| **Current implementation** | All fifteen diagrams. Every solid-stroke element exists in the working tree and is covered by a passing test. |
| **Designed, not implemented** | Only three places, always dashed and tagged: the backend panel in the high-level architecture, the designed response chain in the response sequence, and the restart note in the state machine. |
| **Simulated** | One place: `EndpointRemediationEngine` in the response sequence, tagged `SIMULATED`. |
| **Planned only (roadmap)** | Nowhere. Roadmap items with no design document are excluded from the set entirely. |

No diagram shows an unimplemented element without a dashed stroke and a tag. That rule is
the single most important thing to preserve when updating this set.

---

## Source-of-truth rules

Diagrams follow this order, and the implementation wins over documentation whenever the two
disagree:

1. Approved ADRs, such as `panopticon-agent/docs/adr/003-process-entity-id.md`
2. The canonical schema, `panopticon-agent/schema/event.schema.json`
3. Architecture documents in both repositories
4. The current implementation
5. Component `README.md` and `CLAUDE.md` files
6. Roadmap documents

Ten documentation-versus-implementation discrepancies were found during the audit and are
listed in `DIAGRAM_SPECIFICATION.md` §9. The most consequential: several documents describe
automated process termination and quarantine, but `EndpointRemediationEngine` performs no
`subprocess`, `os.kill`, `winreg` or socket call. Response is bookkeeping.

---

## Naming conventions

- Files are `panopticon-<subject>.html`, kebab-case, matching the `<title>` and the
  `aria-labelledby` identifier prefix inside the file.
- Component names are canonical and never paraphrased: **Officer** (the agent),
  **eyedetect** (the detection engine), **Panopticon Console**, **Panopticon Event**.
- Class and function names are reproduced exactly as they appear in source.
- A **Detection** is a `DetectionResult`. An **Alert** is the persisted record. A
  **response recommendation** is an `ActiveResponseAction`. These three are never used
  interchangeably.

Full terminology table: `DIAGRAM_SPECIFICATION.md` §5.

---

## Architecture diagrams versus UML diagrams

The set deliberately mixes two notations.

- **Architecture notation** is used for the context and high-level architecture diagrams,
  and for the investigation scenario. These answer "how is the system arranged" and use
  zones, typed node fills and labelled connectors. They are not UML and do not pretend to
  be.
- **UML notation** is used wherever the diagram is named UML, and its semantics are
  preserved exactly: hollow triangles for realization, filled diamonds for composition,
  hollow diamonds for aggregation, open arrowheads for dependencies, stick-figure actors
  with ellipse use cases, lifelines with activation bars and combined fragments, initial
  and final pseudostates, fork and join bars, and three-dimensional device nodes.

Where a UML rule and a visual preference conflicted, the UML rule won. For example activity
nodes use a larger corner radius than the rest of the set, because a UML activity must read
as a rounded node rather than a box.

---

## How the diagrams were generated

Each `.html` file is hand-authored inline SVG produced with the **diagram-design** skill,
using its shipped editorial skin unmodified as the Panopticon visual identity. That skin is
light, high-contrast, and prints and projects reliably; consistency across the set is what
gives the identity, not a bespoke palette. Every file passes the skill's
`scripts/self_check.py`, which enforces the accessible-SVG contract and single-file safety.

No diagram uses JavaScript. No diagram loads a remote asset other than the Google Fonts
stylesheet.

---

## Regenerating a diagram

1. Read `DIAGRAM_SPECIFICATION.md` first, especially §6 (cross-diagram consistency rules).
2. Edit the `.html` file directly. It is the source; the `.svg` and `.png` are derived.
3. Verify the file still passes the skill's self-check:

```bash
python "$SKILL/scripts/self_check.py" path/to/diagram.html
```

where `$SKILL` is the installed `diagram-design` skill directory.

4. Re-export the `.svg` and `.png` (below).
5. Open the `.png` and look at it. A diagram that passes the self-check can still have a
   label sitting on a connector or a line crossing a box. Three defects in this set were
   found only by looking at the rendered output.
6. If the change affects a shared fact (a class name, a field, a count, a direction of
   flow), check every other diagram listed in `DIAGRAM_SPECIFICATION.md` §11 for the same
   fact.

---

## How to export

Both exports are derived from the `.html` source and are safe to regenerate at any time.

**SVG** — extracts the first `<svg>` node, converts HTML named entities to numeric
references so the file is well-formed XML, injects the Google Fonts `@import`, and writes
`<basename>.svg` beside the source.

**PNG** — renders the `.html` in headless Chromium and screenshots the `<svg>` element with
a transparent background at `device_scale_factor=2`. Requires Playwright:

```bash
pip install playwright
playwright install chromium
```

Use scale 2 for documents and slides, and 3 for print handouts. Never scale below 1.

Both helper scripts ship in [`_tooling/`](_tooling/) and take a directory, processing every
`.html` under it recursively:

```bash
# from the repository root
python _tooling/export_svg.py .        # writes every .svg
python _tooling/export_png.py . 2      # writes every .png at 2x
```

---

## Verifying the set

[`_tooling/validate.py`](_tooling/validate.py) is the automated consistency gate. It runs
292 checks against the three source repositories and fails loudly on any drift. It expects
`panopticon-agent`, `panopticon-detection-engine` and `panopticon-console` checked out as
siblings of this repository — clone all four Panopticon-Co repositories into one parent
directory and it finds them automatically:

```bash
python _tooling/validate.py
```

If your clones live elsewhere, point it at the parent directory that contains all three:

```bash
PANOPTICON_WORKSPACE=/path/to/that/parent/directory python _tooling/validate.py
```

It verifies that every one of the 88 class, method and attribute names asserted anywhere in
the set exists in source; that every schema field named in the data-model diagram exists in
`event.schema.json` with the stated enum and nullability; that the stated counts still hold
(86 rules, 15 rule domains, 13 comparison operators, queue capacity 1024, poll interval
3000 ms, port 8787); that the three spool status constants are unchanged; that
`src/remediation/` still contains no `subprocess`, `os.kill`, `winreg` or socket call, which
is what makes the response diagrams true; that the console still has no `do_POST` or
`do_PUT`; that every diagram declares its accessible title and description and carries no
script; and that no diagram reintroduces a banned term such as "named pipe" or "84+".

Run it after any change to either repository. It found one real error during the initial
build of this set, a rule-domain count that was off by one.

---

## Known limitations

- **No performance data is drawn.** The agent's documented event-loss behaviour under very
  high Sysmon event-ID-1 rates is a reliability property, not a structural one.
- **The 86 rules are represented structurally, not enumerated.** A rule catalogue is a
  table.
- **ARM64 is not drawn separately.** The build is triplet-driven and structurally identical;
  only the validated x64 path is shown.
- **Error paths are not exhaustive.** Each sequence shows the success path plus the one
  failure branch that changes persisted state.
- **Detection stages B, C and F** (cloud, identity, enterprise graph) exist in code but
  operate on event shapes Officer does not currently produce. They appear as stages, with a
  note.

Full list: `DIAGRAM_SPECIFICATION.md` §10.

---

## Suggested use

| Audience | Diagrams |
|---|---|
| Interim report | System context, high-level architecture, event data model |
| Final report | All fifteen, grouped as context, UML, data, investigation |
| Presentation or demo | System context, high-level architecture, investigation scenario, response sequence |
| Onboarding a new contributor | Component, then the two class models, then the telemetry collection sequence |
| Defending the response boundary | Response sequence, then `DIAGRAM_SPECIFICATION.md` §9 row 1 |
