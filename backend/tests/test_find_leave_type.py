import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from backend.services.leave_service import find_leave_types

class TestLeaveService(unittest.TestCase):
    @patch('pandas.read_sql')
    @patch('backend.services.leave_service.db_engine')
    def test_find_leave_types(self, mock_engine, mock_read_sql):
        # Setup mock connection
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        # Create test DataFrame with sample leave types
        test_data = pd.DataFrame({
            'id': [1, 2, 3],
            'leave_type': ['Annual', 'Sick', 'Menstruation']
        })
        
        # Configure mock to return test DataFrame
        mock_read_sql.return_value = test_data
        
        # Call the function
        result = find_leave_types()
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertIn('id', result)
        self.assertIn('leave_type', result)
        self.assertEqual(result['id'][0], 1)
        self.assertEqual(result['leave_type'][0], 'Annual')
        
        # Verify SQL query
        mock_read_sql.assert_called_once()
        call_args = mock_read_sql.call_args
        self.assertEqual(
            call_args[0][0].strip(),
            "SELECT id, leave_type FROM dbo.leave_type"
        )
        self.assertEqual(call_args[0][1], mock_conn)

if __name__ == '__main__':
    unittest.main()