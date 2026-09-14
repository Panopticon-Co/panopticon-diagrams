## Summary

<!-- One or two sentences: which diagram(s) changed and why. -->

## Changes

<!-- What changed in each file. Note if a fact shared across diagrams
     (a class name, field, count, or flow direction) was updated, and list
     every other diagram in DIAGRAM_SPECIFICATION.md §11 that shares it. -->

## Testing

<!-- Confirm `_tooling/validate.py` was run against current sibling
     checkouts (panopticon-agent, panopticon-manager,
     panopticon-detection-engine, panopticon-console,
     panopticon-linux-agent) and paste its final line. If it could not be
     run locally, say so and why. -->

## Security Impact

<!-- Does this change add a <script>, a remote asset other than the pinned
     Google Fonts stylesheet, or anything else that widens this repo's
     narrow security surface (see SECURITY.md)? Usually "None." -->

## Documentation

<!-- Does README.md, DIAGRAM_SPECIFICATION.md, or CONTRIBUTING.md need a
     matching update? If a diagram's status (Implemented/Designed/Planned/
     Simulated) changed, confirm it is tagged correctly per
     DIAGRAM_SPECIFICATION.md §2. -->

## Cross-Repository Impact

<!-- Does this change reflect a change in panopticon-agent,
     panopticon-manager, panopticon-detection-engine, panopticon-console,
     panopticon-linux-agent, or panopticon-response-engine? Link the
     source commit/PR that motivated it. -->

## Checklist

- [ ] I read `DIAGRAM_SPECIFICATION.md` before making this change
- [ ] Every unimplemented/designed/simulated element is dashed and tagged
- [ ] `_tooling/export_svg.py` and `_tooling/export_png.py` were re-run and
      the derived `.svg`/`.png` files are included in this PR
- [ ] I opened the rendered `.png` and visually checked for label/connector
      overlaps
- [ ] `_tooling/validate.py` passes (or CI is expected to confirm it)
- [ ] No new class, method, field, or count was invented — everything
      asserted exists in the referenced source repository
