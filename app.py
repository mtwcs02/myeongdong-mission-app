import streamlit as st
from data.spots import SPOTS
from utils.helpers import get_spot_by_id
from services.image_match import calculate_similarity  # [수정 1] import를 최상단으로 이동
from datetime import datetime
import random
import json
import re  # [수정 1] import를 최상단으로 이동
import base64  # [수정 1] import를 최상단으로 이동
import streamlit.components.v1 as components

# 페이지 설정 (모바일 최적화를 위해 layout은 'centered' 추천하나 wide에서 반응형 대응)
st.set_page_config(
    page_title="명동 역사 탐방",
    page_icon="🏯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================================
# [수정 2] 세션 상태 초기화 — 가장 먼저 실행되어야 함
# 기존에는 세션 초기화 코드가 250~305줄에 있었어서,
# 그 위에서 세션을 사용하는 함수들이 에러를 일으켰음.
# =====================================================================
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
    st.session_state.quiz_data = {}

if 'trigger_balloons' not in st.session_state:
    st.session_state.trigger_balloons = False

if 'trigger_confetti' not in st.session_state:
    st.session_state.trigger_confetti = False

# =====================================================================
# [수정 3] localStorage 대신 쿠키 기반 저장으로 교체
# 기존 방식(JS → URL 파라미터 → Python)은 무한 리다이렉트 위험 + 불안정
# streamlit-cookies-manager 사용: pip install streamlit-cookies-manager
# =====================================================================
try:
    from streamlit_cookies_manager import EncryptedCookieManager
    cookies = EncryptedCookieManager(
        prefix="myeongdong_",
        password="myeongdong-secret-key-2024"  # 실제 배포 시 더 복잡한 키 사용 권장
    )
    COOKIES_AVAILABLE = True
    if not cookies.ready():
        st.stop()
except ImportError:
    # 라이브러리가 없으면 쿠키 없이 동작 (세션 내에서만 유지)
    COOKIES_AVAILABLE = False
    cookies = None

# 쿠키에서 진행 데이터 불러오기 (앱 시작 시 1회 실행)
if COOKIES_AVAILABLE and 'cookie_loaded' not in st.session_state:
    st.session_state.cookie_loaded = True
    try:
        saved_raw = cookies.get('progress')
        if saved_raw:
            data = json.loads(saved_raw)
            # 불러온 데이터로 세션 상태 덮어쓰기
            loaded_progress = data.get('spot_progress', {})
            # SPOTS에 있는 장소만 복원 (데이터 구조 안전하게 병합)
            for spot in SPOTS:
                if spot['id'] in loaded_progress:
                    st.session_state.spot_progress[spot['id']] = loaded_progress[spot['id']]
            st.session_state.completed_missions = data.get('completed_missions', [])
            st.session_state.completion_date = data.get('completion_date', None)
            st.session_state.quiz_data = data.get('quiz_data', {})
    except Exception as e:
        # 쿠키 데이터가 깨졌을 경우 무시하고 초기 상태로 진행
        pass

# 쿠키에 진행 데이터 저장하는 함수
def save_progress_to_cookie():
    if not COOKIES_AVAILABLE:
        return
    try:
        save_data = {
            'spot_progress': st.session_state.spot_progress,
            'completed_missions': st.session_state.completed_missions,
            'completion_date': st.session_state.completion_date,
            'quiz_data': st.session_state.quiz_data
        }
        cookies['progress'] = json.dumps(save_data, ensure_ascii=False)
        cookies.save()
    except Exception:
        pass

# =====================================================================
# 커스텀 CSS (모바일 최적화) — 변경 없음
# =====================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    .main { background-color: #FAF9F6; }
    .stApp { background-color: #FAF9F6; }
    
    div[data-testid="stSidebar"] .element-container,
    div[data-testid="stSidebar"] .stButton,
    div[data-testid="stSidebar"] .stButton > button,
    .stButton > button {
        width: 100% !important;
        border-radius: 12px !important;
        height: 4rem !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        margin-bottom: 8px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
        transition: all 0.2s !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        text-align: left !important;
        padding: 0 15px !important;
    }
    .stButton>button[kind="primary"] { background-color: #007bff; border: none; }
    .stButton>button[kind="secondary"] { background-color: #ffffff; color: #495057; border: 1px solid #dee2e6; }

    .mission-card {
        background-color: white; padding: 20px; border-radius: 16px;
        border-left: 6px solid #007bff; margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .mission-card h4 { color: #212529; margin-top: 0; }

    .guidebook-card {
        background-color: #ffffff; padding: 30px; border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04); margin-bottom: 25px;
        border: 1px solid #f0f0f0;
    }
    
    h1 { color: #1E3A8A !important; font-size: 2.8rem !important; font-weight: 800 !important; letter-spacing: 0.05em !important; }
    h2, h3 { color: #1E3A8A !important; }

    .step-badge {
        display: inline-block; padding: 8px 20px; background-color: #1E3A8A;
        color: white; border-radius: 50px; font-weight: 700; font-size: 1rem;
        margin-bottom: 20px; box-shadow: 0 4px 10px rgba(30, 58, 138, 0.2);
    }
    .spot-description { font-size: 1.15rem !important; line-height: 1.8 !important; color: #444 !important; }
    .spot-description b { color: #1E3A8A !important; font-weight: 700 !important; }

    @media (max-width: 768px) {
        h1 { font-size: 1.8rem !important; letter-spacing: 0.02em !important; }
        .guidebook-card { padding: 20px !important; border-radius: 15px !important; }
        .step-badge { font-size: 0.9rem !important; padding: 6px 15px !important; }
        .spot-description { font-size: 1.05rem !important; line-height: 1.6 !important; }
        .stButton > button { height: 3.5rem !important; }
    }

    .stImage img { border-radius: 12px; }
    
    .completion-stamp {
        position: absolute; left: 50%; top: 50%;
        transform: translate(-50%, -50%) rotate(-10deg);
        width: 220px; height: 220px; border: 5px double #D32F2F;
        border-radius: 50%; display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        background-color: rgba(211, 47, 47, 0.05); color: #D32F2F;
        font-family: 'Noto Sans KR', sans-serif; z-index: 100;
        pointer-events: none; box-shadow: 0 0 15px rgba(211, 47, 47, 0.2);
    }
    .completion-stamp .label { font-size: 1.2rem; font-weight: 800; margin-bottom: 5px; letter-spacing: 2px; }
    .completion-stamp .date { font-size: 1.5rem; font-weight: 900; border-top: 2px solid #D32F2F; border-bottom: 2px solid #D32F2F; padding: 5px 10px; }
    .completion-stamp .myeongdong { font-size: 0.9rem; margin-top: 5px; font-weight: 700; }
    
    [data-testid="stSidebar"] h1 { white-space: nowrap !important; font-size: 1.5rem !important; }
    </style>
""", unsafe_allow_html=True)


# =====================================================================
# 헬퍼 함수들
# =====================================================================

def show_overall_progress():
    """상단 전체 진행률 표시"""
    completed_count = sum(1 for p in st.session_state.spot_progress.values() if p['quizzed'])
    total_count = len(SPOTS)
    progress_val = completed_count / total_count if total_count > 0 else 0
    st.write(f"**전체 미션 진행률: {completed_count}/{total_count}**")
    st.progress(progress_val)
    st.markdown("---")

def show_confetti():
    """폭죽 효과"""
    st.components.v1.html(
        """
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
        <script>
            var end = Date.now() + (2 * 1000);
            var colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'];
            (function frame() {
              confetti({ particleCount: 3, angle: 60, spread: 55, origin: { x: 0 }, colors: colors });
              confetti({ particleCount: 3, angle: 120, spread: 55, origin: { x: 1 }, colors: colors });
              if (Date.now() < end) { requestAnimationFrame(frame); }
            }());
        </script>
        """,
        height=0,
    )

def get_image_base64(path):
    """이미지를 base64로 변환"""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""


# =====================================================================
# 효과 트리거 (세션 초기화 직후 실행)
# =====================================================================
if st.session_state.trigger_balloons:
    st.balloons()
    st.session_state.trigger_balloons = False

if st.session_state.trigger_confetti:
    show_confetti()
    st.session_state.trigger_confetti = False

# 완주 여부 확인 및 날짜 기록
if len(st.session_state.completed_missions) == len(SPOTS) and st.session_state.completion_date is None:
    st.session_state.completion_date = datetime.now().strftime("%Y.%m.%d")


# =====================================================================
# 사이드바
# =====================================================================
st.sidebar.title("🚩 탐방 코스")

if st.sidebar.button("🏠 메인 화면 (지도 보기)", use_container_width=True, type="primary"):
    st.session_state.current_spot_id = None
    st.rerun()

st.sidebar.markdown("---")

for spot in SPOTS:
    progress = st.session_state.spot_progress[spot['id']]
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
    # 쿠키도 초기화
    if COOKIES_AVAILABLE:
        try:
            cookies['progress'] = ''
            cookies.save()
        except Exception:
            pass
    st.rerun()


# =====================================================================
# 상단 진행률
# =====================================================================
show_overall_progress()


# =====================================================================
# 메인 화면
# =====================================================================
if st.session_state.current_spot_id is None:
    st.markdown('<h1 style="margin-bottom: 0;">🧭 명동 역사 탐방</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #666; font-size: 1.1rem; margin-top: 5px; margin-bottom: 30px;">환영합니다! 명동의 숨겨진 역사를 찾아 떠나보세요.</p>', unsafe_allow_html=True)

    stamp_coords = {
        "1":  (18, 25),
        "6":  (78, 18),
        "7":  (53, 30),
        "8":  (52, 55),
        "10": (18, 52),
        "9":  (83, 49),
        "11": (81, 77),
        "12": (35, 79),
    }

    map_base64   = get_image_base64("assets/images/mission_map.png")
    stamp_base64 = get_image_base64("assets/images/complete_stamp.png")

    stamps_html = ""
    for spot_id in st.session_state.completed_missions:
        if spot_id in stamp_coords:
            x, y = stamp_coords[spot_id]
            stamps_html += (
                f'<img src="data:image/png;base64,{stamp_base64}" '
                f'style="position: absolute; left: {x}%; top: {y}%; width: 80px; '
                f'transform: translate(-50%, -50%) rotate(-15deg); z-index: 10;">'
            )

    final_stamp_html = ""
    if st.session_state.completion_date:
        final_stamp_html = (
            f'<div class="completion-stamp">'
            f'<div class="label">MISSION COMPLETE</div>'
            f'<div class="date">{st.session_state.completion_date}</div>'
            f'<div class="myeongdong">명동 역사 탐방</div>'
            f'</div>'
        )

    if map_base64:
        st.markdown(f"""
<div style="position: relative; width: 100%; max-width: 800px; margin: 0 auto;">
<img src="data:image/png;base64,{map_base64}" style="width: 100%; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
{stamps_html}
{final_stamp_html}
</div>
<p style="text-align: center; color: #666; margin-top: 10px;">📜 명동 역사 탐방 미션 맵 (완료 시 도장이 찍힙니다!)</p>
""", unsafe_allow_html=True)
    else:
        st.warning("지도 이미지를 불러올 수 없습니다. assets/images/mission_map.png 파일을 확인해주세요.")

    st.markdown("""
    <div class="mission-card">
        <h4>탐방 가이드</h4>
        <ol>
            <li>아래에서 원하는 <b>장소를 선택</b>합니다.</li>
            <li><b>[📖 역사 학습]</b>에서 이야기를 꼼꼼히 읽고 완료 버튼을 누릅니다.</li>
            <li><b>[📸 사진 인증]</b>에서 현장 사진을 찍어 업로드합니다. (50% 이상 성공 시 통과)</li>
            <li><b>[❓ 역사 퀴즈]</b>를 풀어 미션을 최종 완료하세요!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # ── 장소 선택 카드 (모바일 메인 진입점) ──────────────────────────
    st.markdown("### 📍 장소를 선택하세요")
    cols = st.columns(2)  # 2열 그리드 — 모바일에서도 보기 좋음
    for idx, spot in enumerate(SPOTS):
        p = st.session_state.spot_progress[spot['id']]
        if p['quizzed']:
            icon, badge_color, badge_text = "✅", "#22c55e", "완료"
        elif p['authenticated']:
            icon, badge_color, badge_text = "📸", "#3b82f6", "퀴즈 전"
        elif p['learned']:
            icon, badge_color, badge_text = "📖", "#f59e0b", "학습 완료"
        else:
            icon, badge_color, badge_text = "⚪", "#9ca3af", "미방문"

        with cols[idx % 2]:
            # 카드 HTML (클릭은 아래 버튼으로)
            st.markdown(f"""
                <div style="background:white; border-radius:14px; padding:14px 16px 6px 16px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.08); margin-bottom:4px;
                            border-top: 4px solid {badge_color};">
                    <div style="font-size:1.4rem;">{icon}</div>
                    <div style="font-weight:700; font-size:0.95rem; color:#1e293b; margin:4px 0 2px 0;">
                        {spot['name']}
                    </div>
                    <span style="font-size:0.78rem; background:{badge_color}22;
                                 color:{badge_color}; padding:2px 8px; border-radius:20px;
                                 font-weight:700;">{badge_text}</span>
                </div>
            """, unsafe_allow_html=True)
            if st.button("선택하기", key=f"main_btn_{spot['id']}", use_container_width=True):
                st.session_state.current_spot_id = spot['id']
                st.rerun()

else:
    # =====================================================================
    # 장소별 미션 화면
    # =====================================================================
    try:
        current_spot = get_spot_by_id(SPOTS, st.session_state.current_spot_id)
    except Exception:
        st.error("장소 데이터를 불러오는 중 오류가 발생했습니다.")
        st.session_state.current_spot_id = None
        st.rerun()

    progress = st.session_state.spot_progress[current_spot['id']]

    # 모바일용 상단 홈 버튼 (사이드바 없이도 돌아갈 수 있게)
    if st.button("◀ 장소 목록으로 돌아가기", type="secondary"):
        st.session_state.current_spot_id = None
        st.rerun()

    st.title(f"{current_spot['name']}")

    # ------------------------------------------------------------------
    # 1단계: 역사 학습
    # ------------------------------------------------------------------
    if not progress['learned']:
        st.markdown('<div class="step-badge">📖 1단계: 역사 학습</div>', unsafe_allow_html=True)

        # [수정 4] **bold** 변환 정규식 수정
        # 기존: replace("**", "<b>") 후 불완전한 정규식으로 재처리 → 닫힘 태그 누락
        # 수정: 정규식 한 번에 **텍스트** → <b>텍스트</b> 변환
        desc_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', current_spot['description'])
        desc_html = desc_html.replace("\n", "<br>")

        st.markdown(f"""
            <div class="guidebook-card">
                <div class="spot-description">{desc_html}</div>
            </div>
        """, unsafe_allow_html=True)

        st.image(current_spot['reference_image'], caption=current_spot['name'], use_container_width=True)
        if st.button("내용을 모두 읽었습니다! [학습 완료]", key="read_btn", use_container_width=True):
            st.session_state.spot_progress[current_spot['id']]['learned'] = True
            save_progress_to_cookie()  # 진행 저장
            st.rerun()

    # ------------------------------------------------------------------
    # 2단계: 사진 인증
    # ------------------------------------------------------------------
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
            input_mode = st.radio("인증 방법 선택", ["📷 카메라로 직접 촬영", "📁 사진 파일 업로드"], horizontal=True)

            uploaded_file = None

            if input_mode == "📷 카메라로 직접 촬영":
                # [수정 5] show_camera 키를 장소별로 분리
                # 기존: 'show_camera' 하나 공유 → 장소 이동 시 이전 상태 남음
                camera_key = f'show_camera_{current_spot["id"]}'
                if camera_key not in st.session_state:
                    st.session_state[camera_key] = False

                if not st.session_state[camera_key]:
                    if st.button("📷 인증 카메라 켜기", use_container_width=True):
                        st.session_state[camera_key] = True
                        st.rerun()
                else:
                    uploaded_file = st.camera_input("인증 사진을 찍어주세요")
                    if st.button("카메라 끄기", use_container_width=True):
                        st.session_state[camera_key] = False
                        st.rerun()
            else:
                uploaded_file = st.file_uploader("이미지 파일 선택", type=['jpg', 'png', 'jpeg'])

            if uploaded_file:
                img_bytes = uploaded_file.getvalue()
                with st.spinner("이미지 분석 중..."):
                    try:
                        score = calculate_similarity(current_spot['reference_image'], img_bytes)
                    except Exception:
                        score = 0.0
                        st.warning("이미지 분석 중 오류가 발생했습니다. 건너뛰기 버튼을 이용해주세요.")

                st.metric("유사도 점수", f"{score*100:.1f}%")

                if score >= 0.5:
                    camera_key = f'show_camera_{current_spot["id"]}'
                    st.session_state[camera_key] = False
                    st.markdown("""
                        <div style="background-color: #d4edda; color: #155724; padding: 15px; border-radius: 10px; border: 1px solid #c3e6cb; margin-bottom: 20px;">
                            <h3 style="margin: 0;">✅ 인증 성공!</h3>
                            <p style="margin: 5px 0 0 0;">장소를 정확히 찾으셨네요! 이제 마지막 관문인 퀴즈가 남았습니다.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.session_state.spot_progress[current_spot['id']]['authenticated'] = True
                    save_progress_to_cookie()  # 진행 저장
                    if st.button("❓ 역사 퀴즈 풀러 가기", key="go_to_quiz", use_container_width=True):
                        st.rerun()
                else:
                    st.error("유사도가 조금 낮네요! 50%를 넘어야 합니다. 기준 이미지와 더 비슷한 구도에서 다시 시도해보세요.")
                    st.info("💡 팁: 만약 현장이 확실하다면 아래 버튼을 눌러 바로 퀴즈를 풀 수도 있습니다.")

            # 건너뛰기 버튼
            if st.button("📍 이 장소가 확실합니다. 퀴즈 풀기", key="skip_photo", use_container_width=True):
                st.session_state.spot_progress[current_spot['id']]['authenticated'] = True
                camera_key = f'show_camera_{current_spot["id"]}'
                st.session_state[camera_key] = False
                save_progress_to_cookie()  # 진행 저장
                st.rerun()

        if st.button("⬅️ 이전 단계로 (학습 내용 다시 보기)", type="secondary", use_container_width=True):
            st.session_state.spot_progress[current_spot['id']]['learned'] = False
            st.rerun()

    # ------------------------------------------------------------------
    # 3단계: 역사 퀴즈
    # ------------------------------------------------------------------
    elif not progress['quizzed']:
        st.markdown('<div class="step-badge">❓ 3단계: 역사 퀴즈</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="guidebook-card">
                <h3 style="margin-top: 0;">💡 마지막 관문!</h3>
                <p class="spot-description">장소를 성공적으로 찾으셨군요! 마지막 퀴즈까지 맞히면 미션 완료입니다.</p>
            </div>
        """, unsafe_allow_html=True)

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
        quiz   = current_spot['quizzes'][q_info['quiz_idx']]

        st.info(f"**Q: {quiz['question']}**")
        ans = st.radio("정답을 골라주세요!", q_info['options'], index=None, key=f"quiz_radio_{spot_id}")

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("정답 확인", key="quiz_check", type="primary", use_container_width=True):
                if ans is None:
                    st.warning("정답을 선택해주세요!")
                elif ans == quiz['answer']:
                    st.session_state.trigger_confetti = True
                    st.session_state.trigger_balloons = True
                    st.session_state.spot_progress[current_spot['id']]['quizzed'] = True
                    if current_spot['id'] not in st.session_state.completed_missions:
                        st.session_state.completed_missions.append(current_spot['id'])
                    save_progress_to_cookie()  # 진행 저장
                    st.rerun()
                else:
                    st.error("앗, 틀렸어요! 다시 한번 읽어보시겠어요?")

    # ------------------------------------------------------------------
    # 완료 화면
    # ------------------------------------------------------------------
    else:
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
