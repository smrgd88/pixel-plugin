# 다음 작업 — 2026-10-04

이번 작업은 develop `2114d77` 기반에서 MCP `6507405`를 번들로 반영합니다.
MCP #25 오류 코드·요청 추적 계약은 상류 develop 병합 완료입니다. 기존 안전 기능도 유지합니다.
[계약](MCP_ERRORS.md) · [이번 검증](ERROR_TRACING_VALIDATION.md) · [이전 비교 보고서](reports/mcp22/REPORT.md).
이 소스 변경의 완료와 플러그인 PR 병합·릴리스 배포·사용자 설치 갱신은 별도입니다.

## 우선: 이번 플러그인 PR 통합

최종 pin·5개 binary·56도구 스키마·스킬·설정 문서·검증을 함께 리뷰하고 develop에 통합합니다.
자동 기록은 기본 false를 유지하며, 실제 사용자가 원할 때 config로 선택합니다.

## 이후: 배포 및 운영 범위 결정

- 선택한 develop을 기준으로 버전·CHANGELOG·설치 경로와 release 검증 범위를 정합니다.
- main 병합·태그·marketplace 게시와 사용자 전역 설정 변경은 이 작업에 포함하지 않습니다.
- 오류/요청 추적은 이번에 반영합니다. 성공 payload 전체 통일과 편집·조회·export 확장은 별도 범위 선정 후 진행합니다.
- 정확한 density 비율·AA 후보 확대·palette 중복 제거는 현재 계약 밖 개선 후보입니다.
- 설치된 Codex 앱 자동 연결·GUI는 기존 요청대로 보류합니다. 격리 CLI 검증과 구분합니다.
- native 플랫폼 추가 검증은 해당 환경 작업 시 수행합니다. 교차 빌드를 native 실행으로 세지 않습니다.
- 오래된 worktree의 ignored 증거는 정리 전에 별도 보관합니다.
