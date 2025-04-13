from sqlalchemy.future import select
from app.models.member_view import MemberView
from app.config.settings import AsyncSessionLocal

async def get_members_by_matching_id(matching_id: str):
    """
    주어진 matching_id에 해당하는 멤버 리스트를 MEMBER_VIEW에서 조회
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MemberView).where(MemberView.MATCHING_ID == matching_id)
        )
        members = result.scalars().all()
        return members
