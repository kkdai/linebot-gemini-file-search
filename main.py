from fastapi import Request, FastAPI, HTTPException
import os
import sys
import asyncio
import aiohttp
import aiofiles
import urllib.parse
from pathlib import Path
from typing import Optional

from linebot.models import (
    MessageEvent, TextSendMessage, FileMessage, ImageMessage,
    PostbackEvent, TemplateSendMessage, CarouselTemplate, CarouselColumn,
    PostbackAction, QuickReply, QuickReplyButton, MessageAction,
    FlexSendMessage, BubbleContainer, BoxComponent, TextComponent,
    ButtonComponent, SeparatorComponent, CarouselContainer
)
from linebot.exceptions import InvalidSignatureError
from linebot.aiohttp_async_http_client import AiohttpAsyncHttpClient
from linebot import AsyncLineBotApi, WebhookParser

# Google GenAI imports
from google import genai
from google.genai import types

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or ""

# Supported file formats for Google AI File Search API
# Reference: https://ai.google.dev/gemini-api/docs/file-upload
SUPPORTED_FILE_EXTENSIONS = {
    '.pdf', '.txt', '.docx', '.html', '.htm', '.md',
    '.csv', '.xml', '.rtf'
}

# File format warnings
UNSUPPORTED_FORMAT_MESSAGE = """
⚠️ 檔案格式不支援

您上傳的檔案格式「{extension}」目前不被支援。

✅ 支援的格式：
• PDF (.pdf)
• Word 文件 (.docx)
• 純文字 (.txt)
• Markdown (.md)
• HTML (.html, .htm)
• CSV (.csv)
• RTF (.rtf)

💡 建議：
如果您的檔案是 .doc 格式，請先轉換成 .docx 格式後再上傳。
您可以使用 Microsoft Word 開啟檔案後，選擇「另存新檔」並選擇 .docx 格式。
"""

# LINE Bot configuration
channel_secret = os.getenv("ChannelSecret", None)
channel_access_token = os.getenv("ChannelAccessToken", None)

# Validate environment variables
if channel_secret is None:
    print("Specify ChannelSecret as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify ChannelAccessToken as environment variable.")
    sys.exit(1)
if not GOOGLE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY via env var or code.")

# Initialize GenAI client (Note: File Search API only supports Gemini API, not VertexAI)
client = genai.Client(api_key=GOOGLE_API_KEY)

print("GenAI client initialized successfully.")

# Initialize the FastAPI app for LINEBot
app = FastAPI()
client_session = aiohttp.ClientSession()
async_http_client = AiohttpAsyncHttpClient(client_session)
line_bot_api = AsyncLineBotApi(channel_access_token, async_http_client)
parser = WebhookParser(channel_secret)

# Create uploads directory if not exists
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Model configuration
MODEL_NAME = "gemini-2.5-flash"

def get_store_name(event) -> str:
    """
    Get the file search store name based on the event source.
    Returns user_id for 1-on-1 chat, group_id for group chat.
    Works with both MessageEvent and PostbackEvent.
    """
    if event.source.type == "user":
        return f"user_{event.source.user_id}"
    elif event.source.type == "group":
        return f"group_{event.source.group_id}"
    elif event.source.type == "room":
        return f"room_{event.source.room_id}"
    else:
        return f"unknown_{event.source.user_id}"


def get_reply_target(event: MessageEvent) -> str:
    """
    Get the correct reply target ID based on the message source.
    Returns group_id for group chat, user_id for 1-on-1 chat.
    """
    if event.source.type == "group":
        return event.source.group_id
    elif event.source.type == "room":
        return event.source.room_id
    else:
        return event.source.user_id


def is_bot_mentioned(event: MessageEvent, bot_user_id: str) -> bool:
    """
    Check if the bot is mentioned in a group/room message.
    Returns True for 1-on-1 chat, or if bot is mentioned in group/room.

    Args:
        event: MessageEvent from LINE webhook
        bot_user_id: Bot's user ID (from webhook body's 'destination' field)
    """
    print(f"[DEBUG] is_bot_mentioned called, bot_user_id: {bot_user_id}")
    print(f"[DEBUG] event.source.type: {event.source.type}")

    # In 1-on-1 chat, always respond
    if event.source.type == "user":
        print(f"[DEBUG] 1-on-1 chat detected, returning True")
        return True

    # In group/room, check if bot is mentioned
    print(f"[DEBUG] Group/room chat detected")
    print(f"[DEBUG] hasattr(event.message, 'mention'): {hasattr(event.message, 'mention')}")

    if hasattr(event.message, 'mention'):
        print(f"[DEBUG] event.message.mention: {event.message.mention}")
        if event.message.mention:
            mentionees = event.message.mention.mentionees
            print(f"[DEBUG] Number of mentionees: {len(mentionees) if mentionees else 0}")

            if mentionees:
                for i, mentionee in enumerate(mentionees):
                    print(f"[DEBUG] Mentionee {i}:")
                    print(f"[DEBUG]   type: {type(mentionee)}")
                    print(f"[DEBUG]   hasattr user_id: {hasattr(mentionee, 'user_id')}")
                    if hasattr(mentionee, 'user_id'):
                        print(f"[DEBUG]   user_id value: {mentionee.user_id}")
                        print(f"[DEBUG]   Comparing with bot_user_id: {bot_user_id}")

                    # Check if this mention is for the bot by comparing user_id
                    # LINE SDK's Mentionee doesn't have isSelf attribute, so we compare user_id directly
                    if hasattr(mentionee, 'user_id') and mentionee.user_id == bot_user_id:
                        print(f"[DEBUG] Bot mentioned! (user_id matches)")
                        return True

    print(f"[DEBUG] Bot not mentioned, returning False")
    return False


async def download_line_content(message_id: str, file_name: str) -> Optional[Path]:
    """
    Download file content from LINE and save to local uploads directory.
    Returns the local file path if successful, None otherwise.
    """
    try:
        # Get message content from LINE
        message_content = await line_bot_api.get_message_content(message_id)

        # Extract file extension from original file name
        _, ext = os.path.splitext(file_name)
        # Use safe file name (ASCII only) to avoid encoding issues
        safe_file_name = f"{message_id}{ext}"
        file_path = UPLOAD_DIR / safe_file_name

        async with aiofiles.open(file_path, 'wb') as f:
            async for chunk in message_content.iter_content():
                await f.write(chunk)

        print(f"Downloaded file: {file_path} (original: {file_name})")
        return file_path
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None


def is_supported_file_format(file_name: str) -> tuple[bool, str]:
    """
    Check if the file format is supported by Google AI File Search API.
    Returns (is_supported, file_extension).
    """
    _, ext = os.path.splitext(file_name.lower())
    return (ext in SUPPORTED_FILE_EXTENSIONS, ext)


async def ensure_file_search_store_exists(store_name: str) -> tuple[bool, str]:
    """
    Ensure file search store exists, create if not.
    Returns (success, actual_store_name).
    Note: store_name is used as display_name, but actual name is auto-generated by API.
    """
    try:
        # List all stores and check if one with our display_name exists
        stores = client.file_search_stores.list()
        for store in stores:
            if hasattr(store, 'display_name') and store.display_name == store_name:
                print(f"File search store '{store_name}' already exists: {store.name}")
                return True, store.name

        # Store doesn't exist, create it
        print(f"Creating file search store with display_name '{store_name}'...")
        store = client.file_search_stores.create(
            config={'display_name': store_name}
        )
        print(f"File search store created: {store.name} (display_name: {store_name})")
        return True, store.name

    except Exception as e:
        print(f"Error ensuring file search store exists: {e}")
        return False, ""


# Cache to store display_name -> actual_name mapping
store_name_cache = {}

# Cache to store citations/grounding metadata for each user/group
# Key: store_name, Value: list of grounding chunks
citations_cache = {}


async def list_documents_in_store(store_name: str) -> list:
    """
    List all documents in a file search store.
    Returns list of document info dicts.
    """
    try:
        print(f"[DEBUG] list_documents_in_store called with store_name: {store_name}")

        # Get actual store name
        actual_store_name = None
        if store_name in store_name_cache:
            actual_store_name = store_name_cache[store_name]
            print(f"[DEBUG] Found in cache: {actual_store_name}")
        else:
            # Find store by display_name
            print(f"[DEBUG] Not in cache, searching for store with display_name: {store_name}")
            stores = client.file_search_stores.list()
            print(f"[DEBUG] Total stores found: {len(list(stores))}")

            stores = client.file_search_stores.list()  # Re-list because iterator consumed
            for store in stores:
                store_display_name = getattr(store, 'display_name', None)
                print(f"[DEBUG] Checking store: {store.name}, display_name: {store_display_name}")
                if hasattr(store, 'display_name') and store.display_name == store_name:
                    actual_store_name = store.name
                    store_name_cache[store_name] = actual_store_name
                    print(f"[DEBUG] Found matching store: {actual_store_name}")
                    break

        if not actual_store_name:
            print(f"[DEBUG] Store '{store_name}' not found - returning empty list")
            return []

        print(f"[DEBUG] Using store: {actual_store_name}")

        documents = []

        # Use REST API to list documents (more stable than SDK)
        print(f"[DEBUG] Using REST API to list documents")
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/{actual_store_name}/documents"
        headers = {'Content-Type': 'application/json'}
        params = {'key': GOOGLE_API_KEY}

        print(f"[DEBUG] REST API URL: {url}")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"[DEBUG] REST API returned {len(data.get('documents', []))} documents")

        for doc in data.get('documents', []):
            documents.append({
                'name': doc.get('name', 'N/A'),
                'display_name': doc.get('displayName', 'Unknown'),
                'create_time': doc.get('createTime', ''),
                'update_time': doc.get('updateTime', '')
            })
            print(f"[DEBUG] File found in store '{store_name}': {doc.get('displayName', 'Unknown')}")

        print(f"[DEBUG] Returning {len(documents)} documents")
        return documents

    except Exception as e:
        print(f"[ERROR] Error listing documents in store: {e}")
        import traceback
        traceback.print_exc()
        return []


async def delete_document(document_name: str) -> bool:
    """
    Delete a document from file search store.
    Returns True if successful, False otherwise.
    Note: force=True is required to permanently delete documents from File Search Store.
    """
    try:
        # Try to use SDK method first with force=True
        try:
            if hasattr(client.file_search_stores, 'documents'):
                # Force delete is required for File Search Store documents
                client.file_search_stores.documents.delete(
                    name=document_name,
                    config={'force': True}
                )
                print(f"Document deleted successfully with force=True: {document_name}")
                return True
        except Exception as sdk_error:
            print(f"SDK delete failed, trying REST API: {sdk_error}")

        # Fallback to REST API with force parameter
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/{document_name}"
        headers = {'Content-Type': 'application/json'}
        params = {
            'key': GOOGLE_API_KEY,
            'force': 'true'  # Required for File Search Store documents
        }

        response = requests.delete(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        print(f"Document deleted successfully via REST API with force=true: {document_name}")
        return True

    except Exception as e:
        print(f"Error deleting document: {e}")
        return False


async def upload_to_file_search_store(file_path: Path, store_name: str, display_name: Optional[str] = None) -> bool:
    """
    Upload a file to Gemini file search store.
    Returns True if successful, False otherwise.
    """
    try:
        # Check cache first
        if store_name in store_name_cache:
            actual_store_name = store_name_cache[store_name]
            print(f"Using cached store name: {actual_store_name}")
        else:
            # Ensure the store exists before uploading
            success, actual_store_name = await ensure_file_search_store_exists(store_name)
            if not success:
                print(f"Failed to ensure store '{store_name}' exists")
                return False
            # Cache the mapping
            store_name_cache[store_name] = actual_store_name

        # Upload to file search store
        # actual_store_name is the API-generated name (e.g., fileSearchStores/xxx)
        # display_name is the custom display name for the file (used in citations)
        config_dict = {}
        if display_name:
            config_dict['display_name'] = display_name

        operation = client.file_search_stores.upload_to_file_search_store(
            file_search_store_name=actual_store_name,
            file=str(file_path),
            config=config_dict if config_dict else None
        )

        # Wait for operation to complete (with timeout)
        max_wait = 60  # seconds
        elapsed = 0
        while not operation.done and elapsed < max_wait:
            await asyncio.sleep(2)
            operation = client.operations.get(operation)
            elapsed += 2

        if operation.done:
            print(f"File uploaded to store '{store_name}': {operation}")
            return True
        else:
            print(f"Upload operation timeout for store '{store_name}'")
            return False

    except Exception as e:
        error_msg = str(e)
        print(f"Error uploading to file search store: {error_msg}")

        # Check if it's a file format related error
        if '500' in error_msg or 'INTERNAL' in error_msg:
            print(f"[WARNING] Possible unsupported file format or corrupted file: {file_path}")
            print(f"[INFO] File extension: {file_path.suffix}")

        return False


async def query_file_search(query: str, store_name: str) -> tuple[str, list]:
    """
    Query the file search store using generate_content.
    Returns (AI response text, list of citations).
    """
    try:
        # Get actual store name from cache or by searching
        actual_store_name = None

        if store_name in store_name_cache:
            actual_store_name = store_name_cache[store_name]
            print(f"Using cached store name for query: {actual_store_name}")
        else:
            # Try to find the store by display_name
            try:
                stores = client.file_search_stores.list()
                for store in stores:
                    if hasattr(store, 'display_name') and store.display_name == store_name:
                        actual_store_name = store.name
                        store_name_cache[store_name] = actual_store_name
                        print(f"Found store for query: {actual_store_name}")
                        break
            except Exception as list_error:
                print(f"Error listing stores: {list_error}")

        if not actual_store_name:
            # Store doesn't exist - guide user to upload files
            print(f"File search store '{store_name}' not found")
            return ("📁 您還沒有上傳任何檔案。\n\n請先傳送文件檔案（PDF、DOCX、TXT 等）給我，上傳完成後就可以開始提問了！\n\n💡 提示：如果您想分析圖片，請直接傳送圖片給我，我會立即為您分析。", [])

        # Create FileSearch tool with actual store name
        tool = types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[actual_store_name]
            )
        )

        # Generate content with file search
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=query,
            config=types.GenerateContentConfig(
                tools=[tool],
                temperature=0.7,
            )
        )

        # Extract grounding metadata (citations)
        citations = []
        try:
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    grounding_chunks = candidate.grounding_metadata.grounding_chunks
                    for chunk in grounding_chunks:
                        if hasattr(chunk, 'web') and chunk.web:
                            # Web source
                            citations.append({
                                'type': 'web',
                                'title': getattr(chunk.web, 'title', 'Unknown'),
                                'uri': getattr(chunk.web, 'uri', ''),
                            })
                        elif hasattr(chunk, 'retrieved_context') and chunk.retrieved_context:
                            # File search source
                            citations.append({
                                'type': 'file',
                                'title': getattr(chunk.retrieved_context, 'title', 'Unknown'),
                                'text': getattr(chunk.retrieved_context, 'text', '')[:500],  # Limit to 500 chars
                            })
            print(f"Found {len(citations)} citations")
        except Exception as citation_error:
            print(f"Error extracting citations: {citation_error}")

        # Extract text from response
        if response.text:
            return (response.text, citations)
        else:
            return ("抱歉，我無法從文件中找到相關資訊。", [])

    except Exception as e:
        print(f"Error querying file search: {e}")
        # Check if error is related to missing store
        if "not found" in str(e).lower() or "does not exist" in str(e).lower():
            return ("📁 您還沒有上傳任何檔案。\n\n請先傳送文件檔案（PDF、DOCX、TXT 等）給我，上傳完成後就可以開始提問了！\n\n💡 提示：如果您想分析圖片，請直接傳送圖片給我，我會立即為您分析。", [])
        return (f"查詢時發生錯誤：{str(e)}", [])


async def analyze_image_with_gemini(image_path: Path) -> str:
    """
    Analyze image using Gemini's vision capability.
    Returns the analysis result text.
    """
    try:
        # Read image bytes
        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        # Determine MIME type based on file extension
        ext = image_path.suffix.lower()
        mime_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        mime_type = mime_type_map.get(ext, 'image/jpeg')

        # Create image part
        image = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type
        )

        # Generate content with image
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=["請詳細描述這張圖片的內容，包括主要物品、場景、文字等資訊。", image],
        )

        if response.text:
            return response.text
        else:
            return "抱歉，我無法分析這張圖片。"

    except Exception as e:
        print(f"Error analyzing image with Gemini: {e}")
        return f"圖片分析時發生錯誤：{str(e)}"


async def handle_image_message(event: MessageEvent, message: ImageMessage):
    """
    Handle image messages - analyze using Gemini vision.
    """
    reply_target = get_reply_target(event)
    file_name = f"image_{message.id}.jpg"

    # Download image
    reply_msg = TextSendMessage(text="正在分析您的圖片，請稍候...")
    await line_bot_api.reply_message(event.reply_token, reply_msg)

    file_path = await download_line_content(message.id, file_name)

    if file_path is None:
        error_msg = TextSendMessage(text="圖片下載失敗，請重試。")
        await line_bot_api.push_message(reply_target, error_msg)
        return

    # Analyze image with Gemini
    analysis_result = await analyze_image_with_gemini(file_path)

    # Clean up local file
    try:
        file_path.unlink()
    except Exception as e:
        print(f"Error deleting file: {e}")

    # Send analysis result
    result_msg = TextSendMessage(text=f"📸 圖片分析結果：\n\n{analysis_result}")
    await line_bot_api.push_message(reply_target, result_msg)


async def handle_document_message(event: MessageEvent, message: FileMessage):
    """
    Handle file messages - download and upload to file search store.
    """
    store_name = get_store_name(event)
    reply_target = get_reply_target(event)
    file_name = message.file_name or "unknown_file"

    # Check file format before processing
    is_supported, file_ext = is_supported_file_format(file_name)
    if not is_supported:
        # Send unsupported format message
        error_msg = TextSendMessage(text=UNSUPPORTED_FORMAT_MESSAGE.format(extension=file_ext))
        await line_bot_api.reply_message(event.reply_token, error_msg)
        print(f"[WARNING] Unsupported file format: {file_name} ({file_ext})")
        return

    # Download file
    reply_msg = TextSendMessage(text="正在處理您的檔案，請稍候...")
    await line_bot_api.reply_message(event.reply_token, reply_msg)

    file_path = await download_line_content(message.id, file_name)

    if file_path is None:
        error_msg = TextSendMessage(text="檔案下載失敗，請重試。")
        await line_bot_api.push_message(reply_target, error_msg)
        return

    # Upload to file search store
    success = await upload_to_file_search_store(file_path, store_name, file_name)

    # Clean up local file
    try:
        file_path.unlink()
    except Exception as e:
        print(f"Error deleting file: {e}")

    if success:
        # Create Quick Reply buttons for common actions with specific file name
        # Using Postback instead of MessageAction for better Group chat support
        quick_reply = QuickReply(items=[
            QuickReplyButton(action=PostbackAction(
                label="📝 生成檔案摘要",
                data=f"action=query&prompt={urllib.parse.quote(f'請幫我生成「{file_name}」這個檔案的摘要')}"
            )),
            QuickReplyButton(action=PostbackAction(
                label="📌 重點整理",
                data=f"action=query&prompt={urllib.parse.quote(f'請幫我整理「{file_name}」的重點')}"
            )),
            QuickReplyButton(action=PostbackAction(
                label="📋 列出檔案",
                data="action=list_files"
            )),
        ])

        success_msg = TextSendMessage(
            text=f"✅ 檔案已成功上傳！\n檔案名稱：{file_name}\n\n現在您可以詢問我關於這個檔案的任何問題。",
            quick_reply=quick_reply
        )
        await line_bot_api.push_message(reply_target, success_msg)
    else:
        # Provide more helpful error message
        error_text = f"""❌ 檔案上傳失敗

檔案名稱：{file_name}

可能的原因：
1. 檔案格式可能有問題或檔案已損壞
2. 網路連線問題
3. 檔案過大

請嘗試：
• 確認檔案可以正常開啟
• 如果是 .doc 格式，請轉換成 .docx
• 稍後重試
"""
        error_msg = TextSendMessage(text=error_text)
        await line_bot_api.push_message(reply_target, error_msg)


def is_list_files_intent(text: str) -> bool:
    """
    Check if user wants to list files.
    """
    list_keywords = [
        '列出檔案', '列出文件', '顯示檔案', '顯示文件',
        '查看檔案', '查看文件', '檔案列表', '文件列表',
        '有哪些檔案', '有哪些文件', '我的檔案', '我的文件',
        'list files', 'show files', 'my files'
    ]
    text_lower = text.lower().strip()
    return any(keyword in text_lower for keyword in list_keywords)


async def send_files_carousel(event, documents: list, page: int = 1, store_name: str = ""):
    """
    Send files as LINE Flex Message Carousel with pagination.
    Works with both MessageEvent and PostbackEvent.

    Args:
        event: MessageEvent or PostbackEvent with reply_token
        documents: List of document dicts with 'name', 'display_name', 'create_time'
        page: Current page number (1-indexed)
        store_name: Store name for pagination postback actions
    """
    if not documents:
        no_files_msg = TextSendMessage(text="📁 目前沒有任何文件。\n\n請先上傳文件檔案，就可以查詢囉！")
        await line_bot_api.reply_message(event.reply_token, no_files_msg)
        return

    # 分頁設定：每頁最多 11 個檔案，第 12 個位置留給分頁控制
    page_size = 11
    total_docs = len(documents)
    total_pages = (total_docs + page_size - 1) // page_size  # 向上取整

    # 計算當前頁的檔案範圍
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_docs)
    current_page_docs = documents[start_idx:end_idx]

    print(f"[DEBUG] Pagination: page={page}, total_docs={total_docs}, total_pages={total_pages}")
    print(f"[DEBUG] Showing documents {start_idx+1} to {end_idx}")

    bubbles = []
    for doc in current_page_docs:
        # 提取檔名（去除路徑部分）
        display_name = doc.get('display_name', 'Unknown')
        # 格式化時間
        create_time = doc.get('create_time', '')
        if create_time and 'T' in create_time:
            # 簡化時間顯示 (YYYY-MM-DD HH:MM)
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
                create_time = dt.strftime('%Y-%m-%d %H:%M')
            except:
                create_time = create_time[:16]  # 簡單截斷

        # 建立每個檔案的 Bubble
        bubble = BubbleContainer(
            body=BoxComponent(
                layout='vertical',
                contents=[
                    # 檔案圖示
                    TextComponent(
                        text='📄',
                        size='xxl',
                        align='center',
                        margin='md'
                    ),
                    # 檔案名稱
                    TextComponent(
                        text=display_name[:40],  # 限制長度
                        weight='bold',
                        size='lg',
                        align='center',
                        wrap=True,
                        margin='md'
                    ),
                    # 分隔線
                    SeparatorComponent(margin='md'),
                    # 上傳時間
                    TextComponent(
                        text=f"上傳時間\n{create_time}" if create_time else "文件檔案",
                        size='sm',
                        color='#999999',
                        align='center',
                        wrap=True,
                        margin='md'
                    )
                ],
                padding_all='lg'
            ),
            footer=BoxComponent(
                layout='vertical',
                contents=[
                    # 刪除按鈕
                    ButtonComponent(
                        action=PostbackAction(
                            label='🗑️ 刪除檔案',
                            data=f"action=delete_file&doc_name={doc['name']}"
                        ),
                        style='primary',
                        color='#e74c3c',
                        height='sm'
                    )
                ],
                padding_all='sm'
            )
        )
        bubbles.append(bubble)

    # 加入分頁控制 bubble (如果有多頁)
    if total_pages > 1:
        # 建立分頁按鈕
        pagination_buttons = []

        # 上一頁按鈕 (如果不是第一頁)
        if page > 1:
            pagination_buttons.append(
                ButtonComponent(
                    action=PostbackAction(
                        label='⬅️ 上一頁',
                        data=f"action=list_files&page={page-1}&store={urllib.parse.quote(store_name)}"
                    ),
                    style='secondary',
                    color='#95a5a6',
                    height='sm'
                )
            )

        # 下一頁按鈕 (如果不是最後一頁)
        if page < total_pages:
            pagination_buttons.append(
                ButtonComponent(
                    action=PostbackAction(
                        label='下一頁 ➡️',
                        data=f"action=list_files&page={page+1}&store={urllib.parse.quote(store_name)}"
                    ),
                    style='primary',
                    color='#3498db',
                    height='sm'
                )
            )

        # 建立分頁控制 bubble
        pagination_bubble = BubbleContainer(
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(
                        text='📄',
                        size='xxl',
                        align='center',
                        margin='md'
                    ),
                    TextComponent(
                        text='頁面導航',
                        weight='bold',
                        size='lg',
                        align='center',
                        margin='md'
                    ),
                    SeparatorComponent(margin='md'),
                    TextComponent(
                        text=f'第 {page} / {total_pages} 頁',
                        size='sm',
                        color='#999999',
                        align='center',
                        margin='md'
                    ),
                    TextComponent(
                        text=f'共 {total_docs} 個檔案',
                        size='xs',
                        color='#999999',
                        align='center',
                        margin='sm'
                    )
                ],
                padding_all='lg'
            ),
            footer=BoxComponent(
                layout='vertical',
                contents=pagination_buttons,
                spacing='sm',
                padding_all='sm'
            )
        )
        bubbles.append(pagination_bubble)

    # 建立 Carousel Container
    carousel_container = CarouselContainer(contents=bubbles)

    # 建立 Flex Message
    flex_message = FlexSendMessage(
        alt_text=f'📁 找到 {total_docs} 個文件 (第 {page}/{total_pages} 頁)',
        contents=carousel_container
    )

    await line_bot_api.reply_message(event.reply_token, flex_message)


async def handle_postback(event: PostbackEvent):
    """
    Handle postback events from Quick Reply buttons and other interactions.
    Supports: delete_file, query, list_files, view_citation
    """
    try:
        # Parse postback data
        data = event.postback.data
        params = dict(param.split('=', 1) for param in data.split('&'))

        action = params.get('action')
        print(f"[DEBUG] Postback action: {action}")

        # Get store name for operations
        store_name = get_store_name(event)

        if action == 'delete_file':
            # Handle delete file action
            doc_name = params.get('doc_name')
            if doc_name:
                success = await delete_document(doc_name)

                if success:
                    reply_msg = TextSendMessage(
                        text=f"✅ 檔案已刪除成功！\n\n如需查看剩餘檔案，請點擊下方按鈕。"
                    )
                else:
                    reply_msg = TextSendMessage(text="❌ 刪除檔案失敗，請稍後再試。")

                await line_bot_api.reply_message(event.reply_token, reply_msg)

        elif action == 'query':
            # Handle file query from Quick Reply
            prompt = urllib.parse.unquote(params.get('prompt', ''))
            print(f"[DEBUG] Query prompt: {prompt}")

            if prompt:
                # Query file search
                response_text, citations = await query_file_search(prompt, store_name)

                # Store citations in cache
                if citations:
                    citations_cache[store_name] = citations[:3]
                    print(f"Stored {len(citations_cache[store_name])} citations for {store_name}")

                # Create Quick Reply buttons for citations
                quick_reply = None
                if citations:
                    quick_reply_items = []
                    for i, citation in enumerate(citations[:3], 1):
                        quick_reply_items.append(
                            QuickReplyButton(action=PostbackAction(
                                label=f"📖 引用{i}",
                                data=f"action=view_citation&num={i}"
                            ))
                        )
                    quick_reply = QuickReply(items=quick_reply_items)

                # Reply to user
                reply_msg = TextSendMessage(text=response_text, quick_reply=quick_reply)
                await line_bot_api.reply_message(event.reply_token, reply_msg)
            else:
                reply_msg = TextSendMessage(text="查詢內容不能為空。")
                await line_bot_api.reply_message(event.reply_token, reply_msg)

        elif action == 'list_files':
            # Handle list files request - show carousel with delete buttons
            # Parse pagination parameters
            page = int(params.get('page', 1))
            store = urllib.parse.unquote(params.get('store', store_name))

            print(f"[DEBUG] Postback list_files action for store: {store}, page: {page}")
            documents = await list_documents_in_store(store)
            print(f"[DEBUG] Postback list_documents_in_store returned {len(documents)} documents")
            await send_files_carousel(event, documents, page=page, store_name=store)

        elif action == 'view_citation':
            # Handle view citation request
            citation_num = int(params.get('num', 0))
            print(f"[DEBUG] View citation {citation_num} for store: {store_name}")

            if store_name in citations_cache and 0 < citation_num <= len(citations_cache[store_name]):
                citation = citations_cache[store_name][citation_num - 1]

                # Format citation text
                if citation['type'] == 'file':
                    citation_text = f"📖 引用 {citation_num}\n\n"
                    citation_text += f"📄 文件：{citation['title']}\n\n"
                    citation_text += f"📝 內容：\n{citation['text']}"
                    if len(citation.get('text', '')) >= 500:
                        citation_text += "\n\n... (內容過長，已截斷)"
                elif citation['type'] == 'web':
                    citation_text = f"📖 引用 {citation_num}\n\n"
                    citation_text += f"🌐 來源：{citation['title']}\n"
                    citation_text += f"🔗 連結：{citation['uri']}"
                else:
                    citation_text = "無法顯示此引用。"

                reply_msg = TextSendMessage(text=citation_text)
                await line_bot_api.reply_message(event.reply_token, reply_msg)
            else:
                reply_msg = TextSendMessage(text="找不到此引用，請重新查詢。")
                await line_bot_api.reply_message(event.reply_token, reply_msg)

        else:
            print(f"Unknown postback action: {action}")
            reply_msg = TextSendMessage(text="未知的操作。")
            await line_bot_api.reply_message(event.reply_token, reply_msg)

    except Exception as e:
        print(f"Error handling postback: {e}")
        import traceback
        traceback.print_exc()
        error_msg = TextSendMessage(text="處理操作時發生錯誤。")
        await line_bot_api.reply_message(event.reply_token, error_msg)


async def handle_text_message(event: MessageEvent, message, bot_user_id: str = ''):
    """
    Handle text messages - query the file search store or list files.
    Only responds in groups if bot is mentioned.

    Args:
        event: MessageEvent from LINE webhook
        message: Message object
        bot_user_id: Bot's user ID for mention checking
    """
    # In group/room, only respond if bot is mentioned
    if not is_bot_mentioned(event, bot_user_id):
        print(f"Bot not mentioned in group/room, skipping response")
        return

    store_name = get_store_name(event)
    query = message.text

    print(f"Received query: {query} for store: {store_name}")

    # Note: Citation viewing is now handled by Postback actions
    # The Quick Reply buttons trigger postback events instead of text messages

    # Check if user wants to list files
    if is_list_files_intent(query):
        print(f"[DEBUG] List files intent detected for query: {query}")
        print(f"[DEBUG] Store name: {store_name}")
        # Show files carousel with delete buttons
        documents = await list_documents_in_store(store_name)
        print(f"[DEBUG] list_documents_in_store returned {len(documents)} documents")
        await send_files_carousel(event, documents, page=1, store_name=store_name)
        return

    # Otherwise, query file search
    response_text, citations = await query_file_search(query, store_name)

    # Store citations in cache (limit to 3 for Quick Reply)
    if citations:
        citations_cache[store_name] = citations[:3]
        print(f"Stored {len(citations_cache[store_name])} citations for {store_name}")

    # Create Quick Reply buttons for citations
    # Using Postback instead of MessageAction for better Group chat support
    quick_reply = None
    if citations:
        quick_reply_items = []
        for i, citation in enumerate(citations[:3], 1):  # Limit to 3 citations
            quick_reply_items.append(
                QuickReplyButton(action=PostbackAction(
                    label=f"📖 引用{i}",
                    data=f"action=view_citation&num={i}"
                ))
            )
        quick_reply = QuickReply(items=quick_reply_items)

    # Reply to user
    reply_msg = TextSendMessage(text=response_text, quick_reply=quick_reply)
    await line_bot_api.reply_message(event.reply_token, reply_msg)


@app.post("/")
async def handle_callback(request: Request):
    signature = request.headers["X-Line-Signature"]

    # Get request body as text
    body = await request.body()
    body = body.decode()

    # Log webhook body for debugging
    print("[DEBUG] ===== Webhook Request =====")
    print(f"[DEBUG] Body: {body}")
    print("[DEBUG] ===========================")

    # Parse body to get bot user ID (destination)
    import json
    try:
        body_json = json.loads(body)
        bot_user_id = body_json.get('destination', '')
        print(f"[DEBUG] Bot User ID (destination): {bot_user_id}")
    except json.JSONDecodeError:
        print("[ERROR] Failed to parse webhook body JSON")
        bot_user_id = ''

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        print(f"[DEBUG] Event type: {type(event).__name__}")
        print(f"[DEBUG] Event source type: {event.source.type if hasattr(event, 'source') else 'N/A'}")
        # Handle PostbackEvent (e.g., delete file button clicks)
        if isinstance(event, PostbackEvent):
            await handle_postback(event)
        # Handle MessageEvent
        elif isinstance(event, MessageEvent):
            if event.message.type == "text":
                # Process text message (pass bot_user_id for mention checking)
                await handle_text_message(event, event.message, bot_user_id)
            elif event.message.type == "file":
                # Process file message (upload to file search store)
                await handle_document_message(event, event.message)
            elif event.message.type == "image":
                # Process image message (analyze with Gemini vision)
                await handle_image_message(event, event.message)
            else:
                continue
        else:
            continue

    return "OK"


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    await client_session.close()
