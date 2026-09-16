"""Exercise dotenv loading through the real Just recipe, without a Docker daemon."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest


@pytest.fixture
def run_recipe(tmp_path):
    just = shutil.which("just")
    assert just is not None, "Install Just to run the recipe integration tests"
    shutil.copy2(Path(__file__).resolve().parents[3] / "justfile", tmp_path)
    (tmp_path / ".env").write_text(
        'GOOGLE_GENAI_USE_VERTEXAI="true"\n'
        'GOOGLE_CLOUD_PROJECT="file-project"\n'
        'GOOGLE_CLOUD_LOCATION="europe-west1"\n'
        'APP_NAME="Agent with spaces"\n'
    )
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    docker = bin_dir / "docker"
    # Model Docker's environment options at the process boundary. The recipe
    # and Just's dotenv parsing run unchanged; no credentials or daemon are used.
    docker.write_text(
        f"#!{sys.executable}\n"
        + dedent("""\
            import argparse
            import json
            import os
            from pathlib import Path

            parser = argparse.ArgumentParser()
            parser.add_argument("-e", "--env", action="append", default=[])
            parser.add_argument("--env-file", action="append", default=[])
            options, _ = parser.parse_known_args()
            environment = {}
            for filename in options.env_file:
                for line in Path(filename).read_text().splitlines():
                    if line and not line.startswith("#"):
                        name, _, value = line.partition("=")
                        environment[name] = value
            for item in options.env:
                name, separator, value = item.partition("=")
                if separator:
                    environment[name] = value
                elif name in os.environ:
                    environment[name] = os.environ[name]
            print(json.dumps(environment))
            """)
    )
    docker.chmod(0o755)

    def run(**overrides):
        result = subprocess.run(
            [just, "run"],
            cwd=tmp_path,
            env={
                "PATH": f"{bin_dir}:{os.defpath}",
                "CLOUDSDK_CONFIG": str(tmp_path / "gcloud"),
                **overrides,
            },
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode == 0, result.stderr
        return json.loads(result.stdout)

    return run


def should_pass_unquoted_dotenv_values_to_container(run_recipe):
    environment = run_recipe()

    assert environment["GOOGLE_GENAI_USE_VERTEXAI"] == "true"
    assert environment["GOOGLE_CLOUD_PROJECT"] == "file-project"
    assert environment["APP_NAME"] == "Agent with spaces"
    assert "PORT" not in environment


def should_prefer_shell_environment_over_dotenv(run_recipe):
    environment = run_recipe(GOOGLE_CLOUD_PROJECT="shell-project")

    assert environment["GOOGLE_CLOUD_PROJECT"] == "shell-project"
