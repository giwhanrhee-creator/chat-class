import streamlit as st
import os
from pypdf import PdfReader
import google.generativeai as genai

# 1. API 키 설정 (스트림릿 Secrets 사용)
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error("API 키를 Secrets 설정에서 확인해주세요.")
    st.stop()

# 2. PDF 지식 로드 및 검색
@st.cache_data
def load_pdf_knowledge(pdf_path):
    if not os.path.exists(pdf_path):
        return ""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

pdf_text = load_pdf_knowledge("논어(전문및해석).pdf")

# 3. 모델 설정 (확인된 최신 모델명 사용)
def get_model():
    # 리스트에서 확인된 gemini-3.5-flash 사용
    return genai.GenerativeModel("gemini-3.5-flash")

# 4. 앱 UI
st.set_page_config(page_title="📜 공자 스승님의 마음 상담소", layout="centered")
st.title("📜 공자 스승님의 마음 상담소")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "어서 오시게나. 무엇이 고민인가?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 5. 학생용 예상 질문 버튼
st.markdown("---")
st.write("⬇️ **고민을 선택해 보세요:**")
col1, col2, col3 = st.columns(3)

preset_query = None
if col1.button("✏️ 성적 고민"): preset_query = "스승님, 공부해도 성적이 안 올라 속상합니다."
if col2.button("🤝 친구 관계"): preset_query = "친구와 다투었는데 먼저 화해하기가 어려워요."
if col3.button("🎯 진로 고민"): preset_query = "제 꿈이 무엇인지 잘 모르겠어서 불안해요."

user_input = st.chat_input("공자님께 고민을 말씀드려 보세요...")
if preset_query: user_input = preset_query

# 6. 채팅 답변 로직
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            model = get_model()
            
            # 시스템 프롬프트 구성
            prompt = f"""
            너는 유교의 창시자 '공자'이다. 아래 [논어 지식]을 참고하여, 
            고민을 가진 중학생 제자에게 매우 정중하고 따뜻하게 위로와 가르침을 주어라.
            [논어 지식]: {pdf_text[:10000]}
            [제자의 고민]: {user_input}
            """
            
            response = model.generate_content(prompt, stream=True)
            
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"답변 생성 중 오류가 발생했습니다: {e}")
