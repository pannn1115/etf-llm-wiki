# ETF 入門 LLM Wiki

一個以「ETF 入門」為主題的 **LLM Wiki**，以及從這個 Wiki 自動產生的 **教學 HTML 簡報**。

Wiki 讓 LLM 把多篇資料整理成有來源、有日期、可以檢查的知識頁；簡報只從 Wiki 取內容，並用檢查程式確認沒有混進 Wiki 以外的知識。

- 📖 Wiki 目錄：[wiki/index.md](wiki/index.md)
- 🖥️ 教學簡報：[slides/index.html](slides/index.html)（GitHub Pages：`https://<帳號>.github.io/<repo>/slides/`）

> ⚠️ 本專案僅供教學，**不構成投資建議**。資料整理至 2026-11-20，數字與規定可能改變，請以官方最新資訊為準。

---

## 內容範圍

| 項目 | 設定 |
|---|---|
| 主題 | ETF 入門：從買一檔股票，到用 ETF 組投資組合 |
| 聽眾 | 懂股票是什麼，但沒買過 ETF 的人 |
| 範圍 | 只談台灣掛牌的 ETF |
| 不做的事 | 不提個別 ETF 代號與排名、不給「幾歲配幾成股票」的建議、不寫投資建議 |

Wiki 的 8 個概念頁：

1. [ETF 是什麼](wiki/concepts/01-what-is-etf.md)
2. [ETF 的種類](wiki/concepts/02-etf-types.md)
3. [持有成本：內扣費用](wiki/concepts/03-costs.md)
4. [市價 vs 淨值：折溢價](wiki/concepts/04-premium-discount.md)
5. [追蹤差距與追蹤誤差](wiki/concepts/05-tracking.md)
6. [配息與總報酬](wiki/concepts/06-distributions.md)
7. [資產配置](wiki/concepts/07-asset-allocation.md)
8. [再平衡](wiki/concepts/08-rebalancing.md)

## 特色

- **每句都有來源**：概念頁的每一條重點都標 `[Sxx]`，連到對應的來源卡。
- **管理日期和衝突**：每張來源卡都有日期和狀態（有效／部分過期／統計已舊）；新舊說法衝突時登記在 [index.md](wiki/index.md) 和 `tools/rules.json`，之後自動擋下過期說法。
- **數字用程式重算**：複利、費用、配息率、再平衡等 19 個例子數字，由 `verify_numbers.py` 重算比對。
- **簡報只用 Wiki 的知識**：簡報上的每個數字都必須在對應的 Wiki 頁找得到。
- **新手友善**：專有名詞第一次出現就解釋，每張投影片不超過 180 字，每張都有講稿。
- **版面自動檢查**：用無頭瀏覽器逐張截圖，檢查內容有沒有超出畫面或被蓋住。

## 專案結構

```
.
├── README.md              專案說明（本檔）
├── SUBMISSION.md          作業繳交說明
├── AGENTS.md              給 LLM 的 Wiki 規則（ingest / query / lint）
├── index.html             GitHub Pages 入口，自動跳到簡報
├── .nojekyll              讓 GitHub Pages 直接提供檔案
├── wiki/
│   ├── index.md           目錄：概念頁、來源表、已登記的衝突
│   ├── log.md             操作紀錄（discuss / ingest / lint / fix）
│   ├── sources/S01–S11    來源卡：metadata＋改寫重點＋過期／衝突註記
│   └── concepts/01–08     概念頁：給新手的知識頁
├── slides/
│   └── index.html         教學簡報（單一 HTML 檔，不需網路）
├── docs/
│   ├── 01-discussion.md   先討論：主題、範圍、規則怎麼決定
│   ├── 02-workflow.md     流程圖（Mermaid）與設計說明
│   ├── workflow-graph.png 流程圖圖片版
│   ├── 03-run-record.md   一次實際執行的紀錄
│   └── 04-reflection.md   反思
├── tools/
│   ├── rules.json         檢查規則（語氣、過期說法、名詞表…）
│   ├── check_wiki.py      Wiki 檢查
│   ├── verify_numbers.py  數字重算
│   ├── check_slides.py    簡報內容檢查
│   ├── screenshot_slides.py 簡報版面檢查＋截圖
│   └── run_all.sh         一鍵跑全部檢查
└── checks/                每次檢查的輸出與截圖
```

## Wiki 怎麼組織

參考「LLM Wiki」的做法，分成三層：

| 層 | 位置 | 說明 |
|---|---|---|
| 來源 | `wiki/sources/` | 一篇資料一張卡。只寫改寫後的重點，不貼原文；記錄網址、日期、抓取日、可信度和狀態 |
| 知識 | `wiki/concepts/` | 依主題整理的概念頁。固定段落：一句話、重點、常見誤解、來源 |
| 規則 | `AGENTS.md`、`tools/rules.json` | LLM 維護 Wiki 時要遵守的規則，以及檢查程式用的規則 |

三種操作：

- **Ingest**：抓資料 → 驗證來源 → 寫來源卡 → 比對衝突 → 更新概念頁、index、log。
- **Query**：先讀 `index.md`，只用概念頁裡有來源標記的內容。
- **Lint**：跑 `check_wiki.py` 和 `verify_numbers.py`，全部通過才產生簡報。

## 運作流程

```
討論 → 取得資料 → 【來源驗證】 → Ingest → 生成 Wiki → 【Wiki 檢查】 → 查詢 Wiki → 生成簡報 → 【簡報檢查】 → 輸出
```

括號內是檢查節點，沒通過就退回前面重做。簡報如果出現 Wiki 沒有的內容，要退回 Wiki 補，而不是只改簡報。完整流程圖與說明見 [docs/02-workflow.md](docs/02-workflow.md)。

## 使用方式

### 看簡報

直接用瀏覽器打開 `slides/index.html`。

| 按鍵 | 功能 |
|---|---|
| `→` / 空白鍵 / `Enter` | 下一頁 |
| `←` | 上一頁 |
| `N` | 打開／關閉講稿 |
| `F` | 全螢幕 |
| `Home` / `End` | 第一頁／最後一頁 |

網址加 `#6` 可以直接跳到第 6 張；手機可以左右滑動；用瀏覽器「列印 → 另存 PDF」可以匯出每頁一張的 PDF。

### 跑檢查

```bash
bash tools/run_all.sh
```

需要 Python 3。版面檢查另外需要：

```bash
pip install playwright
playwright install chromium
```

（沒裝 Playwright 的話會自動略過版面檢查。）

| 程式 | 檢查什麼 |
|---|---|
| `check_wiki.py` | 來源卡欄位齊全、每條重點有來源、數字有年份或標明假設、沒有投資建議語氣、沒有已知過期說法 |
| `verify_numbers.py` | 重算 Wiki 裡 19 個例子數字 |
| `check_slides.py` | 每張有對應 Wiki 頁和來源、數字都在 Wiki 裡、名詞第一次出現有解釋、字數上限、結尾有免責聲明 |
| `screenshot_slides.py` | 內容不超出畫面、不壓到來源列、沒有 console 錯誤、控制列不蓋住投影片 |

### 新增一篇資料

1. 在 `wiki/sources/` 新增 `S12.md`，照既有來源卡的欄位填寫。
2. 和現有來源比對；如果說法衝突，寫在兩張卡的「已過期 / 衝突」，並把規則加進 `tools/rules.json`。
3. 更新相關概念頁、`wiki/index.md`，並在 `wiki/log.md` 加一筆紀錄。
4. 跑 `bash tools/run_all.sh`，全部通過後再更新簡報。

## 部署到 GitHub Pages

1. 把整個資料夾上傳到 public repo（包含隱藏檔 `.nojekyll`）。
2. Repo → **Settings** → **Pages** → Source 選 **Deploy from a branch**，Branch 選 `main`、資料夾選 `/ (root)`。
3. 等 1–2 分鐘，打開 `https://<帳號>.github.io/<repo>/`，會自動跳到簡報。

## 資料來源

共 11 篇，包括臺灣證券交易所專題與 e添富、金管會（經 e添富轉載）、中央社、經濟日報、渣打銀行、Vanguard。完整清單、日期與狀態見 [wiki/index.md](wiki/index.md)。

來源卡內容都是改寫後的重點，原文著作權屬於原發布單位，請點來源卡裡的網址閱讀原文。
