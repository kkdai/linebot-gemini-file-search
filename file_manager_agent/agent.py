"""
File Manager Agent using Google ADK.
Provides conversational interface for managing files.
"""

import os
from google import genai
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner

from .tools import list_files_tool, LIST_FILES_DECLARATION


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or ""


class FileManagerAgent:
    """
    Agent for managing files in a conversational way.
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
        self.client = genai.Client(api_key=GOOGLE_API_KEY, vertexai=False)

        # Define the agent configuration
        self.agent = Agent(
            name="file_manager",
            model="gemini-2.5-flash",
            description="檔案管理助手，幫助使用者查看和管理已上傳的文件。",
            instruction="""你是一個友善的檔案管理助手。

當使用者要求列出檔案時：
1. 使用 list_files tool 來取得檔案清單
2. 用口語化、友善的方式呈現結果
3. 不要使用條列式或表格，用自然的對話方式說明
4. 例如：「我看到你上傳了 3 個檔案唷！首先是『會議記錄.pdf』，這是在 1月8日下午2點上傳的。接著是『技術文件.docx』...」
5. 如果檔案很多，可以總結一下，然後挑幾個重要的說明
6. 語氣要輕鬆、親切

回應時請用繁體中文。""",
            tools=[LIST_FILES_DECLARATION],
        )

        # Create runner
        self.runner = InMemoryRunner(agent=self.agent, app_name="file_manager")

    async def handle_list_files(self) -> str:
        """
        Handle list files request in a conversational way.

        Returns:
            Conversational response about the files
        """
        try:
            # Execute the list_files tool
            files_info = await list_files_tool(self.store_name, self.store_name_cache)

            # Let the LLM generate a conversational response
            prompt = f"""使用者想要查看已上傳的檔案清單。

這是檔案清單：
{files_info}

請用友善、口語化的方式向使用者介紹這些檔案。不要使用條列式，用自然的對話方式說明。"""

            # Use generate_content for simple LLM response
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            if response.text:
                return response.text
            else:
                return "目前沒有找到任何檔案唷！"

        except Exception as e:
            print(f"Error in FileManagerAgent: {e}")
            return f"查詢檔案時發生了一點問題：{str(e)}"
