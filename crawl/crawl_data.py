import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random
import re

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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def build_search_url(job_name):
    return f"{BASE_URL}/tuyen-dung?q={job_name.replace(' ', '+')}"

def crawl_jobs():
    all_jobs = []

    for position in JOB_POSITIONS:
        print(f"🔍 Đang crawl vị trí: {position}")
        url = build_search_url(position)

        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            job_items = soup.find_all("div", class_="job__list-item")
            
            # In ra số lượng tìm thấy để bạn kiểm tra
            print(f"   -> Tìm thấy {len(job_items)} công việc trên trang này.")

            # --- THAY ĐỔI Ở ĐÂY: Đã bỏ [:10] để chạy hết danh sách ---
            for item in job_items: 
                try:
                    # 1. Lấy thông tin cơ bản
                    title_tag = item.find("h2", class_="job__list-item-title")
                    if not title_tag: continue
                    a_tag = title_tag.find("a")
                    job_name = a_tag.get_text(strip=True)
                    job_link = a_tag["href"]
                    if not job_link.startswith("http"):
                        job_link = BASE_URL + job_link

                    company_tag = item.find("div", class_="job__list-item-company")
                    company = company_tag.find("span").get_text(strip=True) if company_tag else "N/A"

                    # 2. VÀO TRANG CHI TIẾT
                    experience = "N/A"
                    salary = "N/A"
                    location = "N/A"
                    full_description = "N/A"
                    
                    # Tăng delay một chút để an toàn khi crawl số lượng lớn hơn
                    time.sleep(random.uniform(0.8, 1.5)) 
                    
                    try:
                        res_detail = requests.get(job_link, headers=HEADERS, timeout=10)
                        soup_detail = BeautifulSoup(res_detail.text, "html.parser")

                        # LOGIC QUÉT ATTR-ITEM (Lấy Lương, Kinh nghiệm, Địa điểm)
                        attr_items = soup_detail.find_all("div", class_="attr-item")
                        
                        for attr in attr_items:
                            full_text = attr.get_text(strip=True).lower()
                            value_div = attr.find("div", class_="value")
                            
                            if value_div:
                                value_text = value_div.get_text(strip=True)
                                if "kinh nghiệm" in full_text:
                                    experience = value_text
                                elif "lương" in full_text:
                                    salary = value_text
                                elif "địa điểm" in full_text:
                                    location = value_text

                        # Fallback cho Location nếu chưa tìm thấy
                        if location == "N/A":
                            address_div = soup_detail.find("div", class_="job-detail__info-address")
                            if address_div:
                                location = address_div.get_text(strip=True).replace("Địa điểm làm việc:", "").strip()

                        # Lấy Nội Dung
                        content_div = soup_detail.find("div", class_="content-collapse")
                        if content_div:
                             full_description = content_div.get_text(separator="\n").strip()
                        
                    except Exception as e:
                        print(f"⚠ Lỗi detail link: {e}")

                    all_jobs.append({
                        "position_search": position,
                        "job_name": job_name,
                        "job_link": job_link,
                        "company": company,
                        "location": location,
                        "salary": salary,
                        "experience": experience,
                        "job_description": full_description,
                        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                except Exception as e:
                    print(f"⚠ Lỗi item: {e}")
                    continue

        except Exception as e:
            print(f"❌ Lỗi mạng: {url}")

    return pd.DataFrame(all_jobs)

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = crawl_jobs()
    print(f"\n✅ Tổng số job crawl được: {len(df)}")
    df.to_csv("data/raw_jobs.csv", index=False, encoding="utf-8-sig")