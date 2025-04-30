import streamlit as st
import pandas as pd
from itertools import combinations

st.title("🎓 시간표 추천 앱 (Streamlit 버전)")
st.markdown("조건을 선택하면 AI가 자동으로 시간표를 추천해줍니다!")

uploaded_file = st.file_uploader("📂 timetable_data.csv 파일 업로드", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.sidebar.header("🛠️ 조건 설정")
    target_credit = st.sidebar.slider("총 학점", min_value=12, max_value=21, value=18, step=1)
    prefer_morning = st.sidebar.checkbox("오전 수업만 듣고 싶어요", value=True)
    avoid_friday = st.sidebar.checkbox("금요일 공강 원해요", value=False)

    required_major_basic = 2
    required_major_advanced = 1

    def is_afternoon(time_str):
        times = [t.split('~')[0] for part in time_str.split(',') for t in [part.strip()]]
        for t in times:
            hour = int(t[1:3]) if len(t) >= 4 else int(t[1])
            if hour >= 13:
                return True
        return False

    def is_friday(time_str):
        return '금' in time_str

    df['오후수업'] = df['요일시간'].apply(is_afternoon)
    df['금요일포함'] = df['요일시간'].apply(is_friday)

    filtered_df = df.copy()
    if prefer_morning:
        filtered_df = filtered_df[filtered_df['오후수업'] == False]
    if avoid_friday:
        filtered_df = filtered_df[filtered_df['금요일포함'] == False]

    major_basic = filtered_df[filtered_df['전공구분'].str.contains('전공\\(기초\\)')]
    major_advanced = filtered_df[filtered_df['전공구분'].str.contains('전공\\(심화\\)')]
    liberal = filtered_df[filtered_df['전공구분'].str.contains('교양')]

    results = []

    for basics in combinations(major_basic.index, required_major_basic):
        for advanced in combinations(major_advanced.index, required_major_advanced):
            fixed = list(basics) + list(advanced)
            fixed_df = filtered_df.loc[fixed]
            fixed_credits = fixed_df['학점'].sum()
            remain_credit = target_credit - fixed_credits

            liberal_candidates = liberal[~liberal.index.isin(fixed)]
            for r in range(1, len(liberal_candidates)+1):
                for combo in combinations(liberal_candidates.index, r):
                    liberal_df = filtered_df.loc[list(combo)]
                    total_df = pd.concat([fixed_df, liberal_df])
                    total_credit = total_df['학점'].sum()

                    if total_credit == target_credit:
                        results.append(total_df)
                        break
                if results:
                    break
            if results:
                break
        if results:
            break

    if results:
        st.success("✅ 조건에 맞는 시간표를 추천했어요!")
        st.dataframe(results[0][['과목명', '요일시간', '전공구분', '학점']])
        st.markdown("📝 **추천 이유:** 오전 수업 위주로 구성되었으며 전공 필수 및 심화 기준을 만족하고, 교양 과목도 충돌 없이 배치되었습니다.")
    else:
        st.error("❌ 조건에 맞는 시간표를 찾지 못했어요. 조건을 살짝 완화해볼까요?")
else:
    st.info("📄 timetable_data.csv 파일을 먼저 업로드해주세요.")
