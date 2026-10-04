# Codex CLI 설치·연결 검증 — 2026-10-04

작업: `[SHARED][SPIKE] Codex 설치 및 연결 검증`.
기준: `develop@1f52e2423e6106bd6c1edb6a6d8d8f0388f5b729`.
브랜치: `spike/shared-codex-plugin-install`.
MCP pin `6507405`, 도구 56개, 기존 바이너리·스키마·Claude 설정은 유지합니다.

## 결론과 범위

macOS ARM에서 Codex CLI의 별도 로컬 마켓플레이스가 설치한 캐시를 통해 스킬을 발견하고,
MCP 서버를 시작하여 실제 Aseprite 작업을 수행하는 경로를 확인했습니다.
설치 앱 GUI·다른 OS·같은 설치 ID의 명시적 재설치/업그레이드는 이 결과에 포함하지 않습니다.
M1 전체를 완료로 표시하지 않고 확인된 CLI 범위와 잔여를 구분합니다.

환경: Codex CLI 0.160.0, macOS 26.6.2 arm64, Aseprite 1.3.18.2-arm64, Python 3.14.

## 발견한 문제와 반영

기존 Claude 호환 manifest만으로 스킬 4개는 발견됐지만 `.mcp.json`의
`${CLAUDE_PLUGIN_ROOT}` 실행 경로는 Codex stdio 설정에서 확장되지 않아 서버 시작이 실패했습니다.
Codex 0.160.0의 실제 실행 환경에서 plugin root 변수는 설정되지 않았고 상대 실행 경로는
세션의 cwd를 사용했습니다. hooks의 환경 변수 계약을 stdio MCP에 그대로 적용할 수 없습니다.

- `.codex-plugin/plugin.json`: 스킬·Codex MCP 설정·표시 정보를 선언.
- `config/codex-mcp.json`: `command: ./bin/pixel-mcp`, `cwd: .`.
  Codex가 상대 cwd를 설치된 plugin root에 결합하므로 개인 경로를 저장하지 않고 실행.
- `env_vars`: PIXEL_MCP_CONFIG/PIXEL_MCP_BINARY 명시 전달.
  이 설정 없이 격리된 서버 config가 전달되지 않아 초기화가 실패하는 것도 확인.
- `.agents/plugins/marketplace.json`: `pixel-plugin-local` 로컬 카탈로그.
  Claude의 동일 이름 marketplace와 구분.

실행 시 필요한 사용자 경로는 설치 설정 또는 환경에서 지정하며 distribution에 기록하지 않습니다.
사용자에게 자동 승인 정책을 배포하지 않습니다. 모델 테스트에서만 요청한 Aseprite 작업을
허용하는 process-local MCP policy를 지정했습니다.

## 재현 방법

실제 Aseprite와 Codex CLI가 필요합니다. CLI와 Python 테스트 의존성을 준비한 후:

```bash
python3 -m venv test-outputs/venv
test-outputs/venv/bin/python -m pip install -r bin/requirements-test.txt
test-outputs/venv/bin/python bin/test-codex-install.py --aseprite /Applications/Aseprite.app/Contents/MacOS/aseprite --model-workflow
```

`--model-workflow`를 생략하면 모델 요청 없이 설치/연결/실제 프로토콜 검사를 실행합니다.
두 실행 모두 실제 Aseprite를 사용하며 가짜 서버/실행 파일로 대체하지 않습니다.

테스트는 Git 추적 파일로 깨끗한 package fixture를 만들고 AGENTS.md를 제외합니다.
개인 plugins/MCP와 standalone user skills는 해당 테스트 프로세스에서 비활성화하고,
앱 connector 기능도 비활성화합니다. 별도 marketplace 이름의 실제 Codex cache에서
스킬 4개를 읽는 것을 검증하며 enabled된 연결이 aseprite 하나인지 검사합니다.
사용자 기본 config·개인 marketplace·Aseprite config 파일의 실행 전후 checksum을 비교합니다.
기존 설정 파일을 복원하거나 덮어쓰지 않습니다. 인증은 기존 Codex 로그인에 의존하고,
설치 cache 생성은 실제 Codex runtime을 사용합니다. 완전히 별도 OS 사용자 환경은 아닙니다.

공백이 포함된 fixture 경로로 cwd 및 경로 처리도 검증합니다. 서버 process와 모델 turn은
테스트용이며 구현 작업을 다른 에이전트에 인계하는 방식이 아닙니다.

## 검사 항목

| 검사 | 확인 기준 |
|---|---|
| 스킬 탐색 | 설치 캐시의 creator/animator/professional/exporter 4개, 동일 plugin ID, 오류 없음 |
| 출처 | 캐시 launcher/config/source pin checksum이 작업 package와 일치, 실제 health 성공 |
| 연결 | aseprite만 connected, 등록 도구 56개 및 input/output schema가 현재 contract와 일치 |
| 직접 작업 | 실제 MCP 12회: 생성·픽셀·프레임·시간·native 저장·PNG/GIF/sheet/JSON·예상 실패·preview 경고 |
| 독립 검사 | Aseprite batch inspector로 native/GIF의 색상·프레임·150/100ms 확인, 실제 sheet JSON 시간 대조 |
| 오류·경고 | not_found의 isError·text·request ID, 오류 structuredContent 부재, dry-run warning과 원본 hash 보존 |
| 자연어 | 설치된 creator/animator/exporter 안내를 읽고 aseprite 호출로 32×32, 빨강/파랑 2프레임과 출력 생성 |
| 재시작 | 별도 app-server 프로세스에서 같은 cache로 재연결, 기존 sprite 조회 성공 |
| 소스 변경 | fixture manifest 버전을 바꿔도 기존 cache는 유지됨. 갱신 성공으로 해석하지 않음 |

자연어 검사에서는 MCP 호출뿐 아니라 실제 결과 파일을 독립 확인합니다. 프로토콜 테스트의
RGB 16×16 빨강/초록과 모델 테스트의 RGB 32×32 빨강/파랑을 별도로 구분합니다.
스킬 4개 발견과 모델이 실제 읽은 3개 스킬의 사용을 동일한 주장으로 합치지 않습니다.

## 개발 중 확인한 검증 경계

최초 자연어 실행은 MCP 도구의 기본 승인 정책과 approvalPolicy=never가 충돌하여
create_canvas가 거부됐습니다. 이 실행은 그림 생성 성공으로 세지 않습니다.
명시적으로 허용된 테스트 작업에 한해서 해당 프로세스의 aseprite MCP policy를 approve로
설정한 뒤 자연어 생성·출력 검사가 통과했습니다. 이 정책은 manifest나 사용자 config에 넣지 않습니다.

소스 manifest 수정만으로 cache가 자동 갱신된다고 가정한 초기 assertion은 실제 동작과
일치하지 않았습니다. 최종 검사는 기존 cache 유지 사실을 확인합니다. 별도 버전 설치 실험에서
catalog가 enabled/available이어도 스킬이 노출되지 않는 결과가 있어 업그레이드 완료를 주장하지
않습니다. 동일 설치 ID의 explicit CLI add/remove 재설치는 사용자 설정을 쓰는 별도 검증입니다.
실행한 초기 실패와 최종 통과 자료를 분리해서 보존합니다.

## 잔여와 다음 작업

- 같은 설치 ID의 명시적 설치/제거/재설치·버전 업그레이드 검증은 남아 있습니다.
  CLI 명령 syntax는 설치된 도움말 및 공식 문서와 대조했지만 사용자 기본 config에 대한
  plugin add/remove는 이번 격리 검사에서 실행하지 않았습니다.
- 앱 GUI 설치·자동 연결은 기존 보류 상태입니다. CLI 결과를 앱 검증으로 세지 않습니다.
- macOS ARM 이외의 native 플랫폼은 검증하지 않았습니다.
- 모델의 한 생성/애니메이션/export 요청을 검증했습니다. 간접 요청, 비관련 요청,
  모든 skill 선택/동작, quota·storage failure 또는 rollback 실패의 전체 조합은 이번 범위가 아닙니다.
- 로컬 CLI의 Codex 호환 패키징을 검증했습니다. 공개 plugin directory 제출, portable manifest
  전환이나 배포 artifact 검증은 릴리스 작업에서 별도로 결정합니다.

참고: [공식 패키징](https://developers.openai.com/plugins/build/plugins),
[CLI plugin 명령](https://learn.chatgpt.com/docs/developer-commands),
[설정 참조](https://learn.chatgpt.com/docs/config-file/config-reference).

## 최종 실행 결과

최종 재현 실행: `test-outputs/codex-install/run-48b248b559`.
초기 설치·직접 작업·자연어 작업·재시작·소스 변경 시 cache 유지 검사가 모두 통과했습니다.
자연어 turn의 실제 MCP 호출은 19회이며 전부 aseprite에서 completed입니다.
설치 cache의 creator/animator/exporter SKILL.md를 읽은 기록과 native/GIF/JSON의 독립 검사가
있습니다. 실행 전후 사용자 설정 checksum은 동일했습니다.

기본 플러그인 검증은 7/7 그룹 통과, 문서 링크/앵커·JSON·shell 구문 및 README 한·영
실행 예제 일치 검사가 통과했습니다. 최종 전체 결과는 관련 docs와 검사 스크립트의 변경에
맞춰 확인하며 이 실행을 다른 OS/GUI·explicit reinstall 검증으로 확대하지 않습니다.

CLI의 process-local marketplace override로 실제 저장소의 pixel-plugin-local 카탈로그를
읽고 pixel-plugin 항목이 available로 반환되는 것도 확인했습니다. 사용자 config에
marketplace add/plugin add를 저장한 검사와는 구분합니다.

## 최종 추가 확인과 리뷰

설치 cache의 바이너리 5개 checksum 및 실제 선택된 서버 --version의 source pin을 추가
대조했습니다. 실제 native 실행은 macOS ARM이며 다른 바이너리는 checksum 대조입니다.
추가 검사 이후 최종 focused 실행은 `test-outputs/codex-install/run-301f508cea`에서
초기 설치·실제 작업·재시작·cache 유지 검사를 통과했습니다. 모델 prompt/작업 로직은 바꾸지
않아 위 자연어 실행을 반복하지 않았습니다. 최종 기본 플러그인 suite도 7/7 통과했습니다.

convergent-code-review: develop@1f52e24 기준 12개 파일을 검토했습니다.
초기 검토에서 cache launcher/config hash만으로 실제 선택된 binary provenance를 확정하기
부족한 검증 공백 SHARED-P2-001을 보완했습니다. cache binary hash 및 --version source pin
검사와 focused 실행으로 VERIFIED입니다. 초기 P2 1 → 최종 0, P0/P1 0, 재오픈/신규 지적 0.
초기 1, repair cycle 1, repair-diff 1, closure 1, fresh full-scope 1 (review pass 4).
후보 선정 뒤 관련 코드 변경/후보 무효화 0. manifest/cwd/env 전달, marketplace identity,
사용자 설정 보존, MCP 응답/캐시 경계, test harness와 문서의 지원 범위를 대조했습니다.
Context는 launcher·기존 계약/inspector·Codex 0.160.0의 plugin MCP 파서/loader와 공식 문서입니다.
MCP 소스 수정, 공개 배포, 다른 플랫폼·GUI 및 explicit reinstall은 제외했습니다.

Notes: explicit 동일 ID 설치/제거/재설치·업그레이드, GUI, 다른 native 플랫폼, 모든 모델
요청 조합은 미검증입니다. 이 제한을 유지한 scoped 판정은 PASS_WITH_NOTES입니다.
