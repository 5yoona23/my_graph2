import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.write("영화의 일별 관객 변화를 시간의 흐름에 따라 살펴봅니다.")

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜 열을 진짜 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d"
    )

    # 숫자형 열 변환
    numeric_columns = ["순위", "일관객", "누적관객", "스크린수", "상영횟수"]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_data()

# --------------------------------------------------
# 그래프 1
# --------------------------------------------------
st.divider()
st.header("📈 그래프 1. 영화별 일관객 변화")

st.write("영화를 하나 선택하면 해당 영화의 날짜별 일관객 변화를 볼 수 있습니다.")

# 영화 목록
movie_list = sorted(df["영화명"].dropna().unique())

selected_movie = st.selectbox(
    "🎬 영화를 선택하세요",
    movie_list
)

# 선택한 영화만 추출
movie_df = df[df["영화명"] == selected_movie].copy()

# 날짜순 정렬
movie_df = movie_df.sort_values("날짜")

# 그래프용 데이터
chart_df = movie_df[["날짜", "일관객"]].copy()

# Plotly 선 그래프
fig = px.line(
    chart_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"「{selected_movie}」 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수"
    }
)

# 마우스를 올렸을 때 날짜 + 관객수 표시
fig.update_traces(
    hovertemplate=
        "날짜: %{x|%Y-%m-%d}<br>"
        "일관객: %{y:,}명"
        "<extra></extra>"
)

fig.update_layout(
    hovermode="x unified",
    height=500
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# 사용자가 직접 작성할 자리
st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="예: 이 영화는 개봉 초기에 관객이 가장 많고 이후 점차 감소하는 모습을 보인다.",
    height=100,
    key="graph1_note"
)

# --------------------------------------------------
# 그래프 2
# --------------------------------------------------
st.divider()
st.header("📊 그래프 2. 일관객 합계 TOP 5 영화의 날짜별 변화")

st.write(
    "이 기간 동안 일관객 합계가 가장 큰 5편의 날짜별 일관객 변화를 비교합니다."
)

# 영화별 일관객 합계 계산
top5_movies = (
    df.groupby("영화명")["일관객"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

# 상위 5편 데이터만 추출
top5_df = df[df["영화명"].isin(top5_movies)].copy()

# 날짜순 정렬
top5_df = top5_df.sort_values(["날짜", "영화명"])

# Plotly 선 그래프
fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 TOP 5 영화의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
        "영화명": "영화"
    }
)

# 마우스를 올렸을 때 날짜와 관객수 표시
fig2.update_traces(
    hovertemplate=
        "날짜: %{x|%Y-%m-%d}<br>"
        "일관객: %{y:,}명"
        "<extra>%{fullData.name}</extra>"
)

fig2.update_layout(
    hovermode="x unified",
    height=550,
    legend_title_text="영화"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# 사용자가 직접 작성할 자리
st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="이 그래프에서 알 수 있는 내용을 작성하세요.",
    height=100,
    key="graph2_note"
)

# --------------------------------------------------
# 그래프 3
# 앞으로 추가할 그래프 영역
# --------------------------------------------------
st.divider()
st.header("📊 그래프 3")

st.info("여기에 다음 그래프를 추가하면 됩니다.")

st.markdown("### 💡 이 그래프로 알 수 있는 것")
st.text_area(
    "내용을 직접 작성하세요.",
    placeholder="이 그래프에서 알 수 있는 내용을 작성하세요.",
    height=100,
    key="graph3_note"
)
