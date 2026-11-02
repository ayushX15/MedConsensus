import logging
from fastapi import APIRouter, HTTPException

from backend.models import CouncilRequest, CouncilResponse
from backend.pipeline import run_council

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["council"])


@router.post("/council", response_model=CouncilResponse)
async def council_endpoint(request: CouncilRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    try:
        result = await run_council(request.prompt)
        return result
    except Exception as e:
        logger.exception("Error in /api/council execution")
        raise HTTPException(status_code=502, detail=f"Medical pipeline error: {str(e)}")
