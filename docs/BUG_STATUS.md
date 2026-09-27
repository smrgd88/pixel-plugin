# 버그 수정 및 반영 현황

확인일: **2026-09-27**. 기준은 이 저장소의 `develop`이며, 최신 반영은
[플러그인 PR #7](https://github.com/smrgd88/pixel-plugin/pull/7)의 병합 커밋
`5294bc264469f59fd3271720179b46bd8937f7c7`입니다.

내장 MCP는 [mcp-source.json](../config/mcp-source.json)의
`8d9bdde15c463b1c8227cfdb3a7d8cf65bfac966`에 고정되어 있고 도구 수는 50개입니다.
manifest 버전 0.5.0, MCP protocol serverInfo.version 0.1.0과 소스 커밋은 서로 다른 값입니다.
**develop 병합은 새 릴리스 배포나 upstream marketplace 패키지 갱신을 뜻하지 않습니다.**

## 처음 보고한 5개 버그 — 수정 및 플러그인 반영 완료

| 항목 | 수정 내용 | MCP PR | 플러그인 반영 | 검증 근거 |
|---|---|---|---|---|
| BUG-01 | 명시적 density=0 보존. 생략/null은 0.5, 0은 color1, 1은 color2 | [#17](https://github.com/smrgd88/pixel-mcp/pull/17) | [#6 병합](https://github.com/smrgd88/pixel-plugin/pull/6) | [색상 검증](COLOR_SYNC_VALIDATION.md) |
| BUG-02 | BMP/native 참조 분석 지원. native는 visible frame 1 | [#20](https://github.com/smrgd88/pixel-mcp/pull/20) | [#7 병합](https://github.com/smrgd88/pixel-plugin/pull/7) | [분석·전후 비교](EXPORT_ANALYSIS_VALIDATION.md) |
| BUG-03 | PNG/JPG/BMP 시퀀스 전체 파일 생성 및 files 목록 반환 | [#18](https://github.com/smrgd88/pixel-mcp/pull/18) | #7 병합 | [출력·전후 비교](EXPORT_ANALYSIS_VALIDATION.md) |
| BUG-04 | indexed 감색 시 의도하지 않은 단색 붕괴 수정 | [#16](https://github.com/smrgd88/pixel-mcp/pull/16) | #6 병합 | [색상 검증](COLOR_SYNC_VALIDATION.md) |
| BUG-05 | 비디더링·비indexed 감색도 실제 픽셀을 새 팔레트에 매핑 | #16 | #6 병합 | [색상 검증](COLOR_SYNC_VALIDATION.md) |

warnings 계약과 스킬 안내는 [플러그인 #4](https://github.com/smrgd88/pixel-plugin/pull/4)에서 반영했습니다.
MCP #13 capability 검사와 #14 파일 보호도 현재 내장 버전에 포함됩니다.
파일 보호는 undo/백업 기능 또는 다중 파일 세트의 crash 원자성 보장이 아닙니다.

## 추가 조사 — 전체 버그가 해소된 것은 아님

현재 내장 바이너리로 [추가 조사](BUG_AUDIT.md)를 수행해 아래 3건을 재현했습니다.
이 ID는 **이번 플러그인 조사 기록용**이며 upstream 이슈 번호가 아닙니다.

| ID | 우선도 | 재현한 문제 | 담당 / 상태 |
|---|---|---|---|
| MCP-AUDIT-01 | P1 | indexed 팔레트의 미사용 끝 항목을 제거하면 투명 인덱스가 사용 중인 색으로 이동. 파랑32px이 투명32px으로 바뀌어도 Success=true | MCP SetPalette/팔레트 resize 처리 · 미수정 |
| MCP-AUDIT-02 | P2 | analyze_reference의 edge_threshold=0이 기본값30으로 대체됨 | MCP 인자 기본값 처리 · 미수정 |
| MCP-AUDIT-03 | P2 | suggest_antialiasing의 threshold는 스키마에 민감도로 안내되지만 구현에서 사용하지 않음 | MCP 탐지/계약 · 미수정, 기존 professional 참조에도 제한 언급 |

DITHER-01(중간 Floyd density 미반영), DITHER-02(texture의 제한된 밀도 단계)는
이미 명시된 MCP 구현 제약/후속 개선 항목입니다. BUG-01의 endpoint 수정 완료와 구분합니다.
팔레트 추출의 비결정성·소수색 누락은 품질/계약 검토가 더 필요하며, 이번 조사에서 새 확정 버그로 단정하지 않았습니다.

[알려진 이슈와 사용 시 제약](KNOWN_ISSUES.md)에서 우회 방법과 제한을 확인하세요.
이번 조사는 팔레트·민감도 인자·디더링 경계에 대한 집중 조사이며 전체 50개 도구의 무결함 증명이 아닙니다.

## 검증 이력의 범위

| 기록 | 당시 실제 검증 | 이번 문서 작업과의 관계 |
|---|---|---|
| EXPORT_ANALYSIS_VALIDATION | 기본7/7, 동작105/105, 레시피8/8, Go1094, 실제 Codex 스킬→MCP→답변 | PR #7 구현 때 실행한 이력. 문서 변경으로 다시 실행했다고 표현하지 않음 |
| BUG_AUDIT | 현재 내장 MCP 38회 호출, Aseprite/PNG 독립 확인, 인자 대조 | 이번 집중 조사에서 새로 실행 |
| 앱 GUI/설치 자동 연결 | 보류 | 사용자 요청대로 미실행 상태 유지 |
| 다른 4개 플랫폼 | 교차 빌드·checksum | native 실행 통과로 해석하지 않음 |

저장소는 .claude-plugin 형태로 패키징되어 있습니다. Codex의 실제 스킬+MCP 사용은
격리 CLI 설정으로 검증했으며, 설치된 Codex 플러그인의 자동 연결을 검증한 것은 아닙니다.

## 다음 작업 경계

- 우선 권고: MCP-AUDIT-01의 투명 픽셀 손실 수정, 이후 02/03의 입력 계약 수정 및 회귀 검사.
- [MCP #21 dry-run](https://github.com/smrgd88/pixel-mcp/pull/21)은 확인 시 OPEN입니다.
  현재 내장 pin에는 없으므로 사용 가능한 기능으로 안내하지 않습니다.
- backend 수정은 MCP 저장소에서 별도 작업으로 수행하고, 병합 후 플러그인 pin·바이너리·계약·스킬을 함께 반영합니다.
- upstream 문서에 남아 있는 '병합 대기' 문구보다 실제 PR 상태와 최종 소스 커밋을 우선합니다.
