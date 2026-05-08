#!/usr/bin/env python3
"""Select local BizCafe/BZCF thumbnails for SNS-style reaction replies."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_METADATA = ROOT / "data" / "labels_simple.csv"
THUMB_DIR = ROOT / "thumbnails"

TONE_KEYWORDS = {
    "encouraging": "할수 성공 응원 믿 betting 성장 미래 가능 해보자 가자 웅장".split(),
    "skeptical": "정말요 호들갑 객관적 탁상공론 가스라이팅 패배자 어렵".split(),
    "hype": "쩌는 웅장 미래 독보적 천재 수퍼엘리트 로켓 권력 올인".split(),
    "dry-joke": "정말요 나발 호들갑 그냥 존재 이런날도 맘대로 제발".split(),
    "warning": "하지마 금지 고점 망했다 빼앗기는 위험 걱정 패배자".split(),
    "resignation": "이런날도 존재하기 어렵 패배자 자유롭지 않다 어짜피".split(),
    "life-advice": "인생 조언 행복 욕망 시간관리 아침 루틴 필요한 맘대로 살아가기".split(),
    "money": "돈 주식 투자 비트코인 버핏 블랙록 세일러 고점 경제적 자유".split(),
    "ai-tech": "AI 인공지능 OpenAI 오픈AI 구글 엔비디아 NVIDIA 테슬라 커서 소프트웨어 개발 코딩".split(),
    "work": "일 사업 창업 개발 코딩 시간관리 필요한 생산성 대표 직접".split(),
    "empathy": "죽지 살자 행복 이런날도 괜찮 존재하기 인생 자유롭지".split(),
}

ALIASES = {
    "ai": "ai-tech", "tech": "ai-tech", "technology": "ai-tech", "투자": "money",
    "돈": "money", "일": "work", "work-productivity": "work", "productivity": "work",
    "위로": "empathy", "공감": "empathy", "인생": "life-advice", "조언": "life-advice",
    "경고": "warning", "냉소": "skeptical", "응원": "encouraging", "밈": "dry-joke",
}


def tokenize(text: str) -> list[str]:
    text = text.lower()
    return re.findall(r"[0-9a-zA-Z가-힣]+", text)


def load_items(metadata: Path = DEFAULT_METADATA) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    with metadata.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            label = row.get("label_from_thumbnail_or_title") or row.get("label") or ""
            original = Path(row.get("thumb_file", "")).name
            path = THUMB_DIR / original
            if not path.exists():
                # Metadata points at the old artifact directory; recover by sequence prefix.
                prefix = str(row.get("index", "")).zfill(3) + "_"
                matches = sorted(THUMB_DIR.glob(prefix + "*.jpg"))
                path = matches[0] if matches else path
            items.append({
                "index": row.get("index", ""),
                "label": label,
                "path": str(path.relative_to(ROOT)) if path.exists() else str(path),
                "url": row.get("url", ""),
                "exists": str(path.exists()).lower(),
            })
    return items


def score_item(item: dict[str, str], query: str, tone: str | None) -> tuple[int, list[str]]:
    label = item["label"]
    label_l = label.lower()
    q_tokens = tokenize(query)
    reasons: list[str] = []
    score = 0

    for token in q_tokens:
        if len(token) <= 1:
            continue
        if token in label_l:
            score += 8 if len(token) >= 3 else 3
            reasons.append(f"matches '{token}'")

    normalized_tone = ALIASES.get((tone or "").lower(), (tone or "").lower())
    for keyword in TONE_KEYWORDS.get(normalized_tone, []):
        if keyword.lower() in label_l:
            score += 5
            reasons.append(f"{normalized_tone} tone")

    # General SNS reaction-friendly labels get a small prior.
    for keyword in ("제발", "그냥", "정말요", "하지마", "살자", "미래", "돈", "생각"):
        if keyword in label:
            score += 1

    # Keep deterministic ordering but mildly favor shorter punchy labels.
    score -= max(0, len(label) - 28) // 12
    return score, reasons


def select(query: str, tone: str | None, limit: int) -> list[dict[str, object]]:
    ranked = []
    for item in load_items():
        score, reasons = score_item(item, query, tone)
        ranked.append((score, int(item["index"] or 9999), item, reasons))
    ranked.sort(key=lambda x: (-x[0], x[1]))
    results = []
    for score, _, item, reasons in ranked[:limit]:
        out = dict(item)
        out["score"] = score
        out["reason"] = "; ".join(dict.fromkeys(reasons)) or "best available vibe match"
        results.append(out)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Situation or desired reply vibe")
    parser.add_argument("--tone", help="Optional tone/category, e.g. ai-tech, money, warning, empathy")
    parser.add_argument("--limit", type=int, default=5, help="Number of candidates to return")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a table")
    args = parser.parse_args(argv)

    if args.limit < 1:
        parser.error("--limit must be at least 1")
    results = select(args.query, args.tone, args.limit)
    missing = [r for r in results if r["exists"] != "true"]
    if missing:
        print("error: selected thumbnail path does not exist", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"{r['score']:>3}  {r['path']}  | {r['label']}  # {r['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
