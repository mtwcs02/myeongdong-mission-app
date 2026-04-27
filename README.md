# 명동 역사 탐방 게이미피케이션 웹앱 (myeongdong-mission-app)

사용자가 명동의 주요 역사적 장소를 방문하며 미션을 수행하는 체험형 웹 애플리케이션입니다.  
교육적 목적과 게임 요소를 결합하여, 사용자는 장소 탐방 → 콘텐츠 학습 → 사진 인증 → 퀴즈 해결의 흐름으로 진행합니다.

## 🎯 핵심 목표
- 명동의 역사적 장소를 재미있게 학습할 수 있도록 함
- 가족 단위 사용자가 함께 체험할 수 있는 콘텐츠 제공
- 사진 인증과 퀴즈를 통한 몰입도 향상

## 🧩 주요 기능
- **미션 목록**: 명동의 주요 역사적 장소 리스트 제공
- **역사 콘텐츠**: 각 장소의 역사적 배경과 이미지 제공
- **사진 인증**: OpenCV를 활용한 현장 사진 유사도 판정
- **역사 퀴즈**: 각 장소와 관련된 퀴즈 풀이

## ⚙️ 기술 스택
- **Framework**: Streamlit
- **Image Processing**: OpenCV (opencv-python-headless)
- **Environment**: Python (uv 기반 가상환경)

## 🚀 시작하기

1. **저장소 클론**
   ```bash
   git clone https://github.com/사용자이름/myeongdong-mission-app.git
   cd myeongdong-mission-app
   ```

2. **가상환경 설정 및 패키지 설치 (uv 사용 시)**
   ```bash
   uv venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

3. **앱 실행**
   ```bash
   streamlit run app.py
   ```

## 📁 폴더 구조
- `app.py`: 메인 애플리케이션
- `data/`: 장소 데이터 (설명, 퀴즈 등)
- `services/`: 이미지 유사도 비교 로직
- `assets/`: 기준 이미지 및 리소스
- `utils/`: 공통 유틸리티 함수
