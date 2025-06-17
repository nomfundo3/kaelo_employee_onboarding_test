from odoo import api, fields, models

class EmployeeOnboarding(models.Model):
    _name = 'employee.onboarding'
    _description = 'Employee Onboarding'

    _rec_name = 'full_name'
    _order = 'create_date desc'

    full_name = fields.Char(
        string='Full Name',
        required=True,
        help='Employee full name'
    )
    id_number = fields.Char(
        string='ID Number',
        required=True,
        help='Employee identification number'
    )
    date_of_birth = fields.Date(
        string='Date of Birth',
        required=True,
        help='Employee date of birth'
    )
    employee_number = fields.Char(
        string='Employee Number',
        required=True,
        help='Unique employee number'
    )
    email = fields.Char(
        string='Email Address',
        help='Employee email address'
    )
    
    @api.constrains('employee_number')
    def _check_unique_employee_number(self):
        for record in self:
            if record.employee_number:
                existing = self.search([
                    ('employee_number', '=', record.employee_number),
                    ('id', '!=', record.id)
                ])
                if existing:
                    raise ValidationError(
                        f"Employee number '{record.employee_number}' already exists!"
                    )
    
    @api.constrains('email')
    def _check_email_format(self):
        for record in self:
            if record.email:
                email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_regex, record.email):
                    raise ValidationError(
                        f"Invalid email format: {record.email}"
                    )
    
    @api.constrains('date_of_birth')
    def _check_date_of_birth(self):
        for record in self:
            if record.date_of_birth:
                today = fields.Date.today()
                if record.date_of_birth > today:
                    raise ValidationError(
                        "Date of birth cannot be in the future!"
                    )
                # Check if person is at least 16 years old
                age = today.year - record.date_of_birth.year
                if age < 16:
                    raise ValidationError(
                        "Employee must be at least 16 years old!"
                    )

    # create a view,action and menu for this model as well
