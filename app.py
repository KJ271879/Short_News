import streamlit as st
import requests
import feedparser

# 기본 설정
st.set_page_config(page_title="ShortForm 뉴스/논문 뷰어", layout="centered")
st.title("📲 숏폼 뉴스 & 논문 뷰어")

# 입력받기
query = st.text_input("관심 있는 키워드를 입력하세요:", "AI")
source = st.selectbox("데이터 출처:", ["News", "arXiv Papers"])

NEWS_API_KEY = "secret_key"

# News API 함수
def fetch_news(query, api_key):
    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&pageSize=5&apiKey={api_key}"
    response = requests.get(url)
    return response.json().get("articles", [])

# arXiv API 함수
def fetch_arxiv(query, max_results=5):
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    feed = feedparser.parse(url)
    return feed.entries

# 검색 버튼
if st.button("검색 시작"):
    st.info(f"‘{query}’에 대한 검색 결과를 가져오는 중...")

    if source == "News":
        articles = fetch_news(query, NEWS_API_KEY)
        for article in articles:
            with st.expander(f"📰 {article['title']}"):
                st.write(article.get("description", "설명 없음"))
                st.markdown(f"[원문 링크]({article['url']})")
                st.caption(f"{article['source']['name']} | {article['publishedAt'][:10]}")

    elif source == "arXiv Papers":
        papers = fetch_arxiv(query)
        for paper in papers:
            with st.expander(f"📄 {paper.title}"):
                st.write(paper.summary)
                st.markdown(f"[arXiv 링크]({paper.link})")
                st.caption(", ".join([a.name for a in paper.authors]))
