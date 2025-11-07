from fastapi import Request, FastAPI, HTTPException
import os
import sys
import aiohttp
import aiofiles
from pathlib import Path
from typing import Optional

from linebot.models import MessageEvent, TextSendMessage, FileMessage, ImageMessage
from linebot.exceptions import InvalidSignatureError
from linebot.aiohttp_async_http_client import AiohttpAsyncHttpClient
from linebot import AsyncLineBotApi, WebhookParser

# Google GenAI imports
from google import genai
from google.genai import types

# Configuration
USE_VERTEX = os.getenv("GOOGLE_GENAI_USE_VERTEXAI") or "False"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or ""

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
if USE_VERTEX == "True":
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
    if not GOOGLE_CLOUD_PROJECT:
        raise ValueError(
            "Please set GOOGLE_CLOUD_PROJECT via env var or code when USE_VERTEX is true."
        )
    if not GOOGLE_CLOUD_LOCATION:
        raise ValueError(
            "Please set GOOGLE_CLOUD_LOCATION via env var or code when USE_VERTEX is true."
        )
elif not GOOGLE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY via env var or code.")

# Initialize GenAI client
if USE_VERTEX == "True":
    client = genai.Client(
        vertexai=True,
        project=GOOGLE_CLOUD_PROJECT,
        location=GOOGLE_CLOUD_LOCATION,
    )
else:
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
MODEL_NAME = "gemini-2.0-flash-exp"

def get_store_name(event: MessageEvent) -> str:
    """
    Get the file search store name based on the message source.
    Returns user_id for 1-on-1 chat, group_id for group chat.
    """
    if event.source.type == "user":
        return f"user_{event.source.user_id}"
    elif event.source.type == "group":
        return f"group_{event.source.group_id}"
    elif event.source.type == "room":
        return f"room_{event.source.room_id}"
    else:
        return f"unknown_{event.source.user_id}"


async def download_line_content(message_id: str, file_name: str) -> Optional[Path]:
    """
    Download file content from LINE and save to local uploads directory.
    Returns the local file path if successful, None otherwise.
    """
    try:
        # Get message content from LINE
        message_content = await line_bot_api.get_message_content(message_id)

        # Save to local file
        file_path = UPLOAD_DIR / f"{message_id}_{file_name}"

        async with aiofiles.open(file_path, 'wb') as f:
            async for chunk in message_content.iter_content():
                await f.write(chunk)

        print(f"Downloaded file: {file_path}")
        return file_path
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None


async def upload_to_file_search_store(file_path: Path, store_name: str, display_name: Optional[str] = None) -> bool:
    """
    Upload a file to Gemini file search store.
    Returns True if successful, False otherwise.
    """
    try:
        # Upload file to file search store
        upload_config = {
            "name": store_name,
        }
        if display_name:
            upload_config["display_name"] = display_name

        result = client.files.upload_to_file_search_store(
            path=str(file_path),
            config=upload_config
        )

        print(f"File uploaded to store '{store_name}': {result}")
        return True
    except Exception as e:
        print(f"Error uploading to file search store: {e}")
        return False


async def query_file_search(query: str, store_name: str) -> str:
    """
    Query the file search store using generate_content.
    Returns the AI response text.
    """
    try:
        # Create FileSearch tool with store name
        tool = types.Tool(
            file_search=types.FileSearch(
                file_search_store_names=[store_name]
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

        # Extract text from response
        if response.text:
            return response.text
        else:
            return "抱歉，我無法從文件中找到相關資訊。"

    except Exception as e:
        print(f"Error querying file search: {e}")
        return f"查詢時發生錯誤：{str(e)}"


async def handle_file_message(event: MessageEvent, message):
    """
    Handle file and image messages - download and upload to file search store.
    """
    store_name = get_store_name(event)

    # Determine file name
    if isinstance(message, FileMessage):
        file_name = message.file_name or "unknown_file"
        message_type = "檔案"
    elif isinstance(message, ImageMessage):
        file_name = f"image_{message.id}.jpg"
        message_type = "圖片"
    else:
        return

    # Download file
    reply_msg = TextSendMessage(text=f"正在處理您的{message_type}，請稍候...")
    await line_bot_api.reply_message(event.reply_token, reply_msg)

    file_path = await download_line_content(message.id, file_name)

    if file_path is None:
        error_msg = TextSendMessage(text=f"{message_type}下載失敗，請重試。")
        await line_bot_api.push_message(event.source.user_id, error_msg)
        return

    # Upload to file search store
    success = await upload_to_file_search_store(file_path, store_name, file_name)

    # Clean up local file
    try:
        file_path.unlink()
    except Exception as e:
        print(f"Error deleting file: {e}")

    if success:
        success_msg = TextSendMessage(
            text=f"✅ {message_type}已成功上傳！\n檔案名稱：{file_name}\n\n現在您可以詢問我關於這個{message_type}的任何問題。"
        )
        await line_bot_api.push_message(event.source.user_id, success_msg)
    else:
        error_msg = TextSendMessage(text=f"{message_type}上傳失敗，請重試。")
        await line_bot_api.push_message(event.source.user_id, error_msg)


async def handle_text_message(event: MessageEvent, message):
    """
    Handle text messages - query the file search store.
    """
    store_name = get_store_name(event)
    query = message.text

    print(f"Received query: {query} for store: {store_name}")

    # Query file search
    response_text = await query_file_search(query, store_name)

    # Reply to user
    reply_msg = TextSendMessage(text=response_text)
    await line_bot_api.reply_message(event.reply_token, reply_msg)


@app.post("/")
async def handle_callback(request: Request):
    signature = request.headers["X-Line-Signature"]

    # Get request body as text
    body = await request.body()
    body = body.decode()

    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if not isinstance(event, MessageEvent):
            continue

        if event.message.type == "text":
            # Process text message
            await handle_text_message(event, event.message)
        elif event.message.type == "file":
            # Process file message
            await handle_file_message(event, event.message)
        elif event.message.type == "image":
            # Process image message
            await handle_file_message(event, event.message)
        else:
            continue

    return "OK"


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    await client_session.close()
