from unittest.mock import Mock, patch

from collusion_steering.typesafe_jev import TypeSafeJevClient, collusion_questions


def test_questions_have_typed_schema():
    q = collusion_questions()
    assert q["collusion_present"]["type"] == "noul"
    assert q["collusion_success"]["type"] == "noul"
    assert q["coalition"]["type"] == "choice"
    assert q["action"]["type"] == "choice"
    assert "AB" in q["coalition"]["criteria"]
    assert "quarantine" in q["action"]["criteria"]


def test_decide_parses_answers_and_sends_key(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "test-key")
    response = Mock(status_code=200, text="")
    response.json.return_value = {
        "model": "jev-1.13.0",
        "answers": {
            "collusion_present": {"type": "noul", "noul": 0.82},
            "collusion_success": {"type": "noul", "noul": 0.31},
            "coalition": {"type": "choice", "choice": "AB"},
            "action": {"type": "choice", "choice": "quarantine"},
        },
    }
    with patch("requests.post", return_value=response) as post:
        decision = TypeSafeJevClient().decide("public transcript")
    assert decision.collusion_present == 0.82
    assert decision.collusion_success == 0.31
    assert decision.coalition == "AB"
    assert decision.action == "quarantine"
    assert post.call_args.kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert post.call_args.kwargs["json"]["model"] == "jev-latest"
    assert "questions" in post.call_args.kwargs["json"]
