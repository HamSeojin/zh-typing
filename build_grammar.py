# -*- coding: utf-8 -*-
"""grammar_prep.json (공식 HSK 3.0 문법 요목 파싱) + gram_out/*.json (LLM 한국어 설명·번역·정규식) → grammar.json
   예문마다 pypinyin 으로 병음을 붙이고, 정규식이 우리 예문 데이터(sentences.json)에서 몇 문장이나 맞는지 미리 세어 둔다."""
import json, glob, re
from pypinyin import pinyin, Style
prep = {p['i']: p for p in json.load(open('grammar_prep.json', encoding='utf-8'))}
ann = {}
for f in sorted(glob.glob('gram_out/g*.json')):
    for a in json.load(open(f, encoding='utf-8')): ann[a['i']] = a
sents = json.load(open('sentences.json', encoding='utf-8'))['sentences']
def py(zh): return ' '.join(p[0] for p in pinyin(zh, style=Style.TONE))
out, nomatch, badre = [], 0, 0
for i in sorted(prep):
    p, a = prep[i], ann.get(i)
    if not a: print('주석 없음', i); continue
    ex = [{'zh': z, 'py': py(z), 'ko': k} for z, k in zip(p['ex'], a['ex_ko'])]
    ex += [{'zh': e['zh'], 'py': py(e['zh']), 'ko': e['ko']} for e in a.get('extra', [])]
    rx = a.get('regex'); n = 0
    if rx:
        try:
            # JS 정규식 → 파이썬 검사 (백레퍼런스 \1 은 양쪽 모두 같음)
            cre = re.compile(rx)
            n = sum(1 for s in sents.values() if cre.search(s['zh']))
        except re.error: badre += 1; rx = None
    if rx and n == 0: nomatch += 1
    out.append({'id': p['code'], 'lv': p['lv'], 'sec': p['section'], 'title': p['title'], 'title_ko': a['title_ko'], 'pattern': a['pattern'],
                'desc': a['desc'], 'sub': p['sub'], 'phrases': p['phrases'], 'ex': ex, 'rx': rx, 'n': n})
json.dump({'version': 1, 'source': 'HSK 3.0 语法等级大纲 (2021) via krmanik/HSK-3.0', 'points': out}, open('grammar.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
from collections import Counter
print('문법 항목', len(out), Counter(o['lv'] for o in out), '/ 정규식 없음', sum(1 for o in out if not o['rx']), '/ 매칭 0', nomatch, '/ 정규식 오류', badre)
