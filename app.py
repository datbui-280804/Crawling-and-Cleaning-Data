import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# CẤU HÌNH TRANG
st.set_page_config(
    page_title="IT Job Dashboard",
    page_icon="💼",
    layout="wide"
)

st.title("📊 Dashboard Phân Tích Việc Làm IT")
st.markdown("**Powered by PostgreSQL & Python** 🐘")
st.markdown("---")

# HÀM KẾT NỐI VÀ LẤY DỮ LIỆU TỪ DATABASE
@st.cache_data(ttl=600) # Cập nhật lại mỗi 10 phút
def load_data_from_db():
    DB_USER = 'postgres'
    DB_PASSWORD = 'postgres' 
    DB_HOST = 'postgres'
    DB_PORT = '5432'
    DB_NAME = 'IT_job_data'
    
    try:
        # Tạo kết nối
        engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
        
        # SQL Query để lấy toàn bộ dữ liệu từ bảng it_jobs
        query = "SELECT * FROM it_jobs;"
        df = pd.read_sql(query, engine)
        
        return df
    except Exception as e:
        st.error(f"❌ Lỗi kết nối Database: {e}")
        return pd.DataFrame()

# TẢI DỮ LIỆU
df = load_data_from_db()

if df.empty:
    st.warning("Chưa có dữ liệu trong Database. Vui lòng chạy luồng ETL trước!")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔍 Bộ Lọc")
    positions = ["Tất cả"] + sorted(df["position_search"].unique().tolist())
    selected_position = st.selectbox("Chọn vị trí công việc:", positions)

# --- FILTER DATA ---
if selected_position != "Tất cả":
    filtered_df = df[df["position_search"] == selected_position]
else:
    filtered_df = df

# --- METRICS ---
col1, col2, col3 = st.columns(3)
col1.metric("Số lượng công việc", len(filtered_df))
col2.metric("Vị trí đang chọn", selected_position)

st.markdown("---")

# --- HIỂN THỊ JOB LIST ---
st.subheader(f"📌 Danh sách công việc ({len(filtered_df)} jobs)")

for index, row in filtered_df.iterrows():
    with st.container():
        st.markdown(f"### 👉 [{row['job_name']}]({row['job_link']})")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"🏢 **Công ty:** {row['company']}")
        c2.markdown(f"📍 **Địa điểm:** {row['location']}")
        c3.markdown(f"💰 **Lương:** {row['salary']}")
        c4.markdown(f"🧠 **Kinh nghiệm:** {row['experience']}")
        
        with st.expander("📝 Xem chi tiết nội dung công việc"):
            if pd.notna(row['job_description']) and row['job_description'] != "N/A":
                st.markdown(row['job_description'])
            else:
                st.warning("Chưa có thông tin mô tả.")
        
        st.divider()