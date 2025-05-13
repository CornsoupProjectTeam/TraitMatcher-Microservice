from typing import List, Tuple, TypedDict
import numpy as np
from decimal import Decimal

VectorWithID = Tuple[np.ndarray, str]
Team = List[VectorWithID]
Solution = List[Team]
FilteredSolution = Tuple[Solution, List[float], float]  # 솔루션, 솔루션 내 각 팀의 점수, 솔루션 내 팀의 점수 평균

# 가중치 상수
WEIGHTS = {
    "성실성 평균": Decimal("20.82"),
    "친화성 평균": Decimal("20.82"),
    "성실성 유사도": Decimal("16.67"),
    "친화성 유사도": Decimal("16.67"),
    "개방성 다양성": Decimal("12.50"),
    "외향성 다양성": Decimal("8.33"),
    "신경증 유사도": Decimal("4.19"),
}

# 기준 상수
C_MEAN_THRESHOLD = Decimal("0.70")
C_STD_THRESHOLD = Decimal("0.75")
A_STD_THRESHOLD = Decimal("0.75")
MAX_STD = Decimal("15.0")
MAX_VAR = Decimal("150.0")

# 팀별 최소 기준 평가용 지표
class TeamTraits(TypedDict):
    conscientiousness_mean: float
    conscientiousness_std: float
    agreeableness_std: float

# 1차 솔루션 품질 기준
#DEFAULT_AVG_SCORE_THRESHOLD = 48.0
#DEFAULT_MIN_SCORE_THRESHOLD = 46.0

# 2차 솔루션 품질 기준
# DEFAULT_AVG_SCORE_THRESHOLD = 45.0
# DEFAULT_MIN_SCORE_THRESHOLD = 43.0

# 3차 솔루션 품질 기준
DEFAULT_AVG_SCORE_THRESHOLD = 46.0
DEFAULT_MIN_SCORE_THRESHOLD = 44.0

# 초기 솔루션 필터링
def filtering_solutions(
        initial_solutions: List[Solution]
) -> List[FilteredSolution]:
    """
    초기 솔루션 리스트를 필터링

    - 솔루션 내 각 팀이 최소 기준을 만족
    - 솔루션 내 최저 팀 점수가 기준 이상
    - 솔루션 전체 평균 점수가 기준 이상
    """

    filtered = []
    for teams in initial_solutions:
        # 1. 팀별 최소 기준 검사
        for team in teams:
            traits = get_team_traits(team)
            if not passes_minimum_criteria(traits):
                break
        else:
            # 2. 전체 솔루션 기준 검사
            team_scores = [calculate_team_score(team) for team in teams]
            if is_valid_solution(team_scores):
                avg_score = sum(team_scores) / len(team_scores)
                filtered.append((teams, team_scores, avg_score))

    return filtered

# 최소 기준 평가요소 계산
def get_team_traits(team: Team) -> TeamTraits:

    if not team:
        raise ValueError("팀이 비어 있습니다.")

    """
    팀의 핵심 성향 정보 (평균/유사도 등)를 반환하여 최소 기준 평가 등에 활용
    """
    vectors = np.array([vec for vec, _ in team])
    return {
        "conscientiousness_mean": vectors[:, 0].mean(),
        "conscientiousness_std": vectors[:, 0].std(),
        "agreeableness_std": vectors[:, 1].std(),
    }

# 팀 점수 계산
def calculate_team_score(team: Team) -> float:
    """
    하나의 팀에 대해 가중치 기반으로 정규화된 점수를 계산
    """

    if not team:
        raise ValueError("팀이 비어 있습니다.")

    team_vectors = np.array([vec for vec, _ in team])

    conscientiousness = team_vectors[:, 0]
    agreeableness = team_vectors[:, 1]
    openness = team_vectors[:, 2]
    extraversion = team_vectors[:, 3]
    neuroticism = team_vectors[:, 4]

    score = Decimal("0.0")

    # 평균 점수: 평균이 높을수록 평균 점수는 높아짐
    score += min(Decimal(conscientiousness.mean()) / Decimal("100.0"), Decimal("1.0")) * WEIGHTS["성실성 평균"]
    score += min(Decimal(agreeableness.mean()) / Decimal("100.0"), Decimal("1.0")) * WEIGHTS["친화성 평균"]

    # 유사도 점수: 표준편차가 클수록 유사도 점수는 작아짐
    score += (Decimal("1.0") - min(Decimal(conscientiousness.std()) / MAX_STD, Decimal("1.0"))) * WEIGHTS["성실성 유사도"]
    score += (Decimal("1.0") - min(Decimal(agreeableness.std()) / MAX_STD, Decimal("1.0"))) * WEIGHTS["친화성 유사도"]
    score += (Decimal("1.0") - min(Decimal(neuroticism.std()) / MAX_STD, Decimal("1.0"))) * WEIGHTS["신경증 유사도"]

    # 다양성 점수: 분산이 클수록 다양성 점수는 커짐
    score += min(Decimal(openness.var()) / MAX_VAR, Decimal("1.0")) * WEIGHTS["개방성 다양성"]
    score += min(Decimal(extraversion.var()) / MAX_VAR, Decimal("1.0")) * WEIGHTS["외향성 다양성"]

    return float(round(score, 2))

# 팀 최소 기준 평가
def passes_minimum_criteria(traits: TeamTraits) -> bool:
    """
    get_team_traits로 얻은 값 기반으로 팀 최소 기준 판단 수행
    """
    c_mean = Decimal(traits["conscientiousness_mean"]) / Decimal("100.0")
    c_std = Decimal(traits["conscientiousness_std"]) / MAX_STD
    a_std = Decimal(traits["agreeableness_std"]) / MAX_STD

    if c_mean >= C_MEAN_THRESHOLD or c_std <= C_STD_THRESHOLD or a_std <= A_STD_THRESHOLD:
        return True
    return False

# 솔루션 품질 평가
def is_valid_solution(team_scores: List[float]) -> bool:
    """
    솔루션이 평균 점수와 최저 팀 점수 기준을 모두 만족하는지 검사
    """
    if not team_scores:
        return False

    min_score = Decimal(min(team_scores))
    avg_score = Decimal(sum(team_scores)) / Decimal(len(team_scores))

    return (
            min_score >= DEFAULT_MIN_SCORE_THRESHOLD and
            avg_score >= DEFAULT_AVG_SCORE_THRESHOLD
    )