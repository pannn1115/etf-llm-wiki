#!/usr/bin/env python3
"""Render every slide in headless Chrome, save screenshots, and report layout problems.

  V1 有沒有內容超出 1280×720 的投影片範圍（被切掉）
  V2 有沒有內容壓到底部的來源列
  V3 瀏覽器 console 有沒有錯誤
  V4 底部控制列有沒有蓋住投影片（第 1 輪靠肉眼看截圖才發現，之後加成自動檢查）

Usage: python3 tools/screenshot_slides.py [--out checks/xxx.txt] [--shots checks/screens]
需要：pip install playwright（並有 Chrome/Chromium）
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "slides" / "index.html"

JS_CHECK = """
() => {
  const s = document.querySelector('.slide.active');
  const box = s.getBoundingClientRect();
  const scale = box.width / 1280;
  const src = s.querySelector('.src');
  const srcTop = src ? src.getBoundingClientRect().top : box.bottom;
  const issues = [];
  for (const el of s.querySelectorAll('*')) {
    if (el.closest('.notes') || el.closest('.src') || el.closest('svg') && el.tagName !== 'svg') continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    const label = el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ')[0] : '');
    const txt = (el.innerText || '').trim().slice(0, 18);
    if (r.right > box.right + 1 || r.bottom > box.bottom + 1)
      issues.push(`V1 超出投影片：${label}「${txt}」`);
    else if (src && r.bottom > srcTop + 1 && !el.contains(src))
      issues.push(`V2 壓到來源列：${label}「${txt}」(底部 ${Math.round((r.bottom - srcTop) / scale)}px)`);
    if (el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflowX === 'hidden')
      issues.push(`V1 文字被裁切：${label}「${txt}」`);
  }
  const ui = document.querySelector('.ui');
  if (ui && ui.getBoundingClientRect().top < box.bottom - 1)
    issues.push(`V4 底部控制列蓋住投影片 ${Math.round(box.bottom - ui.getBoundingClientRect().top)}px`);
  return [...new Set(issues)];
}
"""


def main():
    out_path = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    shots = Path(sys.argv[sys.argv.index("--shots") + 1]) if "--shots" in sys.argv else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    lines, total = ["screenshot_slides.py（headless Chrome，視窗 1280×760）"], 0
    with sync_playwright() as p:
        chrome = Path("/usr/bin/google-chrome")
        browser = (p.chromium.launch(executable_path=str(chrome), args=["--no-sandbox"]) if chrome.exists()
                   else p.chromium.launch())  # 其他電腦：先執行 playwright install chromium
        page = browser.new_page(viewport={"width": 1280, "height": 760})
        console_errors = []
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: console_errors.append(str(e)))
        page.goto(HTML.as_uri())
        n = page.evaluate("document.querySelectorAll('.slide').length")
        for k in range(1, n + 1):
            page.evaluate(f"location.hash = '#{k}'")
            page.wait_for_timeout(150)
            page.evaluate("document.querySelector('.stage').scrollTop = 0")
            title = page.evaluate("document.querySelector('.slide.active').dataset.title")
            issues = page.evaluate(JS_CHECK)
            if shots:
                # 不用 locator.screenshot()：它會自動捲動元素進畫面，把版面問題「修掉」，造成後面的頁誤判（第 3 輪發現）
                clip = page.evaluate("(() => { const r = document.getElementById('deck').getBoundingClientRect(); return {x: r.x, y: r.y, width: r.width, height: r.height}; })()")
                page.screenshot(path=str(shots / f"slide-{k:02d}.png"), clip=clip)
            total += len(issues)
            lines.append(f"第 {k:02d} 張〈{title}〉：" + ("OK" if not issues else f"{len(issues)} 個問題"))
            lines += [f"    - {x}" for x in issues]
        browser.close()
    for e in console_errors:
        lines.append(f"V3 console 錯誤：{e}")
    total += len(console_errors)
    lines.append(f"問題 {total} 個")
    lines.append("結果：PASS" if total == 0 else "結果：FAIL")
    out = "\n".join(lines)
    print(out)
    if out_path:
        Path(out_path).write_text(out + "\n", encoding="utf-8")
    sys.exit(0 if total == 0 else 1)


if __name__ == "__main__":
    main()
