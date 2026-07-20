# AI Agent Guidelines

This repository's AI agent instructions are organized under [`ai/`](./ai). Always read the relevant guide(s) before making changes.

## Required Reading

Start with:

- [`ai/CODE_STYLE_GUIDE.md`](./ai/CODE_STYLE_GUIDE.md) — general coding standards, clean code principles, naming conventions, docstring requirements, formatting rules, import organization, and maintainability guidelines.

Then read the framework-specific guide:

- [`ai/DUCK_PROJECT_GUIDE.md`](./ai/DUCK_PROJECT_GUIDE.md) — Duck Framework architecture, project structure, lifecycle patterns, conventions, and framework-specific development rules.

For UI/component work, also read:

- [`ai/HTML_COMPONENTS_GUIDE.md`](./ai/HTML_COMPONENTS_GUIDE.md) — how to build and structure Lively/component-based HTML, component composition patterns, styling, events, and UI best practices.

For security-sensitive changes, also read:

- [`ai/SECURITY_GUIDE.md`](./ai/SECURITY_GUIDE.md) — secure coding practices, input validation, authentication, authorization, secrets management, dependency considerations, and common security protections.

---

## Guide Selection

Always apply:

- `CODE_STYLE_GUIDE.md` for all code changes.
- `SECURITY_GUIDE.md` whenever handling user input, authentication, authorization, data storage, APIs, file uploads, credentials, or security-related functionality.

Apply additional guides based on the task:

- Backend, framework, architecture, or project structure changes:
  - `DUCK_PROJECT_GUIDE.md`

- HTML components, pages, UI, styling, or frontend-related changes:
  - `HTML_COMPONENTS_GUIDE.md`

- Security-sensitive functionality:
  - `SECURITY_GUIDE.md`

When multiple guides apply, follow all of them. If rules conflict, prefer the more specific guide for that area while still maintaining the general standards from `CODE_STYLE_GUIDE.md`.

---

## Before Making Changes

- Inspect existing code patterns before introducing new ones.
- Reuse existing components, utilities, and conventions.
- Avoid unnecessary files, abstractions, or refactors.
- Keep changes focused and consistent with the existing codebase.
- Preserve existing documentation, comments, and established patterns.
