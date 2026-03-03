from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Cấu hình mặc định cho luồng chạy
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5), # Nếu lỗi sẽ thử lại sau 5 phút
}

# Khởi tạo DAG, hẹn giờ chạy vào lúc 0h00 mỗi ngày
with DAG(
    'it_jobs_etl_pipeline',
    default_args=default_args,
    description='Luồng ETL crawl và xử lý dữ liệu việc làm IT',
    schedule_interval='0 0 * * *', 
    catchup=False,
    tags=['it_jobs', 'etl']
) as dag:

    # Task 1: Chạy file crawl_data.py
    # Lệnh cd để đảm bảo file được chạy đúng thư mục chứa nó
    crawl_task = BashOperator(
        task_id='extract_data',
        bash_command='cd /opt/airflow/crawl && python crawl_data.py'
    )

    # Task 2: Chạy file clean_data.py
    clean_load_task = BashOperator(
        task_id='transform_and_load_data',
        bash_command='cd /opt/airflow/clean && python clean_data.py'
    )

    # Thiết lập thứ tự chạy: Task 1 xong mới đến Task 2
    crawl_task >> clean_load_task