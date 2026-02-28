import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="IT Job Dashboard",
    page_icon="💼",
    layout="wide"
)

st.title("📊 Dashboard Phân Tích Việc Làm IT trên https://123job.vn")
st.markdown("---")

@st.cache_data
def load_data():
    try:
        return pd.read_csv("clean/data/cleaned_jobs.csv")
    except FileNotFoundError:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("Chưa có dữ liệu.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔍 Bộ Lọc")
    positions = ["Tất cả"] + sorted(df["position_search"].unique().tolist())
    selected_position = st.selectbox("Chọn vị trí:", positions)

if selected_position != "Tất cả":
    filtered_df = df[df["position_search"] == selected_position]
else:
    filtered_df = df

# --- METRICS ---
c1, c2, c3 = st.columns(3)
c1.metric("Số lượng công việc", len(filtered_df))
c2.metric("Vị trí", selected_position)
c3.metric("Nguồn", "123job.vn")
st.markdown("---")

# --- DANH SÁCH JOB ---
st.subheader(f"📌 Danh sách công việc ({len(filtered_df)} jobs)")

for index, row in filtered_df.iterrows():
    with st.container():
        # Header
        st.markdown(f"### 👉 [{row['job_name']}]({row['job_link']})")
        
        # Thông tin cơ bản
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"🏢 **Công ty:** {row['company']}")
        c2.markdown(f"📍 **Địa điểm:** {row['location']}")
        c3.markdown(f"💰 **Lương:** {row['salary']}")
        c4.markdown(f"🧠 **Kinh nghiệm:** {row['experience']}")
        
        # Phần nội dung
        with st.expander("📝 Xem chi tiết nội dung công việc"):
            if row['job_description'] != "N/A":
                st.markdown(row['job_description'])
            else:
                st.warning("Chưa có thông tin mô tả.")
        
        st.divider()