# -*- coding: utf-8 -*-
"""
make_audio.py — 단어 발음 mp3 만들기 (Microsoft Edge 의 신경망 음성, edge-tts)

왜 필요한가?
  브라우저 내장 TTS(음성 합성)는 기기마다 목소리가 다르고 딱딱하다. 미리 자연스러운 음성으로 mp3 를 만들어
  앱과 함께 올려 두면 어느 기기에서 열어도 같은 좋은 발음이 난다.

어떻게 저장하나? (스프라이트 방식)
  단어마다 mp3 파일을 따로 두면 파일이 수천 개라 GitHub 웹 업로드가 힘들다. 그래서 150 단어씩 mp3 를 이어 붙여
  audio/w-000.mp3, audio/w-001.mp3 … 로 만들고, audio/index.json 에 "단어 id → [파일 번호, 시작 초, 길이 초]" 를 적어 둔다.
  앱은 그 파일을 받아 해당 구간만 재생한다. (CSS 스프라이트 이미지와 같은 발상)

실행:
  pip install edge-tts
  python make_audio.py --levels 1 2 3 4          # 1~4급 단어 (약 3,200개, 10분 정도)
  python make_audio.py --levels 1 2 3 --sents    # 예문 문장도 (audio/s-000.mp3 …)
  결과: audio/ 폴더 → GitHub 저장소에 같이 올리면 앱이 자동으로 씀 (없으면 브라우저 TTS 로 동작)

필요한 것: ffmpeg (mp3 이어 붙이기·길이 재기). 없으면 https://ffmpeg.org 에서 설치.
"""
import argparse, asyncio, json, os, subprocess, sys, tempfile, shutil

ap = argparse.ArgumentParser()
ap.add_argument("--levels", type=int, nargs="+", default=[1, 2, 3, 4])
ap.add_argument("--sents", action="store_true", help="예문 문장도 만들기")
ap.add_argument("--voice", default="zh-CN-XiaoxiaoNeural", help="edge-tts --list-voices 로 목록 확인 (남성: zh-CN-YunxiNeural)")
ap.add_argument("--rate", default="-10%", help="말하기 속도 (예: -10%%, +0%%)")
ap.add_argument("--chunk", type=int, default=150, help="한 파일에 넣을 항목 수")
ap.add_argument("--proxy", default=os.environ.get("HTTPS_PROXY", ""))
args = ap.parse_args()

try:
    import edge_tts
except ImportError:
    sys.exit("pip install edge-tts 먼저 실행하세요")
if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
    sys.exit("ffmpeg / ffprobe 가 필요합니다 (https://ffmpeg.org)")

words = json.load(open("words.json", encoding="utf-8"))["words"]
targets = [("w", w["id"], w["s"]) for w in words if w["lv"] in args.levels]
if args.sents:
    sents = json.load(open("sentences.json", encoding="utf-8"))["sentences"]
    lvof = {w["id"]: w["lv"] for w in words}
    targets += [("s", int(k), v["zh"]) for k, v in sents.items() if lvof.get(int(k)) in args.levels]
print(f"항목 {len(targets)}개 (단어 {sum(1 for t in targets if t[0]=='w')}, 문장 {sum(1 for t in targets if t[0]=='s')})")

os.makedirs("audio", exist_ok=True)
index = json.load(open("audio/index.json", encoding="utf-8")) if os.path.exists("audio/index.json") else {"w": {}, "s": {}, "voice": args.voice}
tmp = tempfile.mkdtemp()

async def synth(kind, id_, text, path):
    for attempt in range(3):
        try:
            com = edge_tts.Communicate(text, args.voice, rate=args.rate, proxy=args.proxy or None)
            await com.save(path)
            if os.path.getsize(path) > 0: return True
        except Exception as e:
            await asyncio.sleep(1 + attempt)
    print("  실패:", kind, id_, text); return False

async def synth_all(items):
    sem = asyncio.Semaphore(6)   # 동시에 6개까지 (너무 많으면 서버가 끊음)
    async def one(t):
        kind, id_, text = t
        async with sem:
            return await synth(kind, id_, text, os.path.join(tmp, f"{kind}{id_}.mp3"))
    return await asyncio.gather(*[one(t) for t in items])

def dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    return float(out or 0)

# 이미 만든 항목은 건너뜀 (중간에 끊겨도 다시 실행하면 이어서 함)
todo = [t for t in targets if str(t[1]) not in index[t[0]]]
print("새로 만들 항목", len(todo))
for kind in ("w", "s"):
    items = [t for t in todo if t[0] == kind]
    if not items: continue
    existing_files = sorted({v[0] for v in index[kind].values()})
    file_no = (max(existing_files) + 1) if existing_files else 0
    for i in range(0, len(items), args.chunk):
        chunk = items[i:i + args.chunk]
        print(f"[{kind}] {i+1}~{i+len(chunk)} 음성 생성 중…")
        ok = asyncio.run(synth_all(chunk))
        chunk = [t for t, o in zip(chunk, ok) if o]
        # 각 조각을 같은 규격(CBR 48kbps, 24kHz, 모노)으로 바꾼 뒤 이어 붙임 — 규격이 같아야 구간 탐색(seek)이 정확
        parts = []
        for t in chunk:
            src = os.path.join(tmp, f"{t[0]}{t[1]}.mp3"); dst = src + ".cbr.mp3"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-ar", "24000", "-ac", "1", "-b:a", "48k", "-af", "apad=pad_dur=0.15", dst])
            parts.append((t, dst, dur(dst)))
        lst = os.path.join(tmp, "list.txt")
        with open(lst, "w", encoding="utf-8") as f:
            for _, p, _ in parts: f.write(f"file '{p}'\n")
        out = f"audio/{kind}-{file_no:03d}.mp3"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out])
        pos = 0.0
        for t, _, d in parts:
            index[kind][str(t[1])] = [file_no, round(pos, 3), round(d, 3)]
            pos += d
        json.dump(index, open("audio/index.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        print(f"  → {out} ({os.path.getsize(out)//1024} KB, {len(parts)}개)")
        file_no += 1
        for _, p, _ in parts: os.remove(p)
shutil.rmtree(tmp, ignore_errors=True)
print("완료. audio/ 폴더의 파일을 index.html 과 같은 곳에 올리세요.")
