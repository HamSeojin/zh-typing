# -*- coding: utf-8 -*-
"""
build_pinyin.py — 발음 기초 데이터(pinyin.json) 만들기
  · 성모 21개·운모 35개: 한국어 설명(입 모양·혀 위치·한국어와의 차이) + 예시 음절
  · 유효 음절(성조 포함) → 대표 한자: words.json 에서 자동 추출 (TTS 로 음절을 들려줄 때 그 한자를 읽힘)
  · 한국인이 헷갈리는 짝 목록 (최소대립쌍 듣기용)
실행: python build_pinyin.py  → pinyin.json
"""
import json, re, collections

words = json.load(open("words.json", encoding="utf-8"))["words"]

INITIALS = [
 ("b","ㅃ/ㅂ 사이. 입술을 붙였다 떼며 숨을 내지 않음(무기음). 한국어 '빠'에 가깝고 '파'가 아님", ["ba1","bo1","bu4"]),
 ("p","입술을 붙였다 떼며 숨을 강하게 내뿜음(유기음). 손바닥을 입 앞에 대면 바람이 느껴져야 함. 한국어 '파'", ["pa4","po4","pu3"]),
 ("m","한국어 'ㅁ'과 같음", ["ma1","mo2","mu4"]),
 ("f","윗니를 아랫입술에 대고 내는 소리. 한국어에 없음 — 영어 f. 'ㅍ'으로 대신하면 안 됨", ["fa1","fo2","fu4"]),
 ("d","혀끝을 윗니 뒤에 대고 숨 없이. 한국어 '따'에 가까움", ["da4","de5","du4"]),
 ("t","d 와 같은 위치에서 숨을 강하게. 한국어 '타'", ["ta1","te4","tu3"]),
 ("n","한국어 'ㄴ'", ["na4","ne5","nu3"]),
 ("l","혀끝을 윗니 뒤 잇몸에 대고 옆으로 공기를 흘림. 한국어 초성 'ㄹ'(라)과 비슷. n 과 구별 주의", ["la1","le4","lu4"]),
 ("g","혀 뒤를 입천장 뒤에 대고 숨 없이. 한국어 '까'에 가까움", ["ge1","gu3","gao1"]),
 ("k","g 와 같은 위치에서 숨을 강하게. 한국어 '카'", ["ke4","ku1","kai1"]),
 ("h","목 안쪽을 좁혀 거칠게 내는 'ㅎ'. 한국어 'ㅎ'보다 마찰이 세고, 가래 끓듯 목에서 남", ["he2","hu1","hao3"]),
 ("j","혀 앞면을 입천장 앞쪽에 넓게 붙이고 내는 'ㅈ'. 입술을 옆으로 당김(웃는 입). 뒤에는 i·ü 계열 운모만 옴", ["ji1","jia1","ju4"]),
 ("q","j 와 같은 위치에서 숨을 세게 — 한국어 '치'. 뒤에는 i·ü 계열만 옴", ["qi1","qia4","qu4"]),
 ("x","j 위치에서 마찰만 — 한국어 '시'와 비슷하지만 혀 앞면이 더 넓게 닿음. 뒤에는 i·ü 계열만 옴", ["xi1","xia4","xu1"]),
 ("zh","혀끝을 위로 말아 입천장 가운데에 대고 내는 'ㅈ'(권설음). 입술은 둥글게 앞으로. j 와 달리 뒤에 a·e·u 등 다양한 운모가 옴", ["zha1","zhe4","zhu4"]),
 ("ch","zh 위치에서 숨을 세게 — 말아 올린 '츠'", ["cha2","che1","chu1"]),
 ("sh","zh 위치에서 마찰만 — 말아 올린 '스'. 영어 sh 보다 혀가 더 뒤로 말림", ["sha1","she2","shu1"]),
 ("r","sh 와 같은 위치에서 성대를 울림. 한국어 'ㄹ'이 아니라 영어 r 에 가깝되 혀를 말고 입술은 안 내밈", ["re4","ri4","rou4"]),
 ("z","혀끝을 윗니 뒤에 대고 내는 'ㅉ'. 입술을 옆으로 — zh 와 달리 혀를 말지 않음", ["za2","ze2","zu2"]),
 ("c","z 위치에서 숨을 세게 — '츠'(혀 안 말음). ch 와 구별", ["ca1","ce4","cu1"]),
 ("s","z 위치에서 마찰만 — 한국어 'ㅅ'(스). sh 와 구별", ["sa3","se4","su4"]),
]
FINALS = [
 ("a","입을 크게 벌린 '아'", ["ba1","ma1","ta1"]),
 ("o","입술을 둥글게 '오'. b·p·m·f 뒤에서는 '우어'처럼 들림(bo ≈ 뿌어)", ["bo1","po1","mo2"]),
 ("e","'어'와 '으' 사이. 입은 '어' 모양인데 입술을 옆으로 펴서 냄. 한국어 '에'가 아님", ["ge1","he2","le4"]),
 ("i","'이'. 단, z·c·s 뒤에서는 '으'(zi=쯔), zh·ch·sh·r 뒤에서는 혀를 만 '으'(zhi=즈)", ["bi3","zi4","zhi1"]),
 ("u","입술을 앞으로 내민 '우'. j·q·x·y 뒤의 u 는 사실 ü", ["bu4","du4","lu4"]),
 ("ü","'이' 입모양(혀 위치)에서 입술만 '우'로 둥글게. 한국어 '위'를 한 소리로 낸 느낌. j·q·x·y 뒤에서는 점 없이 u 로 씀", ["nü3","lü4","ju4"]),
 ("ai","'아이'를 한 음절로", ["ai4","bai2","kai1"]),
 ("ei","'에이'를 한 음절로", ["bei3","fei1","mei3"]),
 ("ao","'아오'를 한 음절로. '아우'가 아님", ["ao4","bao1","hao3"]),
 ("ou","'어우'에 가까움 — '오우'보다 첫소리가 어둡게", ["ou1","dou1","hou4"]),
 ("an","'안'. 입을 크게 벌린 '아'로 시작", ["an1","ban1","han4"]),
 ("en","'언'. e 가 '으/어'라서 '엔'이 아님", ["en1","ben3","men2"]),
 ("ang","'앙'. 혀 뒤로 코울림 — an 과 구별", ["ang2","bang1","kang4"]),
 ("eng","'엉'. en 과 구별", ["deng3","feng1","leng3"]),
 ("ong","'옹'(입술 둥글게)", ["dong1","hong2","gong1"]),
 ("er","'얼'. 혀끝을 말아 올림", ["er4","er2","er3"]),
 ("ia","'이아' → '야'", ["jia1","xia4","qia4"]),
 ("ie","'이에' → '예'. 여기서 e 는 '에'", ["bie2","jie3","xie4"]),
 ("iao","'이아오' → '야오'", ["jiao4","xiao3","tiao4"]),
 ("iu","'이오우' → '요우'. 가운데 o 가 생략된 철자 (liu=리오우)", ["liu4","jiu3","xiu1"]),
 ("ian","'이엔' → '옌'. '얀'이 아님", ["bian1","tian1","jian4"]),
 ("in","'인'", ["jin1","xin1","lin2"]),
 ("iang","'이앙' → '양'", ["liang3","jiang1","xiang3"]),
 ("ing","'잉'. in 과 구별", ["jing1","xing2","ting1"]),
 ("iong","'이옹' → '용'", ["xiong2","jiong3","qiong2"]),
 ("ua","'우아' → '와'", ["gua1","hua1","kua4"]),
 ("uo","'우어' → '워'", ["duo1","guo2","zuo4"]),
 ("uai","'우아이' → '와이'", ["kuai4","huai4","shuai4"]),
 ("ui","'우에이' → '웨이'. 가운데 e 가 생략된 철자 (dui=뚜에이)", ["dui4","hui4","shui3"]),
 ("uan","'우안' → '완'", ["guan1","huan4","duan3"]),
 ("un","'우언' → '원'(uen 의 줄임)", ["dun4","hun1","lun4"]),
 ("uang","'우앙' → '왕'", ["huang2","guang1","zhuang1"]),
 ("ueng","'우엉' → '웡'. 단독(weng)으로만 씀", ["weng1"]),
 ("üe","'위에' → 'ㅟ에'. j·q·x·y 뒤에서는 ue 로 씀", ["yue4","xue2","jue2"]),
 ("üan","'위안' → 'ㅟ엔'에 가까움(quan=취엔)", ["yuan2","quan2","xuan3"]),
 ("ün","'윈'", ["yun2","jun1","xun2"]),
]
# 한국인이 헷갈리는 짝 (최소대립쌍 듣기). kind: ini=성모, fin=운모
PAIRS = [
 ("b/p","ini","b","p","숨의 유무: b 는 숨 없이(빠), p 는 숨 세게(파)"),
 ("d/t","ini","d","t","숨의 유무: d(따) / t(타)"),
 ("g/k","ini","g","k","숨의 유무: g(까) / k(카)"),
 ("zh/j","ini","zh","j","zh 는 혀를 말고 입술 둥글게, j 는 혀 앞면을 펴고 입술 옆으로"),
 ("ch/q","ini","ch","q","ch 는 혀를 말고, q 는 혀 앞면"),
 ("sh/x","ini","sh","x","sh 는 혀를 말고, x 는 혀 앞면"),
 ("z/zh","ini","z","zh","z 는 혀끝 윗니 뒤(쯔), zh 는 혀 말아 올림(즈)"),
 ("c/ch","ini","c","ch","c 는 혀끝 윗니 뒤, ch 는 혀 말아 올림"),
 ("s/sh","ini","s","sh","s 는 혀끝 윗니 뒤, sh 는 혀 말아 올림"),
 ("n/l","ini","n","l","n 은 코로, l 은 혀 옆으로 공기"),
 ("l/r","ini","l","r","l 은 혀끝 잇몸, r 은 혀 말아 올린 채 성대 울림"),
 ("f/h","ini","f","h","f 는 윗니-아랫입술, h 는 목 안쪽"),
 ("u/ü","fin","u","ü","u 는 입술만 둥글게, ü 는 '이' 혀 위치에 입술 둥글게"),
 ("an/ang","fin","an","ang","an 은 혀끝이 잇몸에(안), ang 은 혀 뒤로 코울림(앙)"),
 ("en/eng","fin","en","eng","en(언) / eng(엉)"),
 ("in/ing","fin","in","ing","in(인) / ing(잉)"),
 ("ian/iang","fin","ian","iang","ian(옌) / iang(양)"),
 ("uan/uang","fin","uan","uang","uan(완) / uang(왕)"),
 ("ie/üe","fin","ie","üe","ie(예) / üe(ㅟ에)"),
 ("ao/ou","fin","ao","ou","ao(아오) / ou(어우)"),
 ("e/o","fin","e","o","e(어/으) / o(오)"),
]

INI_LIST = sorted([i[0] for i in INITIALS], key=len, reverse=True)
def split_syl(s):
    s = s.lower()
    m = re.match(r"^([a-z:ü]+?)([1-5])$", s)
    if not m: return None
    body, tone = m.group(1).replace("u:", "ü").replace("v", "ü"), int(m.group(2))
    ini = next((i for i in INI_LIST if body.startswith(i)), "")
    fin = body[len(ini):]
    # y/w 로 시작하는 철자를 운모로 환원 (yi→i, ya→ia, wu→u, wa→ua, yu→ü, yue→üe …)
    if not ini:
        if fin.startswith("yu"): fin = "ü" + fin[2:]
        elif fin == "yi": fin = "i"
        elif fin.startswith("y"): fin = "i" + fin[1:] if fin[1:] not in ("in", "ing") else fin[1:]
        elif fin == "wu": fin = "u"
        elif fin.startswith("w"): fin = "u" + fin[1:]
    # j q x y 뒤의 u 는 ü
    if ini in ("j","q","x") and fin.startswith("u"): fin = "ü" + fin[1:]
    fin = {'iou':'iu','uei':'ui','uen':'un'}.get(fin, fin)   # you/wei/wen 을 축약 철자와 같은 항목으로
    return ini, fin, tone, body

# 음절(성조 포함) → 대표 한자. 단어 글자 수 = 음절 수 인 단어에서 글자-음절 짝. 한 글자 단어·낮은 급수·읽기가 하나뿐인 글자 우선
cand = collections.defaultdict(list)
char_readings = collections.defaultdict(set)
for w in words:
    cs, ps = list(w["s"]), w["pyn"].lower().split()
    if len(cs) != len(ps): continue
    for c, p in zip(cs, ps):
        p = p.replace("u:", "ü").replace("v", "ü")
        char_readings[c].add(p)
        cand[p].append((len(cs) != 1, w["lv"], c))
syl = {}; common = []
for p, lst in cand.items():
    lst = sorted(lst, key=lambda x: (len(char_readings[x[2]]) > 1, x[0], x[1]))
    syl[p] = lst[0][2]
    if lst[0][1] <= 3: common.append(p)   # 1~3급 단어에서 나온 음절 → 퀴즈는 이 범위에서 냄
# 음절 → 분해 정보 (성모·운모) — 표에서 필터링용
table = {}
for p in syl:
    sp = split_syl(p)
    if sp and sp[1]: table[p] = [sp[0], sp[1]]
for p in [k for k in syl if k not in table]: del syl[p]   # 儿化 r 처럼 분해 안 되는 것 제외

out = {
 "initials": [{"k": k, "ko": ko, "ex": ex} for k, ko, ex in INITIALS],
 "finals": [{"k": k, "ko": ko, "ex": ex} for k, ko, ex in FINALS],
 "pairs": [{"k": k, "kind": kind, "a": a, "b": b, "ko": ko} for k, kind, a, b, ko in PAIRS],
 "syl": syl, "table": table, "common": [c for c in common if c in table],
}
json.dump(out, open("pinyin.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
missing = [e for grp in (INITIALS, FINALS) for _, _, exs in grp for e in exs if e not in syl]
print("음절", len(syl), "개 / 예시 중 대표 한자 없는 것:", missing)
