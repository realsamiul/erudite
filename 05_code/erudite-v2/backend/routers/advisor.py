from fastapi import APIRouter, Depends, HTTPException
from models.schemas import AdvisorQueryRequest, AdvisorQueryResponse
from middleware.auth import verify_token
from services.discovery import retrieve_snippets
from services.gemini import synthesize_counselor_response
from services.persistence import log_session_state

router = APIRouter()

@router.post("/query", response_model=AdvisorQueryResponse)
async def query_counselor(
    request: AdvisorQueryRequest,
    decoded_token: dict = Depends(verify_token)
):
    """
    Main counseling intelligence endpoint.
    Performs standard Search retrieval, synthesizes a scannable empathetic response,
    and commits a cryptographically chained audit record to Modal.
    """
    # 1. Retrieve the relevant document snippets keylessly from Discovery Engine
    retrieved_chunks = await retrieve_snippets(
        query=request.question,
        category=request.category,
        top_k=5
    )
    
    # 2. Synthesize the scannable, structured counselor JSON response
    counselor_payload = await synthesize_counselor_response(
        query=request.question,
        retrieved_chunks=retrieved_chunks
    )
    
    # 3. Format the retrieved text for ledger logging
    context_str = "\n".join(chunk.text for chunk in retrieved_chunks)
    
    # 4. Compute and commit the provenance chained hash directly to Modal
    provenance_hash = await log_session_state(
        session_id=request.session_id,
        query=request.question,
        answer=counselor_payload.get("answer", ""),
        context=context_str
    )
    
    # 5. Pack and return the verified response payload
    return AdvisorQueryResponse(
        greeting=counselor_payload.get("greeting", "Hello, let's look at this together."),
        answer=counselor_payload.get("answer", "No answer compiled."),
        quick_stats=counselor_payload.get("quick_stats", []),
        charts=counselor_payload.get("charts", []),
        audit_feedback=counselor_payload.get("audit_feedback", {
            "loopholes": "Awaiting document synchronization.",
            "curriculum_warnings": "National curriculum evaluation is active.",
            "pipeline_alerts": "No pipeline bias observed."
        }),
        provenance_hash=provenance_hash
    )
