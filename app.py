import streamlit as st
import os
from pypdf import PdfReader
import google.generativeai as genai

# ==========================================
# 1. 환경 설정 및 API 키
# ==========================================
part1 = "AIzaSyBo3bV3KJESRq" 
part2 = "rjGcbtAp8mO3w6h844T_E"
genai.configure(api_key=part1 + part2)

# ==========================================
# 2. PDF 지식 데이터베이스 로드 및 검색 기능 (이 부분이 중요합니다)
# ==========================================
@st.cache_data
def load_pdf_knowledge(pdf_path):
    if not os.path.exists(pdf_path):
        return []
    reader = PdfReader(pdf_path)
    knowledge_base = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            knowledge_base.append(text)
    return knowledge_base

def get_relevant_text(user_query, knowledge_base):
    # 사용자의 질문과 관련된 PDF 페이지를 찾아내는 간단한 검색 로직
    for page_text in knowledge_base:
        if any(keyword in page_text for keyword in user_query.split() if len(keyword) > 2):
            return page_text
    return knowledge_base[0] if knowledge_base else "내용 없음"

# ==========================================
# 3. 모델 설정
# ==========================================
def get_model():
    return genai.GenerativeModel("gemini-1.5-flash")

# ==========================================
# 4. 앱 UI
# ==========================================
st.set_page_config(page_title="🎨 논어 마음 상담소", layout="centered")
st.title("📜 공자 스승님의 마음 상담소")

# PDF 지식고 생성
pdf_path = "논어(전문및해석).pdf"
knowledge = load_pdf_knowledge(pdf_path)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "어서 오시게나. 무엇이 궁금한가?"}]

# 채팅 기록 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 사용자 입력
if user_input := st.chat_input("공자님께 여쭤보세요..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # 질문과 관련된 논어 구절 검색
            context = get_relevant_text(user_input, knowledge)
            
            # AI에게 역할과 지식을 함께 전달
            full_prompt = f"""
            너는 공자이다. 다음 [논어 구절]을 바탕으로 중학생 제자에게 따뜻하고 정중하게 상담해줘.
            [논어 구절]: {context[:3000]}
            [제자의 고민]: {user_input}
            """
            
            model = get_model()
            response = model.generate_content(full_prompt, stream=True)
            
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"⚠️ 연결 오류 발생: {e}")
