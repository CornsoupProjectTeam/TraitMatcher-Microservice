from sqlalchemy import Column, String, Numeric
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MemberView(Base):
    __tablename__ = 'MEMBER_VIEW'

    MEMBER_ID = Column(String(41), primary_key=True)
    MATCHING_ID = Column(String(20), nullable=False)
    OPENNESS_SCORE = Column(Numeric(4, 2), nullable=False)  # 개방성
    CONSCIENTIOUSNESS_SCORE = Column(Numeric(4, 2), nullable=False)  # 성실성
    EXTRAVERSION_SCORE = Column(Numeric(4, 2), nullable=False)  # 외향성
    AGREEABLENESS_SCORE = Column(Numeric(4, 2), nullable=False)  # 친화성
    NEUROTICISM_SCORE = Column(Numeric(4, 2), nullable=False)  # 신경증
