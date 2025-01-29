import streamlit as st
import replicate
import requests
import os
from PIL import Image
from io import BytesIO
from tqdm import tqdm

# 페이지 기본 설정
st.set_page_config(
    page_title="AI 애니메이션 생성기",
    page_icon="🎭",
    layout="wide"
)

# 상태 초기화
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'image_url' not in st.session_state:
    st.session_state.image_url = None
if 'video_url' not in st.session_state:
    st.session_state.video_url = None

# Replicate API 초기화 함수
def init_replicate_api():
    if not st.session_state.api_key:
        return False
    try:
        os.environ["REPLICATE_API_TOKEN"] = st.session_state.api_key.strip()
        return True
    except Exception as e:
        st.error(f"API 키 인증 실패: {str(e)}")
        return False

# 이미지 다운로드 및 표시 함수
def display_image(image_url):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            st.image(image, caption="🖼 생성된 이미지", use_column_width=True)
        else:
            st.error("이미지를 불러오는 데 실패했습니다.")
    except Exception as e:
        st.error(f"이미지 표시 중 오류 발생: {e}")

# 비디오 다운로드 함수
def download_video(video_url):
    local_filename = "generated_video.mp4"
    response = requests.get(video_url, stream=True)

    if response.status_code != 200:
        st.error("비디오를 다운로드할 수 없습니다.")
        return None

    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 KB

    with open(local_filename, 'wb') as file, tqdm(
        desc="Downloading",
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(block_size):
            bar.update(len(data))
            file.write(data)

    return local_filename

# 비디오 생성 함수
def generate_video(prompt, image_url):
    if not st.session_state.api_key:
        st.error("API 키를 입력해주세요.")
        return False

    try:
        client = replicate.Client(api_token=st.session_state.api_key.strip())

        with st.spinner("🎬 비디오 생성 중..."):
            output = client.run(
                "minimax/video-01-live",
                input={"prompt": prompt, "first_frame_image": image_url}
            )

        if isinstance(output, list) and output:
            video_url = output[0]
            st.session_state.video_url = video_url

            # 비디오 다운로드 수행
            video_file = download_video(video_url)

            if video_file:
                st.success("✅ 비디오 생성이 완료되었습니다!")

                with open(video_file, "rb") as f:
                    st.download_button(
                        label="📥 비디오 다운로드",
                        data=f,
                        file_name="animation.mp4",
                        mime="video/mp4"
                    )

            return True
        else:
            st.error("❌ 비디오 생성에 실패했습니다.")
            return False

    except Exception as e:
        st.error(f"비디오 생성 중 오류가 발생했습니다: {str(e)}")
        return False

# UI 구성
st.sidebar.title("⚙️ 설정")
api_key = st.sidebar.text_input("Replicate API 키", type="password")
if api_key:
    st.session_state.api_key = api_key.strip()
    os.environ["REPLICATE_API_TOKEN"] = api_key.strip()
    st.sidebar.success("✅ API 키가 확인되었습니다!")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 이미지 설정")
image_width = st.sidebar.slider("너비", 384, 1024, 640, 128)
image_height = st.sidebar.slider("높이", 384, 1024, 640, 128)

st.markdown("<h1 class='main-header'>🎭 AI 애니메이션 생성기</h1>", unsafe_allow_html=True)

# 프롬프트 입력
prompt = st.text_area(
    "애니메이션으로 만들고 싶은 장면을 자세히 설명해주세요 (영어로 입력)",
    height=100
)

# 버튼 영역
col1, col2 = st.columns(2)

with col1:
    if st.button("1️⃣ 이미지 생성", use_container_width=True):
        if not prompt:
            st.error("프롬프트를 입력해주세요!")
        else:
            # 여기에서 실제 이미지 생성 API 호출 (현재 더미 URL)
            st.session_state.image_url = "https://via.placeholder.com/640x640.png"
            st.success("✅ 이미지 생성이 완료되었습니다!")

with col2:
    if st.button("2️⃣ 비디오 생성", use_container_width=True, disabled=not st.session_state.image_url):
        if not st.session_state.image_url:
            st.error("먼저 이미지를 생성해주세요.")
        else:
            generate_video(prompt, st.session_state.image_url)

# 결과 표시
if st.session_state.image_url:
    display_image(st.session_state.image_url)

if st.session_state.video_url:
    st.video(st.session_state.video_url)

# 비디오 다운로드 버튼 추가
if st.session_state.video_url:
    video_file = download_video(st.session_state.video_url)
    
    if video_file:
        with open(video_file, "rb") as f:
            st.download_button(
                label="📥 비디오 다운로드",
                data=f,
                file_name="animation.mp4",
                mime="video/mp4"
            )
