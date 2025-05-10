import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
from backend.services.fiscal_service import find_fiscal_years

class TestFiscalService(unittest.TestCase):
    @patch('pandas.read_sql')
    @patch('backend.services.fiscal_service.db_engine')
    def test_find_fiscal_years(self, mock_engine, mock_read_sql):
        # Setup mock connection
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        # Create test DataFrame with sample fiscal years
        test_data = pd.DataFrame({
            'fiscal_start_date': [
                datetime(2023, 7, 16),
                datetime(2024, 7, 16)
            ],
            'fiscal_end_date': [
                datetime(2024, 7, 15),
                datetime(2025, 7, 15)
            ]
        })
        
        # Configure mock to return test DataFrame
        mock_read_sql.return_value = test_data
        
        # Call the function
        result = find_fiscal_years()
        
        # Assertions
        self.assertIsInstance(result, dict)
        self.assertIn('fiscal_start_date', result)
        self.assertIn('fiscal_end_date', result)
        
        # Verify dates are present
        self.assertEqual(
            result['fiscal_start_date'][0].year,
            2023
        )
        self.assertEqual(
            result['fiscal_end_date'][0].year,
            2024
        )
        
        # Verify SQL query
        mock_read_sql.assert_called_once()
        call_args = mock_read_sql.call_args
        self.assertEqual(
            call_args[0][0].strip(),
            "SELECT fiscal_start_date, fiscal_end_date  from dbo.fiscal"
        )
        self.assertEqual(call_args[0][1], mock_conn)

if __name__ == '__main__':
    unittest.main()