# 주의: 문서마다 LLM을 여러 번 호출합니다. 세션 중에는 실행하지 마세요.
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
ROOT = Path(__file__).resolve().parent.parent
PROMPT = ("다음 사내 문서에서 (주어, 관계, 대상) 삼중항을 JSON 배열로 추출하라. "
          "문서 ID(SEC-xx, EQ-xx), 장비 모델명, 부서명은 표기를 그대로 쓴다. 형식: [[\"SEC-04\", \"참조\", \"SEC-03\"], ...]")
edges = []
for p in sorted((ROOT / "data/guides").glob("*.md")):
    r = client.chat.completions.create(model="gpt-4o-mini", temperature=0, response_format={"type": "json_object"},
        messages=[{"role": "system", "content": PROMPT + ' 최상위 키는 "triples".'},
                  {"role": "user", "content": p.read_text(encoding="utf-8")}])
    edges += [tuple(t) for t in json.loads(r.choices[0].message.content)["triples"]]
print(len(edges), "triples")
(ROOT / "build/triples.json").write_text(json.dumps(edges, ensure_ascii=False, indent=1), encoding="utf-8")
