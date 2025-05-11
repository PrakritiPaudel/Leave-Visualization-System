import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import date
from backend.services.leave_service import find_leaves

class TestLeaveService(unittest.TestCase):
    @patch('pandas.read_sql')
    @patch('backend.services.leave_service.db_engine')
    def test_find_leaves_with_date_range(self, mock_engine, mock_read_sql):
        # Setup mock connection
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        # Create a fake leave data table with columns like employee_id, name, etc.
        test_data = pd.DataFrame({
            'employee_id': ['E001', 'E002'],
            'first_name': ['John', 'Jane'],
            'last_name': ['Doe', 'Smith'],
            'employee_name': ['John Doe', 'Jane Smith'],
            'designation_name': ['Engineer', 'Manager'],
            'department_description': ['IT', 'HR'],
            'start_date': ['2024-01-01', '2024-01-02'],
            'end_date': ['2024-01-05', '2024-01-06'],
            'leave_type': ['Annual', 'Sick'],
            'leave_status': ['Approved', 'Pending'],
            'leave_days': [5, 4],
            'reason': ['Vacation', 'Health'],
            'leave_type_id': [1, 2],
            'fiscal_id': [2024, 2024],
            'is_automated': [0, 0],
            'is_converted': [0, 0]
        })
        
        # When read_sql() is called, return this fake data.
        mock_read_sql.return_value = test_data
        
        # Test parameters
        start_date = date(2024, 1, 1) #Set test start date.
        end_date = date(2024, 1, 31)
        leave_type_id = 1
        
        # Call function being tested
        result = find_leaves(start_date, end_date, leave_type_id)
        
        # Assertions
        self.assertIsInstance(result, dict) #Make sure the result is a dictionary.
        self.assertIn('employee_id', result) #Check if 'employee_id' is in the result.
        self.assertIn('employee_name', result)
        self.assertEqual(result['employee_id'][0], 'E001') #Check if first result has the right employee ID.
        self.assertEqual(result['employee_name'][0], 'John Doe')
        
        # Verify SQL query
        mock_read_sql.assert_called_once()
        call_args = mock_read_sql.call_args #Get the SQL query that was passed to read_sql().
        
        # Verify query contains main select and joins
        self.assertIn('SELECT DISTINCT l.employee_id', call_args[0][0]) #Ensure the query selects employee IDs.
        self.assertIn('LEFT JOIN dbo.department d', call_args[0][0])
        
        # Verify parameters
        self.assertEqual(
            call_args[1]['params'],
            {'start_date': start_date, 'end_date': end_date, 'leave_type_id': leave_type_id} #Ensure correct parameters were sent with the SQL.
        )

    @patch('pandas.read_sql') #Replaces pandas.read_sql() with a fake version. This prevents it from querying a real database.
    @patch('backend.services.leave_service.db_engine') #Replaces db_engine with a fake engine, so no real DB connection is made.
    def test_find_leaves_without_leave_type(self, mock_engine, mock_read_sql):  #Define a test where no leave type is provided.The mock objects are injected as parameters — mock_engine and mock_read_sql.
        # Setup mocks
        mock_conn = MagicMock() #Create a fake database connection object.
        mock_engine.connect.return_value.__enter__.return_value = mock_conn #Makes sure that with db_engine.connect() in real code returns the mock connection.
        mock_read_sql.return_value = pd.DataFrame() #When read_sql() is called in the function, it will return an empty DataFrame.
        
        # Sets up the test input: we’re calling find_leaves() without a leave type ID.
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        leave_type_id = None #	No filter by leave type.
        
        # Call function
        result = find_leaves(start_date, end_date, leave_type_id) #Calls the actual function being tested. Internally, it will use read_sql() and db_engine.connect(), but both are mocked.
        
        # Verify SQL doesn't contain leave_type_id filter
        call_args = mock_read_sql.call_args
        self.assertNotIn('AND l.leave_type_id', call_args[0][0]) #check the SQL query string that was passed to read_sql(). Make sure it does NOT contain the text 'AND l.leave_type_id'

if __name__ == '__main__':
    unittest.main()