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
passages = json.load(open("passages.json", encoding="utf-8")) if os.path.exists("passages.json") else {"passages": []}
pblob = json.dumps(passages, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
exam = json.load(open("exam.json", encoding="utf-8")) if os.path.exists("exam.json") else {"bank": {}}
eblob = json.dumps(exam, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
import datetime, hashlib, glob
gram = json.load(open("grammar.json", encoding="utf-8")) if os.path.exists("grammar.json") else {"points": []}
gblob = json.dumps(gram, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
pyblob = open("pinyin.json", encoding="utf-8").read().replace("<", "\\u003c")   # 발음 기초 (build_pinyin.py)
ext = {k: open(f"{k}.json", encoding="utf-8").read().replace("<", "\\u003c") for k in ("dict", "hanzi", "sents2", "phrases", "idioms", "opus")}   # HSK 밖 보조 데이터 (build_ext.py), 필요할 때 받음
blobs = {"words": blob, "sents": sblob, "strokes": kblob, "passages": pblob, "exam": eblob, "grammar": gblob, "pinyin": pyblob, **ext}
print("읽기 글", len(passages["passages"]), "편 포함")
version = "v" + datetime.datetime.now().strftime("%m%d.%H%M")
common = tpl.replace("__APP_VERSION__", version).replace("__HANZI_WRITER_JS__", hw.replace("</script>", "<\\/script>"))   # 라이브러리 안의 </script> 문자열이 태그를 닫지 않게
# ── artifact.html: claude.ai 게시용. 데이터를 페이지 안에 통째로 내장 (claude.ai 는 외부 파일 fetch 가 막혀 있어서) ──
ART_SKIP = {"opus"}   # claude.ai 아티팩트는 16MB 제한 → 자막 말뭉치(2.8MB)는 GitHub 버전에서만
embedded = "\n".join(f'<script id="{k}" type="application/json">{v if k not in ART_SKIP else ""}</script>' for k, v in blobs.items())
with open("artifact.html", "w", encoding="utf-8") as f:
    f.write(common.replace("__DATA_BLOCKS__", embedded))
# ── index.html (GitHub Pages): 데이터를 data/*.json 으로 분리. 파일 이름에 내용 해시(지문) 8자리를 붙여
#    내용이 바뀌면 이름도 바뀌게 함 → 브라우저·서비스 워커가 옛 파일을 오래 캐시해도 새 버전과 섞이지 않음 ──
os.makedirs("data", exist_ok=True)
for old in glob.glob(os.path.join("data", "*.json")): os.remove(old)   # 이전 해시 파일 정리
linked = []
for k, v in blobs.items():
    raw = v.replace("\\u003c", "<")   # 별도 파일에서는 < 를 그대로 둬도 안전
    h = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]
    name = f"data/{k}.{h}.json"
    with open(name, "w", encoding="utf-8") as f: f.write(raw)
    linked.append(f'<script id="{k}" type="application/json" data-src="{name}"></script>')
    print(f"  {name}  {len(raw.encode('utf-8'))//1024} KB")
html = common.replace("__DATA_BLOCKS__", "\n".join(linked))
# index.html: GitHub Pages 등 단독 배포용 완전한 문서. 폰 브라우저가 화면 폭에 맞추도록 viewport 메타태그가 꼭 필요
title_start = html.find("<title>"); title_end = html.find("</title>") + len("</title>")
title = html[title_start:title_end]; body = html[:title_start] + html[title_end:]
head = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#F4F6F9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#141922" media="(prefers-color-scheme: dark)">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="汉习">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%232B7F68'/%3E%3Ctext x='32' y='44' font-size='34' text-anchor='middle' fill='white' font-family='serif'%3E习%3C/text%3E%3C/svg%3E">
<link rel="apple-touch-icon" href="icons/icon-180.png">
<link rel="manifest" href="manifest.json">
{title}
<style>img{{max-width:100%}}</style>
<script>
// PWA: 홈 화면 설치·오프라인용 서비스 워커 등록 (https 에서만 동작. claude.ai 게시본에는 없음)
if ('serviceWorker' in navigator && location.protocol === 'https:') {{
  window.addEventListener('load', () => {{ navigator.serviceWorker.register('sw.js', {{ updateViaCache: 'none' }}).then(reg => reg.update()).catch(() => {{}}); }});
  // 새 서비스 워커가 자리를 잡으면(=새 버전) 한 번 새로고침해서 바로 반영
  let reloaded = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {{ if (reloaded) return; reloaded = true; if (navigator.serviceWorker.controller) location.reload(); }});
}}
</script>
</head>
<body>
"""
with open("index.html", "w", encoding="utf-8") as f:
    f.write(head + body + "\n</body>\n</html>\n")
print("획순 데이터", len(strokes), "자 내장 / hanzi-writer", "포함" if hw else "없음")
print("예문", len(sents["sentences"]), "개 포함")
print("index.html 생성 완료 —", len(data["words"]), "단어")
