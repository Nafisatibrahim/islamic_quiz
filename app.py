import streamlit as st
import json
import random
import time
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
    
    if 'question_start_time' not in st.session_state:
        st.session_state.question_start_time = None
    
    if 'nafi_choice' not in st.session_state:
        st.session_state.nafi_choice = None
    
    if 'moya_choice' not in st.session_state:
        st.session_state.moya_choice = None

def validate_answers():
    current_quiz = st.session_state.quizzes[st.session_state.current_question]
    correct_answer = current_quiz['answer']
    
    st.session_state.answered = True
    
    if st.session_state.nafi_choice == correct_answer:
        st.session_state.nafi_score += 1
    
    if st.session_state.moya_choice == correct_answer:
        st.session_state.moya_score += 1

def next_question():
    st.session_state.current_question += 1
    st.session_state.answered = False
    st.session_state.nafi_choice = None
    st.session_state.moya_choice = None
    st.session_state.question_start_time = time.time() if st.session_state.timer_enabled else None

def reset_quiz(save_current=False):
    if save_current and len(st.session_state.quizzes) > 0:
        save_session(
            st.session_state.nafi_score,
            st.session_state.moya_score,
            len(st.session_state.quizzes)
        )
    
    st.session_state.current_question = 0
    st.session_state.nafi_score = 0
    st.session_state.moya_score = 0
    st.session_state.answered = False
    st.session_state.nafi_choice = None
    st.session_state.moya_choice = None
    st.session_state.question_start_time = None
    filtered = filter_quizzes(st.session_state.all_quizzes, st.session_state.selected_category, st.session_state.selected_difficulty)
    st.session_state.quizzes = filtered.copy() if filtered else st.session_state.all_quizzes.copy()
    random.shuffle(st.session_state.quizzes)

initialize_session()

with st.sidebar:
    st.title("📚 Navigation")
    page = st.radio("Menu", ["🎮 Quiz", "🏆 Classement", "📊 Historique", "⚙️ Paramètres"])
    
    if page == "🎮 Quiz":
        st.divider()
        st.subheader("Filtres")
        
        categories = ["Toutes"] + sorted(list(set([q.get('category', 'Toutes') for q in st.session_state.all_quizzes])))
        difficulties = ["Toutes", "Facile", "Moyen", "Difficile"]
        
        category = st.selectbox("Catégorie", categories, index=categories.index(st.session_state.selected_category))
        difficulty = st.selectbox("Difficulté", difficulties, index=difficulties.index(st.session_state.selected_difficulty))
        
        if category != st.session_state.selected_category or difficulty != st.session_state.selected_difficulty:
            st.session_state.selected_category = category
            st.session_state.selected_difficulty = difficulty
            filtered = filter_quizzes(st.session_state.all_quizzes, category, difficulty)
            if filtered and len(filtered) > 0:
                st.session_state.quizzes = filtered.copy()
                random.shuffle(st.session_state.quizzes)
                st.session_state.current_question = 0
                st.session_state.nafi_score = 0
                st.session_state.moya_score = 0
                st.session_state.answered = False
                st.session_state.nafi_choice = None
                st.session_state.moya_choice = None
                st.session_state.question_start_time = None
                st.session_state.quiz_saved = False
                st.rerun()
            else:
                st.warning("Aucun quiz ne correspond à ces critères. Veuillez modifier vos filtres.")
        
        st.divider()
        st.subheader("Chronomètre")
        timer_enabled = st.checkbox("Activer le chronomètre", value=st.session_state.timer_enabled)
        if timer_enabled != st.session_state.timer_enabled:
            st.session_state.timer_enabled = timer_enabled
        
        if timer_enabled:
            timer_duration = st.slider("Durée (secondes)", 10, 120, st.session_state.timer_duration, 5)
            if timer_duration != st.session_state.timer_duration:
                st.session_state.timer_duration = timer_duration

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

elif page == "⚙️ Paramètres":
    st.title("⚙️ Paramètres")
    
    st.subheader("📤 Importer des questions personnalisées")
    st.info("Téléchargez un fichier JSON avec vos propres questions de quiz.")
    
    uploaded_file = st.file_uploader("Choisir un fichier JSON", type=['json'])
    
    if uploaded_file is not None:
        try:
            custom_quizzes = json.load(uploaded_file)
            
            if 'quizzes' in custom_quizzes and isinstance(custom_quizzes['quizzes'], list):
                if len(custom_quizzes['quizzes']) == 0:
                    st.error("Le fichier JSON doit contenir au moins une question.")
                else:
                    st.success(f"✅ {len(custom_quizzes['quizzes'])} questions chargées avec succès !")
                    
                    if st.button("Utiliser ces questions"):
                        with open('quizzes.json', 'w', encoding='utf-8') as f:
                            json.dump(custom_quizzes, f, ensure_ascii=False, indent=2)
                        
                        st.session_state.all_quizzes = custom_quizzes['quizzes']
                        st.session_state.quizzes = st.session_state.all_quizzes.copy()
                        random.shuffle(st.session_state.quizzes)
                        st.session_state.current_question = 0
                        st.session_state.nafi_score = 0
                        st.session_state.moya_score = 0
                        st.session_state.answered = False
                        st.session_state.nafi_choice = None
                        st.session_state.moya_choice = None
                        st.session_state.quiz_saved = False
                        
                        st.success("Questions importées et quiz réinitialisé !")
                        st.rerun()
            else:
                st.error("Le fichier JSON doit contenir une clé 'quizzes' avec une liste de questions.")
        except json.JSONDecodeError:
            st.error("Erreur : Le fichier n'est pas un JSON valide.")
        except Exception as e:
            st.error(f"Erreur lors du chargement : {str(e)}")
    
    st.divider()
    st.subheader("📋 Format attendu")
    st.code('''
{
  "quizzes": [
    {
      "question": "Votre question ?",
      "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
      "answer": "Option correcte",
      "category": "Catégorie",
      "difficulty": "Facile"
    }
  ]
}
    ''', language='json')

elif page == "🎮 Quiz":
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
        
        if st.session_state.timer_enabled and not st.session_state.answered:
            if st.session_state.question_start_time is None:
                st.session_state.question_start_time = time.time()
            
            elapsed = time.time() - st.session_state.question_start_time
            remaining = max(0, st.session_state.timer_duration - elapsed)
            
            timer_placeholder = st.empty()
            if remaining > 0:
                timer_placeholder.info(f"⏱️ Temps restant : {int(remaining)} secondes")
            else:
                timer_placeholder.error("⏰ Temps écoulé !")
                if not st.session_state.answered:
                    validate_answers()
                    st.rerun()
        
        st.markdown(f"### {current_quiz['question']}")
        st.write("")
        
        if not st.session_state.answered:
            col_nafi, col_center, col_moya = st.columns([2, 0.5, 2])
            
            with col_nafi:
                st.markdown("#### 🔵 Réponse de Nafi")
                for idx, option in enumerate(current_quiz['options']):
                    button_type = "primary" if st.session_state.nafi_choice == option else "secondary"
                    if st.button(f"{chr(65+idx)}. {option}", key=f"nafi_{idx}", 
                               use_container_width=True, type=button_type):
                        st.session_state.nafi_choice = option
                        st.rerun()
            
            with col_moya:
                st.markdown("#### 🔴 Réponse de Moya")
                for idx, option in enumerate(current_quiz['options']):
                    button_type = "primary" if st.session_state.moya_choice == option else "secondary"
                    if st.button(f"{chr(65+idx)}. {option}", key=f"moya_{idx}", 
                               use_container_width=True, type=button_type):
                        st.session_state.moya_choice = option
                        st.rerun()
            
            st.write("")
            
            both_answered = st.session_state.nafi_choice is not None and st.session_state.moya_choice is not None
            if both_answered:
                if st.button("✅ Valider les réponses", use_container_width=True, type="primary"):
                    validate_answers()
                    st.rerun()
            else:
                missing = []
                if st.session_state.nafi_choice is None:
                    missing.append("Nafi")
                if st.session_state.moya_choice is None:
                    missing.append("Moya")
                st.info(f"⏳ En attente de la réponse de : {', '.join(missing)}")
        else:
            col_nafi, col_center, col_moya = st.columns([2, 0.5, 2])
            
            with col_nafi:
                st.markdown("#### 🔵 Réponse de Nafi")
                for idx, option in enumerate(current_quiz['options']):
                    if option == current_quiz['answer'] and option == st.session_state.nafi_choice:
                        st.success(f"✅ {chr(65+idx)}. {option}")
                    elif option == st.session_state.nafi_choice:
                        st.error(f"❌ {chr(65+idx)}. {option}")
                    elif option == current_quiz['answer']:
                        st.info(f"✓ {chr(65+idx)}. {option}")
                    else:
                        st.markdown(f"{chr(65+idx)}. {option}")
            
            with col_moya:
                st.markdown("#### 🔴 Réponse de Moya")
                for idx, option in enumerate(current_quiz['options']):
                    if option == current_quiz['answer'] and option == st.session_state.moya_choice:
                        st.success(f"✅ {chr(65+idx)}. {option}")
                    elif option == st.session_state.moya_choice:
                        st.error(f"❌ {chr(65+idx)}. {option}")
                    elif option == current_quiz['answer']:
                        st.info(f"✓ {chr(65+idx)}. {option}")
                    else:
                        st.markdown(f"{chr(65+idx)}. {option}")
            
            st.write("")
            
            results_col1, results_col2 = st.columns(2)
            with results_col1:
                if st.session_state.nafi_choice == current_quiz['answer']:
                    st.success("🎉 Nafi a trouvé la bonne réponse ! +1 point")
                else:
                    st.error("❌ Nafi s'est trompé")
            
            with results_col2:
                if st.session_state.moya_choice == current_quiz['answer']:
                    st.success("🎉 Moya a trouvé la bonne réponse ! +1 point")
                else:
                    st.error("❌ Moya s'est trompé")
            
            if st.session_state.nafi_choice == current_quiz['answer'] or st.session_state.moya_choice == current_quiz['answer']:
                st.balloons()
            
            st.write("")
            if st.session_state.current_question < len(st.session_state.quizzes) - 1:
                if st.button("➡️ Question suivante", use_container_width=True):
                    next_question()
                    st.rerun()
            else:
                st.info("C'était la dernière question !")
                if st.button("🏁 Voir les résultats", use_container_width=True):
                    st.session_state.current_question += 1
                    st.rerun()

    else:
        if 'quiz_saved' not in st.session_state or not st.session_state.quiz_saved:
            save_session(
                st.session_state.nafi_score,
                st.session_state.moya_score,
                len(st.session_state.quizzes)
            )
            st.session_state.quiz_saved = True
        
        st.success("🎊 Quiz terminé !")
        st.write("")
        
        st.markdown("### 🏆 Résultats finaux")
        
        col1, col2 = st.columns(2)
        total_questions = len(st.session_state.quizzes)
        if total_questions > 0:
            nafi_pct = (st.session_state.nafi_score / total_questions * 100)
            moya_pct = (st.session_state.moya_score / total_questions * 100)
        else:
            nafi_pct = 0
            moya_pct = 0
        
        with col1:
            st.metric("🔵 Nafi", st.session_state.nafi_score, f"{nafi_pct:.1f}%")
        with col2:
            st.metric("🔴 Moya", st.session_state.moya_score, f"{moya_pct:.1f}%")
        
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
        st.session_state.quiz_saved = False
        reset_quiz(save_current=False)
        st.rerun()
