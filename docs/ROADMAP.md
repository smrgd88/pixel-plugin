# 플러그인 로드맵

기준일: **2026-10-18** · 플러그인 기준: `develop@49d9687` · 동기화 후보 MCP pin: `99f193a` · 도구: 64개.
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
3. 선택된 번들로 MCP 초기화와 tools/list를 확인하고 후보의 64개 계약과 대조.
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

## Top4 동기화 후보와 서버 잔여

MCP #29/#30/#31/#33/#34/#32/#35는 develop `99f193a`에 병합됐습니다.
현재 플러그인 후보는 이 commit을 정확히 pin하고 다섯 binary·64 tool schema·스킬·검증을
갱신합니다. 도구 개수만으로 완료를 판단하지 않습니다.

| 항목 | 현재 서버 상태 | 이번 플러그인 작업 |
|---|---|---|
| RM-FIX-01 nested draw_pixels | #29 수정 완료 | 중첩 고유 이름과 duplicate 거부, legacy lookup 경계 검증 |
| 구조/cel 조회·속성·unlink | #30/#31/#33 포함 | 조회→revision→편집→재조회, 공유 영향 집합/동의와 단일 cel 분리 구분 |
| 레이어/그룹·태그 편집 | #34/#32 포함 | 구조/태그 ID 무효화, 잠금/숨김/명시적 0·빈 값·이름 정책 반영 |
| 선택 export·trim/extrude/padding·출력 세트 | #35 포함 | GIF 차이, source 번호, JSON/일반 오류 rollback·background 계약 검증 |
| 정확한 indexed PNG 유지 옵션·크기 예산 정밀화 | 서버 후속 | 구현됐다고 표시하지 않음 |
| 출력 세트 crash 복구·고아 staging 정리 | 서버 후속 | 현재 ordinary-error rollback과 구분 |
| slice/pivot/nine-slice·범용 모드 전환 | 별도 범위 선정 | 서버 구현 뒤 도구/스킬/번들 동기화 |

[편집 계약](MCP_STRUCTURE_EDITING.md), [출력 지원표](MCP_EXPORT_OPTIONS.md),
[후보 검증](TOP4_SYNC_VALIDATION.md)을 따릅니다. 플러그인 develop/main 통합, 릴리스 및
개인 설치본 갱신은 각각 별도 완료 단계입니다. M2/M3를 이 기능 동기화로 완료 처리하지 않습니다.

## 제외 범위

사용자가 Godot 게임 예제를 플러그인에 반영하지 않기로 결정했습니다. 별도 백업의
소스·에셋·테스트 자료와 Git 이력을 검증한 뒤 예제 워크트리/브랜치를 정리했습니다.
이 게임은 마일스톤·릴리스·기능 backlog에 넣지 않습니다. 저장소에 이미 있는 Aseprite
에셋 생성 예제와 그 별도 Godot 게임의 통합 여부를 혼동하지 않습니다.

GUI 실시간 편집, 임의 Lua 실행, 게임 엔진 전용 exporter는 현재 파일 기반 계약 밖입니다.
개별 제품 요구와 별도 범위 결정 없이 이 로드맵의 완료 조건으로 추가하지 않습니다.
