import streamlit as st
import json
import random
from database import init_db, save_session, get_leaderboard, get_all_sessions

st.set_page_config(page_title="Quiz Islamique - Nafi vs Moya", page_icon="📚", layout="wide")

init_db()

def load_quizzes():
    with open('quizzes.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['quizzes']

def filter_quizzes(all_quizzes, category, difficulty):
    filtered = all_quizzes
    if category != "Toutes":
        filtered = [q for q in filtered if q.get('category') == category]
    if difficulty != "Toutes":
        filtered = [q for q in filtered if q.get('difficulty') == difficulty]
    return filtered

def initialize_session():
    if 'all_quizzes' not in st.session_state:
        st.session_state.all_quizzes = load_quizzes()
    
    if 'quizzes' not in st.session_state:
        st.session_state.quizzes = st.session_state.all_quizzes.copy()
        random.shuffle(st.session_state.quizzes)
    
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    
    if 'nafi_score' not in st.session_state:
        st.session_state.nafi_score = 0
    
    if 'moya_score' not in st.session_state:
        st.session_state.moya_score = 0
    
    if 'answered' not in st.session_state:
        st.session_state.answered = False
    
    if 'last_answer' not in st.session_state:
        st.session_state.last_answer = None
    
    if 'last_player' not in st.session_state:
        st.session_state.last_player = None
    
    if 'selected_category' not in st.session_state:
        st.session_state.selected_category = "Toutes"
    
    if 'selected_difficulty' not in st.session_state:
        st.session_state.selected_difficulty = "Toutes"
    
    if 'timer_enabled' not in st.session_state:
        st.session_state.timer_enabled = False
    
    if 'timer_duration' not in st.session_state:
        st.session_state.timer_duration = 30

def check_answer(selected_option, player):
    current_quiz = st.session_state.quizzes[st.session_state.current_question]
    correct_answer = current_quiz['answer']
    
    st.session_state.answered = True
    st.session_state.last_answer = selected_option
    st.session_state.last_player = player
    
    if selected_option == correct_answer:
        if player == "Nafi":
            st.session_state.nafi_score += 1
        else:
            st.session_state.moya_score += 1
        return True
    return False

def next_question():
    st.session_state.current_question += 1
    st.session_state.answered = False
    st.session_state.last_answer = None
    st.session_state.last_player = None

def reset_quiz():
    if st.session_state.current_question >= len(st.session_state.quizzes):
        save_session(
            st.session_state.nafi_score,
            st.session_state.moya_score,
            len(st.session_state.quizzes)
        )
    
    st.session_state.current_question = 0
    st.session_state.nafi_score = 0
    st.session_state.moya_score = 0
    st.session_state.answered = False
    st.session_state.last_answer = None
    st.session_state.last_player = None
    filtered = filter_quizzes(st.session_state.all_quizzes, st.session_state.selected_category, st.session_state.selected_difficulty)
    st.session_state.quizzes = filtered.copy() if filtered else st.session_state.all_quizzes.copy()
    random.shuffle(st.session_state.quizzes)

initialize_session()

with st.sidebar:
    st.title("📚 Navigation")
    page = st.radio("Menu", ["🎮 Quiz", "🏆 Classement", "📊 Historique"])

if page == "🏆 Classement":
    st.title("🏆 Classement")
    
    leaderboard = get_leaderboard()
    
    if leaderboard:
        col1, col2 = st.columns(2)
        
        for stats in leaderboard:
            if stats.player_name == "Nafi":
                with col1:
                    st.subheader("🔵 Nafi")
                    st.metric("Parties jouées", stats.total_games)
                    st.metric("Victoires", stats.total_wins)
                    st.metric("Score total", stats.total_score)
                    st.metric("Moyenne", f"{stats.average_score:.2f}")
                    if stats.total_games > 0:
                        win_rate = (stats.total_wins / stats.total_games) * 100
                        st.metric("Taux de victoire", f"{win_rate:.1f}%")
            
            elif stats.player_name == "Moya":
                with col2:
                    st.subheader("🔴 Moya")
                    st.metric("Parties jouées", stats.total_games)
                    st.metric("Victoires", stats.total_wins)
                    st.metric("Score total", stats.total_score)
                    st.metric("Moyenne", f"{stats.average_score:.2f}")
                    if stats.total_games > 0:
                        win_rate = (stats.total_wins / stats.total_games) * 100
                        st.metric("Taux de victoire", f"{win_rate:.1f}%")
    else:
        st.info("Aucune partie jouée pour le moment. Commencez un quiz !")

elif page == "📊 Historique":
    st.title("📊 Historique des parties")
    
    sessions = get_all_sessions()
    
    if sessions:
        for session in sessions:
            with st.expander(f"{session.session_date.strftime('%d/%m/%Y %H:%M')} - {session.winner} gagne"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🔵 Nafi", session.nafi_score)
                with col2:
                    st.metric("Total questions", session.total_questions)
                with col3:
                    st.metric("🔴 Moya", session.moya_score)
    else:
        st.info("Aucune partie jouée pour le moment. Commencez un quiz !")

else:
    st.title("📚 Quiz Islamique")
    st.subheader("Nafi vs Moya")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.metric("🔵 Nafi", st.session_state.nafi_score)
    with col2:
        st.metric("📊 Question", f"{st.session_state.current_question + 1}/{len(st.session_state.quizzes)}")
    with col3:
        st.metric("🔴 Moya", st.session_state.moya_score)

    st.divider()

    if st.session_state.current_question < len(st.session_state.quizzes):
        current_quiz = st.session_state.quizzes[st.session_state.current_question]
        
        st.markdown(f"### {current_quiz['question']}")
        st.write("")
        
        if not st.session_state.answered:
            for idx, option in enumerate(current_quiz['options']):
                col_nafi, col_option, col_moya = st.columns([1, 3, 1])
                
                with col_option:
                    st.markdown(f"**{chr(65+idx)}.** {option}")
                
                with col_nafi:
                    if st.button(f"Nafi", key=f"nafi_{idx}", use_container_width=True):
                        is_correct = check_answer(option, "Nafi")
                        st.rerun()
                
                with col_moya:
                    if st.button(f"Moya", key=f"moya_{idx}", use_container_width=True):
                        is_correct = check_answer(option, "Moya")
                        st.rerun()
        else:
            for idx, option in enumerate(current_quiz['options']):
                if option == current_quiz['answer']:
                    st.success(f"✅ **{chr(65+idx)}.** {option} (Bonne réponse)")
                elif option == st.session_state.last_answer:
                    st.error(f"❌ **{chr(65+idx)}.** {option} (Réponse de {st.session_state.last_player})")
                else:
                    st.markdown(f"**{chr(65+idx)}.** {option}")
            
            st.write("")
            if st.session_state.last_answer == current_quiz['answer']:
                st.balloons()
                st.success(f"🎉 Bravo {st.session_state.last_player} ! +1 point")
            else:
                st.error(f"❌ Désolé {st.session_state.last_player}, la bonne réponse était : {current_quiz['answer']}")
            
            st.write("")
            if st.session_state.current_question < len(st.session_state.quizzes) - 1:
                if st.button("➡️ Question suivante", use_container_width=True):
                    next_question()
                    st.rerun()
            else:
                st.info("C'était la dernière question !")

    else:
        st.success("🎊 Quiz terminé !")
        st.write("")
        
        st.markdown("### 🏆 Résultats finaux")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🔵 Nafi", st.session_state.nafi_score, f"{(st.session_state.nafi_score/len(st.session_state.quizzes)*100):.1f}%")
        with col2:
            st.metric("🔴 Moya", st.session_state.moya_score, f"{(st.session_state.moya_score/len(st.session_state.quizzes)*100):.1f}%")
        
        st.write("")
        
        if st.session_state.nafi_score > st.session_state.moya_score:
            st.success("🏆 Nafi gagne !")
        elif st.session_state.moya_score > st.session_state.nafi_score:
            st.success("🏆 Moya gagne !")
        else:
            st.info("🤝 Égalité parfaite !")

    st.write("")
    st.divider()

    if st.button("🔄 Nouvelle session", use_container_width=True):
        reset_quiz()
        st.rerun()
