# -*- coding: utf-8 -*-
"""exam_out/e*.json → exam.json  (모의고사 문항 은행: 듣기 판단 tf / 대화 dlg / 문장 순서 order, 급수별)"""
import json, glob, os, re
from pypinyin import pinyin, Style
PUNCT = set('。，！？、；：""''（）!?,.…—')
def norm(s): return ''.join(t for t in re.split(r'\s+', s.strip()) if t)
def py(s): return ' '.join(''.join(p[0] for p in pinyin(t, style=Style.TONE)) if not all(c in PUNCT for c in t) else t for t in re.split(r'\s+', s.strip()) if t)
bank = {}
bad = 0
for f in sorted(glob.glob('exam_out/e*.json')):
    lv = int(os.path.basename(f)[1])
    try: d = json.load(open(f, encoding='utf-8'))
    except Exception as e: print('JSON 오류', f, e); continue
    b = bank.setdefault(str(lv), {'tf': [], 'dlg': [], 'order': []})
    for it in d.get('tf', []):
        try: b['tf'].append({'audio': norm(it['audio']), 'shown': norm(it['shown']), 'py': py(it['shown']), 'ans': bool(it['ans']), 'ko': it.get('ko','')})
        except Exception: bad += 1
    for it in d.get('dlg', []):
        try:
            assert len(it['opts']) == 3 and 0 <= int(it['ans']) < 3
            b['dlg'].append({'a': norm(it['a']), 'b': norm(it['b']), 'q': norm(it['q']), 'qpy': py(it['q']), 'opts': [norm(o) for o in it['opts']], 'ans': int(it['ans']), 'ko': it.get('ko','')})
        except Exception: bad += 1
    for it in d.get('order', []):
        try:
            assert len(it['sents']) == 3
            b['order'].append({'sents': [norm(s) for s in it['sents']], 'py': [py(s) for s in it['sents']], 'ko': it.get('ko','')})
        except Exception: bad += 1
json.dump({'version': 1, 'bank': bank}, open('exam.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for lv, b in bank.items(): print(lv, {k: len(v) for k, v in b.items()})
print('오류', bad)
