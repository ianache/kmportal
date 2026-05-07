# AGENT.md

This file provides guidance to Gemini  when working with code in this repository.

## Memory Rules

- **Session start** — at the beginning of every session, check if `memory\MEMORY.md` exists and read it along with all files it references. If it does not exist, analyze the codebase (git log, key source files, `.planning/STATE.md`, `ROADMAP.md`) and synthesize an understanding of the repository before proceeding and create `memory\MEMORY.md`.
- **Session end** — when the user signals the session is ending (e.g., "bye", "done", "closing", "hasta luego") or explicitly asks to save memory, update the memory files under `memory\` to reflect any decisions made, code changes introduced, new patterns observed, or project state changes that occurred during the session. Keep MEMORY.md index concise (one line per entry).

## Working Rules

- **Use Graphify MCP** — always explore the codebase using Graphify MCP tool to understand the codebase structure.
- **Research and plan before coding** — always explore the codebase, gather context, and produce a clear plan before writing any code. Get approval on the plan first.
- **No assumptions** — never assume requirements, intent, or expected behavior. Ask for feedback whenever anything is unclear or ambiguous.
- **Always verify results** — after implementing anything, test the output to confirm it works as expected before considering the task done.

## UX/UI Rules

- **Google Stitch** - Siempre que se solicite un diseño de página o sistema, utiliza la herramienta google-stitch vía MCP para obtener los esquemas actuales antes de generar código Vue o Spring Boot.

## Project Status

Phases 1-7 are complete. Core infrastructure, API, ingestion, search, BFF, and core micro-UIs (Search, Domains, Ingestion) are implemented and functional.

**Current Focus:** Phase 8 — Admin and API keys. Implementing the Admin micro-UI and API key lifecycle management.

## Project Name

`Knowledge Management Center` — a personal knowledge management tool/system.
