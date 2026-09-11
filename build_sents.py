# -*- coding: utf-8 -*-
"""sent_out/*.json (예문 생성 결과) → sentences.json
   각 예문에 pypinyin 으로 병음을 붙이고, 대상 단어가 실제로 들어 있는지 검사한다."""
import json, glob, os, re
from pypinyin import pinyin, Style

words = {w['id']: w for w in json.load(open('words.json', encoding='utf-8'))['words']}
out, bad = {}, []
PUNCT = set('。，！？、；：""''（）!?,.')
for f in sorted(glob.glob('sent_out/*.json')):
    m = json.load(open(f, encoding='utf-8'))
    b = os.path.basename(f)[:-5]
    ids = [int(l.split('\t')[0]) for l in open(f'sent_batches/{b}.tsv', encoding='utf-8') if l.strip()]
    keys = [int(k) for k in m]
    # 생성 결과의 키가 실제 id 가 아니라 1..N 줄 번호로 적힌 경우 → 순서대로 대응
    pairs = list(zip(ids, m.values())) if keys == list(range(1, len(m)+1)) and ids[0] != 1 else [(int(k), v) for k, v in m.items()]
    for wid, v in pairs:
        w = words.get(wid)
        if not w or not isinstance(v, dict) or not v.get('zh'): bad.append((wid, 'format')); continue
        seg = [t for t in re.split(r'\s+', v['zh'].strip()) if t]
        zh = ''.join(seg)
        if w['s'] not in zh: bad.append((wid, f"{w['s']} 없음: {zh}")); continue
        # 병음: 글자 단위로 붙이되 어절 단위로 묶음. 구두점은 병음 없음
        py_seg = []
        for t in seg:
            if all(c in PUNCT for c in t): py_seg.append(t); continue
            py_seg.append(''.join(p[0] for p in pinyin(t, style=Style.TONE)))
        out[str(wid)] = {'zh': zh, 'seg': seg, 'py': ' '.join(py_seg), 'ko': v.get('ko', '').strip()}
json.dump({'version': 1, 'sentences': out}, open('sentences.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('예문', len(out), '개 저장 / 문제 있는 항목', len(bad))
for b in bad[:20]: print('  ', b)
