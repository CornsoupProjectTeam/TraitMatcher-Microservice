from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MemberView(Base):
    __tablename__ = 'MEMBER_VIEW'

    MEMBER_ID = Column(String, primary_key=True)
    MATCHING_ID = Column(String, nullable=False)
    OPENNESS_SCORE = Column(Integer, nullable=False)  # 개방성
    CONSCIENTIOUSNESS_SCORE = Column(Integer, nullable=False)  # 성실성
    EXTRAVERSION_SCORE = Column(Integer, nullable=False)  # 외향성
    AGREEABLENESS_SCORE = Column(Integer, nullable=False)  # 친화성
    NEUROTICISM_SCORE = Column(Integer, nullable=False)  # 신경증

