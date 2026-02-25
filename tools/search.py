import time
import wikipedia
import arxiv
from ddgs import DDGS
from langchain_core.tools import tool

# Tool 1: Wikipedia search.
@tool
def wiki_tool(query: str) -> str:
    """
    If the lesson is about history, definitions, standard concepts, or famous people
    search Wikipedia for encyclopedic background on a topic.
    """
    try:
        wikipedia.set_lang("en")
        summary = wikipedia.summary(query, sentences=8, auto_suggest=True)
        return f"[Wikipedia: {query}]\n{summary}"
    except wikipedia.exceptions.DisambiguationError as e:
        try:
            fallback = wikipedia.summary(e.options[0], sentences=8, auto_suggest=False)
            return f"[Wikipedia: {e.options[0]}]\n{fallback}"
        except Exception:
            return f"Could not retrieve Wikipedia content for: {query}"
    except wikipedia.exceptions.PageError:
        return f"No Wikipedia page found for: {query}"
    except Exception as e:
        return f"Wikipedia search failed: {str(e)}"
    
# Tool 2: Arxiv search
@tool
def arxiv_tool(query: str) -> str:
    """
    If the lesson is about deep learning architectures, quantum physics, math theorems, or bleeding-edge research,
    search ArXiv for academic papers and research.
    """
    try:
        client = arxiv.Client()
        search = arxiv.Search(query=query, max_results=3, sort_by=arxiv.SortCriterion.Relevance)
        results = list(client.results(search))
        
        if not results:
            return f"No ArXiv papers found for: {query}"
        
        summaries = []
        for paper in results:
            summaries.append(
                f"Title: {paper.title}\n"
                f"Authors: {', '.join(str(a) for a in paper.authors[:3])}\n"
                f"Abstract: {paper.summary[:500]}"
            )
        return f"[ArXiv: {query}]\n\n" + "\n\n---\n\n".join(summaries)
    except Exception as e:
        return f"ArXiv search failed: {str(e)}"
    
# Tool 3: Duckduckgo search
@tool
def search_tool(query: str) -> str:
    """
     For EVERYTHING else. Especially: "How to install...", "Best practices for...", "Current events", "Code examples".
    Search the web via DuckDuckGo for general information.
    Best for: current events, practical how-to topics, business concepts, pop culture,
    anything too recent or niche for Wikipedia or ArXiv.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))
        
        if not results:
            return f"No web results found for: {query}"
        
        snippets = [f"{r['title']}: {r['body']}" for r in results]
        return f"[DuckDuckGo: {query}]\n\n" + "\n\n".join(snippets)
    except Exception as e:
        return f"DuckDuckGo search failed: {str(e)}"

# Putting all tools together in a list.
SEARCH_TOOLS = [wiki_tool, arxiv_tool, search_tool]

