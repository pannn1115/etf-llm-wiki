#!/usr/bin/env python3
"""Recompute every example number in the Wiki with code, then confirm the
Wiki page states the same value.

LLM 很常把百分比、複利、配息率算錯，所以「自行試算」與來源裡的舉例都用程式重算一次。

Usage: python3 tools/verify_numbers.py [--out checks/xxx.txt]
Exit code 0 = pass, 1 = fail.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
C = ROOT / "wiki" / "concepts"


def pct(x, nd=0):
    return f"{x * 100:.{nd}f}%"


checks = []  # (page, description, computed_string, string_expected_in_page)

# 02 槓反 ETF：連兩天各漲 10%（S09 的舉例）
idx = 1.1 * 1.1 - 1
lev2 = 1.2 * 1.2 - 1
inv1 = 0.9 * 0.9 - 1
checks += [
    ("02-etf-types.md", "指數兩天各漲 10% 的累計", pct(idx), "+21%"),
    ("02-etf-types.md", "正 2 倍累計", pct(lev2), "+44%"),
    ("02-etf-types.md", "反 1 倍累計", pct(inv1), "-19%"),
]
# 02 自行試算：指數 100 → 110 → 100
d1, d2 = 0.10, 100 / 110 - 1
lev_side = (1 + 2 * d1) * (1 + 2 * d2) - 1
inv_side = (1 - d1) * (1 - d2) - 1
checks += [
    ("02-etf-types.md", "盤整時正 2 倍", pct(lev_side, 1), "-1.8%"),
    ("02-etf-types.md", "盤整時反 1 倍", pct(inv_side, 1), "-1.8%"),
]

# 03 費用：渣打舉例 5% - 0.40%
checks.append(("03-costs.md", "年報酬扣掉 0.40% 費用", pct(0.05 - (0.003 + 0.001), 1), "4.6%"))
# 03 自行試算：100 萬、5%、20 年、費用率 0.2% vs 1.0%（簡化：每年報酬直接扣費用率）
low = 100 * (1 + 0.05 - 0.002) ** 20
high = 100 * (1 + 0.05 - 0.010) ** 20
checks += [
    ("03-costs.md", "費用率 0.2% 20 年後（萬元）", f"{low:.0f} 萬元", "255 萬元"),
    ("03-costs.md", "費用率 1.0% 20 年後（萬元）", f"{high:.0f} 萬元", "219 萬元"),
    ("03-costs.md", "兩者差距（萬元）", f"{low - high:.0f} 萬元", "36 萬元"),
]

# 04 折溢價自行試算
nav, price, nav2 = 20, 21, 20.5
checks += [
    ("04-premium-discount.md", "溢價幅度", pct(price / nav - 1), "溢價 5%"),
    ("04-premium-discount.md", "溢價消失後買方報酬", pct(nav2 / price - 1, 1), "-2.4%"),
]

# 05 追蹤差距自行試算
td = (0.096 - 0.100) * 100
checks.append(("05-tracking.md", "追蹤差距（百分點）", f"{td:.1f} 個百分點", "-0.4 個百分點"))

# 06 配息：除息參考價、收益平準金例子（S10）
checks.append(("06-distributions.md", "50 元配 5 元的除息參考價", f"{50 - 5} 元", "45 元"))
distributable = 100_000 * 2 / 20          # 可分配收益 1 萬
ratio = 4_000 / distributable             # 預告配息占 40%
usable = 2_000 * ratio                    # 新申購平準金可動用 800 元
checks += [
    ("06-distributions.md", "可動用平準金", f"{usable:.0f} 元", "800 元"),
    ("06-distributions.md", "規模 12 萬、不用平準金配息率", pct(4_000 / 120_000, 2), "3.33%"),
    ("06-distributions.md", "規模 12 萬、加平準金配息率", pct((4_000 + usable) / 120_000), "4%"),
]

# 08 再平衡自行試算
stock, bond = 70 * 1.36, 30
total = stock + bond
move = stock - total * 0.7
checks += [
    ("08-rebalancing.md", "股票漲 36% 後金額（萬元）", f"{stock:.1f} 萬元", "95.2 萬元"),
    ("08-rebalancing.md", "股票占比", pct(stock / total, 1), "76.0%"),
    ("08-rebalancing.md", "要移到債券的金額（萬元）", f"{move:.2f} 萬元", "7.56 萬元"),
]


TOKEN = re.compile(r"-?\d[\d,\.]*(%|萬元|元|個百分點)")


def norm(s):
    return s.replace(" ", "").replace("−", "-").replace("＋", "+")


def main():
    lines, fails = ["verify_numbers.py", "頁面 | 項目 | 程式算出 | Wiki 寫的 | 結果"], 0
    for page, desc, computed, expected in checks:
        text = norm((C / page).read_text(encoding="utf-8"))
        comp = norm(computed).lstrip("+")
        exp = norm(expected)
        in_page = exp in text
        token = TOKEN.search(exp.replace("+", ""))
        match = bool(token) and token.group(0) == comp
        ok = in_page and match
        fails += 0 if ok else 1
        lines.append(f"{page} | {desc} | {computed} | {expected} | {'OK' if ok else 'FAIL'}"
                     + ("" if in_page else "（頁面找不到這個數字）"))
    lines.append(f"共 {len(checks)} 項，錯誤 {fails} 項")
    lines.append("結果：PASS" if fails == 0 else "結果：FAIL")
    out = "\n".join(lines)
    print(out)
    if "--out" in sys.argv:
        Path(sys.argv[sys.argv.index("--out") + 1]).write_text(out + "\n", encoding="utf-8")
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    main()
