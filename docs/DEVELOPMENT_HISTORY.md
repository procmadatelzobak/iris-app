# Development History

## [2025-12-14] Phase 32 - Lore Web Viewer
### Prompt
- Convert `/docs/iris/lore` markdown archive into an embeddable web app and integrate it as a dedicated tab in the ROOT dashboard.

### Plan
- [x] Build a static lore website in `/doc/iris/lore-web/` with navigation between all lore modules.
- [x] Expose the new site through FastAPI so it can be embedded inside the application UI.
- [x] Add a ROOT dashboard tab that hosts the lore viewer inside a reusable container.
- [x] Reconcile project documentation and status logs with the new functionality.

### Outcome
- Generated styled HTML pages for every lore document, preserving the existing folder structure and cross-links.
- Mounted the lore site at `/lore-web` and embedded it inside a new ROOT dashboard tab for easy access.
- Updated project logs to reflect the new documentation surface and integration work.

### Tests
- Not run (UI/docs-only change; no automated coverage available for the static embed).
