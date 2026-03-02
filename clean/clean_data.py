import pandas as pd
import re
import os
from sqlalchemy import create_engine

def load_to_postgres(df):
    
    # Cấu hình thông tin kết nối 
    DB_USER = 'postgres'
    DB_PASSWORD = 'postgres' 
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_NAME = 'IT_job_data'

    try:
        # Tạo kết nối đến database
        engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
        
        # Đẩy DataFrame vào database
        df.to_sql('it_jobs', engine, if_exists='replace', index=False)
        
        print("✅ Đã load dữ liệu vào DB.")
    except Exception as e:
        print(f"❌ Lỗi khi đẩy dữ liệu vào Database: {e}")

def clean_jobs():
    print("🚀 Đang bắt đầu tiến trình làm sạch dữ liệu...")
    
    # --- CẤU HÌNH ĐƯỜNG DẪN ---
    current_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(current_dir, "..", "crawl", "data", "raw_jobs.csv")
    output_dir = os.path.join(current_dir, "data")
    output_file = os.path.join(output_dir, "cleaned_jobs.csv")

    if not os.path.exists(input_file):
        print(f"❌ LỖI: Không tìm thấy file '{input_file}'!")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Đã tạo thư mục chứa dữ liệu sạch tại: {output_dir}")

    try:
        df = pd.read_csv(input_file, encoding="utf-8-sig")
        print(f"📂 Đã đọc file raw. Số lượng ban đầu: {len(df)} dòng.")

        if df.empty:
            print("⚠️ Cảnh báo: File dữ liệu rỗng.")
            return

        # 1. XỬ LÝ TRÙNG LẶP
        df.drop_duplicates(subset=["job_link"], inplace=True)

        # 2. KIỂM TRA VÀ XÓA DÒNG THIẾU DỮ LIỆU
        before_drop = len(df)
        
        # Lấy danh sách các cột cần kiểm tra 
        exclude_cols = ["salary", "experience", "job_requirements"]
        cols_to_check = [col for col in df.columns if col not in exclude_cols]

        for col in cols_to_check:
            # Lọc bỏ các dòng có giá trị null thực sự (NaN)
            df = df[df[col].notna()]
            # Lọc bỏ các dòng chứa chuỗi "N/A", "nan", rỗng 
            df = df[~df[col].astype(str).str.strip().str.lower().isin(["n/a", "nan", "", "none"])]

        after_drop = len(df)
        if before_drop - after_drop > 0:
            print(f"    -> Đã xóa {before_drop - after_drop} dòng không đủ dữ liệu hợp lệ.")

        # Fill N/A cho các giá trị rỗng còn sót lại 
        df.fillna("N/A", inplace=True)

        # 3. CHUẨN HÓA LƯƠNG
        df["salary"] = (
            df["salary"]
            .astype(str)
            .str.replace("Xem nhanh", "", regex=False)
            .str.replace("\n", " ")
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )
        df.loc[df["salary"].str.lower() == "đang cập nhật", "salary"] = "Thoả thuận"

        # 4. CHUẨN HÓA KINH NGHIỆM
        def format_experience(exp):
            exp = str(exp).strip()
            
            match = re.search(r"OccupationalExperienceRequirements,\s*(\d+)", exp)
            if match:
                months = int(match.group(1))
                if months >= 12:
                    return f"{months // 12} năm"
                elif months > 0:
                    return f"{months} tháng"
            
            targets = ["không yêu cầu", "nan", "n/a", "", "cập nhật", "đang cập nhật", "no requirements"]
            if exp.lower() in targets:
                return "Có yêu cầu"
            
            return exp

        df["experience"] = df["experience"].apply(format_experience)

        # 5. ĐỊNH DẠNG MÔ TẢ (Heading & List)
        def smart_format(text):
            if str(text) == "N/A": return text
            lines = str(text).split('\n')
            fmt = []
            keys = ["mô tả", "yêu cầu", "quyền lợi", "phúc lợi", "description", "requirements", "benefits", "who we are", "about", "responsibilities"]
            
            for l in lines:
                l = l.strip()
                if not l: continue
                if len(l) < 55 and (l.isupper() or any(l.lower().startswith(k) for k in keys) or l.endswith(":")):
                    fmt.append(f"\n#### {l.upper()}")
                else:
                    if not l.startswith(("-", "*", "•", "+")):
                        fmt.append(f"- {l}")
                    else:
                        fmt.append(l)
            return "  \n".join(fmt)

        if "job_description" in df.columns:
            df["job_description"] = df["job_description"].apply(smart_format)

        if "job_requirements" in df.columns:
            df.drop(columns=["job_requirements"], inplace=True)

        # 6. LƯU FILE
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"✅ THÀNH CÔNG! Đã lưu {len(df)} dòng data sạch.")
        # 7. ĐẨY DỮ LIỆU VÀO DATABASE
        load_to_postgres(df)

    except PermissionError:
        print(f"❌ LỖI: Không thể ghi file.")
    except Exception as e:
        print(f"❌ Đã xảy ra lỗi: {e}")

if __name__ == "__main__":
    clean_jobs()