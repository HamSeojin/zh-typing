# -*- coding: utf-8 -*-
"""read_out/*.json (LLM 이 만든 읽기 글) → passages.json. 병음은 pypinyin 으로 붙이고 형식을 검증."""
import json, glob, os, re
from pypinyin import pinyin, Style
PUNCT = set('。，！？、；：""''（）!?,.…—')
def py_of(seg): return ' '.join(t if all(c in PUNCT for c in t) else ''.join(p[0] for p in pinyin(t, style=Style.TONE)) for t in seg)
out, bad = [], 0
for f in sorted(glob.glob('read_out/r*.json')):
    lv = int(os.path.basename(f)[1])
    try: arr = json.load(open(f, encoding='utf-8'))
    except Exception as e: print('JSON 오류', f, e); continue
    for p in arr:
        try:
            sents = []
            for s in p['sents']:
                seg = [t for t in re.split(r'\s+', s['zh'].strip()) if t]
                sents.append({'zh': ''.join(seg), 'seg': seg, 'py': py_of(seg), 'ko': s['ko'].strip()})
            qs = []
            for q in p['qs']:
                qseg = [t for t in re.split(r'\s+', q['q'].strip()) if t]
                opts = [''.join(re.split(r'\s+', o.strip())) for o in q['opts']]
                assert len(opts) == 3 and 0 <= int(q['ans']) < 3
                qs.append({'q': ''.join(qseg), 'qpy': py_of(qseg), 'qko': q.get('qko',''), 'opts': opts, 'optsko': q.get('optsko', ['','','']), 'ans': int(q['ans'])})
            out.append({'id': len(out)+1, 'lv': lv, 'title': ''.join(p['title'].split()), 'sents': sents, 'qs': qs})
        except Exception as e: bad += 1; print('항목 오류', f, e)
json.dump({'version': 1, 'passages': out}, open('passages.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
from collections import Counter
print('글', len(out), '편 저장 / 오류', bad, '/ 급수별', sorted(Counter(p['lv'] for p in out).items()))
