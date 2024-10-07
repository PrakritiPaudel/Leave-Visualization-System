from airflow import DAG
from airflow.operators.python import PythonOperator
from dotenv import load_dotenv
from airflow.utils.dates import days_ago
from datetime import timedelta
import sys
import os
import requests
# Add the path where your transformation scripts are located
sys.path.append('/home/prakriti/project-leave-visualization-system')

# Load environment variables from .env file
load_dotenv()

# # Get the api endpoint URL from the environment variable
api_endpoint = os.getenv('FASTAPI_URL')



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
def ingest_raw_data():
    response = requests.post(api_endpoint+'/ingest')
    return response.json()

def tranform_and_load_data():
    response = requests.post(api_endpoint+'/transform')
    return response.json()

# Define the task using PythonOperator
ingest_data_task = PythonOperator(
    task_id='ingest_data_task',
    python_callable=ingest_raw_data,
    dag=dag,
)

transform_data_task = PythonOperator(
    task_id='transform_data_task',
    python_callable=tranform_and_load_data,
    dag=dag,
)

# Set task dependencies if you have multiple tasks, for now, it’s a single task
ingest_data_task >> transform_data_task
