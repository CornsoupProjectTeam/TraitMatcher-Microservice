from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from app.security.authentication import verify_and_extract_matching_id
from app.services.traitmatcher_service import start_team_matching

import asyncio

router = APIRouter()

class StartMatchingRequest(BaseModel):
    teamSize: int

@router.post("/start")
async def start_matching(
        request: StartMatchingRequest,
        authorization: str = Header(...)
):
    # 1. Authorization 헤더에서 Bearer 토큰 추출
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header must start with 'Bearer'.")

    token = authorization.removeprefix("Bearer ").strip()

    # 2. 토큰 검증 + matching_id 추출
    matching_id = verify_and_extract_matching_id(token)
    if matching_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    # 3. Body에서 teamSize를 추출
    team_size = request.teamSize

    # 4. 팀매칭 로직을 비동기로 실행
    asyncio.create_task(start_team_matching(matching_id, team_size))

    # 5. 바로 응답
    return "", 202
