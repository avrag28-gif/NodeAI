import httpx
import re
from ..base import BaseTool


TOR_PROXY = "socks5://127.0.0.1:9050"


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the internet via DuckDuckGo"
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
                response = await client.get(
                    "https://html.duckduckgo.com/html/",
                    params={"q": query},
                    headers=headers
                )

                if response.status_code == 200:
                    text = response.text
                    results = []
                    blocks = re.findall(r'<a[^>]*class="result__a"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', text, re.DOTALL)
                    if blocks:
                        for i, (title, snippet) in enumerate(blocks[:5]):
                            clean_title = re.sub(r'<.*?>', '', title).strip()
                            clean_snippet = re.sub(r'<.*?>', '', snippet).strip()
                            if clean_title:
                                results.append(f"{i+1}. {clean_title}\n   {clean_snippet}")
                    if results:
                        return "\n\n".join(results)
                    links = re.findall(r'<a[^>]*href="(http[^"]*)"[^>]*>(.*?)</a>', text, re.DOTALL)
                    if links:
                        for i, (url, title) in enumerate(links[:5]):
                            clean_title = re.sub(r'<.*?>', '', title).strip()
                            if clean_title and 'duckduckgo' not in url:
                                results.append(f"{i+1}. {clean_title}\n   {url}")
                    if results:
                        return "\n\n".join(results)
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
    description = "Fetch content from any URL (surface web, deep web, .onion via Tor)"
    parameters = {
        "url": {"type": "string", "description": "URL to fetch"},
        "use_tor": {"type": "boolean", "description": "Use Tor for .onion or anonymous access", "default": False}
    }
    permission_required = "network"

    async def execute(self, url: str = "", use_tor: bool = False, **kwargs) -> str:
        if not url:
            return "Error: url is required"

        try:
            # Use Tor proxy for .onion sites or anonymous access
            if use_tor or '.onion' in url:
                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, transport=httpx.AsyncHTTPTransport(proxy=TOR_PROXY)) as client:
                    response = await client.get(
                        url,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MyAI/1.0"}
                    )
            else:
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


class TorSearchTool(BaseTool):
    name = "tor_search"
    description = "Search and access .onion sites via Tor (Dark Web)"
    parameters = {
        "url": {"type": "string", "description": ".onion URL to access"},
        "query": {"type": "string", "description": "Search query for dark web search engines"}
    }
    permission_required = "network"

    async def execute(self, url: str = "", query: str = "", **kwargs) -> str:
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, transport=httpx.AsyncHTTPTransport(proxy=TOR_PROXY)) as client:
                if url:
                    response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                    response.raise_for_status()
                    text = response.text
                    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
                    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
                    text = re.sub(r'<[^>]+>', ' ', text)
                    text = re.sub(r'\s+', ' ', text).strip()
                    if len(text) > 10000:
                        text = text[:10000] + "\n... (truncated)"
                    return text

                if query:
                    # Try Ahmia search engine
                    search_url = f"http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion/search/?q={query}"
                    response = await client.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
                    text = response.text
                    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
                    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
                    text = re.sub(r'<[^>]+>', ' ', text)
                    text = re.sub(r'\s+', ' ', text).strip()
                    if len(text) > 5000:
                        text = text[:5000]
                    return text

                return "Provide either url or query parameter"
        except Exception as e:
            return f"Tor error: {e}"


class ArchiveWebTool(BaseTool):
    name = "archive_web"
    description = "Access web archives (Bergie Web) via Wayback Machine"
    parameters = {
        "url": {"type": "string", "description": "URL to find archived version"},
        "timestamp": {"type": "string", "description": "Timestamp (YYYYMMDD) or 'latest'"}
    }
    permission_required = "network"

    async def execute(self, url: str = "", timestamp: str = "latest", **kwargs) -> str:
        if not url:
            return "Error: url is required"

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                # Get available snapshots
                api_url = f"https://archive.org/wayback/available?url={url}"
                response = await client.get(api_url)
                data = response.json()

                snapshots = data.get("archived_snapshots", {})
                closest = snapshots.get("closest", {})

                if closest:
                    archive_url = closest.get("url", "")
                    if archive_url:
                        # Fetch archived content
                        resp = await client.get(archive_url, headers={"User-Agent": "Mozilla/5.0"})
                        text = resp.text
                        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
                        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
                        text = re.sub(r'<[^>]+>', ' ', text)
                        text = re.sub(r'\s+', ' ', text).strip()
                        if len(text) > 10000:
                            text = text[:10000] + "\n... (truncated)"
                        return f"Archived version from {closest.get('timestamp', 'unknown')}:\n\n{text}"

                return f"No archived version found for {url}"
        except Exception as e:
            return f"Archive error: {e}"


class DeepWebSearchTool(BaseTool):
    name = "deep_web_search"
    description = "Search deep web databases, academic papers, government records"
    parameters = {
        "query": {"type": "string", "description": "Search query"},
        "source": {"type": "string", "description": "Source: scholar, pubmed, arxiv, government"}
    }
    permission_required = "network"

    async def execute(self, query: str = "", source: str = "scholar", **kwargs) -> str:
        if not query:
            return "Error: query is required"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                if source == "scholar":
                    url = f"https://scholar.google.com/scholar?q={query}&hl=en"
                    response = await client.get(url, headers=headers)
                    text = response.text
                    titles = re.findall(r'<h3[^>]*>(.*?)</h3>', text, re.DOTALL)
                    results = []
                    for i, t in enumerate(titles[:5]):
                        clean = re.sub(r'<.*?>', '', t).strip()
                        if clean:
                            results.append(f"{i+1}. {clean}")
                    return "\n".join(results) if results else "No scholar results"

                elif source == "pubmed":
                    url = f"https://pubmed.ncbi.nlm.nih.gov/?term={query}&format=pubmed"
                    response = await client.get(url, headers=headers)
                    text = response.text
                    titles = re.findall(r'<h3[^>]*class="[^"]*"[^>]*>.*?<a[^>]*>(.*?)</a>', text, re.DOTALL)
                    results = []
                    for i, t in enumerate(titles[:5]):
                        clean = re.sub(r'<.*?>', '', t).strip()
                        if clean:
                            results.append(f"{i+1}. {clean}")
                    return "\n".join(results) if results else "No PubMed results"

                elif source == "arxiv":
                    url = f"https://export.arxiv.org/api/query?search_query=all:{query}&max_results=5"
                    response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                    text = response.text
                    titles = re.findall(r'<title>(.*?)</title>', text, re.DOTALL)
                    results = []
                    for i, t in enumerate(titles[1:6]):
                        clean = t.strip()
                        if clean and clean != "Error":
                            results.append(f"{i+1}. {clean}")
                    if not results:
                        # Fallback: use DuckDuckGo for arxiv
                        search_url = f"https://html.duckduckgo.com/html/?q=site:arxiv.org+{query}"
                        resp = await client.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
                        links = re.findall(r'<a[^>]*class="result__a"[^>]*>(.*?)</a>', resp.text, re.DOTALL)
                        for i, t in enumerate(links[:5]):
                            clean = re.sub(r'<.*?>', '', t).strip()
                            if clean:
                                results.append(f"{i+1}. {clean}")
                    return "\n".join(results) if results else "No arXiv results"

                else:
                    return f"Unknown source: {source}. Use scholar, pubmed, or arxiv."
        except Exception as e:
            return f"Deep web search error: {e}"
