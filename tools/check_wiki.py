#!/usr/bin/env python3
"""Lint the ETF LLM Wiki.

Checks (rules come from tools/rules.json and AGENTS.md):
  W1 每張來源卡 frontmatter 欄位齊全
  W2 概念頁必備段落齊全
  W3 「重點」「常見誤解」每一條都有 [Sxx]，而且 Sxx 存在
  W4 有統計數字的句子要有年份，或標明假設／舉例／試算
  W5 不可出現投資建議語氣
  W6 已知過期說法（outdated_patterns）不可單獨出現

Usage: python3 tools/check_wiki.py [--out checks/xxx.txt]
Exit code 0 = pass, 1 = fail.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = json.loads((ROOT / "tools" / "rules.json").read_text(encoding="utf-8"))
SRC_DIR = ROOT / "wiki" / "sources"
CONCEPT_DIR = ROOT / "wiki" / "concepts"


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    return fields


def sections(text):
    """Return {heading: [lines]} for level-2 headings."""
    out, current = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line.strip()
            out[current] = []
        elif current:
            out[current].append(line)
    return out


def main():
    errors = []
    source_ids = set()

    # W1 source cards
    for p in sorted(SRC_DIR.glob("S*.md")):
        fm = frontmatter(p.read_text(encoding="utf-8"))
        missing = [f for f in RULES["source_fields"] if not fm.get(f)]
        if missing:
            errors.append(f"W1 {p.name}: 缺少欄位 {missing}")
        source_ids.add(fm.get("id", p.stem))

    num_re = re.compile(RULES["number_pattern"])
    ok_re = re.compile(RULES["number_ok_pattern"])
    advice_res = [re.compile(a) for a in RULES["advice_patterns"]]
    cite_re = re.compile(r"\[(S\d{2})\]")

    pages = sorted(CONCEPT_DIR.glob("*.md"))
    checked_lines = 0
    for p in pages:
        text = p.read_text(encoding="utf-8")
        secs = sections(text)
        # W2
        for s in RULES["required_sections"]:
            if s not in secs:
                errors.append(f"W2 {p.name}: 缺少段落 {s}")
        for s in RULES["checked_sections"]:
            for line in secs.get(s, []):
                if not line.strip().startswith("- "):
                    continue
                checked_lines += 1
                short = line.strip()[:60]
                cites = cite_re.findall(line)
                # W3
                if not cites:
                    errors.append(f"W3 {p.name}: 沒有來源標記 → {short}")
                for c in cites:
                    if c not in source_ids:
                        errors.append(f"W3 {p.name}: 引用不存在的來源 {c} → {short}")
                # W4
                if num_re.search(line) and not ok_re.search(line):
                    errors.append(f"W4 {p.name}: 數字沒有年份或「假設/舉例」標記 → {short}")
                # W5
                for a in advice_res:
                    if a.search(line):
                        errors.append(f"W5 {p.name}: 投資建議語氣（{a.pattern}）→ {short}")
                # W6
                for rule in RULES["outdated_patterns"]:
                    if re.search(rule["pattern"], line):
                        ok = True
                        if "must_cite" in rule and f"[{rule['must_cite']}]" not in line:
                            ok = False
                        if "must_contain" in rule and not re.search(rule["must_contain"], line):
                            ok = False
                        if "must_cite" not in rule and "must_contain" not in rule:
                            ok = False
                        if not ok:
                            errors.append(f"W6 {p.name}: 過期/錯誤說法 [{rule['id']}] {rule['reason']} → {short}")

    report = [
        "check_wiki.py",
        f"來源卡 {len(source_ids)} 張｜概念頁 {len(pages)} 頁｜檢查條目 {checked_lines} 條",
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
