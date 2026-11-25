# edu-2026h2-graphrag-wiki

2026 하반기 9회차 **GraphRAG와 LLM Wiki** (EDU-2026-H2-09, 2026-11-05) 실습 저장소입니다. 환경: Python 3.12, Conda 환경 `hs-2026h2`

같은 가이드 8건(`data/guides/`)을 세 방식으로 정리해 두었습니다.

| 경로 | 내용 |
| --- | --- |
| `indexes/vector/` | 실행할 때 `compare.py`가 만듭니다 (임베딩만 쓰므로 저렴) |
| `indexes/graph/graph.graphml` | LLM으로 추출한 엔티티·관계 그래프 |
| `indexes/graph/communities.json` | 커뮤니티(묶음)와 요약 |
| `indexes/wiki/*.md` | LLM이 미리 작성한 주제별 Wiki 페이지 |
| `build/` | 인덱스를 직접 다시 만드는 스크립트 (**세션 중 실행 금지**, 교육용 키 한도 소모가 큼) |
| `eval/questions_graph.json` | 사실 3 / 관계 3 / 전체 요약 2 |
| `compare.py` | 같은 질문을 세 방식으로 답하고 비교 |

```bash
python compare.py --question-set eval/questions_graph.json
python compare.py --methods vector,wiki     # GraphRAG 빼고 먼저
```

> 그래프에는 의도적으로 추출 오류가 하나 남아 있습니다 (`HS-NB14`와 `HS NB14 노트북`). 찾아보세요.
