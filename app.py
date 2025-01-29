import streamlit as st
import replicate
import requests
from PIL import Image
from io import BytesIO
import time

# 페이지 기본 설정
st.set_page_config(
    page_title="AI 애니메이션 생성기",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 적용
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #f5f7fa, #c3cfe2);
    }
    .main-header {
        font-family: 'Arial Black', sans-serif;
        background: -webkit-linear-gradient(45deg, #2c3e50, #3498db);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.title("⚙️ 설정")
    api_key = st.text_input("Replicate API 키를 입력하세요", type="password")
    st.caption("API 키는 안전하게 저장되며 세션에서만 사용됩니다.")
    
    st.markdown("---")
    st.markdown("### 🎨 이미지 설정")
    image_width = st.slider("이미지 너비", 384, 1024, 768, 128)
    image_height = st.slider("이미지 높이", 384, 1024, 768, 128)
    
    st.markdown("---")
    st.markdown("### ℹ️ 도움말")
    with st.expander("사용 방법"):
        st.write("""
        1. API 키를 입력합니다
        2. 원하는 애니메이션에 대한 설명을 입력합니다
        3. '생성 시작' 버튼을 클릭합니다
        4. 잠시 기다리면 이미지와 비디오가 생성됩니다
        """)

# 메인 페이지
st.markdown("<h1 class='main-header'>🎭 AI 애니메이션 생성기</h1>", unsafe_allow_html=True)
st.markdown("##### 당신의 상상을 움직이는 애니메이션으로 만들어보세요!")

# 프롬프트 입력
prompt = st.text_area(
    "애니메이션으로 만들고 싶은 장면을 자세히 설명해주세요",
    placeholder="예: a young woman with long brown hair laughing, cartoon style, soft lighting",
    height=100
)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("✨ 생성 시작", use_container_width=True):
        if not api_key:
            st.error("🔑 API 키를 입력해주세요!")
        elif not prompt:
            st.error("✍️ 프롬프트를 입력해주세요!")
        else:
            try:
                # API 키 설정
                replicate.Client(api_token=api_key)
                
                with st.status("🎨 AI가 작업중입니다...", expanded=True) as status:
                    # 1. 이미지 생성
                    st.write("🖼 첫 프레임 이미지를 생성하고 있습니다...")
                    image_output = replicate.run(
                        "stability-ai/sdxl:2b017d9b67edd2ee1401238df49d75da53c523f36e363881e057f5dc3ed3c5b2",
                        input={
                            "prompt": prompt,
                            "width": image_width,
                            "height": image_height,
                        }
                    )
                    
                    if image_output:
                        image_url = image_output[0] if isinstance(image_output, list) else image_output
                        st.write("✅ 이미지 생성 완료!")
                        
                        # 2. 비디오 생성
                        st.write("🎬 비디오를 생성하고 있습니다...")
                        video_output = replicate.run(
                            "minimax/video-01-live",
                            input={
                                "prompt": prompt,
                                "prompt_optimizer": True,
                                "first_frame_image": str(image_url)
                            }
                        )
                        
                        if video_output:
                            video_url = video_output[0] if isinstance(video_output, list) else video_output
                            status.update(label="✨ 생성 완료!", state="complete")
                            
                            # 결과 표시
                            col_img, col_vid = st.columns(2)
                            with col_img:
                                st.markdown("### 🖼 생성된 이미지")
                                st.image(image_url, use_column_width=True)
                            
                            with col_vid:
                                st.markdown("### 🎬 생성된 비디오")
                                st.video(video_url)
                            
                            # 다운로드 버튼
                            st.download_button(
                                label="🎬 비디오 다운로드",
                                data=requests.get(video_url).content,
                                file_name="generated_animation.mp4",
                                mime="video/mp4"
                            )
                        else:
                            st.error("비디오 생성에 실패했습니다.")
                    else:
                        st.error("이미지 생성에 실패했습니다.")
                        
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")

# 페이지 하단
st.markdown("---")
st.markdown("### 💡 프롬프트 작성 팁")
with st.expander("더 나은 결과를 위한 팁"):
    st.markdown("""
    - 캐릭터의 특징을 자세히 설명해주세요 (머리 색, 표정, 스타일 등)
    - 원하는 아트 스타일을 명시해주세요 (애니메이션, 만화, 사실적 등)
    - 장면의 분위기나 감정을 포함시켜주세요
    - 배경이나 조명에 대한 설명도 추가하면 좋습니다
    """)
