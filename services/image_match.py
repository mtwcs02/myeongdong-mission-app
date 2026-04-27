import cv2
import numpy as np

def calculate_similarity(base_img_path, target_img_bytes):
    """
    ORB(Oriented FAST and Rotated BRIEF) 특징점 매칭을 사용하여 두 이미지 간의 유사도를 계산합니다.
    """
    try:
        from utils.helpers import fix_image_orientation
        # 1. 이미지 로드 및 방향 교정
        base_img = cv2.imread(base_img_path)
        if base_img is None:
            return 0.0
            
        # 사용자 이미지 방향 교정 (EXIF 대응)
        target_img_bytes = fix_image_orientation(target_img_bytes)
        
        # 바이트 데이터를 이미지로 변환
        nparr = np.frombuffer(target_img_bytes, np.uint8)
        target_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if target_img is None:
            return 0.0

        # 그레이스케일 변환
        gray1 = cv2.cvtColor(base_img, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)

        # 2. ORB 특징점 검출기 생성
        orb = cv2.ORB_create(nfeatures=1000)

        # 특징점과 기술자 검출
        kp1, des1 = orb.detectAndCompute(gray1, None)
        kp2, des2 = orb.detectAndCompute(gray2, None)

        if des1 is None or des2 is None:
            return 0.0

        # 3. Brute-Force 매칭기 생성 (Hamming 거리 사용)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)

        # 거리에 따라 정렬
        matches = sorted(matches, key=lambda x: x.distance)

        # 4. 유사도 점수 계산
        # 좋은 매칭의 비율을 점수로 환산 (단순화된 방식)
        good_matches = [m for m in matches if m.distance < 50]
        
        # 기본 유사도: 매칭된 특징점 수 기반
        score = len(good_matches) / 100.0  # 100개 이상이면 1.0 (100%)
        
        # 점수를 0.0 ~ 1.0 사이로 제한
        final_score = min(score, 1.0)
        
        return final_score

    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0
