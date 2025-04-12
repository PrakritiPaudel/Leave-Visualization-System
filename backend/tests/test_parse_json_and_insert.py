# Sample api data 
# insert to db mock
# df nested and df main expected structure ma ako cha ki nai check 
# such that database ma correctly write vako hoss.

import pytest
import pandas as pd
import json
from unittest.mock import patch

# # Mock the database insert function
# def test_parse_json_and_insert():
#     # Sample API data with nested 'allocations'
#         api_data = "{\n  \"data\": [\n    {\n      \"id\": 1778,\n      \"userId\": 507,\n      \"empId\": \"343423\",\n      \"teamManagerId\": null,\n      \"designationId\": 71,\n      \"designationName\": \"Engineering Manager\",\n      \"firstName\": \"Prakash\",\n      \"middleName\": \"Kiran\",\n      \"lastName\": \"RajBhandari\",\n      \"email\": \"prakashbhandari@lftechnology.com\",\n      \"isHr\": false,\n      \"isSupervisor\": false,\n      \"leaveIssuerId\": 405,\n      \"issuerFirstName\": \"Lorene\",\n      \"issuerMiddleName\": null,\n      \"issuerLastName\": \"Rawcliffe\",\n      \"currentLeaveIssuerId\": 427,\n      \"currentLeaveIssuerEmail\": \"anishsilwal@lftechnology.com\",\n      \"departmentDescription\": \"Engineering\",\n      \"startDate\": \"2021-08-03\",\n      \"endDate\": \"2021-08-07\",\n      \"leaveDays\": 4,\n      \"reason\": \"Lorem ipsum dolor sit amet consectetur adipiscing elit, mauris porttitor dictum justo suspendisse gravida, molestie luctus congue potenti libero aliquet. Praesent enim ullamcorper penatibus facilisis faucibus feugiat neque, diam volutpat lectus fringilla tellus dictumst felis sociosqu, pretium nam mus cras nunc fermentum. Laoreet cum enim sagittis lacus sollicitudin fames justo leo, suspendisse nibh per aliquet class quis pretium nisl pulvinar, a fringilla pellentesque penatibus velit nisi ante. Ac varius viverra eget justo duis posuere lacus, velit ornare nullam sociis litora orci, tellus venenatis condimentum tempor cursus luctus. Integer aenean cursus inceptos faucibus sagittis feugiat sodales ut tincidunt, netus lacus tristique sem eget phasellus cubilia posuere. Urna laoreet euismod sed blandit faucibus viverra vel cras iaculis, eros lacinia felis hendrerit himenaeos enim mus rutrum, pretium condimentum at et non fermentum feugiat lacus. Eget imperdiet est ultricies curabitur litora erat a varius pulvinar placerat neque sociosqu, nulla diam platea dictumst nibh porta nullam lacinia mattis lacus.\",\n      \"leaveStatus\": \"APPROVED\",\n      \"status\": \"APPROVED\",\n      \"responseRemarks\": null,\n      \"leaveTypeId\": 11,\n      \"leaveType\": \"Leave Without Pay\",\n      \"defaultDays\": 0,\n      \"transferableDays\": 0,\n      \"isConsecutive\": 0,\n      \"fiscalId\": 99,\n      \"fiscalStartDate\": \"2021-07-14T00:00:00.000Z\",\n      \"fiscalEndDate\": \"2022-07-16T00:00:00.000Z\",\n      \"fiscalIsCurrent\": false,\n      \"createdAt\": \"2021-08-19T11:31:22.000Z\",\n      \"updatedAt\": \"2021-09-28T10:28:04.000Z\",\n      \"isAutomated\": 0,\n      \"isConverted\": 0,\n      \"totalCount\": 150333,\n      \"allocations\": null\n    },\n    {\n      \"id\": 1780,\n      \"userId\": 518,\n      \"empId\": \"777\",\n      \"teamManagerId\": null,\n      \"designationId\": 9,\n      \"designationName\": \"Development Manager\",\n      \"firstName\": \"Kritish \",\n      \"middleName\": null,\n      \"lastName\": \"Dhaubanjar\",\n      \"email\": \"kritishdhaubanjar@lftechnology.com\",\n      \"isHr\": false,\n      \"isSupervisor\": false,\n      \"leaveIssuerId\": 410,\n      \"issuerFirstName\": \"jjjj\",\n      \"issuerMiddleName\": \"Jyo\",\n      \"issuerLastName\": \"Shrestha\",\n      \"currentLeaveIssuerId\": 400,\n      \"currentLeaveIssuerEmail\": \"kailashraj@lftechnology.com\",\n      \"departmentDescription\": \"Engineering\",\n      \"startDate\": \"2021-08-19\",\n      \"endDate\": \"2021-08-19\",\n      \"leaveDays\": 1,\n      \"reason\": \"ok ok\",\n      \"leaveStatus\": \"APPROVED\",\n      \"status\": \"APPROVED\",\n      \"responseRemarks\": null,\n      \"leaveTypeId\": 11,\n      \"leaveType\": \"Leave Without Pay\",\n      \"defaultDays\": 0,\n      \"transferableDays\": 0,\n      \"isConsecutive\": 0,\n      \"fiscalId\": 99,\n      \"fiscalStartDate\": \"2021-07-14T00:00:00.000Z\",\n      \"fiscalEndDate\": \"2022-07-16T00:00:00.000Z\",\n      \"fiscalIsCurrent\": false,\n      \"createdAt\": \"2021-08-19T11:52:10.000Z\",\n      \"updatedAt\": \"2021-09-28T10:28:04.000Z\",\n      \"isAutomated\": 0,\n      \"isConverted\": 0,\n      \"totalCount\": 150333,\n      \"allocations\": [\n        {\n          \"id\": 903,\n          \"name\": \"test project test\",\n          \"type\": \"project\"\n        },\n        {\n          \"id\": 914,\n          \"name\": \"ABCD\",\n          \"type\": \"project\"\n        }\n      ]\n    }\n  ],\n  \"meta\": {\n    \"total\": 150333,\n    \"page\": 1,\n    \"size\": 2\n  }\n}"

#     # Expected main_data and nested_data after processing
#     expected_main_data = pd.DataFrame([
#         {
#             "empId": "E123",
#             "firstName": "John",
#             "lastName": "Doe",
#             "email": "john.doe@example.com",
#             "allocations": json.dumps([
#                 {"id": "A1", "name": "Project A", "type": "Full-time"},
#                 {"id": "A2", "name": "Project B", "type": "Part-time"}
#             ])
#         },
#         {
#             "empId": "E124",
#             "firstName": "Jane",
#             "lastName": "Smith",
#             "email": "jane.smith@example.com",
#             "allocations": json.dumps([
#                 {"id": "A3", "name": "Project C", "type": "Full-time"}
#             ])
#         }
#     ])

#     expected_nested_data = pd.DataFrame([
#         {"empId": "E123", "id": "A1", "name": "Project A", "type": "Full-time"},
#         {"empId": "E123", "id": "A2", "name": "Project B", "type": "Part-time"},
#         {"empId": "E124", "id": "A3", "name": "Project C", "type": "Full-time"}
#     ])

#     # Mock insert_data_to_db function
#     with patch('your_module.insert_data_to_db') as mock_insert:
#         # Call the function
#         parse_json_and_insert(api_data)

#         # Ensure insert_data_to_db is called twice: once for main_data and once for nested_data
#         assert mock_insert.call_count == 2

#         # Check the first call to insert_data_to_db (for 'api_data')
#         args_main = mock_insert.call_args_list[0][0]
#         pd.testing.assert_frame_equal(args_main[0], expected_main_data)
#         assert args_main[1] == 'api_data'
#         assert args_main[2] == 'raw'

#         # Check the second call to insert_data_to_db (for 'allocation_data')
#         args_nested = mock_insert.call_args_list[1][0]
#         pd.testing.assert_frame_equal(args_nested[0], expected_nested_data)
#         assert args_nested[1] == 'allocation_data'
#         assert args_nested[2] == 'raw'
