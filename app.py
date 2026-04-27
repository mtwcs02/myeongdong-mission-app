import streamlit as st
from data.spots import SPOTS
from utils.helpers import get_spot_by_id
from datetime import datetime
import random
import json
import streamlit.components.v1 as components

# 페이지 설정 (모바일 최적화를 위해 layout은 'centered' 추천하나 wide에서 반응형 대응)
st.set_page_config(
    page_title="명동 역사 탐방",
    page_icon="🏯",
    layout="wide",
    initial_sidebar_state="collapsed" # 모바일에서는 사이드바를 기본으로 닫음
)

# 커스텀 CSS (모바일 최적화)
st.markdown("""
    <style>
    /* 전체 배경 및 폰트 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    .main {
        background-color: #FAF9F6;
    }
    
    .stApp {
        background-color: #FAF9F6;
    }
    
    /* 버튼 모바일 최적화 및 크기 균일화 */
    div[data-testid="stSidebar"] .element-container,
    div[data-testid="stSidebar"] .stButton,
    div[data-testid="stSidebar"] .stButton > button,
    .stButton > button {
        width: 100% !important;
        border-radius: 12px !important;
        height: 4rem !important; /* 고정 높이 설정으로 크기 통일 */
        font-size: 1rem !important;
        font-weight: 700 !important;
        margin-bottom: 8px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        transition: all 0.2s !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important; /* 왼쪽 정렬 */
        text-align: left !important;
        padding: 0 15px !important;
    }
    
    /* 강조 버튼 (Primary) */
    .stButton>button[kind="primary"] {
        background-color: #007bff;
        border: none;
    }
    
    /* 보조 버튼 (Secondary) */
    .stButton>button[kind="secondary"] {
        background-color: #ffffff;
        color: #495057;
        border: 1px solid #dee2e6;
    }

    /* 미션 카드 스타일 */
    .mission-card {
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        border-left: 6px solid #007bff;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    
    .mission-card h4 {
        color: #212529;
        margin-top: 0;
    }

    /* 프리미엄 가이드북 카드 스타일 */
    .guidebook-card {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04);
        margin-bottom: 25px;
        border: 1px solid #f0f0f0;
    }
    
    /* 제목 스타일 개선 */
    h1 {
        color: #1E3A8A !important;
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.05em !important; /* 글자 간격 약간 넓힘 */
    }
    
    h2, h3 {
        color: #1E3A8A !important;
    }

    /* 단계 뱃지 스타일 */
    .step-badge {
        display: inline-block;
        padding: 8px 20px;
        background-color: #1E3A8A;
        color: white;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(30, 58, 138, 0.2);
    }
    
    /* 본문 텍스트 가독성 */
    .spot-description {
        font-size: 1.15rem !important;
        line-height: 1.8 !important;
        color: #444 !important;
    }
    .spot-description b {
        color: #1E3A8A !important;
        font-weight: 700 !important;
    }

    /* 모바일 반응형 최적화 */
    @media (max-width: 768px) {
        h1 {
            font-size: 1.8rem !important;
            letter-spacing: 0.02em !important;
        }
        .guidebook-card {
            padding: 20px !important;
            border-radius: 15px !important;
        }
        .step-badge {
            font-size: 0.9rem !important;
            padding: 6px 15px !important;
        }
        .spot-description {
            font-size: 1.05rem !important;
            line-height: 1.6 !important;
        }
        .stButton > button {
            height: 3.5rem !important;
        }
    }

    /* 이미지 테두리 둥글게 */
    .stImage img {
        border-radius: 12px;
    }
    
    /* 완주 날짜 도장 스타일 */
    .completion-stamp {
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%) rotate(-10deg);
        width: 220px;
        height: 220px;
        border: 5px double #D32F2F;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: rgba(211, 47, 47, 0.05);
        color: #D32F2F;
        font-family: 'Noto Sans KR', sans-serif;
        z-index: 100;
        pointer-events: none;
        box-shadow: 0 0 15px rgba(211, 47, 47, 0.2);
    }
    .completion-stamp .label {
        font-size: 1.2rem;
        font-weight: 800;
        margin-bottom: 5px;
        letter-spacing: 2px;
    }
    .completion-stamp .date {
        font-size: 1.5rem;
        font-weight: 900;
        border-top: 2px solid #D32F2F;
        border-bottom: 2px solid #D32F2F;
        padding: 5px 10px;
    }
    .completion-stamp .myeongdong {
        font-size: 0.9rem;
        margin-top: 5px;
        font-weight: 700;
    }
    
    /* 사이드바 제목 줄바꿈 방지 */
    [data-testid="stSidebar"] h1 {
        white-space: nowrap !important;
        font-size: 1.5rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# 상단 진행률 표시
def show_overall_progress():
    completed_count = sum(1 for p in st.session_state.spot_progress.values() if p['quizzed'])
    total_count = len(SPOTS)
    progress_val = completed_count / total_count
    
    st.write(f"**전체 미션 진행률: {completed_count}/{total_count}**")
    st.progress(progress_val)
    st.markdown("---")

# 화려한 폭죽 효과 (JavaScript)
def show_confetti():
    st.components.v1.html(
        """
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
        <script>
            var end = Date.now() + (2 * 1000);
            var colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'];

            (function frame() {
              confetti({
                particleCount: 3,
                angle: 60,
                spread: 55,
                origin: { x: 0 },
                colors: colors
              });
              confetti({
                particleCount: 3,
                angle: 120,
                spread: 55,
                origin: { x: 1 },
                colors: colors
              });

              if (Date.now() < end) {
                requestAnimationFrame(frame);
              }
            }());
        </script>
        """,
        height=0,
    )

# --- 자동 저장 및 불러오기 로직 (LocalStorage) ---
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    # 브라우저 저장소에서 데이터 읽어오기 시도 (JS -> Query Params)
    components.html("""
        <script>
            const saved = localStorage.getItem('myeongdong_mission_progress');
            if (saved) {
                const url = new URL(window.location.href);
                url.searchParams.set('load_p', btoa(unescape(encodeURIComponent(saved))));
                window.parent.location.href = url.href;
            }
        </script>
    """, height=0)

# Query Params에 로드된 데이터가 있다면 복구
if 'load_p' in st.query_params:
    try:
        import base64
        decoded = base64.b64decode(st.query_params['load_p']).decode('utf-8')
        data = json.loads(decoded)
        st.session_state.spot_progress = data.get('spot_progress', {})
        st.session_state.completed_missions = data.get('completed_missions', [])
        st.session_state.completion_date = data.get('completion_date', None)
        st.session_state.quiz_data = data.get('quiz_data', {})
        
        # 로드 후 쿼리 파라미터 제거 (무한 루프 방지)
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"데이터 복구 중 오류 발생: {e}")

# 세션 상태 초기화
if 'spot_progress' not in st.session_state or len(st.session_state.spot_progress) != len(SPOTS):
    st.session_state.spot_progress = {
        spot['id']: {'learned': False, 'authenticated': False, 'quizzed': False} 
        for spot in SPOTS
    }

if 'completed_missions' not in st.session_state:
    st.session_state.completed_missions = []

if 'current_spot_id' not in st.session_state:
    st.session_state.current_spot_id = None

if 'completion_date' not in st.session_state:
    st.session_state.completion_date = None

if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = {} # {spot_id: {'quiz_idx': 0, 'options': []}}

if 'trigger_balloons' not in st.session_state:
    st.session_state.trigger_balloons = False

if 'trigger_confetti' not in st.session_state:
    st.session_state.trigger_confetti = False

# 효과 트리거 체크 (리런 후 실행)
if st.session_state.trigger_balloons:
    st.balloons()
    st.session_state.trigger_balloons = False

if st.session_state.trigger_confetti:
    show_confetti()
    st.session_state.trigger_confetti = False

# 완주 여부 확인 및 날짜 기록
if len(st.session_state.completed_missions) == len(SPOTS) and st.session_state.completion_date is None:
    st.session_state.completion_date = datetime.now().strftime("%Y.%m.%d")

# 사이드바: 탐방 장소 목록
st.sidebar.title("🚩 탐방 코스")

# 메인 화면으로 돌아가기 버튼 추가
if st.sidebar.button("🏠 메인 화면 (지도 보기)", use_container_width=True, type="primary"):
    st.session_state.current_spot_id = None
    st.rerun()

st.sidebar.markdown("---")

for spot in SPOTS:
    progress = st.session_state.spot_progress[spot['id']]
    
    # 상태 아이콘 결정
    if progress['quizzed']:
        status_icon = "✅"
    elif progress['authenticated']:
        status_icon = "📸"
    elif progress['learned']:
        status_icon = "📖"
    else:
        status_icon = "⚪"
        
    if st.sidebar.button(f"{status_icon} {spot['name']}", key=f"btn_{spot['id']}", use_container_width=True):
        st.session_state.current_spot_id = spot['id']
        st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("진행 상황 초기화", type="secondary", use_container_width=True):
    st.session_state.spot_progress = {
        spot['id']: {'learned': False, 'authenticated': False, 'quizzed': False} for spot in SPOTS
    }
    st.session_state.completed_missions = []
    st.session_state.current_spot_id = None
    st.session_state.completion_date = None
    st.session_state.quiz_data = {}
    
    # 로컬 스토리지 초기화
    components.html("""
        <script>
            localStorage.removeItem('myeongdong_mission_progress');
        </script>
    """, height=0)
    
    st.rerun()

# 상단 진행률 표시
show_overall_progress()

# 메인 화면 UI
if st.session_state.current_spot_id is None:
    st.markdown('<h1 style="margin-bottom: 0;">🧭 명동 역사 탐방</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #666; font-size: 1.1rem; margin-top: 5px; margin-bottom: 30px;">환영합니다! 명동의 숨겨진 역사를 찾아 떠나보세요.</p>', unsafe_allow_html=True)
    
    # 지도 및 도장 오버레이 설정
    # 각 장소별 지도 내 좌표 (x, y 퍼센트)
    stamp_coords = {
        "1": (18, 25),   # 명동성당
        "6": (78, 18),   # 이재명 의사 의거 터
        "7": (53, 30),   # 이회영 6형제 집터
        "8": (52, 55),   # 나석주 의사 의거 터
        "10": (18, 52),  # 한국전력 서울본부
        "9": (83, 49),   # 쌍용빌딩
        "11": (81, 77),  # 한성화교소학교
        "12": (35, 79),  # 홍영식 동상
    }
    
    import base64
    def get_image_base64(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
            
    map_base64 = get_image_base64("assets/images/mission_map.png")
    stamp_base64 = get_image_base64("assets/images/complete_stamp.png")
    
    stamps_html = ""
    for spot_id in st.session_state.completed_missions:
        if spot_id in stamp_coords:
            x, y = stamp_coords[spot_id]
            stamps_html += f'<img src="data:image/png;base64,{stamp_base64}" style="position: absolute; left: {x}%; top: {y}%; width: 80px; transform: translate(-50%, -50%) rotate(-15deg); z-index: 10;">'
            
    final_stamp_html = ""
    if st.session_state.completion_date:
        final_stamp_html = f"""<div class="completion-stamp"><div class="label">MISSION COMPLETE</div><div class="date">{st.session_state.completion_date}</div><div class="myeongdong">명동 역사 탐방</div></div>"""
            
    st.markdown(f"""
<div style="position: relative; width: 100%; max-width: 800px; margin: 0 auto;">
<img src="data:image/png;base64,{map_base64}" style="width: 100%; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
{stamps_html}
{final_stamp_html}
</div>
<p style="text-align: center; color: #666; margin-top: 10px;">📜 명동 역사 탐방 미션 맵 (완료 시 도장이 찍힙니다!)</p>
""", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="mission-card">
        <h4>탐방 가이드</h4>
        <ol>
            <li>왼쪽 사이드바에서 원하는 <b>장소를 선택</b>합니다.</li>
            <li><b>[📖 역사 학습]</b>에서 이야기를 꼼꼼히 읽고 완료 버튼을 누릅니다.</li>
            <li><b>[📸 사진 인증]</b>에서 현장 사진을 찍어 업로드합니다. (50% 이상 성공 시 통과)</li>
            <li><b>[❓ 역사 퀴즈]</b>를 풀어 미션을 최종 완료하세요!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    st.info("시작하려면 사이드바에서 장소를 선택해보세요!")

else:
    # 선택된 장소 데이터 가져오기
    current_spot = get_spot_by_id(SPOTS, st.session_state.current_spot_id)
    progress = st.session_state.spot_progress[current_spot['id']]
    
    st.title(f"{current_spot['name']}")

    # 미션 진행 상태 (탭 대신 직관적인 단계별 UI)
    if not progress['learned']:
        st.markdown('<div class="step-badge">📖 1단계: 역사 학습</div>', unsafe_allow_html=True)
        # 마크다운을 HTML로 변환 (단순 변환 로직)
        desc_html = current_spot['description'].replace("**", "<b>").replace("\n", "<br>")
        # 짝수 번째 <b>는 </b>로 닫아줘야 하지만, 브라우저가 어느 정도 보정하므로 간단히 처리하거나 
        # 정규식을 사용하여 정확히 변환합니다.
        import re
        desc_html = re.sub(r'<b>(.*?)<b>', r'<b>\1</b>', desc_html) # <b>단어<b> -> <b>단어</b>
        
        st.markdown(f"""
            <div class="guidebook-card">
                <div class="spot-description">{desc_html}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.image(current_spot['reference_image'], caption=current_spot['name'], use_container_width=True)
        if st.button("내용을 모두 읽었습니다! [학습 완료]", key="read_btn", use_container_width=True):
            st.session_state.spot_progress[current_spot['id']]['learned'] = True
            st.rerun()
            
    elif not progress['authenticated']:
        st.markdown('<div class="step-badge">📸 2단계: 사진 인증</div>', unsafe_allow_html=True)
        st.markdown(f"""
            <div class="guidebook-card">
                <p class="spot-description">현장에서 {current_spot['name']}의 사진을 촬영하여 인증해주세요.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.image(current_spot['reference_image'], caption="기준 이미지 (이 모습이 찍히게 해주세요)")
        
        with col_b:
            # 카메라 입력과 파일 업로드 선택 가능하게 구성
            input_mode = st.radio("인증 방법 선택", ["📷 카메라로 직접 촬영", "📁 사진 파일 업로드"], horizontal=True)
            
            uploaded_file = None
            if input_mode == "📷 카메라로 직접 촬영":
                if 'show_camera' not in st.session_state:
                    st.session_state.show_camera = False
                
                if not st.session_state.show_camera:
                    if st.button("📷 인증 카메라 켜기", use_container_width=True):
                        st.session_state.show_camera = True
                        st.rerun()
                else:
                    uploaded_file = st.camera_input("인증 사진을 찍어주세요")
                    if st.button("카메라 끄기", use_container_width=True):
                        st.session_state.show_camera = False
                        st.rerun()
            else:
                uploaded_file = st.file_uploader("이미지 파일 선택", type=['jpg', 'png', 'jpeg'])

            if uploaded_file:
                from services.image_match import calculate_similarity
                img_bytes = uploaded_file.getvalue()
                with st.spinner("이미지 분석 중..."):
                    score = calculate_similarity(current_spot['reference_image'], img_bytes)
                
                st.metric("유사도 점수", f"{score*100:.1f}%")
                
                if score >= 0.5:
                    # 인증 성공 시 카메라 자동 닫기 설정 가능
                    st.session_state.show_camera = False 
                    st.markdown("""
                        <div style="background-color: #d4edda; color: #155724; padding: 15px; border-radius: 10px; border: 1px solid #c3e6cb; margin-bottom: 20px;">
                            <h3 style="margin: 0;">✅ 인증 성공!</h3>
                            <p style="margin: 5px 0 0 0;">장소를 정확히 찾으셨네요! 이제 마지막 관문인 퀴즈가 남았습니다.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.session_state.spot_progress[current_spot['id']]['authenticated'] = True
                    if st.button("❓ 역사 퀴즈 풀러 가기", key="go_to_quiz", use_container_width=True):
                        st.rerun()
                else:
                    st.error("유사도가 조금 낮네요! 50%를 넘어야 합니다. 기준 이미지와 더 비슷한 구도에서 다시 시도해보세요.")
                    st.info("💡 팁: 만약 현장이 확실하다면 아래 버튼을 눌러 바로 퀴즈를 풀 수도 있습니다.")
            
            # 사진 인증 건너뛰기 버튼 (항상 표시)
            if st.button("📍 이 장소가 확실합니다. 퀴즈 풀기", key="skip_photo", use_container_width=True):
                st.session_state.spot_progress[current_spot['id']]['authenticated'] = True
                st.session_state.show_camera = False
                st.rerun()
        
        if st.button("⬅️ 이전 단계로 (학습 내용 다시 보기)", type="secondary", use_container_width=True):
            st.session_state.spot_progress[current_spot['id']]['learned'] = False
            st.rerun()

    elif not progress['quizzed']:
        st.markdown('<div class="step-badge">❓ 3단계: 역사 퀴즈</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="guidebook-card">
                <h3 style="margin-top: 0;">💡 마지막 관문!</h3>
                <p class="spot-description">장소를 성공적으로 찾으셨군요! 마지막 퀴즈까지 맞히면 미션 완료입니다.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # 퀴즈 데이터 초기화 및 유지 (정답 맞히기 전까지 고정)
        spot_id = current_spot['id']
        if spot_id not in st.session_state.quiz_data:
            quiz_idx = random.randint(0, len(current_spot['quizzes']) - 1)
            selected_quiz = current_spot['quizzes'][quiz_idx]
            shuffled_options = list(selected_quiz['options'])
            random.shuffle(shuffled_options)
            
            st.session_state.quiz_data[spot_id] = {
                'quiz_idx': quiz_idx,
                'options': shuffled_options
            }
        
        q_info = st.session_state.quiz_data[spot_id]
        quiz = current_spot['quizzes'][q_info['quiz_idx']]
        
        st.info(f"**Q: {quiz['question']}**")
        ans = st.radio("정답을 골라주세요!", q_info['options'], index=None, key=f"quiz_radio_{spot_id}")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("정답 확인", key="quiz_check", type="primary", use_container_width=True):
                if ans == quiz['answer']:
                    st.session_state.trigger_confetti = True
                    st.session_state.trigger_balloons = True
                    st.session_state.spot_progress[current_spot['id']]['quizzed'] = True
                    if current_spot['id'] not in st.session_state.completed_missions:
                        st.session_state.completed_missions.append(current_spot['id'])
                    st.rerun()
                else:
                    st.error("앗, 틀렸어요! 다시 한번 읽어보시겠어요?")

    else:
        # 정답 피드백 화면
        st.markdown("""
            <div style="text-align: center; padding: 30px; background-color: #f0fdf4; border-radius: 20px; border: 3px solid #22c55e; margin-bottom: 25px; box-shadow: 0 10px 25px rgba(34, 197, 94, 0.2);">
                <h1 style="color: #15803d; margin: 0; font-size: 3.5rem !important;">🎊 훌륭해! 🎊</h1>
                <p style="font-size: 1.5rem; color: #166534; font-weight: 700; margin-top: 15px;">역사 박사님이 탄생했어요!</p>
                <p style="font-size: 1.1rem; color: #15803d; margin-top: 10px;">이제 지도에 보물 도장이 찍혔습니다.</p>
            </div>
        """, unsafe_allow_html=True)
        st.success(f"🎊 축하합니다! {current_spot['name']}의 모든 미션을 완료했습니다.")
        
        if st.button("⬅️ 이전 단계로 (사진 다시 확인)", type="secondary", use_container_width=True):
            st.session_state.spot_progress[current_spot['id']]['authenticated'] = False
            st.rerun()

        
        # 다음 장소 찾기
        current_idx = next(i for i, s in enumerate(SPOTS) if s['id'] == current_spot['id'])
        
        if current_idx < len(SPOTS) - 1:
            next_spot = SPOTS[current_idx + 1]
            if st.button(f"🚩 다음 장소로 이동 ({next_spot['name']})", key="next_spot", use_container_width=True):
                st.session_state.current_spot_id = next_spot['id']
                st.rerun()
        else:
            st.info("축하합니다! 명동 탐방 코스의 모든 장소를 방문하셨습니다.")
            if st.button("🏠 처음 화면으로 돌아가기", key="go_home", use_container_width=True):
                st.session_state.current_spot_id = None
                st.rerun()

# --- 데이터 로컬 저장 (실시간 동기화) ---
if 'spot_progress' in st.session_state:
    save_data = {
        'spot_progress': st.session_state.spot_progress,
        'completed_missions': st.session_state.completed_missions,
        'completion_date': st.session_state.completion_date,
        'quiz_data': st.session_state.quiz_data
    }
    json_data = json.dumps(save_data, ensure_ascii=False)
    components.html(f"""
        <script>
            localStorage.setItem('myeongdong_mission_progress', `{json_data}`);
        </script>
    """, height=0)
