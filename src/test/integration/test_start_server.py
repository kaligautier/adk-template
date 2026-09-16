"""Verify launcher modes without binding a port or contacting Datadog."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def launcher(tmp_path):
    shutil.copy2(Path(__file__).resolve().parents[3] / "start_server.sh", tmp_path)
    (tmp_path / "src").mkdir()
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name in ("gunicorn", "uvicorn"):
        command = bin_dir / name
        command.write_text(
            '#!/bin/sh\nprintf "DEBUG=%s\\n" "$DEBUG"\nprintf "%s\\n" "$@"\n'
        )
        command.chmod(0o755)
    tracer = bin_dir / "ddtrace-run"
    tracer.write_text('#!/bin/sh\necho TRACED\nexec "$@"\n')
    tracer.chmod(0o755)

    def run(*args, tracing=None, installed=True):
        if not installed:
            tracer.unlink()
        env = {
            "PATH": f"{bin_dir}:{os.defpath}",
            "DEBUG": "true",
            "HOST": "127.0.0.1",
            "PORT": "8181",
        }
        if tracing is not None:
            env["DD_TRACE_ENABLED"] = tracing
        return subprocess.run(
            ["bash", str(tmp_path / "start_server.sh"), *args],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            text=True,
            timeout=5,
        )

    return run


def should_disable_debug_and_tracing_by_default(launcher):
    result = launcher()
    assert result.returncode == 0, result.stderr
    assert "DEBUG=false" in result.stdout
    assert "TRACED" not in result.stdout
    assert "127.0.0.1:8181" in result.stdout


def should_enable_local_ui_and_reload(launcher):
    result = launcher("local")
    assert result.returncode == 0, result.stderr
    assert "DEBUG=true" in result.stdout
    assert "--reload" in result.stdout
    assert "8181" in result.stdout


def should_enable_tracing_when_requested(launcher):
    result = launcher(tracing="true")
    assert result.returncode == 0, result.stderr
    assert "TRACED" in result.stdout


def should_fail_clearly_if_requested_tracing_is_not_installed(launcher):
    result = launcher(tracing="true", installed=False)
    assert result.returncode != 0
    assert "datadog" in result.stderr.lower()
