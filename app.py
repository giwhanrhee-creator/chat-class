import streamlit as st
import google.generativeai as genai

# 1. API 키 설정 (오류 방지)
try:
    genai.configure(api_key="AIzaSyBo3bV3KJESR" + "qrjGcbtAp8mO3w6h844T_E")
except:
    st.error("API 설정 오류")

st.title("📜 공자 스승님 상담소")

# 2. 채팅 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "어서 오시게나."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 3. 질문 처리
if user_input := st.chat_input("질문을 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)
    
    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(f"당신은 공자입니다. 제자의 고민에 답해주세요: {user_input}")
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.write(f"답변 생성 실패: {str(e)}")
