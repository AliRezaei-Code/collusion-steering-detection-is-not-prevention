import json
from unittest.mock import patch

from collusion_steering.cli_client import LocalCLIClient


def _fake_proc(stdout: str = "", returncode: int = 0, stderr: str = ""):
    class Proc:
        pass

    proc = Proc()
    proc.stdout = stdout
    proc.stderr = stderr
    proc.returncode = returncode
    return proc


def test_cli_client_extracts_text():
    events = "\n".join(
        [
            json.dumps({"type": "step_start"}),
            json.dumps({"type": "text", "part": {"text": "hello"}}),
            json.dumps({"type": "text", "part": {"text": "world"}}),
            json.dumps({"type": "step_finish"}),
        ]
    )
    client = LocalCLIClient(max_retries=1)
    with patch("subprocess.run", return_value=_fake_proc(events)):
        result = client.chat("ignored", [{"role": "user", "content": "hi"}])
    assert result["text"] == "hello\nworld"
    assert result["model"] == client.model_id


def test_cli_client_retries_on_nonzero_exit():
    client = LocalCLIClient(max_retries=2)
    with patch(
        "subprocess.run",
        side_effect=[
            _fake_proc(returncode=1, stderr="boom"),
            _fake_proc(json.dumps({"type": "text", "part": {"text": "ok"}})),
        ],
    ):
        result = client.chat("ignored", [{"role": "user", "content": "hi"}])
    assert result["text"] == "ok"


def test_flatten_includes_roles_and_json_instruction():
    prompt = LocalCLIClient._flatten(
        [
            {"role": "system", "content": "sys"},
            {"role": "user", "content": "usr"},
        ],
        {"type": "json_object"},
    )
    assert "[SYSTEM]" in prompt
    assert "[USER]" in prompt
    assert "Return only one JSON object" in prompt
    assert "Do not use any tools" in prompt
