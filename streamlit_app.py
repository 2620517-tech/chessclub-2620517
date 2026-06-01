import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 페이지 설정
st.set_page_config(page_title="전국 체스클럽 지도", layout="wide", page_icon="♟️")

st.title("♟️ 전국 실제 체스클럽 및 교육센터 지도")
st.markdown("유명 체스클럽부터 각 지역의 체스 교육 거점까지, 전국 곳곳의 체스 공간을 확인해 보세요!")

# 2. 전국 실제/주요 체스 공간 데이터 (좌표 포함)
@st.cache_data
def load_chess_club_data():
    data = {
        "클럽명": [
            "슥슥이 체스클럽", 
            "체스프릭 클럽 (체스프릭 EPA)", 
            "마에스트로 체스클럽",
            "아이체스 (I-Chess)", 
            "인천 마스터 체스학원",
            "대전 체스 연합 (유성 거점)",
            "대구 브레인 체스 아카데미",
            "광주 체스클럽 & 보드룸",
            "울산 체스 교육센터",
            "제주 체스 아일랜드 클럽"
        ],
        "지역": ["경기 고양", "경기 성남", "서울 서초", "서울 강남", "인천", "대전", "대구", "광주", "울산", "제주"],
        "주소": [
            "경기 고양시 덕양구 서정마을1로 20-10 201호",
            "경기 성남시 수정구 위례동로 135 신성위례캐슬타워 9층",
            "서울특별시 서초구 효령로 321",
            "서울특별시 강남구 역삼로 140",
            "인천광역시 연수구 송도동 23-4",
            "대전광역시 유성구 대학로 99",
            "대구광역시 수성구 달구벌대로 2513",
            "광주광역시 서구 상무중앙로 48",
            "울산광역시 남구 문수로 431",
            "제주특별자치도 제주시 노형로 350"
        ],
        # 전국 각 주요 위치의 위도, 경도 좌표
        "Latitude": [37.6258, 37.4725, 37.4871, 37.4951, 37.3925, 36.3621, 35.8589, 35.1478, 35.5342, 33.4851],
        "Longitude": [126.8443, 127.1428, 127.0253, 127.0378, 126.6534, 127.3563, 128.6368, 126.8475, 129.3021, 126.4712],
        "특징": [
            "인기 체스 유튜버 '슥슥이'님이 운영하는 고양시 핫플레이스 클럽",
            "국가대표 CM 김창훈 선수가 운영하는 위례 체스아카데미 및 정기 모임 공간",
            "대한체스연맹 공식 대회 및 오프라인 모임이 자주 열리는 전통의 클럽",
            "어린이 및 성인 체스 전문 교육과 대국이 이루어지는 공간",
            "송도 국제도시 중심의 주니어 체스 선수 육성 및 취미반 학원",
            "카이스트 및 대학가 인근 체스 동호인들과 주니어들이 모이는 대전 거점",
            "대구 수성구의 대표적인 체스 전문 학원이자 영남권 체스 대국 공간",
            "호남 지역 체스 유저들의 소통 공간이자 주니어 체스 교육 교실",
            "울산 지역 체스 저변 확대를 위한 성인/아동 체스 아카데미",
            "제주 지역 체스 마니아들과 주니어 교육을 위한 특별 공간"
        ]
    }
    return pd.DataFrame(data)

df = load_chess_club_data()

# 3. 사이드바 - 검색 및 광역 필터 기능
st.sidebar.header("🔍 체스클럽 검색")

# '지역'에서 광역 단위(서울, 경기, 인천 등)만 추출해서 필터링하기 편하게 가공
def get_broad_region(region_str):
    return region_str.split()[0]

df['광역지역'] = df['지역'].apply(get_broad_region)
broad_regions = ["전체"] + sorted(list(df["광역지역"].unique()))

selected_region = st.sidebar.selectbox("지역(시/도) 선택", broad_regions)
search_keyword = st.sidebar.text_input("클럽명 검색", "")

# 데이터 필터링
filtered_df = df.copy()
if selected_region != "전체":
    filtered_df = filtered_df[filtered_df["광역지역"] == selected_region]
if search_keyword:
    filtered_df = filtered_df[filtered_df["클럽명"].str.contains(search_keyword, case=False)]

# 4. 화면 레이아웃 (좌측 지도 / 우측 목록)
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ 전국 체스맵")
    
    # 지도 중심점 및 줌 레벨 계산 (전체일 때는 대한민국 중심, 특정 지역일 때는 해당 지역 중심)
    if not filtered_df.empty and selected_region != "전체":
        center_lat = filtered_df["Latitude"].mean()
        center_lon = filtered_df["Longitude"].mean()
        zoom_level = 11
    else:
        # 전국을 한눈에 보여줄 수 있는 중심 좌표
        center_lat, center_lon, zoom_level = 36.0, 127.8, 7

    # Folium 지도 객체 생성
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level, control_scale=True)

    # 마커 컬러 및 아이콘 지정
    for idx, row in filtered_df.iterrows():
        if "슥슥이" in row["클럽명"]:
            icon_color, icon_type = "red", "star"
        elif "체스프릭" in row["클럽명"]:
            icon_color, icon_type = "darkpurple", "star"
        elif "마에스트로" in row["클럽명"]:
            icon_color, icon_type = "orange", "bookmark"
        else:
            icon_color, icon_type = "blue", "info-sign"

        popup_html = f"""
        <div style='font-family: Arial, sans-serif; width: 240px;'>
            <h4 style='margin: 0 0 8px 0; color: #2C3E50; font-size: 14px;'>{row['클럽명']}</h4>
            <p style='font-size: 11px; margin: 4px 0;'><b>📍 주소:</b> {row['주소']}</p>
            <p style='font-size: 11px; color: #555; margin: 4px 0; line-height: 1.4;'>💡 {row['특징']}</p>
        </div>
        """
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row["클럽명"],
            icon=folium.Icon(color=icon_color, icon=icon_type)
        ).add_to(m)

    # Streamlit에 지도 렌더링
    st_folium(m, width="100%", height=600, returned_objects=[])

with col2:
    st.subheader("📋 클럽 상세 리스트")
    st.write(f"검색 결과: 총 **{len(filtered_df)}**개 공간")
    
    if not filtered_df.empty:
        for idx, row in filtered_df.iterrows():
            # expander 타이틀 타이포그래피 개선
            with st.expander(f"♟️ {row['클럽명']} ({row['지역']})"):
                st.write(f"**주소:** `{row['주소']}`")
                st.info(f"{row['특징']}")
    else:
        st.warning("검색 조건에 맞는 클럽이 없습니다.")

# 5. 하단 데이터프레임
st.markdown("---")
st.subheader("📊 전국 체스 거점 데이터 요약")
st.dataframe(filtered_df[["클럽명", "지역", "주소", "특징"]], use_container_width=True)