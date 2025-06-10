import streamlit as st
from urllib.parse import quote
import requests
import feedparser

st.set_page_config(page_title="📲 숏폼 뉴스 & 논문 & 영상 뷰어", layout="centered")
st.title("📲 숏폼 뉴스 & 논문 & 영상 뷰어")

# API 키 설정 (본인의 NewsAPI 키를 입력하세요)
NEWS_API_KEY = "여기에_본인의_NewsAPI_키_입력"

# 세션 상태 초기화
if "index" not in st.session_state:
    st.session_state.index = 0
if "data" not in st.session_state:
    st.session_state.data = []
if "source" not in st.session_state:
    st.session_state.source = None

# 검색어 및 데이터 출처 입력
query = st.text_input("관심 있는 키워드를 입력하세요:", "AI")
source = st.selectbox("데이터 출처 선택", ["News", "arXiv Papers", "Video (URL 직접 입력)"])

# 영상 URL 입력 (영상 모드일 때만 보이도록)
video_url = None
if source == "Video (URL 직접 입력)":
    video_url = st.text_input("영상 URL을 입력하세요 (유튜브 숏츠, 릴스 등)")

# 뉴스 API 함수
def fetch_news(query, api_key):
    query_encoded = quote(query)
    url = f"https://newsapi.org/v2/everything?q={query_encoded}&sortBy=publishedAt&language=en&pageSize=10&apiKey={api_key}"
    response = requests.get(url)

    if response.status_code != 200:
        st.error(f"뉴스 API 오류: {response.status_code}")
        st.error(f"응답 내용: {response.text}")
        return []

    data = response.json()
    if data.get("status") != "ok":
        st.error(f"뉴스 API 오류 메시지: {data.get('message')}")
        return []

    return data.get("articles", [])

# arXiv API 함수
def fetch_arxiv(query, max_results=10):
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    feed = feedparser.parse(url)
    if feed.bozo:
        st.error("arXiv API 파싱 오류")
        return []
    return feed.entries

# 검색 버튼 클릭 시
if st.button("검색 시작"):
    st.session_state.index = 0
    st.session_state.source = source

    if source == "News":
        st.session_state.data = fetch_news(query, NEWS_API_KEY)
    elif source == "arXiv Papers":
        st.session_state.data = fetch_arxiv(query)
    elif source == "Video (URL 직접 입력)":
        if video_url:
            st.session_state.data = [video_url]
        else:
            st.error("영상 URL을 입력해주세요")
            st.session_state.data = []
    else:
        st.session_state.data = []

# 데이터가 있으면 보여주기
if st.session_state.data:
    idx = st.session_state.index

    if st.session_state.source == "News":
        item = st.session_state.data[idx]
        st.markdown(f"### 📰 {item.get('title', '제목 없음')}")
        # 이미지가 있으면 보여주기
        if item.get("urlToImage"):
            st.image(item["urlToImage"], use_column_width=True)
        st.write(item.get("description", "설명 없음"))
        st.markdown(f"[기사 원문 보기]({item.get('url', '#')})")
        st.caption(f"{item.get('source', {}).get('name', '')} | {item.get('publishedAt', '')[:10]}")

    elif st.session_state.source == "arXiv Papers":
        item = st.session_state.data[idx]
        st.markdown(f"### 📄 {item.title}")
        st.write(item.summary)
        st.markdown(f"[arXiv 원문 보기]({item.link})")
        st.caption(", ".join([author.name for author in item.authors]))

    elif st.session_state.source == "Video (URL 직접 입력)":
        video_url = st.session_state.data[0]
        st.video(video_url)

    # 이전 / 다음 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅ 이전") and idx > 0:
            st.session_state.index -= 1
            st.experimental_rerun()
    with col2:
        if st.button("다음 ➡") and idx < len(st.session_state.data) - 1:
            st.session_state.index += 1
            st.experimental_rerun()
else:
    st.write("검색 버튼을 눌러 결과를 받아오세요.")
