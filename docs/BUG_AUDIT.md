# 추가 버그 집중 조사 — 2026-09-27

> Historical reproduction against MCP 8d9bdde. The three confirmed defects below are fixed by merged MCP #22 and included in the current bd13cdb bundle. “미수정” below records the audit-time state, not the current status. See [current status](BUG_STATUS.md) and [repaired controls](MCP_REVIEW_CONTROLS.md).

대상: 플러그인 develop `5294bc264469f59fd3271720179b46bd8937f7c7`, 내장 MCP
`8d9bdde15c463b1c8227cfdb3a7d8cf65bfac966`, macOS arm64 / Aseprite 1.3.18.2 API 41.
`bin/pixel-mcp` → 실제 MCP → Aseprite로 **38회 호출**했습니다.
스킬이나 앱 UI를 통한 실행은 아니며, 테스트 파일만 사용했습니다.

범위: indexed 팔레트 resize, 분석/AA 민감도 인자의 경계, 중간 density 제약.
MCP 소스나 플러그인 실행 코드는 수정하지 않았습니다. 아래 '미수정' 항목은
조사 결과이며 이 문서 PR로 런타임 버그가 해결됐다는 뜻이 아닙니다.

## MCP-AUDIT-01 — indexed 팔레트 축소 시 사용 중인 색이 투명해짐

**P1 / MCP 구현 / 재현됨 / 미수정**

1. create_canvas(width=8,height=8,color_mode=rgb).
2. Layer 1/frame 1에 왼쪽 4열은 #FF0000, 오른쪽 4열은 #0000FF로 draw_pixels.
3. quantize_palette(target_colors=2,algorithm=median_cut,dither=false,convert_to_indexed=true).
4. set_palette(colors=[#FF0000,#0000FF,#000000,#FFFFFF]). 실제 사용하는 색은 앞의 두 항목뿐.
5. set_palette(colors=[#FF0000,#0000FF])로 미사용 끝 두 항목만 제거.

| 측정 | 단계4 이후 | 단계5 이후 |
|---|---|---|
| palette 항목 수 | 4 | 2 |
| transparent index | 3 | 1 |
| 빨강 opaque 픽셀 | 32 | 32 |
| 파랑 opaque 픽셀 | 32 | 0 |
| 투명 픽셀 | 0 | 32 |
| set_palette 응답 | Success=true | Success=true |

실제 native를 독립 Aseprite의 RGB Image.drawSprite로 PNG 렌더링한 뒤 RGBA를 세어
확인했습니다. MCP get_pixels 또는 검사기의 표시 오류로 판단한 것이 아닙니다.
사용 중인 두 색의 순서·값은 그대로인데 투명 마스크가 blue index 1로 바뀝니다.

원인: [고정 소스 SetPalette](https://github.com/smrgd88/pixel-mcp/blob/8d9bdde15c463b1c8227cfdb3a7d8cf65bfac966/pkg/aseprite/lua_palette.go#L74)는
palette:resize 후 transparentColor/사용 중인 index의 관계를 보정하지 않습니다.
Aseprite resize의 mask clamp를 그대로 노출하는 MCP 통합 문제이며, 수정된 quantize_palette와는 별도 경로입니다.

대조 실험: quantize_palette가 반환한 동일한 **2개 항목을 크기 변경 없이** set_palette한 경우는
빨강32·파랑32와 mask255가 유지됐습니다. 모든 set_palette 호출이 깨진다고 일반화하지 않습니다.

대응: indexed 팔레트를 set_palette로 줄이지 말고, 원본 사본을 유지한 채 기존 길이에서 항목을 편집합니다.
실제 감색이 목적일 때만 단일 프레임 quantize_palette를 사용합니다. 임의 팔레트 교체를 감색으로 자동 대체하지 않습니다.
검증·수정 권고: 미사용 항목 제거/마스크 범위 밖/사용 중인 opaque index/완전 투명 픽셀 축을 함께 검사.

## MCP-AUDIT-02 — reference edge_threshold=0이 30으로 대체됨

**P2 / MCP 인자 기본값 처리 / 재현됨 / 미수정**

8×8 RGB를 왼쪽 #646464, 오른쪽 #656565로 채우고 PNG frame 1로 내보냅니다.
같은 PNG에 analyze_reference(target_width=8,target_height=8)의 edge_threshold만 바꿉니다.

| edge_threshold | edge grid에서 0이 아닌 칸 |
|---:|---:|
| 0 | 0 |
| 1 | 12 |
| 30 | 0 |

0 입력의 grid는 30 입력과 같았습니다. 숫자 관찰뿐 아니라
[analysis.go](https://github.com/smrgd88/pixel-mcp/blob/8d9bdde15c463b1c8227cfdb3a7d8cf65bfac966/pkg/tools/analysis.go#L100)의
`if edgeThreshold == 0 { edgeThreshold = 30 }`를 확인했습니다.
0–255로 안내된 명시적 0을 생략과 구분하지 못합니다.

대응: 양수 threshold를 명시합니다. 1은 작은 임계값으로 동작하지만 진짜 0의 대체 계약이라고 주장하지 않습니다.
수정 권고: 생략/null과 숫자0을 구분하고 0/1/30 및 낮은 대비 이미지 회귀 검사를 추가.

## MCP-AUDIT-03 — AA threshold가 탐지에 사용되지 않음

**P2 / MCP 기능·계약 불일치 / 재현됨 / 미수정**

8×8 RGB 투명 배경에서 y=1..6 각각 x=y..min(y+1,7)에 흰색 픽셀을 그려 계단 모양을 만듭니다.
같은 Layer 1/frame 1에 suggest_antialiasing(auto_apply=false,use_palette=false)를 호출합니다.

| threshold | total_edges | suggestions |
|---:|---:|---:|
| 1 | 5 | 5 |
| 128 | 5 | 5 |
| 255 | 5 | 5 |

세 응답 전체가 동일하며 원본 바이트도 유지됐습니다. 같은 결과만으로 무시를 단정하지 않고,
[detectJaggedEdges](https://github.com/smrgd88/pixel-mcp/blob/8d9bdde15c463b1c8227cfdb3a7d8cf65bfac966/pkg/tools/antialiasing.go#L109)의
`_ = threshold`도 대조했습니다. 스키마는 민감도라고 안내하지만 구현은 future-use 예약입니다.
기존 professional reference의 제한 언급을 이번에 실제 호출로 재확인한 것이며, 새 회귀로 오인하지 않습니다.

대응: threshold를 바꾸면 결과가 조절된다고 안내하지 않습니다. 제안 확인과 수동 픽셀 조정을 사용합니다.
수정 권고: 실제 효과를 구현하거나 미지원 인자를 계약에서 명시적으로 다루되, 기존 호출 호환성을 검토.

## 이미 문서화된 디더링 구현 제약 — 신규 버그와 분리

RGB 8×8 전체, 빨강=color1 / 파랑=color2, density=0.25/0.5/0.75를 비교했습니다.

| 패턴 | 0.25 빨강/파랑 | 0.5 빨강/파랑 | 0.75 빨강/파랑 | 해석 |
|---|---|---|---|---|
| floyd_steinberg | 32/32 | 32/32 | 32/32 | 세 결과의 픽셀 해시까지 동일. DITHER-01: 중간값은 기존 가로 gradient |
| checkerboard | 32/32 | 32/32 | 0/64 | DITHER-02: 이진 texture threshold의 제한된 단계 |
| bayer_4x4 | 48/16 | 32/32 | 16/48 | 대조군에서 중간값에 따라 픽셀 수가 변함 |

이는 [현재 MCP 후속 작업 목록](https://github.com/smrgd88/pixel-mcp/blob/8d9bdde15c463b1c8227cfdb3a7d8cf65bfac966/docs/NEXT_STEPS.md)에
이미 등록된 구현 개선입니다. 현재 schema/스킬은 중간값이 정확한 비율을 보장하지 않는다고 설명하므로,
이번에 endpoint 수정이 실패했다고 보고하지 않습니다.

## 플러그인 쪽 관찰 및 한계

- README의 bundled pin이 b166b16에 머물렀고 CHANGELOG에는 Unreleased 제목이 두 번 있었습니다.
  이번 문서 변경에서 현재 pin/병합 상태·역사적 검증 링크를 정리합니다.
- 이번 조사에서 플러그인 파서가 값을 바꾸거나 응답을 누락한 런타임 결함은 발견하지 못했습니다.
  위 세 현상은 스킬을 거치지 않은 MCP 호출과 서버 소스에서 확인했습니다.
- palette 추출의 소수색 누락/반복 실행 차이는 알고리즘 품질과 계약 정의를 추가 검토해야 합니다.
  형식 로딩 수정과 구분하며 이번 새 확정 버그 수에 포함하지 않습니다.
- 전체 50개 도구에 대한 추가 전수/무작위 탐색, 타 OS, 앱 GUI 테스트는 수행하지 않았습니다.
  기존 105개 동작 및 Go1094 통과 이력은 이 좁은 인자 경계의 무결함을 보장하지 않습니다.

원자료는 현재 작업의 ignored `test-outputs/audit/`에 있습니다: probe.py, calls.json,
results.json, palette-shrink.py, palette-shrink.json, shrink-before.png, shrink-after.png.
이 문서의 단계·인자·수치가 저장소에 남는 재현 요약이며, 원자료는 Git에 포함되지 않습니다.

## 문서 변경 검증

- 작업: [SHARED][DOCS] MCP 수정 현황 및 잔여 이슈 조사.
- 브랜치: docs/shared-mcp-status-audit. 기준/최초 HEAD/merge-base는
  `5294bc264469f59fd3271720179b46bd8937f7c7`이며 초기 작업 트리는 깨끗했습니다.
- 실제 워크트리: `/Users/keumheesung/orca/workspaces/pixel-plugin/shared-docs-mcp-status-audit`.
- 변경은 Markdown 15개 파일입니다. MCP pin·바이너리·JSON 계약·실행 코드는 동일합니다.
- 이번 실행: 기본 검증 `bin/test-plugin.sh` 7/7, 새 조사 MCP 호출38회,
  문서 수치/원자료 대조, 링크·계약·generated reference·checksum 및 `git diff --check` 통과.
- 기존 Go1094/동작105/레시피8 전체는 런타임 변경이 없어 반복하지 않았습니다.
  앱 GUI·다른 플랫폼 검증도 이번 범위에 포함하지 않았습니다.
- 문서 전체 검토1회 + 최종 전체 재검토1회, 총2회. 문서 리뷰의 신규 finding/수정 주기/closure/후보 무효화0회.
  코드 컨텍스트로 pinned palette·analysis·AA·dither handler와 기존 검사기를 확인했습니다.
- 위 MCP-AUDIT-01~03은 이번에 **보고한 미해결 runtime 항목**입니다. 문서 PR의 결함이나 수정 완료 항목으로 계산하지 않습니다.
  MCP runtime 수정은 별도 작업 범위이며, 문서 병합 준비 판정이 backend 버그 해결을 뜻하지 않습니다.
- 문서 PR 판정: **PASS_WITH_NOTES**. 병합/브랜치·워크트리 삭제는 하지 않습니다.
