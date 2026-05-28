import streamlit as st
import google.generativeai as genai

st.title("사용 가능한 모델 목록 확인")

if st.button("내 API 키가 허용하는 모델 목록 불러오기"):
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # 허용된 모든 모델을 가져와서 이름만 출력
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.write("사용 가능한 모델 목록:")
        st.write(models)
    except Exception as e:
        st.error(f"오류: {e}")
