import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests
import os

# 1. 페이지 설정
st.set_page_config(page_title="전국 체스클럽 자동 수집 지도", layout="wide", page_icon="♟️")

# 데이터 파일 경로 설정 (Streamlit Cloud 환경에서도 유지되도록 로컬 혹은 세션 상태 활용)
# 여기서는 세션 상태(Session State)를 활용해 앱이 켜져 있는 동안 데이터가 누적되도록 합니다.
DATA_FILE = "chess_clubs_database.csv"

# 카카오 API 키 입력 (자신의 REST API 키를 입력해야 작동합니다)
# Streamlit Cloud 배포 시에는 Advanced Settings의 Secrets 기능을 쓰는 것이 안전합니다.
KAKAO_API_KEY = st.secrets.get("KAKAO_API_KEY", "YOUR_KAKAO_REST_API_KEY_HERE")

# 초기 데이터 로드 함수
def init_data():
    if "club_df" not in st.session_state:
        # 파일이 이미 존재하면 읽어오고, 없으면 기본 데이터로 시작
        if os.path.exists(DATA_FILE):
            st.session_state.club_df = pd.read_csv(DATA_FILE)
        else:
            base_data = {
                "클럽명": ["슥슥이 체스클럽", "체스프릭 클럽 (체스프릭 EPA)", "마에스트로 체스클럽"],
                "지역": ["경기 고양", "경기 성남", "서울 서초"],
                "주소": ["경기 고양시 덕양구 서정마을1로 20-10", "경기 성남시 수정구 위례동로 135", "서울특별시 서초구 효령로 321"],
                "Latitude": [37.6258, 37.4725, 37.4871],
                "Longitude": [126.8443, 127.1428, 127.0253],
                "출처": ["수동입력", "수동입력", "수동입력"]
            }
            st.session_state.club_df = pd.DataFrame(base_data)

init_data()

# 카카오 지도 검색 API를 통해 '체스클럽'을 검색하는 함수
def search_kakao_chess_clubs(keyword):
    if KAKAO_API_KEY == "YOUR_KAKAO_REST_API_KEY_HERE" or not KAKAO_API_KEY:
        st.error("⚠️ 카카오 API 키가 설정되지 않았습니다. 사이드바 혹은 Secrets에 키를 입력해주세요.")
        return []
    
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": keyword, "size": 15} # 한 번에 최대 15개 수집
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            documents = response.json().get("documents", [])
            new_clubs = []
            for doc in documents:
                # 간단한 지역 가공
                address = doc.get("address_name", "")
                region = " ".join(address.split()[:2]) if address else "기타"
                
                new_clubs.append({
                    "클럽명": doc.get("place_name"),
                    "지역": region,
                    "주소": address if address else doc.get("road_address_name"),
                    "Latitude": float(doc.get("y")),
                    "Longitude": float(doc.get("x")),
                    "출처": "카카오 자동수집"
                })
            return new_clubs
        else:
            st.error(f"API 요청 실패: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"오류 발생: {e}")
        return []

# --- 메인 화면 레이아웃 ---
st.title("♟️ 전국 체스클럽 실시간 수집 및 지도")

# 3. 사이드바 제어창
st.sidebar.header("⚙️ 데이터 자동 수집기")
search_term = st.sidebar.text_input("인터넷 검색 키워드", "체스클럽")

if st.sidebar.button("🔍 인터넷에서 새로 찾아오기"):
    with st.spinner(f"인터넷에서 '{search_term}' 관련 장소를 검색 중..."):
        fetched_clubs = search_kakao_chess_clubs(search_term)
        
        if fetched_clubs:
            fetched_df = pd.DataFrame(fetched_clubs)
            
            # 중복 제거 로직 (클럽명이 같으면 제외)
            existing_names = st.session_state.club_df["클럽명"].tolist()
            filtered_new_df = fetched_df[~fetched_df["클럽명"].isin(existing_names)]
            
            if not filtered_new_df.empty:
                # 기존 데이터에 합치기
                st.session_state.club_df = pd.concat([st.session_state.club_df, filtered_new_df], ignore_index=True)
                # 파일로도 저장 보관
                st.session_state.club_df.to_csv(DATA_FILE, index=False)
                st.sidebar.success(f"🎉 새롭게 {len(filtered_new_df)}개의 장소를 찾아 추가했습니다!")
            else:
                st.sidebar.info("새로 검색된 장소 중 기존 리스트에 없는 새로운 곳이 없습니다.")
        else:
            st.sidebar.warning("검색 결과가 없거나 API 설정을 확인하세요.")

# 일반 필터 기능
st.sidebar.markdown("---")
st.sidebar.header("🔍 필터 및 검색")
search_keyword = st.sidebar.text_input("등록된 클럽명 검색", "")

display_df = st.session_state.club_df.copy()
if search_keyword:
    display_df = display_df[display_df["클럽명"].str.contains(search_keyword, case=False)]

# 4. 지도 및 목록 시각화
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ 체스 거점 지도")
    center_lat, center_lon = 36.5, 127.5
    m = folium.Map(location=[center_lat, center_lon], zoom_start=7, control_scale=True)

    for idx, row in display_df.iterrows():
        color = "red" if "슥슥이" in row["클럽명"] or "체스프릭" in row["클럽명"] else "blue"
        popup_html = f"<b>{row['클럽명']}</b><br><small>{row['주소']}</small><br><span style='color:green;'>[{row['출처']}]</span>"
        
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=row["클럽명"],
            icon=folium.Icon(color=color)
        ).add_to(m)

    st_folium(m, width="100%", height=500, returned_objects=[])

with col2:
    st.subheader("📋 수집된 공간 목록")
    st.write(f"현재 총 **{len(display_df)}**개의 공간이 지도에 표시 중입니다.")
    
    for idx, row in display_df.iterrows():
        with st.expander(f"{row['클럽명']} ({row['지역']})"):
            st.write(f"**📍 주소:** {row['주소']}")
            st.caption(f"데이터 출처: {row['출처']}")

st.markdown("---")
st.subheader("📊 데이터베이스 전체 보기")
st.dataframe(st.session_state.club_df, use_container_width=True)