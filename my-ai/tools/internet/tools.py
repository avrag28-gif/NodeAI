import httpx
import re
from ..base import BaseTool


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the internet for information"
    parameters = {
        "query": {"type": "string", "description": "Search query"}
    }
    permission_required = "network"

    async def execute(self, query: str = "", **kwargs) -> str:
        if not query:
            return "Error: query is required"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                # Try DuckDuckGo (bot-friendly)
                response = await client.get(
                    "https://html.duckduckgo.com/html/",
                    params={"q": query},
                    headers=headers
                )

                if response.status_code == 200:
                    text = response.text
                    results = []

                    # Extract results from DuckDuckGo
                    blocks = re.findall(r'<a[^>]*class="result__a"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', text, re.DOTALL)
                    
                    if blocks:
                        for i, (title, snippet) in enumerate(blocks[:5]):
                            clean_title = re.sub(r'<.*?>', '', title).strip()
                            clean_snippet = re.sub(r'<.*?>', '', snippet).strip()
                            if clean_title:
                                results.append(f"{i+1}. {clean_title}\n   {clean_snippet}")
                    
                    if results:
                        return "\n\n".join(results)

                    # Fallback: extract any links
                    links = re.findall(r'<a[^>]*href="(http[^"]*)"[^>]*>(.*?)</a>', text, re.DOTALL)
                    if links:
                        for i, (url, title) in enumerate(links[:5]):
                            clean_title = re.sub(r'<.*?>', '', title).strip()
                            if clean_title and 'duckduckgo' not in url:
                                results.append(f"{i+1}. {clean_title}\n   {url}")
                    
                    if results:
                        return "\n\n".join(results)

                    # Last resort: extract text
                    clean = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
                    clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL)
                    clean = re.sub(r'<[^>]+>', ' ', clean)
                    clean = re.sub(r'\s+', ' ', clean).strip()
                    if len(clean) > 500:
                        return clean[:500]
                    return "No search results found"
                else:
                    return f"Search returned status {response.status_code}"

        except Exception as e:
            return f"Search error: {e}"


class FetchWebTool(BaseTool):
    name = "fetch_web"
    description = "Fetch and read content from a URL"
    parameters = {
        "url": {"type": "string", "description": "URL to fetch"}
    }
    permission_required = "network"

    async def execute(self, url: str = "", **kwargs) -> str:
        if not url:
            return "Error: url is required"

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MyAI/1.0"}
                )
                response.raise_for_status()

                content_type = response.headers.get("content-type", "")
                if "text" not in content_type and "html" not in content_type:
                    return f"Non-text content: {content_type} ({len(response.content)} bytes)"

                text = response.text
                text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
                text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
                text = re.sub(r'<[^>]+>', ' ', text)
                text = re.sub(r'\s+', ' ', text).strip()

                if len(text) > 10000:
                    text = text[:10000] + "\n... (truncated)"

                return text
        except Exception as e:
            return f"Fetch error: {e}"
