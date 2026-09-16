import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# --------------------------------------------------
# 1. 기본 화면 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 박스오피스",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 박스오피스")
st.write("달력에서 날짜를 골라 그날의 박스오피스를 확인해 보세요.")


# --------------------------------------------------
# 2. 한국 시간 기준 날짜 계산
# --------------------------------------------------
# 배포 서버의 시간이 한국 시간이 아닐 수 있으므로
# 한국 시간(Asia/Seoul)을 기준으로 오늘 날짜를 계산합니다.
kst_now = datetime.now(ZoneInfo("Asia/Seoul"))
today_kst = kst_now.date()

# 오늘은 아직 집계 전이므로 어제까지만 선택할 수 있습니다.
yesterday_kst = today_kst - timedelta(days=1)


# --------------------------------------------------
# 3. 날짜 선택
# --------------------------------------------------
selected_date = st.date_input(
    "📅 조회할 날짜",
    value=yesterday_kst,
    max_value=yesterday_kst,
    help="오늘은 아직 집계 전이므로 어제까지만 선택할 수 있습니다."
)

# KOBIS API가 요구하는 날짜 형식
target_date = selected_date.strftime("%Y%m%d")

# 화면에 보여 줄 날짜
display_date = selected_date.strftime("%Y년 %m월 %d일")


# --------------------------------------------------
# 4. Secrets에서 KOBIS 인증키 가져오기
# --------------------------------------------------
# Streamlit Cloud의 Secrets에
#
# KOBIS_KEY = "발급받은_인증키"
#
# 를 저장해 둡니다.
try:
    kobis_key = st.secrets["KOBIS_KEY"]

except Exception:
    st.error("🔑 KOBIS 인증키를 찾을 수 없습니다.")

    st.info(
        "Streamlit Cloud의 앱 설정에서 Secrets를 열고 "
        "KOBIS_KEY가 등록되어 있는지 확인하세요."
    )

    st.stop()


# --------------------------------------------------
# 5. KOBIS API 호출 함수
# --------------------------------------------------
# 같은 날짜의 결과는 1시간 동안 캐시합니다.
@st.cache_data(ttl=3600)
def get_boxoffice_data(target_dt, api_key):

    url = (
        "https://www.kobis.or.kr/kobisopenapi/webservice/rest/"
        "boxoffice/searchDailyBoxOfficeList.json"
    )

    params = {
        "key": api_key,
        "targetDt": target_dt
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        return {
            "success": True,
            "data": data,
            "error": None
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "data": None,
            "error": "API 요청 시간이 초과되었습니다."
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "data": None,
            "error": f"API 요청 중 문제가 발생했습니다.\n{e}"
        }

    except ValueError:
        return {
            "success": False,
            "data": None,
            "error": "API가 올바른 JSON 데이터를 보내지 않았습니다."
        }


# --------------------------------------------------
# 6. 선택한 날짜의 데이터 가져오기
# --------------------------------------------------
result = get_boxoffice_data(
    target_date,
    kobis_key
)


# --------------------------------------------------
# 7. API 요청 실패 확인
# --------------------------------------------------
if not result["success"]:

    st.error("❌ 박스오피스 데이터를 가져오지 못했습니다.")

    st.info(
        "다음 사항을 확인해 주세요.\n\n"
        "• 인터넷 연결 상태\n"
        "• KOBIS API 서버 상태\n"
        "• KOBIS_KEY가 정확하게 등록되어 있는지\n"
        "• 잠시 후 다시 접속해 보기"
    )

    st.stop()


data = result["data"]


# --------------------------------------------------
# 8. KOBIS faultInfo 확인
# --------------------------------------------------
# 인증키가 틀려도 HTTP 상태코드는 200일 수 있습니다.
# 그래서 faultInfo가 있는지를 별도로 확인합니다.
if "faultInfo" in data:

    fault_info = data["faultInfo"]

    error_code = fault_info.get(
        "errorCode",
        "알 수 없음"
    )

    error_message = fault_info.get(
        "message",
        "KOBIS API에서 오류가 발생했습니다."
    )

    st.error("❌ KOBIS API 오류")

    st.warning(
        f"오류 코드: {error_code}\n\n"
        f"오류 내용: {error_message}"
    )

    st.info(
        "다음 사항을 확인해 주세요.\n\n"
        "• Streamlit Secrets의 KOBIS_KEY가 정확한지\n"
        "• 인증키에 불필요한 공백이 없는지\n"
        "• KOBIS Open API에서 인증키가 정상적으로 발급되었는지"
    )

    st.stop()


# --------------------------------------------------
# 9. 박스오피스 결과 확인
# --------------------------------------------------
boxoffice_result = data.get("boxOfficeResult")

if not boxoffice_result:

    st.error("❌ 박스오피스 결과를 찾을 수 없습니다.")

    st.info(
        "KOBIS API의 응답이 정상인지 확인하거나 "
        "잠시 후 다시 시도해 주세요."
    )

    st.stop()


# 영화 목록 가져오기
movie_list = boxoffice_result.get(
    "dailyBoxOfficeList",
    []
)


# --------------------------------------------------
# 10. 영화 목록이 비어 있는 경우
# --------------------------------------------------
if not movie_list:

    st.warning("📭 그날은 아직 집계 전입니다.")

    st.info(
        f"선택한 날짜: {display_date}\n\n"
        "KOBIS에서 해당 날짜의 일별 박스오피스 "
        "데이터가 아직 제공되지 않는 것일 수 있습니다."
    )

    st.stop()


# --------------------------------------------------
# 11. DataFrame으로 변환
# --------------------------------------------------
df = pd.DataFrame(movie_list)


# --------------------------------------------------
# 12. 숫자 데이터 숫자형으로 변환
# --------------------------------------------------
# KOBIS API에서는 숫자도 문자열로 전달됩니다.
number_columns = [
    "rank",
    "rankInten",
    "audiCnt",
    "audiAcc",
    "scrnCnt",
    "showCnt"
]

for column in number_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0)


# 순위 기준으로 정렬
df = df.sort_values(
    "rank"
).reset_index(drop=True)


# --------------------------------------------------
# 13. total_audi 만들기
# --------------------------------------------------
# KOBIS 일별 박스오피스에서는 누적 관객수가 audiAcc입니다.
# 여기서는 이것을 total_audi라는 이름으로 사용합니다.
df["total_audi"] = df["audiAcc"]


# --------------------------------------------------
# 14. 날짜 표시
# --------------------------------------------------
st.subheader(f"📅 {display_date}")

st.caption(
    f"KOBIS 조회 날짜: {target_date}"
)


# ==================================================
# 그래프 1
# ==================================================

# --------------------------------------------------
# 15. 1위 영화
# --------------------------------------------------
first_movie = df.iloc[0]

first_movie_name = first_movie["movieNm"]

first_audience = int(
    first_movie["audiCnt"]
)

first_audience_acc = int(
    first_movie["audiAcc"]
)

first_screen = int(
    first_movie["scrnCnt"]
)


# --------------------------------------------------
# 16. 1위 영화 지표 카드
# --------------------------------------------------
st.subheader(
    f"🥇 1위: {first_movie_name}"
)

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "관객수",
        f"{first_audience:,}명"
    )

with col2:

    st.metric(
        "누적 관객수",
        f"{first_audience_acc:,}명"
    )

with col3:

    st.metric(
        "스크린수",
        f"{first_screen:,}개"
    )


# --------------------------------------------------
# 17. 관객수 상위 5편 막대그래프
# --------------------------------------------------
st.subheader("📊 관객수 상위 5편")

top5 = (
    df.sort_values(
        "audiCnt",
        ascending=False
    )
    .head(5)
    .copy()
)

chart_data = top5.set_index(
    "movieNm"
)[["audiCnt"]]

st.bar_chart(
    chart_data,
    x_label="영화",
    y_label="관객수"
)


# ==================================================
# 그래프 2
# ==================================================

# --------------------------------------------------
# 18. 장르별 영화 트리맵
# --------------------------------------------------
# 주의:
# KOBIS 일별 박스오피스 API에는 장르 정보가 없으므로
# 이 부분은 장르 데이터가 별도로 들어온 경우에 사용할 수 있습니다.
#
# 현재 API 결과에 genreNm이 있다면 트리맵을 만들고,
# 없다면 안내 문구를 보여 줍니다.
if "genreNm" in df.columns:

    st.subheader("🌳 장르별 영화 관객 트리맵")

    treemap_df = df[
        ["genreNm", "movieNm", "total_audi"]
    ].copy()

    treemap_df["genreNm"] = (
        treemap_df["genreNm"]
        .fillna("장르 미상")
    )

    fig_treemap = px.treemap(
        treemap_df,
        path=["genreNm", "movieNm"],
        values="total_audi",
        hover_data={
            "genreNm": False,
            "movieNm": True,
            "total_audi": ":,"
        }
    )

    fig_treemap.update_traces(
        hovertemplate=(
            "영화명: %{label}<br>"
            "총 관객: %{value:,}명"
            "<extra></extra>"
        )
    )

    st.plotly_chart(
        fig_treemap,
        use_container_width=True
    )

else:

    st.subheader("🌳 장르별 영화 트리맵")

    st.info(
        "현재 사용 중인 KOBIS 일별 박스오피스 API 응답에는 "
        "장르 정보가 포함되어 있지 않아 트리맵을 그릴 수 없습니다."
    )

    st.caption(
        "장르별 트리맵을 만들려면 영화별 장르 정보가 필요합니다."
    )


# ==================================================
# 그래프 3
# ==================================================

# --------------------------------------------------
# 19. total_audi 히스토그램
# --------------------------------------------------
st.subheader("📈 총 관객수 분포")

st.write(
    "영화별 총 관객수가 어느 구간에 많이 모여 있는지 "
    "히스토그램으로 확인합니다."
)


# total_audi가 숫자인 영화만 사용
hist_df = df[
    ["movieNm", "total_audi"]
].copy()

hist_df = hist_df[
    hist_df["total_audi"] >= 0
]


# --------------------------------------------------
# 20. 히스토그램 구간 설정
# --------------------------------------------------
# 관객수의 범위를 보고 자동으로 구간을 나눕니다.
if len(hist_df) > 0:

    min_audi = hist_df["total_audi"].min()
    max_audi = hist_df["total_audi"].max()

    # 모든 영화의 total_audi가 같은 경우
    if min_audi == max_audi:

        bins = 1

    else:

        # 최대 10개 정도의 구간으로 나눕니다.
        bins = min(10, len(hist_df))


    # Plotly로 히스토그램 생성
    fig_hist = px.histogram(
        hist_df,
        x="total_audi",
        nbins=bins,
        labels={
            "total_audi": "총 관객수",
            "count": "영화 수"
        }
    )

    fig_hist.update_traces(
        hovertemplate=(
            "총 관객수 구간: %{x}<br>"
            "영화 수: %{y}편"
            "<extra></extra>"
        )
    )

    fig_hist.update_layout(
        xaxis_title="총 관객수",
        yaxis_title="영화 수"
    )

    st.plotly_chart(
        fig_hist,
        use_container_width=True
    )


    # --------------------------------------------------
    # 21. 가장 많이 몰려 있는 구간 계산
    # --------------------------------------------------
    counts, bin_edges = pd.cut(
        hist_df["total_audi"],
        bins=bins,
        include_lowest=True,
        retbins=True
    )

    bin_counts = (
        counts
        .value_counts()
        .sort_index()
    )

    # 영화가 가장 많이 들어 있는 구간
    most_common_bin = bin_counts.idxmax()

    lower = most_common_bin.left
    upper = most_common_bin.right


    # --------------------------------------------------
    # 22. 총 관객이 가장 많은 영화 찾기
    # --------------------------------------------------
    most_audience_movie = hist_df.loc[
        hist_df["total_audi"].idxmax()
    ]

    most_audience_movie_name = (
        most_audience_movie["movieNm"]
    )

    most_audience = int(
        most_audience_movie["total_audi"]
    )


    # --------------------------------------------------
    # 23. 그래프 아래 설명 문구
    # --------------------------------------------------
    st.markdown(
        f"""
        **📌 히스토그램 해석**

        - 대부분의 영화는 **{lower:,.0f}명 ~ {upper:,.0f}명**
          구간에 몰려 있습니다.
        - 총 관객이 가장 많은 영화는
          **{most_audience_movie_name}**이며,
          총 관객은 **{most_audience:,}명**입니다.
        """
    )


# ==================================================
# 영화 목록 표
# ==================================================

# --------------------------------------------------
# 24. 표에 표시할 데이터 만들기
# --------------------------------------------------
st.subheader("🎥 일별 박스오피스 10위권")

table_df = df[
    [
        "rank",
        "rankInten",
        "movieNm",
        "openDt",
        "audiCnt",
        "audiAcc",
        "scrnCnt"
    ]
].copy()


# --------------------------------------------------
# 25. 순위 증감 화살표
# --------------------------------------------------
def make_rank_change(value):

    value = int(value)

    # 양수 = 순위 상승
    if value > 0:

        return (
            '<span style="color:red; font-weight:bold;">'
            f'▲ {value}'
            '</span>'
        )

    # 음수 = 순위 하락
    elif value < 0:

        return (
            '<span style="color:blue; font-weight:bold;">'
            f'▼ {abs(value)}'
            '</span>'
        )

    # 변화 없음
    else:

        return "–"


table_df["순위 변동"] = table_df[
    "rankInten"
].apply(make_rank_change)


# --------------------------------------------------
# 26. 100만 관객 트로피
# --------------------------------------------------
def make_movie_name(row):

    movie_name = row["movieNm"]

    accumulated = int(
        row["audiAcc"]
    )

    if accumulated > 1_000_000:

        return f"{movie_name} 🏆"

    return movie_name


table_df["영화명"] = table_df.apply(
    make_movie_name,
    axis=1
)


# --------------------------------------------------
# 27. 표 열 정리
# --------------------------------------------------
table_df = table_df[
    [
        "rank",
        "순위 변동",
        "영화명",
        "openDt",
        "audiCnt",
        "audiAcc",
        "scrnCnt"
    ]
].copy()


table_df.columns = [
    "순위",
    "전날 대비",
    "영화명",
    "개봉일",
    "관객수",
    "누적관객",
    "스크린수"
]


# --------------------------------------------------
# 28. 숫자에 천 단위 쉼표
# --------------------------------------------------
for column in [
    "순위",
    "관객수",
    "누적관객",
    "스크린수"
]:

    table_df[column] = table_df[column].map(
        lambda x: f"{int(x):,}"
    )


# --------------------------------------------------
# 29. HTML 표 표시
# --------------------------------------------------
html_table = table_df.to_html(
    index=False,
    escape=False
)

st.markdown(
    html_table,
    unsafe_allow_html=True
)


# --------------------------------------------------
# 30. 안내 문구
# --------------------------------------------------
st.caption(
    "🔺 빨간 위 화살표: 전날보다 순위 상승  |  "
    "🔻 파란 아래 화살표: 전날보다 순위 하락"
)

st.caption(
    "🏆 누적관객 100만 명 초과 영화"
)

st.caption(
    "※ 데이터 출처: 영화진흥위원회(KOBIS) "
    "일별 박스오피스 Open API"
)
