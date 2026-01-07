import pandas as pd
import re

def clean_jobs():
    df = pd.read_csv("data/raw_jobs.csv")

    df.drop_duplicates(subset=["job_link"], inplace=True)
    df.fillna("N/A", inplace=True)

    # ===== CLEAN SALARY =====
    df["salary"] = (
        df["salary"]
        .astype(str)
        .str.replace("Xem nhanh", "", regex=False)
        .str.replace("\n", " ")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # ===== CLEAN EXPERIENCE =====
    df["experience"] = df["experience"].astype(str).str.strip()

    df.loc[
        df["experience"].str.contains("OccupationalExperienceRequirements", na=False),
        "experience"
    ] = "Đang cập nhật"

    df.to_csv("data/cleaned_jobs.csv", index=False, encoding="utf-8-sig")
    return df

if __name__ == "__main__":
    df = clean_jobs()
    print("✅ Đã làm sạch dữ liệu thành công!")
    print(f"📄 Số lượng bản ghi: {len(df)}")
