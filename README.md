# [최유진] TraitMatcher Microservice
**Simulated Annealing 기반 팀 매칭 서버**

사용자의 성향 점수를 바탕으로 팀 조합을 계산하는 서비스입니다.

DB에서 매칭 대상 유저의 성향 데이터를 가져와
Simulated Annealing 알고리즘으로 더 적합한 팀 구성을 찾고,
최종 팀 매칭 결과를 Kafka로 전달합니다.

---

## 기술 스택

- Python 3.11.0
- FastAPI
- Kafka (비동기 메시지 브로커)
- SQLAlchemy / asyncpg
- NumPy
- JWT 인증
