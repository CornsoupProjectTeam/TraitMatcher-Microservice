from app.repository.member_repository import get_members_by_matching_id
from app.services.solution_filtering_service import filtering_solutions
from app.services.best_solution_selector import select_best_solution
from app.services.trait_evaluation_service import evaluate_team_traits
from app.config.settings import settings
from typing import List, Tuple
import random
import numpy as np
from app.models.member_view import MemberView
from datetime import datetime
from zoneinfo import ZoneInfo

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
    best_solution = select_best_solution(filtered_solutions)

    # 6. 팀 평가 점수 추출
    evaluated_teams = evaluate_team_traits(best_solution)

    # 6. kafka payload 생성
    payload = {
        "matchingId": matching_id,
        "teams": evaluated_teams,
        "timestamp": datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%dT%H:%M:%S+09:00")
    }

    # 7. Kafka 발행
    settings.KAFKA_PRODUCER.send(
        "team_matching_results",
        value=payload
    )

    # 8. Kafka close
    settings.KAFKA_PRODUCER.flush()

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
    MAX_SOLUTIONS = 10000
    MIN_SOLUTIONS = 1000

    num_members = len(vectors)

    # 총 솔루션 개수 계산
    num_teams = num_members // team_size
    num_solutions = max(MIN_SOLUTIONS, min(num_teams * multiplier, MAX_SOLUTIONS))

    solutions = []

    for _ in range(num_solutions):
        shuffled_pairs = vectors.copy()
        random.shuffle(shuffled_pairs)

        teams = [
            shuffled_pairs[i:i + team_size]
            for i in range(0, num_members, team_size)
        ]

        solutions.append(teams)

    return solutions