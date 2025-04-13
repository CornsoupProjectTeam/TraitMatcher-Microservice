from typing import List, Tuple
import numpy as np

# 초기 솔루션 필터링
def filtering_solutions(
        initial_solutions: List[List[List[Tuple[np.ndarray, str]]]],
        avg_threshold: float = 70.0,
        min_threshold: float = 65.0
) -> List[Tuple[List[List[Tuple[np.ndarray, str]]], List[float]]]:
    """
    초기 솔루션 리스트를 필터링

    - 각 팀이 최소 기준을 만족해야 함
    - 솔루션 내 최저 팀 점수가 기준 이상
    - 솔루션 전체 평균 점수가 기준 이상
    """

    filtered = []

    for teams in initial_solutions:
        # 1. 팀 점수 계산
        team_scores = [calculate_team_score(team) for team in teams]

        # 2. 각 팀이 최소 기준을 모두 통과하는지 확인
        if not all(passes_minimum_criteria(team) for team in teams):
            continue

        # 3. 솔루션 평균 점수와 최저 팀 점수 기준 통과 여부 확인
        if not is_valid_solution(team_scores, avg_threshold, min_threshold):
            continue

        # 4. 모든 기준 통과 시 솔루션 채택
        filtered.append((teams, team_scores))

    return filtered

# 팀 점수 계산
def calculate_team_score(team: List[Tuple[np.ndarray, str]]) -> float:
    """
    하나의 팀에 대해 가중치 기반으로 점수를 계산
    """
    team_vectors = np.array([vec for vec, _ in team])

    weights = {
        "성실성 평균": 20.22,
        "친화성 평균": 20.22,
        "성실성 유사도": 16.18,
        "친화성 유사도": 16.18,
        "개방성 다양성": 12.14,
        "외향성 다양성": 8.09,
        "신경증 유사도": 4.05,
        "개방성 평균": 0.97,
        "외향성 평균": 0.97,
        "신경증 평균": 0.97,
    }

    conscientiousness_mean = team_vectors[:, 0].mean()
    agreeableness_mean = team_vectors[:, 1].mean()
    openness_mean = team_vectors[:, 2].mean()
    extraversion_mean = team_vectors[:, 3].mean()
    neuroticism_mean = team_vectors[:, 4].mean()

    conscientiousness_std = team_vectors[:, 0].std()
    agreeableness_std = team_vectors[:, 1].std()
    openness_var = team_vectors[:, 2].var()
    extraversion_var = team_vectors[:, 3].var()
    neuroticism_std = team_vectors[:, 4].std()

    score = 0
    score += (1 - abs(conscientiousness_mean - 50) / 50) * weights["성실성 평균"]
    score += (1 - abs(agreeableness_mean - 50) / 50) * weights["친화성 평균"]
    score += (1 - conscientiousness_std / 50) * weights["성실성 유사도"]
    score += (1 - agreeableness_std / 50) * weights["친화성 유사도"]
    score += (openness_var / 50) * weights["개방성 다양성"]
    score += (extraversion_var / 50) * weights["외향성 다양성"]
    score += (1 - neuroticism_std / 50) * weights["신경증 유사도"]
    score += (1 - abs(openness_mean - 50) / 50) * weights["개방성 평균"]
    score += (1 - abs(extraversion_mean - 50) / 50) * weights["외향성 평균"]
    score += (1 - abs(neuroticism_mean - 50) / 50) * weights["신경증 평균"]

    return round(score, 2)

# 팀 최소 기준 평가
def passes_minimum_criteria(team: List[Tuple[np.ndarray, str]]) -> bool:
    """
    팀이 최소 기준(친화성 유사도와 성실성 평균 또는 유사도)을 만족하는지 검사
    """
    team_vectors = np.array([vec for vec, _ in team])
    conscientiousness_mean = team_vectors[:, 0].mean()
    conscientiousness_std = team_vectors[:, 0].std()
    agreeableness_std = team_vectors[:, 1].std()

    # (1) 성실성 평균이 높고 친화성 유사도가 높을 때
    if conscientiousness_mean >= 75 and agreeableness_std <= 5:
        return True

    # (2) 성실성과 친화성 모두 유사도가 높을 때
    if conscientiousness_std <= 5 and agreeableness_std <= 5:
        return True

    return False

# 솔루션 품질 평가
def is_valid_solution(team_scores: List[float], avg_threshold: float, min_threshold: float) -> bool:
    """
    솔루션이 평균 점수와 최저 팀 점수 기준을 모두 만족하는지 검사
    """
    if not team_scores:
        return False

    min_score = min(team_scores)
    avg_score = sum(team_scores) / len(team_scores)

    return min_score >= min_threshold and avg_score >= avg_threshold