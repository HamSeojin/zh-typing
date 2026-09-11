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
SEC_KO = {"名词": "명사", "代词": "대명사", "动词": "동사", "形容词": "형용사", "数词": "수사(숫자)", "量词": "양사(세는 말)", "副词": "부사", "连词": "접속사", "助词": "조사", "叹词": "감탄사", "拟声词": "의성어", "前缀": "접두사", "后缀": "접미사", "类前缀": "접두사처럼 쓰이는 말", "类后缀": "접미사처럼 쓰이는 말", "语气副词": "어기부사(말투·태도)", "程度副词": "정도부사(얼마나)", "时间副词": "시간부사", "范围、协同副词": "범위·함께 부사(都·也·一起)", "频率、重复副词": "빈도·반복 부사", "否定副词": "부정부사(不·没)", "方式副词": "방식부사", "关联副词": "연결부사(就·才·还)", "情态副词": "정태부사(태도)", "语气助词": "어기조사(문장 끝 吗·呢·吧)", "结构助词": "구조조사(的·地·得)", "主语": "주어", "谓语": "술어", "宾语": "목적어", "定语": "관형어(명사 꾸밈)", "状语": "부사어(동사 꾸밈)", "补语": "보어(동작의 결과·정도·방향)", "动作的态": "동작의 상(진행·완료·경험)", "数的表示法": "수 표현법", "时间表示法": "시간 표현법", "单句": "단문", "复句": "복문(절이 둘 이상)", "句类": "문장의 종류(평서·의문·명령·감탄)", "句型": "문형", "特殊句型": "특수 문형(把·被·是…的 등)", "特殊句式": "특수 문형", "结构类型": "구조 유형", "功能类型": "기능 유형", "按形式分类": "형식에 따른 분류", "按意义分类": "의미에 따른 분류", "并列复句": "병렬 복문(그리고)", "递进复句": "점층 복문(게다가)", "选择复句": "선택 복문(아니면)", "转折复句": "전환 복문(그러나)", "假设复句": "가정 복문(만약)", "条件复句": "조건 복문(~하기만 하면)", "因果复句": "인과 복문(때문에)", "目的复句": "목적 복문(~하기 위해)", "承接复句": "연속 복문(그러고 나서)", "让步复句": "양보 복문(비록 ~일지라도)", "紧缩复句": "긴축 복문(짧게 붙인 복문)", "解说复句": "해설 복문", "多重复句": "다중 복문", "句群": "문장군(문장 여러 개의 연결)", "提问的方法": "질문하는 법", "强调的方法": "강조하는 법", "表示排除": "제외 표현(除了)", "特殊表达法": "특수 표현법", "引出对象": "대상을 이끄는 개사(对·给·跟)", "引出时间、处所": "시간·장소를 이끄는 개사(在·从)", "引出时间": "시간을 이끄는 개사", "引出方向、路径": "방향·경로를 이끄는 개사(往·向)", "引出凭借、依据": "수단·근거를 이끄는 개사(用·按照)", "引出目的、原因": "목적·원인을 이끄는 개사(为了·由于)", "引出施事、受事": "행위자·대상을 이끄는 개사(被·把)", "固定格式": "고정 격식(정해진 틀)", "口语格式": "구어 격식(말할 때 자주 쓰는 틀)", "四字格": "사자성어식 4글자 표현", "其他": "기타"}
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
    out.append({'id': p['code'], 'lv': p['lv'], 'sec': p['section'], 'sec_ko': SEC_KO.get(p['section'], p['section']), 'title': p['title'], 'title_ko': a['title_ko'], 'pattern': a['pattern'],
                'desc': a['desc'], 'sub': p['sub'], 'phrases': p['phrases'], 'ex': ex, 'rx': rx, 'n': n})
json.dump({'version': 1, 'source': 'HSK 3.0 语法等级大纲 (2021) via krmanik/HSK-3.0', 'points': out}, open('grammar.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
from collections import Counter
print('문법 항목', len(out), Counter(o['lv'] for o in out), '/ 정규식 없음', sum(1 for o in out if not o['rx']), '/ 매칭 0', nomatch, '/ 정규식 오류', badre)
