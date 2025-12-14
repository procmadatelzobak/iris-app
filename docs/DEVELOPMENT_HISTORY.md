# Development History

## [2025-12-14] Phase 32 - Admin Task Visibility Fix
### Prompt
Admin dashboard shows no tasks while users see their submissions queued for approval; ensure task workflow matches lore expectations.

### Plan
- [x] Review task workflow (backend serialization, admin auth, websocket updates) to identify why pending tasks are hidden for admins.
- [x] Implement fixes so admins see pending and submitted tasks consistently.
- [x] Update project documentation and note any tests executed.

### Progress Notes
- Task listing API now returns plain status strings to match UI comparisons.
- Admin task fetch, approval, and payout calls now include bearer tokens to satisfy admin-only endpoints.
- Admin dashboard websocket now triggers task refresh when new submissions arrive.

### Outcome
- Testing not run (UI-level change only); manual verification recommended during next session.
