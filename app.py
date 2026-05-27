import streamlit as st
from google import genai

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="일정 정리 챗봇",
    page_icon="📅",
    layout="centered"
)

st.title("📅 일정 정리 Gemini 챗봇")
st.caption("Gemini 2.5 Flash Lite 기반")

# -----------------------------
# Gemini Client 생성
# -----------------------------
try:
    client = genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )
except Exception as e:
    st.error(f"API 키 설정 오류: {e}")
    st.stop()

# -----------------------------
# 시스템 프롬프트
# -----------------------------
SYSTEM_PROMPT = """
당신은 일정 정리를 도와주는 AI 비서입니다.

역할:
- 사용자의 일정을 깔끔하게 정리
- 날짜별/시간별로 보기 좋게 요약
- 중요한 일정 우선순위 표시
- 일정 충돌이 있으면 알려주기
- 간단한 할 일(To-do) 목록 생성
- 한국어로 친절하게 응답

출력 형식:
- Markdown 형식 사용
- 표나 리스트 적극 활용
"""

# -----------------------------
# 세션 상태 초기화
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# 이전 채팅 출력
# -----------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------
# 채팅 입력
# -----------------------------
user_input = st.chat_input(
    "일정을 입력하세요. 예: 내일 오후 3시 회의, 금요일 병원 예약"
)

# -----------------------------
# 사용자 입력 처리
# -----------------------------
if user_input:

    # 사용자 메시지 저장
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # 사용자 메시지 출력
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI 응답 영역
    with st.chat_message("assistant"):

        response_placeholder = st.empty()

        try:
            # 대화 히스토리 구성
            conversation_text = SYSTEM_PROMPT + "\n\n"

            for msg in st.session_state.messages:
                role = "사용자" if msg["role"] == "user" else "AI"
                conversation_text += f"{role}: {msg['content']}\n"

            # 스트리밍 응답
            response = client.models.generate_content_stream(
                model="gemini-2.5-flash-lite",
                contents=conversation_text
            )

            full_response = ""

            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(
                        full_response + "▌"
                    )

            response_placeholder.markdown(full_response)

            # 응답 저장
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })

        except Exception as e:
            error_message = f"""
❌ 오류가 발생했습니다.

오류 내용:
```bash
{str(e)}
