from odoo import models, fields, api, tools as tl
import xmlrpc.client
import os
import json
import logging
import datetime
import psycopg2
_logger = logging.getLogger(__name__)



class DbMigrateJobs(models.Model):
    _inherit = "hr.job"
    old_id = fields.Integer(string='id before migration')
    old_department_id = fields.Integer(string='old department_id hr.department')
    old_address_id = fields.Integer(string='old address_id res.partner')
    old_user_id = fields.Integer(string='old user_id res.users')
    old_allias_id = fields.Integer(string='old allias_id mail.alias')
    old_company_id = fields.Integer(string='old company id res.company')
    old_manager_id = fields.Integer(string='old manager_id hr_employee')
    old_hr_responsible_id = fields.Integer(string='old responsible user res_users')

class DbMigrateState(models.Model):
    _inherit = "hr.recruitment.stage"
    old_id = fields.Integer(string="id before migration")
    old_job_id = fields.Integer(string='old job id hr.job')


class DbMigrateDepartment(models.Model):
    _inherit = "hr.department"
    old_id = fields.Integer(string="id before migration")
    old_company_id = fields.Integer(string='old company id res.company')
    old_manager_id = fields.Integer(string='old manager_id hr_employee')


class DbMigrateCompany(models.Model):
    _inherit = "res.company"
    old_id = fields.Integer(string='id before migration')
    old_partner_id = fields.Integer(string='old partner id res.partner')
    old_parent_id = fields.Integer(string='old parent id res.company')


class DdMigrateEmployee(models.Model):
    _inherit = 'hr.employee'
    old_id = fields.Integer(string='id before migration')
    old_user_id = fields.Integer(string='old user_id res.users')
    old_company_id = fields.Integer(string='old company id res.company')
    old_address_home_id = fields.Integer(string='old address home id res.partner')
    old_address_id = fields.Integer(string='old address id res.partner')
    old_parent_id = fields.Integer(string='old parent id hr.employee')
    old_coach_id = fields.Integer(string='old coach_id hr.employee')


class DbMigrateHrApplicantLanguage(models.Model):
    _inherit = 'hr.applicant.language'
    old_id = fields.Integer(string='id before migration')


class DbMigrateHrApplicantExperience(models.Model):
    _inherit = 'hr.applicant.experience'
    old_id = fields.Integer(string='id before migration')


class DbMigrateHrApplicantEducation(models.Model):
    _inherit = 'hr.applicant.education'
    old_id = fields.Integer(string='id before migration')


class DbMigrateHrApplicantCategory(models.Model):
    _inherit = 'hr.applicant.category'
    old_id = fields.Integer(string='id before migration')

class DbMigrate(models.Model):
    _inherit = "hr.applicant"
    old_id = fields.Integer(string='id before migration')
    old_partner_id = fields.Integer(string='partner id before migration res.partner')
    old_stage_id = fields.Integer(string='old stage id before migration hr.recruitment.stage')
    old_user_id = fields.Integer(string='old user id before migration 	res.users')
    old_job_id = fields.Integer(string='old job id hr.job')
    old_company_id = fields.Integer(string='old company id res.company')
    old_department_id = fields.Integer(string='old department id hr_department')
    old_emp_id = fields.Integer(string='old emp_id hr_employee')

    def new_hr_applicant_migrate(self):
        try:
            _logger.info("APPLICANTS MIGRATE")
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            _logger.info(f"You are connected to -  {record}")

            cursor.execute("Select * FROM hr_applicant LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            # print(colnames)
            query = '''SELECT * FROM hr_applicant; '''
            cursor.execute(query)
            records_applicants = cursor.fetchall()

            connection2 = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                           password=cli_commands.get('local_odoo_db_password'),
                                           host="172.19.0.2",
                                           port="5432",
                                           database="v14-empty")

            cursor2 = connection2.cursor()
            cursor2.execute("Select * FROM hr_applicant LIMIT 0")
            list_fields_v14 = [desc[0] for desc in cursor2.description]
            for record in records_applicants:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'partner_id':
                        data['old_partner_id'] = record[i]
                        data['partner_id'] = 1
                    elif colnames[i] == 'stage_id':
                        data['old_stage_id'] = record[i]
                    elif colnames[i] == 'user_id':
                        data['old_user_id'] = record[i]
                    elif colnames[i] == 'job_id':
                        data['old_job_id'] = record[i]
                    elif colnames[i] == 'company_id':
                        companies = self.env['res.company'].sudo().search([('old_id', '=', record[i])])
                        if companies:
                            for company in companies:
                                data['company_id'] = company.id
                    elif colnames[i] == 'department_id':
                        data['old_department_id'] = record[i]
                    elif colnames[i] == 'emp_id':
                        data['old_emp_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]

                for key in list(data):
                    if key not in list_fields_v14:
                        data.pop(key)
                data.pop('last_stage_id')
                data.pop('message_main_attachment_id')
                data.pop('source_id')
                data.pop('campaign_id')
                data.pop('medium_id')
                _logger.info(f"DATATA E {data}")
                try:
                    _logger.info("CREATE")
                    self.env['hr.applicant'].sudo().create(data)
                except (Exception, psycopg2.Error) as error:
                    _logger.info(f"Error while creating a attachment {error}")
                    _logger.info("\n")
                    _logger.info("\n")
                _logger.info("\n")
                _logger.info("\n")

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def new_hr_applicant_language_migrate(self):
        try:
            _logger.info("LANGUAGE MIGRATE")
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            print("You are connected to - ", record, "\n")

            cursor.execute("Select * FROM hr_applicant_language LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM hr_applicant_language; '''
            cursor.execute(query)
            records_applicants = cursor.fetchall()
            print(len(records_applicants))
            applicants = self.env['hr.applicant'].sudo().search([])
            for record in records_applicants:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'applicant_id':
                        for applicant in applicants:
                            if applicant.old_id == record[i]:
                                data['applicant_id'] = applicant.id
                    else:
                        data[colnames[i]] = record[i]
                # for pair in data.items():
                #    print(pair)
                _logger.info(f"{data}")
                try:
                    self.env['hr.applicant.language'].sudo().create(data)
                except (Exception, psycopg2.Error) as error:
                    _logger.info(f"Error while creating a language {error}")
                    continue
                    _logger.info("\n")
                    _logger.info("\n")
                _logger.info("\n")
                _logger.info("\n")
        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def new_hr_applicant_experience_migrate(self):
        try:
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            print("You are connected to - ", record, "\n")

            cursor.execute("Select * FROM hr_applicant_experience LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM hr_applicant_experience; '''
            cursor.execute(query)
            records_applicants = cursor.fetchall()
            print(len(records_applicants))
            applicants = self.env['hr.applicant'].sudo().search([])
            for record in records_applicants:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'applicant_id':
                        for applicant in applicants:
                            if applicant.old_id == record[i]:
                                data['applicant_id'] = applicant.id
                    else:
                        data[colnames[i]] = record[i]
                # for pair in data.items():
                #    print(pair)
                try:
                    self.env['hr.applicant.experience'].sudo().create(data)
                except (Exception, psycopg2.Error) as error:
                    _logger.info(f"Error while creating a experience {error}")
                    _logger.info("\n")
                    _logger.info("\n")

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def new_hr_applicant_education_migrate(self):
        try:
            _logger.info("EDUCATION MIGRATE")
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            print("You are connected to - ", record, "\n")

            cursor.execute("Select * FROM hr_applicant_education LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM hr_applicant_education; '''
            cursor.execute(query)
            records_applicants = cursor.fetchall()
            print(len(records_applicants))
            applicants = self.env['hr.applicant'].sudo().search([])
            for record in records_applicants:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'applicant_id':
                        for applicant in applicants:
                            if applicant.old_id == record[i]:
                                data['applicant_id'] = applicant.id
                    else:
                        data[colnames[i]] = record[i]
                # for pair in data.items():
                #    print(pair)
                _logger.info(f"{data}")
                try:
                    self.env['hr.applicant.education'].sudo().create(data)
                except (Exception, psycopg2.Error) as error:
                    _logger.info(f"Error while creating a experience {error}")
                    _logger.info("\n")
                    _logger.info("\n")

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def new_hr_applicant_category_migrate(self):
        try:
            _logger.info("CATEGORY MIGRATE")
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            print("You are connected to - ", record, "\n")

            cursor.execute("Select * FROM hr_applicant_category LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM hr_applicant_category; '''
            cursor.execute(query)
            records_applicants = cursor.fetchall()
            print(len(records_applicants))

            for record in records_applicants:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    data[colnames[i]] = record[i]
                _logger.info({f"{data}"})
                categories = self.env['hr.applicant.category'].sudo().search([])
                flag = 0
                for category in categories:
                    if category.name == data['name']:
                        flag += 1
                        category.write({
                            'old_id': data['old_id'],
                        })
                if flag == 0:
                    print(data['name'])
                    self.env['hr.applicant.category'].sudo().create(data)
        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")
        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def new_update_relation_applicant_category(self):
        _logger.info("UPDATE APPLICANT CATEGORY")
        applicants = self.env['hr.applicant'].sudo().search([])
        categories = self.env['hr.applicant.category'].sudo().search([])
        try:
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            print("You are connected to - ", record, "\n")

            cursor.execute("Select * FROM hr_applicant_hr_applicant_category_rel LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM hr_applicant_hr_applicant_category_rel; '''
            cursor.execute(query)
            records_applicants = cursor.fetchall()
            print(len(records_applicants))

            connection1 = psycopg2.connect(user="odoo",
                                           password="odoo",
                                           host="172.19.0.2",
                                           port="5432",
                                           database="v14-empty")

            cursor1 = connection1.cursor()
            cursor1.execute("SELECT version();")
            record1 = cursor1.fetchone()
            query = '''SELECT * FROM hr_applicant_hr_applicant_category_rel; '''
            cursor1.execute(query)
            records_in_relation = cursor1.fetchall()
            _logger.info(f"You are connected to - {connection1.get_dsn_parameters()}")
            for record in records_applicants:
                data = {}
                for i in range(len(colnames)):
                    if colnames[i] == 'hr_applicant_id':
                        for applicant in applicants:
                            if applicant.old_id == record[i]:
                                data['hr_applicant_id'] = applicant.id
                    if colnames[i] == 'hr_applicant_category_id':
                        for category in categories:
                            if category.old_id == record[i]:
                                data['hr_applicant_category_id'] = category.id

                if 'hr_applicant_id' in data and 'hr_applicant_category_id' in data:
                    tuple = (data['hr_applicant_id'], data['hr_applicant_category_id'])
                    if tuple not in records_in_relation:
                        _logger.info(f"{tuple}")
                        query1 = f"INSERT INTO hr_applicant_hr_applicant_category_rel(hr_applicant_id, hr_applicant_category_id) VALUES({data['hr_applicant_id']},{data['hr_applicant_category_id']});"
                        # print(query1)
                        cursor1.execute(query1)
                        connection1.commit()


        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                # cursor1.close()
                # connection1.close()
                _logger.info("PostgreSQL connection is closed")

    def new_hr_job_migrate(self):
        try:
            _logger.info("JOB MIGRATE")
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            print("You are connected to - ", record, "\n")

            cursor.execute("Select * FROM hr_job LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query_job = '''SELECT * FROM hr_job; '''
            cursor.execute(query_job)
            records_jobs = cursor.fetchall()
            for job in records_jobs:
                _logger.info(f"{job}")
                data_job = {}
                data_job['old_id'] = job[0]
                for i in range(1, len(colnames)):
                    # print(f'{colnames[i]} : {job[i]}')
                    if colnames[i] == 'department_id':
                        data_job['old_department_id'] = job[i]
                    elif colnames[i] == 'address_id':
                        data_job['old_address_id'] = job[i]
                    elif colnames[i] == 'user_id':
                        data_job['old_user_id'] = job[i]
                    elif colnames[i] == 'alias_id':
                        data_job['old_allias_id'] = job[i]
                    elif colnames[i] == 'company_id':
                        companies = self.env['res.company'].sudo().search([('old_id', '=', job[i])])
                        if companies:
                            for company in companies:
                                data_job['company_id'] = company.id
                    elif colnames[i] == 'manager_id':
                        data_job['old_manager_id'] = job[i]
                    elif colnames[i] == 'hr_responsible_id':
                        data_job['old_hr_responsible_id'] = job[i]
                    else:
                        data_job[colnames[i]] = job[i]
                data_job.pop('message_last_post')
                job = self.env['hr.job'].sudo().search([('name', "ilike", data_job['name'])])
                _logger.info(f"{data_job}")
                if job:
                    job.write({
                        'old_id': data_job['old_id']
                    })
                    _logger.info("POSTOI VAKVA RABOTA")
                else:
                    self.env['hr.job'].sudo().create(data_job)
                    _logger.info("\n")
                    _logger.info("\n")


        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info(f"PostgreSQL connection is closed")

    def new_hr_department_migrate(self):
        try:
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            print("You are connected to - ", record, "\n")

            cursor.execute("Select * FROM hr_department LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM hr_department; '''
            cursor.execute(query)
            records_applicants = cursor.fetchall()
            companies = self.env['res.company'].sudo().search([])
            departments = self.env['hr.department'].sudo().search([])
            _logger.info(f"{len(records_applicants)}")
            for record in records_applicants:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'company_id':
                        for company in companies:
                            if record[i] == company.old_id:
                                data[colnames[i]] = company.id
                    elif colnames[i] == 'manager_id':
                        data['old_manager_id'] = record[i]
                        # data['manager_id'] = 1
                    else:
                        data[colnames[i]] = record[i]
                data.pop('message_last_post')
                flag = 0
                for department in departments:
                    if department.name == data['name']:
                        department.write({'old_id': data['old_id']})
                        flag += 1
                if flag == 0:
                    _logger.info(f"Department name: {data['name']}")
                    self.env['hr.department'].create(data)

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")

    def new_update_department_db(self):
        departments = self.env['hr.department'].sudo().search([])
        companies = self.env['res.company'].sudo().search([])
        employees = self.env['hr.employee'].sudo().search([])
        print(len(departments))
        print(len(companies))
        for dep in departments:
            for emp in employees:
                if dep.old_manager_id == emp.old_id:
                    dep.write({'manager_id': emp.id})

    def new_hr_employee_migrate(self):
        try:
            _logger.info("EMPLOYEE MIGRATE")
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            _logger.info(f"You are connected to -  {record}")

            cursor.execute("Select * FROM hr_employee LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            # print(colnames)
            query = '''SELECT * FROM hr_employee; '''
            cursor.execute(query)
            records = cursor.fetchall()
            companies = self.env['res.company'].sudo().search([])
            departments = self.env['hr.department'].sudo().search([])
            jobs = self.env['hr.job'].search([])
            employees = self.env['hr.employee'].sudo().search([])
            connection2 = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                           password=cli_commands.get('local_odoo_db_password'),
                                           host="172.19.0.2",
                                           port="5432",
                                           database="v14-empty")

            cursor2 = connection2.cursor()
            cursor2.execute("Select * FROM hr_employee LIMIT 0")
            list_fields_v14 = [desc[0] for desc in cursor2.description]
            # _logger.info(f"FILDOVI VO 14ka{list_fields_v14}")
            for record in records:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'company_id':
                        for company in companies:
                            if company.old_id == record[i]:
                                data['company_id'] = company.id
                    elif colnames[i] == 'address_home_id':
                        data['old_address_home_id'] = record[i]
                    elif colnames[i] == 'address_id':
                        data['old_address_id'] = record[i]
                    elif colnames[i] == 'parent_id':
                        data['old_parent_id'] = record[i]
                    elif colnames[i] == 'department_id':
                        for dep in departments:
                            if dep.old_id == record[i]:
                                data['department_id'] = dep.id
                    elif colnames[i] == 'job_id':
                        for job in jobs:
                            if job.old_id == record[i]:
                                data['job_id'] = job.id
                    elif colnames[i] == 'coach_id':
                        data['old_coach_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]
                for key in list(data):
                    if key not in list_fields_v14:
                        data.pop(key)
                data['resource_id'] = 1
                data.pop('resource_calendar_id')
                _logger.info(f"DATATA E {data}")
                _logger.info(f"{data['name']}")
                self.env['hr.employee'].sudo().create(data)
                _logger.info("\n")
                _logger.info("\n")

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def new_hr_stage_migrate(self):
        try:
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            print("You are connected to - ", record, "\n")

            cursor.execute("Select * FROM hr_recruitment_stage LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM hr_recruitment_stage; '''
            cursor.execute(query)
            records_applicants = cursor.fetchall()
            print(len(records_applicants))
            jobs = self.env['hr.job'].sudo().search([])
            for record in records_applicants:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'job_id':
                        for job in jobs:
                            if job.old_id == record[i]:
                                data['job_ids'] = [job.id]
                    else:
                        data[colnames[i]] = record[i]
                # self.env['hr.recruitment.stage'].create(data)
                stage = self.env['hr.recruitment.stage'].sudo().search([('name', 'ilike', data['name'])])
                if stage:
                    stage.write({
                        'old_id': data['old_id']
                    })
                    _logger.info("postoi")
                else:
                    self.env['hr.recruitment.stage'].sudo().create(data)

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def new_update_stage(self):
        stages = self.env['hr.recruitment.stage'].sudo().search([])
        jobs = self.env['hr.job'].sudo().search([])
        print(len(stages))
        print(len(jobs))
        for stage in stages:
            for job in jobs:
                if stage.old_job_id == job.old_id:
                    # print(f'Department: {dep.name}, Company: {com.name}')
                    stage.write({'job_ids': [job.id]})

    def new_update_hr_applicant_db(self):
        applicants = self.env['hr.applicant'].sudo().search([])
        jobs = self.env['hr.job'].sudo().search([])
        departments = self.env['hr.department'].sudo().search([])
        companies = self.env['res.company'].sudo().search([])
        stages = self.env['hr.recruitment.stage'].sudo().search([])
        print(len(applicants))
        for applicant in applicants:
            for dep in departments:
                if applicant.old_department_id == dep.old_id and applicant.old_department_id > 1:
                    applicant.sudo().write({'department_id': dep.id})
            for com in companies:
                if applicant.old_company_id == com.old_id and applicant.old_company_id > 1:
                    applicant.sudo().write({'company_id': com.id})
            for job in jobs:
                if applicant.old_job_id == job.old_id and applicant.old_job_id > 1:
                    applicant.sudo().write({'job_id': job.id})
            for stage in stages:
                if applicant.old_stage_id == stage.old_id:
                    applicant.sudo().write({'stage_id': stage.id})

    def new_hr_applicants_creation_in_res_partner(self):
        _logger.info("DALI RABOTI")
        applicants = self.env['hr.applicant'].sudo().search([])
        data = {}
        for applicant in applicants:
            if type(applicant.partner_name) is str:
                applicant_name = applicant.partner_name.strip()
                applicant_name = applicant_name.replace("  ", " ")
                exist = self.env['res.partner'].sudo().search([('name', "ilike", applicant_name)])
                _logger.info("NOV REKORD")
                if not exist:
                    _logger.info(f"{applicant_name}")
                    _logger.info('not exist')
                    data['name'] = applicant_name
                    data['email'] = applicant.email_from
                    if data['name'] != '' and data['name'] != False:
                        _logger.info("VREDNOSTITE VO DATA SE")
                        _logger.info(f"{data}")
                        new_partner = self.env['res.partner'].sudo().create(data)
                        _logger.info('novo kreiran partner')
                        _logger.info(f'{new_partner}')
                        applicant.write({'partner_id': new_partner.id})
                else:
                    _logger.info(f"{applicant_name}")
                    _logger.info('exist')
                    for partner in exist:
                        applicant.write({'partner_id': partner.id})
                        break
                data = {}

    def new_followers_update_for_applicant_messages(self):
        try:
            _logger.info("FOLLOWERS UPDATE")
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            _logger.info(f"You are connected to -  {record}")

            cursor.execute("Select * FROM mail_followers LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            # print(colnames)
            query = '''SELECT * FROM mail_followers where res_model='hr.applicant'; '''
            cursor.execute(query)
            records_followers = cursor.fetchall()
            for record in records_followers:
                data={}
                for i in range(1, len(colnames)):
                    if colnames[i] == 'partner_id':
                        partners = self.env['res.partner'].sudo().search([('old_id','=',record[i])])
                        if partners:
                            for partner in partners:
                                _logger.info(f"partner id e {partner.id}, a ime mu e {partner.name}")
                                data['partner_id'] = partner.id
                                break
                    elif colnames[i] == 'res_model':
                        data['res_model'] = record[i]
                    elif colnames[i] == 'res_id':
                        _logger.info(f"res_id = old_id {record[i]}")
                        applicants = self.env['hr.applicant'].sudo().search([('old_id','=',record[i])])
                        _logger.info(f"{applicants}")
                        if applicants:
                            for applicant in applicants:
                                _logger.info(f"applicant id e {applicant.id}, a ime mu e {applicant.partner_name}")
                                data['res_id'] = applicant.id
                                break
                    else:
                        data[colnames[i]] = record[i]

                #DA SE KREIRA
                _logger.info(f"{data}")
                if 'partner_id' in data:
                    _logger.info("ima partner_id")
                    self.env['mail.followers'].sudo().create(data)
                _logger.info("\n")
                _logger.info("\n")


        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")