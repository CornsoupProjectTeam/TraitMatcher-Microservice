from typing import List, Tuple
import numpy as np
import random
from decimal import Decimal

# 타입 정의
VectorWithID = Tuple[np.ndarray, str]  # (성향 벡터, member_id)
Team = List[VectorWithID]
Solution = List[Team]

# 가중치 상수 (총합 100)
WEIGHTS = {
    "conscientiousness_mean": Decimal("20.82"),
    "agreeableness_mean": Decimal("20.82"),
    "conscientiousness_similarity": Decimal("16.67"),
    "agreeableness_similarity": Decimal("16.67"),
    "openness_diversity": Decimal("12.50"),
    "extraversion_diversity": Decimal("8.33"),
    "neuroticism_similarity": Decimal("4.19"),
}

# 팀 점수 계산 함수
def calculate_team_score(vectors: List[np.ndarray]) -> float:
    v = np.array(vectors)

    conscientiousness = v[:, 0]
    agreeableness = v[:, 1]
    openness = v[:, 2]
    extraversion = v[:, 3]
    neuroticism = v[:, 4]

    score = Decimal("0.0")

    # 평균 항목
    score += min(Decimal(conscientiousness.mean()) / Decimal("100.0"), Decimal("1.0")) * WEIGHTS["conscientiousness_mean"]
    score += min(Decimal(agreeableness.mean()) / Decimal("100.0"), Decimal("1.0")) * WEIGHTS["agreeableness_mean"]

    # 유사도 항목
    score += (Decimal("1.0") - min(Decimal(conscientiousness.std()) / Decimal("20.0"), Decimal("1.0"))) * WEIGHTS["conscientiousness_similarity"]
    score += (Decimal("1.0") - min(Decimal(agreeableness.std()) / Decimal("20.0"), Decimal("1.0"))) * WEIGHTS["agreeableness_similarity"]
    score += (Decimal("1.0") - min(Decimal(neuroticism.std()) / Decimal("20.0"), Decimal("1.0"))) * WEIGHTS["neuroticism_similarity"]

    # 다양성 항목
    score += min(Decimal(openness.var()) / Decimal("150.0"), Decimal("1.0")) * WEIGHTS["openness_diversity"]
    score += min(Decimal(extraversion.var()) / Decimal("150.0"), Decimal("1.0")) * WEIGHTS["extraversion_diversity"]

    return float(round(score, 2))


# 솔루션 점수 평가
def evaluate_solution(solution: Solution) -> float:
    team_scores = [
        calculate_team_score([vec for vec, _ in team]) for team in solution
    ]
    return sum(team_scores) / len(team_scores)


# 이웃 솔루션 생성 (두 멤버 교환)
def generate_neighbor(solution: Solution) -> Solution:
    new_solution = [team.copy() for team in solution]
    t1, t2 = random.sample(range(len(new_solution)), 2)
    if not new_solution[t1] or not new_solution[t2]:
        return new_solution
    i, j = random.randrange(len(new_solution[t1])), random.randrange(len(new_solution[t2]))
    new_solution[t1][i], new_solution[t2][j] = new_solution[t2][j], new_solution[t1][i]
    return new_solution

# SA 최적화
def simulated_annealing(initial_solution: Solution, iterations=1000, T_start=100.0, alpha=0.98):
    current = initial_solution
    best = current
    best_score = evaluate_solution(best)
    current_score = best_score
    T = T_start

    for _ in range(iterations):
        neighbor = generate_neighbor(current)
        neighbor_score = evaluate_solution(neighbor)
        delta = neighbor_score - current_score

        if delta > 0 or random.random() < np.exp(delta / T):
            current = neighbor
            current_score = neighbor_score
            if current_score > best_score:
                best = current
                best_score = current_score
        T *= alpha

    return best
