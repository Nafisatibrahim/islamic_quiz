from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv('DATABASE_URL')
Base = declarative_base()

if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        DATABASE_AVAILABLE = True
    except Exception as e:
        print(f"Warning: Database connection failed: {e}")
        DATABASE_AVAILABLE = False
        engine = None
        SessionLocal = None
else:
    print("Warning: DATABASE_URL not set, database features disabled")
    DATABASE_AVAILABLE = False
    engine = None
    SessionLocal = None

class QuizSession(Base):
    __tablename__ = "quiz_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_date = Column(DateTime, default=datetime.utcnow)
    nafi_score = Column(Integer)
    moya_score = Column(Integer)
    total_questions = Column(Integer)
    winner = Column(String)
    quiz_type = Column(String, default="standard")

class PlayerStats(Base):
    __tablename__ = "player_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, unique=True)
    total_games = Column(Integer, default=0)
    total_wins = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)

def init_db():
    if DATABASE_AVAILABLE:
        Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def save_session(nafi_score, moya_score, total_questions, quiz_type="standard"):
    if not DATABASE_AVAILABLE:
        return
    
    db = SessionLocal()
    try:
        if nafi_score > moya_score:
            winner = "Nafi"
        elif moya_score > nafi_score:
            winner = "Moya"
        else:
            winner = "Égalité"
        
        session = QuizSession(
            nafi_score=nafi_score,
            moya_score=moya_score,
            total_questions=total_questions,
            winner=winner,
            quiz_type=quiz_type
        )
        db.add(session)
        db.commit()
        
        update_player_stats(db, "Nafi", nafi_score, winner == "Nafi")
        update_player_stats(db, "Moya", moya_score, winner == "Moya")
        
    finally:
        db.close()

def update_player_stats(db, player_name, score, is_winner):
    stats = db.query(PlayerStats).filter(PlayerStats.player_name == player_name).first()
    
    if not stats:
        stats = PlayerStats(player_name=player_name)
        db.add(stats)
    
    stats.total_games += 1
    stats.total_score += score
    if is_winner:
        stats.total_wins += 1
    stats.average_score = stats.total_score / stats.total_games
    
    db.commit()

def get_player_stats(player_name):
    if not DATABASE_AVAILABLE:
        return None
    
    db = SessionLocal()
    try:
        stats = db.query(PlayerStats).filter(PlayerStats.player_name == player_name).first()
        return stats
    finally:
        db.close()

def get_all_sessions():
    if not DATABASE_AVAILABLE:
        return []
    
    db = SessionLocal()
    try:
        sessions = db.query(QuizSession).order_by(QuizSession.session_date.desc()).all()
        return sessions
    finally:
        db.close()

def get_leaderboard():
    if not DATABASE_AVAILABLE:
        return []
    
    db = SessionLocal()
    try:
        stats = db.query(PlayerStats).all()
        return stats
    finally:
        db.close()
