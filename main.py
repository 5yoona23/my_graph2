# ==================================================
# 그래프 5
# ==================================================

# --------------------------------------------------
# 34. 장르별 총 관객수 박스플롯
# --------------------------------------------------
st.subheader("📦 장르별 총 관객수 분포")

st.write(
    "영화가 10편 이상인 장르만 골라 "
    "장르별 총 관객수의 분포를 비교합니다."
)


# --------------------------------------------------
# 35. 박스플롯에 필요한 데이터 확인
# --------------------------------------------------
if "genreNm" in df.columns and "total_audi" in df.columns:

    box_df = df[
        [
            "movieNm",
            "genreNm",
            "total_audi"
        ]
    ].copy()


    # 총 관객수를 숫자로 변환
    box_df["total_audi"] = pd.to_numeric(
        box_df["total_audi"],
        errors="coerce"
    )


    # 장르가 없는 영화는 '장르 미상'으로 표시
    box_df["genreNm"] = (
        box_df["genreNm"]
        .fillna("장르 미상")
    )


    # 총 관객수가 없는 행은 제외
    box_df = box_df.dropna(
        subset=["total_audi"]
    )


    # --------------------------------------------------
    # 36. 영화가 10편 이상인 장르 찾기
    # --------------------------------------------------
    genre_counts = (
        box_df["genreNm"]
        .value_counts()
    )


    valid_genres = genre_counts[
        genre_counts >= 10
    ].index


    # 조건을 만족하는 장르만 남기기
    box_df = box_df[
        box_df["genreNm"].isin(valid_genres)
    ].copy()


    # --------------------------------------------------
    # 37. 데이터가 없는 경우
    # --------------------------------------------------
    if box_df.empty:

        st.info(
            "영화가 10편 이상인 장르가 없습니다."
        )

    else:

        # --------------------------------------------------
        # 38. 박스플롯 만들기
        # --------------------------------------------------
        fig_box = px.box(
            box_df,
            x="genreNm",
            y="total_audi",

            # 각 영화의 이름을 hover에서 사용
            hover_name="movieNm",

            # hover에 총 관객수와 장르 표시
            hover_data={
                "genreNm": True,
                "total_audi": ":,"
            },

            points="outliers",

            labels={
                "genreNm": "장르",
                "total_audi": "총 관객수"
            }
        )


        # --------------------------------------------------
        # 39. 이상치(outlier)에 영화명 표시
        # --------------------------------------------------
        # 박스플롯에서 points="outliers"로 설정하면
        # 상자 밖의 점만 표시됩니다.
        fig_box.update_traces(
            hovertemplate=(
                "<b>%{hovertext}</b><br>"
                "장르: %{x}<br>"
                "총 관객: %{y:,}명"
                "<extra></extra>"
            )
        )


        fig_box.update_layout(
            xaxis_title="장르",
            yaxis_title="총 관객수",
            showlegend=False
        )


        # --------------------------------------------------
        # 40. 그래프 출력
        # --------------------------------------------------
        st.plotly_chart(
            fig_box,
            use_container_width=True
        )


else:

    st.info(
        "현재 데이터에 장르 정보 또는 total_audi가 없어 "
        "박스플롯을 그릴 수 없습니다."
    )
