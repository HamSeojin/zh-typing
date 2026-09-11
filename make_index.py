# -*- coding: utf-8 -*-
"""app_template.html 의 __WORDS_JSON__ 자리에 words.json 내용을 끼워 넣어 index.html 을 만든다."""
import json, os

with open("words.json", encoding="utf-8") as f:
    data = json.load(f)
# separators: 공백 없이 압축. '<' 는 <script> 태그가 중간에 끊기는 사고를 막기 위해 < 로 바꿈
blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
sents = json.load(open("sentences.json", encoding="utf-8")) if os.path.exists("sentences.json") else {"sentences": {}}
sblob = json.dumps(sents, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
with open("app_template.html", encoding="utf-8") as f:
    tpl = f.read()
# 획순 데이터: HSK 1~3급 단어에 나오는 한자만 내장 (vendor/node_modules/hanzi-writer-data)
SD = os.path.join("vendor", "node_modules", "hanzi-writer-data")
chars = sorted({ch for w in data["words"] if w["lv"] <= 3 for ch in w["s"] if "\u4e00" <= ch <= "\u9fff"})
strokes = {}
for ch in chars:
    fp = os.path.join(SD, ch + ".json")
    if os.path.exists(fp):
        with open(fp, encoding="utf-8") as f: strokes[ch] = json.load(f)
kblob = json.dumps(strokes, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
HW = os.path.join("vendor", "node_modules", "hanzi-writer", "dist", "hanzi-writer.min.js")
hw = open(HW, encoding="utf-8").read() if os.path.exists(HW) else ""
html = tpl.replace("__WORDS_JSON__", blob).replace("__SENTS_JSON__", sblob).replace("__STROKES_JSON__", kblob)
import datetime
html = html.replace("__APP_VERSION__", "v" + datetime.datetime.now().strftime("%m%d.%H%M"))
html = html.replace("__HANZI_WRITER_JS__", hw.replace("</script>", "<\\/script>"))   # 라이브러리 안의 </script> 문자열이 태그를 닫지 않게
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("획순 데이터", len(strokes), "자 내장 / hanzi-writer", "포함" if hw else "없음")
print("예문", len(sents["sentences"]), "개 포함")
print("index.html 생성 완료 —", len(data["words"]), "단어")
