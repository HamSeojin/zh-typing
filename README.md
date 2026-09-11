# 汉语 타자 단어장

HSK 3.0 (1~9급) 단어를 뜻만 보고 키보드로 입력해 외우는 웹앱. 파일 하나(`index.html`)로 동작하고, 서버가 필요 없습니다.

## 폴더 구성

| 파일 | 역할 |
|---|---|
| `index.html` | **앱 본체 (GitHub Pages 용 완전한 HTML 문서).** 단어·예문·획순 데이터가 안에 통째로 들어 있어 이 파일 하나만 있으면 어디서든 열림 |
| `artifact.html` | 같은 앱의 claude.ai 게시용 (문서 머리 부분 없이 알맹이만). claude.ai 가 겉을 씌워 줌 |
| `words.json` | 단어 데이터 (11,330개). `build_words.py` 가 만들어 냄. 앱은 이 파일을 직접 읽지 않고 `index.html` 에 내장된 복사본을 씀 |
| `build_words.py` | 데이터 준비 스크립트. 원본(GitHub 저장소)에서 HSK 3.0 단어만 골라 `words.json` 생성 |
| `app_template.html` | 앱 소스 (데이터가 빠진 원본). 앱을 고칠 때는 **이 파일**을 고친 뒤 아래 "다시 만들기" 를 실행 |
| `sentences.json` | 예문 데이터 (HSK 1~6급 단어별 1문장, 5,423개). `build_sents.py` 가 만들어 냄 |
| `build_sents.py` | `sent_out/*.json`(LLM 이 만든 예문·번역) 에 pypinyin 으로 병음을 붙이고 검증해 `sentences.json` 생성 |
| `make_index.py` | `app_template.html` + `words.json` + `sentences.json` + 획순 데이터 + hanzi-writer → `index.html` 합치기 |
| `passages.json` | 읽기 글 128편 (1~4급 × 32). `build_read.py` 가 `read_out/*.json` 에서 만듦 |
| `manifest.json`, `sw.js`, `icons/` | PWA(홈 화면 설치·오프라인) 용. GitHub Pages 에서만 동작 |
| `vendor/` | `npm install hanzi-writer hanzi-writer-data` 결과 (획순 라이브러리·데이터). 없으면 획순 기능 없이 만들어짐 |

## 앱 기능

- **학습 모드 4가지** (학습 화면에서 선택): 익히기(한자·병음·뜻 보고 따라 입력) · 뜻→한자(뜻만 보고 한자 입력) · 한자→병음(한자 보고 병음 입력, `ni3hao3`/`nǐ hǎo` 둘 다 인정) · 듣고 쓰기(발음을 듣고, 동음이의어 구분용 뜻을 참고해 한자 입력) · 손으로 쓰기(뜻·병음 보고 획순대로 손가락/마우스로 그리기, hanzi-writer 채점) · 성조 맞히기(발음 듣고 음절마다 1~4성/경성 고르기, 키보드 1~5, 3성+3성→2성+3성 변화 인정) · 자음 구별(발음 듣고 zh/j, ch/q, sh/x, z/zh, b/p, d/t, g/k, n/l/r, f/h 중 첫 자음 고르기, 통계에 자음별 정답률) · 말하기(단어를 읽으면 브라우저 음성 인식(zh-CN)으로 판정, 동음이의어로 들리면 발음 인정. 마이크 허용 필요)
- **문장 연습 3가지** (HSK 1~6급 단어 5,423개 예문, 7~9급은 예문이 없어 뜻→한자로 대체): 빈칸 채우기(예문의 빈칸 단어 입력) · 문장 받아쓰기(문장을 듣고 전체 입력, 구두점 무시, 틀린 글자 표시) · 어순 배열(흩어진 어절을 순서대로 눌러 완성)
- **옵션** (설정 탭): 한국어 뜻·영어 뜻·번체 표시, 글자 크기, 자동 발음, 음성 선택·속도
- **발음**: 브라우저 내장 TTS. Edge 브라우저에서 열면 자연스러운 신경망 음성(Xiaoxiao 등)을 고를 수 있음
- **✍ 획순 버튼**: 어느 모드에서든 단어의 획순 애니메이션 보기 (HSK 1~3급 한자 900자는 내장, 그 밖은 GitHub Pages 에서 열었을 때 인터넷에서 받아옴)
- **정답 확인 후**: YouGlish(유튜브 자막에서 단어가 쓰인 장면), Forvo(원어민 녹음), 네이버 사전 링크
- **과(課) 단위 학습**: 급수를 20단어(설정에서 10/20/30/50)씩 과로 나눔. 한 과의 단어를 전부 한 번씩 맞히면 결과 화면(정답률·틀린 단어) → 다음 과 / 다시 / 틀린 것만 다시. 완료한 과는 ✓ 표시
- **읽기 탭**: 1~4급 짧은 글 128편. 단어를 누르면 뜻·발음 풍선, 병음/번역 토글, 전체 읽어주기, 내용 질문 2개(중국어 3지선다, 번역은 답 확인 후)
- **통계 탭**: 연속 학습일, 최근 7일 문제 수, 16주 학습 달력(히트맵), 최근 14일 막대, 급수별 진도, **약한 단어 20개(바로 학습 버튼)**, 헷갈리는 짝, 모드별·성조별 정답률, 기억 단계 분포. 하루 목표 문제 수(설정)
- **PWA**: GitHub Pages 주소를 폰 사파리/크롬에서 열고 '홈 화면에 추가'하면 앱 아이콘으로 설치되고 인터넷 없이도 열림 (새 버전은 한 번 열고 나서 다음에 반영)
- **복습**: 복습 기한이 된 단어를 최대 30개씩 묶어 따로 세션으로 진행
- **간격 반복(SRS)**: 맞히면 상자↑(1→3→7→14→30→60일 뒤 복습), 틀리면 상자 0. 힌트를 보고 맞히거나 익히기 모드에서 맞힌 단어는 "아직 못 외운 것"으로 보고 바로 복습 목록에 들어감
- **내 단어장**: 학습 화면 ☆(Alt+S)이나 전체 단어 목록에서 별표로 담기 (문장 모드에서 ☆ 는 그 문장을 "내 문장"에 담고, 내 문장만 빈칸·받아쓰기·어순으로 연습 가능). 정답 확인 후 문장의 단어를 누르면 뜻 풍선, HSK에 없는 단어 직접 추가(한자·병음·뜻), 내 단어장만 따로 학습
- **한국어 뜻 직접 입력**: 학습 화면 또는 단어장 탭에서 입력 → 브라우저에 저장
- **기기 간 동기화** (설정 탭): claude.ai 게시 페이지에서는 계정 저장소로 자동 동기화. GitHub Pages 등에서 열면 GitHub 토큰(gist 권한)을 넣어 비공개 Gist 로 동기화 — 같은 토큰을 다른 기기에도 넣으면 이어짐. 항목마다 더 최근에 바뀐 쪽이 이기는 방식으로 병합
- **데이터 이동**: 설정 탭 → 내보내기(JSON 텍스트) → 다른 기기에서 붙여넣고 가져오기 (동기화 없이 옮길 때)

## 데이터 다시 만들기

```bash
# 1) 원본 데이터 (MIT 라이선스, CC-CEDICT 기반)
git clone https://github.com/drkameleon/complete-hsk-vocabulary.git data/complete-hsk-vocabulary
#    다음자(说 shuō/shuì 처럼 읽기가 여러 개인 단어)의 대표 읽기를 정하는 데 쓰는 목록
git clone --depth 1 https://github.com/krmanik/HSK-3.0.git data/HSK-3.0
# 2) words.json 생성 (기존 words.json 의 한국어 뜻은 보존됨)
python build_words.py
# 3) index.html 합치기
python make_index.py
```

## GitHub Pages 에 올리기 (폰에서 링크로 열기)

1. GitHub 에서 새 저장소 만들기 (예: `zh-typing`) — **Public** 으로
2. 이 폴더의 파일들을 저장소에 올리기 (웹에서 "Add file → Upload files" 로 드래그해도 됨. 최소한 `index.html` 하나면 충분)
3. 저장소 **Settings → Pages → Build and deployment → Source: "Deploy from a branch"**, Branch: `main`, 폴더 `/ (root)` → Save
4. 1~2분 뒤 `https://<깃허브아이디>.github.io/zh-typing/` 에서 열림. 이 주소를 폰 홈 화면에 추가하면 앱처럼 씀

이후 `index.html` 을 고쳐서 다시 올리면(commit) 자동으로 반영됩니다.

> 학습 기록은 브라우저(localStorage)에 저장되므로 기본적으로 PC 와 폰 기록은 따로입니다. 설정 탭에서 GitHub 토큰을 넣어 동기화를 켜면 기기 간에 합쳐집니다.

## 데이터 구조 (`words.json`)

```json
{ "id": 1, "s": "的", "t": "的", "py": "de", "pyn": "de5",
  "en": "of; ~'s (possessive particle) ; ...", "ko": "",
  "lv": 1, "lv26": 1, "old": 1, "freq": 1, "pos": ["u","n"] }
```

`s` 간체 · `t` 번체 · `py` 병음(성조부호) · `pyn` 병음(숫자) · `en` 영어 뜻 · `ko` 한국어 뜻 · `lv` HSK 3.0 급수(7 = 7~9급) · `lv26` 2026 개정 급수 · `old` HSK 2.0 급수 · `freq` 빈도 순위(작을수록 흔함) · `pos` 품사

## 출처

- 획순 데이터·라이브러리: [hanzi-writer](https://github.com/chanind/hanzi-writer) (MIT), [hanzi-writer-data](https://github.com/chanind/hanzi-writer-data) — Make Me a Hanzi 기반 (Arphic Public License)
- 단어 목록·뜻·병음: [drkameleon/complete-hsk-vocabulary](https://github.com/drkameleon/complete-hsk-vocabulary) (MIT) — [CC-CEDICT](https://www.mdbg.net/chinese/dictionary?page=cedict) (CC BY-SA 4.0) 기반
