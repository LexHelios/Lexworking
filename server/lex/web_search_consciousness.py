"""
Web Search Consciousness for LEX
Provides natural language web search capabilities
"""
import logging
from typing import Dict, Any, Optional, List
from ..web.search_engine import web_search_engine

logger = logging.getLogger(__name__)

class WebSearchConsciousness:
    """
    Web search awareness module for LEX
    Handles natural language web search requests
    """
    
    def __init__(self):
        self.search_engine = web_search_engine
        
        # Search intent patterns
        self.search_patterns = {
            "general": [
                "search for", "look up", "find information about",
                "what is", "who is", "tell me about",
                "search the web", "google", "search online"
            ],
            "news": [
                "latest news", "current events", "what's happening",
                "recent news", "news about", "headlines",
                "breaking news", "today's news"
            ],
            "realtime": [
                "right now", "currently", "at this moment",
                "live", "real-time", "happening now",
                "current status", "latest update"
            ],
            "research": [
                "research about", "detailed information",
                "comprehensive search", "deep dive",
                "everything about", "all about"
            ]
        }
        
        logger.info("🌐 Web Search Consciousness initialized")
    
    async def process_search_intent(self, user_input: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check if user input contains web search intent
        """
        input_lower = user_input.lower()
        
        # Check for explicit search requests
        for pattern_type, patterns in self.search_patterns.items():
            for pattern in patterns:
                if pattern in input_lower:
                    return await self._execute_search(user_input, pattern_type, context)
        
        # Check for implicit search requests (questions about current events, facts, etc.)
        if self._is_factual_question(input_lower):
            return await self._execute_search(user_input, "general", context)
        
        return None
    
    def _is_factual_question(self, input_lower: str) -> bool:
        """
        Determine if the input is asking for factual information
        """
        question_words = ["what", "who", "when", "where", "why", "how", "which"]
        current_indicators = ["2024", "2025", "current", "latest", "recent", "now"]
        
        # Check if it's a question
        is_question = any(input_lower.startswith(word) for word in question_words) or "?" in input_lower
        
        # Check if it's about current/recent information
        needs_current_info = any(indicator in input_lower for indicator in current_indicators)
        
        # Check for topics that typically need web search
        web_topics = ["stock", "weather", "score", "election", "news", "price", "rate", "update"]
        has_web_topic = any(topic in input_lower for topic in web_topics)
        
        return is_question and (needs_current_info or has_web_topic)
    
    async def _execute_search(self, user_input: str, search_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute web search and format results
        """
        try:
            # Extract search query from user input
            query = self._extract_search_query(user_input)
            
            # Determine search parameters
            if search_type == "news":
                results = await self.search_engine.search_news(query, num_results=5, time_range="day")
            elif search_type == "realtime":
                results = await self.search_engine.search_realtime(query, num_results=5)
            else:
                # General search
                time_range = "day" if "recent" in user_input.lower() or "latest" in user_input.lower() else None
                results = await self.search_engine.search(query, num_results=10, time_range=time_range)
            
            # Format results for LEX
            if results.get("error"):
                return {
                    "type": "search_error",
                    "response": f"I couldn't search for that right now. Error: {results['error']}",
                    "show_ui": False
                }
            
            # Create formatted response
            formatted_results = self._format_search_results(results, query)
            
            return {
                "type": "search_results",
                "response": formatted_results["summary"],
                "data": {
                    "results": results.get("results", []),
                    "total_results": results.get("total_results", 0),
                    "query": query,
                    "provider": results.get("provider", "unknown")
                },
                "show_ui": True,
                "actions": ["view_full", "search_more"],
                "formatting": "rich"
            }
            
        except Exception as e:
            logger.error(f"Search execution error: {e}")
            return {
                "type": "search_error",
                "response": "I encountered an issue while searching. Please try again.",
                "show_ui": False
            }
    
    def _extract_search_query(self, user_input: str) -> str:
        """
        Extract the actual search query from natural language input
        """
        # Remove common search phrases
        query = user_input.lower()
        
        remove_phrases = [
            "search for", "look up", "find information about",
            "search the web for", "google", "search online for",
            "tell me about", "what is", "who is", "find",
            "latest news about", "current events about",
            "can you search for", "please search for",
            "i want to know about", "show me"
        ]
        
        for phrase in remove_phrases:
            if phrase in query:
                query = query.replace(phrase, "").strip()
        
        # Clean up the query
        query = query.strip("?.,!").strip()
        
        # If query is too short or empty, use original input
        if len(query) < 3:
            query = user_input
        
        return query
    
    def _format_search_results(self, results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """
        Format search results for display
        """
        if not results.get("results"):
            return {
                "summary": f"I couldn't find any results for '{query}'.",
                "formatted": ""
            }
        
        # Create summary
        num_results = len(results["results"])
        provider = results.get("provider", "web search")
        
        summary_parts = [f"I found {num_results} results for '{query}' using {provider}."]
        
        # Add top 3 results to summary
        for i, result in enumerate(results["results"][:3], 1):
            title = result.get("title", "Untitled")
            snippet = result.get("snippet", "")[:150] + "..."
            summary_parts.append(f"\n{i}. {title}: {snippet}")
        
        if num_results > 3:
            summary_parts.append(f"\n...and {num_results - 3} more results.")
        
        return {
            "summary": "\n".join(summary_parts),
            "formatted": self.search_engine.format_results_for_chat(results)
        }
    
    async def search_directly(self, query: str, search_type: str = "general") -> str:
        """
        Direct search method for explicit search requests
        """
        try:
            if search_type == "news":
                results = await self.search_engine.search_news(query)
            elif search_type == "realtime":
                results = await self.search_engine.search_realtime(query)
            else:
                results = await self.search_engine.search(query)
            
            return self.search_engine.format_results_for_chat(results)
            
        except Exception as e:
            logger.error(f"Direct search error: {e}")
            return f"Search error: {str(e)}"

# Global instance
web_search_consciousness = WebSearchConsciousness()