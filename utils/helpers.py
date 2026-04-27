import streamlit as st
from PIL import Image, ImageOps
import io

def get_spot_by_id(spots, spot_id):
    """ID로 장소 데이터를 찾습니다."""
    return next((s for s in spots if s['id'] == spot_id), None)

def fix_image_orientation(image_bytes):
    """
    이미지의 EXIF 데이터를 확인하여 회전된 이미지를 바로잡습니다.
    """
    img = Image.open(io.BytesIO(image_bytes))
    try:
        # EXIF 정보를 바탕으로 이미지 자동 회전 교정
        img = ImageOps.exif_transpose(img)
    except Exception:
        # EXIF 정보가 없거나 오류 발생 시 원본 유지
        pass
    
    # 다시 바이트로 변환
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()
