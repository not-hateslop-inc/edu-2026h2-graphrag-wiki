# 주의: LLM 호출 비용이 큽니다. 세션 중에는 실행하지 마세요.
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
ROOT = Path(__file__).resolve().parent.parent
docs = "\n\n".join(f"=== {p.stem} ===\n{p.read_text(encoding='utf-8')}" for p in sorted((ROOT / 'data/guides').glob('*.md')))
TOPICS = {"장비 반납": "equipment-return", "외부 미팅 보안": "external-meeting-security", "계정 관리": "account-management", "생성형 AI 사용": "genai-usage"}
for t, slug in TOPICS.items():
    r = client.chat.completions.create(model="gpt-4o-mini", temperature=0, messages=[
        {"role": "system", "content": "사내 위키 편집자다. 주어진 문서만 근거로 주제 정리 페이지를 마크다운으로 쓰고, 마지막 줄에 '근거: 문서ID, ...'를 단다."},
        {"role": "user", "content": f"주제: {t}\n\n{docs}"}])
    (ROOT / f"indexes/wiki/{slug}.md").write_text(r.choices[0].message.content, encoding="utf-8")
    print("wrote", t)
