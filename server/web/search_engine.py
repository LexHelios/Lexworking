"""
Web Search Engine for LexOS
Provides real-time web search capabilities with multiple search providers
"""
import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from urllib.parse import quote_plus
import os

logger = logging.getLogger(__name__)

class WebSearchEngine:
    """
    Multi-provider web search engine
    Supports multiple search APIs and fallbacks
    """
    
    def __init__(self):
        # Search provider configurations
        self.providers = {
            'duckduckgo': {
                'enabled': True,
                'base_url': 'https://api.duckduckgo.com/',
                'rate_limit': 1,  # requests per second
                'requires_key': False
            },
            'serpapi': {
                'enabled': bool(os.getenv('SERPAPI_KEY')),
                'base_url': 'https://serpapi.com/search',
                'api_key': os.getenv('SERPAPI_KEY'),
                'rate_limit': 10,
                'requires_key': True
            },
            'bing': {
                'enabled': bool(os.getenv('BING_API_KEY')),
                'base_url': 'https://api.bing.microsoft.com/v7.0/search',
                'api_key': os.getenv('BING_API_KEY'),
                'rate_limit': 3,
                'requires_key': True
            },
            'searx': {
                'enabled': bool(os.getenv('SEARX_INSTANCE')),
                'base_url': os.getenv('SEARX_INSTANCE', 'https://searx.me'),
                'rate_limit': 2,
                'requires_key': False
            }
        }
        
        # Results cache (simple in-memory cache)
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        logger.info(f"Web Search Engine initialized with providers: {[p for p, c in self.providers.items() if c['enabled']]}")
    
    async def search(
        self,
        query: str,
        num_results: int = 10,
        search_type: str = "general",
        time_range: Optional[str] = None,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform web search across available providers
        
        Args:
            query: Search query
            num_results: Number of results to return
            search_type: Type of search (general, news, images, videos)
            time_range: Time filter (day, week, month, year)
            region: Region code for localized results
        """
        try:
            # Check cache first
            cache_key = f"{query}:{search_type}:{time_range}:{region}"
            if cache_key in self.cache:
                cached_result = self.cache[cache_key]
                if (datetime.now() - cached_result['timestamp']).seconds < self.cache_ttl:
                    logger.info(f"Returning cached results for: {query}")
                    return cached_result['data']
            
            # Try each provider in order
            for provider_name, config in self.providers.items():
                if not config['enabled']:
                    continue
                    
                try:
                    if provider_name == 'duckduckgo':
                        results = await self._search_duckduckgo(query, num_results, search_type)
                    elif provider_name == 'serpapi':
                        results = await self._search_serpapi(query, num_results, search_type, time_range)
                    elif provider_name == 'bing':
                        results = await self._search_bing(query, num_results, search_type, time_range)
                    elif provider_name == 'searx':
                        results = await self._search_searx(query, num_results, search_type)
                    else:
                        continue
                    
                    if results and results.get('results'):
                        # Cache successful results
                        self.cache[cache_key] = {
                            'timestamp': datetime.now(),
                            'data': results
                        }
                        
                        # Add metadata
                        results['query'] = query
                        results['provider'] = provider_name
                        results['timestamp'] = datetime.now().isoformat()
                        results['search_type'] = search_type
                        
                        return results
                        
                except Exception as e:
                    logger.error(f"Search failed with {provider_name}: {e}")
                    continue
            
            # If all providers fail, return error
            return {
                'error': 'All search providers failed',
                'query': query,
                'results': [],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return {
                'error': str(e),
                'query': query,
                'results': [],
                'timestamp': datetime.now().isoformat()
            }
    
    async def _search_duckduckgo(self, query: str, num_results: int, search_type: str) -> Dict[str, Any]:
        """Search using DuckDuckGo Instant Answer API"""
        try:
            # DuckDuckGo Instant Answer API
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.providers['duckduckgo']['base_url']}",
                    params=params
                ) as response:
                    data = await response.json()
            
            results = []
            
            # Parse instant answer
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'Summary'),
                    'url': data.get('AbstractURL', ''),
                    'snippet': data.get('Abstract', ''),
                    'source': data.get('AbstractSource', 'DuckDuckGo')
                })
            
            # Parse related topics
            for topic in data.get('RelatedTopics', [])[:num_results-1]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('Text', '').split(' - ')[0],
                        'url': topic.get('FirstURL', ''),
                        'snippet': topic.get('Text', ''),
                        'source': 'DuckDuckGo'
                    })
            
            # If no results, try web search (requires additional implementation)
            if not results:
                # Fallback to web scraping or another method
                results = await self._search_duckduckgo_html(query, num_results)
            
            return {
                'results': results[:num_results],
                'total_results': len(results),
                'provider': 'duckduckgo'
            }
            
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            raise
    
    async def _search_duckduckgo_html(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Fallback HTML search for DuckDuckGo"""
        try:
            # Use DuckDuckGo HTML interface
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers) as response:
                    html = await response.text()
            
            # Simple HTML parsing (in production, use BeautifulSoup)
            results = []
            
            # Extract results from HTML (simplified)
            import re
            
            # Find result blocks
            result_pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)">([^<]+)</a>'
            snippet_pattern = r'<a class="result__snippet" href="[^"]+">([^<]+)</a>'
            
            urls_titles = re.findall(result_pattern, html)
            snippets = re.findall(snippet_pattern, html)
            
            for i, (url, title) in enumerate(urls_titles[:num_results]):
                snippet = snippets[i] if i < len(snippets) else ''
                results.append({
                    'title': title.strip(),
                    'url': url,
                    'snippet': snippet.strip(),
                    'source': 'DuckDuckGo'
                })
            
            return results
            
        except Exception as e:
            logger.error(f"DuckDuckGo HTML search error: {e}")
            return []
    
    async def _search_serpapi(self, query: str, num_results: int, search_type: str, time_range: Optional[str]) -> Dict[str, Any]:
        """Search using SerpAPI (Google results)"""
        if not self.providers['serpapi']['api_key']:
            raise ValueError("SerpAPI key not configured")
        
        try:
            params = {
                'q': query,
                'api_key': self.providers['serpapi']['api_key'],
                'num': num_results,
                'engine': 'google'
            }
            
            if time_range:
                time_map = {
                    'day': 'd',
                    'week': 'w',
                    'month': 'm',
                    'year': 'y'
                }
                params['tbs'] = f"qdr:{time_map.get(time_range, 'd')}"
            
            if search_type == 'news':
                params['tbm'] = 'nws'
            elif search_type == 'images':
                params['tbm'] = 'isch'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.providers['serpapi']['base_url'],
                    params=params
                ) as response:
                    data = await response.json()
            
            results = []
            
            # Parse organic results
            for result in data.get('organic_results', [])[:num_results]:
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('link', ''),
                    'snippet': result.get('snippet', ''),
                    'source': result.get('source', 'Google'),
                    'date': result.get('date', '')
                })
            
            # Add knowledge graph if available
            if data.get('knowledge_graph'):
                kg = data['knowledge_graph']
                results.insert(0, {
                    'title': kg.get('title', ''),
                    'url': kg.get('website', ''),
                    'snippet': kg.get('description', ''),
                    'source': 'Knowledge Graph',
                    'type': 'knowledge_graph'
                })
            
            return {
                'results': results,
                'total_results': data.get('search_information', {}).get('total_results', len(results)),
                'provider': 'serpapi'
            }
            
        except Exception as e:
            logger.error(f"SerpAPI search error: {e}")
            raise
    
    async def _search_bing(self, query: str, num_results: int, search_type: str, time_range: Optional[str]) -> Dict[str, Any]:
        """Search using Bing Search API"""
        if not self.providers['bing']['api_key']:
            raise ValueError("Bing API key not configured")
        
        try:
            headers = {
                'Ocp-Apim-Subscription-Key': self.providers['bing']['api_key']
            }
            
            params = {
                'q': query,
                'count': num_results,
                'mkt': 'en-US'
            }
            
            if time_range:
                params['freshness'] = time_range  # Day, Week, Month
            
            endpoint = 'search'
            if search_type == 'news':
                endpoint = 'news/search'
            elif search_type == 'images':
                endpoint = 'images/search'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.providers['bing']['base_url']}/{endpoint}",
                    headers=headers,
                    params=params
                ) as response:
                    data = await response.json()
            
            results = []
            
            # Parse web results
            if 'webPages' in data:
                for result in data['webPages'].get('value', [])[:num_results]:
                    results.append({
                        'title': result.get('name', ''),
                        'url': result.get('url', ''),
                        'snippet': result.get('snippet', ''),
                        'source': 'Bing',
                        'date': result.get('dateLastCrawled', '')
                    })
            
            # Parse news results
            elif 'value' in data:
                for result in data.get('value', [])[:num_results]:
                    results.append({
                        'title': result.get('name', ''),
                        'url': result.get('url', ''),
                        'snippet': result.get('description', ''),
                        'source': result.get('provider', [{}])[0].get('name', 'Bing'),
                        'date': result.get('datePublished', '')
                    })
            
            return {
                'results': results,
                'total_results': data.get('totalEstimatedMatches', len(results)),
                'provider': 'bing'
            }
            
        except Exception as e:
            logger.error(f"Bing search error: {e}")
            raise
    
    async def _search_searx(self, query: str, num_results: int, search_type: str) -> Dict[str, Any]:
        """Search using Searx instance"""
        try:
            params = {
                'q': query,
                'format': 'json',
                'lang': 'en',
                'pageno': 1
            }
            
            if search_type == 'news':
                params['categories'] = 'news'
            elif search_type == 'images':
                params['categories'] = 'images'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.providers['searx']['base_url']}/search",
                    params=params
                ) as response:
                    data = await response.json()
            
            results = []
            
            for result in data.get('results', [])[:num_results]:
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'snippet': result.get('content', ''),
                    'source': result.get('engine', 'Searx'),
                    'score': result.get('score', 0)
                })
            
            return {
                'results': results,
                'total_results': len(results),
                'provider': 'searx'
            }
            
        except Exception as e:
            logger.error(f"Searx search error: {e}")
            raise
    
    async def search_news(self, query: str, num_results: int = 10, time_range: str = "week") -> Dict[str, Any]:
        """Specialized news search"""
        return await self.search(query, num_results, "news", time_range)
    
    async def search_realtime(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Real-time search for current events"""
        return await self.search(query, num_results, "news", "day")
    
    def format_results_for_chat(self, results: Dict[str, Any]) -> str:
        """Format search results for chat display"""
        if results.get('error'):
            return f"Search error: {results['error']}"
        
        if not results.get('results'):
            return "No results found."
        
        formatted = f"🔍 **Web Search Results for: {results.get('query', '')}**\n\n"
        
        for i, result in enumerate(results['results'][:5], 1):
            formatted += f"{i}. **{result.get('title', 'Untitled')}**\n"
            formatted += f"   {result.get('snippet', 'No description available')}\n"
            formatted += f"   🔗 {result.get('url', '')}\n"
            if result.get('date'):
                formatted += f"   📅 {result['date']}\n"
            formatted += "\n"
        
        if results.get('total_results', 0) > 5:
            formatted += f"... and {results['total_results'] - 5} more results"
        
        return formatted

# Global instance
web_search_engine = WebSearchEngine()