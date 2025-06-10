import streamlit as st
from urllib.parse import quote
import requests
import feedparser

st.set_page_config(page_title="숏폼 뉴스 & 논문 & 영상 뷰어", layout="centered")
st.title("📲 숏폼 뉴스 & 논문 & 영상 뷰어")

# API 키 설정 (본인의 NewsAPI 키를 입력하세요)
NEWS_API_KEY = st.secrets['SECRET_API_KEY'] # NewsAPI 키를 Streamlit Secrets에 저장해주세요.

# 세션 상태 초기화
if "index" not in st.session_state:
    st.session_state.index = 0
if "data" not in st.session_state:
    st.session_state.data = []
if "source" not in st.session_state:
    st.session_state.source = None

# 사용자 입력 섹션
st.header("🔍 검색 설정")
query = st.text_input("어떤 내용이 궁금하신가요? (예: AI, 환경, 건강)", "AI")
source_options = {
    "뉴스": "News",
    "arXiv 논문": "arXiv Papers",
    "영상 (URL 직접 입력)": "Video (URL 직접 입력)"
}
selected_source_korean = st.selectbox("어떤 종류의 정보를 찾으시나요?", list(source_options.keys()))
source = source_options[selected_source_korean]

video_url = None
if source == "Video (URL 직접 입력)":
    video_url = st.text_input("유튜브 숏츠, 릴스 등 영상의 URL을 여기에 입력해주세요.")

# 뉴스 API 함수
@st.cache_data(ttl=3600) # 1시간 캐싱
def fetch_news(query, api_key):
    query_encoded = quote(query)
    url = f"https://newsapi.org/v2/everything?q={query_encoded}&sortBy=publishedAt&language=en&pageSize=10&apiKey={api_key}"
    response = requests.get(url)

    if response.status_code != 200:
        st.error(f"뉴스 정보를 가져오는 데 실패했습니다. 오류 코드: {response.status_code}")
        st.error(f"응답 내용: {response.text}")
        return []

    data = response.json()
    if data.get("status") != "ok":
        st.error(f"뉴스 API 오류 메시지: {data.get('message')}")
        return []

    return data.get("articles", [])

# arXiv API 함수
@st.cache_data(ttl=3600) # 1시간 캐싱
def fetch_arxiv(query, max_results=10):
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    try:
        feed = feedparser.parse(url)
        if feed.bozo:
            st.error("arXiv 논문 정보를 파싱하는 데 오류가 발생했습니다.")
            return []
        return feed.entries
    except Exception as e:
        st.error(f"arXiv 논문 정보를 가져오는 중 오류 발생: {e}")
        return []

# 검색 버튼 클릭 시
if st.button("🚀 검색 시작하기"):
    st.session_state.index = 0
    st.session_state.source = source
    st.session_state.data = [] # 이전 검색 결과 초기화

    if source == "News":
        st.session_state.data = fetch_news(query, NEWS_API_KEY)
        if not st.session_state.data:
            st.warning("뉴스 검색 결과가 없습니다. 다른 키워드로 다시 시도해주세요.")
    elif source == "arXiv Papers":
        st.session_state.data = fetch_arxiv(query)
        if not st.session_state.data:
            st.warning("arXiv 논문 검색 결과가 없습니다. 다른 키워드로 다시 시도해주세요.")
    elif source == "Video (URL 직접 입력)":
        if video_url:
            st.session_state.data = [video_url]
        else:
            st.error("영상을 보려면 URL을 입력해주세요.")
            st.session_state.data = []

# ---
st.markdown("---")
st.header("💡 검색 결과")

# 데이터가 있으면 보여주기
if st.session_state.data:
    idx = st.session_state.index
    total_items = len(st.session_state.data)

    if st.session_state.source == "News":
        if idx < total_items:
            item = st.session_state.data[idx]
            st.markdown(f"### 📰 {item.get('title', '제목 없음')}")
            if item.get("urlToImage"):
                st.image(item["urlToImage"], use_column_width=True, caption="기사 이미지")
            st.write(item.get("description", "설명 없음"))
            st.markdown(f"[➡️ 기사 원문 보기]({item.get('url', '#')})")
            st.caption(f"출처: {item.get('source', {}).get('name', '알 수 없음')} | 발행일: {item.get('publishedAt', '')[:10]}")
        else:
            st.info("더 이상 표시할 뉴스가 없습니다.")

    elif st.session_state.source == "arXiv Papers":
        if idx < total_items:
            item = st.session_state.data[idx]
            st.markdown(f"### 📄 {item.title}")
            st.write(item.summary)
            st.markdown(f"[➡️ arXiv 원문 보기]({item.link})")
            authors = ", ".join([author.name for author in item.authors])
            st.caption(f"저자: {authors}")
        else:
            st.info("더 이상 표시할 논문이 없습니다.")

    elif st.session_state.source == "Video (URL 직접 입력)":
        if video_url: # Directly use the video_url from input if it's set
            st.video(video_url)
        else: # Fallback if somehow video_url is not set but source is video
            st.warning("영상 URL이 유효하지 않습니다.")

    # 이전 / 다음 버튼
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        # 'key' 매개변수를 추가하여 각 버튼에 고유한 ID를 부여합니다.
        if st.button("⬅️ 이전 콘텐츠", key="prev_button_active") and idx > 0:
            st.session_state.index -= 1
            st.experimental_rerun()
        # 이 버튼은 위에 있는 조건이 거짓일 때 (즉, idx == 0 일 때)만 나타납니다.
        elif st.button("⬅️ 이전 콘텐츠", key="prev_button_inactive"):
            st.info("첫 번째 콘텐츠입니다.")
    with col2:
        # 'key' 매개변수를 추가하여 각 버튼에 고유한 ID를 부여합니다.
        if st.button("다음 콘텐츠 ➡️", key="next_button_active") and idx < total_items - 1:
            st.session_state.index += 1
            st.experimental_rerun()
        # 이 버튼은 위에 있는 조건이 거짓일 때 (즉, 마지막 항목일 때)만 나타납니다.
        elif st.button("다음 콘텐츠 ➡️", key="next_button_inactive"):
            st.info("마지막 콘텐츠입니다.")

    st.markdown(f"<p style='text-align: center;'>현재 {idx + 1} / {total_items} 페이지</p>", unsafe_allow_html=True)

else:
    st.info("아직 검색 결과가 없습니다. 위에 검색 조건을 입력하고 '🚀 검색 시작하기' 버튼을 눌러주세요!")
