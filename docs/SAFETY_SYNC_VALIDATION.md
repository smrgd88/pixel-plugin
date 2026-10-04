# MCP 안전 기능 동기화 검증 — 2026-10-02

작업: `[SHARED][FEATURE] MCP 안전 기능 동기화`.
플러그인 기준/초기 HEAD/merge-base는 develop `b7f0a413a90e1652f9dd857b121a7a5c676f88af`,
작업 브랜치는 `feature/shared-mcp-safety-sync`입니다.
이전 MCP pin `bd13cdb` → 새 pin `7f439a0df1ec0d2d24ef6dabba6de4d30c2484f9`.
상류 PR #21 dry-run, #23 snapshot/restore, #24 history/undo는 GitHub 병합 상태와
최종 소스를 확인했습니다. 상류 문서 일부의 “병합 대기”는 과거 기록입니다.

## 반영 범위

- 소스 archive에서 Go1.25.0으로 5개 플랫폼 binary를 재빌드하고 checksum을 갱신했습니다.
- 실제 tools/list는50→56개. 새6개는 create/list/restore/delete_snapshot 및 list_operation_history/undo_last_operation입니다.
- 기존50개 도구의 required 입력과 기존 input/output 속성은 그대로입니다. 세 도구에 optional dry_run 입력과 dry_run/preview 출력만 추가됐고 나머지47개 정의는 동일합니다.
- 감색 k-means의 결정적 초기화 공유도 새 source tree에 포함됩니다. 기존 감색/픽셀 회귀로 확인했습니다.
- 4개 스킬에 recovery 도구와 공통 지침을 연결했습니다. professional에는7개 검증 가능한 호출 예시를 추가했습니다.
- dry-run warnings는 원본 변경 완료가 아니라 적용 시 예상 효과로 설명합니다. 자동 기록은 false 기본값이며 전역 설정을 바꾸지 않았습니다.

## 실제 결과

macOS arm64 / Aseprite1.3.18.2(API41), 전용 Python venv, 격리 temp/snapshot 저장소입니다.
실제 배포 wrapper→MCP→Aseprite 경로를 호출했고 오류는 MCP isError/JSON-RPC 오류로 판정했습니다.

| 검사 | 원본/입력 | 실제 결과 |
|---|---|---|
| flatten dry-run 2회 | RGB8×8, 레이어2 | preview 레이어2→1, 원본 바이트·inode·mode·mtime 동일 |
| kmeans 감색 dry-run 2회 | RGB8×8, 레이어2, dither=true,2색 | preview indexed·레이어1·palette2, 원본은 유지; 감색/변환/병합 경고 보존 |
| auto shading dry-run 2회 | RGB8×8, 레이어2,cell/.6 | preview palette1→10, 원본은 유지 |
| 위3개 실제 적용 | 동일 원본·옵션 | dry_run/preview는 생략, 나머지 반환값 및 실제 상태가 preview와 일치 |
| manual snapshot | 저장된 원본 → 편집 → 서버 재시작 | snapshot 재발견, 원본 바이트 복원, pre-restore backup으로 편집 상태도 복원 |
| history | 기록 off→on, flatten+draw | on에서만2개 편집 기록; off로 재시작 후에도 최신→이전 순서 undo 및 원본 바이트 복원 |
| 실패 방어 | 지원하지 않는 dry_run, 잘못된 인자·snapshot 원본/ID·오래된 operation ID·중복 undo·외부 편집 | 예상 거부9건, 거부 시 원본 바이트·inode·mode·mtime 보존 |
| 제외 동작 | dry-run·실패·조회·export·manual snapshot | 추가 자동 편집 이력 없음 |

새 플러그인 safety suite는 **69회 호출: 성공60·예상 거부9**, 최종 통과했습니다.
이력의 no-op/quota/만료/손상/동시성/pending 복구 및 복사본 실패 정리는 아래 상류 집중 테스트로 보완했습니다.

## 이번 실행한 검증

| 명령/범위 | 결과 |
|---|---|
| bin/build-mcp.py --release | 5개 교차 빌드·checksum 통과 |
| bin/test-plugin.sh | 7/7 그룹;56도구·80예시·8레시피·링크·wrapper·기존/신규 계약 검사 |
| bin/test-mcp-safety.py --aseprite … | 69회 호출, 기본2개 계약/client 검사 통과 |
| bin/test-mcp-review-fixes.py --aseprite … | 팔레트·threshold·density·희소색 회귀61회 통과 |
| bin/test-mcp-color-operations.py --aseprite … | 감색36조합·density endpoint32건·픽셀/실패 보호 통과 |
| bin/test-mcp-warnings.py --aseprite … | 성공23조건·오류3조건, text/structured 일치 |
| bin/test-mcp-live.py --aseprite … | 37회 실제 호출 통과 |
| bin/test-mcp-behavior.py --aseprite … | 최종111/111 시나리오,56도구 모두 검사 |
| bin/test-skill-workflows.py --aseprite … | 8/8 레시피 통과 |
| bin/test-mcp-export-analysis.py --aseprite … | 28회 실제 호출 통과 |
| 상류 core -race (Snapshot/History/SpritePreview/Config/Server 선택) | subtest 포함55 PASS, 실패/skip0 |
| 상류 integration (DryRun/SnapshotMCP/HistoryMCP 선택) | subtest 포함15 PASS, 실패/skip0 |

## 실제 Codex 스킬 사용 시험

격리된 codex exec에서 현재 creator/professional 스킬을 연결해 실제 도구18회를 호출했습니다.
두 SKILL.md와 공통 안전/경고 계약을 읽은 이벤트를 확인했습니다. 사용자 전역 설정을 수정하지
않고 시험 config에서만 enable_history=true를 사용했습니다.

- RGB8×8에 빨강/초록/파랑 각2픽셀과 빈 Overlay를 만들어2개 레이어 상태를 snapshot으로 보관했습니다.
- kmeans2색/dither=true는 dry_run으로만 호출했습니다. 반환 경고3개를 잠재 적용 효과로 설명하고 원본 변경으로 오해하지 않았습니다.
- 실제 flatten은2→1레이어로 변경됐고, 목록에서 해당 flatten operation ID만 선택해 undo했습니다.
- 독립 검증에서 복원 파일 SHA-256이 수동 snapshot과 동일했고,2개 레이어·빨강/초록/파랑 각2픽셀도 일치했습니다.
-18회 중17회는 구조화된 성공 응답입니다. 빈 Overlay의 get_pixels1회는 기존 No cel found 오류를 반환했습니다. Codex는 이를 오류로 보고했고 복원을 실패/성공으로 과장하지 않았습니다.

기록은 `test-outputs/safety/codex/{prompt.txt,events.jsonl,final.txt,independent.json}`입니다.
이는 실제 스킬→MCP→Aseprite 사용 시험이며 설치 앱의 자동 연결/GUI 검증은 아닙니다.

## 실행 중 수정한 테스트

- 신규 safety fixture가 flatten 후 레이어 이름을 Layer1로 가정해 최초 실행이 실패했습니다. get_sprite_info의 실제 이름을 사용하도록 수정했고69회 검사로 재검증했습니다.
- 기존 전체 도구 sweep는 새6개 도구에 대해 No implementation으로 실패했습니다. 누락된6개 검사를 구현하고, snapshot_dir도 격리했습니다. 기존105개 시나리오는 첫 실행에서도 통과했습니다.

이 실패를 제품 오류로 세거나 최종 성공으로 숨기지 않습니다. 최초·최종 전체 도구 sweep 로그는 별도 보관합니다.

## 재현과 제한

테스트 원자료: `test-outputs/safety/{checks.json,focused-final/calls.json,*.log}`.
전체 도구 sweep는 `test-outputs/mcp-behavior/`에 버전·호출·결과를 기록합니다.
상류 소스는 이 worktree 안에 git archive로 추출했으며 원래 MCP checkout은 변경하지 않았습니다.

Go focused 명령:

```sh
go test -race -count=1 -json ./pkg/aseprite ./pkg/config ./pkg/server -run 'Test(Snapshot|History|SpritePreview|Config|Server)'
go test -count=1 -json -tags=integration ./pkg/tools -run 'Test(DryRun|SnapshotMCP|HistoryMCP)'
```

PIXEL_MCP_CONFIG는 격리 config를, TMPDIR은 canonical worktree 임시 디렉터리를 사용했습니다.
상류 전체 Go suite와 apple demo 전체 생성은 이번에는 반복하지 않았습니다. 영향받는 안전 기능·감색·스킬·export·전체 도구 동작을 집중 검증했습니다.
설치된 앱 자동 연결/GUI는 기존 요청대로 보류했습니다. 교차 빌드는 다른 OS native 실행 통과를 뜻하지 않습니다.
기존 날짜의 validation 문서는 과거 실행 기록이며 이번 실행으로 합산하지 않습니다.

## 범위 제한 셀프리뷰

기준 b7f0a41 대비32파일(5개 생성 binary·생성 schema/reference·config·스킬·문서·테스트)을
검토했습니다. 상류 config/snapshot/history/dry-run 및 wrapper/validator는 직접 계약 문맥으로
확인했고 원래 MCP 저장소는 수정하지 않았습니다. GUI, 전역 설정 변경, 신규 backend 기능은 제외했습니다.

구현 중 드러난 테스트2건(병합 후 레이어명 가정, 새 도구 sweep 누락)은 위와 같이 수정했고
각각69회/111시나리오로 재검증했습니다. 최종 scoped review에서 새 actionable finding은0건입니다.
초기 전체 검토1회, 최종 fresh 전체 검토1회(총2 review pass), 리뷰 중 mutation cycle0회,
repair-diff/closure0회, 최종 후보 무효화0회. 구현 중 보정과 리뷰 mutation 수를 구분합니다.
P0/P1/P2 미해결0, accepted/out-of-scope finding0, 재오픈0. 추가 차단 사항이 없어 종료했습니다.

최종 후보는 HEAD b7f0a41 + 로컬 candidate.json의31파일 hash 집합이며, 이 보고서만 reporting-only로 제외했습니다.
후보 선정 이후 의미 있는 파일 변경이 없음을 해시로 확인했고 기본7/7도 최종 재실행했습니다.
남는 제한은 설치 GUI 미검증, snapshot TTL/quota, 저장 파일에 한정된 undo 및 기존 empty-cel 조회 오류입니다.

**판정: PASS_WITH_NOTES.**

## 추가 셀프리뷰 수정 — 2026-10-04

추가 review-only 검토 대상은 b7f0a41→20b9750(32파일)이었고 P2/P3 각각1건을 발견했습니다.
이번 수정은20b9750을 초기 HEAD로 삼아 아래 두 항목과 직접 연결된 테스트/문서4파일에 한정했습니다.

| ID | 상태 | 수정과 재검증 |
|---|---|---|
| TEST-P2-001 | VERIFIED | 동일 --output의 store 재사용으로 snapshot이 누적되던 문제. 매 실행 private run-* 하위 경로를 만들고 그 실행 내 서버 재시작만 같은 store를 공유하도록 변경 |
| DOC-P3-002 | VERIFIED | LOCAL_MCP의 최신 검증 링크를 이 문서로 연결하고 이전 MCP #22/export 결과를 과거 이력으로 명시 |

이미 유효 snapshot100개가 남은 `test-outputs/re-review/reused`를 같은 --output으로 지정해
실제 safety suite를 연속2회 실행했습니다. 서로 다른 run-v7t7dx3n/run-xux8pz2s에 각각69회 호출
(성공60·예상 거부9)이 통과했습니다. 두 번째 실행 전후에는 첫 번째 실행의 산출물도 포함해
기존 파일 전체 SHA-256이 동일함을 확인했습니다. 기존 snapshot이나 로그를 지우지 않았습니다.
기록: `test-outputs/re-review/{verify-repair.py,repair-1.log,repair-2.log,repair-results.json,repair-plugin.log}`.

기본 suite7/7, 문서 링크/생성 문서/56도구 스키마/5개 binary checksum 검사도 다시 통과했습니다.
제품 runtime·binary·schema·config·스킬은20b9750과 동일합니다. 따라서 전체111시나리오,
Go 집중70건, Codex18회는 이번 수정에서는 반복하지 않았습니다. 설치 GUI 등의 기존 검증 한계도 유지합니다.

수정 cycle1회, repair-diff 검토1회, closure1회, 최종 baseline-to-candidate fresh 전체범위 검토1회.
직전 discovery1회를 포함한 해당 finding의 총 review pass4회. 최초 P2=1/P3=1 → VERIFIED2,
P0/P1·신규·수정 유발·재오픈·미해결 finding0. 최종 후보 선정 후 관련 mutation/인증 무효화0회.
Reviewed: 원래32파일 및 수정4파일(기존 범위 내). Context: client의 재연결/종료, snapshot quota/TTL,
검증 명령과 로컬 증거. Changed during repair: safety test, LOCAL_MCP, TESTING_CHECKLIST, 이 보고서.
Excluded: MCP backend 수정, 전역 설정, GUI/타OS native 추가 검증. 두 finding의 재현 조건이
해소되고 기존 증거 보존 및 전체 계약 대조가 완료돼 종료했습니다.

**추가 수정 판정: PASS_WITH_NOTES.**
