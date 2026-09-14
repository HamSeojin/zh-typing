# 汉习 (Hànxí) — 중국어 학습 앱

HSK 3.0 (1~9급) 단어를 뜻만 보고 키보드로 입력해 외우는 웹앱. 파일 하나(`index.html`)로 동작하고, 서버가 필요 없습니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| `index.html` | **앱 본체 (GitHub Pages 용 완전한 HTML 문서, 약 200KB).** 데이터는 `data/` 폴더에서 따로 받아옴 → 첫 화면이 빨리 뜸 |
| `data/*.json` | 단어·예문·획순·읽기·모의고사·문법 데이터. `make_index.py` 가 만들며 파일 이름에 내용 지문(해시)이 붙어 있어 내용이 바뀌면 이름도 바뀜 (브라우저가 옛 파일을 오래 캐시해도 안전). **index.html 을 올릴 때 data/ 도 같이 올려야 함** |
| `artifact.html` | 같은 앱의 claude.ai 게시용 (문서 머리 부분 없이, 데이터를 안에 통째로 내장). claude.ai 가 겉을 씌워 줌 |
| `grammar.json` | 문법 항목 570개 (HSK 3.0 语法等级大纲 기반 + 한국어 설명·번역). `build_grammar.py` 가 `grammar_prep.json` + `gram_out/*.json` 에서 만듦 |
| `make_audio.py` | (선택) Microsoft Edge 신경망 음성(edge-tts)으로 단어·예문 발음 mp3 를 만들어 `audio/` 에 저장. 올려 두면 앱이 브라우저 TTS 대신 그걸 씀 |
| `words.json` | 단어 데이터 (11,330개). `build_words.py` 가 만들어 냄. 앱은 이 파일을 직접 읽지 않고 `index.html` 에 내장된 복사본을 씀 |
| `build_words.py` | 데이터 준비 스크립트. 원본(GitHub 저장소)에서 HSK 3.0 단어만 골라 `words.json` 생성 |
| `app_template.html` | 앱 소스 (데이터가 빠진 원본). 앱을 고칠 때는 **이 파일**을 고친 뒤 아래 "다시 만들기" 를 실행 |
| `sentences.json` | 예문 데이터 (HSK 1~7급 단어별 1문장, 7,392개). `build_sents.py` 가 만들어 냄 |
| `build_sents.py` | `sent_out/*.json`(LLM 이 만든 예문·번역) 에 pypinyin 으로 병음을 붙이고 검증해 `sentences.json` 생성 |
| `make_index.py` | `app_template.html` + `words.json` + `sentences.json` + 획순 데이터 + hanzi-writer → `index.html` 합치기 |
| `passages.json` | 읽기 글 224편 (1~6급·7~9급 × 32). `build_read.py` 가 `read_out/*.json` 에서 만듦 |
| `exam.json` | 모의고사 문항 은행 (1~6급·7~9급 × 듣기판단 60·대화 60·순서 40). `build_exam.py` 가 `exam_out/*.json` 에서 만듦 |
| `manifest.json`, `sw.js`, `icons/` | PWA(홈 화면 설치·오프라인) 용. GitHub Pages 에서만 동작 |
| `vendor/` | `npm install hanzi-writer hanzi-writer-data` 결과 (획순 라이브러리·데이터). 없으면 획순 기능 없이 만들어짐 |

## 앱 구조 (2026-09-11 재설계)

하단 탭 4개: **홈**(오늘 할 일 — 이어서 학습, 복습, 목표) · **학습**(단어 학습 / 문장 연습 / 읽기 / 문법 / 듣기 대화 / 모의고사 메뉴) · **단어장**(내 단어장 / 내 문장 / 모의고사 오답 / 전체 검색) · **더보기**(통계 / 설정). 단어·문장 학습은 시작 시트에서 급수·방식·과를 고른 뒤 조작판 없는 전체 화면 세션으로 들어가며, 세션 상단 제목을 누르면 언제든 시트를 다시 열어 바꿀 수 있음.

## 앱 기능

- **학습 모드 4가지** (학습 화면에서 선택): 익히기(한자·병음·뜻 보고 따라 입력) · 뜻→한자(뜻만 보고 한자 입력) · 한자→병음(한자 보고 병음 입력, `ni3hao3`/`nǐ hǎo` 둘 다 인정) · 듣고 쓰기(발음을 듣고, 동음이의어 구분용 뜻을 참고해 한자 입력) · 손으로 쓰기(뜻·병음 보고 획순대로 손가락/마우스로 그리기, hanzi-writer 채점) · 성조 맞히기(발음 듣고 음절마다 1~4성/경성 고르기, 키보드 1~5, 3성+3성→2성+3성 변화 인정) · 자음 구별(발음 듣고 zh/j, ch/q, sh/x, z/zh, b/p, d/t, g/k, n/l/r, f/h 중 첫 자음 고르기, 통계에 자음별 정답률) · 말하기(단어를 읽으면 브라우저 음성 인식(zh-CN)으로 판정, 동음이의어로 들리면 발음 인정. 마이크 허용 필요)
- **문장 연습 3가지** (HSK 1~7급 단어 7,392개 예문. 7~9급은 원본에 한 덩어리(5,907개)라 빈도순으로 7·8·9급으로 나눴고, 8~9급은 아직 예문이 없어 뜻→한자로 대체): 빈칸 채우기(예문의 빈칸 단어 입력) · 문장 받아쓰기(문장을 듣고 전체 입력, 구두점 무시, 틀린 글자 표시) · 어순 배열(흩어진 어절을 순서대로 눌러 완성)
- **옵션** (설정 탭): 한국어 뜻·영어 뜻·번체 표시, 글자 크기, 자동 발음, 음성 선택·속도
- **발음**: `audio/` 에 미리 만든 mp3 가 있으면 그걸 먼저 재생(설정에서 끌 수 있음), 없으면 브라우저 내장 TTS. Edge 브라우저에서 열면 자연스러운 신경망 음성(Xiaoxiao 등)을 고를 수 있음
- **✍ 획순 버튼**: 어느 모드에서든 단어의 획순 애니메이션 보기 (HSK 1~3급 한자 900자는 내장, 그 밖은 GitHub Pages 에서 열었을 때 인터넷에서 받아옴)
- **정답 확인 후**: YouGlish(유튜브 자막에서 단어가 쓰인 장면), Forvo(원어민 녹음), 네이버 사전 링크
- **과(課) 단위 학습**: 급수를 20단어(설정에서 10/20/30/50)씩 과로 나눔. 한 과의 단어를 전부 한 번씩 맞히면 결과 화면(정답률·틀린 단어) → 다음 과 / 다시 / 틀린 것만 다시. 완료한 과는 ✓ 표시
- **문법 탭**: HSK 3.0 공식 문법 요목 570개 항목(1급 48 · 2급 81 · 3급 81 · 4급 75 · 5급 71 · 6급 66 · 7~9급 148)을 급수별·분류별로. 항목마다 한국어 이름·공식·설명, 공식 예문(병음·번역·발음), 우리 예문 데이터에서 그 문법이 쓰인 문장을 자동으로 찾아 보여주고 그 문장들로 바로 어순 배열·빈칸·받아쓰기 연습. 검색 가능. 문장 연습에서 정답 확인 후 "관련 문법" 칩으로 연결
- **듣기 대화 연습** (모의고사 탭): 대화 문항을 시간 제한 없이 10개씩. A·B 를 다른 목소리(없으면 높낮이)로 읽어 주고, 답을 고르면 대본·번역이 보임
- **관련 단어** (정답 확인 후): 같은 글자가 든 단어(出去·走出), 발음이 같거나 성조만 다른 단어, 뜻이 비슷한 단어를 자동으로 골라 보여줌 (누르면 뜻 풍선)
- **읽기 탭**: 1~9급 짧은 글 224편(급수별 32편, 상위 급수는 논설문·에세이 수준). 제목·문제·보기의 단어도 누르면 뜻 풍선. 단어를 누르면 뜻·발음 풍선, 병음/번역 토글, 전체 읽어주기, 내용 질문 2개(중국어 3지선다, 번역은 답 확인 후)
- **모의고사 탭**: HSK 3.0 1~9급 형식을 본뜬 40문항 (7~9급은 한 시험)(듣기 판단 8·대화 8·독해 빈칸 8·순서 4·글 4·쓰기 어순 8), 30분 제한, 듣기 다시 듣기 2회, 영역별 점수·틀린 문항 복습, 공식 샘플 시험지 링크. 기출문제 아님(저작권). 빈칸·어순에서 틀린 단어는 학습 탭 복습과 별개인 "모의고사 오답 단어" 목록에 쌓이고, 거기서 학습(뜻→한자/빈칸)해 맞히면 빠짐
- **통계 탭**: 연속 학습일, 최근 7일 문제 수, 16주 학습 달력(히트맵), 최근 14일 막대, 급수별 진도, **약한 단어 20개(바로 학습 버튼)**, 헷갈리는 짝, 모드별·성조별 정답률, 기억 단계 분포. 하루 목표 문제 수(설정)
- **AI 선생님** (설정 탭에서 켬): 학습 화면·문법 상세·읽기 글의 "🤖 묻기", 단어 풍선의 "🤖 묻기"로 지금 보고 있는 단어·예문·문법을 자동으로 함께 보내며 LLM에게 질문. 빠른 질문 버튼(뜻·용법, 비슷한 단어 차이, 예문 더, 문법 분석, 외우는 요령, 흔한 실수 …) + 자유 질문. 제공자는 Gemini(무료 티어) · Claude · OpenAI 호환(DeepSeek, OpenAI 등 — API 주소와 모델 이름만 바꾸면 됨)을 고를 수 있고, API 키는 이 기기의 브라우저에만 저장(동기화·내보내기 제외). 답변은 문맥(단어·문법·글)별로 최근 30개까지 저장돼 이어서 질문할 때 최근 3문답을 함께 보내고, 단어장 탭 → AI 노트에서 검색·열람·★중요 표시·형광펜(답변 글자 드래그 후 버튼)·내 메모·복사·삭제·필터(전체/중요/형광펜)·.md 저장이 되며 기기 간 동기화·내보내기에 포함됨. 서버 없이 브라우저가 각 회사 API를 직접 호출. 잔액 소진·키 오류·모델 오류는 한국어로 안내하고, 이 기기에서 쓴 질문 수와 대략 비용을 설정에 표시
- **타자 연습** (학습 메뉴): 이미 학습한 단어(한 번 이상 맞힌 것)만으로 30초/60초/2분 드릴. 병음(성조 없이, 실제 중국어 입력기처럼) 또는 한자(입력기) 방식, 학습한 단어만으로 된 문장도 가능. 글자/분·정확도 기록, 기기 간 동기화
- **PWA**: GitHub Pages 주소를 폰 사파리/크롬에서 열고 '홈 화면에 추가'하면 앱 아이콘으로 설치되고 인터넷 없이도 열림 (새 버전은 한 번 열고 나서 다음에 반영)
- **복습**: 복습 기한이 된 단어를 최대 30개씩 묶어 따로 세션으로 진행
- **간격 반복(SRS)**: 맞히면 상자↑(1→3→7→14→30→60일 뒤 복습), 틀리면 상자 0. 힌트를 보고 맞히거나 익히기 모드에서 맞힌 단어는 "아직 못 외운 것"으로 보고 바로 복습 목록에 들어감
- **내 단어장**: 학습 화면 ☆(Alt+S)이나 전체 단어 목록에서 별표로 담기 (문장 모드에서 ☆ 는 그 문장을 "내 문장"에 담고, 내 문장만 빈칸·받아쓰기·어순으로 연습 가능). 정답 확인 후 문장의 단어를 누르면 뜻 풍선, HSK에 없는 단어 직접 추가(한자·병음·뜻), 내 단어장만 따로 학습
- **한국어 뜻 직접 입력**: 학습 화면 또는 단어장 탭에서 입력 → 브라우저에 저장
- **기기 간 동기화** (설정 탭): claude.ai 게시 페이지에서는 계정 저장소로 자동 동기화. GitHub Pages 등에서 열면 GitHub 토큰(gist 권한)을 넣어 비공개 Gist 로 동기화 — 같은 토큰을 다른 기기에도 넣으면 이어짐. 항목마다 더 최근에 바뀐 쪽이 이기는 방식으로 병합
- **데이터 이동**: 설정 탭 → 내보내기(JSON 텍스트) → 다른 기기에서 붙여넣고 가져오기 (동기화 없이 옮길 때)

## 발음 mp3 만들기 (선택)

브라우저 TTS 가 딱딱하게 들리면, PC 에서 한 번 만들어 올려 두면 폰에서도 같은 자연스러운 음성이 나옵니다.
(이 작업은 Microsoft 음성 서버에 접속해야 해서 인터넷이 되는 PC 에서 직접 실행해야 함)

```bash
pip install edge-tts        # ffmpeg 도 필요 (https://ffmpeg.org)
python make_audio.py --levels 1 2 3 4          # 1~4급 단어 약 3,200개 → audio/ (약 30MB, 10분쯤)
python make_audio.py --levels 1 2 3 --sents    # 1~3급 예문 문장까지
```

`audio/` 폴더(mp3 + index.json)를 저장소에 올리면 끝. 150개씩 한 파일에 이어 붙여(스프라이트) 파일 수가 적습니다. 중간에 끊겨도 다시 실행하면 이어서 만듭니다.

## 데이터 다시 만들기

빌드 순서대로 실행하면 `index.html` + `data/` 가 새로 만들어집니다. LLM 으로 만든 중간 산출물(`*_out/*.json`)은 저장소에 없고, 없으면 그 단계는 건너뛰면 됩니다(해당 기능만 빠짐).

```bash
# 0) 원본 단어 데이터 (MIT, CC-CEDICT 기반)
git clone https://github.com/drkameleon/complete-hsk-vocabulary.git data/complete-hsk-vocabulary
git clone --depth 1 https://github.com/krmanik/HSK-3.0.git data/HSK-3.0   # 다음자 대표 읽기 참고용

python build_words.py     # → words.json      (기존 words.json 의 한국어 뜻은 보존)
python build_sents.py     # → sentences.json  (sent_out/*.json 필요)
python build_read.py      # → passages.json   (read_out/*.json 필요)
python build_exam.py      # → exam.json       (exam_out/*.json 필요)
python build_lis.py       # → exam.json 에 듣기 연습 합치기 (lis_out/*.json 필요, build_exam.py 다음)
python build_grammar.py   # → grammar.json    (grammar_prep.json + gram_out/*.json)
python build_pinyin.py    # → pinyin.json     (발음 기초: 성모·운모 설명, 음절표, 최소 대립쌍)
python build_ext.py       # → dict/idioms/hanzi/phrases/sents2.json  (아래 ext/ 준비 필요)

python make_index.py      # app_template.html + 위 json + 획순 → index.html, data/, artifact.html
```

`vendor/` 는 `npm install hanzi-writer hanzi-writer-data` 결과입니다(획순). 없으면 획순 기능 없이 만들어집니다.

### `ext/` 준비 (build_ext.py 입력)

용량·라이선스가 제각각이라 저장소에 넣지 않았습니다. 아래를 받아 `ext/` 에 두면 재생성됩니다.

| 파일 | 어디서 | 라이선스 |
|---|---|---|
| `ext/cedict.txt` | [CC-CEDICT](https://www.mdbg.net/chinese/dictionary?page=cc-cedict) `cedict_ts.u8` | CC BY-SA 4.0 |
| `ext/idiom.json` | [chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua) `data/idiom.json` | MIT |
| `ext/mmah_dictionary.txt`, `ext/hanzi_raw.json` | [Make Me a Hanzi](https://github.com/skishore/makemeahanzi) `dictionary.txt` → HSK 한자만 추림 | Arphic Public License / LGPL |
| `ext/cmn_sentences.tsv`, `ext/kor_sentences.tsv`, `ext/cmn-kor_links.tsv` → `ext/tatoeba_ko.json` | [Tatoeba 내려받기](https://tatoeba.org/en/downloads) | CC BY 2.0 FR |
| `ext/olp_vocab.csv` → `ext/olp_ex.json` | [Chinese Zero to Hero](https://github.com/chinesezerotohero) 어휘·예문 | 각 저장소 표기 |
| `ext/opus/*` | [OPUS OpenSubtitles zh-ko](https://opus.nlpl.eu/OpenSubtitles.php) 병렬 자막 | CC BY-NC(비상업) — 학습용 발췌만 |
| `ext/zh_freq.json` | `pip install wordfreq` 후 `large_zh.msgpack.gz` 추출 (SUBTLEX-CH 대체) | MIT (데이터는 각 출처) |

LLM 으로 만든 부분(한국어 번역·설명): `ext/idiom_sel.json` + `ext/idiom_out/*.json`(성어 600 한국어 뜻·예문), `ext/hz_out/*.json`(한자 어원 한국어 힌트), `ext/subs_out/*.json`(자막에서 고른 회화 표현 1,142), `ext/misc_out/{radicals,measure}.json`(부수 214·양사 71). 같은 형식으로 다시 만들면 됩니다 — 각 `*_batches/` 폴더의 프롬프트 파일이 그대로 들어 있습니다.

## GitHub Pages 에 올리기 (폰에서 링크로 열기)

1. GitHub 에서 새 저장소 만들기 (예: `zh-typing`) — **Public** 으로
2. 이 폴더의 파일들을 저장소에 올리기 (웹에서 "Add file → Upload files" 로 드래그해도 됨. 최소한 `index.html` + `data/` 폴더 + `sw.js`, `manifest.json`, `icons/`)
3. 저장소 **Settings → Pages → Build and deployment → Source: "Deploy from a branch"**, Branch: `main`, 폴더 `/ (root)` → Save
4. 1~2분 뒤 `https://<깃허브아이디>.github.io/zh-typing/` 에서 열림. 이 주소를 폰 홈 화면에 추가하면 앱처럼 씀

이후 `index.html` 을 고쳐서 다시 올리면(commit) 자동으로 반영됩니다. 데이터가 바뀌었으면 `data/` 의 새 파일도 같이 올리세요 (옛 파일은 지워도 되고 두어도 됨).

> 학습 기록은 브라우저(localStorage)에 저장되므로 기본적으로 PC 와 폰 기록은 따로입니다. 설정 탭에서 GitHub 토큰을 넣어 동기화를 켜면 기기 간에 합쳐집니다.

## 데이터 구조 (`words.json`)

```json
{ "id": 1, "s": "的", "t": "的", "py": "de", "pyn": "de5",
  "en": "of; ~'s (possessive particle) ; ...", "ko": "",
  "lv": 1, "lv26": 1, "old": 1, "freq": 1, "pos": ["u","n"] }
```

`s` 간체 · `t` 번체 · `py` 병음(성조부호) · `pyn` 병음(숫자) · `en` 영어 뜻 · `ko` 한국어 뜻 · `lv` HSK 3.0 급수 1~9 (원본은 7~9급이 한 덩어리라 빈도순으로 7·8·9급으로 나눔) · `lv26` 2026 개정 급수 · `old` HSK 2.0 급수 · `freq` 빈도 순위(작을수록 흔함) · `pos` 품사

## 출처 · 라이선스

앱과 함께 배포되는 데이터의 출처입니다. 원본 라이선스를 따르며, 재배포가 제한된 원본(`ext/`)은 저장소에 포함하지 않았습니다.

| 쓰임 | 출처 | 라이선스 |
|---|---|---|
| 단어·뜻·병음 (`words.json`) | [drkameleon/complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary) — [CC-CEDICT](https://www.mdbg.net/chinese/dictionary?page=cedict) 기반 | MIT / CC BY-SA 4.0 |
| 급수·다음자 참고 | [krmanik/HSK-3.0](https://github.com/krmanik/HSK-3.0) | MIT |
| 획순 (`vendor/`, `data/strokes`) | [hanzi-writer](https://github.com/chanind/hanzi-writer), [hanzi-writer-data](https://github.com/chanind/hanzi-writer-data) — Make Me a Hanzi 기반 | MIT / Arphic Public License |
| 보조 사전 (`dict.json`, 48,961 단어) | CC-CEDICT | CC BY-SA 4.0 |
| 성어 600 (`idioms.json`) | [chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua) 성어 목록 + 한국어 뜻·예문은 LLM 작성 | MIT |
| 한자 분해·부수 (`hanzi.json`, 3,020자) | [Make Me a Hanzi](https://github.com/skishore/makemeahanzi) + 한국어 힌트는 LLM 작성 | Arphic Public License / LGPL |
| 회화 표현 1,142 · 자막 검색 4만 줄 (`phrases.json`, `opus.json`) | [OPUS OpenSubtitles](https://opus.nlpl.eu/OpenSubtitles.php) zh-ko 병렬 자막에서 선별 | CC BY-NC (비상업 학습용) |
| 추가 예문 (`sents2.json`) | [Tatoeba](https://tatoeba.org) zh-ko, Chinese Zero to Hero 어휘 예문 | CC BY 2.0 FR / 각 저장소 표기 |
| 빈도 정렬 | [wordfreq](https://github.com/rspeer/wordfreq) (자막·위키 등 합산) | MIT |
| 예문·읽기 글·모의고사·문법 설명·듣기 대화 | 이 프로젝트에서 LLM 으로 생성 (HSK 3.0 요목을 참고했을 뿐 기출문제 아님) | — |
| 발음 mp3 (`audio/`, 선택) | Microsoft Edge 신경망 음성(edge-tts)으로 생성 | 개인 학습용 |

앱 안에서 쓰는 바깥 링크: YouGlish(영상 속 발음), Forvo(원어민 녹음), 네이버 중국어사전.
