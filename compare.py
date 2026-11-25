import argparse, json
from pathlib import Path
import chromadb, networkx as nx
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(timeout=30)
ROOT = Path(__file__).resolve().parent


def embed(t): return [d.embedding for d in client.embeddings.create(model="text-embedding-3-small", input=t).data]


def ask(context: str, q: str) -> tuple[str, int]:
    r = client.chat.completions.create(model="gpt-4o-mini", temperature=0, messages=[
        {"role": "system", "content": "주어진 자료만 근거로 짧게 답한다. 없으면 모른다고 한다."},
        {"role": "user", "content": f"<자료>\n{context}\n</자료>\n질문: {q}"}])
    return r.choices[0].message.content, r.usage.total_tokens


# --- Vector
_col = None
def vector_ctx(q, k=3):
    global _col
    if _col is None:
        _col = chromadb.PersistentClient(str(ROOT / "indexes/vector")).get_or_create_collection("g", metadata={"hnsw:space": "cosine"})
        docs = {p.stem: p.read_text(encoding="utf-8") for p in sorted((ROOT / "data/guides").glob("*.md"))}
        if _col.count() != len(docs):
            _col.upsert(ids=list(docs), documents=list(docs.values()), embeddings=embed(list(docs.values())))
    return "\n\n".join(_col.query(query_embeddings=embed([q]), n_results=k)["documents"][0])


# --- GraphRAG (간단 버전: 질문에 나온 엔티티 주변 관계 + 관련 커뮤니티 요약)
G = nx.read_graphml(ROOT / "indexes/graph/graph.graphml")
COMM = json.loads((ROOT / "indexes/graph/communities.json").read_text(encoding="utf-8"))
def graph_ctx(q):
    ents = [n for n in G.nodes if n in q] or [n for n in G.nodes if any(w in n for w in q.split() if len(w) > 1)]
    lines = [f"{s} --{d['relation']}--> {t}" for e in ents for s, t, d in list(G.out_edges(e, data=True)) + list(G.in_edges(e, data=True))]
    comms = [c["summary"] for c in COMM if set(ents) & set(c["members"])] or [c["summary"] for c in COMM]
    return "관계:\n" + "\n".join(sorted(set(lines))) + "\n\n요약:\n" + "\n".join(comms)


# --- Wiki
WIKI = {p.stem: p.read_text(encoding="utf-8") for p in sorted((ROOT / "indexes/wiki").glob("*.md"))}
def wiki_ctx(q):
    score = {k: sum(w in v for w in q.split()) for k, v in WIKI.items()}
    best = sorted(score, key=lambda k: -score[k])[:2]
    return "\n\n".join(WIKI[k] for k in best)


METHODS = {"vector": vector_ctx, "graph": graph_ctx, "wiki": wiki_ctx}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--question-set", default="eval/questions_graph.json")
    ap.add_argument("--methods", default="vector,graph,wiki")
    a = ap.parse_args()
    qs = json.loads((ROOT / a.question_set).read_text(encoding="utf-8"))
    table = {m: {} for m in a.methods.split(",")}
    for q in qs:
        print(f"\n[{q['type']}] {q['question']}")
        for m in table:
            ans, tok = ask(METHODS[m](q["question"]), q["question"])
            ok = q["answer_contains"] in ans
            table[m].setdefault(q["type"], []).append((ok, tok))
            print(f"  {m:<6} {'O' if ok else 'X'} {tok:>5} tok  {ans[:70]!r}")
    print("\n요약")
    for m, by_type in table.items():
        cells = [f"{t} {sum(o for o, _ in v)}/{len(v)}" for t, v in by_type.items()]
        toks = [tk for v in by_type.values() for _, tk in v]
        print(f"  {m:<6} " + " | ".join(cells) + f" | 평균 {sum(toks)//len(toks)} tok")
