from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import sys
import os

# Add the path where your transformation scripts are located
sys.path.append('/home/prakriti/project-leave-visualization-system')

from src.transformation.dbo.transform import transform_data as transform_data_function

# Define default_args for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    # 'email_on_failure': ['your-email@example.com'],
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'transform_data_function',
    default_args=default_args,
    description='A DAG to transform and load data into dbo tables',
    schedule_interval='@daily',  # Adjust the schedule as needed
    start_date=days_ago(1),
    catchup=False,
)
# Define a function to run all transformation tasks
def run_transform_data():
    transform_data_function()
    print("Data transformed and inserted into dbo tables successfully.")

# Define the task using PythonOperator
transform_data_task = PythonOperator(
    task_id='transform_data_task',
    python_callable=run_transform_data,
    dag=dag,
)

# Set task dependencies if you have multiple tasks, for now, it’s a single task
transform_data_task
