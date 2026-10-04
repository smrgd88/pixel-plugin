# 플러그인 로드맵

기준일: **2026-10-04** · 플러그인 기준: `develop@1f52e24` · MCP pin: `6507405` · 도구: 56개.
[현재 실행 순서](NEXT_STEPS.md) · [수정 현황](BUG_STATUS.md) · [제약](KNOWN_ISSUES.md).

이 문서는 Aseprite 작업을 위한 스킬·클라이언트 연동·MCP 번들·배포의 계획입니다.
아래 M0–M3는 저장소 문서의 단계 ID이며, GitHub에 등록된 마일스톤이나 확정 버전·일정이
아닙니다. 등록된 GitHub 마일스톤은 없습니다. 진행 작업은 각각의 PR 상태를 따릅니다.
새 작업의 시작·검증·병합에 맞춰 상태와 근거를 갱신합니다.

## 완료된 기반

| 항목 | 상태 | 근거 |
|---|---|---|
| 드로잉·색상·참조 분석·시퀀스 출력 수정과 스킬 동기화 | develop 반영 | [수정 현황](BUG_STATUS.md), 플러그인 #3–#9 |
| dry-run·스냅샷·기록 기반 undo | develop 반영 | [PR #11](https://github.com/smrgd88/pixel-plugin/pull/11), `2114d77`, [검증](SAFETY_SYNC_VALIDATION.md) |
| 오류 코드·요청 ID·부분 롤백 복구 정보 | develop 반영 | [PR #12](https://github.com/smrgd88/pixel-plugin/pull/12), `d966828`, [검증](ERROR_TRACING_VALIDATION.md) |
| Codex 우선 README 한·영, 영어 AGENTS.md | develop 반영 | [PR #13](https://github.com/smrgd88/pixel-plugin/pull/13), `82d5edb` |

manifest 버전은 0.5.0이며 누적 기능은 Unreleased입니다. 위 완료는 develop 통합 완료를
뜻합니다. 정식 플러그인 릴리스, 사용자 설치 갱신, 설치 앱 GUI 검증 완료를 뜻하지 않습니다.

## 마일스톤과 완료 조건

| ID | 목적 | 현재 상태 | 완료 조건 | 의존 관계 |
|---|---|---|---|---|
| M0 | 현재 상태·다음 작업 정리 | [PR #14](https://github.com/smrgd88/pixel-plugin/pull/14) develop 병합 완료 | 완료 PR과 남은 작업 구분, 소유 저장소·범위·검증 기준 명시, README 진입 링크·문서 검증 통과 후 develop 병합 | 없음 |
| M1 | Codex 설치·연결 검증 | CLI 범위 검증 완료: macOS 초기/모델, Linux Docker lifecycle; GUI 보류 | 선택한 설치 경로에서 스킬 탐색·참조 파일·MCP 실행·실제 결과를 검증하고 지원 클라이언트·제약을 기록 | M0 이후 범위 확정; 실제 Aseprite 필요 |
| M2 | 정식 플러그인 릴리스 | 예정 | 릴리스 기준 커밋·버전·배포 대상 결정, 메타데이터·CHANGELOG·설치 경로 일치, 검증 증거 확보, 승인된 main 반영·태그·artifact 게시 확인 | 배포 대상 클라이언트의 M1 검증, 해당 플랫폼의 M3 검증 |
| M3 | 플랫폼 실행 검증 확대 | macOS ARM·Linux amd64 Docker 일부 검증; 추가 환경 예정 | 선언한 OS/아키텍처에서 실제 Aseprite와 번들 launcher의 smoke·실패 경로 검증, CI/수동 증거·미지원 범위 기록 | M1과 병행 가능; 해당 실행 환경 필요 |

M1은 CLI 경로만 검증했다면 CLI 지원 범위에 한해 완료할 수 있습니다. 기존에 보류한 Codex
앱 GUI·자동 연결은 재개 요청 전까지 미검증으로 남깁니다. CLI 성공을 앱 GUI 성공으로
표현하지 않습니다. M2에서 미검증 클라이언트나 플랫폼을 지원 대상으로 선언하지 않습니다.

## M1: CLI 설치 SPIKE와 잔여

작업명: `[SHARED][SPIKE] Codex 플러그인 설치 및 연결 검증`.
브랜치: `spike/shared-codex-plugin-install`.

현재 README의 수동 MCP 연결 및 AGENTS.md 라우팅과 설치형 플러그인 동작을 구분합니다.
Codex 호환 manifest와 별도 stdio 설정을 추가하고 설치 cache 기반 CLI 경로를 검증했습니다.
[실행 결과와 제한](CODEX_INSTALL_VALIDATION.md)을 따릅니다. 동일 ID의 명시적 설치/제거/재설치·업그레이드와 수동 MCP 충돌은 독립 Linux Docker 환경에서
검증했습니다. M1의 CLI 범위를 완료하며 앱 GUI 및 추가 native 플랫폼 검증은 별도입니다.

완료 증거:

1. 실제 Codex/운영체제/Aseprite 버전과 플러그인·MCP 소스 식별값 기록.
2. 격리된 설치·설정에서 스킬 4개와 참조/예제 파일이 실제로 읽히는지 확인.
3. 선택된 번들로 MCP 초기화와 tools/list를 확인하고 문서의 56개 계약과 대조.
4. 최소 생성→저장→픽셀 확인→내보내기를 실제 MCP 호출로 검증하고 파일을 검사.
5. 도구 실패의 오류 코드·요청 ID, 경고, 재연결 시 서버 선택을 검사.
6. 중복 스킬·중복 MCP 연결, 경로 공백, 설치 캐시와 원본 체크아웃의 차이를 확인.
7. 재현 명령과 지원/실패/미검증 범위를 기록하고 README 한·영을 함께 갱신.

사용자 전역 설정과 history 기본값을 바꾸지 않습니다. 문서·schema 검사, 직접 CLI 호출,
모델의 실제 스킬 선택, 앱 GUI를 각각의 증거로 구분합니다. 격리 검증으로 설치 경로를
확인할 수 없다면 확인한 한계와 필요한 환경을 기록하며 성공을 가정하지 않습니다.

## 릴리스 준비 범위: M2

- 포크의 배포 경로를 선택하고 원본 저장소와 혼동되지 않도록 homepage/repository/설치 안내를 정리.
  원저자·라이선스 표기는 보존.
- 임의의 다음 버전을 미리 지정하지 않고 실제 포함 변경과 0.x 호환성 정책으로 버전을 결정.
- 해당 버전의 MCP pin, 5개 binary, checksum, 스키마, 스킬, 문서 및 검증 기록을 함께 고정.
- CHANGELOG Unreleased를 실제 포함 변경 기준으로 정리하고 개발·릴리스·사용자 설치 상태를 구분.
- 기본 플러그인 검사와 배포 대상의 실제 사용 흐름을 검증. CI의 구조·계약 검사를 native Aseprite
  실행으로 세지 않음.
- main/develop의 분기 상태를 확인하고 릴리스 범위의 커밋을 대조. 사용자 병합·게시 승인에 따라 진행.
- 설치/갱신/이전 버전 복귀 절차와 공개 artifact의 소스 커밋·체크섬을 기록.

게임 테스트용 사전 릴리스는 플러그인 정식 릴리스의 근거로 사용하지 않습니다.

## 플랫폼 검증 범위: M3

번들 대상은 macOS amd64/arm64, Linux amd64/arm64, Windows amd64입니다.
macOS arm64 실행과 Linux amd64 Docker의 CLI lifecycle/실제 Aseprite 실행을 검증했습니다.
Linux Docker는 ARM 호스트에서 amd64 emulation을 사용했으며 물리 x86_64 검증과 구분합니다.
나머지 대상은 교차 빌드·체크섬 근거입니다.
각 대상의 실제 launcher→MCP→Aseprite 실행, 최소 버전/설정 경로, 출력 파일·오류 응답을
확인해야 합니다. Windows Bash 래퍼 제약과 native launcher 필요성은 조사 후 별도 OPS 작업으로
범위를 정합니다. 실행 환경이 없는 대상을 완료로 표시하지 않습니다.

## MCP 저장소에서 선행해야 할 작업

플러그인은 서버 기능을 직접 구현하는 저장소가 아닙니다. MCP 수정/기능이 병합된 뒤에
동작·스키마 차이를 검토하고 pin·binary·스킬·검증을 함께 갱신합니다.

| 항목 | 소유/현재 상태 | 플러그인의 후속 작업 |
|---|---|---|
| RM-FIX-01 그룹 내부 draw_pixels의 레이어 조회 실패 | MCP 회귀 점검에서 재현, 별도 서버 FIX 필요 | 서버 수정 후 그룹 내부 drawing 성공·실패 보호와 관련 스킬 회귀 검증 |
| GAP-02 상세 구조/cel 읽기 전용 조회 | MCP R3의 첫 후보, 구현 범위 미확정 | 등록 도구·스키마·스킬 조회 절차와 예제 갱신 |
| 레이어·태그·cel 편집, export 범위·slice | MCP R3/R4 계획 | 서버 구현 이후 대상 지정·출력 메타데이터·기존 워크플로 호환 검증 |
| 정확한 density 비율·AA 후보 확대·팔레트 중복 제거 | 설계 후보 | 새 계약이 확정될 때만 지원 안내와 검증 갱신 |

확인한 MCP develop은 `2ec6c79`입니다. 현재 pin `6507405` 이후
[#26](https://github.com/smrgd88/pixel-mcp/pull/26) 상태 문서,
[#27](https://github.com/smrgd88/pixel-mcp/pull/27) 회귀 테스트·문서,
[#28](https://github.com/smrgd88/pixel-mcp/pull/28) Codex 안내가 병합됐습니다.
이 3개 변경은 서버 production 코드·도구 스키마를 바꾸지 않아 새 기능 번들 업데이트로
취급하지 않습니다. RM-FIX-01의 재현 근거가 추가된 것은 수정 완료를 뜻하지 않습니다.
상류 진행 상황은 [정확한 기준의 로드맵](https://github.com/smrgd88/pixel-mcp/blob/2ec6c79b184ba04d2c0cfcbf9ff49ed7475cadd2/docs/ROADMAP.md)과
[회귀 결과](https://github.com/smrgd88/pixel-mcp/blob/2ec6c79b184ba04d2c0cfcbf9ff49ed7475cadd2/docs/REGRESSION_MATRIX.md)를 따릅니다.

## 제외 범위

사용자가 Godot 게임 예제를 플러그인에 반영하지 않기로 결정했습니다. 별도 백업의
소스·에셋·테스트 자료와 Git 이력을 검증한 뒤 예제 워크트리/브랜치를 정리했습니다.
이 게임은 마일스톤·릴리스·기능 backlog에 넣지 않습니다. 저장소에 이미 있는 Aseprite
에셋 생성 예제와 그 별도 Godot 게임의 통합 여부를 혼동하지 않습니다.

GUI 실시간 편집, 임의 Lua 실행, 게임 엔진 전용 exporter는 현재 파일 기반 계약 밖입니다.
개별 제품 요구와 별도 범위 결정 없이 이 로드맵의 완료 조건으로 추가하지 않습니다.
