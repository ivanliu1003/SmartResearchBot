import os
import sys
from dotenv import load_dotenv
from serpapi import GoogleSearch
import google.generativeai as genai
#environment
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
#---------------------------------------------------------

def web_search(query: str) -> dict:
    """
    Use this tool when you need up-to-date or external information (recent events, prices, lists, rules updates,
    or facts you are unsure about). Returns top search snippets.
    """
    params = {
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "engine": "google",
    }
    results = GoogleSearch(params).get_dict()
    snippets = []
    ab = results.get("answer_box", {})
    if isinstance(ab, dict) and ab.get("snippet"):
        snippets.append(ab["snippet"])

    for r in results.get("organic_results", [])[:5]:
        title = r.get("title", "")
        snippet = r.get("snippet", "")
        link = r.get("link", "")
        if snippet:
            snippets.append(f"{title} | {snippet} | {link}")

    if not snippets:
        snippets = ["（搜尋沒有找到明確結果）"] #防止AI亂猜

    return {"top_results": snippets}


def need_search(question: str) -> bool:
    """
    Ask Gemini to decide if web search is needed. Output strictly YES/NO.
    """
    model = genai.GenerativeModel("gemini-3-flash-preview")
    prompt = f"""
你是一個嚴謹的助理。請判斷回答問題是否需要「外部或即時資料」（例如網路搜尋）。
如果問題涉及：近期事件、最新規則、價格、名單、特定網站內容、或你不確定的事實 -> 需要搜尋。
如果是：概念解釋、基礎知識、數學推理、程式教學、一般不隨時間變動的內容 -> 不需要搜尋。

只回答 YES 或 NO。

問題：{question}
""".strip()

    resp = model.generate_content(prompt)
    ans = (resp.text or "").strip().upper()
    return ans.startswith("YES")

# ----------------------------
# 3) Final Answer: with optional search context
# ----------------------------
def answer(question: str) -> str:
    # Decide
    do_search = need_search(question)

    context = ""
    if do_search:
        try:
            data = web_search(question)
            # Format search results
            lines = []
            for i, s in enumerate(data.get("top_results", [])[:5], start=1):
                lines.append(f"[{i}] {s}")
            context = "\n".join(lines)
        except Exception as e:
            context = f"（搜尋失敗：{e}。我將在沒有外部資料的情況下回答。）"

    # Answer with Gemini Pro (stronger reasoning)
    model = genai.GenerativeModel("gemini-3-flash-preview")

    final_prompt = f"""
你是一個嚴謹且清楚的研究助理。請回答使用者問題。
- 如果提供了搜尋結果：請根據搜尋結果作答，並引用你用到的結果編號（例如 [1][3]）。
- 如果未提供搜尋結果：請直接用你的知識回答。若你不確定，請坦白說明不確定之處，並建議下一步怎麼查。

搜尋結果：
{context if context else "（未使用搜尋）"}

問題：
{question}
""".strip()

    resp = model.generate_content(final_prompt)
    return resp.text or ""

# ----------------------------
# 4) CLI loop
# ----------------------------
def main():
    print("你好！我是你的 AI 研究助理（會自己決定要不要上網查）。輸入 exit 結束。")
    while True:
        q = input("\n> ").strip()
        if not q:
            continue
        if q.lower() == "exit":
            print("感謝使用，再見！")
            break
        try:
            out = answer(q)
            print("\n🤖 AI 回覆:\n" + out)
        except Exception as e:
            print(f"\n⚠️ 發生錯誤：{e}")

if __name__ == "__main__":
    main()
