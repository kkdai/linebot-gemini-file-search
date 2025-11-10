"""
Tools for File Manager Agent.
"""

from google import genai
from google.genai import types
import os
import requests


GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or ""


async def list_files_tool(store_name: str, store_name_cache: dict) -> str:
    """
    List all documents in a file search store.

    Args:
        store_name: The display name of the file search store
        store_name_cache: Cache mapping display_name to actual store name

    Returns:
        Formatted string with file information
    """
    try:
        client = genai.Client(api_key=GOOGLE_API_KEY)

        # Get actual store name
        actual_store_name = None
        if store_name in store_name_cache:
            actual_store_name = store_name_cache[store_name]
        else:
            # Find store by display_name
            stores = client.file_search_stores.list()
            for store in stores:
                if hasattr(store, 'display_name') and store.display_name == store_name:
                    actual_store_name = store.name
                    store_name_cache[store_name] = actual_store_name
                    break

        if not actual_store_name:
            return f"找不到名稱為 '{store_name}' 的文件庫。"

        documents = []

        # Try to use SDK method first
        try:
            if hasattr(client.file_search_stores, 'documents'):
                for doc in client.file_search_stores.documents.list(parent=actual_store_name):
                    documents.append({
                        'name': doc.name,
                        'display_name': getattr(doc, 'display_name', 'Unknown'),
                        'create_time': str(getattr(doc, 'create_time', '')),
                    })
            else:
                # Fallback to REST API
                url = f"https://generativelanguage.googleapis.com/v1beta/{actual_store_name}/documents"
                headers = {'Content-Type': 'application/json'}
                params = {'key': GOOGLE_API_KEY}

                response = requests.get(url, headers=headers, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                for doc in data.get('documents', []):
                    documents.append({
                        'name': doc.get('name', 'N/A'),
                        'display_name': doc.get('displayName', 'Unknown'),
                        'create_time': doc.get('createTime', ''),
                    })

        except Exception as e:
            print(f"Error with SDK, trying REST API: {e}")
            # Fallback to REST API
            url = f"https://generativelanguage.googleapis.com/v1beta/{actual_store_name}/documents"
            headers = {'Content-Type': 'application/json'}
            params = {'key': GOOGLE_API_KEY}

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            for doc in data.get('documents', []):
                documents.append({
                    'name': doc.get('name', 'N/A'),
                    'display_name': doc.get('displayName', 'Unknown'),
                    'create_time': doc.get('createTime', ''),
                })

        if not documents:
            return "目前沒有任何已上傳的文件。"

        # Format the documents list as a simple string for LLM to process
        result = f"找到 {len(documents)} 個文件：\n"
        for i, doc in enumerate(documents, 1):
            create_time = doc['create_time']
            if create_time and 'T' in create_time:
                # Format time
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(create_time.replace('Z', '+00:00'))
                    create_time = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    create_time = create_time[:16]

            result += f"{i}. {doc['display_name']} (上傳時間: {create_time})\n"

        return result

    except Exception as e:
        print(f"Error listing files: {e}")
        return f"列出檔案時發生錯誤：{str(e)}"


# Define the tool schema for ADK
LIST_FILES_DECLARATION = types.FunctionDeclaration(
    name="list_files",
    description="列出使用者已上傳的所有文件檔案，包含檔案名稱和上傳時間。",
    parameters={
        "type": "object",
        "properties": {},
        "required": []
    }
)
