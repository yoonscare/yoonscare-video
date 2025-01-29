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
if 'generation_complete' not in st.session_state:
   st.session_state.generation_complete = False

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
   div[data-testid="stSidebarNav"] {
       background-color: #0f172a;
   }
   .stMarkdown {
       color: #ffffff;
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
   .result-container {
       background: rgba(30, 41, 59, 0.7);
       padding: 2rem;
       border-radius: 10px;
       margin: 1rem 0;
   }
   .video-container {
       margin-top: 2rem;
   }
   </style>
""", unsafe_allow_html=True)

def init_replicate_api():
   if not st.session_state.api_key:
       return False
   try:
       token = st.session_state.api_key.strip()
       client = replicate.Client(api_token=token)
       os.environ["REPLICATE_API_TOKEN"] = token
       return True
   except Exception as e:
       st.error(f"API 키 인증 실패: {str(e)}")
       return False

def generate_image(prompt, width, height):
   if not st.session_state.api_key:
       st.error("API 키를 입력해주세요.")
       return False
   
   try:
       token = st.session_state.api_key.strip()
       client = replicate.Client(api_token=token)
       
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
       token = st.session_state.api_key.strip()
       client = replicate.Client(api_token=token)
       
       output = client.run(
           "minimax/video-01-live",
           input={
               "prompt": prompt,
               "first_frame_image": image_url
           }
       )
       
       if isinstance(output, list) and len(output) > 0:
           video_url = output[0]
           if video_url and video_url.startswith(('http://', 'https://')):
               st.session_state.video_url = video_url
               st.session_state.generation_complete = True
               return True
               
       st.error("비디오 생성에 실패했습니다.")
       return False
           
   except Exception as e:
       st.error(f"비디오 생성 중 오류가 발생했습니다: {str(e)}")
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
       cleaned_key = api_key.strip()
       st.session_state.api_key = cleaned_key
       os.environ["REPLICATE_API_TOKEN"] = cleaned_key
       
       try:
           client = replicate.Client(api_token=cleaned_key)
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
prompt = st.text_area(
   "애니메이션으로 만들고 싶은 장면을 자세히 설명해주세요 (영어로 입력)",
   height=100,
   placeholder="예시: Back view of a beautiful woman walking on the beach with sea breeze, cartoon style"
)

# 생성 버튼
if st.button("✨ 애니메이션 생성 시작", use_container_width=True):
   if not prompt:
       st.error("프롬프트를 입력해주세요!")
   else:
       st.session_state.generation_complete = False
       
       # 이미지 생성
       with st.status("🎨 이미지 생성 중...", expanded=True) as status:
           success = generate_image(prompt, image_width, image_height)
           if success:
               status.update(label="✅ 이미지 생성 완료!", state="complete")
               
               # 비디오 생성
               status.update(label="🎬 비디오 생성 중...", state="running")
               video_success = generate_video(prompt, st.session_state.image_url)
               if video_success:
                   status.update(label="✅ 애니메이션 생성 완료!", state="complete")
               else:
                   status.update(label="❌ 비디오 생성 실패", state="error")
           else:
               status.update(label="❌ 이미지 생성 실패", state="error")

# 결과 표시
if st.session_state.image_url and st.session_state.video_url:
   with st.container():
       st.markdown("## 🎬 생성된 애니메이션")
       
       # 이미지와 비디오를 나란히 표시
       col1, col2 = st.columns([1, 2])
       
       with col1:
           st.markdown("### 첫 프레임")
           st.image(st.session_state.image_url, use_column_width=True)
       
       with col2:
           st.markdown("### 생성된 영상")
           st.video(st.session_state.video_url)
           
           # 다운로드 버튼
           if st.session_state.generation_complete:
               try:
                   response = requests.get(st.session_state.video_url)
                   if response.status_code == 200:
                       st.download_button(
                           label="📥 애니메이션 다운로드",
                           data=response.content,
                           file_name="animation.mp4",
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
       st.session_state.generation_complete = False
       st.experimental_rerun()

# 도움말
with st.expander("💡 프롬프트 작성 팁"):
   st.markdown("""
   - 캐릭터의 특징을 자세히 설명해주세요 (머리 색, 표정, 스타일 등)
   - 원하는 아트 스타일을 명시해주세요 (cartoon style, anime style 등)
   - 장면의 분위기나 움직임을 포함시켜주세요
   - 영어로 작성하면 더 좋은 결과를 얻을 수 있습니다
   """)
