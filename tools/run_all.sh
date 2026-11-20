#!/usr/bin/env bash
# 一鍵跑全部檢查：Wiki → 數字 → 簡報內容 → 簡報版面
cd "$(dirname "$0")/.." || exit 1
status=0
python3 tools/check_wiki.py        || status=1
echo
python3 tools/verify_numbers.py    || status=1
echo
python3 tools/check_slides.py      || status=1
echo
if python3 -c "import playwright" 2>/dev/null; then
  python3 tools/screenshot_slides.py --shots checks/screens || status=1
else
  echo "（沒有安裝 playwright，略過版面檢查：pip install playwright && playwright install chromium）"
fi
echo
[ $status -eq 0 ] && echo "全部檢查：PASS" || echo "全部檢查：有錯誤"
exit $status
