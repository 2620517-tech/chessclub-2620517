import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. 페이지 설정
st.set_page_config(page_title="전국 체스클럽 지도", layout="wide", page_icon="♟️")

st.title("♟️ 전국 체스클럽 위치 지도")
st.markdown("전국의 주요 체스클럽 위치를 확인하고 검색해보세요!")

# 2. 샘플 데이터 생성 (실제 데이터로 확장 가능)
# 실제 서비스 시에는 공공데이터나 직접 수집한 주소 기반의 위도(Lat), 경도(Lon) 데이터를 넣으시면 됩니다.
@st.cache_data
def load_chess_club_data():
    data = {
        "클럽명": [
            "서울 체스 아카데미", "강남 마스터 체스클럽", "홍대 체크메이트 카페",
            "부산 체스 연합", "대전 나이트 체스클럽", "대구 비숍 체스교실", "광주 룩 체스센터"
        ],
        "지역": ["서울", "서울", "서울", "부산", "대전", "대구", "광주"],
        "주소": [
            "서울특별시 강남구 역삼동 123-4",
            "서울특별시 서초구 서초동 567-8",
            "서울특별시 마포구 서교동 910-11",
            "부산광역시 해운대구 우동 222",
            "대전광역시 서구 둔산동 333",
            "대구광역시 수성구 범어동 444",
            "광주광역시 서구 치평동 555"
        ],
        "Latitude": [37.4979, 37.4918, 37.5565, 35.1595, 36.3504, 35.8597, 35.1492],
        "Longitude": [127.0276, 127.0076, 126.9239, 129.1626, 127.3848, 128.6253, 126.8514],
        "연락처": ["02-123-4567", "02-987-6543", "02-555-5555", "051-111-2222", "042-333-4444", "053-555-6666", "062-777-8888"]
    }
    return pd.DataFrame(data)

df = load_chess_club_data()

# 3. 사이드바 - 지역 선택 및 검색 기능
st.sidebar.header("🔍 체스클럽 검색")
regions = ["전체"] + list(df["지역"].unique())
selected_region = st.sidebar.selectbox("지역 선택", regions)

search_keyword = st.sidebar.text_input("클럽명 검색", "")

# 데이터 필터링
filtered_df = df.copy()
if selected_region != "전체":
    filtered_df = filtered_df[filtered_df["지역"] == selected_region]
if search_keyword:
    filtered_df = filtered_df[filtered_df["클럽명"].str.contains(search_keyword, case=False)]

# 4. 메인 화면 구성 (레이아웃 분할)
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ 체스클럽 지도")
    
    # 지도의 중심점 설정 (데이터가 있으면 첫 번째 데이터 위치, 없으면 대한민국 중심)
    if not filtered_df.empty:
        center_lat = filtered_df["Latitude"].mean()
        center_lon = filtered_df["Longitude"].mean()
        zoom_level = 7 if selected_region == "전체" else 12
    else:
        center_lat, center_lon, zoom_level = 36.5, 127.5, 7

    # Folium 지도 객체 생성
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level, control_scale=True)

    # 지도에 마커 추가
    for idx, row in filtered_df.iterrows():
        popup_html = f"""
        <div style='font-family: Arial, sans-serif; width: 200px;'>
            <h4>{row['클럽명']}</h4>
            <p><b>주소:</b> {row['주소']}</p>
            <p><b>연락처:</b> {row['연락처']}</p>
        </div>
        """
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=row["클럽명"],
            icon=folium.Icon(color="cadetblue", icon="info-sign")
        ).add_to(m)

    # Streamlit에 지도 렌더링
    st_folium(m, width="100%", height=500, returned_objects=[])

with col2:
    st.subheader("📋 클럽 목록")
    st.write(f"검색된 클럽 수: {len(filtered_df)}개")
    
    # 지도 옆에 리스트 형태로 상세 정보 표시
    if not filtered_df.empty:
        for idx, row in filtered_df.iterrows():
            with st.expander(f"♟️ {row['클럽명']} ({row['지역']})"):
                st.write(f"**주소:** {row['주소']}")
                st.write(f"**연락처:** {row['연락처']}")
    else:
        st.warning("검색 결과가 없습니다.")

# 5. 데이터 테이블 표시 (하단)
st.markdown("---")
st.subheader("📊 전체 데이터 보기")
st.dataframe(filtered_df[["클럽명", "지역", "주소", "연락처"]], use_container_width=True)