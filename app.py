import streamlit as st
import os
from pypdf import PdfReader
import google.generativeai as genai

# 1. 스트림릿 Secrets에서 안전하게 키를 불러옵니다.
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("API 키가 Secrets에 설정되지 않았습니다. 설정을 확인하세요.")
    st.stop()

# 2. PDF 지식 로드 (오류 방지)
@st.cache_data
def load_knowledge():
    if not os.path.exists("논어(전문및해석).pdf"):
        return "논어 파일 없음"
    reader = PdfReader("논어(전문및해석).pdf")
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

pdf_content = load_knowledge()

# 3. 화면 UI 구성
st.set_page_config(page_title="🎨 공자 스승님의 상담소", layout="centered")
st.title("📜 공자 스승님의 마음 상담소")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "어서 오시게나. 무슨 고민이 있는가?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 4. 채팅 및 답변 처리
if user_input := st.chat_input("공자님께 여쭤보세요..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"당신은 공자입니다. 아래 [지식]을 바탕으로 중학생 제자의 [질문]에 따뜻하게 답하세요.\n[지식]: {pdf_content[:15000]}\n[질문]: {user_input}"
            
            response = model.generate_content(prompt, stream=True)
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"오류: {e}")
