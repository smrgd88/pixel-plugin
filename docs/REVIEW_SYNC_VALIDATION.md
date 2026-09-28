# MCP #22 리뷰 수정 반영 검증

실행일: 2026-09-28. 플러그인 기준 develop `881028fb850eff575ef8f18aa3fc8a40c6d06ed8`,
작업 브랜치 `fix/shared-mcp-review-sync`. 이전 MCP pin은 `8d9bdde15c463b1c8227cfdb3a7d8cf65bfac966`,
새 pin은 `bd13cdb64d071ab69e0f4d17fc710196e6506570`입니다.
[MCP #22](https://github.com/smrgd88/pixel-mcp/pull/22)는 2026-09-28 11:06:41 KST 병합됐습니다.
최종 리뷰 head `349e98d`와 merge `bd13cdb`의 직접 tree diff는 비어 있습니다.
플러그인 [PR #9](https://github.com/smrgd88/pixel-plugin/pull/9)는 2026-09-28 13:30:39 KST 병합됐습니다.
병합55c5697과 검증 후보8066c09의 tree는 동일합니다. 릴리스 배포와 앱 갱신은 별도입니다.

후속으로 이전/현재 번들 각각56회(총112회)를 새로 비교했습니다.
[설명·이미지·수치 보고서](reports/mcp22/REPORT.md) / [HTML](reports/mcp22/REPORT.html).
아래 본문은 PR #9 구현 당시 검증 기록으로 보존하며 후속 실행과 혼동하지 않습니다.

## 변경 및 계약

동일 source archive에서 5개 배포 바이너리를 빌드하고 checksum/source metadata,
실제 tools/list 스냅샷, 생성 문서를 함께 갱신했습니다. 도구 50개와 모든 outputSchema는
그대로입니다. analyze_reference.edge_threshold 및 suggest_antialiasing.threshold는
기존 integer에 null을 추가 허용하며, draw_with_dither 설명이 새 density 의미를 반영합니다.
professional 스킬·참조·예시 및 pixel-palette 명령은 과거의 동작 불가 안내 대신
[현재 제어 계약](MCP_REVIEW_CONTROLS.md)을 사용합니다.

## 수치 비교

“이전”은 MCP #22 개발 당시의 같은 8×8 입력 비교 및 [과거 감사](BUG_AUDIT.md)의
보관 기록입니다. 이번 실행으로 이전 서버를 다시 검사했다고 주장하지 않습니다.
“현재”는 이번 플러그인 번들에 대한 새 실행 결과입니다.

| 입력/관찰 | 이전 8d9bdde | 현재 bd13cdb |
|---|---|---|
| indexed 빨강32/파랑32, 미사용 팔레트 끝 항목 축소 | 파랑32가 투명해짐 | 빨강32/파랑32 유지; 확장→축소→추가 모두 64픽셀과 mask255 보존 |
| #646464/#656565 경계, reference threshold 0/1/30 | edge 셀 0/12/0 | 12/12/0; 생략/null은 각각0 |
| alpha64 흰색 계단, AA threshold 0/63/64/128/255 | 후보5/5/5/5/5 | 5/5/0/0/0; 생략/null은 각각0 |
| Floyd density .25/.5/.75의 파랑픽셀 수 | 32/32/32 | 16/32/49 |
| checkerboard 동일 density | 32/32/64 | 16/32/48 |
| dots 동일 density | 56/56/64 | 28/56/60 |
| Bayer4 동일 density | 16/32/48 | 16/32/48 |

AA는 기존 계단 후보를 premultiplied RGBA 대비로 필터합니다. 이 입력의 대비가64이므로
threshold63에서는5개,64에서는0개가 맞습니다. preview는 원본 바이트를 보존했고,
threshold0 apply는5개를 적용해 파일이 바뀌었습니다. 단순히 인자를 받는지만 확인한 결과가 아닙니다.

빨강63/초록1 참조를5번 분석한 결과가 매번 동일했고 색별 usage 합은
98.4375%/1.5625%였습니다. 요청한5개 palette 항목은 유지되므로 중복/usage0 항목은
남을 수 있습니다. 모든 이미지에서 모든 희귀색을 보존한다는 보장은 아닙니다.

## 이번 실행

환경: macOS arm64, Aseprite 1.3.18.2 / API41, Go1.25.0,
전용 worktree의 Python venv(jsonschema/Pillow). 실제 호출은 배포 wrapper→내장 MCP→Aseprite입니다.
원본 MCP 저장소의 checkout은 변경하지 않았습니다.

새 `bin/test-mcp-review-fixes.py --aseprite … --output test-outputs/sync/review-controls`:
61회 호출(성공55, 예상된 잘못된 threshold 거부6), 모든 단언 통과.
실제 출력은 고정 outputSchema로 검증하고 Aseprite Lua inspector로 픽셀을 독립 확인합니다.
생략/null/명시적0과 대비 경계, preview/apply, 오류 시 원본 보존,
팔레트 resize,4개 density profile,5회 분석 재현성을 검사합니다.
기본 suite에는 Aseprite 없는 nullable 입력 계약 검사도 추가했습니다.

| 실행 | 결과 |
|---|---|
| test-plugin.sh | 7/7 그룹, 50도구·73예시·8레시피의 계약·문서 링크·5개 checksum·wrapper 확인 |
| test-mcp-color-operations.py | 감색36조합, density endpoint32건 및 기본값/투명픽셀/실패·동시 쓰기·sequence 회귀 통과 |
| test-mcp-warnings.py --aseprite | 성공23조건·오류3조건, text/structured equality 통과 |
| test-mcp-live.py --aseprite | 실제 호출37회 통과 |
| test-mcp-behavior.py --aseprite | 105/105 시나리오 통과 |
| test-skill-workflows.py --aseprite | 8/8 레시피 통과 |
| examples/apple/generate.py + demo/test-engine.cjs | 실제 MCP231회·3애니메이션 및 엔진 회귀 통과 |
| test-mcp-export-analysis.py --aseprite | 28회 호출; PNG/BMP/JPG sequence, 실패·원본 보호, native/BMP 분석 회귀 통과 |

## 실제 Codex 스킬 사용 시험

전역 설정을 변경하지 않은 `codex exec --ignore-user-config --ephemeral`에 현재
professional/creator 스킬 경로와 이번 wrapper를 연결했습니다. 실제 읽은 작업 스킬은
`pixel-art-professional`이며, 공통 계약·warnings·수정된 제어 문서와 예시도 읽었습니다.
새 기능의 정답 수치를 프롬프트로 주지 않고 low.png의 threshold0/30 분석 및
checkerboard density .25/.75 제작·픽셀 집계를 요청했습니다.

실제 MCP12회, 오류0. threshold0/30 결과12/0을 보고했고 checkerboard의
빨강/파랑48/16 및16/48을 get_pixels로 확인했습니다. 별도 Aseprite Lua inspector에서도
두 native 파일의64픽셀 집계가 일치했습니다. Codex 답변은 이 fixture의 실측값과
모든 패턴의 정확 비율 보장을 구분했습니다. 이 작업들에는 warnings가 반환되지 않았으며,
경고 발생 조건은 위 warnings suite에서 별도 검증했습니다.

기록: `test-outputs/sync/codex/{prompt.txt,events.jsonl,final.txt,independent-verification.json}`.
이것은 격리 CLI의 실제 스킬/MCP 사용 시험이며 설치된 앱 플러그인 자동 연결·GUI 시험이 아닙니다.

## 재현 및 증거

- `bin/build-mcp.py /path/to/pixel-mcp --release --go /path/to/go1.25.0`
- `bin/test-plugin.sh` (venv bin을 PATH 앞에 두기)
- `python bin/test-mcp-review-fixes.py --aseprite /absolute/path/to/aseprite --output test-outputs/sync/review-controls`
- 기존 live/behavior/warnings/skill/color/export-analysis 스크립트에 같은 `--aseprite` 사용
- 로컬 증거: `test-outputs/sync/{checks.json,*.log,review-controls/calls.json,review-controls/results.json}`

이전 MCP 개발 시 Go 통합1132건, race/coverage,vet 검증은 과거 실행입니다.
이번 플러그인 동기화에서는 동일 tree의 Go suite를 반복하지 않고 새 배포 번들의 실제 회귀를 수행합니다.
다른4개 플랫폼은 교차 빌드/checksum까지만 확인하며 native 실행은 미검증입니다.
설치된 Codex 앱 플러그인의 자동 연결·GUI는 사용자 요청대로 보류했습니다.

## Convergent 셀프리뷰

review-and-repair 범위는 기준881028f 대비 번들·계약·스킬·테스트·문서 변경26파일입니다.
신규 런타임 기능 개발이나 MCP #21은 제외했습니다. MCP 최종 소스의 palette/drawing/
analysis/AA 구현과 기존 client/build/validator/CI/inspector는 계약 확인을 위한 문맥으로 읽었습니다.

| ID | 우선도 | 원인·영향 | 처리/근거 |
|---|---|---|---|
| DOC-P2-001 | P2 | README의 develop 병합 단정 및 BUG_STATUS의 과거38회 호출을 현재 실행으로 읽게 하는 문구 | VERIFIED: checkout 번들/플러그인 병합을 구분하고 과거 PR #8·현재 검증을 분리; 문서/링크 검사 및 재독 통과 |

초기 발견1회, 수정1사이클(README·BUG_STATUS), 수정 diff 검토1회,
closure1회, 독립 fresh-discovery 전체범위 검토1회: 총4 review pass.
초기 P0/P1=0, P2=1 → VERIFIED1; 신규/수정 유발/재오픈/미해결 finding=0.
수정 후 pin→binary hashes→live schema→스킬 설정→성공/오류 결과 경로를 다시 확인했습니다.
최종 기본 suite7/7도 재실행했습니다. 병합 차단 사항이 없고, 아래 검증 한계를 공개한 상태로 종료합니다.

최종 후보는 HEAD881028f와 로컬 `final-candidate.json`의25파일 변경
(이 검증 보고서는 reporting-only로 제외)이며, 경로/내용 hash 집합 digest는
`66580b2bce981195586df5f589562329c2650c54200287a063f09495fa9c4fbc`입니다.
후보 선정 후 관련 파일 mutation/무효화0회. 커밋8066c09 직전에 동일성을 재확인했습니다.
미검증 native 플랫폼과 설치 GUI, 알고리즘상 비율/희귀색 보장 범위는 남는 제약입니다.

**판정: PASS_WITH_NOTES.**
