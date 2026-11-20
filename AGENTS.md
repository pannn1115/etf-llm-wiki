# AGENTS.md — ETF 入門 LLM Wiki 的維護規則

這份檔案是給 LLM（Claude / Codex 等 agent）看的「Wiki 憲法」。每次 ingest、查詢、產生簡報前都要先讀。
（同內容也適用 CLAUDE.md 慣例。）

## 1. 主題與範圍（討論階段已定案，見 docs/01-discussion.md）
- 主題：ETF 入門：從買一檔股票，到用 ETF 組投資組合
- 聽眾：懂股票是什麼、但沒買過 ETF 的人
- 範圍：只談在台灣掛牌的 ETF；不談海外 ETF 的稅與匯率細節
- 真實代號：不提個別 ETF 代號與排名，不比較哪一檔比較好
- 資產配置：只講股債比例、分散、再平衡的概念；不給「幾歲該配幾成股票」之類建議

## 2. 資料夾結構
```
wiki/
  index.md        # 目錄：每頁一行摘要 + 來源表（查詢時先讀這裡）
  log.md          # 時間序紀錄：discuss / ingest / lint / generate
  sources/Sxx.md  # 來源卡：metadata + 改寫重點 + 過期/衝突註記（不貼原文）
  concepts/*.md   # 概念頁：給新手看的知識頁
slides/index.html # 由 Wiki 產生的教學簡報
tools/            # 檢查程式（check_wiki / verify_numbers / check_slides）
checks/           # 每次檢查的輸出紀錄
```

## 3. 三種操作
### Ingest（加入一篇來源）
1. 抓取來源。抓不到（被擋、404、只有錯誤頁）→ 記在 log.md，找替代來源，不可用記憶補內容。
2. 寫來源卡 `wiki/sources/Sxx.md`，frontmatter 必填：id, title, publisher, date, url, fetched, type, status。
3. 內容一律改寫，不貼原文段落。
4. 跟既有來源比對：同一件事說法不同 → 在兩張卡的「已過期 / 衝突」寫清楚，並把規則加進 `tools/rules.json` 的 `outdated_patterns`。
5. 更新相關概念頁、index.md，並在 log.md 加一筆。

### Query（從 Wiki 取答案 / 做簡報）
- 先讀 index.md 找頁面，只用概念頁裡有來源標記的內容；Wiki 沒有的東西不可自己補。

### Lint（檢查）
- 執行 `python3 tools/check_wiki.py` 與 `python3 tools/verify_numbers.py`，全部通過才可以產生簡報。

## 4. 概念頁寫作規則（check_wiki.py 會檢查）
1. 必備段落：`## 一句話`、`## 重點`、`## 常見誤解`、`## 來源`。
2. 「重點」與「常見誤解」裡每一條都要有來源標記，例如 `[S03]`，而且 Sxx 必須存在。
3. 有統計數字（%、元、檔、億、兆、萬）的句子，必須寫年份；若是例子，要寫明「假設」「舉例」或「試算」。
4. 自己算的數字要寫「自行試算（假設）」，並登記在 `tools/verify_numbers.py` 讓程式重算。
5. 不可出現投資建議語氣（推薦、必買、穩賺、首選、保證獲利……），描述來源的看法時寫成「金管會描述／作者建議」。
6. 舊資料與新資料衝突時，以較新的官方來源為準；提到舊說法時要同時引用新來源。

## 5. 簡報規則（check_slides.py 會檢查）
1. 每張內容投影片要標 `data-wiki`，指向它根據的概念頁。
2. 每張內容投影片底部要有來源（Sxx）。
3. 投影片上的數字必須出現在對應的概念頁裡（簡報不可以自己生新數字）。
4. 專有名詞第一次出現的那一張，要用 `<dfn>` 解釋。
5. 每張投影片正文不超過 180 字（新手讀得完）。
6. 結尾頁（`data-type="end"`）要有免責聲明：僅供教學，不構成投資建議。
7. 版面檢查（screenshot_slides.py）：內容不可超出投影片、不可壓到來源列、console 不可有錯誤、底部控制列不可蓋住投影片。

## 6. 檢查程式本身
- 新增或修改檢查規則後，先做自我測試：故意寫錯，確認會被抓到；也確認正確的否定句不會被誤判。
- 一鍵執行全部檢查：`bash tools/run_all.sh`
