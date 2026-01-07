import streamlit as st
import pandas as pd

# CẤU HÌNH TRANG
st.set_page_config(
    page_title="IT Job Dashboard",
    layout="wide"
)

st.title("📊 Dashboard việc làm ngành IT")

# LOAD DATA
@st.cache_data
def load_data():
    return pd.read_csv("data/cleaned_jobs.csv")

df = load_data()

# SIDEBAR - CHỌN VỊ TRÍ
st.sidebar.header("🔍 Lọc vị trí IT")

positions = sorted(df["position_search"].unique())
selected_position = st.sidebar.selectbox(
    "Chọn vị trí:",
    positions
)

filtered_df = df[df["position_search"] == selected_position]

st.subheader(f"📌 {selected_position} — {len(filtered_df)} công việc")

# HIỂN THỊ JOB
for _, row in filtered_df.iterrows():
    with st.container():
        st.markdown(f"### 🔹 {row['job_name']}")
        st.markdown(f"🏢 **Công ty:** {row['company']}")
        st.markdown(f"📍 **Địa điểm:** {row['location']}")
        st.markdown(f"💰 **Lương:** {row['salary']}")
        st.markdown(f"🧠 **Kinh nghiệm:** {row['experience']}")

        # Yêu cầu công việc (expand)
        with st.expander("📋 Yêu cầu công việc"):
            st.text(row["job_requirements"])

        # Link chi tiết
        st.markdown(f"[🔗 Xem chi tiết]({row['job_link']})")

        st.divider()
