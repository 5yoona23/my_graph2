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

# KOBIS API용 날짜 형식
target_date = selected_date.strftime("%Y%m%d")

# 화면에 표시할 날짜
display_date = selected_date.strftime("%Y년 %m월 %d일")


# --------------------------------------------------
# 4. KOBIS 인증키 가져오기
# --------------------------------------------------
# Streamlit Cloud의 Secrets에 다음과 같이 저장합니다.
#
# KOBIS_KEY = "발급받은_인증키"
#
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
# 같은 날짜의 데이터는 1시간 동안 캐시합니다.
# 따라서 같은 날짜를 다시 선택해도 API를 반복해서 호출하지 않습니다.
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
# 인증키가 잘못되어도 HTTP 상태코드가 200일 수 있으므로
# faultInfo가 있는지 확인합니다.
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


# 순위순으로 정렬
df = df.sort_values(
    "rank"
).reset_index(drop=True)


# --------------------------------------------------
# 13. 날짜 표시
# --------------------------------------------------
st.subheader(f"📅 {display_date}")

st.caption(
    f"KOBIS 조회 날짜: {target_date}"
)


# --------------------------------------------------
# 14. 1위 영화
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
# 15. 1위 영화 지표 카드
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
        f"{first


# ── 그래프 2. 장르 안의 영화 (트리맵) ──
st.header("2. 장르 안의 영화 (트리맵)")
fig2 = px.treemap(df, path=["장르", "movieNm"], values="total_audi",
                  hover_data=["total_audi"])
st.plotly_chart(fig2, width="stretch")
st.caption("이 그래프로 알 수 있는 것: (한 문장으로 적어 보세요)")
