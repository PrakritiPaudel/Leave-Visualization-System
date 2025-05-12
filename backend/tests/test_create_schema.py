import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

from backend.data_ingestion.api_fetch import create_schema

class TestCreateSchema(unittest.TestCase):
    # Test Schema is created and correct message is printed
    
    @patch('backend.data_ingestion.api_fetch.engine') # fake the engine object so we don't call a real DB
    def test_create_schema_success(self, mock_engine): # the fake engine object from patch
        """Test that the function correctly creates the schema"""
        # Setup mock connection
        mock_connection = MagicMock() #Create a fake DB connection object
        mock_engine.begin.return_value.__enter__.return_value = mock_connection 
        #begin: returns something (a context manager) 
        #__enter__(): when with block starts, it returns mock_connection
        
    
        with patch('builtins.print') as mock_print: #Replace Python’s print() with mock_print so we can check what was printed
            create_schema() #Call create_schema() like normal
        
        # Check if execute() was called once (expected behavior)
        mock_connection.execute.assert_called_once()
        
        # Get the actual SQL query that was run, and convert it to a string
        sql = str(mock_connection.execute.call_args[0][0])
        # Check that the query contains this exact phrase (to ensure correct SQL)
        self.assertIn("CREATE SCHEMA IF NOT EXISTS raw", sql)
        
        # Check that the correct success message was printed
        mock_print.assert_called_with("Schema 'raw' created or already exists.")
    
    # Test Error is handled properly and error message is shown
    @patch('backend.data_ingestion.api_fetch.engine')
    def test_create_schema_error(self, mock_engine):
        """Test that the function handles errors gracefully"""
        # Make the connection raise an error
        mock_engine.begin.return_value.__enter__.side_effect = SQLAlchemyError("Database error")
        
        # Call the function and check the error is printed
        with patch('builtins.print') as mock_print:
            create_schema()
            mock_print.assert_called_once()
            # Check that the error message starts correctly
            call_args = mock_print.call_args[0][0]
            self.assertTrue(call_args.startswith("Error creating schema 'raw':"))

if __name__ == '__main__':
    unittest.main()