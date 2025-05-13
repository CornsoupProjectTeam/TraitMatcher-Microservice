from typing import List, Tuple
import numpy as np
import math

VectorWithID = Tuple[np.ndarray, str]
Team = List[VectorWithID]
Solution = List[Team]

# 평가 기준 4척도
# 1: 낮다
# 2: 다소 낮다
# 3: 다소 높다
# 4: 높다

# 절대 평가 기준 (Top 25%, 50%, 75%) - 방향성 반영된 상태
PERCENTILE_THRESHOLDS = {
    "conscientiousnessSimilarity": [7.51, 9.57, 12.31],
    "agreeablenessSimilarity": [6.33, 8.36, 10.68],
    "neuroticismSimilarity": [8.91, 11.56, 14.53],
    "opennessDiversity": [101.61, 64.81, 39.46],
    "extraversionDiversity": [156.66, 99.43, 59.52]
}

# 어떤 trait이 낮을수록 좋은가?
REVERSE_DIRECTION = {
    "conscientiousnessSimilarity": True,
    "agreeablenessSimilarity": True,
    "neuroticismSimilarity": True,
    "opennessDiversity": False,
    "extraversionDiversity": False,
}

# trait 값의 현실적인 범위
BOUNDS_LIMITS = {
    "conscientiousnessSimilarity": (0.0, 20.0),
    "agreeablenessSimilarity": (0.0, 20.0),
    "neuroticismSimilarity": (0.0, 25.0),
    "opennessDiversity": (0.0, 300.0),
    "extraversionDiversity": (0.0, 300.0)
}

def get_eval(value: float, thresholds: list, reverse: bool) -> int:
    """
    절대 평가 기준에 따라 1~4등급 계산
    """
    if reverse:
        if value <= thresholds[0]: return 4
        elif value <= thresholds[1]: return 3
        elif value <= thresholds[2]: return 2
        else: return 1
    else:
        if value >= thresholds[0]: return 4
        elif value >= thresholds[1]: return 3
        elif value >= thresholds[2]: return 2
        else: return 1

def score_from_eval(key: str, eval: int, value: float, thresholds: list, reverse: bool) -> float:
    """
    Eval 구간에 따라 점수 범위 내 선형 보간 점수 생성 (좋을수록 점수 높음)
    """
    eval_score_ranges = {
        4: (85, 100),
        3: (70, 84),
        2: (55, 69),
        1: (40, 54),
    }

    lower_score, upper_score = eval_score_ranges[eval]

    lower_bound, upper_bound = BOUNDS_LIMITS[key]
    bounds = [lower_bound] + thresholds + [upper_bound]

    idx = eval - 1
    bound_low = bounds[idx]
    bound_high = bounds[idx + 1]

    denom = bound_high - bound_low
    if denom <= 0:
        ratio = 0.5
    else:
        ratio = (value - bound_low) / denom
        ratio = min(max(ratio, 0), 1)

    score = lower_score + (upper_score - lower_score) * (1 - ratio if reverse else ratio)
    return round(score, 2)

def grade_relative(score: float, avg: float) -> int:
    """
    상대 평가: 전역 평균을 기준으로 4단계 등급 평가
    """
    if score >= avg + 10:
        return 4
    elif score >= avg:
        return 3
    elif score >= avg - 10:
        return 2
    else:
        return 1

# 각 팀에 대해 주요 trait 점수 및 평가 추출
def evaluate_team_traits(solution: Solution) -> List[dict]:
    result = []

    # 솔루션 평균 계산
    all_vectors = np.array([vec for team in solution for vec, _ in team])
    global_averages = {
        "conscientiousnessMean": all_vectors[:, 0].mean(),
        "agreeablenessMean": all_vectors[:, 1].mean(),
    }

    # 팀 별 trait 점수 생성
    for i, team in enumerate(solution):
        vectors = np.array([vec for vec, _ in team])
        memberIds = [member_id for _, member_id in team]

        conscientiousness = vectors[:, 0]
        agreeableness = vectors[:, 1]
        openness = vectors[:, 2]
        extraversion = vectors[:, 3]
        neuroticism = vectors[:, 4]

        traits = {
            "conscientiousnessSimilarity": conscientiousness.std(),
            "conscientiousnessMean": conscientiousness.mean(),
            "agreeablenessSimilarity": agreeableness.std(),
            "agreeablenessMean": agreeableness.mean(),
            "opennessDiversity": openness.var(),
            "extraversionDiversity": extraversion.var(),
            "neuroticismSimilarity": neuroticism.std(),
        }

        graded_traits = {}

        for key, value in traits.items():
            if key in global_averages:
                avg = global_averages[key]
                graded_traits[f"{key}Score"] = round(value, 2)
                graded_traits[f"{key}Eval"] = grade_relative(value, avg)
            else:
                thresholds = PERCENTILE_THRESHOLDS[key]
                reverse = REVERSE_DIRECTION[key]
                eval_score = get_eval(value, thresholds, reverse)
                score = score_from_eval(key, eval_score, value, thresholds, reverse)

                graded_traits[f"{key}Score"] = score
                graded_traits[f"{key}Eval"] = eval_score

        # ✅ 팀 평가가 모두 끝난 후에 result에 한 번 추가
        result.append({
            "teamIndex": i + 1,
            "memberIds": memberIds,
            **graded_traits
        })

    return result