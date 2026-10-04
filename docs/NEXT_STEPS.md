# 다음 작업 — 2026-10-04

플러그인 기준은 `develop@82d5edb`입니다. MCP 번들은 `6507405`에 고정된 56개 도구이며,
버전은 0.5.0/Unreleased입니다. 우선순위·범위·완료 조건은 [로드맵](ROADMAP.md)에서 관리하고,
이 문서에는 현재 실행 순서만 둡니다.

## 완료된 통합

- [플러그인 #11](https://github.com/smrgd88/pixel-plugin/pull/11): dry-run·snapshot·undo,
  `2114d77`. [계약](MCP_SAFETY.md) · [검증](SAFETY_SYNC_VALIDATION.md).
- [플러그인 #12](https://github.com/smrgd88/pixel-plugin/pull/12): MCP #25 오류 코드·요청 추적,
  `d966828`. [계약](MCP_ERRORS.md) · [검증](ERROR_TRACING_VALIDATION.md).
- [플러그인 #13](https://github.com/smrgd88/pixel-plugin/pull/13): Codex 우선 README 한·영과
  영어 AGENTS.md, `82d5edb`.

위 PR 통합은 남은 작업이 아닙니다. 정식 릴리스·게시·사용자 설치 갱신과는 별개입니다.

## 실행 순서

1. **M0 — 로드맵 현행화:** 이번 문서 변경의 검증·리뷰를 완료하고 develop에 통합.
2. **M1 — Codex 격리 CLI 설치 SPIKE:** 설치 경로를 선택하고 스킬·참조·MCP 연결과 실제
   생성/내보내기·오류 처리를 검증. 다음 구현 후보이며 [완료 조건](ROADMAP.md)을 따름.
3. **M2 — 릴리스 준비:** 검증한 클라이언트·플랫폼에 맞게 버전, 메타데이터, CHANGELOG,
   설치/갱신 경로, artifact와 릴리스 절차를 결정.
4. **M3 — 플랫폼 검증:** 필요한 환경 확보 시 M1과 병행. 교차 빌드를 native 실행으로 세지 않음.

기존에 보류한 설치 앱 자동 연결·GUI는 재개 요청 전까지 미검증 상태로 유지합니다.
main 병합·태그·marketplace 게시, 사용자 전역 설정 변경은 별도 승인 범위입니다.

## MCP 변경을 기다리는 항목

- 그룹 내부 draw_pixels 조회 실패 RM-FIX-01: 서버 저장소의 별도 FIX 필요.
- R3 상세 구조/cel 조회와 편집, R4 export/slice 확장: 서버에서 범위를 확정·구현한 뒤 동기화.
- 성공 payload 전체 통일, 정확한 density 비율, AA 후보 확대, palette 중복 제거: 개선 후보.

MCP #26–#28은 문서/회귀 테스트 변경이며 현재 pin 이후 서버 production 코드의 변경이 없습니다.
이 문서 작업에서 번들을 다시 빌드하거나 도구를 추가하지 않습니다.

## 범위와 관리

- Godot 게임 예제는 사용자 결정에 따라 반영 제외·별도 백업 완료. 개발/릴리스 backlog에서 제외.
- 자동 history는 기본 false를 유지하며 사용자 요청 없이 켜지 않음.
- 새 서버 변경은 MCP 병합 후 plugin pin·binary·schema·스킬·검증을 한 변경으로 동기화.
- GitHub 이슈·마일스톤은 확인 시점에 등록돼 있지 않음. M0–M3는 문서상의 계획 ID임.
- 검증 기록은 실행 당시 소스와 범위를 유지하며, 새 문서 변경을 테스트 재실행으로 표현하지 않음.
- 워크트리 정리 전에 ignored 증거를 보관.
