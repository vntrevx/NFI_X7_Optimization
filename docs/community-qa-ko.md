# TestX7 커뮤니티 Q&A

Discord나 커뮤니티에서 자주 나오는 질문에 짧게 답하기 위한 한국어 문서입니다.

가장 중요한 원칙은 과장하지 않는 것입니다. `TestX7`는 로컬 성능 proof package이며, 공식 NFI 기능도 아니고 production 추천도 아닙니다.

## 짧은 현재 상태

```text
TestX7는 로컬 성능 proof package입니다.

NFI X7의 live-style analyze(pairs) 경로를 빠르게 만드는 것이 목표입니다.
진입, 청산, DCA, grind, 레버리지, 포지션 로직은 의도적으로 바꾸지 않았습니다.

공식 기능이 아니고, production-ready도 아니고, 수익률 개선 주장도 아닙니다.
```

## live trading에 적용할 수 있나요?

짧은 답:

```text
원칙적으로는 가능합니다.

이 최적화는 live/dry-run 분석 흐름에 들어가는 live-style analyze(pairs) 경로를 대상으로 합니다.

하지만 현재 상태를 production drop-in이라고 부르지는 않겠습니다.
maintainer review, dry-run/live 관찰, worker limit 설정, 다음 NFI 버전 기준 테스트가 더 필요합니다.
```

더 조심스러운 답:

```text
아이디어 자체는 live 분석 경로를 위한 것이 맞습니다.

하지만 현재 repo는 아직 proof package입니다.
지금까지 검증한 것은 로컬 live-style loop benchmark와 backtest parity check입니다.
장기 실전 live trading 검증은 아닙니다.

실제 live를 고려하기 전에 dry-run 테스트가 먼저입니다.
```

## live나 dry-run에서 테스트해봤나요?

```text
제 쪽에서는 아직 장기 live/dry-run 테스트를 하지 않았습니다.

현재까지 테스트한 것:
- 로컬 live-style analyze(pairs) loop
- 원본 X7과 로컬 backtest parity 비교
- 로컬 80페어 speed gate

커뮤니티 유저 한 명이 로컬 backtest를 테스트했고, 결과는 같으면서 실행 시간이 더 빨랐다고 공유했습니다.

하지만 저는 아직 TestX7를 실제 live trading이나 장기 dry-run으로 직접 돌리지는 않았습니다.
지금은 proof package로 보는 것이 맞습니다.
```

## 매매 로직이 바뀌나요?

```text
의도적인 매매 로직 변경은 없습니다.

entry, exit, DCA, grind, leverage, position adjustment, signal tag는 그대로 유지하는 것이 목표입니다.

검증한 1년 backtest trade surface는 원본 X7과 같았습니다.
trade_surface_equal=true
first_difference=null
```

쉽게 말하면:

```text
신호를 바꿔서 더 벌게 만드는 작업이 아닙니다.
검증된 같은 판단을 훨씬 빠르게 계산하게 만드는 작업입니다.
```

## 로컬 속도 결과는 어땠나요?

```text
로컬 80페어 live-style analyze loop:

원본 X7:
- 평균 238.833499s
- 최대 242.990876s

TestX7:
- 평균 3.340671s
- 최대 4.221486s
- 40/40 loop가 5초 안에 끝남

평균 기준 약 71.5x 빨라졌습니다.
```

## backtest도 빨라지나요?

조심스러운 답:

```text
가장 강하게 검증된 것은 아직 live-style analyze(pairs) 경로입니다.

다만 커뮤니티 유저가 공유한 외부 backtest 사례가 하나 있습니다.

원본 X7: 214s
TestX7: 137s
약 36% faster
결과 surface matched

이건 좋은 신호지만, 모든 backtest에서 빨라진다고 일반화하기에는 아직 부족합니다.
backtest speed는 별도 controlled profiling이 필요합니다.
```

## workers / threads는 몇 개를 써야 하나요?

```text
머신마다 다릅니다.

workers를 너무 많이 쓰면 오히려 느려질 수 있습니다.
특히 작은 VPS에서는 CPU/RAM 압박이 생길 수 있습니다.

장기적으로는 사용자가 설정할 수 있어야 합니다.
- auto = CPU 기준 보수적 선택
- 1 = sequential / disabled
- N = 사용자가 직접 지정한 worker limit
```

로컬 proof 결과:

```text
최종 로컬 테스트 머신에서는 Docker가 10 CPU를 볼 수 있었습니다.
9 workers가 5초 gate를 통과했습니다.
10 workers와 8 workers는 테스트에서 max-loop spike가 더 나빴습니다.

그렇다고 모든 머신에서 9가 정답이라는 뜻은 아닙니다.
```

## market data fetch timeout을 고친 건가요?

```text
아니요. 직접적으로 고친 것은 아닙니다.

exchange/network fetch timeout 자체를 고친 것이 아닙니다.

이 작업은 CPU-bound strategy analysis 지연을 줄이는 쪽입니다.
fresh candle 이후 pair analysis가 너무 오래 걸려서 봇이 밀리는 상황이라면,
더 많은 CPU core 활용과 반복 계산 cache로 Strategy analysis took ... 지연을 줄일 수 있습니다.
```

## 작은 VPS에서도 쓸 수 있나요?

```text
가능할 수도 있지만, 조심해야 합니다.

작은 VPS는 worker limit을 보수적으로 잡아야 합니다.
CPU/RAM 여유가 없는데 workers를 너무 많이 열면 오히려 더 나빠질 수 있습니다.

그래서 실제 사용자 기능으로 만들려면 worker/thread limit 설정이 꼭 필요합니다.
```

## 테스트한 사람이 무엇을 공유하면 좋나요?

`TestX7`를 테스트했다면 아래 정보를 공유하면 좋습니다.

```text
- machine / CPU / RAM
- Docker CPU limit 또는 Docker에서 보이는 CPU 수
- OS / Docker 환경
- exchange와 trading mode
- spot 또는 futures
- pairlist와 실제 사용된 effective pair count
- timerange
- 정확한 command
- worker settings / env vars
- 원본 X7 runtime
- TestX7 runtime
- result surface가 matched인지 여부
- 가능하면 exported backtest summary
```

## 안전한 테스트 순서

```text
1. 두 전략이 모두 로딩되는지 확인
2. 짧은 backtest 비교
3. trade-surface parity 확인
4. 더 긴 backtest 비교
5. dry-run 관찰
6. maintainer review와 추가 hardening 전에는 real live testing을 신중하게 판단
```

## 자주 나오는 질문

### TestX7는 live-ready인가요?

```text
아직 live-ready가 아닙니다.

이건 로컬 proof package입니다.
최적화 대상은 live-style analysis path지만,
production-ready라고 보기 전에는 maintainer review, dry-run testing, worker limit, 추가 검증이 필요합니다.
```

### TestX7를 써도 되나요?

```text
아직 production replacement로 추천하지는 않습니다.

테스트하고 싶다면 backtesting이나 dry-run부터 시작하고,
원본 X7과 비교해서 trade surface가 같은지 확인하는 것이 좋습니다.
```

### 테스트 결과를 공유하려면 뭘 알려줘야 하나요?

```text
공유해주면 정말 도움이 됩니다.

machine, pairlist/effective pair count, timerange, command, worker settings,
원본 runtime, TestX7 runtime, result surface matched 여부를 같이 알려주면 좋습니다.
```

### CPU를 더 쓰는 건가요?

```text
네. 분석 병목을 줄이기 위해 가능한 CPU core를 더 활용하는 방향입니다.

pair analysis가 대부분 한 core에 묶여 오래 걸리는 상황을 줄이는 것이 목표입니다.
다만 작은 VPS에서는 workers를 너무 많이 쓰면 더 나빠질 수 있으므로 worker count는 설정 가능해야 합니다.
```

## 결론

```text
유망한 proof package입니다.
공식 기능은 아닙니다.
production-ready는 아닙니다.
수익률 개선 주장이 아닙니다.
추가 테스트, dry-run 관찰, maintainer review, upstream용 작은 단위 분리가 필요합니다.
```
