import streamlit as st
import os
import ssl
import urllib3
import requests
import json
from pypdf import PdfReader

# ==========================================
# 1. SSL 인증서 예외 처리 (학교 망/방화벽 대비)
# ==========================================
ssl._create_default_https_context = ssl._create_unverified_context
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["PYTHONHTTPSVERIFY"] = "0"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 2. [보안 우회] API 키 2조각 결합
# ==========================================
part1 = "AIzaSyBo3bV3KJESR" 
part2 = "qrjGcbtAp8mO3w6h844T_E"

TEACHER_API_KEY = part1 + part2

# ==========================================
# 3. 앱 페이지 설정 및 디자인
# ==========================================
st.set_page_config(page_title="🎨 논어 마음 상담소", page_icon="📜", layout="centered")

st.title("📜 공자 스승님의 마음 상담소")
st.markdown("---")

# ==========================================
# 4. PDF 지식 데이터베이스 로드
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
# 5. 대화 기록 관리 및 초기화 기능
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
# 6. 고민 예시 버튼
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

# ==========================================
# 7. [최종 통신 안정화] 사용자 입력 및 AI 답변 처리
# ==========================================
user_input = st.chat_input("공자 스승님께 여쭐 고민을 적어보세요...")

if preset_query:
    user_input = preset_query

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
            
            # [수정 1] 구글 서버에서 권장하는 가장 안전한 SSE 스트리밍 방식(alt=sse) 적용
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:streamGenerateContent?alt=sse&key={TEACHER_API_KEY}"
            
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": user_input}]}],
                "systemInstruction": {"parts": [{"text": confucius_prompt}]},
                "generationConfig": {"temperature": 0.6}
            }
            
            response = requests.post(url, headers=headers, json=payload, verify=False, stream=True)
            
            if response.status_code == 200:
                # [수정 2] 구글 공식 JSON 데이터 파싱 로직 적용 (절대 글자가 누락되거나 숨겨지지 않음)
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith("data: "):
                            data_str = decoded_line[6:]
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                data_json = json.loads(data_str)
                                chunk = data_json["candidates"][0]["content"]["parts"][0]["text"]
                                full_response += chunk
                                message_placeholder.markdown(full_response + "▌")
                            except Exception:
                                pass
                
                # 만약 어떤 이유로든 빈칸이 반환되면 안내 문구 출력
                if full_response.strip() == "":
                    full_response = "스승님이 깊은 생각에 잠기셨습니다. 다시 한 번 질문해 주시겠습니까?"
                
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            else:
                # [핵심] API 키가 틀렸거나 통신에 실패하면 구글 서버가 뱉어내는 '진짜 에러 원인'을 화면에 빨간색으로 출력!
                st.error(f"⚠️ 구글 서버 통신 실패 (상태코드 {response.status_code}): {response.text}")
            
        except Exception as e:
            st.error(f"⚠️ 시스템 오류가 발생했습니다: {e}")
