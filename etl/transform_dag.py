from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.sensors.external_task import ExternalTaskSensor
from dotenv import load_dotenv
from airflow.utils.dates import days_ago
from datetime import timedelta, datetime
import sys
import os
import requests

# Add the path where your transformation scripts are located
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

# Define the transform DAG
transform_dag = DAG(
    'transform_dag',
    default_args=default_args,
    description='A DAG to transform and load data into dbo tables',
    schedule_interval=None,  # Set None since we're using TriggerDagRunOperator
    start_date=days_ago(1),
    catchup=False,
)

def transform_and_load_data(**context):
    try:
        response = requests.post(api_endpoint+'/transform')
        result = response.json()
        # Store result in XCom
        context['task_instance'].xcom_push(key='transform_result', value=result)
        return result
    except Exception as e:
        # Raise the exception to trigger the failure workflow
        raise Exception(f"Data transformation failed: {str(e)}")

# Define the transform task
transform_task = PythonOperator(
    task_id='transform_dag',
    python_callable=transform_and_load_data,
    provide_context=True,  # This passes the context to the callable
    dag=transform_dag,
)

# Add a task to send a detailed email on failure
email_on_failure_task = EmailOperator(
    task_id='send_failure_email',
    to=[email_recipient],
    subject='Airflow Alert: Transform Data Task Failed',
    html_content="""
    <h2>Transform Data Task Failed</h2>
    <p>The data transformation task in the 'transform_and_load_data' DAG has failed.</p>
    <p>Please check the Airflow logs for more details.</p>
    <p>DAG: {{ dag.dag_id }}</p>
    <p>Task: {{ task.task_id }}</p>
    <p>Execution Date: {{ ds }}</p>
    <p>Log URL: {{ ti.log_url }}</p>
    """,
    trigger_rule='one_failed',  # This task will only run if any upstream task fails
    dag=transform_dag,
)

# Set the dependencies
transform_task >> email_on_failure_task