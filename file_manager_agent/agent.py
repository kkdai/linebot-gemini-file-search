"""
File Manager Agent using Google Gemini.
Provides conversational interface for managing files.
"""

import os
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner

from .tools import list_files_tool


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or ""


class FileManagerAgent:
    """
    Agent for managing files in a conversational way.
    Uses Gemini to generate natural, conversational responses.
    """

    def __init__(self, store_name: str, store_name_cache: dict):
        """
        Initialize the File Manager Agent.

        Args:
            store_name: The display name of the file search store
            store_name_cache: Cache mapping display_name to actual store name
        """
        self.store_name = store_name
        self.store_name_cache = store_name_cache

        # Create a wrapper function that captures the context
        async def list_files():
            """列出使用者已上傳的所有文件檔案，包含檔案名稱和上傳時間。"""
            return await list_files_tool(self.store_name, self.store_name_cache)

        # Store the wrapper function
        self._list_files = list_files

        # Initialize the ADK Agent with the callable function
        self.agent = Agent(
            name="file_manager",
            model="gemini-2.5-flash",
            description="檔案管理助手，幫助使用者查看和管理已上傳的文件。",
            instruction="""你是一個友善的檔案管理助手。
當使用者想要查看檔案時，使用 list_files 工具獲取檔案清單。
請用自然、口語化的方式向使用者介紹這些檔案，不要使用條列式，用對話的方式說明。
讓使用者感覺像在跟朋友聊天一樣。""",
            tools=[self._list_files],  # Pass the callable function
        )

        # Initialize the runner
        self.runner = InMemoryRunner(
            agent=self.agent,
            app_name="file_manager"
        )

    async def handle_list_files(self) -> str:
        """
        Handle list files request in a conversational way.

        Returns:
            Conversational response about the files
        """
        try:
            # Use the ADK runner to process the request
            user_prompt = "請列出所有已上傳的檔案"

            # Run the agent
            response = await self.runner.run(user_prompt)

            # Extract the response text
            if hasattr(response, 'text') and response.text:
                return response.text
            elif hasattr(response, 'content') and response.content:
                return response.content
            elif isinstance(response, str):
                return response
            else:
                # Try to get the last message from the runner
                messages = self.runner.get_messages()
                if messages and len(messages) > 0:
                    last_msg = messages[-1]
                    if hasattr(last_msg, 'content'):
                        return last_msg.content
                    elif hasattr(last_msg, 'text'):
                        return last_msg.text

                return "目前沒有找到任何檔案唷！"

        except Exception as e:
            print(f"Error in FileManagerAgent: {e}")
            import traceback
            traceback.print_exc()
            return f"查詢檔案時發生了一點問題：{str(e)}"
