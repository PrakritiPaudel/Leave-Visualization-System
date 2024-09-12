from supabase import create_client, Client
import os
import time

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_API_KEY')
BUCKET_NAME= os.getenv('BUCKET_NAME')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to upload file
def upload_file_to_supabase(file_name, file_content):
    try:
        uploaded_file_name = str(time.time())+file_name

        # Upload file to the specified bucket
        response = supabase.storage.from_(BUCKET_NAME).upload(uploaded_file_name,  file_content)
        # return response
        print("Upload successful:", response)
    except Exception as e:
        print("Error during upload:", e)
