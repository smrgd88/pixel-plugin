# 다음 작업 — 2026-10-18

현재 plugin develop은 [PR #16](https://github.com/smrgd88/pixel-plugin/pull/16)의
`f5228e3b7dd3096600cebd216808f7cc2829330a`입니다. 검증 후보 `4814d47`과 tree가 같습니다.
MCP runtime pin은 `99f193ad3a0eefcb8e8b71a3b9e3f69be47ac2d8`, 등록 도구는 64개로 유지합니다.
MCP 현황 문서 [PR #36](https://github.com/smrgd88/pixel-mcp/pull/36)도 develop `42bab18`에
병합됐지만 plugin runtime pin을 변경한 것은 아닙니다. manifest 0.5.0의 누적 변경은 **Unreleased**입니다.
[로드맵](ROADMAP.md) · [Top4 검증과 병합 이력](TOP4_SYNC_VALIDATION.md).

## develop 반영 완료

- 플러그인 #11 안전 기능, #12 오류/추적, #13 README/AGENTS, #14 로드맵,
  #15 Codex 설치·연결·lifecycle 및 smrgd88 publisher 표시가 develop에 병합돼 있습니다.
  [설치 검증 이력](CODEX_INSTALL_VALIDATION.md)은 당시 pin/도구 수를 유지합니다.
- 서버 #29 nested draw_pixels, #30 structure, #31 cel properties/revision,
  #33 unlink, #34 layer/group, #32 tags, #35 export options가 모두 MCP develop에 병합됐습니다.
- plugin #16은 56→64의 실제 등록 집합, 기존 draw_pixels/두 export schema 변경,
  revision freshness·linked 영향·native 파일·선택 출력/JSON 계약을 검증하고 develop에 병합됐습니다.
- background caveat는 Exporter 스킬에, 선택 export 사용 흐름은 스킬·예제·레시피에 반영됐습니다.
  태그 변경 후 재조회 지침은 Animator 스킬·예제에 반영됐으며, 실행 레시피는 조회→태그 편집까지를 다룹니다. 실제 반영 범위는 [스킬과 계약](TOP4_SYNC_VALIDATION.md#스킬과-계약)을
  따르며 모든 format/색상 모드 조합이나 앱 GUI 검증 완료를 뜻하지 않습니다.

## 현재 실행 순서

1. **다음 단계는 M2 릴리스 준비**입니다: 검증한 commit/지원 범위에 맞게 버전·CHANGELOG·배포 artifact·설치/갱신/복귀
   절차를 확정합니다. 릴리스·게시와 사용자의 설치 갱신은 별도 단계입니다.
2. M3 플랫폼 확대: 추가 OS/아키텍처의 실제 실행 증거를 확보합니다. 교차 빌드는 native 검증이 아닙니다.
3. 설치 앱 GUI 자동 검증은 기존 보류 상태를 유지합니다. 이번 작업에서 개인 설정/설치본을 교체하지 않습니다.

## 서버 잔여와 플러그인 후속

- 보이는 native background의 canvas 유지 및 일부 indexed background texture의 RGB 전환은
  현재 계약이며 [export 안내](MCP_EXPORT_OPTIONS.md)에 포함됩니다.
- 크기 예산 정밀화는 별도 MCP `feature/be-export-size-budget` 세션에서 작업 중인 후속입니다.
  현재 plugin pin에는 포함되지 않았습니다. 서버 구현·검증·병합 뒤 별도 plugin 동기화를 판단합니다.
- 별도 indexed PNG 유지 옵션, 출력 세트 crash 복구·고아 staging 정리는 MCP 후속 TODO입니다.
  일반 오류 rollback을 crash 원자성으로 표현하지 않습니다.
- slice/pivot/nine-slice, 범용 색상 모드 변환과 추가 편집 기능은 범위 선정·서버 구현 이후 동기화합니다.
- 정확한 density 비율, AA 후보 확대, palette 중복 제거와 성공 payload 일괄 표준화는 개선 후보입니다.
- 구조/태그 ID는 영구 식별자가 아니며 모든 변경 후 재조회합니다. 새 지원을 legacy 도구 전체에 소급하지 않습니다.

## 유지하는 경계

Godot 게임은 반영 제외·별도 백업 상태입니다. 원저자 MIT 고지, smrgd88 publisher, Codex/Claude
패키징과 영구 설치 경로를 보존합니다. 자동 history 기본 false와 timeout=30을 유지합니다.
실행하지 않은 OS/GUI·광범위 조합과 이전 실패는 검증 보고서에 구분합니다.
