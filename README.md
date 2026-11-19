# Johndurux/news-image-20261119

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Johndurux/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Johndurux/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

One image that sums up Thursday 19 November 2026: a single editorial front
page with the date across the top, the Shenzhen summit as the lead story, four
more stories from four other regions under it, and a three-line strip at the
foot. The program writes it to `/output/entry.png` with no network, no image
service and no third-party artwork — the page was drawn from shapes and type
by `design/make_page.py` while the entry was built, and `main.py` puts those
exact bytes in place, so two runs write one file byte for byte.

## Run it

```sh
python3 main.py
```

`main.py` reads `entry.png` beside it, checks the file's size and that it is a
whole PNG, and copies it to `/output/entry.png`. To redraw the page instead,
run `python3 design/make_page.py` with Pillow installed — it needs the
Liberation and DejaVu fonts and writes `entry.png` in the directory it is run
from.

---

<sub>Entered on [make.fun](https://make.fun/?ref=1w5j0ma7&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
