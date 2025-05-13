from typing import List, Tuple
import random
import numpy as np
from decimal import Decimal
from app.services.solution_filtering_service import calculate_team_score

# 타입 정의
VectorWithID = Tuple[np.ndarray, str]
Team = List[VectorWithID]
Solution = List[Team]
FilteredSolution = Tuple[Solution, List[float], float]  # 솔루션, 솔루션 내 각 팀의 점수, 솔루션 내 팀의 점수 평균

def select_best_solution(
        filtered_solutions: List[FilteredSolution],
        mutation_rate: float = 0.15
) -> Solution:
    """
    필터링된 솔루션 리스트를 유전 알고리즘을 통해 최적 솔루션으로 선택
    """
    if not filtered_solutions:
        raise ValueError("필터링된 솔루션이 없습니다.")

    # 동적 파라미터 설정
    n = len(filtered_solutions)

    # 최소 개수 조건 검사
    if n < 10:
        raise ValueError(f"유전 알고리즘을 실행하기 위한 최소 필터링 솔루션 수는 10개 이상이어야 합니다. 현재: {n}개")

    population_size = max(10, min(int(n * 0.5), 50))        # 최소 10, 최대 50
    elite_size = max(2, int(population_size * 0.25))        # 상위 25%
    generations = max(10, int(np.log2(n) * 5))              # 로그 기반 계산

    # 초기 population 구성
    population = select_initial_population(filtered_solutions, population_size)

    for _ in range(generations):
        # 1. 각 솔루션의 fitness 계산
        scored_population = [(solution, evaluate_solution(solution)) for solution in population]
        scored_population.sort(key=lambda x: x[1], reverse=True)

        # 2. 상위 elite 개체 선택
        elites = [sol for sol, _ in scored_population[:elite_size]]

        # 3. 선택된 elite를 기반으로 다음 세대 생성
        next_generation = elites.copy()
        while len(next_generation) < population_size:
            parent = random.choice(elites)
            child = crossover(parent)
            if random.random() < mutation_rate:
                child = mutate(child)
            next_generation.append(child)

        population = next_generation

    # 마지막 세대 중 가장 높은 점수의 솔루션 반환
    final_scored_population = [(sol, evaluate_solution(sol)) for sol in population]
    final_scored_population.sort(key=lambda x: x[1], reverse=True)
    return final_scored_population[0][0]

def select_initial_population(
        filtered_solutions: List[FilteredSolution],
        population_size: int
) -> List[Solution]:
    """
    필터링된 솔루션 중에서 초기 population 구성:
    - 상위 절반은 점수 기준으로 선별
    - 나머지 절반은 랜덤하게 선택
    """

    if len(filtered_solutions) <= population_size:
        return [fs[0] for fs in filtered_solutions]

    # 1. 상위 절반: 평균 팀 점수 기준 정렬
    sorted_by_score = sorted(
        filtered_solutions,
        key=lambda fs: fs[2],  # 평균 점수
        reverse=True
    )

    top_half = [fs[0] for fs in sorted_by_score[:population_size // 2]]

    # 2. 나머지 절반: 상위 절반 제외하고 랜덤 선택
    remaining_candidates = sorted_by_score[population_size // 2:]
    random_half = random.sample(
        [fs[0] for fs in remaining_candidates],
        k=population_size - len(top_half)
    )

    # 3. 병합하여 반환
    return top_half + random_half

def evaluate_solution(solution: Solution) -> float:
    """
    솔루션의 평균 팀 점수 계산
    """
    scores = [Decimal(calculate_team_score(team)) for team in solution]
    avg_score = sum(scores) / Decimal(len(scores))
    return float(round(avg_score, 2))

def crossover(parent: Solution) -> Solution:
    """
    단일 부모 솔루션을 기반으로 멤버 순서를 무작위로 섞고,
    동일한 팀 크기로 다시 분할하여 자식 솔루션을 생성
    """
    # 1. 부모 솔루션의 모든 멤버 평탄화
    all_members = [member for team in parent for member in team]

    # 2. 무작위로 멤버 섞기
    random.shuffle(all_members)

    # 3. 팀 크기 및 팀 수 파악
    if not parent or not parent[0]:
        raise ValueError("부모 솔루션이 유효한 팀 구성을 갖고 있지 않습니다.")
    team_size = len(parent[0])
    num_teams = len(parent)

    # 4. 재분할
    child = [
        all_members[i * team_size:(i + 1) * team_size]
        for i in range(num_teams)
    ]
    return child

def mutate(solution: Solution) -> Solution:
    """
    솔루션의 두 멤버를 서로 다른 팀 간에 무작위로 교환
    """
    new_solution = [team.copy() for team in solution]
    
    # 1. 서로 다른 두 팀 무작위 선택
    team_indices = list(range(len(new_solution)))
    t1, t2 = random.sample(team_indices, 2)
    
    # 2. 두 팀 중 한 팀이라도 비어있을 경우 mutate하지 않고 그대로 반환
    if not new_solution[t1] or not new_solution[t2]:
        return new_solution

    # 3. 두 멤버를 무작위 선택 및 교환
    m1_idx = random.randrange(len(new_solution[t1]))
    m2_idx = random.randrange(len(new_solution[t2]))
    new_solution[t1][m1_idx], new_solution[t2][m2_idx] = new_solution[t2][m2_idx], new_solution[t1][m1_idx]
    return new_solution
