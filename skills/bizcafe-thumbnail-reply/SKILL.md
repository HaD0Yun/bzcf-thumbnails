# BizCafe Thumbnail Reply

Use this skill when the user wants to pick a BizCafe/BZCF thumbnail, screenshot, or reaction image as a short SNS-style reply instead of writing a normal one-line response. Triggers include requests like "비즈카페 섬네일로 답장", "BZCF reaction image", "상황별 스크린샷 골라줘", or "한줄 답변 대신 쓸 짤".

## Workflow

1. Read the user's situation and infer the intended tone: encouraging, skeptical, hype, dry joke, warning, resignation, life advice, money/investing, AI/tech, work/productivity, or casual empathy.
2. Run the selector from the repository root:

   ```bash
   python3 skills/bizcafe-thumbnail-reply/scripts/select_thumbnail.py "<situation>" --tone <tone> --limit 5
   ```

   Omit `--tone` if the tone is unclear; use `--json` when another tool needs structured output.
3. Prefer the top result, but sanity-check that the label actually matches the situation. If the top result is too literal or awkward, choose the next better candidate.
4. Verify the returned `path` exists under `thumbnails/`. Do not invent paths and do not add/download images.
5. Reply compactly with:
   - thumbnail path
   - optional caption (SNS one-liner)
   - brief reason if helpful

## Selection guidance

- Match both content and vibe. A slightly funnier emotional match beats a keyword-only match.
- For "stop overthinking / focus" vibes, prefer labels like `잡생각 금지`, `제발 필요한 일만 하세요`, or `생각좀 하면서 살자`.
- For "let it go / live your life" vibes, prefer `그냥 존재하기`, `자기 인생을 살자`, `어짜피 한번인데 맘대로 사세요`, or `이런날도 있지 뭐`.
- For AI/product/tech optimism, prefer AI, OpenAI, Google, NVIDIA, Tesla, Cursor, or Silicon Valley related labels.
- For investing/money warnings, prefer Buffett, Howard Marks, Bitcoin, BlackRock, or `주식 지금 고점임` labels.
- If multiple results are close, return 2-3 options with different tones rather than over-explaining.
