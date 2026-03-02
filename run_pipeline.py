import subprocess
import time
import os

def run_script(script_name, working_dir):
    print(f"\n{'='*50}")
    print(f"{'='*50}\n")
    
    start_time = time.time()
    
    try:
        # Sử dụng subprocess để chạy file python
        process = subprocess.run(
            ["python", script_name],
            cwd=working_dir,
            check=True # Báo lỗi ngay nếu script chạy thất bại
        )
        
        end_time = time.time()
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ LỖI NGHIÊM TRỌNG TẠI BƯỚC: {script_name}")
        print(f"Chi tiết mã lỗi: {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"\n❌ Không tìm thấy 'python'. Hãy kiểm tra lại biến môi trường.")
        return False

def main():
    print("🚀 BẮT ĐẦU CHẠY TOÀN BỘ LUỒNG DỮ LIỆU (ETL PIPELINE) 🚀")
    total_start_time = time.time()
    
    # Lấy đường dẫn tuyệt đối của thư mục gốc
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Crawl Data (Extract)
    crawl_dir = os.path.join(base_dir, "crawl")
    if not run_script("crawl_data.py", crawl_dir):
        print("\n🛑 Pipeline bị dừng vì Crawl thất bại.")
        return

    # Clean & Load Data (Transform & Load)
    clean_dir = os.path.join(base_dir, "clean")
    if not run_script("clean_data.py", clean_dir):
        print("\n🛑 Pipeline bị dừng vì Clean thất bại.")
        return

    total_end_time = time.time()

if __name__ == "__main__":
    main()