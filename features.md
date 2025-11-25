# 🚀 功能開發計畫

> 本文件記錄所有計劃中和開發中的新功能，方便追蹤進度與優先級。

---

## 📋 目錄

- [已完成功能](#-已完成功能)
- [開發中功能](#-開發中功能)
- [計劃中功能](#-計劃中功能)
  - [1. 對話記憶與上下文理解](#1️⃣-對話記憶與上下文理解-)
  - [2. Excel 支援與智能表格分析](#2️⃣-excel-支援與智能表格分析-)
  - [3. 多檔案比較與跨文件分析](#3️⃣-多檔案比較與跨文件分析-)
  - [4. 檔案標籤與智能分類系統](#4️⃣-檔案標籤與智能分類系統-)
- [未來構想](#-未來構想)
- [優先級排序](#-優先級排序)

---

## ✅ 已完成功能

### 核心功能
- ✅ LINE Bot 基礎整合
- ✅ Google Gemini File Search API 整合
- ✅ 1對1 聊天支援
- ✅ 群組聊天支援（@mention 機制）
- ✅ 圖片即時分析（Gemini Vision）
- ✅ AI 口語化檔案列表
- ✅ Quick Reply 快速操作

### 檔案格式支援
- ✅ PDF 原生支援
- ✅ Word 文件支援（.doc 自動轉換為 .docx）
- ✅ PowerPoint 支援（.ppt 自動轉換為 .pptx）
- ✅ 純文字檔案（.txt, .md, .html, .csv, .rtf）
- ✅ 圖片檔案（JPG, PNG, GIF, WebP）

### 自動轉換功能
- ✅ .doc → .docx 自動轉換（使用 LibreOffice）
- ✅ .ppt → .pptx 自動轉換（使用 LibreOffice）
- ✅ 轉換進度通知
- ✅ 轉換失敗處理

### 檔案管理功能
- ✅ 檔案刪除功能（Flex Message UI）
- ✅ 每個檔案的刪除按鈕（🗑️ 紅色按鈕）
- ✅ 永久刪除支援（force=true）
- ✅ SDK + REST API 雙重刪除機制
- ✅ 刪除成功/失敗通知

**完成時間：** 2025-01

---

## 🔨 開發中功能

### 對話記憶與上下文理解 🧠（✅ 實作完成，待測試）

**狀態：** 實作完成 (2025-01-25)
**優先級：** 🔥 P0

#### 實作內容
✅ Google ADK Chat Session 整合
✅ Per-user session 管理系統
✅ 自動 session 超時（1小時）
✅ 清除對話指令（清除對話、reset、clear）
✅ 選項 A 實作：有文件才啟用 File Search
✅ 對話記憶與 File Search 整合

#### 核心程式碼
- `chat_session_manager.py` - Session 管理模組
- `main.py:query_file_search_with_session()` - Session-based 查詢
- `main.py:handle_text_message()` - 整合 Chat Session

#### 待測試項目
- [ ] 多輪對話記憶測試
- [ ] Session 超時測試
- [ ] 清除對話指令測試
- [ ] 群組對話隔離測試
- [ ] File Search 整合測試

#### 使用方式
```
👤 用戶：這份 Q1 報告的營收是多少？
🤖 Bot：根據 Q1 報告，營收為 NT$ 12,000,000

👤 用戶：成長率呢？
🤖 Bot：（記得上一輪在討論 Q1 報告）
       Q1 營收成長率為 +18%，相比去年同期

👤 用戶：清除對話
🤖 Bot：✅ 對話記憶已清除。我們可以重新開始對話了！
```

---

## 📅 計劃中功能

### 優先級說明
- 🔥 **P0** - 極高優先級（立即開發）
- ⭐ **P1** - 高優先級（1-2個月內）
- 💡 **P2** - 中優先級（長期規劃）

---

## 1️⃣ 對話記憶與上下文理解 🧠

**優先級：** 🔥 P0

### 功能描述
AI 記住對話歷史，支援追問和延伸討論，提供更自然的對話體驗。

### 使用場景
```
👤 用戶：這份 Q1 報告的營收是多少？
🤖 Bot：根據 Q1 報告，營收為 NT$ 12,000,000

👤 用戶：成長率呢？
🤖 Bot：（記得上一輪在討論 Q1 報告）
       Q1 營收成長率為 +18%，相比去年同期

👤 用戶：那第二季呢？
🤖 Bot：（理解用戶想看 Q2 的營收成長率）
       Q2 報告顯示：
       • 營收：NT$ 15,000,000
       • 成長率：+25%（相比去年 Q2）

👤 用戶：幫我整理重點
🤖 Bot：（知道要整理 Q1 和 Q2 的討論重點）
       📊 Q1-Q2 營收分析重點：
       1. 兩季營收持續成長
       2. Q2 表現優於 Q1
       3. 整體趨勢良好
```

### 技術要點

**核心技術：**
- Session 管理系統
- 對話歷史儲存（Redis / SQLite）
- Prompt 工程優化
- 上下文提取與理解

**實作重點：**
```python
# 1. Session 管理
conversation_history = {
    "user_U123456": {
        "messages": [...],
        "context": {
            "current_file": "Q1報告.pdf",
            "topic": "營收分析"
        }
    }
}

# 2. 對話歷史整合
async def query_with_context(user_message: str, user_id: str):
    history = get_conversation_history(user_id, limit=5)

    prompt = f"""
    對話歷史：{format_history(history)}
    用戶新問題：{user_message}
    請根據對話歷史理解用戶的問題並回答。
    """

    response = await client.generate_content(prompt)
    save_conversation(user_id, user_message, response.text)
    return response.text

# 3. 記憶管理
- 自動清理過舊對話（> 24 小時）
- 提供「清除對話歷史」指令
- 群組對話獨立管理
```

### 開發時間估計
**總計：3-4 天**
- Day 1: Session 儲存系統設計
- Day 2: 對話歷史整合到 prompt
- Day 3: 上下文理解優化
- Day 4: 記憶管理與清理機制

### 用戶價值
⭐⭐⭐⭐⭐ **極高**
- 大幅提升對話自然度
- 減少重複輸入
- 更像真人助手
- 支援複雜的多輪對話

### 技術難度
⭐⭐⭐ **中等**

### 依賴項
- 無（可獨立開發）

### 相關 Issue
- 待建立

---

## 2️⃣ Excel 支援與智能表格分析 📊

**優先級：** ⭐ P1

### 功能描述
支援 Excel 檔案（.xls/.xlsx）上傳，並提供智能表格數據分析功能。

### 使用場景
```
👤 用戶：[上傳 2024銷售數據.xlsx]
🤖 Bot：✅ 檔案已成功上傳！
       檔案名稱：2024銷售數據.xlsx

       📊 偵測到表格數據：
       • 3 個工作表
       • 共 1,234 筆資料

       [Quick Reply]
       📈 數據摘要 | 📊 統計分析 | 🔍 查詢數據

👤 用戶：第一季哪個產品銷售最好？
🤖 Bot：根據「2024銷售數據.xlsx」的分析：

       第一季銷售冠軍是「產品 A」
       • 銷售額：NT$ 2,500,000
       • 市佔率：35%
       • 成長率：+18%（相比去年同期）
```

### 技術要點

**核心技術：**
- LibreOffice 轉換（.xls → .xlsx）
- Google Gemini File Search API（已支援 .xlsx）
- 可選：pandas 數據分析

**實作重點：**
```python
# 1. 轉換函數（複用現有邏輯）
def convert_xls_to_xlsx(input_path: Path):
    # 與 convert_ppt_to_pptx 幾乎一樣
    subprocess.run([
        libreoffice_path,
        '--headless',
        '--convert-to', 'xlsx',
        '--outdir', str(output_dir),
        str(input_path)
    ])

# 2. 數據預處理（可選）
import pandas as pd

def analyze_excel(file_path):
    df = pd.read_excel(file_path, sheet_name=None)

    summary = {
        'sheets': len(df),
        'total_rows': sum(len(sheet) for sheet in df.values()),
        'columns': [list(sheet.columns) for sheet in df.values()]
    }
    return summary

# 3. 整合到上傳流程
elif file_ext in ['.xls', '.xlsx']:
    if file_ext == '.xls':
        # 轉換為 .xlsx
        convert_xls_to_xlsx(file_path)

    # 可選：生成數據摘要
    summary = analyze_excel(converted_path)

    # 上傳到 File Search Store
```

### 開發時間估計
**總計：2-3 天**
- Day 1: 轉換功能實作
- Day 2: 數據摘要生成（可選）
- Day 3: 測試與文件

### 用戶價值
⭐⭐⭐⭐⭐ **極高**
- 商業用戶最常用的格式
- AI 可以回答數據相關問題
- 自動數據分析節省時間

### 技術難度
⭐⭐ **低至中**

### 依賴項
- LibreOffice（已安裝）
- 可選：pandas（需安裝）

### 相關 Issue
- 待建立

---

## 3️⃣ 多檔案比較與跨文件分析 🔄

**優先級：** ⭐ P1

### 功能描述
AI 可以同時分析多個檔案，進行比較、對比、趨勢分析。

### 使用場景
```
👤 用戶：比較「Q1報告.pdf」和「Q2報告.pdf」的營收差異
🤖 Bot：📊 跨文件分析結果

       比較：Q1報告.pdf vs Q2報告.pdf

       【營收表現】
       • Q1: NT$ 12M → Q2: NT$ 15M
       • 成長率：+25%

       【主要差異】
       1. Q2 新產品線貢獻 NT$ 2M
       2. Q1 營運成本較高（-15%）
       3. Q2 市場擴張到南部地區

---

👤 用戶：在所有簡報中找「預算」相關的內容
🤖 Bot：🔍 跨檔案搜尋結果

       找到 3 個檔案包含「預算」：

       1️⃣ Q1報告.pptx（第 5 頁）
       「本季預算執行率 95%...」

       2️⃣ 年度計畫.pdf（第 12 頁）
       「2024年度總預算為 NT$ 50M...」

       3️⃣ 會議記錄.docx
       「決議下季度預算增加 15%...」
```

### 技術要點

**核心技術：**
- Gemini File Search API（原生支援跨檔案搜尋）
- 指令偵測與檔案名稱提取
- Prompt 工程優化

**實作重點：**
```python
# 1. 偵測比較指令
comparison_keywords = [
    '比較', '對比', 'compare', 'difference',
    '差異', '變化', '趨勢'
]

if any(keyword in user_message for keyword in comparison_keywords):
    files = extract_file_names(user_message)

    if len(files) >= 2:
        prompt = f"""
        請比較以下兩個文件的差異：
        1. {files[0]}
        2. {files[1]}

        關注點：{user_question}
        """

# 2. 跨檔案搜尋
async def search_across_files(keyword: str, store_name: str):
    response = client.chat.send_message(
        model=MODEL_NAME,
        prompt=f"在所有文件中搜尋「{keyword}」相關內容",
        file_search_store=store_name
    )
    return response

# 3. 智能檔案識別
def extract_file_names(message: str):
    # 使用正則或 AI 提取檔案名稱
    # 或使用 Gemini 理解自然語言
    pass
```

### 開發時間估計
**總計：2-3 天**
- Day 1: 比較指令偵測與檔名提取
- Day 2: 多檔案分析 prompt 優化
- Day 3: 跨檔案搜尋功能

### 用戶價值
⭐⭐⭐⭐⭐ **極高**
- 商業分析常見需求（季度比較、年度趨勢）
- 大幅提升 AI 實用性
- 差異化功能（競品少有）

### 技術難度
⭐⭐ **低至中**

### 依賴項
- 無（基於現有 File Search API）

### 相關 Issue
- 待建立

---

## 4️⃣ 檔案標籤與智能分類系統 🏷️

**優先級：** 💡 P2

### 功能描述
用戶可以為檔案加上標籤，系統也能自動建議標籤，方便檔案組織與搜尋。

### 使用場景
```
👤 用戶：[上傳 Q1財報.pdf]
🤖 Bot：✅ 檔案已成功上傳！
       檔案名稱：Q1財報.pdf

       🤖 AI 建議標籤：
       #財務 #報表 #Q1 #2024

       [Quick Reply]
       ✅ 採用建議 | ✏️ 自訂標籤 | ⏭️ 跳過

---

👤 用戶：列出 #財務 相關的檔案
🤖 Bot：找到 3 個標記為 #財務 的檔案：

       1. Q1財報.pdf
          標籤：#財務 #報表 #Q1

       2. 年度預算.xlsx
          標籤：#財務 #預算 #2024

       3. 成本分析.docx
          標籤：#財務 #分析
```

### 技術要點

**核心技術：**
- 檔案 metadata 資料庫擴展
- AI 自動標籤生成（Gemini）
- 標籤搜尋與過濾

**實作重點：**
```python
# 1. 資料庫擴展
file_metadata = {
    "document_id": "doc_abc123",
    "file_name": "Q1財報.pdf",
    "tags": ["財務", "報表", "Q1", "2024"],
    "auto_tags": True,
    ...
}

# 2. AI 自動標籤
async def generate_auto_tags(file_name: str, file_content: str):
    prompt = f"""
    分析以下檔案，建議 3-5 個合適的標籤：

    檔案名稱：{file_name}
    檔案內容摘要：{file_content[:500]}

    請以 #標籤 格式回傳
    """

    response = await client.generate_content(prompt)
    tags = extract_tags(response.text)
    return tags

# 3. 標籤搜尋
def search_by_tags(tags: list, store_name: str):
    files = db.query(store_name).filter(tags__contains=tags)
    return files

# 4. 標籤管理指令
# - "列出 #財務 檔案"
# - "為 xxx.pdf 加上 #重要"
# - "移除 xxx.pdf 的 #待處理 標籤"
```

### 開發時間估計
**總計：3-4 天**
- Day 1: 資料庫設計與標籤儲存
- Day 2: AI 自動標籤生成
- Day 3: 標籤搜尋與管理指令
- Day 4: UI 整合與測試

### 用戶價值
⭐⭐⭐⭐ **高**
- 檔案多時非常實用
- 提升組織效率
- AI 自動標籤減少手動工作

### 技術難度
⭐⭐⭐ **中等**

### 依賴項
- 需要檔案 metadata 資料庫系統

### 相關 Issue
- 待建立

---

## 💡 未來構想

以下是長期考慮的功能，目前優先級較低：

### 音訊與影片支援
- 語音訊息轉文字
- 影片字幕生成
- 音訊內容分析

### 進階協作功能
- 檔案分享（1對1 → 群組）
- 檔案權限管理
- 協作筆記功能

### 自動化與通知
- 定期檔案摘要報告
- 關鍵字監控通知
- Webhook 整合

### 第三方整合
- Google Drive 整合
- Dropbox 整合
- Email 轉發自動上傳

### 數據視覺化
- 從表格數據生成圖表
- 趨勢分析視覺化
- Dashboard 功能

---

## 📊 優先級排序

### 🔥 第一優先（立即開發）- 1週
1. **對話記憶與上下文理解** (3-4天)
   - 影響最大的 UX 提升
   - 技術風險低
   - 差異化競爭優勢

### ⭐ 第二優先（1-2個月內）- 1週
2. **Excel 支援與智能表格分析** (2-3天)
   - 商業用戶必備
   - 複用現有轉換邏輯

3. **多檔案比較與跨文件分析** (2-3天)
   - 差異化功能
   - 技術實作簡單

### 💡 第三優先（長期規劃）- 1週
4. **檔案標籤與智能分類系統** (3-4天)
   - 檔案多時才需要
   - 需要額外資料庫設計

---

## 🎯 推薦開發路徑

### 路徑 A：快速提升體驗（1週）⭐ 推薦
```
對話記憶（3-4天）→ 多檔案比較（2-3天）
```
**適合：** 想快速提升 AI 智能度和用戶體驗

### 路徑 B：完整進階功能（2週）
```
Excel 支援（2-3天）→ 檔案標籤（3-4天）→ 對話記憶（3-4天）
```
**適合：** 打造完整的商業級文件管理系統

### 路徑 C：商業用戶優先（1週）
```
對話記憶（3-4天）→ Excel 支援（2-3天）
```
**適合：** 兼顧用戶體驗與商業需求

---

## 📝 更新記錄

- **2025-01-25**:
  - ✅ 完成「對話記憶與上下文理解」功能實作
  - 使用 Google ADK Chat Session
  - 實作 Session 管理系統與清除對話指令
  - 初始文件創建，規劃 4 個主要功能
  - 確認檔案刪除功能已完成，移至「已完成功能」區
- **2025-01**: 完成 .doc 和 .ppt 自動轉換功能、檔案刪除管理功能

---

## 🤝 貢獻

如果您有新的功能想法或建議，歡迎：
1. 提交 GitHub Issue
2. 發起 Pull Request
3. 在本文件中新增構想

---

**最後更新：** 2025-01-25 (對話記憶功能實作完成)
