# Working on the ADK template

## Purpose and boundaries

This repository is a reusable Google ADK 2.6 template. The calculator and clock
are small examples that demonstrate the boundary between agent orchestration,
ADK tools, and Python business logic.

Preserve that boundary:

```text
HTTP API -> Workflow -> LlmAgent -> FunctionTool -> Python service
```

- `src/app/components/agents/root/agent.py` exports `root_agent`, a `Workflow`.
- `assistant_agent` is its `LlmAgent` node, configured in `chat` mode to retain session context across turns. Chat agents must be wired directly after `START`.
- `components/tools/custom/` adapts service functions to ADK.
- `services/` contains business logic without ADK imports.
- `instructions/templates/` contains Jinja2 prompts with frontmatter.
- `application.py` creates the ADK API and registers the `AppError` handler.
- `main.py` configures logging and exports the ASGI application.

Do not add interfaces, factories, or layers without a concrete use case.
Keep changes scoped to the user's request. Preserve unrelated local work.
Only commit, push, or publish when requested. Generated `__pycache__` and `.pyc`
files must stay out of version control.

## Commands

Run these from the repository root:

```bash
just install       # uv sync, including development dependencies
just api           # Local API and development UI on 127.0.0.1:8000
just test          # All tests; minimum 83% coverage
just lint          # Ruff checks
just format        # Ruff formatter
just sort-imports  # Ruff import sorting
just pre-commit    # Format, lint, tests
just build         # Docker image
just run           # Local Docker UI, with ADC mounted
```

For a focused test:

```bash
uv run pytest src/test/unit/services/test_time_service.py
uv run pytest src/test/integration/test_application.py
```

Use `uv lock` to regenerate the lockfile after changing dependencies; do not
edit `uv.lock` manually. Datadog is an optional extra (`uv sync --extra datadog`).
Use `uv run --extra datadog` when a command needs to retain that extra.

## Configuration and execution

`Settings` validates environment variables. At module import, `.env` is loaded
into the environment unless `DOCKER_ENV` is set. Existing environment values
win. Google ADK also reads its provider configuration from that environment.

Required variables:

- `GOOGLE_GENAI_USE_VERTEXAI`
- `GOOGLE_CLOUD_PROJECT`
- `GOOGLE_CLOUD_LOCATION`

Defaults: `MODEL=gemini-2.5-flash`, `AGENT_NAME=template_agent`, `DEBUG=false`.

`DEBUG=true` enables ADK's development UI and endpoints. `just api` and the
`local` launcher set it explicitly. The production launcher forces it off.
Authentication belongs at the deployment boundary (platform IAM or an
authenticating proxy); the template does not identify end users. A multi-user
application must authorize the supplied user ID and session ownership.

Default ADK session storage is for local development, and may become in-memory
on cloud platforms. Configure durable services explicitly in `create_app()`
for deployments that need persistence. See the production section in README.

## Adding tools and agents

1. Put reusable Python logic in `services/`.
2. Add a typed ADK function in `components/tools/custom/` and wrap it in
   `FunctionTool`. ADK supports synchronous and asynchronous functions; use
   async for genuinely asynchronous I/O.
3. Convert service validation errors to `ToolExecutionError` at the adapter.
   `handle_tool_error` returns those failures to the model as structured tool
   responses. Unexpected exceptions remain failures.
4. Register the tool on `assistant_agent`, and test its behavior through ADK
   when changing schemas, callbacks, or execution flow.
5. Extend the root workflow's edges for orchestration. A separately discoverable
   agent directory must export a variable named `root_agent` in `agent.py`,
   regardless of the directory name.

Do not log tool arguments or responses wholesale. Do not put credentials in
prompts, exceptions, logs, or test fixtures.

## HTTP contract

- `GET /health`: ADK availability response, `{"status": "ok"}`.
- `GET /list-apps`: discover available agents, including `root`.
- `POST /apps/{app_name}/users/{user_id}/sessions/{session_id}`: create a session.
- `GET /apps/{app_name}/users/{user_id}/sessions/{session_id}`: read a session.
- `POST /run`: execute a turn and return ADK events.
- `POST /run_sse`: stream ADK events; inspect error events even with HTTP 200.
- `GET /docs`: generated API documentation.
- `GET /dev-ui/`: local development mode only.

Custom routes raising `AppError` receive its JSON body and mapped HTTP status.
Expected tool errors are delivered inside the agent turn and can be handled by
the model. These two contracts serve different callers.

## Verification

Both `test_*` and `should_*` test functions are collected. Unit tests cover
services, adapters, callbacks, instructions, and configuration. Integration
tests cover HTTP/SSE execution with a deterministic model, dev/prod endpoints,
HTTP errors, and the shell launcher. Session files stay in temporary folders.

Tests force dummy Google configuration and disable automatic `.env` loading.
For required-setting tests, import `Settings` first, then isolate the process
environment and disable any explicit env file with `_env_file=None`.

Before handing changes back, run relevant tests, `just test`, `just lint`, and
`git diff --check`. Verify the Docker build and startup after changing the
image, dependencies, or launcher. Distinguish these checks from a live Gemini
call or a deployed application. Never report a mocked model as live validation.

## References

- [README](README.md): setup, deployment boundary, optional tracing.
- [Architecture](docs/ARCHITECTURE.md): dependency flow and responsibilities.
- [Services vs tools](docs/SERVICES_VS_TOOLS.md): adapter examples.
- [Tool guidelines](docs/TOOL_GUIDELINES.md): integration choices.
- [Contributing](CONTRIBUTING.md): local verification and contribution workflow.
- [ADK documentation](https://adk.dev/): verify APIs against the locked version.
