"""
Chat Session Manager for Google ADK Chat Sessions.

Manages conversation memory and context for each user.
"""

from google import genai
from google.genai import types
from datetime import datetime, timedelta
from typing import Optional, Dict


class ChatSessionManager:
    """
    Manages Google ADK Chat Sessions for multiple users.

    Features:
    - Per-user session management
    - Automatic session timeout (1 hour)
    - Optional File Search tool integration
    - Session cleanup
    """

    def __init__(self, client: genai.Client, model_name: str = "gemini-2.5-flash"):
        """
        Initialize ChatSessionManager.

        Args:
            client: Google GenAI client
            model_name: Model name to use for chat sessions
        """
        self.client = client
        self.model_name = model_name
        self.sessions: Dict[str, dict] = {}  # user_id -> {chat, last_active, store_name}
        self.session_timeout = timedelta(hours=1)

    def get_or_create_session(
        self,
        user_id: str,
        store_name: str,
        enable_file_search: bool = True
    ):
        """
        Get existing chat session or create a new one.

        Args:
            user_id: User ID for session management
            store_name: File search store name (actual API name, not display name)
            enable_file_search: Whether to enable File Search tool

        Returns:
            Chat session object
        """
        # Check if session exists and is still valid
        if user_id in self.sessions:
            session_data = self.sessions[user_id]
            last_active = session_data['last_active']

            # Check timeout
            if datetime.now() - last_active < self.session_timeout:
                # Session is still valid - update last_active and return
                session_data['last_active'] = datetime.now()
                print(f"[INFO] Reusing existing session for user: {user_id}")
                return session_data['chat']
            else:
                # Session expired
                print(f"[INFO] Session expired for user: {user_id}, creating new session")
                del self.sessions[user_id]

        # Create new session
        print(f"[INFO] Creating new chat session for user: {user_id}")
        print(f"[INFO] File Search enabled: {enable_file_search}")
        if enable_file_search:
            print(f"[INFO] Using store: {store_name}")

        # Build config
        tools = []
        if enable_file_search:
            # Add File Search tool
            tools.append(
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store_name]
                    )
                )
            )

        config = types.GenerateContentConfig(
            tools=tools if tools else None,
            temperature=0.7,
            system_instruction="""你是一個專業的文件分析助手。

當用戶詢問文件相關問題時：
- 使用 File Search 工具搜尋相關內容
- 基於文件內容提供準確、詳細的回答
- 引用具體的段落或章節
- 如果文件中沒有相關資訊，誠實告知用戶

當用戶進行一般對話時：
- 友善、專業地回答
- 記住對話上下文，提供連貫的回應

重要原則：
- 保持對話記憶，理解前後文關聯
- 如果用戶提到「剛才」、「之前」等詞，回顧對話歷史
- 提供簡潔但完整的回答"""
        )

        # Create chat session
        chat = self.client.chats.create(
            model=self.model_name,
            config=config
        )

        # Store session
        self.sessions[user_id] = {
            'chat': chat,
            'last_active': datetime.now(),
            'store_name': store_name
        }

        print(f"[INFO] Chat session created successfully for user: {user_id}")
        return chat

    def clear_session(self, user_id: str) -> bool:
        """
        Clear chat session for a user.

        Args:
            user_id: User ID

        Returns:
            True if session was cleared, False if no session existed
        """
        if user_id in self.sessions:
            del self.sessions[user_id]
            print(f"[INFO] Cleared session for user: {user_id}")
            return True
        print(f"[INFO] No session to clear for user: {user_id}")
        return False

    def get_session_info(self, user_id: str) -> Optional[dict]:
        """
        Get session information for a user.

        Args:
            user_id: User ID

        Returns:
            Session info dict or None if no session exists
        """
        if user_id in self.sessions:
            session_data = self.sessions[user_id]
            return {
                'exists': True,
                'last_active': session_data['last_active'],
                'store_name': session_data['store_name'],
                'age_seconds': (datetime.now() - session_data['last_active']).total_seconds()
            }
        return None

    def cleanup_expired_sessions(self):
        """
        Remove expired sessions from memory.
        Should be called periodically.
        """
        now = datetime.now()
        expired_users = []

        for user_id, session_data in self.sessions.items():
            if now - session_data['last_active'] >= self.session_timeout:
                expired_users.append(user_id)

        for user_id in expired_users:
            del self.sessions[user_id]
            print(f"[INFO] Cleaned up expired session for user: {user_id}")

        if expired_users:
            print(f"[INFO] Cleaned up {len(expired_users)} expired sessions")
