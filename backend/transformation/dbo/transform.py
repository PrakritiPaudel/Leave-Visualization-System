from backend.transformation.dbo.employee import populate_employee_data
from backend.transformation.dbo.department import populate_department_data
from backend.transformation.dbo.designation import populate_designation_data
from backend.transformation.dbo.allocation import populate_allocation_data
from backend.transformation.dbo.fiscal import populate_fiscal_data
from backend.transformation.dbo.leave_type import populate_leave_type_data 
from backend.transformation.dbo.leave import populate_leave_data

def transform_data():
    populate_employee_data()
    populate_designation_data()
    populate_department_data()
    populate_allocation_data()
    populate_fiscal_data()
    populate_leave_type_data()
    populate_leave_data()
    
    print("Data transformed and inserted into dbo tables successfully.")
