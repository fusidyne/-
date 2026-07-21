"""
더마 카테고리 검색 트렌드 대시보드 (네이버 데이터랩 API)
──────────────────────────────────────────────
키워드를 입력하면 최근 검색 관심도 추이를 실시간으로 조회합니다.
"""

import streamlit as st
import requests
import pandas as pd
import altair as alt
from datetime import date, timedelta

st.set_page_config(page_title="더마 카테고리 검색 트렌드", page_icon="🔍", layout="wide")

def get_secret(key):
    """secrets.toml이 없어도 에러 없이 빈 문자열을 반환"""
    try:
        return st.secrets.get(key, "")
    except Exception:
        return ""

# ── 사이드바: API 인증 ────────────────────────────────
st.sidebar.title("🔑 네이버 API 설정")
client_id = st.sidebar.text_input(
    "Client ID",
    value=get_secret("NAVER_CLIENT_ID"),
    type="default",
)
client_secret = st.sidebar.text_input(
    "Client Secret",
    value=get_secret("NAVER_CLIENT_SECRET"),
    type="password",
)
st.sidebar.caption("발급: developers.naver.com → 애플리케이션 등록 → 데이터랩(검색어 트렌드) 사용 설정")

st.sidebar.markdown("---")
st.sidebar.title("⚙️ 조회 조건")

today = date.today()
default_start = today - timedelta(days=90)
start_date = st.sidebar.date_input("시작일", value=default_start)
end_date = st.sidebar.date_input("종료일", value=today)
time_unit = st.sidebar.radio("집계 단위", ["date", "week", "month"], index=1, horizontal=True)

device = st.sidebar.selectbox("디바이스", ["전체", "PC", "모바일"], index=0)
device_map = {"전체": "", "PC": "pc", "모바일": "mo"}

gender = st.sidebar.selectbox("성별", ["전체", "여성", "남성"], index=0)
gender_map = {"전체": "", "여성": "f", "남성": "m"}

ages = st.sidebar.multiselect(
    "연령대 (선택 안 하면 전체)",
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"],
    format_func=lambda x: {
        "1": "0~12세", "2": "13~18세", "3": "19~24세", "4": "25~29세", "5": "30~34세",
        "6": "35~39세", "7": "40~44세", "8": "45~49세", "9": "50~54세", "10": "55~60세", "11": "60세 이상",
    }[x],
)

# ── 메인: 키워드 그룹 입력 ────────────────────────────────
st.title("🧴 더마 카테고리 검색 트렌드 대시보드")
st.caption("키워드를 입력하면 네이버 데이터랩 API로 실시간 검색 관심도 추이를 가져옵니다. (상대값, 100 기준 지수)")

st.markdown("**비교하고 싶은 키워드 그룹을 입력하세요** (최대 5개 그룹, 그룹당 콤마로 여러 키워드 묶음 가능)")

cols = st.columns(5)
default_examples = ["시카크림", "판테놀크림", "마데카소사이드", "트러블크림", ""]
group_inputs = []
for i, col in enumerate(cols):
    with col:
        val = st.text_input(f"그룹 {i+1}", value=default_examples[i], key=f"grp_{i}")
        group_inputs.append(val.strip())

run = st.button("🔍 트렌드 조회", type="primary", use_container_width=True)

# ── API 호출 함수 ────────────────────────────────
def call_datalab(client_id, client_secret, start_date, end_date, time_unit,
                  keyword_groups, device="", gender="", ages=None):
    url = "https://openapi.naver.com/v1/datalab/search"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
        "Content-Type": "application/json",
    }
    body = {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "timeUnit": time_unit,
        "keywordGroups": [
            {"groupName": name, "keywords": [k.strip() for k in name.split(",")]}
            for name in keyword_groups if name
        ],
    }
    if device:
        body["device"] = device
    if gender:
        body["gender"] = gender
    if ages:
        body["ages"] = ages

    resp = requests.post(url, headers=headers, json=body, timeout=10)
    if resp.status_code != 200:
        raise RuntimeError(f"API 오류 ({resp.status_code}): {resp.text}")
    return resp.json()


# ── 실행 ────────────────────────────────
if run:
    if not client_id or not client_secret:
        st.error("사이드바에 Client ID / Client Secret을 먼저 입력해주세요.")
    elif not any(group_inputs):
        st.error("키워드를 하나 이상 입력해주세요.")
    else:
        try:
            with st.spinner("네이버 데이터랩에서 데이터를 가져오는 중..."):
                data = call_datalab(
                    client_id, client_secret, start_date, end_date, time_unit,
                    group_inputs, device_map[device], gender_map[gender], ages or None,
                )

            rows = []
            for result in data["results"]:
                for point in result["data"]:
                    rows.append({"날짜": point["period"], "그룹": result["title"], "지수": point["ratio"]})
            df = pd.DataFrame(rows)
            df["날짜"] = pd.to_datetime(df["날짜"])

            latest_period = df["날짜"].max()
            k1, k2, k3 = st.columns(3)
            with k1:
                st.metric("조회 기간", f"{start_date} ~ {end_date}")
            with k2:
                top_group = df[df["날짜"] == latest_period].sort_values("지수", ascending=False).iloc[0]
                st.metric("최신 시점 관심도 1위", top_group["그룹"], f"{top_group['지수']:.1f}")
            with k3:
                trend_scores = {}
                for g in df["그룹"].unique():
                    sub = df[df["그룹"] == g].sort_values("날짜")
                    if len(sub) >= 2:
                        trend_scores[g] = sub["지수"].iloc[-1] - sub["지수"].iloc[-2]
                if trend_scores:
                    rising = max(trend_scores, key=trend_scores.get)
                    st.metric("최근 상승세 1위", rising, f"+{trend_scores[rising]:.1f}")

            st.subheader("검색 관심도 추이")
            chart = (
                alt.Chart(df)
                .mark_line(point=True)
                .encode(
                    x=alt.X("날짜:T", title=None),
                    y=alt.Y("지수:Q", title="상대 검색 지수 (100 기준)"),
                    color=alt.Color("그룹:N", title="키워드 그룹"),
                    tooltip=["날짜:T", "그룹:N", "지수:Q"],
                )
                .properties(height=420)
                .interactive()
            )
            st.altair_chart(chart, use_container_width=True)

            with st.expander("원본 데이터 보기"):
                pivot = df.pivot(index="날짜", columns="그룹", values="지수")
                st.dataframe(pivot, use_container_width=True)

            st.subheader("자동 인사이트")
            avg_by_group = df.groupby("그룹")["지수"].mean().sort_values(ascending=False)
            st.markdown(f"- 조회 기간 평균 관심도가 가장 높은 키워드는 **{avg_by_group.index[0]}** 입니다.")
            if trend_scores:
                st.markdown(f"- 가장 최근 구간 대비 상승폭이 큰 키워드는 **{rising}** (+{trend_scores[rising]:.1f}) 입니다. 신제품·프로모션 타이밍 검토에 참고하세요.")
            st.caption("※ 지수는 절대 검색량이 아닌 조회 기간 내 상대값(최댓값=100)입니다. 여러 기간을 비교할 때는 기간을 동일하게 맞춰 조회하세요.")

        except Exception as e:
            st.error(f"조회 중 오류가 발생했어요: {e}")
else:
    st.info("왼쪽에 API 키를 입력하고, 키워드 그룹을 채운 뒤 '트렌드 조회'를 눌러주세요.")
    st.caption("예시: 시카크림 / 판테놀크림 / 마데카소사이드 / 트러블크림 처럼 성분·제품군 키워드로 비교하면 좋아요.")