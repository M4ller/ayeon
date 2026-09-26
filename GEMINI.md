# Ayeon — Project Operating Instructions

## 1. Project identity

Ayeon is a portable-first cognitive core for an intelligent assistant.

The project prioritizes:

- determinism;
- zero-trust architecture;
- explicit contracts;
- strict separation of responsibilities;
- traceability;
- verifiable side effects;
- safe memory handling;
- maintainability;
- incremental development.

Do not treat Ayeon as a prototype that can be freely rewritten.

Respect the existing architecture before proposing structural changes.

---

## 2. Source of truth

The Git repository is the source of truth.

Before starting significant work, inspect:

```bash
git status
git log -5 --oneline
```

Never assume repository state.

Never claim that a commit, push, test run or modification succeeded unless the command output confirms it.

Do not rewrite or discard existing work unless explicitly requested.

---

## 3. Current project baseline

At the time this file was created, the current repository baseline is:

```text
branch: master
HEAD: 9fa0ad1
tests: 471 passing
ruff: clean
```

Recent commits include:

```text
9fa0ad1 feat: add lexical semantic memory relevance
16d00c4 security: treat verified memory as contextual data
1ef48f6 refactor: format verified memory prompts deterministically
7827ffc feat: use verified memory in cognition prompts
4e5eb7e feat: integrate verified memory into cognitive context
```

Treat this only as a historical baseline.

Always verify the current state before working.

---

## 4. Mandatory development method

Work incrementally.

The preferred workflow is:

```text
inspect
↓
understand
↓
propose smallest useful change
↓
modify
↓
run focused tests
↓
review result
↓
run broader tests
↓
continue
```

Prefer:

```text
small change
→ focused test
→ result
→ next change
```

Avoid:

```text
