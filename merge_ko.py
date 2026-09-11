# -*- coding: utf-8 -*-
"""ko_out/*.json (번역 결과) 을 words.json 의 ko 칸에 합친다.
번역 파일의 키가 실제 id 가 아니라 1..N 줄 번호로 적힌 경우도 순서대로 대응시켜 처리."""
import json, glob, os

words = json.load(open("words.json", encoding="utf-8"))
by_id = {w["id"]: w for w in words["words"]}
filled = 0
for f in sorted(glob.glob("ko_out/*.json")):
    b = os.path.basename(f)[:-5]
    ids = [int(l.split("\t")[0]) for l in open(f"ko_batches/{b}.tsv", encoding="utf-8") if l.strip()]
    m = json.load(open(f, encoding="utf-8"))
    keys = list(m)
    if set(int(k) for k in keys) == set(ids):
        pairs = [(int(k), v) for k, v in m.items()]
    elif len(keys) == len(ids) and [int(k) for k in keys] == list(range(1, len(ids) + 1)):
        pairs = list(zip(ids, m.values()))          # 줄 번호로 적힌 경우 → 순서대로 대응
        print(b, ": 줄번호 키 → 순서대로 대응")
    else:
        print(b, ": 키 불일치, 건너뜀"); continue
    for i, v in pairs:
        if v and v.strip():
            by_id[i]["ko"] = v.strip(); filled += 1

json.dump(words, open("words.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("채워진 한국어 뜻:", sum(1 for w in words["words"] if w["ko"]), "/", len(words["words"]))
