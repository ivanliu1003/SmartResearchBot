import os
import adk
from google.generativeai import configure as gg_configure
from serpapi import GoogleSearch

def setup_keys():
    """從環境變數設定 API Keys"""
    # 在真實的評估系統中，API Keys 通常會由平台注入環境變數
    # 所以這段本地設定的程式碼在伺服器上也能正常運作
    try:
        gg_configure(api_key=os.environ["GEMINI_API_KEY"])
        return os.environ["SERPAPI_API_KEY"]
    except KeyError as e:
        print(f"❌ 錯誤：缺少環境變數 {e}。請確保已設定 API Keys。")
        exit() # 如果缺少 Key，直接退出程式

def web_search(query: str, serpapi_key: str) -> str:
    """
    當你需要回答關於近期事件、特定人物、產品或任何無法在現有知識中找到的資訊時，請使用此工具進行網路搜尋。
    Args:
        query (str): 你想要搜尋的關鍵字或問題。
    Returns:
        str: 一個包含搜尋結果摘要的字串。
    """
    print(f"⚡ 正在執行網頁搜尋: {query}")
    try:
        params = {"q": query, "api_key": serpapi_key, "engine": "google"}
        search = GoogleSearch(params)
        results = search.get_dict()
        snippets = []
        if "organic_results" in results:
            for result in results["organic_results"][:5]:
                if "snippet" in result: snippets.append(result["snippet"])
        if "answer_box" in results and "snippet" in results["answer_box"]:
            snippets.insert(0, results["answer_box"]["snippet"])
        if not snippets: return "網頁搜尋沒有找到相關資訊。"
        return " ".join(snippets)
    except Exception as e:
        print(f"⚠️ 搜尋時發生錯誤: {e}")
        return "網頁搜尋失敗。"

def main():
    """
    主執行函數：處理單一問題並輸出結果。
    """
    serpapi_key = setup_keys()

    # 將 web_search 工具與 SerpApi key 綁定
    # 使用 lambda 讓 agent 呼叫時不需要傳入 serpapi_key
    search_tool_with_key = lambda query: web_search(query=query, serpapi_key=serpapi_key)
    search_tool_with_key.__doc__ = web_search.__doc__ # 複製註解，讓 LLM 能看懂

    research_agent = adk.Agent(
        model="gemini-1.5-pro-latest",
        tools=[search_tool_with_key]
    )

    # 從標準輸入讀取一個問題
    print("請輸入您的問題：")
    user_question = input()
    
    if not user_question:
        print("沒有收到問題，程式結束。")
        return

    # 處理問題並印出結果
    response = research_agent.chat(user_question)
    print("\n🤖 AI 回覆:")
    print(response)

# --- 程式進入點 ---
if __name__ == "__main__":
    main()
