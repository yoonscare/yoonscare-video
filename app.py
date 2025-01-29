import streamlit as st
import replicate
import requests
import time
import json
import os

# 페이지 기본 설정
st.set_page_config(
   page_title="AI 애니메이션 생성기",
   page_icon="🎭",
   layout="wide"
)

# 상태 초기화
if 'authentication_status' not in st.session_state:
   st.session_state.authentication_status = False
if 'image_url' not in st.session_state:
   st.session_state.image_url = None
if 'video_url' not in st.session_state:
   st.session_state.video_url = None
if 'api_key' not in st.session_state:
   st.session_state.api_key = None

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
   .css-1n76uvr {  /* 사이드바 */
       background-color: #0f172a;
   }
   .stMarkdown {
       color: #ffffff;
   }
   .stStatus {
       background-color: #1e293b;
       color: white;
   }
   .stExpander {
       background-color: #1e293b;
       border: 1px solid #334155;
   }
   .error {
       background-color: #7f1d1d;
       color: white;
       padding: 1rem;
       border-radius: 0.5rem;
   }
   .success {
       background-color: #064e3b;
       color: white;
       padding: 1rem;
       border-radius: 0.5rem;
   }
   .status {
       background-color: #1e293b;
       color: white;
       padding: 1rem;
       border-radius: 0.5rem;
       margin: 1rem 0;
   }
   .stSlider > div > div > div > div {
       background-color: #4361ee;
   }
   .stTextInput > label {
       color: white !important;
   }
   .stTextArea > label {
       color: white !important;
   }
   .element-container {
       background-color: #1e293b;
       padding: 1rem;
       border-radius: 0.5rem;
       margin: 1rem 0;
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
   .title {
       color: white !important;
   }
   </style>
""", unsafe_allow_html=True)

def init_replicate_api():
   try:
       if st.session_state.api_key:
           os.environ["REPLICATE_API_TOKEN"] = st.session_state.api_key
           replicate.Client(api_token=st.session_state.api_key)
           return True
       return False
   except Exception as e:
       st.markdown(f'<p class="error">❌ API 키 인증에 실패했습니다: {str(e)}</p>', unsafe_allow_html=True)
       return False

# 이미지 생성 함수
def generate_image():
   if not init_replicate_api():
       st.markdown('<p class="error">❌ API 키를 먼저 설정해주세요.</p>', unsafe_allow_html=True)
       return False
       
   try:
       with st.status("🎨 이미지 생성 중...", expanded=True) as status:
           st.markdown('<p class="status">이미지를 생성하고 있습니다. 잠시만 기다려주세요...</p>', unsafe_allow_html=True)
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
               st.markdown('<p class="success">✅ 이미지 생성이 완료되었습니다!</p>', unsafe_allow_html=True)
               return True
           st.markdown('<p class="error">❌ 이미지 생성에 실패했습니다.</p>', unsafe_allow_html=True)
           return False
   except Exception as e:
       st.markdown(f'<p class="error">❌ 오류 발생: {str(e)}</p>', unsafe_allow_html=True)
       return False

# 비디오 생성 함수
def generate_video():
   if not init_replicate_api():
       st.markdown('<p class="error">❌ API 키를 먼저 설정해주세요.</p>', unsafe_allow_html=True)
       return False
       
   try:
       with st.status("🎬 비디오 생성 중...", expanded=True) as status:
           st.markdown('<p class="status">비디오를 생성하고 있습니다. 잠시만 기다려주세요...</p>', unsafe_allow_html=True)
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
               st.markdown('<p class="success">✅ 비디오 생성이 완료되었습니다!</p>', unsafe_allow_html=True)
               return True
           st.markdown('<p class="error">❌ 비디오 생성에 실패했습니다.</p>', unsafe_allow_html=True)
           return False
   except Exception as e:
       st.markdown(f'<p class="error">❌ 오류 발생: {str(e)}</p>', unsafe_allow_html=True)
       return False

# 사이드바
with st.sidebar:
   st.markdown("<h2 class='title'>⚙️ 설정</h2>", unsafe_allow_html=True)
   api_key = st.text_input("Replicate API 키", type="password", key="api_input")
   
   if api_key:
       st.session_state.api_key = api_key
       if init_replicate_api():
           st.markdown('<p class="success">✅ API 키가 확인되었습니다!</p>', unsafe_allow_html=True)
           st.session_state.authentication_status = True
       else:
           st.markdown('<p class="error">❌ API 키 인증에 실패했습니다.</p>', unsafe_allow_html=True)
           st.session_state.authentication_status = False
   
   st.markdown("---")
   st.markdown("<h3 class='title'>🎨 이미지 설정</h3>", unsafe_allow_html=True)
   image_width = st.slider("너비", 384, 1024, 768, 128)
   image_height = st.slider("높이", 384, 1024, 768, 128)

# 메인 영역
st.markdown("<h1 class='main-header'>🎭 AI 애니메이션 생성기</h1>", unsafe_allow_html=True)

# 프롬프트 입력
prompt = st.text_area(
   "애니메이션으로 만들고 싶은 장면을 자세히 설명해주세요 (영어로 입력)",
   height=100,
   placeholder="예시: Back view of a beautiful woman walking on the beach with sea breeze, cartoon style"
)

# 버튼 컬럼
col1, col2 = st.columns(2)

with col1:
   if st.button("1️⃣ 이미지 생성", use_container_width=True, disabled=not st.session_state.authentication_status):
       if not prompt:
           st.markdown('<p class="error">❌ 프롬프트를 입력해주세요!</p>', unsafe_allow_html=True)
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
   st.markdown("<h3 class='title'>🖼 생성된 이미지</h3>", unsafe_allow_html=True)
   st.image(st.session_state.image_url, use_column_width=True)

if st.session_state.video_url:
   st.markdown("<h3 class='title'>🎬 생성된 비디오</h3>", unsafe_allow_html=True)
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
       st.markdown('<p class="error">❌ 비디오 다운로드 준비 중 오류가 발생했습니다.</p>', unsafe_allow_html=True)

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
