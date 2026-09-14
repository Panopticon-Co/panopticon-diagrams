# Security Policy

`panopticon-diagrams` is a documentation repository: it contains hand-authored,
self-contained HTML/SVG diagram files and two small Python helper scripts
(`_tooling/export_svg.py`, `_tooling/export_png.py`, `_tooling/validate.py`). It
ships no service, no server, and no dependency that runs in production. The
realistic security surface here is narrow — for example, a diagram file that
somehow smuggled in a `<script>` tag or an external asset reference (the
consistency gate in `_tooling/validate.py` already checks for both and fails
the build if either appears), or a supply-chain issue in the `playwright`
dependency used only for local PNG export.

## Reporting a vulnerability

**Do not open a public GitHub issue for a security concern.**

Report it privately using GitHub's Security Advisories feature for this
repository:

<https://github.com/Panopticon-Co/panopticon-diagrams/security/advisories/new>

This lets maintainers assess the report and coordinate a fix before any public
disclosure.

## Response expectations

This is a capstone/research security project maintained on a best-effort
basis. There is no guaranteed response time or SLA. Reports will be
acknowledged and triaged as promptly as maintainer availability allows.

## Scope

In scope:

- The diagram HTML/SVG files in this repository and whether they violate the
  set's own "no script, no remote asset other than the pinned Google Fonts
  stylesheet" rule (enforced by `_tooling/validate.py`).
- The `_tooling/` helper scripts and their dependencies.
- This repository's GitHub Actions workflow (`.github/workflows/validate.yml`).

Out of scope (report to the relevant repository instead):

- `panopticon-agent`, `panopticon-linux-agent`, `panopticon-detection-engine`,
  `panopticon-response-engine`, `panopticon-manager`, `panopticon-console` —
  each accepts its own security reports via its own repository's Security
  Advisories page under the [Panopticon-Co](https://github.com/Panopticon-Co)
  organization.
