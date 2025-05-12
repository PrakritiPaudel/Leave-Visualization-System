import pandas as pd
from sqlalchemy import text
from backend.db import db_engine
import logging

def populate_allocation_data():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        with db_engine.connect() as connection:
            # Start a transaction
            with connection.begin():
                # Query to retrieve distinct allocation data
                allocation_query = """
                SELECT DISTINCT
                    CAST(ad."id" AS INTEGER) AS id,
                    ad."empId" AS emp_id,
                    ad."name",
                    ad."type"
                FROM raw.allocation_data ad
                """
                allocation_df = pd.read_sql(allocation_query, connection)
                
                # Check for duplicate IDs in the source data
                if allocation_df['id'].duplicated().any():
                    duplicate_ids = allocation_df[allocation_df['id'].duplicated(keep=False)]['id'].unique()
                    logger.warning(f"Found duplicate IDs in source data: {duplicate_ids}")
                    # Keep only the first occurrence of each ID
                    allocation_df = allocation_df.drop_duplicates(subset=['id'], keep='first')
                
                # Log the count of records to be inserted
                logger.info(f"Attempting to upsert {len(allocation_df)} allocation records")
                
                success_count = 0
                error_count = 0
                
                for _, row in allocation_df.iterrows():
                    try:
                        upsert_allocation_query = """
                        INSERT INTO dbo.allocation (id, emp_id, name, type)
                        VALUES (:id, :emp_id, :name, :type)
                        ON CONFLICT (id)
                        DO UPDATE SET
                            emp_id = EXCLUDED.emp_id,
                            name = EXCLUDED.name,
                            type = EXCLUDED.type;
                        """
                        connection.execute(text(upsert_allocation_query), {
                            'id': row['id'],
                            'emp_id': row['emp_id'],
                            'name': row['name'],
                            'type': row['type']
                        })
                        success_count += 1
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error upserting allocation ID {row['id']}: {str(e)}")
                
                logger.info(f"Allocation data upsert complete. Success: {success_count}, Errors: {error_count}")
        
        print("Allocation data upsert process completed.")
        return True
    
    except Exception as e:
        logger.error(f"Failed to populate allocation data: {str(e)}")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    populate_allocation_data()