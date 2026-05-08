import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "bizcafe-thumbnail-reply" / "scripts" / "select_thumbnail.py"
spec = importlib.util.spec_from_file_location("select_thumbnail", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_select_returns_existing_thumbnail():
    result = mod.select("AI 때문에 개발 공부하기 애매할 때", "ai-tech", 3)[0]
    assert result["exists"] == "true"
    assert Path(result["path"]).parts[0] == "thumbnails"
    assert Path(result["path"]).suffix == ".jpg"


def test_money_tone_prefers_money_or_investing_label():
    results = mod.select("주식 고점인가 불안할 때", "money", 5)
    labels = " ".join(r["label"] for r in results)
    assert any(word in labels for word in ["주식", "투자", "비트코인", "버핏", "돈"])


def test_cli_json_output_is_valid(tmp_path):
    import json
    import subprocess

    proc = subprocess.run(
        ["python3", str(SCRIPT), "그냥 위로가 필요할 때", "--tone", "empathy", "--limit", "2", "--json"],
        check=True,
        text=True,
        capture_output=True,
    )
    data = json.loads(proc.stdout)
    assert len(data) == 2
    assert all(item["exists"] == "true" for item in data)
