import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# CẤU HÌNH
JOB_POSITIONS = [
    "Tester",
    "Backend Developer",
    "Frontend Developer",
    "Fullstack Developer",
    "Data Engineer",
    "Data Analyst",
    "Data Scientist",
    "DevOps Engineer",
    "AI Engineer",
    "Mobile Developer"
]

BASE_URL = "https://123job.vn"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# BUILD SEARCH URL
def build_search_url(job_name):
    return f"{BASE_URL}/tuyen-dung?q={job_name.replace(' ', '+')}"

# MAIN CRAWLER
def crawl_jobs():
    all_jobs = []

    for position in JOB_POSITIONS:
        print(f"🔍 Đang crawl vị trí: {position}")
        url = build_search_url(position)

        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"❌ Không truy cập được: {url}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        job_items = soup.find_all("div", class_="job__list-item-content")

        print(f"➡ Tìm thấy {len(job_items)} job")

        for job in job_items:
            title_tag = job.find("a")

            job_name = title_tag.text.strip() if title_tag else "N/A"
            job_link = title_tag["href"] if title_tag else "N/A"

            # 🔧 Fix link tương đối
            if job_link.startswith("/"):
                job_link = BASE_URL + job_link

            company = job.find("div", class_="job__list-item-company")
            location = job.find("div", class_="address")
            salary = job.find("div", class_="salary")

            experience = "N/A"
            requirements = "N/A"

            # TRANG CHI TIẾT
            if job_link != "N/A":
                try:
                    detail_res = requests.get(job_link, headers=HEADERS, timeout=15)
                    if detail_res.status_code == 200:
                        detail_soup = BeautifulSoup(detail_res.text, "html.parser")

                        # Kinh nghiệm
                        attr_items = detail_soup.find_all("div", class_="attr-item")
                        for item in attr_items:
                            label_div = item.find("div", class_="text mb-1")

                            if label_div and "Kinh nghiệm" in label_div.text:
                                value_div = item.find("div", class_="value")
                                if value_div:
                                    experience = value_div.text.strip()
                                break
                            
                        # Yêu cầu công việc
                        for group in detail_soup.find_all("div", class_="content-group"):
                            title = group.find("h2")
                            if title and "Yêu cầu công việc" in title.text:
                                content = group.find("div", class_="content-group__content")
                                requirements = (
                                    content.get_text(separator="\n").strip()
                                    if content else "N/A"
                                )
                except Exception as e:
                    print(f"⚠ Lỗi khi crawl chi tiết: {job_link}")

            all_jobs.append({
                "position_search": position,
                "job_name": job_name,
                "job_link": job_link,
                "company": company.text.strip() if company else "N/A",
                "location": location.text.strip() if location else "N/A",
                "salary": salary.text.strip() if salary else "N/A",
                "experience": experience,
                "job_requirements": requirements,
                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    return pd.DataFrame(all_jobs)

# RUN & SAVE
if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    df = crawl_jobs()

    print(f"\n✅ Tổng số job crawl được: {len(df)}")

    df.to_csv(
        "data/raw_jobs.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("📁 Đã lưu file: data/raw_jobs.csv")
