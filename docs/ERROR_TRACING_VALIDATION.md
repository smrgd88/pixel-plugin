# MCP 오류·요청 추적 반영 검증 — 2026-10-04

작업: `[SHARED][FEATURE] MCP 오류·요청 추적 반영`.
작업 경로: `/Users/keumheesung/orca/workspaces/pixel-plugin/shared-feature-mcp-error-tracing`.
브랜치: `feature/shared-mcp-error-tracing`.
기준 develop/origin/develop, 초기 HEAD, merge-base 모두
`2114d77ace44ac62f59404dbc96790c983b52e7a`입니다. 시작 때 원격 develop도 동일함을 확인했습니다.
Orca가 만든 신규 브랜치만 승인된 목표 이름으로 변경했으며 원본/다른 작업 워크트리는 수정하지 않았습니다.

## 반영 계약

MCP pin `7f439a0df1ec0d2d24ef6dabba6de4d30c2484f9` →
`65074051f5d3903124ead37367c7fc62d9e7e7f6` (상류 PR #25, 1 commit).
GitHub API의 merged/merge_commit_sha와 정확한 pin의 docs/ERRORS.md를 확인했습니다.
문서 첫 줄의 구현 브랜치 표기는 과거 상태입니다. [플러그인 계약](MCP_ERRORS.md).

- 별도 checkout의 정확한 commit을 archive하여 Go 1.25.0으로 5개 번들을 빌드했습니다.
  darwin amd64/arm64, linux amd64/arm64, windows amd64 모두 생성·형식·checksum 확인했습니다.
- 새 번들의 실제 tools/list를 캡처했습니다. 기준의 56개 도구 정의와 완전히 동일하며
  snapshot의 source_commit만 바뀌었습니다. 생성 참조에는 오류 계약 링크를 추가했습니다.
- 성공 payload/warnings와 call() 반환 형식은 유지합니다. ToolError는 원본 result, diagnostic,
  request_id, code, recovery를, ProtocolError는 원본 error, code, data를 보존합니다.
  둘 다 RuntimeError이며 자동 재시도는 없습니다. 성공 metadata 검사는 request()로 수행합니다.
- 4개 스킬과 관련 명령·공통 지침은 코드/요청 ID 보고, 모든 recovery 항목 보존,
  file_rollback_failed의 자동 재시도 금지와 원래 canonical 위치의 수동 확인을 안내합니다.
- 기존 오류 문구 및 예외 문자열 검색을 구조화된 코드 검사로 바꿨습니다.
  safety 실패 9건은 실제 snapshot/history/argument 코드와 오류 metadata를 검사합니다.

## 실행 환경과 결과

macOS arm64, Aseprite 1.3.18.2-arm64, Go 1.25.0, 전용 Python venv.
플러그인 wrapper의 새 번들로 실행했고 PIXEL_MCP_BINARY override는 제거했습니다.
실행별 config/temp를 사용하고 snapshot/history 검증에는 격리된 store를 사용했습니다.
사용자 config/history 설정은 변경하지 않았습니다. 상류 검증 역시 PIXEL_MCP_CONFIG로
이 워크트리의 격리 설정을 사용했습니다.

| 검증 | 결과 |
|---|---|
| bin/build-mcp.py --release | 5개 교차 빌드, source pin/checksum 일치 |
| bin/test-plugin.sh | 최종 7/7 그룹: 56도구·80예시·8레시피·링크·wrapper·생성 참조·checksum·client 회귀 |
| bin/test-mcp-errors.py --aseprite … | client 3개 검사, 실제 요청 ID 18건 통과 |
| bin/test-mcp-safety.py --aseprite … --output … | 최종 69회 호출: 성공 60, 예상 거부 9; 원본 bytes/inode/mode/mtime 보존 |
| bin/test-mcp-export-analysis.py --aseprite … | 시퀀스/단일 파일/PNG·JPG·BMP·GIF, alias/보호 출력, 참조 분석 통과 |
| bin/test-mcp-warnings.py --aseprite … | 성공 경고 조건 23개, 실제 not_found 오류 3개, text/structured 일치 |
| bin/test-mcp-live.py --aseprite … | 37회 실제 호출, 링크 cel·timing·export·픽셀 smoke 통과 |
| bin/test-mcp-behavior.py --aseprite … | 56개 도구, 111/111 시나리오, 398회 호출 통과 |
| bin/test-mcp-color-operations.py --aseprite … | 감색 36조합, density endpoint 32건, 픽셀·실패 보호·동시 쓰기 통과 |
| bin/test-mcp-review-fixes.py --aseprite … | indexed mask·threshold·density·희소색 회귀 통과 |
| bin/test-skill-workflows.py --aseprite … | 8/8 레시피 통과 |
| skill-creator quick_validate.py | 4개 스킬 모두 통과 |
| 상류 집중 go test -race | subtest 포함 37 PASS, fail/skip 0 |
| 상류 영향 패키지 go vet | 통과 |

새 오류 회귀는 timing on/off 모두 server UUID의 유일성, client ID 무시, 각 응답과 완료 로그의
ID 일치, 성공 경고 유지, 도구 오류의 text/metadata 일치 및 structuredContent 부재를 검사합니다.
실제 not_found/invalid_arguments/lua_error와 SDK 필수값/타입/unknown-tool -32602,
error.data 보존 및 non-debug 경로/입력 비노출을 확인했습니다.

rollback은 경계를 나눠 검증했습니다. 상류 실제 파일 교체 실패 주입은 commit/cancel/timeout에
앞서는 file_rollback_failed, 남아 있는 원본 백업 bytes, 순번/상대 복구 폴더, backup_file 생략,
rollback_failed:false 항목 및 정상 rollback을 검사합니다. 별도 실제 SDK session 테스트는
text와 metadata 직렬화·request ID·로그 코드·절대 경로 비노출을 확인합니다.
플러그인 client fixture는 동일 형태의 recovery 배열과 unknown code를 손실 없이 보존하고
한 번만 요청하는지 검사합니다. 번들 Aseprite 호출에서 실제 디스크 rollback 실패를 유발했다고
주장하지 않습니다. 상류 Lua 구문/실행·일반 process·timeout/cancel·임시 script 정리 및
console/file 로그의 non-debug/debug 차이도 집중 테스트에 포함됩니다.

상류 명령 (정확한 pin의 archive 디렉터리):

```sh
go test -race -count=1 -json ./internal/diagnostics ./pkg/server ./pkg/aseprite ./cmd/pixel-mcp -run 'Test(Classify|Redact|Rollback|ToolDiagnostics|Output|CommandDiagnostics|CreateLogger)'
go vet ./internal/diagnostics ./pkg/server ./pkg/aseprite ./cmd/pixel-mcp
```

구현 중 신규 fixture 2건을 보정했습니다. width=0은 handler invalid_arguments가 아니라
Lua 검증에 도달했으므로 빈 palette 입력으로 바꿨습니다. get_pixels는 필수 영역 인자가 빠져
SDK 단계에서 거부됐으므로 존재하지 않는 레이어의 delete_layer로 실제 Lua 오류를 검사했습니다.
둘 다 제품 결함으로 집계하지 않았으며 수정된 최종 회귀는 통과했습니다.
quick_validate의 PyYAML 누락은 전용 venv에 설치하여 해결했습니다.

## 범위 제한 셀프리뷰

convergent-code-review의 backend 계약 관점으로 기준 대비 37파일을 검토했습니다.
초기 전체 검토 1회, 후보 확정 뒤 fresh-discovery 전체 검토 1회, 총 2 review pass입니다.
review finding 기반 mutation cycle/repair-diff/closure 0회(수정 finding 없음),
초기/추가 P0·P1·P2·P3 finding 0, verified/accepted/out-of-scope/reopened/unresolved 모두 0입니다.
차단 위험은 초기 0 → 최종 0이며, 계약 경계와 최종 검증이 일치해 종료했습니다.

Reviewed: pin·5개 생성 binary·checksum·snapshot·client·변경 테스트·4개 스킬·명령·문서.
Context: build helper/wrapper/contract validator와 직접 소비하는 기존 테스트, 상류 diagnostics,
server/SDK 직렬화, output rollback, Lua 실행, CLI 로그, snapshot/history 등록 경계.
Changed during review repair: 없음. Excluded: 새 MCP 기능/소스 수정, 원본/다른 작업 워크트리,
전역 설정, 앱 GUI, 릴리스·병합·게시.

최종 후보는 초기 HEAD와 `test-outputs/error-tracing/candidate.json`의 36파일 SHA-256 집합입니다.
이 reporting-only 문서만 hash 집합에서 제외했습니다. 이후 관련 파일 변경/후보 무효화 0회이며,
최종 검사 후 hash 일치를 확인했습니다. 커밋은 같은 후보와 이 검증 보고서를 포함합니다.

원자료: `test-outputs/error-tracing/{candidate.json,results.json,final-results.json,*-final.log,go-focused.jsonl,go-vet.log}`.
안전 호출: `test-outputs/error-tracing/safety-final/run-ztavnq8c/calls.json`.
전체 동작: `test-outputs/mcp-behavior/run-d2b8360a/`; 레시피: `test-outputs/skill-workflows/`.
ignored 로컬 증거를 포함하므로 워크트리를 정리하기 전 보관이 필요합니다.

## Notes

- macOS arm64만 native 실행했습니다. 다른 4개 플랫폼은 교차 빌드·형식·checksum만 확인했으며,
  해당 대상의 릴리스 전 native smoke가 필요합니다.
- 설치 앱의 자동 연결/GUI 및 모델의 실제 스킬 선택은 이번 검증에 포함하지 않았습니다.
  스킬 frontmatter/링크와 8개 실제 MCP 레시피 검증을 모델 행동 검증으로 세지 않습니다.
- 상류 전체 Go/integration suite는 반복하지 않았습니다. 이 동기화의 오류/복구/Lua/로그 집중
  race·vet와 플러그인의 전체 도구/안전/출력 회귀를 수행했습니다.
- 실제 저장장치 장애를 Aseprite export 중 end-to-end로 재현하지 않았습니다. 복구 실패 주입,
  SDK 직렬화, 플러그인 client 보존은 위의 서로 다른 경계에서 검증했습니다.

**판정: PASS_WITH_NOTES.**
