from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    BigInteger,
)


from utils.database import Base


class Requests(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    release_year = Column(Integer)
    local_id = Column(Integer)
    tmdbid = Column(Integer)
    tvdbid = Column(Integer)
    user_id = Column(BigInteger)


class JellyfinAccounts(Base):
    __tablename__ = "jellyfin_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger)
    jellyfin_user_id = Column(String)
    deletion_time = Column(DateTime)
