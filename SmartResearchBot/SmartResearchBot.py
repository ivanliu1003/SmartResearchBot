import os
import adk
from google.generativeai import configure as gg_configure
from serpapi import GoogleSearch

# --- 1. 設定 API Keys ---
# 建議使用環境變數來管理你的 API Keys，這更安全
# 你需要先取得這兩個 Keys
# Google Gemini API Key: https://aistudio.google.com/app/apikey
# SerpApi Key: https://serpapi.com/manage-api-key (註冊後免費額度足夠專案使用)
gg_configure(api_key=os.environ["AIzaSyDrvZfFvqS7KXYdlW66MGSxRmXcDCq8XW0"])
SERPAPI_API_KEY = os.environ["c3fbf92d60b1e10262be7cb94e299bb8bea3b71037a7bc5d06bdb293130e87f5"]


# --- 2. 定義你的「工具」(Tool) ---
# 這是一個簡單的 Python 函數，但關鍵在於它的 "docstring" (註解)
# LLM 會閱讀這個註解來理解這個工具的功能、參數和用途。
def web_search(query: str) -> str:
    """
    當你需要回答關於近期事件、特定人物、產品或任何無法在現有知識中找到的資訊時，請使用此工具進行網路搜尋。

    Args:
        query (str): 你想要搜尋的關鍵字或問題。

    Returns:
        str: 一個包含搜尋結果摘要的字串。
    """
    print(f"⚡ 正在執行網頁搜尋: {query}")
    try:
        params = {
            "q": query,
            "api_key": SERPAPI_API_KEY,
            "engine": "google",
        }
        search = GoogleSearch(params)
        results = search.get_dict()

        # 從搜尋結果中提取有用的片段
        snippets = []
        if "organic_results" in results:
            for result in results["organic_results"][:5]: # 只取前5個結果
                if "snippet" in result:
                    snippets.append(result["snippet"])
        
        if "answer_box" in results and "snippet" in results["answer_box"]:
            snippets.insert(0, results["answer_box"]["snippet"]) # 優先使用 Google 的 Answer Box

        if not snippets:
            return "網頁搜尋沒有找到相關資訊。"

        return " ".join(snippets)

    except Exception as e:
        print(f"⚠️ 搜尋時發生錯誤: {e}")
        return "網頁搜尋失敗。"


# --- 3. 建立並設定你的「代理人」(Agent) ---
# 我們告訴 Agent 它的「大腦」是哪個模型，以及它有哪些「工具」可以使用。
research_agent = adk.Agent(
    model="gemini-1.5-pro-latest",  # 使用支援工具呼叫的最新模型
    tools=[web_search]             # 將我們定義的搜尋工具註冊給 Agent
)

# --- 4. 開始與 Agent 互動 ---
print("你好！我是你的 AI 研究助理。有什麼問題儘管問！(輸入 'exit' 結束)")

while True:
    user_question = input("\n> ")
    if user_question.lower() == 'exit':
        print("感謝使用，再見！")
        break

    # 使用 agent.chat() 讓 Agent 處理問題
    # 它會自動決定是否要呼叫 web_search 工具
    response = research_agent.chat(user_question)

    print(f"\n🤖 AI 回覆:\n{response}")
