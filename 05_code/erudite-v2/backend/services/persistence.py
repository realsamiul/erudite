import os
import modal
import hashlib
from typing import Optional, Dict, Any

def compute_provenance_hash(
    prev_hash: str,
    query: str,
    answer: str,
    context: str
) -> str:
    """
    Computes a tamper-evident SHA256 provenance signature.
    Chains the current exchange immutably to the prior session hash.
    """
    hasher = hashlib.sha256()
    hasher.update(prev_hash.encode("utf-8"))
    hasher.update(query.encode("utf-8"))
    hasher.update(answer.encode("utf-8"))
    hasher.update(context.encode("utf-8"))
    return hasher.hexdigest()

async def log_session_state(
    session_id: str,
    query: str,
    answer: str,
    context: str
) -> str:
    """
    Logs the current exchange to the serverless Modal persistence volume,
    automatically retrieving the previous hash and returning the newly chained hash.
    """
    # Fallback default hash for genesis block
    prev_hash = "0" * 64
    
    try:
        # Retrieve the latest session block directly from the Modal app keylessly
        lookup_func = modal.Function.lookup("docrag-persistence", "get_job")
        latest_session = lookup_func(session_id)
        
        if latest_session and "provenance_hash" in latest_session:
            prev_hash = latest_session["provenance_hash"]
            
    except Exception as e:
        print(f"[Persistence] Prior hash lookup warning: {e}")
        
    # Calculate the new chained hash
    new_hash = compute_provenance_hash(prev_hash, query, answer, context)
    
    payload = {
        "session_id": session_id,
        "query": query,
        "answer": answer,
        "provenance_hash": new_hash
    }
    
    try:
        # Commit the session block permanently to Modal
        commit_func = modal.Function.lookup("docrag-persistence", "save_job")
        commit_func(session_id, payload)
        print(f"[Persistence] Successfully committed session block: {new_hash[:8]}...")
    except Exception as e:
        print(f"[Persistence] Commit failed: {e}")
        
    return new_hash
