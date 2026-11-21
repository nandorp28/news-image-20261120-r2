# news-image-20261120-r2

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/nandorp28/news-image-20261120-r2/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/nandorp28/news-image-20261120-r2/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

Round 2 entry for make.fun's "Sum up 20 November's world news in one image"
bounty: a dense data broadsheet — 48 sourced stories across 7 regions, a
key-figures strip, a region bar, four feature cards, a 12-card grid, a
dot-grid world map with pins, and a date check — drawn by a pure-stdlib
Python program (no network, no fonts on disk: text uses a 5x7 bitmap font
defined in the code).

Lead stories: Russian missiles crash in Poland; GTA VI's record $3.79bn
day one; Wall Street slides into correction; COP31 deadlocks on fossil
fuels. Every story happened or was first reported on Friday 20 November
2026, with its source named.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024, deterministic across runs). Validate only
with `python3 main.py --check`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=qyk2abaw&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
