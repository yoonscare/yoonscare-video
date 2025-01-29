import streamlit as st
import replicate
import requests
import time
import json

# 페이지 기본 설정
st.set_page_config(
    page_title="AI 애니메이션 생성기",
    page_icon="🎨",
    layout="wide"
)

# 상태 초기화
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = False
if 'image_url' not in st.session_state:
    st.session_state.image_url = None
if 'video_url' not in st.session_state:
    st.session_state.video_url = None

# CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f0f4f8, #d1e3ff);
    }
    .error {
        color: red;
        padding: 10px;
        border-radius: 5px;
        background-color: #ffe6e6;
    }
    .success {
        color: green;
        padding: 10px;
        border-radius: 5px;
        background-color: #e6ffe6;
    }
    </style>
""", unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.title("⚙️ 설정")
    api_key = st.text_input("Replicate API 키", type="password", key="api_key")
    
    if api_key:
        try:
            client = replicate.Client(api_token=api_key)
            st.session_state.authentication_status = True
            st.success("API 키가 확인되었습니다! ✅")
        except Exception as e:
            st.error("API 키 인증에 실패했습니다. 다시 확인해주세요.")
            st.session_state.authentication_status = False
    
    st.markdown("---")
    st.markdown("### 🎨 이미지 설정")
    image_width = st.slider("너비", 384, 1024, 768, 128)
    image_height = st.slider("높이", 384, 1024, 768, 128)

# 메인 영역
st.title("🎭 AI 애니메이션 생성기")

# 프롬프트 입력
prompt = st.text_area(
    "애니메이션으로 만들고 싶은 장면을 자세히 설명해주세요 (영어로 입력)",
    height=100,
    placeholder="예시: Back view of a beautiful woman walking on the beach with sea breeze, cartoon style"
)

# 이미지 생성 함수
def generate_image():
    try:
        with st.status("🎨 이미지 생성 중...", expanded=True) as status:
            output = replicate.run(
                "stability-ai/sdxl:2b017d9b67edd2ee1401238df49d75da53c523f36e363881e057f5dc3ed3c5b2",
                input={
                    "prompt": prompt,
                    "width": image_width,
                    "height": image_height,
                }
            )
            if output and len(output) > 0:
                st.session_state.image_url = output[0]
                status.update(label="✅ 이미지 생성 완료!", state="complete")
                return True
            return False
    except Exception as e:
        st.error(f"이미지 생성 중 오류 발생: {str(e)}")
        return False

# 비디오 생성 함수
def generate_video():
    try:
        with st.status("🎬 비디오 생성 중...", expanded=True) as status:
            output = replicate.run(
                "minimax/video-01-live",
                input={
                    "prompt": prompt,
                    "prompt_optimizer": True,
                    "first_frame_image": st.session_state.image_url
                }
            )
            if output and len(output) > 0:
                st.session_state.video_url = output[0]
                status.update(label="✅ 비디오 생성 완료!", state="complete")
                return True
            return False
    except Exception as e:
        st.error(f"비디오 생성 중 오류 발생: {str(e)}")
        return False

# 버튼 컬럼
col1, col2 = st.columns(2)

with col1:
    if st.button("1️⃣ 이미지 생성", use_container_width=True, disabled=not st.session_state.authentication_status):
        if not prompt:
            st.error("프롬프트를 입력해주세요!")
        else:
            success = generate_image()
            if success:
                st.session_state.video_url = None  # 새 이미지 생성시 비디오 초기화

with col2:
    if st.button("2️⃣ 비디오 생성", use_container_width=True, 
                disabled=not (st.session_state.authentication_status and st.session_state.image_url)):
        success = generate_video()

# 결과 표시
if st.session_state.image_url:
    st.markdown("### 🖼 생성된 이미지")
    st.image(st.session_state.image_url, use_column_width=True)

if st.session_state.video_url:
    st.markdown("### 🎬 생성된 비디오")
    st.video(st.session_state.video_url)
    
    # 다운로드 버튼
    try:
        video_data = requests.get(st.session_state.video_url).content
        st.download_button(
            label="📥 비디오 다운로드",
            data=video_data,
            file_name="generated_animation.mp4",
            mime="video/mp4",
            use_container_width=True
        )
    except Exception as e:
        st.error("비디오 다운로드 준비 중 오류가 발생했습니다.")

# 초기화 버튼
if st.session_state.image_url or st.session_state.video_url:
    if st.button("🔄 처음부터 다시 시작", use_container_width=True):
        st.session_state.image_url = None
        st.session_state.video_url = None
        st.experimental_rerun()

# 도움말
with st.expander("💡 프롬프트 작성 팁"):
    st.markdown("""
    - 캐릭터의 특징을 자세히 설명해주세요 (머리 색, 표정, 스타일 등)
    - 원하는 아트 스타일을 명시해주세요 (cartoon style, anime style 등)
    - 장면의 분위기나 움직임을 포함시켜주세요
    - 영어로 작성하면 더 좋은 결과를 얻을 수 있습니다
    """)
