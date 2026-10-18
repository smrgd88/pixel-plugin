# Top4 MCP 기능 및 export 계약 동기화 검증 — 2026-10-18

작업: `[SHARED][FEATURE] Top4 MCP 기능 및 export 계약 플러그인 동기화`.
경로: `/Users/keumheesung/orca/workspaces/pixel-plugin/shared-feature-top4-mcp-sync`.
브랜치: `feature/shared-top4-mcp-sync`.
기준 develop/초기 HEAD/merge-base: `49d96871ff75a956e4b9261078303ee74ec70d8a`.
시작 시 원격 develop과 같은 commit임을 확인하고 Orca 관리 워크트리에서만 수정했습니다.

## 소스와 산출물

- MCP pin: `65074051f5d3903124ead37367c7fc62d9e7e7f6` →
  `99f193ad3a0eefcb8e8b71a3b9e3f69be47ac2d8`.
- 서버 #29/#30/#31/#33/#34/#32/#35 포함. GitHub API에서도 #35의 merge commit `99f193a` 확인.
- 원본 MCP 저장소는 이 commit의 clean develop이며 읽기/아카이브만 사용했습니다. source 변경이나
  branch 전환은 하지 않았습니다. Go focused 검사는 task 내부의 `git archive` 사본에서 실행했습니다.
- Go 1.25.0, CGO_ENABLED=0, -mod=readonly/-trimpath/-buildvcs=false 및 source-commit ldflags로
  darwin amd64/arm64, linux amd64/arm64, windows amd64를 재빌드했습니다. 기존 build helper가
  다섯 결과를 모두 만든 뒤 binary/checksum manifest를 교체했습니다.
- 다섯 format/architecture·실행 권한·SHA-256을 확인했습니다. 별도 host 재빌드의 darwin arm64
  SHA-256이 실제 bundled binary와 동일했습니다. 원본 upstream release binary를 복사하지 않았습니다.
- 새 bundled 서버의 실제 tools/list를 캡처했습니다. 추가 8개, 변경된 기존 정의 3개
  (draw_pixels/export_sprite/export_spritesheet), 총 64개이며 기존 이름의 삭제는 없습니다.
  모든 input/output schema와 live snapshot을 대조했고 참조 문서를 재생성했습니다.

publisher/Codex/Claude manifest·marketplace·config launch·원저자 MIT LICENSE는 plugin base와
byte-identical입니다. README 한/영 원저자·포크 크레딧과 영구 개인 설치본은 유지했습니다.
개인 config/marketplace/Aseprite config/설치 manifest의 보호 checksum도 일치했습니다.

## 스킬과 계약

| 영역 | 변화 |
|---|---|
| Creator | 구조 조회, revision, layer/group 속성·이동, nested draw의 고유 이름·중복 거부. get_pixels/link_cel 등 legacy lookup으로 확대하지 않음 |
| Animator | cel setter의 전체 sharing 영향·allow_linked 권한, native unlink 후 재조회, 태그 조회/ID/range/direction/repeats 수정 |
| Exporter/command | PNG/JPG/BMP 및 sheet 선택과 GIF 제한, fresh layer_id+revision, hidden/empty, trim/extrude, padding 0/null, overwrite 세트, JSON source indices/frameTags |
| 검증 자원 | 신규 도구 8개 예제, 선택 export 예제, revision을 실제 응답에서 전달하는 레시피 3개. 전체 90예제·11레시피 |

[편집 계약](MCP_STRUCTURE_EDITING.md)과 [export 지원표](MCP_EXPORT_OPTIONS.md)를 entrypoint 및
commands에서 연결했습니다. 새 ID는 영구 UUID가 아니며 mutation 뒤 재조회해야 합니다.
warning은 성공 효과 보고이며 추가 동의 요청이나 자동 retry의 근거가 아닙니다. 공유 속성을
변경하는 요청의 영향 집합에 대한 명시적 권한은 mutation 전에 확인합니다.

visible native background는 canvas trim을 유지합니다. 단일 palette indexed background의
texture RGB/RGBA 전환과 source indexed bytes 보존을 구분합니다. 일반 오류의 texture+JSON
rollback은 포함되지만 crash 원자성·정확한 indexed PNG 유지 옵션·크기 예산 정밀화·slice는
서버 후속입니다. 이번 플러그인에서 구현됐다고 표시하지 않습니다.

## 실행 환경과 결과

macOS arm64, 실제 Aseprite 1.3.18.2-arm64/API 41, Go 1.25.0, Python 3.14,
jsonschema 4.25.1/Pillow 13.0.0. user binary override를 제거하고 전용 config/temp/snapshot store를
사용했습니다. timeout=30초와 history 기본 false를 유지했습니다. 필요 시 각 기존 테스트의
전용 history fixture만 true를 사용하며 사용자 설정을 변경하지 않습니다.

| 검사 | 결과·증거 |
|---|---|
| 5-target build + 반복 host build | pin/checksum/형식/권한 일치; `test-outputs/top4/{build.log,rebuild-host.log}` |
| 기본 plugin suite | 7/7 그룹, 실제 bundled initialize/list·64 schema·90예제·11레시피·19 negative 계약 회귀·wrapper/client·checksum |
| 전체 MCP behavior sweep | 64개 도구의 119/119 시나리오, 431회 호출; `behavior-final/run-d6a7b705` |
| 스킬 workflow | 11/11, nested/revision·unlink/tag·selected sheet 포함. native PNG 픽셀·timing/JSON 검사 |
| Top4 실증 | 92회 요청: 성공 70, 예상 tool 거부 21, SDK RPC 거부 1. 92개 고유 request ID, 10개 검증 묶음; `workflow/run-669e230e` |
| 기존 live smoke | 실제 37회, source/pixel/link/timing/PNG/GIF/sheet 회귀 통과 |
| 오류/추적 | timing on/off, 실제 request ID 18개, Lua/SDK/unknown 오류 및 redaction 통과 |
| 안전 기능 | 실제 69회(예상 거부 9), preview/source stat·snapshot·history/undo 거부 및 원본 보존 통과 |
| 기존 export/analysis | PNG/BMP/JPG 시퀀스·alias/보호 출력·PNG/JPEG/GIF/BMP/native 참조 입력 전체 재검사 통과 |
| 경고 | 성공 경고 23조건·실제 실패 3건, text/structured 일치 통과 |
| pinned upstream 집중 검사 | 세 패키지 -race/-tags=integration, test/subtest 93 PASS, fail/skip 0 |
| 격리 Codex CLI | 0.163.0, 실제 설치 cache 4개 스킬·64개 정확한 schema·binary/pin·12 MCP 호출·재시작·cache 경계 통과. 앱/개인 설치 변경 없음 |
| Linux amd64 Docker smoke | bundled binary health/API 41, 64 schema와 nested group 이동/드로잉·선택 export의 실제 PNG 픽셀·JSON 통과 |
| 정적 검사 | Python compile, 변경 Markdown 링크/앵커, README 한/영 실행 예제 일치, 4개 skill quick_validate, diff 공백 검사 통과 |

Top4 workflow는 MCP 생성→group/move/nested draw→구조/revision→공유 속성/거부→unlink/재조회→
태그 수정/재정렬→선택 이미지·sheet를 실행했습니다. 별도 batch로 재열어 이미지 bytes/공유,
cel·layer·sprite metadata와 palette를 검사하고 Pillow로 실제 출력 픽셀/크기를 대조했습니다.
source bytes/inode/mtime/mode는 읽기·export·실패에서 유지됐습니다. JSON bounds/sourceSize/
source_frame_number/duration, control-character 이름 및 output-relative frameTags를 확인했고,
태그 방향이 실제 frame 색/순서를 반복·역전하지 않는 것도 검사했습니다.

padding의 null fallback과 명시적 0, empty page/tag/selection, 독립 cel 중복 unlink, no-op,
locked ancestor와 unlock-only, 숨김 대상·조상, 중복 draw/tag, stale token, SDK 필수입력,
include_json=false의 sidecar overwrite 보호를 포함합니다. 실패 export 뒤에는 output directory
항목과 내용이 유지되는지도 검사합니다. 성공 flag나 개수만으로 판정하지 않았습니다.

upstream 집중 명령 (정확한 pin의 archive 디렉터리):

```bash
GOMAXPROCS=2 PIXEL_MCP_CONFIG=/absolute/isolated/config.json go test -p 1 -parallel 1 -count=1 -race -tags=integration ./pkg/aseprite ./pkg/tools ./pkg/server -run 'TestOutputFiles|TestOutputRollback|TestFileProtectionSheet|TestExportOptions|TestExportSequence|TestExportSpritesheet|TestToolDiagnostics|TestSnapshotToolsRegistered' -json
```

실제 filesystem commit/rollback 실패 주입과 cancel/timeout 우선 recovery 정보를 검사했습니다.
이는 번들 Aseprite export 중 실제 저장장치 장애를 end-to-end로 유발했다는 주장이 아닙니다.
TestExportOptionsRangePathsProperties와 NativeJSONControlProperties는 각각 deterministic
1000개 입력을 실행했습니다. 전체 Go/unit/integration suite를 새로 완료했다고 표현하지 않습니다.

Linux smoke는 기존 `pixel-mcp-ci:latest`의 실제 Aseprite 1.3.18.3-dev를 사용했습니다.
Apple Silicon 호스트에서 linux/amd64 emulation이며 물리 x86_64 native 검증과 구분합니다.
소스 mount는 read-only, config·output은 전용 경로였습니다. 다른 container/워크트리는 수정하지 않았습니다.

## 초기 실패와 수정·재실행

- 기본 PATH에 Go가 없어 첫 build 시도가 실패했습니다. 기존 Go 1.25.0 실행 파일을 명시해
  pinned archive를 다시 빌드했고 버전/전역 PATH를 변경하지 않았습니다.
- 병렬로 시작한 최초 recipe의 sheet timing 요청이 timeout으로 실패했습니다. 순차 실행에서
  같은 timeout으로 전체 레시피를 통과했습니다. 병렬도가 원인이라고 확정하지 않습니다.
- 순차 legacy export/analysis에서도 analyze_reference timeout 1건이 있었습니다. 실패 로그와
  request ID를 보존했고 같은 timeout 30초의 전체 재실행은 통과했습니다. 원인은 미확정입니다.
  실패 case를 빼거나 timeout을 늘리지 않았습니다.
- 새 Python helper의 name 인자와 새 도구 name 속성 충돌, 검사 Lua의 palette 컬렉션 반복,
  legacy link/get_pixels의 root lookup을 잘못 가정한 초기 fixture를 수정했습니다. 모델/스킬에는
  nested draw의 지원을 다른 도구에 소급하지 않는 지침과 root에서 link 후 이동하는 실제 경로를 반영했습니다.
- 초기 실패의 calls/summary와 최초 timeout 로그는 ignored evidence에 남깁니다. Pillow의 getdata
  deprecation warning은 현재 버전에서 실패가 아니며 실제 데이터 비교를 생략하지 않았습니다.

## 셀프리뷰

convergent-code-review backend lens, plugin base부터 49파일 범위(5 generated binaries,
source/build/schema snapshots, 관련 스킬/commands/문서/테스트)를 검토했습니다.
주변 문맥은 build/wrapper/client/기존 inspector 및 pinned 서버의 structure/cel/layer/tag/export
계약·핸들러와 output rollback/diagnostics 경계입니다. 다른 서버 기능 구현이나 전역 설정은 제외합니다.

| ID | 우선순위·상태 | 원인·수정·검증 |
|---|---|---|
| SHARED-P2-001 | P2 VERIFIED | 새 JSON 객체 직렬화 순서를 시간/프레임 순서로 가정하던 검사를 source_frame_number 순서로 정렬하도록 수정. Top4·recipe·Codex 직접 소비자를 대조하고 실제 파일/시간 검사 재실행 |
| SHARED-P2-002 | P2 VERIFIED | 오류 코드/원본 보존만으로 실패 export의 잔여 파일을 놓칠 수 있어 출력 directory 항목/내용 hash 불변 검사를 추가. 실제 거부 21건 및 SDK 오류를 포함한 92요청 workflow 통과 |
| SHARED-P2-003 | P2 VERIFIED | 보호 문구 갱신 중 비협력 writer도 output set과 함께 보호된다는 과도한 표현을 분리. 현재 외부 writer/ABA/final-check race와 crash 한계를 지원표·기존 분석 문서·server 계약에 대조 |

초기 discovery 1, bounded repair cycle 1, repair-diff 1, closure 1, fresh 전체 범위 1,
총 review pass 4. 초기 P2 3→최종 0, P0/P1 0, 신규/repair 유발/재개방/accepted/out-of-scope/
미해결 finding 0. JSON 순서 가정의 직접 소비자 전파를 보강하며 후보 snapshot을 1회 갱신했습니다.
최종 후보는 `test-outputs/top4/final-candidate.json`의 48개 SHA-256과 base commit으로 식별하며,
이 reporting-only 문서만 hash에서 제외했습니다. 최종 후보 선택 뒤 runtime/test/계약의 추가 변경은
없으며 최종 검증 후 hash 일치를 확인합니다. 전체 시간은 별도로 측정하지 않았습니다.

차단 위험(P0/P1)은 전 단계 0이며 세 검증/계약 공백을 해결한 뒤 추가 mutation을 중단했습니다.
셀프리뷰이며 독립 외부 리뷰나 병합 승인을 대신하지 않습니다.

## Notes

1. macOS amd64/Linux arm64/Windows amd64는 cross-build·format·checksum만 확인했습니다.
   macOS ARM 전체/race·모든 mode/format/layer/blend 조합·물리 Linux x86_64·최소 지원 버전
   전체 재실행은 미검증입니다. 이번 archive의 focused race와 bundle workflow 결과와 구분합니다.
2. 위 두 native timeout은 같은 설정 재실행에서 통과했지만 최초 원인은 미확정입니다. 재발 시
   보존한 request ID/오류 본문과 환경을 확인해야 합니다. timeout guard를 낮추거나 우회하지 않았습니다.
3. 앱 UI·개인 설치본 교체·명시적 설치 lifecycle·새 모델의 전체 skill 선택은 실행하지 않았습니다.
   이전 설치 검증 이력은 보존하며 이번 isolated CLI 계약 검증으로 대체하지 않습니다.
4. 일반 오류 rollback과 파일 순번/recovery 정보는 검증했으나 실제 디스크 장애·crash 원자성,
   정확한 indexed PNG 유지 옵션·size budget 정밀화·slice 기능을 이번 완료로 표현하지 않습니다.

판정: **PASS_WITH_NOTES** (최종 후보의 필수 검사·closure·fresh 리뷰 완료 기준).
미병합 task branch/worktree와 ignored evidence를 유지합니다. develop/main 병합·release·공개 게시,
개인 설치 갱신은 이 작업에 포함하지 않습니다.

최종 후보의 레시피 전체는 `recipes-certified`에서 11/11, 순서 소비자 보강 후 Codex 검사는
`codex-certified/run-472597e45e`에서 PASS, 기본 suite는 `plugin-certified.log`에서 7/7입니다.
최종 48개 hash 및 보호 설정의 일치를 확인했고 요약은 `test-outputs/top4/final-results.json`에
보존했습니다. 이 보고 문장 외의 코드/계약 변경은 없습니다.
