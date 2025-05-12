from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator  
from dotenv import load_dotenv
from airflow.utils.dates import days_ago
from datetime import timedelta
import sys
import os
import requests

# Add the path where your scripts are located
sys.path.append('/home/prakriti/project-leave-visualization-system')

# Load environment variables from .env file
load_dotenv()

# Get the api endpoint URL from the environment variable
api_endpoint = os.getenv('SERVER_ENDPOINT')

# Email to receive failure notifications
email_recipient = 'iprakrity.paudel0@gmail.com'

# Define default_args for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': [email_recipient],  # Email to send notifications to
    'email_on_failure': True,    # Send email on task failure
    'email_on_retry': False,     # Don't send email on retry
    'retries': 0,
    # 'retry_delay': timedelta(minutes=5),
}

# Define the ingest DAG
ingest_dag = DAG(
    'ingest_raw_data',
    default_args=default_args,
    description='A DAG to ingest raw data',
    schedule_interval='*/05 * * * *',  # Every 10 minutes - must match transform DAG
    start_date=days_ago(1),
    catchup=False,
)

def ingest_raw_data(**context):
    try:
        response = requests.post(api_endpoint+'/ingest')
        result = response.json()
        # Store the result in XCom for potential use in other tasks
        context['ti'].xcom_push(key='ingest_result', value=result)
        return result
    except Exception as e:
        # Raise the exception to trigger the failure workflow
        raise Exception(f"Data ingestion failed: {str(e)}")

# Define the ingest task
ingest_data_task = PythonOperator(
    task_id='ingest_data_task',
    python_callable=ingest_raw_data,
    provide_context=True,  # This passes the context to the callable
    dag=ingest_dag,
)

# Add a task to check if ingestion was successful
def check_ingest_success(**context):
    ti = context['ti']
    ingest_result = ti.xcom_pull(task_ids='ingest_data_task', key='ingest_result')
    if not ingest_result:
        raise Exception("Ingestion failed or no data received")
    return ingest_result

check_ingest_task = PythonOperator(
    task_id='check_ingest_success',
    python_callable=check_ingest_success,
    provide_context=True,
    dag=ingest_dag
)

# Add trigger for transform DAG
trigger_transform = TriggerDagRunOperator(
    task_id='trigger_transform_dag',
    trigger_dag_id='transform_dag',
    wait_for_completion=False,
    trigger_rule='all_success',
    conf={'ingest_execution_date': '{{ ds }}'},  # Pass execution date to transform DAG
    dag=ingest_dag
)

# Add a task to send a detailed email on failure
email_on_failure_task = EmailOperator(
    task_id='send_failure_email',
    to=[email_recipient],
    subject='Airflow Alert: Ingest Data Task Failed',
    html_content="""
    <h2>Ingest Data Task Failed</h2>
    <p>The data ingestion task in the 'ingest_raw_data' DAG has failed.</p>
    <p>Please check the Airflow logs for more details.</p>
    <p>DAG: {{ dag.dag_id }}</p>
    <p>Task: {{ task.task_id }}</p>
    <p>Execution Date: {{ ds }}</p>
    <p>Log URL: {{ ti.log_url }}</p>
    """,
    trigger_rule='one_failed',  # This task will only run if the upstream task fails
    dag=ingest_dag,
)

# Set branching task dependencies
ingest_data_task >> check_ingest_task
check_ingest_task >> trigger_transform  # Success path
check_ingest_task >> email_on_failure_task  # Failure path