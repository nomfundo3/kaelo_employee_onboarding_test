from odoo import models, fields, api
from odoo.exceptions import UserError
import csv
import io
import base64
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class EmployeeOnboardingImport(models.TransientModel):
    _name = 'employee.onboarding.import'
    _description = 'Employee Onboarding Import Wizard'

    file_upload = fields.Binary(
        string='CSV File',
        required=True,
        help='Upload CSV file with employee data'
    )
    filename = fields.Char(
        string='Filename'
    )
    
    def action_import(self):
        """Import employee data from CSV file"""
        if not self.file_upload:
            raise UserError("Please upload a CSV file.")
        
        # Decode the file
        try:
            file_content = base64.b64decode(self.file_upload).decode('utf-8')
        except Exception as e:
            raise UserError(f"Error reading file: {str(e)}")
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(file_content))
        
        success_count = 0
        error_count = 0
        errors = []
        duplicate_employee_numbers = set()
        
        # First pass: check for duplicate employee numbers in CSV
        file_content_copy = base64.b64decode(self.file_upload).decode('utf-8')
        csv_reader_check = csv.DictReader(io.StringIO(file_content_copy))
        employee_numbers_in_csv = []
        
        for row in csv_reader_check:
            emp_num = row.get('employee_number', '').strip()
            if emp_num:
                if emp_num in employee_numbers_in_csv:
                    duplicate_employee_numbers.add(emp_num)
                else:
                    employee_numbers_in_csv.append(emp_num)
        
        # Second pass: process rows
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
            try:
                # Extract and clean data
                full_name = row.get('full_name', '').strip()
                id_number = row.get('id_number', '').strip()
                date_of_birth_str = row.get('date_of_birth', '').strip()
                employee_number = row.get('employee_number', '').strip()
                email = row.get('email', '').strip()
                
                # Validation
                validation_errors = []
                
                # Check required fields
                if not full_name:
                    validation_errors.append("Full Name is required")
                if not id_number:
                    validation_errors.append("ID Number is required")
                if not date_of_birth_str:
                    validation_errors.append("Date of Birth is required")
                if not employee_number:
                    validation_errors.append("Employee Number is required")
                
                # Check for duplicates in CSV
                if employee_number in duplicate_employee_numbers:
                    validation_errors.append(f"Duplicate Employee Number in CSV: {employee_number}")
                
                # Check for existing employee number in database
                if employee_number:
                    existing = self.env['employee.onboarding'].search([
                        ('employee_number', '=', employee_number)
                    ])
                    if existing:
                        validation_errors.append(f"Employee Number already exists in database: {employee_number}")
                
                # Parse and validate date of birth
                date_of_birth = None
                if date_of_birth_str:
                    try:
                        # Try DD/MM/YYYY format
                        date_of_birth = datetime.strptime(date_of_birth_str, '%d/%m/%Y').date()
                        
                        # Check if date is not in the future
                        today = fields.Date.today()
                        if date_of_birth > today:
                            validation_errors.append("Date of Birth cannot be in the future")
                        
                        # Check age (at least 16 years old)
                        age = today.year - date_of_birth.year
                        if age < 16:
                            validation_errors.append("Employee must be at least 16 years old")
                            
                    except ValueError:
                        validation_errors.append("Invalid Date of Birth format. Use DD/MM/YYYY")
                
                # Validate email format if provided
                if email:
                    import re
                    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_regex, email):
                        validation_errors.append("Invalid email format")
                
                # If there are validation errors, skip this row
                if validation_errors:
                    error_count += 1
                    error_msg = f"Row {row_num}: {', '.join(validation_errors)}"
                    errors.append(error_msg)
                    _logger.warning(error_msg)
                    continue
                
                # Create employee onboarding record
                vals = {
                    'full_name': full_name,
                    'id_number': id_number,
                    'date_of_birth': date_of_birth,
                    'employee_number': employee_number,
                    'email': email or False,
                }
                
                self.env['employee.onboarding'].create(vals)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                error_msg = f"Row {row_num}: Unexpected error - {str(e)}"
                errors.append(error_msg)
                _logger.error(error_msg)
        
        summary = f"Import completed!\n"
        summary += f"✅ Successfully imported: {success_count} records\n"
        summary += f"❌ Failed to import: {error_count} records\n"
        
        if errors:
            summary += f"\nErrors:\n"
            for error in errors[:10]:  # Show first 10 errors
                summary += f"• {error}\n"
            if len(errors) > 10:
                summary += f"... and {len(errors) - 10} more errors"
        
        _logger.info(summary)
        
        # Show summary to user
        if error_count > 0:
            raise UserError(summary)
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Import Successful!',
                    'message': f'Successfully imported {success_count} employee records.',
                    'type': 'success',
                    'sticky': False,
                }
            }
