import asyncio
from typing import Optional, List
import os
from google.cloud import discoveryengine_v1beta as discoveryengine

class SearchChunk:
    """Represents a discrete text segment retrieved from our Discovery Engine search stores."""
    def __init__(self, text: str, source_display_name: str, score: float = 0.5):
        self.text = text
        self.source_display_name = source_display_name
        self.score = score

async def retrieve_snippets(
    query: str,
    category: str,
    top_k: int = 10
) -> List[SearchChunk]:
    """
    Retrieves relevant text segments keylessly and credit-safely 
    directly from our active Discovery Engine Search data stores.
    """
    PROJECT_ID = os.environ.get("PROJECT_ID", "project-a1f62154-a7ad-4b37-93b")
    
    # Select the matching search store
    if category.lower() == "statutes":
        data_store_id = "statutes-search-store"
    elif category.lower() == "it_security":
        data_store_id = "it-security-search-store"
    elif category.lower() == "clinical_safety":
        data_store_id = "clinical-safety-search-store"
    else:
        data_store_id = "statutes-search-store"
        
    serving_config = f"projects/{PROJECT_ID}/locations/global/collections/default_collection/dataStores/{data_store_id}/servingConfigs/default_search_config"
    print(f"[Discovery] Querying store '{data_store_id}' for: '{query}'...")
    
    client = discoveryengine.SearchServiceClient()
    loop = asyncio.get_event_loop()
    
    try:
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=top_k
        )
        
        # Run blocking gRPC client call in an executor thread to preserve event loop speed
        res = await loop.run_in_executor(
            None,
            lambda: client.search(request)
        )
        
        chunks = []
        for result in res.results:
            derived = result.document.derived_struct_data
            if not derived:
                continue
                
            text_content = ""
            if "extractive_segments" in derived:
                text_content = "\n".join(seg.get("content", "") for seg in derived["extractive_segments"])
            elif "snippets" in derived:
                text_content = "\n".join(snip.get("snippet", "") for snip in derived["snippets"])
            else:
                text_content = str(derived)
                
            chunks.append(SearchChunk(
                text=text_content,
                source_display_name=result.document.id or "Document Segment",
                score=0.75
            ))
            
        print(f"[Discovery] Successfully retrieved {len(chunks)} document chunks.")
        return chunks
        
    except Exception as e:
        print(f"[Discovery] Search failed: {e}")
        return []
