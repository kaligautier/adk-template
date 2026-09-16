"""Exercise the HTTP server and ADK runner with a deterministic model."""

import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from pydantic import Field

from app.application import create_app
from app.config.settings import Settings, settings
from app.utils.error import InvalidInputError, ToolExecutionError


class ScriptedLlm(BaseLlm):
    model: str = "test-model"
    tool_name: str = "calculate"
    tool_args: dict
    calls: int = 0

    async def generate_content_async(self, llm_request, stream=False):
        self.calls += 1
        if self.calls == 1:
            part = types.Part(
                function_call=types.FunctionCall(
                    id="test-call", name=self.tool_name, args=self.tool_args
                )
            )
        else:
            response = next(
                part.function_response.response
                for content in reversed(llm_request.contents)
                for part in content.parts
                if part.function_response
            )
            part = types.Part(text=json.dumps(response))
        yield LlmResponse(content=types.Content(role="model", parts=[part]))


class ConversationLlm(BaseLlm):
    model: str = "test-model"
    requests: list[list[types.Content]] = Field(default_factory=list)

    async def generate_content_async(self, llm_request, stream=False):
        self.requests.append(
            [content.model_copy(deep=True) for content in llm_request.contents]
        )
        yield LlmResponse(
            content=types.Content(
                role="model", parts=[types.Part(text="I will remember it.")]
            )
        )


@pytest.fixture
def app(monkeypatch, tmp_path):
    # Keep the real loader and SQLite session service in an isolated directory.
    agents_dir = tmp_path / "agents"
    shutil.copytree(
        Path(settings.AGENT_DIR),
        agents_dir,
        ignore=shutil.ignore_patterns("__pycache__", ".adk"),
    )
    monkeypatch.setattr(Settings, "AGENT_DIR", property(lambda self: str(agents_dir)))
    monkeypatch.setattr(settings, "DEBUG", False)
    return create_app()


@pytest.fixture
def client(app):
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client


def should_disable_dev_ui_in_production(client):
    assert client.get("/dev-ui/").status_code == 404
    schema = client.get("/openapi.json").json()
    assert "/run" in schema["paths"]
    assert not any(path.startswith("/dev/") for path in schema["paths"])


def should_enable_dev_ui_explicitly(app, monkeypatch):
    monkeypatch.setattr(settings, "DEBUG", True)
    with TestClient(create_app()) as client:
        assert client.get("/dev-ui/").status_code == 200


def should_expose_one_health_route_and_application_metadata(app, client):
    assert client.get("/health").json() == {"status": "ok"}
    assert sum(getattr(route, "path", None) == "/health" for route in app.routes) == 1
    assert client.get("/openapi.json").json()["info"]["title"] == settings.APP_NAME


@pytest.mark.parametrize(
    "error", [InvalidInputError("Invalid request"), ToolExecutionError("Unavailable")]
)
def should_map_application_errors_to_http(app, client, error):
    @app.get("/test-error")
    async def raise_error():
        raise error

    response = client.get("/test-error")

    assert response.status_code == error.status_code
    assert response.json() == error.to_dict()


@pytest.mark.parametrize("endpoint", ["/run", "/run_sse"])
def should_send_previous_session_turns_to_the_model(client, monkeypatch, endpoint):
    llm = ConversationLlm()
    monkeypatch.setattr(LlmAgent, "canonical_model", property(lambda self: llm))
    session_path = "/apps/root/users/test-user/sessions/test-session"
    assert client.post(session_path, json={}).status_code == 200
    prompts = ["Remember MISTRALABC123.", "What did I ask you to remember?"]

    for prompt in prompts:
        response = client.post(
            endpoint,
            json={
                "appName": "root",
                "userId": "test-user",
                "sessionId": "test-session",
                "newMessage": {"role": "user", "parts": [{"text": prompt}]},
                "streaming": endpoint == "/run_sse",
            },
        )
        assert response.status_code == 200
        events = (
            response.json()
            if endpoint == "/run"
            else [
                json.loads(line.removeprefix("data: "))
                for line in response.text.splitlines()
                if line.startswith("data:")
            ]
        )
        assert events
        assert not any("error" in event or "errorCode" in event for event in events)

    assert len(llm.requests) == 2
    assert [
        (content.role, part.text)
        for content in llm.requests[1]
        for part in content.parts
        if part.text
    ] == [
        ("user", prompts[0]),
        ("model", "I will remember it."),
        ("user", prompts[1]),
    ]
    session = client.get(session_path).json()
    assert sum(event["author"] == "user" for event in session["events"]) == 2


@pytest.mark.parametrize("endpoint", ["/run", "/run_sse"])
@pytest.mark.parametrize(
    ("tool_name", "tool_args", "expected_error"),
    [
        ("calculate", {"operation": "add", "a": 5, "b": 3}, False),
        ("calculate", {"operation": "divide", "a": 10, "b": 0}, True),
        ("get_current_time", {"timezone": "Mars/Olympus"}, True),
    ],
)
def should_complete_agent_turn_after_tool_response(
    client, monkeypatch, endpoint, tool_name, tool_args, expected_error
):
    llm = ScriptedLlm(tool_name=tool_name, tool_args=tool_args)
    # Patch model resolution, including agents materialized by the workflow.
    monkeypatch.setattr(LlmAgent, "canonical_model", property(lambda self: llm))
    session = client.post("/apps/root/users/test-user/sessions/test-session", json={})
    assert session.status_code == 200

    response = client.post(
        endpoint,
        json={
            "appName": "root",
            "userId": "test-user",
            "sessionId": "test-session",
            "newMessage": {"role": "user", "parts": [{"text": "Use the tool"}]},
        },
    )

    assert response.status_code == 200
    events = (
        response.json()
        if endpoint == "/run"
        else [
            json.loads(line.removeprefix("data: "))
            for line in response.text.splitlines()
            if line.startswith("data:")
        ]
    )
    assert not any("error" in event or "errorCode" in event for event in events)
    tool_response = next(
        part["functionResponse"]["response"]
        for event in events
        for part in event.get("content", {}).get("parts", [])
        if "functionResponse" in part
    )
    if expected_error:
        assert tool_response["status"] == "error"
        assert tool_response["error_code"] == "TOOL_EXECUTION_ERROR"
    else:
        assert tool_response["result"] == 8
    assert llm.calls == 2
    assert any(
        "text" in part
        for event in events
        for part in event.get("content", {}).get("parts", [])
    )
