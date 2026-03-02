import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random

# CẤU HÌNH
JOB_POSITIONS = [
    "Backend Developer",
    "Frontend Developer",
    "Fullstack Developer",
    "Mobile Developer",
    "Game Developer",
    
    "Data Engineer",
    "Data Analyst",
    "Data Scientist",
    "AI Engineer",
    "Machine Learning Engineer",
    
    "Tester",
    "QA Engineer",
    "QC Engineer",
    "Automation Test",
    
    "DevOps Engineer",
    "Cloud Engineer",
    "System Administrator",
    "Network Engineer",
    "Security Engineer",
    "Embedded Engineer",
    
    "Business Analyst", 
    "Product Manager",
    "Project Manager",
    "Scrum Master",
    "UI/UX Designer"
]

BASE_URL = "https://123job.vn"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# THÊM THAM SỐ PAGE VÀO URL
def build_search_url(job_name, page=1):
    return f"{BASE_URL}/tuyen-dung?q={job_name.replace(' ', '+')}&page={page}"

def crawl_jobs():
    all_jobs = []

    for position in JOB_POSITIONS:
        print(f"\n🔍 Đang crawl vị trí: {position}")
        page = 1 # Bắt đầu từ trang 1
        
        while True: # Vòng lặp chạy vô tận cho đến khi hết trang
            url = build_search_url(position, page)
            print(f"   -> Đang quét trang {page}...")

            try:
                response = requests.get(url, headers=HEADERS, timeout=15)
                soup = BeautifulSoup(response.text, "html.parser")
                job_items = soup.find_all("div", class_="job__list-item")
                
                # NẾU KHÔNG TÌM THẤY JOB NÀO TRÊN TRANG NÀY -> ĐÃ ĐẾN TRANG CUỐI CÙNG -> THOÁT
                if len(job_items) == 0:
                    print(f"   🛑 Đã quét hết dữ liệu cho vị trí '{position}'.")
                    break 

                print(f"      Tìm thấy {len(job_items)} công việc. Bắt đầu lấy chi tiết...")

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
                        
                        time.sleep(random.uniform(1.5, 3.0)) # Giữ delay để tránh bị khóa IP
                        
                        try:
                            res_detail = requests.get(job_link, headers=HEADERS, timeout=10)
                            soup_detail = BeautifulSoup(res_detail.text, "html.parser")

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

                            if location == "N/A":
                                address_div = soup_detail.find("div", class_="job-detail__info-address")
                                if address_div:
                                    location = address_div.get_text(strip=True).replace("Địa điểm làm việc:", "").strip()

                            content_div = soup_detail.find("div", class_="content-collapse")
                            if content_div:
                                 full_description = content_div.get_text(separator="\n").strip()
                            
                        except Exception as e:
                            print(f"      ⚠ Lỗi detail link: {e}")

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
                        print(f"      ⚠ Lỗi item: {e}")
                        continue
                
                # Chuyển sang trang tiếp theo sau khi quét xong trang hiện tại
                page += 1

            except Exception as e:
                print(f"❌ Lỗi mạng ở trang {page}: {url} - {e}")
                break # Thoát nếu gặp lỗi mạng nghiêm trọng

    return pd.DataFrame(all_jobs)

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    print("🚀 BẮT ĐẦU QUÁ TRÌNH CRAWL TOÀN BỘ DỮ LIỆU...")
    df = crawl_jobs()
    print(f"\n✅ Đã hoàn thành! Tổng số job crawl được: {len(df)}")
    df.to_csv("data/raw_jobs.csv", index=False, encoding="utf-8-sig")