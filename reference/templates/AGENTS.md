# AGENTS.md: <project name>

<One sentence: what this project is and who uses it.>

## Layout
- `<src>/` <what lives here>. `<file>` owns <the logic agents get wrong>.
- `<tests>/` <test framework>. `docs/<spec>.md` defines <behavior>.
- `<protected folder>/` read-only for agents.

## Commands
- Install: `<command>`
- All tests: `<command>`
- One test file: `<command>`
- Lint and types: `<command>`
- Start the app: `<command>`

## Rules
<!-- Add a rule only after you have seen the failure it prevents. Note the PR or issue. -->
- <Rule that prevents a real, observed mistake.> (from #<issue>)
- Do not edit or delete existing tests. Add new tests next to them.
- Do not add dependencies without asking.

## Where to look
- Architecture: `docs/architecture.md`
- Current plan: `docs/plans/active/`
- Decisions: `docs/decisions/`

## Done means
<Checks that must pass.> Your final message lists files changed, tests run with
results, and any assumptions you made.
