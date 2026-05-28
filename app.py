import streamlit as st
import os
from pypdf import PdfReader
import google.generativeai as genai

# ==========================================
# 1. API 키 설정 (안전한 조각 결합)
# ==========================================
# 큰따옴표 안에 선생님의 진짜 API 키를 반으로 나누어 넣어주세요. 공백이 없어야 합니다!
part1 = "AIzaSyBo3bV3KJESRq" 
part2 = "rjGcbtAp8mO3w6h844T_E"

TEACHER_API_KEY = part1 + part2

# 구글 공식 라이브러리에 키 등록
genai.configure(api_key=TEACHER_API_KEY)

# ==========================================
# 2. 앱 페이지 설정 및 디자인
# ==========================================
st.set_page_config(page_title="🎨 논어 마음 상담소", page_icon="📜", layout="centered")

st.title("📜 공자 스승님의 마음 상담소")
st.markdown("---")

# ==========================================
# 3. PDF 지식 데이터베이스 로드
# ==========================================
@st.cache_data
def load_pdf_knowledge(pdf_path):
    if not os.path.exists(pdf_path):
        return None
    reader = PdfReader(pdf_path)
    knowledge_base = []
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            knowledge_base.append({"page": page_num + 1, "content": text})
    return knowledge_base

def find_relevant_context(user_query, knowledge_base):
    if not knowledge_base:
        return ""
    keywords = [word for word in user_query.split() if len(word) >= 2]
    best_page = None
    max_matches = 0
    for page in knowledge_base:
        matches = sum(1 for kw in keywords if kw in page["content"])
        if matches > max_matches:
            max_matches = matches
            best_page = page["content"]
    return best_page if best_page else knowledge_base[0]["content"]

pdf_path = "논어(전문및해석).pdf"
논어_지식고 = load_pdf_knowledge(pdf_path)

if 논어_지식고 is None:
    st.error(f"⚠️ 폴더 안에 '{pdf_path}' 파일이 없습니다. 파일명을 확인해 주세요.")

# ==========================================
# 4. 대화 기록 관리 및 초기화 기능
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "어서 오시게나. 요즘 그대의 마음을 어지럽히는 고민이 무엇인가? 함께 지혜를 나누어보세."}
    ]

col1, col2 = st.columns([8, 2])
with col2:
    if st.button("🔄 처음부터 다시 대화하기"):
        st.session_state.messages = [
            {"role": "assistant", "content": "어서 오시게나. 요즘 그대의 마음을 어지럽히는 고민이 무엇인가? 함께 지혜를 나누어보세."}
        ]
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ==========================================
# 5. 학생들이 쉽게 누를 수 있는 고민 예시 버튼
# ==========================================
st.markdown("⬇️ **어떤 말을 해야 할지 모르겠다면 아래 고민을 눌러보세요!**")
btn_col1, btn_col2, btn_col3 = st.columns(3)

preset_query = ""
with btn_col1:
    if st.button("✏️ 성적이 안 올라 고민이에요"):
        preset_query = "스승님, 열심히 공부하는데도 성적이 잘 오르지 않아 속상합니다. 어떻게 해야 할까요?"
with btn_col2:
    if st.button("🤝 친구와 다투어 서먹해요"):
        preset_query = "스승님, 친한 친구와 말다툼을 하고 사이가 서먹해졌습니다. 먼저 다가가기 부끄러운데 어쩌죠?"
with btn_col3:
    if st.button("🎯 미래에 뭘 할지 모르겠어요"):
        preset_query = "스승님, 제가 커서 무엇을 해야 할지, 제 꿈이 무엇인지 잘 모르겠어서 불안합니다."

user_input = st.chat_input("공자 스승님께 여쭐 고민을 적어보세요...")

if preset_query:
    user_input = preset_query

# ==========================================
# 6. [구글 공식 라이브러리 적용] 통신 안정화
# ==========================================
if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            referenced_context = find_relevant_context(user_input, 논어_지식고)
            
            confucius_prompt = f"""
너는 유교의 창시자 '공자(孔子)'이다. 사용자는 가르침을 구하는 중학교 제자(청소년)이다.
[대화 규칙]
1. 말투: 매우 정중하고, 온화하며, 자애로운 스승의 어조(~이지요, ~해보는 것은 어떻겠습니까?, 대견합니다)를 쓴다.
2. 학생 맞춤형 가르침: 제자가 중학생 청소년임을 고려하여 지나치게 어렵거나 딱딱한 문어체는 피하고, 따뜻하게 위로하며 격려해 준다.
3. 지식 기반: 아래 제공된 [참고 논어 구절]을 바탕으로 답변해야 한다. 구절에 포함된 한자 원문이나 한글 해석을 대화에 자연스럽게 인용하라.
4. 역할: 질문에 대해 단순히 답을 주기보다, 제공된 구절의 지혜를 현대적으로 풀어서 제자가 스스로 깨닫고 위로받도록 이끌어주어라.

[참고 논어 구절]
{referenced_context}
"""
            
            # 구글 공식 모델 불러오기
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=confucius_prompt
            )
            
            # 텍스트 조각이 깨질 위험이 없는 공식 스트리밍 통신
            response = model.generate_content(user_input, stream=True)
            
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"⚠️ 구글 AI 연결 중 오류가 발생했습니다: {e}")
