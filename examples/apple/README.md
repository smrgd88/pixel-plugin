# 사과 생성·애니메이션 예제

현재 사과 샘플을 재현하는 예제입니다. 좌표와 프레임은 Python으로 계산하고,
실제 캔버스·레이어·픽셀 기록·프레임·cel 연결·내보내기는 플러그인의 MCP 도구로 실행합니다.
Pillow는 좌표 마스크 계산과 결과 검증에 사용합니다.

## 결과 보기

- [애니메이션 3종](assets/index.html): 전체 흔들림, 잎만 흔들림, 구르기
- [브라우저 게임](assets/game.html): 씨앗 5개를 모아 깃발까지 이동
- [생성·검증 기록](assets/validation.json)

두 HTML은 이미지와 코드를 내장하므로 서버 없이 열 수 있습니다.
게임은 HTML Canvas + JavaScript 데모이며 Godot 프로젝트가 아닙니다.
이동은 ← → / A·D, 감속은 Space, 재시작은 R입니다.
화면 버튼도 누르고 있는 동안 동작합니다.

## 파일 구성

| 파일 | 역할 |
|---|---|
| `art.py` | 선택한 사과의 외곽선·색·레이어 및 픽셀 좌표 계산 |
| `frames.py` | 전체/잎/구르기 프레임 계산, 연결·회전 여백 검사 |
| `generate.py` | 실제 MCP 호출로 세 애니메이션 생성 및 검증 |
| `verify.py` | PNG 픽셀, 시트 크기·타이밍, GIF 반복 및 정지 영역 검사 |
| `build_preview.py` | 생성 결과를 내장한 HTML 갤러리와 게임 제작 |
| `demo/` | 게임 엔진·화면 코드·HTML 템플릿·엔진 테스트 |
| `assets/` | 저장소에 포함하는 대표 생성 결과 |
| `generated/` | 기본 재생성 경로, Git 추적 제외 |

## 재생성

Python 3.10 이상과 Aseprite가 필요합니다. MCP는 저장소의 `bin/pixel-mcp`를 사용합니다.
Go나 별도 MCP 소스 체크아웃은 필요 없습니다.

저장소 루트에서:

```bash
python3 -m venv examples/apple/.venv
examples/apple/.venv/bin/python -m pip install -r examples/apple/requirements.txt
examples/apple/.venv/bin/python examples/apple/generate.py \
  --aseprite /path/to/aseprite
```

macOS 앱으로 설치한 경우 `--aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite`를 사용합니다.
다른 작업 폴더에서도 스크립트의 절대 경로로 실행할 수 있습니다.
생성 경로는 기본적으로 `examples/apple/generated/`이며, `--output /path/to/output`으로 바꿀 수 있습니다.
스크립트는 지정한 출력 폴더의 같은 이름 파일을 덮어씁니다.
사용자 Aseprite 설정은 수정하지 않고 실행 중 임시 MCP 설정을 사용합니다.

개발 MCP 바이너리를 쓰려면 `--binary /absolute/path/to/pixel-mcp`를 추가합니다.
기본 래퍼는 기존 `PIXEL_MCP_BINARY` 환경변수도 지원합니다.
생성된 `validation.json`에 실제 실행한 바이너리의 버전이 기록됩니다.
`calls.json`에는 인자·응답을 포함한 실제 호출이 저장되며 출력·임시 경로는
`${OUTPUT}` / `${TEMP}`로 치환됩니다. 상세 호출 로그는 대표 `assets/`에는 포함하지 않습니다.

```bash
# 저장된 샘플 검증: Aseprite/MCP 실행 불필요
examples/apple/.venv/bin/python examples/apple/verify.py examples/apple/assets
# HTML만 다시 만들기: Python 표준 라이브러리만 사용
python3 examples/apple/build_preview.py examples/apple/assets
# 게임 엔진 테스트: Node.js 필요
node examples/apple/demo/test-engine.cjs
```

재생성은 세 애니메이션의 모든 프레임을 실제 MCP로 다시 그리므로 시간이 걸립니다.
`generated/index.html`과 `generated/game.html`에서 새 결과를 확인하세요.

## 출력과 Godot 전달

| 애니메이션 | 원본 크기 | 프레임 | 프레임 시간 | 길이 |
|---|---:|---:|---:|---:|
| `whole` 전체 흔들림 | 32×32 | 24 | 100ms | 2.4초 |
| `leaf` 잎만 흔들림 | 32×32 | 24 | 100ms | 2.4초 |
| `roll` 한 바퀴 회전 | 40×40 | 32 | 70ms | 2.24초 |

각 이름의 `.aseprite`, `.png`(첫 프레임), `.gif`, `-sheet.png`, `-sheet.json`이 있습니다.
시트는 패딩 없는 가로 배열이고 JSON에 각 프레임의 사각형과 시간이 있습니다.
`leaf`의 Body 레이어는 연결 cel로 공유되어 몸통과 가지가 고정됩니다.
`roll`은 그림을 확대하지 않고 32px 그림 주위에 회전 여백을 둔 40px 프레임입니다.

Godot으로 가져갈 주요 파일은 PNG 시트와 프레임 JSON입니다.
JSON은 Aseprite 형식이며 Godot용 자동 importer나 `.tscn`/GDScript는 제공하지 않습니다.
`roll`의 이미지 회전 중심은 (20,20), 원래 32px 그림의 몸통 중심은 (16,18)입니다.
회전 각도는 프레임당 11.25°입니다.

### 브라우저 데모의 알려진 한계

데모는 잎·가지를 포함한 프레임 최하단(`sprite-data.json`의 `feet`)을 바닥에 맞춥니다.
따라서 회전 중 높이가 변하며 덜컥거릴 수 있습니다. 이 예제 정리에서는 동작을 보존했습니다.
Godot의 충돌체·물리 이동은 별도로 구현하고, 몸통 기준 고정 원형 충돌체와 회전 중심을 사용하는 편이 적합합니다.
회전 중 픽셀의 재배치 및 원래 32프레임 회전 간격도 보일 수 있습니다.
브라우저 게임은 애셋 확인용 데모이며 완성된 물리 시뮬레이션이 아닙니다.
