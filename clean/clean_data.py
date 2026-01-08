import pandas as pd
import re
import os

def clean_jobs():
    print("🚀 Bắt đầu quá trình làm sạch dữ liệu...")
    
    file_path = "data/raw_jobs.csv"
    
    # 1. Kiểm tra file tồn tại
    if not os.path.exists(file_path):
        print(f"❌ LỖI: Không tìm thấy file '{file_path}'")
        print("👉 Nguyên nhân: Có thể quá trình crawl chưa chạy xong hoặc bị lỗi.")
        return pd.DataFrame()

    try:
        df = pd.read_csv(file_path)
        print(f"📂 Đã đọc file raw. Số lượng bản ghi ban đầu: {len(df)}")
    except Exception as e:
        print(f"❌ Lỗi khi đọc file CSV: {e}")
        return pd.DataFrame()

    if df.empty:
        print("⚠️ CẢNH BÁO: File raw_jobs.csv có tồn tại nhưng KHÔNG CÓ DỮ LIỆU bên trong.")
        return df

    # 2. Xử lý trùng lặp
    print("... Đang xóa dữ liệu trùng lặp...")
    df.drop_duplicates(subset=["job_link"], inplace=True)
    df.fillna("N/A", inplace=True)

    # 3. Clean Salary
    print("... Đang chuẩn hóa cột Lương...")
    df["salary"] = (
        df["salary"]
        .astype(str)
        .str.replace("Xem nhanh", "", regex=False)
        .str.replace("\n", " ")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # 4. Clean Location
    df["location"] = df["location"].astype(str).str.strip()

    # 5. Clean Experience
    print("... Đang chuẩn hóa cột Kinh nghiệm...")
    def format_experience(exp):
        exp = str(exp).strip()
        match = re.search(r"OccupationalExperienceRequirements,\s*(\d+)", exp)
        if match:
            months = int(match.group(1))
            return f"{months // 12} năm" if months >= 12 else f"{months} tháng"
        if exp.lower() in ["nan", "n/a", "", "cập nhật"]: return "Không yêu cầu"
        return exp
    
    df["experience"] = df["experience"].apply(format_experience)

    # 6. Clean Description (Tạo Heading và List)
    print("... Đang định dạng Mô tả công việc (Heading & List)...")
    def format_description(text):
        if str(text) == "N/A": return text
        
        lines = str(text).split('\n')
        formatted_lines = []
        
        keywords = ["mô tả", "yêu cầu", "quyền lợi", "phúc lợi", "địa điểm", "thông tin", "description", "requirements", "benefits", "responsibility", "trách nhiệm"]
        
        for line in lines:
            line = line.strip()
            if not line: continue 
            
            is_header = False
            lower_line = line.lower()
            
            if len(line) < 50:
                if line.isupper() and len(line) > 4: 
                    is_header = True
                elif any(lower_line.startswith(k) for k in keywords):
                    is_header = True
                elif line.endswith(":"): 
                    is_header = True

            if is_header:
                formatted_lines.append(f"\n#### {line.upper()}") 
            else:
                if not line.startswith(("-", "*", "•", "+")):
                    formatted_lines.append(f"- {line}")
                else:
                    formatted_lines.append(line)
        
        return "  \n".join(formatted_lines)

    if "job_description" in df.columns:
        df["job_description"] = df["job_description"].apply(format_description)

    if "job_requirements" in df.columns:
        df.drop(columns=["job_requirements"], inplace=True)

    # 7. Lưu file
    output_path = "data/cleaned_jobs.csv"
    print(f"💾 Đang lưu kết quả vào '{output_path}'...")
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    
    return df

if __name__ == "__main__":
    df = clean_jobs()
    if not df.empty:
        print(f"\n✅ ĐÃ HOÀN THÀNH! Tổng số công việc sạch: {len(df)}")
    else:
        print("\n❌ QUÁ TRÌNH THẤT BẠI HOẶC KHÔNG CÓ DỮ LIỆU.")