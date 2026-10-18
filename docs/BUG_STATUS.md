# 버그 수정 및 반영 현황

확인일: **2026-10-18** · plugin 기준 `develop@e856582` (문서 PR #17 병합), 크기 예산 동기화 후보.
이전 Top4 런타임·스킬 동기화는 [플러그인 PR #16](https://github.com/smrgd88/pixel-plugin/pull/16)으로
병합됐습니다. 이전 #12 오류/추적, #13 Codex 안내, #15 설치 검증·publisher 변경도 포함됩니다.

내장 MCP는 [mcp-source.json](../config/mcp-source.json)의
`fcb83861df08b4ee897f162d9a175bd9d149ed96`이며 도구 수는 64개입니다.
MCP 현황 문서 [PR #36](https://github.com/smrgd88/pixel-mcp/pull/36)은 develop `42bab18`에
병합됐으며 당시 runtime pin은 유지됐습니다. 이후 MCP #37 크기 예산 개선이 `fcb8386`에 병합됐고
이 후보의 번들·스킬·문서를 동기화했습니다. 이번 plugin develop 병합은 미수행이며 누적 변경은 Unreleased입니다.
manifest 버전 0.5.0, MCP protocol serverInfo.version 0.1.0과 소스 커밋은 서로 다른 값입니다.
**develop 병합은 새 릴리스 배포나 upstream marketplace 패키지 갱신을 뜻하지 않습니다.**
우선순위·소유 저장소·완료 조건은 [플러그인 로드맵](ROADMAP.md)을 따릅니다.

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

## 추가 조사 항목 — MCP #22 수정 및 내장 반영

[원래 조사](BUG_AUDIT.md)는 이전 pin 8d9bdde의 재현 기록으로 보존합니다.
아래 ID는 조사용 ID이며 upstream 이슈 번호가 아닙니다.

| ID | 과거 문제 | 현재 상태 |
|---|---|---|
| MCP-AUDIT-01 | indexed 팔레트 축소로 사용 중인 색이 투명해짐 | set_palette/add_palette_color가 mask를 보존; 현재 내장 반영 |
| MCP-AUDIT-02 | edge_threshold=0이30으로 대체 | 생략/null만30, 명시적0 사용; 현재 내장 반영 |
| MCP-AUDIT-03 | AA threshold 미적용 | premultiplied RGBA 대비 필터 적용, 생략/null128; 현재 내장 반영 |
| DITHER-01/02 | Floyd 중간값 미반영·texture 단계 제한 | gradient 평균·문양 그룹 내 순위 조절, texture 및 폭>1 Floyd의 0.5 결과 보존; 현재 내장 반영 |
| palette 추출 조사 노트 | 첫 평균 계산 전 수렴·무작위 seed로 소수색 누락/결과 차이 | 결정적 farthest-point seed와 초기 assignment 수정; 현재 내장 반영 |

수정 MCP: [PR #22](https://github.com/smrgd88/pixel-mcp/pull/22), 2026-09-28 11:06:41 KST develop 병합.
정확한 threshold 경계와 밀도 예시는 [제어 계약](MCP_REVIEW_CONTROLS.md)을 따릅니다.
“내장 반영”은 이 소스 변경의 번들에 포함됐다는 뜻이며, 릴리스 배포나 사용자 앱의 자동 갱신을 뜻하지 않습니다.

[남은 알고리즘/검증 제약](KNOWN_ISSUES.md)은 별도 유지합니다. 정확한 전역 색 비율,
AA 후보 전체 재설계, palette 중복 항목 제거, 모든 희귀색 보장은 이번 수정의 계약이 아닙니다.

## 검증 이력의 범위

| 기록 | 실제 검증 | 이번 반영 작업과의 관계 |
|---|---|---|
| EXPORT_ANALYSIS_VALIDATION | 기본7/7, 동작105/105, 레시피8/8, Go1094, 실제 Codex 스킬→MCP→답변 | PR #7 구현 때 실행한 이력. 문서 변경으로 다시 실행했다고 표현하지 않음 |
| BUG_AUDIT | 이전 pin 8d9bdde로 MCP 38회 호출, Aseprite/PNG 독립 확인, 인자 대조 | PR #8의 과거 조사 기록 |
| REVIEW_SYNC_VALIDATION | bd13cdb 번들, 실제 Aseprite 회귀·계약·스킬 확인 | PR #9 후보에서 실행한 기록 |
| [전후 비교·이미지](reports/mcp22/REPORT.md) | 이전56회+현재56회, 총112회; native26개 PNG 대조 | PR #9 후보의 후속 실제 비교. 문서 갱신 때 재실행한 결과가 아님 |
| 앱 GUI/설치 자동 연결 | 보류 | 사용자 요청대로 미실행 상태 유지 |
| [Top4 동기화](TOP4_SYNC_VALIDATION.md) | 64도구·119/119 시나리오, 11/11 레시피, 92요청, 격리 CLI 및 Linux Docker smoke | PR #16 당시 실행 기록; 이번 문서 갱신에서 재실행하지 않음 |
| macOS amd64/Linux arm64/Windows amd64 | 교차 빌드·checksum | native 실행 통과로 해석하지 않음; Linux amd64는 ARM 호스트의 Docker emulation 검증 |

저장소는 Codex와 Claude 패키징을 함께 유지합니다. Codex의 실제 스킬+MCP 사용은
격리 CLI 설정으로 검증했으며, 설치된 Codex 플러그인의 자동 연결을 검증한 것은 아닙니다.

## 다음 작업 경계

- [MCP #21 dry-run](https://github.com/smrgd88/pixel-mcp/pull/21)은 2026-09-28 13:10:26 KST 병합됐습니다(`1c410b6`). 이 번들에는 #23 snapshot/restore 및 #24 history/undo와 함께 포함됩니다. [사용 계약](MCP_SAFETY.md).
- 우선순위와 완료 조건은 [다음 작업](NEXT_STEPS.md)을 따릅니다.
- 현재 번들의 실제 실행 범위는 [크기 예산 검증](EXPORT_SIZE_BUDGET_VALIDATION.md)에 기록합니다.
  [Top4 검증](TOP4_SYNC_VALIDATION.md)은 이전 pin의 실행·실패·리뷰 이력입니다.
  [오류·요청 추적 검증](ERROR_TRACING_VALIDATION.md)은 이전 PR #12의 실행 기록입니다.
  [리뷰 수정 반영 검증](REVIEW_SYNC_VALIDATION.md)은 이전 PR #9의 실행 기록입니다.
- 새 backend 변경은 MCP 병합 후 plugin pin·5개 binary·schema·스킬을 함께 갱신합니다.
- 설치된 앱 플러그인의 자동 연결/GUI와 다른 OS native 검증은 기존 보류 상태입니다.

## 이전 안전 기능 동기화

MCP #21/#23/#24는 모두 develop 병합을 확인했습니다. #24 최종7f439a0를 기준으로 합니다.
상류 문서에 남은 “구현 브랜치/병합 대기” 표현보다 최종 소스와 실제 PR 상태를 우선합니다.
당시 실행 결과는 [안전 기능 검증](SAFETY_SYNC_VALIDATION.md)에 기록하며 과거 기록과 합산하지 않습니다.

## 오류·요청 추적 — develop 반영 완료

상류 [MCP #25](https://github.com/smrgd88/pixel-mcp/pull/25)는 `6507405`로 병합됐습니다.
플러그인 #12는 해당 pin의 5개 번들·56개 도구 계약·요청 ID·오류 코드·rollback 복구 정보와
스킬/명령을 동기화했고 develop에 병합됐습니다. [계약](MCP_ERRORS.md) · [이번 검증](ERROR_TRACING_VALIDATION.md).
main 반영·정식 게시·사용자 설치 갱신은 별도 작업으로 남아 있습니다.

## Top4 서버·플러그인 develop 반영 완료

서버 PR #29에서 RM-FIX-01 nested draw_pixels를 수정했고, #30/#31에서 구조 조회·cel 속성과
revision을 추가했습니다. #33 unlink, #34 레이어/그룹, #32 태그, #35 선택 export·trim/extrude·
padding·overwrite·출력 세트 보호가 develop `99f193a`에 포함됩니다.
plugin #16은 정확한 pin·5개 binary·64개 schema·스킬·레시피·검증을 함께 갱신하고 develop에 병합됐습니다.
[편집 계약](MCP_STRUCTURE_EDITING.md) · [export 계약](MCP_EXPORT_OPTIONS.md) ·
[실행과 리뷰](TOP4_SYNC_VALIDATION.md).

RM-FIX-01은 수정 완료지만 draw_pixels의 재귀적인 이름 조회를 다른 legacy 도구에 소급 적용하지
않습니다. get_sprite_info는 기존 경량 응답을 유지하며 상세 구조/태그는 별도 도구로 조회합니다.
현재 출력 세트의 일반 오류 rollback과 MCP #37의 실제 trim/layout/중복 기반 예산·scratch
수명 개선은 포함됩니다. 구버전(<1.3.18.2) packed 정밀화, 전체 프로세스 RSS 제한,
비협력 writer 경쟁 보호, crash 복구, indexed PNG 유지 옵션과 slices/pivot은 미구현입니다.
별도 crash-recovery SPIKE는 설계·process kill 실험이며 production 복구 tool이나 자동 retry를
추가하지 않았습니다. [현재 계약](MCP_EXPORT_OPTIONS.md#size-and-planning-budgets)과
[이번 검증](EXPORT_SIZE_BUDGET_VALIDATION.md)을 따릅니다. Plugin 후보 PR 검토·별도 병합 판단 후
M2 릴리스 준비로 진행합니다.
