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
        
        # Create test DataFrame
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
        
        # Configure mock to return test DataFrame
        mock_read_sql.return_value = test_data
        
        # Test parameters
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        leave_type_id = 1
        
        # Call function
        result = find_leaves(start_date, end_date, leave_type_id)
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertIn('employee_id', result)
        self.assertIn('employee_name', result)
        self.assertEqual(result['employee_id'][0], 'E001')
        self.assertEqual(result['employee_name'][0], 'John Doe')
        
        # Verify SQL query
        mock_read_sql.assert_called_once()
        call_args = mock_read_sql.call_args
        
        # Verify query contains main select and joins
        self.assertIn('SELECT DISTINCT l.employee_id', call_args[0][0])
        self.assertIn('LEFT JOIN dbo.department d', call_args[0][0])
        
        # Verify parameters
        self.assertEqual(
            call_args[1]['params'],
            {'start_date': start_date, 'end_date': end_date, 'leave_type_id': leave_type_id}
        )

    @patch('pandas.read_sql')
    @patch('backend.services.leave_service.db_engine')
    def test_find_leaves_without_leave_type(self, mock_engine, mock_read_sql):
        # Setup mocks
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        mock_read_sql.return_value = pd.DataFrame()
        
        # Test without leave_type_id
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        leave_type_id = None
        
        # Call function
        result = find_leaves(start_date, end_date, leave_type_id)
        
        # Verify SQL doesn't contain leave_type_id filter
        call_args = mock_read_sql.call_args
        self.assertNotIn('AND l.leave_type_id', call_args[0][0])

if __name__ == '__main__':
    unittest.main()