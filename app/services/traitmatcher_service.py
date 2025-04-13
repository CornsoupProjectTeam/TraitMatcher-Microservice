from app.repository.member_repository import get_members_by_matching_id
from app.services.solution_filtering_service import filtering_solutions
from typing import List, Tuple
import numpy as np
from app.models.member_view import MemberView

async def start_team_matching(matching_id: str, team_size:int):
    print(f"팀 매칭 연산 시작 - matchingId: {matching_id}")

    # 1. DB에서 matching_id에 해당하는 멤버 데이터 조회
    members = await get_members_by_matching_id(matching_id)
    if not members:
        print(f"해당 matching_id에 해당하는 멤버가 없습니다.")
        return

    # 2. 멤버 데이터를 5차원 벡터로 변환
    vectors = convert_members_to_vectors(members)
    print(f"멤버 데이터 벡터로 변환 완료 - matchingId: {matching_id}")

    # 3. 초기 솔루션 생성
    initial_solutions = create_initial_solutions(vectors, team_size)
    print(f"초기 솔루션 생성 완료 - matchingId: {matching_id}")

    # 4. 솔루션 평가 및 필터링
    filtered_solutions = filtering_solutions(initial_solutions)
    print(f"솔루션 필터링 완료: {len(filtered_solutions)}개 솔루션이 남았습니다. - matchingId: {matching_id}")

    # 5. 최적화 기반 매칭 (유전 알고리즘)
    # TODO: 나중에 유전 알고리즘으로 best_solution 최적화 선택
    # best_solution =

    # 6. 결과 저장 및 Kafka 발행
    # TODO: 최적화된 best_solution에서 최종 member_id 리스트 추출
    # final_member_ids = []
    # for team in best_solution:
    #     for vector, member_id in team:
    #         final_member_ids.append(member_id)

def convert_members_to_vectors(members: List[MemberView]) -> List[Tuple[np.ndarray, str]]:
    """
    MemberView 리스트를 5차원 성향 벡터 배열 + 멤버 ID 튜플 리스트로 변환
    """
    vectors = []

    for member in members:
        vector = np.array([
            member.CONSCIENTIOUSNESS_SCORE,
            member.AGREEABLENESS_SCORE,
            member.OPENNESS_SCORE,
            member.EXTRAVERSION_SCORE,
            member.NEUROTICISM_SCORE
        ])
        vectors.append((vector, member.MEMBER_ID))  # (벡터, 멤버 ID)

    return vectors

def create_initial_solutions(
        vectors: List[Tuple[np.ndarray, str]],
        team_size: int,
        multiplier: int = 100
) -> List[List[List[Tuple[np.ndarray, str]]]]:
    """
    멤버 벡터 배열을 무작위로 섞은 뒤 팀 크기에 맞게 분할하여 초기 솔루션 생성
    """
    num_members = len(vectors)

    # 총 솔루션 개수 계산
    num_teams = num_members // team_size
    num_solutions = num_teams * multiplier

    # 팀 분할 실시
    solutions = []

    for _ in range(num_solutions):
        # numpy로 빠르게 섞고, 리스트 변환
        shuffled_pairs = np.random.permutation(vectors).tolist()

        # 팀 단위로 분할
        teams = [
            shuffled_pairs[i:i+team_size]
            for i in range(0, num_members, team_size)
        ]

        solutions.append(teams)

    return solutions