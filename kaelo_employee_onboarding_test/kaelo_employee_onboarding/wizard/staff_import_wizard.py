import base64, csv, io
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StaffImportWizard(models.TransientModel):
    _name = 'employee.onboarding.import'
    _description = 'Import Employee Onboarding'

    csv_file = fields.Binary('CSV File', required=True)
    filename = fields.Char('Filename')

    def action_import(self):
        data = base64.b64decode(self.csv_file or b'')
        f = io.StringIO(data.decode('utf-8'))
        reader = csv.DictReader(f)
        errors = []
        created = 0
        # complete this import and handling
    import base64, csv, io
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StaffImportWizard(models.TransientModel):
    _name = 'employee.onboarding.import'
    _description = 'Import Employee Onboarding'

    csv_file = fields.Binary('CSV File', required=True)
    filename = fields.Char('Filename')

    def action_import(self):
        data = base64.b64decode(self.csv_file or b'')
        f = io.StringIO(data.decode('utf-8'))
        reader = csv.DictReader(f)
        errors = []
        created = 0
        # complete this import and handling
     # Collect existing employee_numbers to detect duplicates
        existing_numbers = set(
            self.env['employee.onboarding'].search([]).mapped('employee_number')
        )

        for i, row in enumerate(reader, start=2):  # line 2 includes header
            full_name = (row.get('full_name') or '').strip()
            id_number = (row.get('id_number') or '').strip()
            dob_str = (row.get('date_of_birth') or '').strip()
            employee_number = (row.get('employee_number') or '').strip()
            email = (row.get('email') or '').strip()

            # Validate required fields
            if not full_name:
                errors.append(f"Row {i}: Missing full_name.")
                continue
            if not id_number:
                errors.append(f"Row {i}: Missing id_number.")
                continue
            if not dob_str:
                errors.append(f"Row {i}: Missing date_of_birth.")
                continue

            # Validate and parse date
            try:
                dob = datetime.strptime(dob_str, '%d/%m/%Y').date()
                if dob > datetime.today().date():
                    raise ValueError("Future date")
            except Exception:
                errors.append(f"Row {i}: Invalid date_of_birth '{dob_str}'.")
                continue

            # Check for duplicate employee_number
            if employee_number in existing_numbers:
                errors.append(f"Row {i}: Duplicate employee_number '{employee_number}'.")
                continue

            # Create the onboarding record
            self.env['employee.onboarding'].create({
                'full_name': full_name,
                'id_number': id_number,
                'date_of_birth': dob,
                'employee_number': employee_number,
                'email': email,
            })
            created += 1
            existing_numbers.add(employee_number)

        # Summary
        summary = f"{created} record(s) successfully imported."
        if errors:
            summary += "\n\nErrors:\n" + "\n".join(errors)
            raise UserError(summary)


        
