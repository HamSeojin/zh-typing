# -*- coding: utf-8 -*-
"""lis_out/l*.json → exam.json 에 합침 (듣기 대화 연습 확장: 짧은 대화 dlg 추가, 긴 대화 long, 독백 mono)
   build_exam.py 가 만든 exam.json 을 읽어 급수별 은행에 덧붙인다. 실행 순서: build_exam.py → build_lis.py"""
import json, glob, os, re
from pypinyin import pinyin, Style
PUNCT = set('。，！？、；：""''（）!?,.…—')
def norm(s): return ''.join(t for t in re.split(r'\s+', s.strip()) if t)
def py(s): return ' '.join(''.join(p[0] for p in pinyin(t, style=Style.TONE)) if not all(c in PUNCT for c in t) else t for t in re.split(r'\s+', s.strip()) if t)
def qs(lst):
    out = []
    for q in lst:
        assert len(q['opts']) == 3 and 0 <= int(q['ans']) < 3
        out.append({'q': norm(q['q']), 'qpy': py(q['q']), 'opts': [norm(o) for o in q['opts']], 'ans': int(q['ans'])})
    return out
ex = json.load(open('exam.json', encoding='utf-8')); bank = ex['bank']; bad = 0
for lv in bank: bank[lv]['long'] = []; bank[lv]['mono'] = []; bank[lv]['dlg'] = [d for d in bank[lv]['dlg'] if not d.get('src')]
for f in sorted(glob.glob('lis_out/l*.json')):
    lv = os.path.basename(f)[1]
    try: d = json.load(open(f, encoding='utf-8'))
    except Exception as e: print('JSON 오류', f, e); continue
    b = bank[lv]
    for it in d.get('dlg', []):
        try:
            assert len(it['opts']) == 3 and 0 <= int(it['ans']) < 3
            b['dlg'].append({'a': norm(it['a']), 'b': norm(it['b']), 'q': norm(it['q']), 'qpy': py(it['q']), 'opts': [norm(o) for o in it['opts']], 'ans': int(it['ans']), 'ko': it.get('ko',''), 'src': 'lis'})
        except Exception: bad += 1
    for it in d.get('long', []):
        try:
            turns = [{'s': t['s'].strip().upper()[:1], 't': norm(t['t'])} for t in it['turns']]; assert 3 <= len(turns) <= 8
            b['long'].append({'turns': turns, 'qs': qs(it['qs']), 'ko': it.get('ko','')})
        except Exception: bad += 1
    for it in d.get('mono', []):
        try: b['mono'].append({'text': norm(it['text']), 'py': py(it['text']), 'qs': qs(it['qs']), 'ko': it.get('ko','')})
        except Exception: bad += 1
json.dump(ex, open('exam.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
for lv, b in bank.items(): print(lv, {k: len(v) for k, v in b.items()})
print('오류', bad)
