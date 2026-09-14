# -*- coding: utf-8 -*-
"""
build_ext.py — HSK 밖 공개 데이터 → 앱용 파일
  ext/cedict.txt (CC-CEDICT, CC BY-SA 4.0)   → dict.json   : HSK 단어장에 없는 단어의 병음·영어 뜻 (탭 사전 보조)
  ext/idiom.json (chinese-xinhua, MIT) + LLM  → idioms.json : 자주 쓰는 성어 600 (한국어 뜻·설명·예문)
  ext/mmah_dictionary.txt (Make Me a Hanzi)   → hanzi.json  : HSK 한자 3,020자 분해·부수·어원 힌트 (1~3급은 한국어)
  ext/opus (OpenSubtitles zh-ko) + LLM 선별   → phrases.json: 실전 회화 표현 ~1,200 (한국어·용법·분류)
  ext/tatoeba*, olp_vocab.csv (CC BY / CC0)   → sents2.json : 단어별 추가 예문 (Tatoeba zh-ko, Zero to Hero 예문 zh-en)
  ext/zh_freq.json (wordfreq, 자막·위키 등 합산 빈도; SUBTLEX-CH 대체) → 각 파일의 빈도 순 정렬에 사용
실행: python build_ext.py  (ext/ 원본과 ext/*_out/ LLM 결과가 있어야 함)
"""
import json, glob, os, re, collections, csv
from pypinyin import pinyin, Style
PUNCT = set('。，！？、；：""''（）!?,.…—')
def py(s): return ' '.join(''.join(p[0] for p in pinyin(t, style=Style.TONE)) if not all(c in PUNCT for c in t) else t for t in re.split(r'\s+', s.strip()) if t)
def norm(s): return ''.join(t for t in re.split(r'\s+', s.strip()) if t)
words = json.load(open('words.json', encoding='utf-8'))['words']
BY_S = {w['s']: w for w in words}
freq = json.load(open('ext/zh_freq.json', encoding='utf-8'))

# ── 성어 ──
sel = {x['w']: x for x in json.load(open('ext/idiom_sel.json', encoding='utf-8'))}
idioms = []
for f in sorted(glob.glob('ext/idiom_out/i*.json')):
    for it in json.load(open(f, encoding='utf-8')):
        w = it['w']
        if w not in sel: continue
        idioms.append({'w': w, 'py': sel[w]['py'], 'ko': it['ko'], 'desc': it['desc'], 'ex': norm(it['ex']), 'expy': py(' '.join(norm(it['ex']))), 'ex_ko': it['ex_ko'], 'f': sel[w]['f']})
idioms.sort(key=lambda x: x['f'])
json.dump({'idioms': idioms}, open('idioms.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('성어', len(idioms))

# ── 한자 분해 ──
mm = json.load(open('ext/hanzi_raw.json', encoding='utf-8'))
ko_hint = {}
for f in sorted(glob.glob('ext/hz_out/h*.json')): ko_hint.update(json.load(open(f, encoding='utf-8')))
TYPE_KO = {'ideographic': '회의자', 'pictographic': '상형자', 'pictophonetic': '형성자'}
hanzi = {}
for c, d in mm.items():
    hanzi[c] = {'d': d['d'], 'r': d['r'], 't': TYPE_KO.get(d['et'], ''), 'h': ko_hint.get(c, ''), 'en': d['hint'], 'ph': d['ph'], 'sem': d['sem']}
# 부수 214 · 양사 목록 (LLM 작성, ext/misc_out) 도 같은 파일에
rad = json.load(open('ext/misc_out/radicals.json', encoding='utf-8')); mea = json.load(open('ext/misc_out/measure.json', encoding='utf-8'))
rad_index = collections.defaultdict(list)   # 부수 → 그 부수를 가진 HSK 한자 (급수 낮은 순 12개)
lvc = {}
for w in words:
    for c in w['s']: lvc[c] = min(lvc.get(c, 9), w['lv'])
for c, d in mm.items():
    if d['r']: rad_index[d['r']].append(c)
for r in rad_index: rad_index[r] = sorted(set(rad_index[r]), key=lambda c: lvc.get(c, 9))
for it in rad:   # 본 부수 + 변형(氵·亻…) 으로 잡힌 글자를 합쳐 급수 낮은 순 12자
    keys = [it['r']] + [v.strip()[:1] for v in re.split(r'[,\s、·]+', it.get('v', '')) if v.strip()]
    got = []
    for k in keys: got += rad_index.get(k, [])
    it['hsk'] = ''.join(sorted(set(got), key=lambda c: lvc.get(c, 9))[:12])
json.dump({'chars': hanzi, 'radicals': rad, 'measure': mea}, open('hanzi.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('한자', len(hanzi), '한국어 힌트', len(ko_hint), '부수', len(rad), '양사', len(mea))

# ── 회화 표현 ──
phr = {}
for f in sorted(glob.glob('ext/subs_out/s*.json')):
    for it in json.load(open(f, encoding='utf-8')):
        z = norm(it['zh']); core = re.sub(r'[，。！？…、：]', '', z)
        if core in phr or len(core) < 2 or (core in BY_S and len(core) <= 2): continue   # 단어장에 있는 낱말 하나짜리는 표현이 아니므로 제외
        phr[core] = {'zh': z, 'py': py(it['zh']), 'ko': it['ko'], 'note': it.get('note', ''), 'tag': it.get('tag', '기타'), 'f': freq.get(core, 999)}
phrases = sorted(phr.values(), key=lambda x: x['f'])
json.dump({'phrases': phrases}, open('phrases.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('회화 표현', len(phrases), collections.Counter(p['tag'] for p in phrases).most_common())

# ── 추가 예문: 단어 id → [{zh, py, ko|en, src}] ──
sents2 = collections.defaultdict(list)
def add(wid, zh, tr, src, lang):
    if len(sents2[wid]) >= 4: return
    if any(x['zh'] == zh for x in sents2[wid]): return
    sents2[wid].append({'zh': zh, 'py': py(' '.join(zh)), lang: tr, 'src': src})
# Zero to Hero 예문 (단어에 바로 연결됨, 영어 번역)
for s, ex, tr in json.load(open('ext/olp_ex.json', encoding='utf-8')):
    if s in BY_S and 4 <= len(ex) <= 40: add(BY_S[s]['id'], ex, tr, 'zth', 'en')
# Tatoeba 중-한: 문장 안에 들어 있는 HSK 단어(2글자 이상, 최대 3개)에 연결
multi = sorted([s for s in BY_S if len(s) >= 2], key=len, reverse=True)
for _, zh, ko in json.load(open('ext/tatoeba_ko.json', encoding='utf-8')):
    hit = [s for s in multi if s in zh][:3]
    for s in hit: add(BY_S[s]['id'], zh, ko, 'tatoeba', 'ko')
# pypinyin 은 글자별이라 띄어쓰기 없는 문장은 글자 단위 병음 → 표시용으로는 충분
for wid in sents2:
    for x in sents2[wid]: x['py'] = py(' '.join(x['zh'])).replace(' ', '') if False else x['py']
json.dump({'sents': sents2}, open('sents2.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('추가 예문 단어 수', len(sents2), '문장 수', sum(len(v) for v in sents2.values()))
