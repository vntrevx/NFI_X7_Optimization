# 직접 설치 가이드

이 패키지는 두 층으로 나뉩니다.

- `configs/`, `docs/`는 검토용 자료입니다.
- `release/testx7-v174109-rescue-short641-install-20260523.tar.gz`가 실제
  설치용 번들입니다.

검증된 `TestX7` v17.4.109 패키지를 Freqtrade userdir에 넣고 싶으면 release
bundle을 사용하세요. 이 repo 루트의 `user_data/strategies`를 그대로 쓰면
안 됩니다. 설치용 v17.4.109 전략 파일은 release bundle 안에 있습니다.

## 가장 쉬운 설치 방법

아래처럼 설치 스크립트를 받은 뒤, 본인 Freqtrade 폴더만 넘기면 됩니다.

```bash
cd /tmp
curl -L -O \
  https://raw.githubusercontent.com/vntrevx/NFI_X7_Optimization/main/tuning/x7-v174109-rescue-short641/release/install-testx7-v174109.sh
chmod +x install-testx7-v174109.sh
./install-testx7-v174109.sh /path/to/freqtrade
```

`/path/to/freqtrade`는 본인 Freqtrade checkout 경로로 바꾸세요. 예를 들면:

```bash
./install-testx7-v174109.sh ~/freqtrade
```

스크립트가 하는 일은 네 가지입니다.

- 공개 설치 번들 다운로드
- sha256 자동 확인
- 임시 폴더에 압축 해제
- `user_data` 파일을 Freqtrade checkout으로 복사

기존 파일이 덮어써질 경우 `user_data/testx7-v174109-backup-*` 아래에
백업됩니다.

## 번들 포함 파일

번들은 `user_data` 전략/설정 파일만 포함합니다.

- `user_data/strategies/NostalgiaForInfinityX7.py`
- `user_data/strategies/TestX7.py`
- `user_data/strategies/test_x7_modules/*`
- `user_data/config-x7-futures3x-80pairs.example.json`
- 선택된 후보 config
- speed-safe config
- paper overlay config

거래소 credential, live bot 상태, DB, backtest archive는 포함하지 않습니다.

## 수동 설치 방법

스크립트를 쓰기 싫다면 아래처럼 수동으로 설치해도 됩니다. 먼저 live bot이
아니라 깨끗한 테스트용 Freqtrade checkout에서 실행하세요.

```bash
curl -L \
  -o testx7-v174109-rescue-short641-install-20260523.tar.gz \
  https://raw.githubusercontent.com/vntrevx/NFI_X7_Optimization/main/tuning/x7-v174109-rescue-short641/release/testx7-v174109-rescue-short641-install-20260523.tar.gz

sha256sum testx7-v174109-rescue-short641-install-20260523.tar.gz
```

예상 sha256:

```text
c8803508f146254e1f553015f9ab37b20858004c120a8e6b749203c54382418a
```

참고: `evidence/local-status.json`의 `bundle_sha256`은 로컬 검증 때 사용한
내부 transfer bundle 기준입니다. 공개 설치용 번들은 내부 handoff 문서를
제거한 sanitized bundle이라 위의 다른 sha256을 사용합니다.

압축을 풀기 전에 파일 목록을 먼저 확인하세요.

```bash
tar -tzf testx7-v174109-rescue-short641-install-20260523.tar.gz
```

임시 폴더에 먼저 풉니다.

```bash
mkdir -p /tmp/testx7-v174109-install-preview
tar -xzf testx7-v174109-rescue-short641-install-20260523.tar.gz \
  -C /tmp/testx7-v174109-install-preview
```

확인한 뒤 Freqtrade checkout으로 복사합니다.

```bash
rsync -av /tmp/testx7-v174109-install-preview/user_data/ /path/to/freqtrade/user_data/
```

`/path/to/freqtrade`는 본인 Freqtrade 경로로 바꾸면 됩니다.

## 로드 확인

Freqtrade checkout에서 로컬 Docker 로드 체크를 실행하세요.

```bash
CANDIDATE="$(basename "$(ls user_data/config-x7-futures3x-prodage-v2-risk-topmode-*.example.json | head -n 1)")"

docker compose run --rm freqtrade list-strategies \
  --userdir /freqtrade/user_data \
  --config /freqtrade/user_data/config-x7-futures3x-80pairs.example.json \
  --config "/freqtrade/user_data/$CANDIDATE" \
  --config /freqtrade/user_data/config-test-x7-live-speed-safe.example.json \
  --config /freqtrade/user_data/config-x7-v174109-rescue-short641-paper-overlay.example.json
```

`TestX7`가 로드되어야 합니다. 기대 기준은 다음입니다.

```text
Test X7 based on v17.4.109
```

## 처음은 paper 모드

포함된 overlay는 paper/tiny-canary용입니다.

- `dry_run=true`
- `dry_run_wallet=1000`
- `stake_amount=100`
- `max_open_trades=4`
- `trading_mode=futures`
- `margin_mode=isolated`
- `force_entry_enable=false`

본인 검토, 별도 private credential config, fresh paper run 없이 live config에
바로 섞지 마세요.
