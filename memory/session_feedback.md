---
name: Session Feedback and Workflow Preferences
description: Behavioral guidance from the user about how to collaborate in this project
type: feedback
---

**Memory Rules added to CLAUDE.md on 2026-05-04.**

Rule: At session start, read `memory\MEMORY.md` and all referenced files. If memory doesn't exist, analyze the codebase and create it.
Rule: At session end (user says "cerrar sesion", "bye", "done", "closing", "hasta luego"), synthesize and update memory files.

**Why:** User wants persistent context across sessions without having to re-explain project state each time.

**How to apply:** Always check for `memory\MEMORY.md` before doing any codebase exploration. On session close, write updates before signing off.
