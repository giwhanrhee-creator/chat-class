import streamlit as st
import google.generativeai as genai

st.title("연결 상태 점검")

if st.button("구글과 연결 테스트 시작"):
    try:
        # Secrets에서 키를 가져오는지 확인
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.write("1. Secrets에서 키를 불러오는 데 성공했습니다.")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        st.write("2. 구글 AI 모델에 연결 중...")
        response = model.generate_content("안녕? 연결되었니?")
        
        st.success(f"3. 성공! 답변: {response.text}")
    except Exception as e:
        st.error(f"❌ 실패! 원인: {e}")
