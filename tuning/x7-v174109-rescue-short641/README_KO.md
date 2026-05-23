# TestX7 v17.4.109 Rescue Short641 튜닝 패키지

이 폴더는 `NostalgiaForInfinityX7` `v17.4.109` 기반으로 진행한
로컬 TestX7 튜닝 연구 패키지입니다.

원본 전략을 대체하자는 PR이 아니고, 실전 수익 보장도 아닙니다. 목적은
후보 선정, 로컬 검증 근거, 속도 게이트, 남은 리스크를 리뷰 가능한 형태로
정리해 두는 것입니다.

## 결론

- 최종 로컬 후보: `rescue-short641-paramkeys-v1`
- 기준 버전: `NostalgiaForInfinityX7` `v17.4.109`
- 상태: 로컬 검증 완료, 라이브 미적용
- 다음 단계: paper 또는 tiny-canary 관찰
- full-capital live 승인: 아님

## 핵심 결과

| 항목 | 결과 |
| --- | --- |
| Production gate | `promotable=true`, `risk_level=low`, `failed_rules=[]` |
| Full timerange | `+191.866939%`, `269` trades |
| Fresh OOS | `+25.906538%`, `54` trades |
| No-top3 retention | `83.151154%` |
| Default live-cost retention | `82.441272%` |
| 80-pair speed gate | `PASS`, max loop `3.882162s`, over-5s loops `0` |
| Targeted verifier tests | `258`, `OK` |
| Local Docker full unittest discovery | `337`, `OK` |

## 중요한 경계

이 패키지는 upstream X7 `v17.4.109` 기반입니다. 다만 로컬 기준 파일은
upstream과 완전히 byte-identical 하지는 않았습니다.

확인된 차이는 `short_entry_condition_641_enable`과
`short_entry_condition_642_enable` 기본값 처리입니다. upstream은 해당 예시
라인이 주석 처리되어 있고, 로컬 기준 파일은 두 값을 `False`로 명시했습니다.

자세한 내용은 `docs/upstream-baseline-note.md`에 정리했습니다.

## 포함 내용

- `INSTALL.md` - 직접 설치 가이드
- `INSTALL_KO.md` - 한국어 직접 설치 가이드
- `configs/candidate-config.example.json` - 선택된 후보 config
- `configs/paper-overlay.example.json` - paper/tiny-canary overlay
- `docs/final-report.md` - 공개용 최종 요약
- `docs/risk-audit.md` - 남은 리스크 요약
- `docs/effectiveness-retrospective.md` - 이번 작업의 효과 정리
- `docs/upstream-baseline-note.md` - upstream 버전 및 로컬 차이
- `evidence/local-status.json` - 로컬 상태 JSON 스냅샷
- `release/install-testx7-v174109.sh` - 로컬 Freqtrade checkout에 설치하는
  가장 쉬운 installer
- `release/testx7-v174109-rescue-short641-install-20260523.tar.gz` - 검증된
  v17.4.109 전략/설정 파일만 담은 sanitized 설치 번들
