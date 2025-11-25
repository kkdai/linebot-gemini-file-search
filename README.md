# LINE Bot 智能文件助手 📚

> 一個結合 LINE Bot 與 Google Gemini File Search 的智能文件問答機器人

<img width="1179" height="2556" alt="image" src="https://github.com/user-attachments/assets/4d5a4e0e-0eec-4753-a1b0-8b1e1e6d661a" />


## 🎯 這是什麼？

想像一下：你可以把任何 PDF、Word 文件、圖片傳給 LINE Bot，然後直接問它「這份文件在講什麼？」、「幫我整理重點」、「這張圖片裡有什麼？」，Bot 就會用 AI 幫你分析並回答！

這個專案讓你輕鬆打造一個專屬的文件智能助手，只要：
1. 📤 傳送文件或圖片給 Bot
2. 💬 用自然語言提問
3. 🤖 AI 立即分析並回答

## ✨ 功能特色

### 📁 支援多種檔案格式
- 📄 文件檔案：PDF、Word (DOC/DOCX)、PowerPoint (PPT/PPTX)、純文字 (TXT) 等
  - 自動上傳到 File Search Store
  - 支援後續文字查詢
  - **自動轉換功能**：
    - .doc 格式自動轉換為 .docx
    - .ppt 格式自動轉換為 .pptx
- 🖼️ 圖片檔案：JPG、PNG 等
  - 使用 Gemini 視覺理解能力即時分析
  - 無需上傳，直接回傳分析結果

### 🧠 AI 智能問答
- 使用 Google Gemini 2.5 Flash 模型
- 基於你上傳的文件內容回答問題
- 支援繁體中文、英文等多語言

### 💬 對話記憶功能 🆕
- **記住對話歷史**：AI 會記得之前的對話內容，支援追問和延伸討論
- **自動上下文理解**：使用 Google ADK Chat Session 技術
- **智能 Session 管理**：
  - 每位用戶獨立的對話記憶
  - 自動超時清理（1小時無活動）
  - 手動清除指令：輸入「清除對話」、「reset」或「clear」
- **無縫整合 File Search**：對話記憶與文件搜尋完美結合

### 👥 多人協作支援
- **1 對 1 聊天**：每個人有自己的文件庫（隔離的），所有訊息都會回覆
- **群組聊天**：
  - 群組成員共享文件庫（大家都能查詢）
  - **需要 @提及（mention）機器人才會回覆文字訊息**
  - 上傳檔案/圖片不需要 mention，會自動處理
  - 回覆訊息會顯示在群組中，所有成員都看得到
- 自動識別對話類型，無需手動設定

### 📋 檔案管理功能
- **AI 口語化列表**：使用 Google ADK Agent 以自然對話方式介紹檔案
- **智能識別**：支援多種關鍵字（列出檔案、顯示檔案、list files 等）
- **Quick Reply 快速操作**：上傳成功後提供「生成摘要」、「重點整理」等快捷按鈕
- **明確檔案指定**：Quick Reply 自動帶入檔案名稱，避免混淆
- **檔案刪除**：每個檔案都有刪除按鈕，輕鬆管理文件庫

### 🚀 部署簡單
- 支援 Docker 容器化部署
- 可部署到 Google Cloud Run
- 或在本地開發測試

### 🔮 未來規劃
更多精彩功能正在開發中！查看 [功能開發計畫](./features.md) 了解即將推出的新功能。

## 📸 使用範例

### 📤 上傳文件並查詢

```
👤 你: [上傳一份會議記錄.pdf]
🤖 Bot: ✅ 檔案已成功上傳！
       檔案名稱：會議記錄.pdf

       現在您可以詢問我關於這個檔案的任何問題。

       [Quick Reply 按鈕]
       📝 生成檔案摘要 | 📌 重點整理 | 📋 列出檔案

👤 你: [點擊「📝 生成檔案摘要」]
     → 自動發送「請幫我生成「會議記錄.pdf」這個檔案的摘要」

🤖 Bot: 好的！這份會議記錄主要記錄了 2025 年第一季的營運會議...

       主要決議包括：
       1. 下季度預算增加 15%
       2. 新產品預計 6 月上市
       3. 人力資源部門將擴編 3 名員工
       ...
```

### 🔄 自動轉換 .doc 檔案

```
👤 你: [上傳舊版報告.doc]
🤖 Bot: 正在處理您的檔案，請稍候...

🤖 Bot: 🔄 偵測到 .doc 格式，正在自動轉換為 .docx...

🤖 Bot: ✅ 檔案已成功上傳！
       檔案名稱：舊版報告.docx

       📝 註：檔案已自動從 .doc 轉換為 .docx 格式

       現在您可以詢問我關於這個檔案的任何問題。

       [Quick Reply 按鈕]
       📝 生成檔案摘要 | 📌 重點整理 | 📋 列出檔案

👤 你: 這份報告的重點是什麼？
🤖 Bot: 好的！這份報告主要討論...
```

> 💡 **自動轉換功能**：系統使用 LibreOffice 自動將 .doc 轉換為 .docx，無需手動操作！

### 📊 自動轉換 .ppt 簡報檔

```
👤 你: [上傳季度報告.ppt]
🤖 Bot: 正在處理您的檔案，請稍候...

🤖 Bot: 🔄 偵測到 .ppt 格式，正在自動轉換為 .pptx...

       ⏳ PPT 檔案較大，轉換可能需要 10-30 秒，請稍候...

🤖 Bot: ✅ 檔案已成功上傳！
       檔案名稱：季度報告.pptx

       📊 註：檔案已自動從 .ppt 轉換為 .pptx 格式

       現在您可以詢問我關於這個檔案的任何問題。

       [Quick Reply 按鈕]
       📝 生成檔案摘要 | 📌 重點整理 | 📋 列出檔案

👤 你: 這份簡報的主要內容是什麼？
🤖 Bot: 這份季度報告簡報包含以下重點：
       1. 第一季營收達成率 120%
       2. 新產品市場反應良好
       3. 下季度策略規劃...
```

> 💡 **PPT 轉換說明**：
> - 保留文字、圖片、表格內容
> - 動畫效果可能遺失
> - 轉換時間視檔案大小而定（通常 10-30 秒）
> - PPTX 格式可直接上傳，無需轉換

### 💬 多輪對話記憶 🆕

```
👤 你: 這份 Q1 報告的營收是多少？
🤖 Bot: 根據 Q1 報告，營收為 NT$ 12,000,000，
       相比去年同期成長了 18%。

👤 你: 那成本呢？
🤖 Bot: （記得你在問 Q1 報告）
       Q1 的總成本為 NT$ 8,500,000，
       營運成本佔比 45%，人力成本佔比 35%。

👤 你: 淨利率是多少？
🤖 Bot: （知道你在討論 Q1 的財務數據）
       Q1 的淨利率為 29.2%
       （營收 1200萬 - 成本 850萬 = 淨利 350萬）

👤 你: 清除對話
🤖 Bot: ✅ 對話記憶已清除。我們可以重新開始對話了！
```

> 💡 **對話記憶說明**：
> - AI 會記住整個對話歷史，理解「那」、「它」等代詞
> - 支援追問和延伸討論，無需重複完整問題
> - 輸入「清除對話」、「reset」或「clear」可清除記憶
> - 1小時無活動會自動清除（節省資源）

### 📋 列出檔案（AI 口語化）

```
👤 你: 列出檔案
🤖 Bot: 我看到你上傳了 3 個檔案唷！

       首先是「會議記錄.pdf」，這是在 1月8日下午2點半上傳的。
       接著是「技術文件.docx」，是在下午3點20分傳的。
       最後一個是「報告.txt」，這個是在下午4點10分上傳的。

       需要我幫你查詢哪個檔案的內容呢？😊
```

> 💡 **提示**：使用 Google ADK Agent 讓 AI 用自然對話方式介紹檔案，比傳統的清單或卡片更親切！

### 🗑️ 刪除檔案

```
👤 你: 列出檔案
🤖 Bot: [顯示檔案列表，每個檔案都有刪除按鈕]

       ┌─────────────────────┐
       │ 會議記錄.pdf        │
       │ 2025-01-08 14:30    │
       │ [🗑️ 刪除檔案]      │
       └─────────────────────┘

👤 你: [點擊 🗑️ 刪除檔案]
🤖 Bot: ✅ 檔案已刪除成功！

       如需查看剩餘檔案，請點擊下方按鈕。
```

> 💡 **檔案刪除說明**：
> - 每個檔案都有紅色的刪除按鈕
> - 刪除是永久性的，無法復原
> - 刪除後會立即從文件庫移除

### 🖼️ 圖片分析

```
👤 你: [傳送圖片]
🤖 Bot: 正在分析您的圖片，請稍候...

🤖 Bot: 📸 圖片分析結果：

       這張圖片顯示了一個現代化的辦公室空間...
```

### 👥 群組聊天使用

```
[在群組中]

👤 Alice: [上傳 Q1報告.pdf]
🤖 Bot: ✅ 檔案已成功上傳！
       檔案名稱：Q1報告.pdf

       現在您可以詢問我關於這個檔案的任何問題。
       📝 生成檔案摘要 | 📌 重點整理 | 📋 列出檔案

👤 Bob: 這份報告的結論是什麼？
（Bot 不回覆，因為沒有 mention）

👤 Charlie: @bot 這份報告的結論是什麼？
🤖 Bot: 根據 Q1 報告，主要結論如下：
       1. 營收成長 20%
       2. 客戶滿意度提升到 90%
       3. 新產品線表現優異
       ...

👤 Alice: @bot 列出檔案
🤖 Bot: 我看到這個群組上傳了 1 個檔案唷！

       是「Q1報告.pdf」，這是在今天下午3點上傳的。
       需要我幫你查詢這個檔案的內容嗎？😊
```

> 💡 **群組使用重點**：
> - ✅ 上傳檔案/圖片：直接上傳，無需 mention
> - ⚠️ 查詢文件：需要 @機器人
> - ✅ 所有成員共享文件庫

## 🛠️ 技術架構

- **Python 3.9+**
- **FastAPI** - 高效能異步 Web 框架
- **LINE Messaging API** - LINE Bot 介面（含 Quick Reply）
- **Google Gemini API** - 文件搜尋與 AI 問答
- **Google ADK (Agent Development Kit)** - 口語化檔案管理 Agent
- **Docker** - 容器化部署

## 📦 快速開始

### 1️⃣ 環境準備

首先，你需要準備這些：

**LINE Bot 設定**
1. 到 [LINE Developers Console](https://developers.line.biz/console/) 建立一個 Messaging API channel
2. 取得你的 `Channel Secret` 和 `Channel Access Token`

**Google Gemini API**
1. 到 [Google AI Studio](https://aistudio.google.com/app/apikey) 建立 API Key
2. 複製你的 `API Key`

### 2️⃣ 下載專案

```bash
git clone <你的 repo URL>
cd linebot-file-search-adk
```

### 3️⃣ 安裝套件

```bash
pip install -r requirements.txt
```

**額外依賴：LibreOffice（用於 .doc 和 .ppt 格式轉換）**

為了支援舊版 .doc 和 .ppt 檔案的自動轉換，需要安裝 LibreOffice：

```bash
# macOS
brew install --cask libreoffice

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libreoffice libreoffice-impress

# 驗證安裝
soffice --version
```

> 💡 **注意**：如果未安裝 LibreOffice，.doc 和 .ppt 檔案將無法上傳，但其他格式（.docx, .pptx, .pdf 等）仍可正常使用。

### 4️⃣ 設定環境變數

建立 `.env` 檔案或直接設定環境變數：

```bash
export ChannelSecret="你的 LINE Channel Secret"
export ChannelAccessToken="你的 LINE Channel Access Token"
export GOOGLE_API_KEY="你的 Google Gemini API Key"
```

### 5️⃣ 啟動服務

```bash
uvicorn main:app --reload
```

服務會在 `http://localhost:8000` 啟動

### 6️⃣ 設定 Webhook

如果在本地開發，使用 ngrok 來建立公開的網址：

```bash
ngrok http 8000
```

然後到 LINE Developers Console，把 Webhook URL 設定為：
```
https://你的-ngrok-網址.ngrok.io/
```

## 🎮 使用方式

### 📱 在不同對話中使用

**1 對 1 聊天**：
- ✅ 直接發送訊息，無需 mention
- ✅ 每個人有獨立的文件庫
- ✅ 所有訊息都會得到回覆

**群組聊天**：
- ✅ **上傳檔案/圖片**：直接上傳，無需 mention
- ⚠️ **查詢文件內容**：需要 @提及（mention）機器人
- ✅ 回覆訊息會顯示在群組中
- ✅ 所有成員共享同一個文件庫

> 💡 **群組使用提示**：在群組中查詢文件時，記得要 @機器人，例如：「@bot 這份報告的結論是什麼？」

### 📤 上傳檔案

**文件檔案（PDF、DOCX、TXT 等）：**
1. 直接在 LINE 聊天室傳送文件檔案（**群組中無需 mention**）
2. Bot 會回覆「正在處理您的檔案，請稍候...」
3. 上傳完成後會顯示「✅ 檔案已成功上傳！」
4. 現在可以開始提問關於文件的內容
   - **1對1**：直接提問
   - **群組**：需要 @機器人

**圖片檔案（JPG、PNG 等）：**
1. 直接在 LINE 聊天室傳送圖片（**群組中無需 mention**）
2. Bot 會回覆「正在分析您的圖片，請稍候...」
3. 立即收到圖片分析結果
4. 圖片不會儲存，每次都是即時分析

### 💬 開始提問

**1 對 1 聊天（直接提問）：**

- 「這份文件的重點是什麼？」
- 「幫我整理成條列式」
- 「第三章在講什麼？」
- 「根據這份報告，我們應該注意什麼？」

**群組聊天（需要 mention）：**

- 「@bot 這份文件的重點是什麼？」
- 「@bot 幫我整理成條列式」
- 「@bot 第三章在講什麼？」
- 「@bot 根據這份報告，我們應該注意什麼？」

**圖片分析（直接傳圖片，無需 mention）：**

- 傳送圖片後自動分析
- 會描述圖片的內容、場景、物品、文字等
- 無需額外提問

### 📋 管理已上傳的檔案

**列出檔案（AI 口語化）：**

支援多種關鍵字來查看已上傳的文件：
- 「列出檔案」或「列出文件」
- 「顯示檔案」或「查看檔案」
- 「我的檔案」或「檔案列表」
- 英文：「list files」、「show files」、「my files」

**使用方式**：
- **1對1**：直接輸入「列出檔案」
- **群組**：輸入「@bot 列出檔案」

Bot 會用 **Google ADK Agent** 以自然對話方式介紹檔案：
- 🤖 口語化描述（而非條列式清單）
- 📅 自動格式化上傳時間
- 💬 友善親切的語氣
- 🎯 智能總結（檔案多時會挑重點說明）

**Quick Reply 快速操作：**

上傳檔案成功後，Bot 會提供快捷按鈕：
- 📝 **生成檔案摘要** - 自動帶入檔案名稱「請幫我生成『檔名』這個檔案的摘要」
- 📌 **重點整理** - 自動帶入檔案名稱「請幫我整理『檔名』的重點」
- 📋 **列出檔案** - 查看所有已上傳的文件

> 💡 **提示**：
> - Quick Reply 會自動帶入剛上傳的檔案名稱，避免多檔案時的混淆
> - **在群組中點擊 Quick Reply 後，仍需手動加上 @機器人**

### 📁 檔案管理方式

**文件檔案：**
- **1對1 聊天**：
  - 每個人有獨立的文件庫（`user_U123456`）
  - 只能查詢自己上傳的檔案
  - 完全隔離，保護隱私
- **群組聊天**：
  - 所有群組成員共享同一個文件庫（`group_G123456`）
  - 任何人上傳的檔案都能被查詢
  - **注意**：群組中的文件對所有成員公開
- 文件會持續保存在 File Search Store 中

**圖片檔案：**
- 不會儲存到 File Search Store
- 每次傳送都是即時分析
- 分析完成後圖片會自動清除

> ⚠️ **隱私提醒**：如果需要查詢私密文件，請在 1對1 聊天中上傳，避免在群組中分享敏感資料。

## 🐳 Docker 部署

### 建立映像檔

```bash
docker build -t linebot-file-search .
```

### 啟動容器

```bash
docker run -p 8000:8000 \
  -e ChannelSecret=你的SECRET \
  -e ChannelAccessToken=你的TOKEN \
  -e GOOGLE_API_KEY=你的API_KEY \
  linebot-file-search
```

## ☁️ 部署到 Google Cloud Run

### 步驟 1：安裝 Google Cloud SDK

參考[官方文件](https://cloud.google.com/sdk/docs/install)安裝

### 步驟 2：登入並設定專案

```bash
gcloud auth login
gcloud config set project 你的專案ID
```

### 步驟 3：建立並上傳 Docker 映像

```bash
gcloud builds submit --tag gcr.io/你的專案ID/linebot-file-search
```

### 步驟 4：部署到 Cloud Run

```bash
gcloud run deploy linebot-file-search \
  --image gcr.io/你的專案ID/linebot-file-search \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated \
  --set-env-vars ChannelSecret=你的SECRET,ChannelAccessToken=你的TOKEN,GOOGLE_API_KEY=你的API_KEY
```

### 步驟 5：取得服務網址

```bash
gcloud run services describe linebot-file-search \
  --platform managed \
  --region asia-east1 \
  --format 'value(status.url)'
```

把這個網址設定到 LINE Bot 的 Webhook URL 就完成了！

## 🔒 安全性建議

**不要把敏感資訊寫進程式碼！** 建議使用 Google Secret Manager：

```bash
# 建立 secrets
echo -n "你的SECRET" | gcloud secrets create line-channel-secret --data-file=-
echo -n "你的TOKEN" | gcloud secrets create line-channel-token --data-file=-
echo -n "你的API_KEY" | gcloud secrets create google-api-key --data-file=-
```

部署時使用 secrets：

```bash
gcloud run deploy linebot-file-search \
  --image gcr.io/你的專案ID/linebot-file-search \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated \
  --update-secrets=ChannelSecret=line-channel-secret:latest,ChannelAccessToken=line-channel-token:latest,GOOGLE_API_KEY=google-api-key:latest
```

## 📊 監控與除錯

部署後可以透過 Google Cloud Console 監控：

### 查看 Logs

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=linebot-file-search" --limit 50
```

### 檢查服務狀態

直接到 [Cloud Run Console](https://console.cloud.google.com/run) 查看服務狀態、錯誤率、回應時間等指標

## 💡 使用小技巧

1. **上傳多份文件**：可以連續上傳多份文件，Bot 會記住所有文件並在查詢時搜尋
2. **圖片即時分析**：圖片不需要「上傳」，直接傳送就會立即分析並回覆
3. **文件持久化**：上傳的文件會持續保存在 File Search Store，可隨時查詢
4. **Quick Reply 快捷操作**：
   - 上傳檔案後立即使用 Quick Reply 按鈕（生成摘要、重點整理）
   - Quick Reply 會自動帶入檔案名稱，避免多檔案時混淆
   - 點擊按鈕比手動輸入更快速方便
5. **AI 口語化檔案列表**：
   - 輸入「列出檔案」會得到自然對話式的回應
   - AI 會用親切的語氣介紹每個檔案和上傳時間
   - 比傳統清單更友善、更易讀
6. **支援的檔案類型**：
   - 文件：PDF、Word (DOC/DOCX)、PowerPoint (PPT/PPTX)、TXT、Markdown、HTML、CSV、RTF 等
   - 圖片：JPG、JPEG、PNG、GIF、WebP
   - **自動轉換**：
     - .doc 檔案自動轉換為 .docx（2-5秒）
     - .ppt 檔案自動轉換為 .pptx（10-30秒）

## 🤔 常見問題

### 基本使用

**Q: 為什麼我問問題時 Bot 說「您還沒有上傳任何檔案」？**
A: 這個訊息是針對文件查詢。請先上傳文件檔案（PDF、DOCX 等），Bot 才能根據文件內容回答。如果您想分析圖片，請直接傳送圖片，無需上傳。

**Q: 圖片和文件的處理有什麼不同？**
A:
- **文件**：會上傳到 File Search Store，可以後續查詢，適合需要反覆查詢的資料
- **圖片**：即時分析後立即清除，適合快速了解圖片內容

**Q: 檔案會保存多久？**
A: 文件檔案會持續保存在 Google Gemini 的 File Search Store，圖片分析後會立即清除。

**Q: 支援哪些語言？**
A: Google Gemini 支援多種語言，包括繁體中文、簡體中文、英文、日文等。

**Q: 可以處理多大的檔案？**
A: 取決於 Google Gemini File API 的限制，一般文件都沒問題。圖片建議不超過 10MB。

**Q: 支援舊版 .doc 格式嗎？**
A: **支援**！系統會自動使用 LibreOffice 將 .doc 轉換為 .docx 格式再上傳。轉換過程完全自動化，無需手動操作。如果轉換失敗（例如未安裝 LibreOffice），系統會提示您手動轉換。

**Q: .doc 轉換需要多久時間？**
A: 通常只需要幾秒鐘。系統會顯示「🔄 偵測到 .doc 格式，正在自動轉換為 .docx...」的訊息。檔案過大時可能需要更長時間（最多 60 秒超時限制）。

**Q: 支援舊版 .ppt 格式嗎？**
A: **支援**！系統會自動使用 LibreOffice 將 .ppt 轉換為 .pptx 格式再上傳。PPTX 格式可直接上傳無需轉換。轉換過程完全自動化，會保留文字、圖片、表格等內容，但動畫效果可能遺失。

**Q: .ppt 轉換需要多久時間？**
A: PPT 檔案通常較大，轉換時間約 10-30 秒。系統會顯示「🔄 偵測到 .ppt 格式，正在自動轉換為 .pptx...」並提示預計等待時間。超大檔案（>50MB）或內容複雜時可能需要更長時間（最多 120 秒超時限制）。

### 對話記憶功能 🆕

**Q: 對話記憶是什麼？**
A: Bot 會記住你們之前的對話內容，讓你可以追問和延伸討論，不需要每次都重複完整的問題。例如問完「Q1 報告的營收是多少？」後，可以直接問「那成本呢？」，Bot 會知道你在問 Q1 報告的成本。

**Q: 對話記憶會保存多久？**
A: 每個用戶的對話記憶會保存 1 小時。如果 1 小時內沒有任何活動，系統會自動清除記憶以節省資源。你也可以隨時輸入「清除對話」、「reset」或「clear」來手動清除。

**Q: 群組聊天的對話記憶是共享的嗎？**
A: 是的。同一個群組內的所有成員共享對話記憶，任何人的提問都會被記錄。這讓團隊討論更順暢。但每個用戶在 1 對 1 聊天時有自己獨立的記憶。

**Q: 如何清除對話記憶？**
A: 輸入以下任一指令即可：
- 「清除對話」
- 「清除对话」（簡體）
- 「reset」
- 「clear」
- 「重置對話」
- 「清空對話」

**Q: 對話記憶會影響費用嗎？**
A: 對話記憶會讓每次 API 調用包含歷史對話，可能增加 token 使用量。但我們已設置 1 小時自動清除機制來控制成本。如果你想進一步節省費用，可以在討論完一個主題後手動清除對話。

**Q: PPT 轉換會保留動畫和特效嗎？**
A: 文字、圖片、表格等內容會完整保留，但動畫效果、轉場特效、嵌入影片可能會遺失。如果需要完整格式，建議使用 Microsoft PowerPoint 手動將 .ppt 另存為 .pptx 格式後再上傳。

### 群組使用

**Q: 為什麼在群組中 Bot 不回覆我的問題？**
A: 在群組聊天中，Bot **只會在被 @提及（mention）時回覆文字訊息**。請確保你的訊息中有 @機器人，例如：「@bot 這份報告的結論是什麼？」

**Q: 在群組中上傳檔案需要 mention 嗎？**
A: **不需要**！上傳檔案或圖片時不需要 mention，Bot 會自動處理。只有**查詢文件內容**時才需要 @機器人。

**Q: 群組中上傳檔案後，為什麼我收到私訊？**
A: 這個問題已經修復！現在群組中上傳檔案後，成功訊息會顯示在群組中，所有成員都看得到。

**Q: 群組聊天中，其他人上傳的檔案我也能查詢嗎？**
A: **可以**！群組中所有成員共享同一個文件庫。但要記得 @機器人才能查詢，例如：「@bot 列出檔案」

**Q: 在群組中點擊 Quick Reply 按鈕後還需要 mention 嗎？**
A: **需要**！Quick Reply 會自動帶入問題文字，但在群組中仍需要手動加上 @機器人。例如點擊「生成檔案摘要」後，需要改成「@bot 請幫我生成...」

**Q: 群組中的文件會被其他成員看到嗎？**
A: **會**！群組中所有成員共享同一個文件庫，任何人上傳的文件都可以被查詢。如果需要查詢私密文件，請在 1對1 聊天中上傳。

### 功能相關

**Q: Quick Reply 按鈕是什麼？**
A: Quick Reply 是上傳檔案成功後出現的快捷按鈕（📝 生成檔案摘要、📌 重點整理、📋 列出檔案）。點擊按鈕會自動發送完整問題，比手動輸入更方便，且會自動帶入檔案名稱避免混淆。

**Q: 為什麼列出檔案時不是顯示清單或卡片？**
A: 我們使用 Google ADK Agent 讓 AI 用自然對話方式介紹檔案，而非傳統的條列式清單或卡片。這樣的呈現更友善、更像真人對話，使用者體驗更好。AI 會根據檔案數量智能調整說明方式。

**Q: 如何自訂 Quick Reply 按鈕的文字？**
A: 在 `main.py` 的 `handle_document_message()` 函數中可以修改 Quick Reply 的設定。你可以調整按鈕的 `label`（顯示文字）和 `text`（發送內容）。

## 🔧 進階設定

### 修改 AI 模型

在 `main.py` 第 51 行可以修改使用的模型：

```python
MODEL_NAME = "gemini-2.5-flash"  # 可改成其他 Gemini 模型
```

### 調整文件查詢的回應溫度

在 `main.py` 約第 220 行可以調整 AI 的創意程度：

```python
temperature=0.7,  # 0.0 = 保守精確, 1.0 = 創意發散
```

### 自訂圖片分析的提示詞

在 `main.py` 約第 270 行可以修改圖片分析的提示：

```python
contents=["請詳細描述這張圖片的內容，包括主要物品、場景、文字等資訊。", image],
```

可以改成：
- `"請用英文描述這張圖片"` - 英文回應
- `"這張圖片中有哪些文字？"` - 專注於 OCR
- `"這張圖片的主題是什麼？"` - 摘要式回應

### 自訂 Quick Reply 按鈕

在 `main.py` 的檔案上傳成功處理部分（約第 447-452 行）：

```python
quick_reply = QuickReply(items=[
    QuickReplyButton(action=MessageAction(
        label="📝 生成檔案摘要",
        text=f"請幫我生成「{file_name}」這個檔案的摘要"
    )),
    QuickReplyButton(action=MessageAction(
        label="📌 重點整理",
        text=f"請幫我整理「{file_name}」的重點"
    )),
    QuickReplyButton(action=MessageAction(
        label="📋 列出檔案",
        text="列出檔案"
    )),
])
```

你可以：
- 修改 `label` 來改變按鈕顯示文字
- 修改 `text` 來改變點擊後發送的內容
- 新增或移除按鈕（LINE 限制最多 13 個）
- 使用 `{file_name}` 變數來自動帶入檔案名稱

### 自訂 FileManagerAgent 的語氣和風格

在 `file_manager_agent/agent.py` 中修改 agent instruction（約第 24-33 行）：

```python
instruction="""你是一個友善的檔案管理助手。

當使用者要求列出檔案時：
1. 使用 list_files tool 來取得檔案清單
2. 用口語化、友善的方式呈現結果
3. 不要使用條列式或表格，用自然的對話方式說明
4. 例如：「我看到你上傳了 3 個檔案唷！首先是『會議記錄.pdf』...」
5. 語氣要輕鬆、親切

回應時請用繁體中文。"""
```

你可以調整：
- **語氣風格**：從「親切」改為「專業」、「幽默」等
- **語言**：改為英文或其他語言
- **呈現方式**：要求 AI 用特定格式（如分類、排序等）
- **細節程度**：決定要說明到多詳細

## 📝 授權條款

MIT License - 歡迎自由使用、修改、分享！

## 🙌 貢獻

歡迎提交 Issue 或 Pull Request！

## 📚 相關連結

### 官方文件
- [Google Gemini File Search 官方文件](https://ai.google.dev/gemini-api/docs/file-search?hl=zh-tw)
- [Google ADK (Agent Development Kit) 文件](https://ai.google.dev/gemini-api/docs/adk)
- [LINE Messaging API 文件](https://developers.line.biz/en/docs/messaging-api/)
- [LINE Messaging API - Quick Reply](https://developers.line.biz/en/docs/messaging-api/using-quick-reply/)
- [LINE Messaging API - Mention Object](https://developers.line.biz/en/reference/messaging-api/#mention-object)
- [FastAPI 文件](https://fastapi.tiangolo.com/)

### 專案文件
- [features.md](./features.md) - 功能開發計畫與路線圖 🔮
- [GROUP_USAGE_GUIDE.md](./GROUP_USAGE_GUIDE.md) - LINE Group 使用完整指南
- [CHANGES_GROUP_SUPPORT.md](./CHANGES_GROUP_SUPPORT.md) - Group 支援變更摘要

---

⭐ 如果這個專案對你有幫助，請給個 Star 支持一下！
