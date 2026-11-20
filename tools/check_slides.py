#!/usr/bin/env python3
"""Check slides/index.html against the Wiki.

  D1 內容頁要有 data-wiki，而且指到的 Wiki 頁存在
  D2 內容頁底部要有來源（Sxx），而且來源卡存在
  D3 投影片上的數字必須出現在 data-wiki 指到的 Wiki 頁裡（簡報不能自己生數字）
  D4 不可出現投資建議語氣
  D5 專有名詞第一次出現的那一張，要用 <dfn> 解釋
  D6 每張正文不超過 slide_max_chars 字
  D7 結尾頁（data-type="end"）要有「不構成投資建議」

不檢查 D1–D3、D5 的頁型：title（封面）、agenda（目錄）、refs（來源清單）、appendix（附錄）。

Usage: python3 tools/check_slides.py [--out checks/xxx.txt]
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = json.loads((ROOT / "tools" / "rules.json").read_text(encoding="utf-8"))
WIKI = ROOT / "wiki"
SKIP_TYPES = {"title", "agenda", "refs", "appendix"}
VOID = {"br", "img", "meta", "input", "hr", "link", "source"}


class SlideParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides, self.stack, self.cur = [], [], None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = set((a.get("class") or "").split())
        if tag == "section" and "slide" in classes:
            self.cur = {"attrs": a, "text": [], "src": [], "dfn": [], "depth": len(self.stack)}
            self.slides.append(self.cur)
        if tag not in VOID:
            self.stack.append((tag, classes))

    def handle_startendtag(self, tag, attrs):
        pass  # self-closing SVG shapes carry no text

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
        if tag == "section" and self.cur is not None and len(self.stack) <= self.cur["depth"]:
            self.cur = None

    def handle_data(self, data):
        if self.cur is None or not data.strip():
            return
        tags = [t for t, _ in self.stack]
        classes = set().union(*[c for _, c in self.stack]) if self.stack else set()
        if {"script", "style"} & set(tags) or ("svg" in tags and "title" in tags):
            return
        if "notes" in classes:
            return
        if "src" in classes:
            self.cur["src"].append(data)
            return
        self.cur["text"].append(data)
        if "dfn" in tags:
            self.cur["dfn"].append(data)


def norm(s):
    return re.sub(r"\s+", "", s).replace("+", "").replace("−", "-").replace("％", "%")


def main():
    html = (ROOT / "slides" / "index.html").read_text(encoding="utf-8")
    p = SlideParser()
    p.feed(html)
    source_ids = {f.stem for f in (WIKI / "sources").glob("S*.md")}
    num_re = re.compile(r"-?\d[\d,\.]*(%|萬元|元|檔|億|兆|萬|個百分點)")
    advice_res = [re.compile(a) for a in RULES["advice_patterns"]]
    errors, seen_terms, has_end_disclaimer = [], set(), False

    for i, s in enumerate(p.slides, 1):
        t = s["attrs"].get("data-type", "content")
        text = "".join(s["text"])
        src = "".join(s["src"])
        dfn = "".join(s["dfn"])
        title = s["attrs"].get("data-title", f"#{i}")
        tag = f"第 {i:02d} 張〈{title}〉"

        # D1
        wiki_paths = [w.strip() for w in s["attrs"].get("data-wiki", "").split(",") if w.strip()]
        if t not in SKIP_TYPES and t != "end" and not wiki_paths:
            errors.append(f"D1 {tag}: 沒有 data-wiki")
        wiki_text = ""
        for w in wiki_paths:
            f = WIKI / w
            if not f.exists():
                errors.append(f"D1 {tag}: data-wiki 指到不存在的頁 {w}")
            else:
                wiki_text += f.read_text(encoding="utf-8")
        # D2
        if t not in SKIP_TYPES and t != "end":
            cites = re.findall(r"S\d{2}", src)
            if not cites:
                errors.append(f"D2 {tag}: 沒有來源標記")
            for c in cites:
                if c not in source_ids:
                    errors.append(f"D2 {tag}: 來源 {c} 不存在")
        # D3
        if wiki_paths:
            wn = norm(wiki_text)
            for m in num_re.finditer(norm(text)):
                tok = m.group(0)
                if not re.search(r"(?<![\d.])" + re.escape(tok), wn):
                    errors.append(f"D3 {tag}: 數字「{tok}」不在對應 Wiki 頁（{', '.join(wiki_paths)}）")
        # D4
        for a in advice_res:
            if a.search(text):
                errors.append(f"D4 {tag}: 投資建議語氣（{a.pattern}）")
        # D5
        if t not in SKIP_TYPES:
            for term in RULES["glossary"]:
                if term in seen_terms or term not in text:
                    continue
                seen_terms.add(term)
                if term not in dfn:
                    errors.append(f"D5 {tag}: 「{term}」第一次出現，但這張沒有用 <dfn> 解釋")
        # D6
        n = len(re.sub(r"\s+", "", text))
        if t not in {"refs", "appendix"} and n > RULES["slide_max_chars"]:
            errors.append(f"D6 {tag}: 正文 {n} 字，超過 {RULES['slide_max_chars']} 字")
        # D7
        if t == "end" and "不構成投資建議" in text:
            has_end_disclaimer = True

    if not has_end_disclaimer:
        errors.append("D7 結尾頁沒有「不構成投資建議」")

    report = [
        "check_slides.py",
        f"投影片 {len(p.slides)} 張｜專有名詞 {len(RULES['glossary'])} 個（出現 {len(seen_terms)} 個）",
        f"錯誤 {len(errors)} 個",
    ] + [f"  - {e}" for e in errors]
    report.append("結果：PASS" if not errors else "結果：FAIL")
    out = "\n".join(report)
    print(out)
    if "--out" in sys.argv:
        Path(sys.argv[sys.argv.index("--out") + 1]).write_text(out + "\n", encoding="utf-8")
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
