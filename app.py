import streamlit as st
import replicate
import requests
import os

# 페이지 기본 설정
st.set_page_config(
    page_title="AI 애니메이션 생성기",
    page_icon="🎭",
    layout="wide"
)

# 앱 시작시 임시 파일 정리
if os.path.exists("temp_video.mp4"):
    os.remove("temp_video.mp4")

# 상태 초기화
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'image_url' not in st.session_state:
    st.session_state.image_url = None
if 'video_url' not in st.session_state:
    st.session_state.video_url = None

# CSS 스타일 적용
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #1a1a2e, #16213e);
    }
    .stTextInput > div > div > input {
        background-color: #222831;
        color: white;
    }
    .stTextArea > div > div > textarea {
        background-color: #222831;
        color: white;
    }
    .stButton > button {
        background-color: #4361ee;
        color: white;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #3b28cc;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(67, 97, 238, 0.3);
    }
    .main-header {
        color: white;
        font-size: 2.5em;
        text-align: center;
        padding: 1rem;
        margin-bottom: 2rem;
        background: rgba(30, 41, 59, 0.7);
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

def generate_image(prompt, width, height):
    if not st.session_state.api_key:
        st.error("API 키를 입력해주세요.")
        return False
    
    try:
        client = replicate.Client(api_token=st.session_state.api_key)
        
        with st.spinner("🎨 이미지를 생성하고 있습니다..."):
            output = client.run(
                "stability-ai/sdxl:2b017d9b67edd2ee1401238df49d75da53c523f36e363881e057f5dc3ed3c5b2",
                input={
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                }
            )
            
            if isinstance(output, list) and len(output) > 0:
                st.session_state.image_url = output[0]
                return True
            return False
            
    except Exception as e:
        st.error(f"이미지 생성 실패: {str(e)}")
        return False

def generate_video(prompt, image_url):
    if not st.session_state.api_key:
        st.error("API 키를 입력해주세요.")
        return False
    
    try:
        client = replicate.Client(api_token=st.session_state.api_key)
        
        with st.spinner("🎬 비디오를 생성하고 있습니다..."):
            output = client.run(
                "minimax/video-01-live",
                input={
                    "prompt": prompt,
                    "first_frame_image": image_url,
                    "num_frames": 50,
                    "frame_rate": 30,
                    "output_video": True,
                    "border_ratio": 0.1,
                    "initial_control_strength": 1,
                    "final_control_strength": 0.5,
                    "motion_bucket_id": 127
                }
            )
            
            if isinstance(output, list) and len(output) > 0:
                video_url = output[0]
                st.session_state.video_url = video_url
                return True
            return False
            
    except Exception as e:
        st.error(f"비디오 생성 실패: {str(e)}")
        return False

# 사이드바
with st.sidebar:
    st.title("⚙️ 설정")
    api_key = st.text_input(
        "Replicate API 키",
        type="password",
        help="https://replicate.com에서 발급받은 API 키를 입력하세요"
    )
    
    if api_key:
        st.session_state.api_key = api_key.strip()
        try:
            client = replicate.Client(api_token=st.session_state.api_key)
            st.success("✅ API 키가 확인되었습니다!")
        except Exception as e:
            st.error(f"❌ API 키 인증 실패: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 🎨 출력 설정")
    image_width = st.slider("이미지/영상 너비", 512, 1024, 768, 128)
    image_height = st.slider("이미지/영상 높이", 512, 1024, 768, 128)

# 메인 영역
st.markdown("<h1 class='main-header'>🎭 AI 애니메이션 생성기</h1>", unsafe_allow_html=True)

# 프롬프트 입력
with st.container():
    st.markdown("### 1️⃣ 장면 설명")
    prompt = st.text_area(
        "애니메이션으로 만들고 싶은 장면을 자세히 설명해주세요 (영어로 입력)",
        height=100,
        placeholder="예시: Back view of a beautiful woman walking on the beach with sea breeze, cartoon style"
    )

    if st.button("🎨 이미지 생성", use_container_width=True):
        if not prompt:
            st.error("프롬프트를 입력해주세요!")
        else:
            success = generate_image(prompt, image_width, image_height)
            if success:
                st.success("✅ 이미지 생성이 완료되었습니다!")

# 이미지가 생성되었을 때만 표시
if st.session_state.image_url:
    st.markdown("### 2️⃣ 생성된 이미지")
    st.image(st.session_state.image_url, width=400)
    
    if st.button("🎬 비디오 생성", use_container_width=True):
        success = generate_video(prompt, st.session_state.image_url)
        if success:
            st.success("✅ 비디오 생성 완료!")

# 비디오 표시 및 다운로드
if st.session_state.video_url:
    st.markdown("### 3️⃣ 생성된 비디오")
    
    video_container = st.container()
    with video_container:
        try:
            # 비디오 표시
            st.video(st.session_state.video_url)
            
            # 비디오 다운로드 준비
            response = requests.get(st.session_state.video_url, stream=True)
            
            if response.status_code == 200:
                # 임시 파일에 비디오 저장
                with open("temp_video.mp4", "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                # 파일에서 비디오 데이터 읽기
                with open("temp_video.mp4", "rb") as f:
                    video_data = f.read()
                
                # 다운로드 버튼
                st.download_button(
                    label="📥 비디오 다운로드",
                    data=video_data,
                    file_name="animation.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )
                
                # URL 복사 옵션
                with st.expander("🔗 비디오 URL"):
                    st.code(st.session_state.video_url)
                    
            else:
                st.error(f"비디오 다운로드 실패 (상태 코드: {response.status_code})")
                
        except Exception as e:
            st.error(f"비디오 처리 중 오류 발생: {str(e)}")
            
        finally:
            # 임시 파일 정리
            if os.path.exists("temp_video.mp4"):
                try:
                    os.remove("temp_video.mp4")
                except:
                    pass

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
