from app.repository.member_repository import get_members_by_matching_id
from app.services.SA_based_solution_selector import simulated_annealing, evaluate_solution
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

    best_overall_solution = None
    highest_avg_score = -1.0

    # 3. SA 알고리즘 반복 실행 및 최고 솔루션 선택
    for i in range(3):
        print(f"{i+1}/3: 초기 솔루션 생성 시작")

        # 무작위 단일 솔루션 생성
        initial_solution = create_random_solution(vectors, team_size)
        print(f"[{i+1}회차] 초기 솔루션 생성 완료")

        # SA 알고리즘 실행
        current_solution = simulated_annealing(initial_solution)

        # 솔루션 평균 팀 점수 계산
        avg_score = evaluate_solution(current_solution)
        print(f"▶ 반복 {i+1} 평균 팀 점수: {avg_score:.2f}")

        # 최고 점수 갱신
        if avg_score > highest_avg_score:
            highest_avg_score = avg_score
            best_overall_solution = current_solution

    # 최종 선택된 베스트 솔루션이 없을 경우
    if not best_overall_solution:
        print("세 번의 반복 중 유효한 베스트 솔루션을 찾지 못했습니다.")
        return

    best_solution = best_overall_solution

    # 4. 팀 평가 점수 추출
    evaluated_teams = evaluate_team_traits(best_solution)

    # 5. kafka payload 생성
    payload = {
        "matchingId": matching_id,
        "teams": evaluated_teams,
        "timestamp": datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%dT%H:%M:%S+09:00")
    }

    # 6. Kafka 발행
    settings.KAFKA_PRODUCER.send(
        "team_matching_results",
        value=payload
    )

    # 7. Kafka close
    settings.KAFKA_PRODUCER.flush()

# MemberView 리스트를 5차원 성향 벡터 배열 + 멤버 ID 튜플 리스트로 변환
def convert_members_to_vectors(members: List[MemberView]) -> List[Tuple[np.ndarray, str]]:
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

# 랜덤 솔루션 생성
def create_random_solution(vectors: List[Tuple[np.ndarray, str]], team_size: int):
    members = vectors[:]
    random.shuffle(members)

    solution = []
    for i in range(0, len(members), team_size):
        team = members[i:i+team_size]
        solution.append(team)

    return solution
