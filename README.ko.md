# Codex와 Claude Code를 위한 Aseprite 픽셀 아트

[English](README.md) | **한국어**

자연어 요청으로 Aseprite에서 픽셀 아트를 만들고, 애니메이션을 구성하고, 내보낼 수 있습니다.
이 저장소는 네 가지 스킬 작업 흐름, 번들 pixel-mcp 서버, 클라이언트 사용 안내를 제공합니다.
[Codex 설정](#codex로-시작하기)부터 시작하세요. 기존 Claude Code 패키지는
[별도 절](#claude-code에서-사용하기)에서 안내합니다.

이 저장소는 [willibrandon/pixel-plugin](https://github.com/willibrandon/pixel-plugin)의
개발 포크인 [smrgd88/pixel-plugin](https://github.com/smrgd88/pixel-plugin)입니다.
번들에 포함된 [pixel-mcp 포크](https://github.com/smrgd88/pixel-mcp)는
[willibrandon/pixel-mcp](https://github.com/willibrandon/pixel-mcp)를 기반으로 합니다.

## 현재 소스 상태

번들은 **MCP 도구 56개**를 제공하며, [소스 매니페스트](config/mcp-source.json)의
`65074051f5d3903124ead37367c7fc62d9e7e7f6` 커밋에 고정되어 있습니다.
드로잉, 애니메이션, 팔레트 작업, 내보내기, 임시 복사본 미리보기, 저장 파일 스냅샷,
선택적으로 기록한 작업의 실행 취소, 요청 ID가 포함된 오류 코드를 지원합니다.

이 설명은 현재 체크아웃의 기능을 기준으로 합니다. `develop`에 병합해도 릴리스가 게시되거나
설치된 플러그인이 갱신되지는 않습니다. 원본 저장소의 마켓플레이스 설치본에는 다른 번들이
들어 있을 수 있습니다. [최신 번들 검증](docs/ERROR_TRACING_VALIDATION.md),
[수정 현황](docs/BUG_STATUS.md), [알려진 문제](docs/KNOWN_ISSUES.md)를 참고하세요.

## Codex로 시작하기

### 1. 저장소 준비

아래 명령에는 Aseprite v1.3.17.2 이상, Codex CLI, Git, 번들 실행용 Bash가 필요합니다.
셸 예제는 macOS/Linux 경로를 사용합니다. Windows에서 래퍼를 사용하려면 Bash가 필요합니다.
Windows 경로 규칙은 [설정 안내](config/README.md)를 참고하세요.
Go는 MCP를 다시 빌드할 때만 필요하고, Python과 테스트 의존성은 검증할 때 필요합니다.

```bash
git clone --branch develop --single-branch https://github.com/smrgd88/pixel-plugin.git
cd pixel-plugin
```

이미 체크아웃이 있다면 해당 저장소 루트를 사용하세요. `develop`은 계속 변경되므로
동일한 번들을 재현하려면 검토된 플러그인 커밋을 체크아웃하세요.

### 2. Aseprite 설정

`~/.config/pixel-mcp/config.json`을 만들거나 수정하여 실제 실행 파일의 절대 경로를 지정하세요.
기존 파일이 있다면 다른 설정 필드를 보존하세요. macOS의 최소 설정 예제입니다.

```json
{
  "aseprite_path": "/Applications/Aseprite.app/Contents/MacOS/aseprite"
}
```

설정 선택 순서는 `--config`, `PIXEL_MCP_CONFIG`, 사용자 홈의
`.config/pixel-mcp/config.json`입니다. JSON 경로에서는 `~`와 셸 변수가 확장되지 않습니다.
템플릿, 실행 파일 탐색 도구, 플랫폼별 경로는 [설정 안내](config/README.md)를 참고하세요.

체크아웃 루트에서 선택된 번들과 Aseprite를 확인하세요.

```bash
bin/pixel-mcp --version
bin/pixel-mcp --health
```

health 검사는 실행 환경을 확인하며 실제 드로잉 테스트는 아닙니다. `PIXEL_MCP_BINARY`가
다른 서버를 선택할 수 있으므로, 표시된 소스 버전이 이 체크아웃과 다르면 해당 설정을 확인하세요.

### 3. MCP 서버 연결

먼저 기존 Codex 연결을 확인하세요.

```bash
codex mcp list
```

`aseprite`가 이미 등록되어 있거나 설치된 플러그인이 제공한다면 새로 추가하기 전에 기존
연결을 확인하세요. CLI에 새로 등록하려면 이 체크아웃에서 실행하세요.

```bash
codex mcp add aseprite -- "$PWD/bin/pixel-mcp"
codex mcp get aseprite
```

이 명령은 Codex 설정에 실행 파일의 절대 경로를 등록합니다. 연결을 사용하는 동안 체크아웃을
그 위치에 유지하세요. 서버가 기본 경로가 아닌 설정 파일을 사용한다면 등록 시 명시하세요.

```bash
codex mcp add aseprite -- "$PWD/bin/pixel-mcp" --config /absolute/path/pixel-mcp-config.json
```

환경에 맞는 등록 명령 하나를 선택하고 두 명령을 모두 실행하지 마세요.
프로젝트 범위로 설정하려면 신뢰된 프로젝트의 `.codex/config.toml`도 사용할 수 있습니다.
[공식 MCP 안내](https://developers.openai.com/codex/mcp)를 참고하세요.
MCP 설정을 바꾼 뒤에는 Codex 세션을 다시 시작하거나 연결을 갱신하세요.

### 4. 저장소 지침 사용

이 저장소의 루트에서 Codex를 시작하세요.

```bash
codex
```

[AGENTS.md](AGENTS.md)는 Codex에 프로젝트 지침을 제공하고 픽셀 아트 작업에 맞는
`skills/*/SKILL.md`를 읽도록 안내합니다. 스킬을 설치하거나 MCP 서버를 시작하지는 않습니다.
Codex의 [지침 탐색](https://developers.openai.com/codex/guides/agents-md)은 `AGENTS.md`를
사용합니다. `CLAUDE.md`는 Claude Code용 진입점입니다.

루트의 `skills/`는 플러그인 패키징용으로 유지됩니다. 저장소를 체크아웃하는 것만으로 해당
폴더들이 독립 Codex 스킬로 자동 발견되지는 않습니다. 이 설정은 AGENTS.md의 안내에 따라
파일을 직접 읽는 방식입니다. 저장소 밖에서도 자동 탐색을 사용하려면
[Codex 스킬 탐색](https://developers.openai.com/codex/skills)에 따라 `.agents/skills` 또는
설치된 플러그인을 설정하고, 스킬이 참조하는 보조 파일도 함께 유지하세요.

다음처럼 자연어로 요청할 수 있습니다.

```text
32x32 게임보이 스타일 스프라이트를 만들고 hero.aseprite로 저장해줘.
프레임당 100ms인 걷기 애니메이션 4프레임을 추가해줘.
애니메이션 GIF와 Aseprite JSON 메타데이터가 포함된 PNG 스프라이트시트를 내보내줘.
```

이전에 격리된 Codex CLI에서 수행한 스킬/MCP 실행 검증은 프로젝트 검증 문서에 기록되어
있습니다. 설치된 Codex 플러그인의 탐색, 앱 GUI 동작, 모델의 자동 스킬 선택은 그 검증에
포함되지 않습니다. 위 수동 연결 방식은 Claude 전용 `.mcp.json` 실행 변수에 의존하지 않습니다.

## 기능과 작업 흐름

| 작업 흐름 | 예시 | 안내 |
|---|---|---|
| 생성·편집 | 캔버스, 레이어, 픽셀, 도형, 선택, 변형 | [Creator](skills/pixel-art-creator/SKILL.md) |
| 애니메이션 | 프레임 시간, 태그, 네이티브 연결 cel | [Animator](skills/pixel-art-animator/SKILL.md) |
| 색상·보정 | 레트로 팔레트, 감색, 디더링, 음영, 안티앨리어싱, 참조 분석 | [Professional](skills/pixel-art-professional/SKILL.md) |
| 내보내기 | PNG/GIF/JPG/BMP, 이미지 시퀀스, 스프라이트시트, Aseprite JSON | [Exporter](skills/pixel-art-exporter/SKILL.md) |

작업은 명시적인 스프라이트 파일 경로를 사용합니다. Aseprite GUI의 활성 문서나 저장하지 않은
문서를 대상으로 하지 않습니다. 새 캔버스는 처음에 서버 임시 디렉터리에 생성되므로 계속
보관하려면 영구적인 네이티브 파일 경로로 저장하세요.

팔레트 프리셋은 gameboy, nes, pico8, db16, db32, c64, cga, retro(db16)를 포함합니다.
두 색으로 직사각형 패턴을 그릴 때는 `draw_with_dither`를 사용하고, 기존 단일 프레임 래스터
스프라이트의 색을 줄일 때는 `quantize_palette`를 사용합니다. 감색 시 디더링을 선택할 수 있습니다.
[팔레트 프리셋](config/palettes.json)과 [색상 작업 제한](docs/MCP_COLOR_OPERATIONS.md)을 참고하세요.

내보내기는 정지 이미지, 번호가 붙은 이미지 시퀀스, 애니메이션 GIF와 horizontal, vertical,
rows, columns, packed 레이아웃의 스프라이트시트를 지원합니다. 배율과 FPS 변경은 저장한
복사본에 적용하며 내보내기 도구의 직접 인자가 아닙니다. JSON은 Aseprite 형식이며 게임 엔진에
맞게 변환해야 합니다. [내보내기 작업 흐름](skills/pixel-art-exporter/export-formats.md)과
[시퀀스 출력 처리](docs/MCP_EXPORT_ANALYSIS.md)를 참고하세요.

## 미리보기와 복구

| 요청 | 동작과 제한 |
|---|---|
| 감색·자동 음영·레이어 병합 미리보기 | 이 세 작업만 `dry_run`을 지원합니다. 원본은 유지되며 영구 미리보기 이미지는 반환하지 않습니다 |
| 저장된 스프라이트 스냅샷 | 파일 바이트를 저장합니다. 7일 뒤 만료되며 저장소 전체에서 100개 / 512 MiB 한도를 공유합니다 |
| 스냅샷 복원 | 현재 존재하는 원래 경로를 교체하고 먼저 백업 스냅샷을 만듭니다. 삭제된 원본은 재생성할 수 없습니다 |
| 기록된 작업 실행 취소 | 보존된 이력 항목이 필요합니다. `enable_history` 기본값은 `false`이며 redo나 GUI undo 연동은 없습니다 |

예: “이 단일 프레임 스프라이트를 변경하지 말고 16색 감색 결과를 미리 확인해줘.”
이력 기록은 명시적으로 설정해야 하며 저장 공간 비용이 추가됩니다. 내보내기나 새 캔버스 생성
등 모든 작업을 기록하는 것은 아닙니다. [복구 규칙](docs/MCP_SAFETY.md)을 확인하세요.

## Claude Code에서 사용하기

기존 `.claude-plugin/` 매니페스트, `commands/`, `.mcp.json`, [CLAUDE.md](CLAUDE.md)는
Claude Code에서 계속 사용할 수 있습니다. 체크아웃 루트에서 실행하세요.

```bash
claude --plugin-dir "$PWD"
```

지속적으로 설치하려면 로컬 체크아웃을 등록하고 매니페스트 이름으로 설치하세요.

```bash
claude plugin marketplace add "$PWD"
claude plugin install pixel-plugin@pixel-plugin
```

원본과 포크는 같은 마켓플레이스 이름을 사용합니다. 이미 `pixel-plugin`이 등록되어 있다면
`/plugin`에서 소스를 확인하세요. 설치본은 캐시를 사용하므로 이 체크아웃을 pull해도 설치본은
갱신되지 않습니다. [Claude Code 플러그인 안내](https://code.claude.com/docs/en/plugins)와
[설치 안내](https://code.claude.com/docs/en/discover-plugins)를 참고하세요.

다음 플러그인 명령은 셸이나 Codex가 아니라 Claude Code 안에서 입력하세요.

| 명령 | 예시 |
|---|---|
| 설정 | `/pixel-plugin:pixel-setup /absolute/path/to/aseprite` |
| 새 스프라이트 | `/pixel-plugin:pixel-new 32x32 gameboy` |
| 팔레트 | `/pixel-plugin:pixel-palette set pico8` |
| 내보내기 | `/pixel-plugin:pixel-export png hero.png scale=4` |
| 도움말 | `/pixel-plugin:pixel-help palettes` |

이 명령들은 Claude 플러그인 명령입니다. Codex에서는 자연어 요청과 스킬 안내를 사용하세요.
`commands/` 파일은 작업 흐름 참고 자료이며 Codex에 등록된 명령이 아닙니다.

## 문제 해결

- **Aseprite를 사용할 수 없음:** 선택된 서버 설정의 `aseprite_path`를 확인한 뒤 체크아웃에서
  `bin/pixel-mcp --health`를 실행하세요. [설정 안내](config/README.md)를 참고하세요.
- **Codex에서 MCP를 사용할 수 없음:** `codex mcp list`, `codex mcp get aseprite`로 등록 상태와
  절대 실행 경로를 확인하고, 변경 후 재시작하거나 재연결하세요. 설정 항목이 존재하는 것만으로
  실제 MCP 연결이 정상이라는 뜻은 아닙니다.
- **예상과 다른 서버 동작:** `bin/pixel-mcp --version`을 고정 소스 커밋과 비교하고,
  `PIXEL_MCP_BINARY` 및 실제 설치·등록된 경로를 확인하세요.
- **작업 실패:** 반환된 오류 코드와 요청 ID가 있으면 함께 보고하세요. `file_rollback_failed`이면
  모든 복구 참조와 백업을 보존하고 재시도 전에 확인하세요. 일부 출력이 변경된 상태일 수 있습니다.
  [오류 처리](docs/MCP_ERRORS.md)를 참고하세요.

알고리즘과 검증의 제한 사항은 [알려진 문제](docs/KNOWN_ISSUES.md)를 참고하세요.

## 예제와 개발

[사과 예제](examples/apple/README.md)는 재현 가능한 MCP 생성 절차, 저장소에 포함된 에셋,
오프라인 브라우저 데모를 제공합니다.

- [AGENTS.md](AGENTS.md): Codex가 읽는 프로젝트 지침, Git 작업 흐름, 스킬 안내
- [로컬 MCP 개발](docs/LOCAL_MCP.md): 재현 가능한 빌드와 테스트 명령
- [MCP 도구](docs/MCP_TOOLS.md): 도구 56개의 정확한 스키마
- [최신 검증](docs/ERROR_TRACING_VALIDATION.md): 번들 검사와 미검증 범위
- [플러그인 로드맵](docs/ROADMAP.md): 단계별 소유 범위와 완료 조건
- [다음 작업](docs/NEXT_STEPS.md): 남은 통합·릴리스 작업
- [기여 안내](CONTRIBUTING.md): 개발 지침
- [이전 비교 보고서](docs/reports/mcp22/REPORT.md): 팔레트·음영 변경 전후

번들 대상은 macOS Intel/Apple Silicon, Linux x86_64/ARM64, Windows x86_64입니다.
가장 최근 기록된 네이티브 실행 검증은 macOS Apple Silicon에서 수행했습니다.
나머지 대상은 교차 빌드와 체크섬을 검증했으며, 이는 네이티브 실행 테스트가 아닙니다.

## 라이선스

MIT. [LICENSE](LICENSE)를 참고하세요.
