# -*- coding: utf-8 -*-
"""
build_words.py — 단어 데이터 준비 스크립트

무엇을 하는가?
  1. complete-hsk-vocabulary 저장소의 complete.json (HSK 2.0/3.0 전체 단어 + CC-CEDICT 뜻/병음)을 읽고
  2. HSK 3.0 급수가 붙은 단어만 골라서
  3. 우리 앱이 쓰기 좋은 납작한(flat) 구조로 바꾼 뒤
  4. words.json 으로 저장한다.

실행 방법:
  git clone https://github.com/drkameleon/complete-hsk-vocabulary.git data/complete-hsk-vocabulary
  python build_words.py

용어:
  JSON  - 사람이 읽을 수 있는 텍스트 형식의 데이터 파일. { "키": 값 } 형태.
  flat  - 중첩(안에 또 안에)이 없이 한 단어 = 한 줄로 평평하게 만든 구조.
"""
import json
import os
import re

SRC = os.path.join("data", "complete-hsk-vocabulary", "complete.json")
OUT = "words.json"

# 기존 words.json 이 있으면 거기 적어둔 한국어 뜻(ko)은 보존한다.
# (스크립트를 다시 돌려도 손으로 채운 뜻이 날아가지 않게)
old_ko = {}
if os.path.exists(OUT):
    with open(OUT, encoding="utf-8") as f:
        for w in json.load(f)["words"]:
            if w.get("ko"):
                old_ko[w["s"]] = w["ko"]

with open(SRC, encoding="utf-8") as f:
    raw = json.load(f)

# ── 다음자(多音字, 읽기가 여러 개인 한자) 처리 ──
# CC-CEDICT 는 说 을 shuì(설득하다)/shuō(말하다) 두 항목으로 갖고 있고, 원본 데이터는 이걸 병음 알파벳순으로
# 늘어놓아 shuì 가 먼저 온다. 그대로 첫 항목을 쓰면 엉뚱한 읽기가 대표가 되므로,
# krmanik/HSK-3.0 저장소의 "correct pinyin" 목록(HSK 단어별 대표 읽기)을 우선 참고한다.
OFFICIAL_DIR = os.path.join("data", "HSK-3.0", "Scripts and data", "correct pinyin")
official = {}   # 간체 → 숫자 병음 (공백 제거, 소문자)
for name in ["HSK1", "HSK2", "HSK3", "HSK4", "HSK5", "HSK6", "HSK7-9"]:
    p = os.path.join(OFFICIAL_DIR, name + ".txt")
    if not os.path.exists(p):
        continue
    for line in open(p, encoding="utf-8-sig"):
        cols = line.rstrip("\n").split("\t")
        if len(cols) >= 3 and cols[0] not in official:
            official[cols[0]] = cols[2].replace(" ", "").lower()

def norm_num(pyn):
    """'shui4 fu2' → 'shui4fu2', ü 표기 통일. 읽기 비교용."""
    return pyn.replace(" ", "").lower().replace("u:", "v").replace("ü", "v")

def is_proper(form):
    """'surname Wang', 'Anhui province' 처럼 고유명사 항목인지 (병음이 대문자로 시작)"""
    py = form["transcriptions"].get("pinyin", "")
    return py[:1].isupper()

def is_variant_only(form):
    ms = form.get("meanings", [])
    return bool(ms) and all(m.startswith(("variant of", "old variant", "erhua variant")) for m in ms)

def choose_form(entry):
    """대표 읽기(form) 하나를 고른다: 1) 공식 목록과 병음이 같은 것 2) 고유명사·이체자 항목 제외 후 뜻이 가장 많은 것"""
    forms = entry["forms"]
    off = official.get(entry["simplified"])
    if off:
        hits = [fm for fm in forms if norm_num(fm["transcriptions"].get("numeric", "")) == norm_num(off)]
        if hits:
            # 같은 읽기 중에서도 '성씨 X' 같은 고유명사 항목보다 일반 뜻 항목을 우선
            plain = [fm for fm in hits if not is_proper(fm) and not is_variant_only(fm)]
            return max(plain or hits, key=lambda fm: len(fm.get("meanings", [])))
    cands = [fm for fm in forms if not is_proper(fm) and not is_variant_only(fm)] or forms
    return max(cands, key=lambda fm: len(fm.get("meanings", [])))

words = []
for entry in raw:
    levels = entry.get("level", [])

    # "new-3" 처럼 HSK 3.0(2021) 급수만 추출. 7~9급은 "new-7" 하나로 묶여 있음.
    new_lv = [int(l.split("-")[1]) for l in levels if l.startswith("new-")]
    newest_lv = [int(l.split("-")[1]) for l in levels if l.startswith("newest-")]
    old_lv = [int(l.split("-")[1]) for l in levels if l.startswith("old-")]
    if not new_lv and not newest_lv:
        continue  # HSK 2.0 에만 있는 단어는 제외

    # forms: 같은 간체가 여러 읽기/번체/뜻을 가질 수 있어 배열. 대표 읽기를 고른다.
    form = choose_form(entry)
    tr = form["transcriptions"]

    # 뜻: 대표 읽기의 뜻을 먼저, 다른 읽기의 뜻은 뒤에 " ; " 로 이어 붙임. "variant of X" 류는 맨 뒤
    meanings = []
    for fm in [form] + [x for x in entry["forms"] if x is not form]:
        for m in fm.get("meanings", []):
            if m not in meanings:
                meanings.append(m)
    meanings.sort(key=lambda m: m.startswith("variant of") or m.startswith("old variant"))

    # 다른 읽기 목록 (고유명사·이체자 항목 제외). 앱에서 "다른 읽기" 로 보여주고, 병음 입력 채점 때 정답으로 인정
    alts = []
    seen = {norm_num(tr.get("numeric", ""))}
    for fm in entry["forms"]:
        n = norm_num(fm["transcriptions"].get("numeric", ""))
        if n in seen or is_proper(fm) or is_variant_only(fm):
            continue
        seen.add(n)
        alts.append({"py": fm["transcriptions"].get("pinyin", ""), "pyn": fm["transcriptions"].get("numeric", ""),
                     "en": "; ".join(fm.get("meanings", [])[:2])})

    words.append({
        "s":   entry["simplified"],          # 간체
        "t":   form.get("traditional", ""),   # 번체
        "py":  tr.get("pinyin", ""),          # 병음 (성조 부호: nǐ hǎo)
        "pyn": tr.get("numeric", ""),         # 병음 (숫자 성조: ni3 hao3) — 채점용
        "en":  " ; ".join(meanings),          # 영어 뜻
        "ko":  old_ko.get(entry["simplified"], ""),  # 한국어 뜻 (앱에서 채움)
        "lv":  min(new_lv) if new_lv else min(newest_lv),   # HSK 3.0 급수 (1~7, 7=7~9급)
        "lv26": min(newest_lv) if newest_lv else None,      # 2026 개정판 급수 (있으면)
        "old": min(old_lv) if old_lv else None,             # HSK 2.0 급수 (있으면)
        "freq": entry.get("frequency"),        # 빈도 순위 (작을수록 흔한 단어)
        "pos": entry.get("pos", []),           # 품사 (n=명사, v=동사 ...)
        "alt": alts,                           # 다른 읽기 [{py, pyn, en}] (없으면 빈 배열)
    })

# 급수 → 빈도 순으로 정렬해서 id 부여 (id 는 학습 기록과 연결하는 열쇠)
words.sort(key=lambda w: (w["lv"], w["freq"] if w["freq"] is not None else 10**9))
for i, w in enumerate(words, start=1):
    w["id"] = i

# 7~9급은 원본에 "new-7" 하나로 묶여 있음(5,907개). 공식 분할이 없으므로 빈도(freq) 순으로 셋으로 나눠 7·8·9급으로 표시한다.
# (id 는 급수→빈도 순으로 이미 매겨져 있어, 이렇게 나눠도 id 와 학습 기록은 그대로 유지됨)
l7 = [w for w in words if w["lv"] == 7]
third = -(-len(l7) // 3)   # 올림 나눗셈
for i, w in enumerate(l7):
    w["lv"] = 7 + i // third

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"version": 1, "source": "drkameleon/complete-hsk-vocabulary (MIT) + CC-CEDICT (CC BY-SA 4.0)",
               "words": words}, f, ensure_ascii=False, indent=0)

from collections import Counter
print(f"총 {len(words)} 단어 저장 → {OUT}")
print("급수별:", sorted(Counter(w["lv"] for w in words).items()))
print("한국어 뜻 채워진 단어:", sum(1 for w in words if w["ko"]))
