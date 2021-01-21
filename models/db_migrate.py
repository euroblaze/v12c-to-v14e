from odoo import models, fields, api, tools as tl
import xmlrpc.client
import os
import json
import logging
import datetime
import psycopg2
_logger = logging.getLogger(__name__)


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

    def test_db(self):
        applicants = self.env['hr.applicant'].sudo().search([])
        _logger.info('HERE HERE HERE HERE HERE HERE')
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
            _logger.info(f'{connection.get_dsn_parameters()}')
            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            print("You are connected to - ", record, "\n")
            _logger.info(f'You are connected to {record}')

            cursor.execute("Select * FROM res_company LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM hr_department LIMIT 5; '''
            companies = self.env['hr.employee'].sudo().search([])
            cursor.execute(query)
            _logger.info(f'{len(companies)}')
            records_applicants = cursor.fetchall()
            #for company in companies:
            #    _logger.info(f'{company.old_id}')
            cursor.close()
            connection.close()
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
            _logger.info(f'Error while connecting to PostgreSQL{error}')
            cursor.close()
            connection.close()

        #finally:
            # closing database connection.
        #    if (connection):
        #        cursor.close()
        #        connection.close()
        #        print("PostgreSQL connection is closed")



    #OVAA NAJPRVO KJE TREBA
    def applicant_db(self):
        try:
            connection = psycopg2.connect(user="leon",
                                          password="Janevski97@",
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

            cursor.execute("Select * FROM hr_applicant LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM hr_applicant; '''
            cursor.execute(query)
            records_applicants = cursor.fetchall()
            for record in records_applicants:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'partner_id':
                        data['old_partner_id'] = record[i]
                        data['partner_id'] = 1
                    elif colnames[i] == 'stage_id':
                        data['old_stage_id'] = record[i]
                        data['stage_id'] = 1
                    elif colnames[i] == 'user_id':
                        data['old_user_id'] = record[i]
                        data['user_id'] = 1
                    elif colnames[i] == 'job_id':
                        data['old_job_id'] = record[i]
                        data['job_id'] = 1
                    elif colnames[i] == 'company_id':
                        data['old_company_id'] = record[i]
                        data['company_id'] = 1
                    elif colnames[i] == 'department_id':
                        data['old_department_id'] = record[i]
                        data['department_id'] = 1
                    elif colnames[i] == 'emp_id':
                        data['old_emp_id'] = record[i]
                        data['emp_id'] = 1
                    else:
                        data[colnames[i]] = record[i]
                data.pop('message_last_post')
                data.pop('title_action')
                data.pop('date_action')
                data.pop('reference')
                data.pop('openupgrade_legacy_12_0_activity_date_deadline')
                data.pop('message_main_attachment_id')
                data.pop('source_id')
                data.pop('last_stage_id')
                data.pop('medium_id')
                data.pop('campaign_id')
                if data['partner_name']:
                    applicant_name = data['partner_name'].strip()
                    applicant_name = applicant_name.replace("  ", " ")
                    exist = self.env['hr.applicant'].sudo().search([('partner_name', "ilike", applicant_name)])
                    data['partner_name'] = applicant_name
                    if exist:
                        for e in exist:
                            _logger.info(f"ime mu e {e.partner_name} , a old_id e {e.old_id}")
                            e.write({
                                'old_id' : data['old_id']
                            })
                            _logger.info("POSTOI")
                    else:
                        _logger.info(f"imeto e {data['partner_name']}")
                        self.env['hr.applicant'].create(data)
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

    # I OVA KJE TREBA
    def update_hr_applicant_db(self):
        applicants = self.env['hr.applicant'].sudo().search([])
        jobs = self.env['hr.job'].sudo().search([])
        departments = self.env['hr.department'].sudo().search([])
        users = self.env['res.users'].sudo().search([])
        companies = self.env['res.company'].sudo().search([])
        stages = self.env['hr.recruitment.stage'].sudo().search([])

        print(len(applicants))
        for applicant in applicants:
            for dep in departments:
               if applicant.old_department_id == dep.old_id and applicant.old_department_id > 1:
                   applicant.sudo().write({'department_id': dep.id})
            for user in users:
               if applicant.old_user_id == user.old_id:
                   applicant.sudo().write({'user_id': user.id})
            for com in companies:
               if applicant.old_company_id == com.old_id and applicant.old_company_id > 1:
                   applicant.sudo().write({'company_id': com.id})
            for job in jobs:
               if applicant.old_job_id == job.old_id and applicant.old_job_id > 1 :
                   applicant.sudo().write({'job_id': job.id})
            for stage in stages:
               if applicant.old_stage_id == stage.old_id:
                   applicant.sudo().write({'stage_id': stage.id})

    def applicant_language(self):
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
                #for pair in data.items():
                #    print(pair)
                self.env['hr.applicant.language'].sudo().create(data)

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def applicant_experience(self):
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
                #for pair in data.items():
                #    print(pair)
                self.env['hr.applicant.experience'].sudo().create(data)

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")
    def applicant_education(self):
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
                #for pair in data.items():
                #    print(pair)
                self.env['hr.applicant.education'].sudo().create(data)

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")
    def applicant_category(self):
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
                categories = self.env['hr.applicant.category'].sudo().search([])
                flag = 0
                for category in categories:
                    if category.name == data['name']:
                        flag += 1
                        category.write({
                            'old_id' : data['old_id'],
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
    def update_relation_applicant_category(self):
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
                                           database="najnovaDB-sabota")

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
                    tuple = (data['hr_applicant_id'],data['hr_applicant_category_id'])
                    if tuple not in records_in_relation:
                        query1 = f"INSERT INTO hr_applicant_hr_applicant_category_rel(hr_applicant_id, hr_applicant_category_id) VALUES({data['hr_applicant_id']},{data['hr_applicant_category_id']});"
                        #print(query1)
                        cursor1.execute(query1)
                        connection1.commit()


        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                #cursor1.close()
                #connection1.close()
                _logger.info("PostgreSQL connection is closed")




    # DONE
    def job_db(self):
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

            cursor.execute("Select * FROM hr_job LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query_job = '''SELECT * FROM hr_job; '''
            cursor.execute(query_job)
            records_jobs = cursor.fetchall()
            for job in records_jobs:
                data_job = {}
                data_job['old_id'] = job[0]
                for i in range(1, len(colnames)):
                    # print(f'{colnames[i]} : {job[i]}')
                    if colnames[i] == 'department_id':
                        data_job['old_department_id'] = job[i]
                        data_job['department_id'] = 1
                    elif colnames[i] == 'address_id':
                        data_job['old_address_id'] = job[i]
                        data_job['address_id'] = 1
                    elif colnames[i] == 'user_id':
                        data_job['old_user_id'] = job[i]
                        data_job['user_id'] = 1
                    elif colnames[i] == 'alias_id':
                        data_job['old_allias_id'] = job[i]
                        data_job['alias_id'] = 1
                    elif colnames[i] == 'company_id':
                        data_job['old_company_id'] = job[i]
                        data_job['company_id'] = 1
                    elif colnames[i] == 'manager_id':
                        data_job['old_manager_id'] = job[i]
                        data_job['manager_id'] = 1
                    elif colnames[i] == 'hr_responsible_id':
                        data_job['old_hr_responsible_id'] = job[i]
                        data_job['hr_responsible_id'] = 1
                    else:
                        data_job[colnames[i]] = job[i]
                data_job.pop('message_last_post')
                job = self.env['hr.job'].sudo().search([('name', "ilike", data_job['name'])])
                if job:
                    job.write({
                        'old_id' : data_job['old_id']
                    })
                    _logger.info("POSTOI VAKVA RABOTA")


        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info(f"PostgreSQL connection is closed")
    def update_job_helper(self):
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

            cursor.execute("Select * FROM hr_job LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query_job = '''SELECT * FROM hr_job; '''
            cursor.execute(query_job)
            records_jobs = cursor.fetchall()
            jobs = self.env['hr.job'].search([])
            for job in records_jobs:
                data_job = {}
                old_id = job[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'address_id':
                        data_job['old_address_id'] = job[i]
                    elif colnames[i] == 'user_id':
                        data_job['old_user_id'] = job[i]
                    elif colnames[i] == 'alias_id':
                        data_job['old_allias_id'] = job[i]

                for job in jobs:
                    if job.old_id == old_id:
                        job.write(data_job)

        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
    def update_job_db(self):
        jobs = self.env['hr.job'].sudo().search([])
        departments = self.env['hr.department'].sudo().search([])
        users = self.env['res.users'].sudo().search([])
        companies = self.env['res.company'].sudo().search([])
        employees = self.env['hr.employee'].sudo().search([])
        partners = self.env['res.partner'].sudo().search([])
        print(len(jobs))
        for job in jobs:
            for dep in departments:
                if job.old_department_id == dep.old_id:
                    # print(f'Department: {dep.name}, Company: {com.name}')
                    job.write({'department_id': dep.id})
            for user in users:
                if job.old_user_id == user.old_id:
                    job.write({'user_id': user.id})
                if job.old_hr_responsible_id == user.old_id:
                    job.write({'hr_responsible_id': user.id})
            for com in companies:
                if job.old_company_id == com.old_id:
                    job.write({'company_id': com.id})
            for emp in employees:
                if job.old_manager_id == emp.old_id:
                    job.write({'manager_id': emp.id})
            #for partner in partners:
            #    if job.old_address_id == partner.old_id:
            #        job.sudo().write({'address_id': partner.id})

    # 2
    def res_partner_db(self):
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
            _logger.info(f"You are connected to - {record}")

            cursor.execute("Select * FROM res_partner LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query_job = '''SELECT * FROM res_partner; '''
            cursor.execute(query_job)
            records = cursor.fetchall()
            print(len(records))

            for record in records:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    # print(f'{colnames[i]} : {record[i]}')
                    if colnames[i] == 'company_id':
                        companies = self.env['res.company'].sudo().search([('old_id', '=', record[i])])
                        for company in companies:
                            if record[i] == company.old_id:
                                data['company_id'] = company.id
                    elif colnames[i] == 'user_id':
                        users = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                        for user in users:
                            if record[i] == user.old_id:
                                data['user_id'] = user.id
                    else:
                        data[colnames[i]] = record[i]
                data.pop('customer')
                data.pop('supplier')
                data.pop('openupgrade_legacy_12_0_opt_out')
                data.pop('picking_warn')
                data.pop('picking_warn_msg')
                data.pop('purchase_warn')
                data.pop('purchase_warn_msg')
                data.pop('x_applicant')
                data.pop('openupgrade_legacy_12_0_activity_date_deadline')
                data.pop('num_of_duplicates')
                data.pop('last_message_activity')
                data.pop('commercial_partner_id')
                data.pop('message_main_attachment_id')
                data.pop('parent_id')
                data.pop('lang')
                data.pop('team_id')
                data.pop('country_id')
                data.pop('title')
                for i in range(len(colnames)):
                    if 'cb_' in colnames[i]:
                        data.pop(colnames[i])
                data.pop('li_connect')
                data.pop('number_of_employees')
                data.pop('x_leadsource')
                flag = 0
                if data['email']:
                    name = data['name'].strip()
                    name = name.replace("  ", " ")
                    partners = self.env['res.partner'].sudo().search(
                        [('name', "ilike", name), ('email', 'ilike', data['email'])])
                else:
                    name = data['name'].strip()
                    name = name.replace("  ", " ")
                    partners = self.env['res.partner'].sudo().search(
                        [('name', "ilike", name)])
                if partners:
                    for partner in partners:
                        flag=1
                        _logger.info("EXIST")
                        partner.write({
                            'old_id' : data['old_id']
                        })
                        break

                # if flag == 0:
                #     _logger.info('CREATE')
                #     self.env['res.partner'].create(data)

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL: {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")
    def update_res_partner(self):
        partners = self.env['res.partner'].search([])
        users = self.env['res.users'].search([])
        companies = self.env['res.company'].search([])
        for partner in partners:
            for user in users:
                if partner.old_user_id == user.old_id:
                    partner.write({'user_id': user.id})
                if partner.old_id == user.old_partner_id:
                    user.write({'partner_id': partner.id})
            for com in companies:
                if partner.old_company_id == com.old_id:
                    partner.write({'company_id': com.id})

    def res_partner_messages(self):
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
            _logger.info(f"You are connected to -  {record}")

            cursor.execute("Select * FROM mail_message LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            # print(colnames)
            query = '''SELECT * FROM mail_message where model='res.partner'; '''
            cursor.execute(query)
            records_applicants = cursor.fetchall()
            # partners = self.env['res.partner'].sudo().search([])
            users = self.env['res.users'].sudo().search([])
            for record in records_applicants:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'parent_id':
                        data['old_parent_id'] = record[i]
                    elif colnames[i] == 'author_id':
                        partner = self.env['res.partner'].sudo().search([('old_id','=',record[i])])
                        if partner:
                            for p in partner:
                                data['author_id'] = p.id
                                break
                        # for partner in partners:
                        #     if record[i] == partner.old_id:
                        #         data['author_id'] = partner.id
                    # elif colnames[i] == 'child_ids':
                    #     data['old_child_ids'] = record[i]
                    elif colnames[i] == 'moderator_id':
                        for user in users:
                            if record[i] == user.old_id:
                                data['moderator_id'] = user.id
                    # elif colnames[i] == 'notified_partner_ids':
                    #     for partner in partners:
                    #         if record[i] == partner.old_id:
                    #             data['notified_partner_ids'] = partner.id
                    # elif colnames[i] == 'partner_ids':
                    #     for partner in partners:
                    #         if record[i] == partner.old_id:
                    #             data['partner_ids'] = [partner.id]
                    elif colnames[i] == 'subtype_id':
                        data['old_subtype_id'] = record[i]
                    elif colnames[i] == 'res_id':
                        data['old_res_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]
                data.pop('layout')
                data.pop('website_published')
                data.pop('sent_mobile')
                data.pop('mail_activity_type_id')
                data.pop('mail_server_id')
                #for pair in data.items():
                #    print(pair)
                messages = self.env['mail.message'].sudo().search([('old_id','=',data['old_id'])])
                if messages:
                    for message in messages:
                        if data['old_id'] == message.old_id:
                            _logger.info('WRITE')
                            # hr_applicant_query = f'''SELECT partner_name FROM hr_applicant where id={data['old_res_id']}; '''
                            # cursor.execute(hr_applicant_query)
                            # record_applicant_name = cursor.fetchall()
                            # for name in record_applicant_name:
                            #     applicant_name = name[0].strip()
                            #     applicant_name = applicant_name.replace("  ", " ")
                            #     _logger.info({applicant_name})
                            #     break
                            new_partner_id = self.env['res.partner'].sudo().search([('old_id', '=', data['old_res_id'])])
                            for new_id in new_partner_id:
                                _logger.info({new_id.id})
                                message.write({'res_id': new_id.id})
                                break
                else:
                    _logger.info('CREATE')
                    # hr_applicant_query = f'''SELECT partner_name FROM hr_applicant where id={data['old_res_id']}; '''
                    # cursor.execute(hr_applicant_query)
                    # record_applicant_name = cursor.fetchall()
                    # _logger.info(f'{data["old_res_id"]}')
                    # for name in record_applicant_name:
                    #     _logger.info(f"{name[0]}")
                    #     applicant_name = name[0].strip()
                    #     applicant_name = applicant_name.replace("  ", " ")
                    #     break
                    # _logger.info(f'{applicant_name}')
                    new_partner_id = self.env['res.partner'].sudo().search([('old_id','=',data['old_res_id'])])
                    for new_id in new_partner_id:
                        _logger.info(f'{new_id.id}')
                        data['res_id'] = new_id.id
                        break
                    self.env['mail.message'].sudo().create(data)

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def res_partner_attachemnts(self):
        try:
            _logger.info("ATTACHMENTS MIGRATE")
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

            cursor.execute("Select * FROM ir_attachment LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            # print(colnames)
            query = '''SELECT * FROM ir_attachment where res_model='res.partner'; '''
            cursor.execute(query)
            attachments = cursor.fetchall()
            for record in attachments:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'company_id':
                        companies = self.env['res.company'].sudo().search([('old_id', '=', record[i])])
                        if companies:
                            for company in companies:
                                data['company_id'] = company.id
                    elif colnames[i] == 'create_uid':
                        users = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                        if users:
                            for user in users:
                                data['create_uid'] = user.id
                    elif colnames[i] == 'write_uid':
                        users = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                        if users:
                            for user in users:
                                data['create_uid'] = user.id
                    elif colnames[i] == 'res_id':
                        partners = self.env['res.partner'].sudo().search([('old_id', '=', record[i])])
                        _logger.info(f"{partners}")
                        if partners:
                            for partner in partners:
                                data['res_id'] = partner.id
                    else:
                        data[colnames[i]] = record[i]

                _logger.info(f"{data}")
                data.pop('old_id')
                data.pop('datas_fname')
                data.pop('openupgrade_legacy_11_0_priority')
                data.pop('res_model_name')
                data.pop('active')
                data.pop('activity_data')
                data.pop('website_id')
                self.env['ir.attachment'].sudo().create(data)
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

    #DONE
    def res_user_db(self):
        try:
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            _logger.info(f'{connection.get_dsn_parameters()}')

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            print("You are connected to - ", record, "\n")
            cursor.execute("Select * FROM res_users LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query_job = '''SELECT * FROM res_users; '''
            cursor.execute(query_job)
            records_jobs = cursor.fetchall()
            print(len(records_jobs))
            companies = self.env['res.company'].search([])
            for job in records_jobs:
                data_job = {}
                data_job['old_id'] = job[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'partner_id':
                        partner = self.env['res.partner'].sudo().search([('old_id','=',job[i])])
                        for p in partner:
                            data_job['partner_id'] = p.id
                        # data_job['partner_id'] = 1
                    elif colnames[i] == 'company_id':
                        data_job['old_company_id'] = job[i]
                        for company in companies:
                            if job[i] == company.old_id:
                                data_job['company_id'] = company.id
                    else:
                        data_job[colnames[i]] = job[i]
                data_job.pop('alias_id')
                data_job.pop('timesheet_notify')
                data_job.pop('sale_team_id')
                for i in range(len(colnames)):
                    if 'google_' in colnames[i]:
                        data_job.pop(colnames[i])
                users_active = self.env['res.users'].sudo().search([])
                users_passive = self.env['res.users'].sudo().search([('active', '=', False)])
                flag = 0
                # for pair in data_job.items():
                #    print(pair)
                for user in users_active:
                    if data_job['login'] in user.login:
                        user.write({'old_id': data_job['old_id']})
                        flag += 1
                for user in users_passive:
                    if data_job['login'] in user.login:
                        user.write({'old_id': data_job['old_id']})
                        flag += 1
                if 'name' not in data_job:
                    data_job['name'] = data_job['login']

                if data_job['login'] == 'sijcepadikova@yahoo.com':
                    print(data_job['login'])
                elif flag != 0:
                    print(data_job['login'])
                else:
                    _logger.info(f"{data_job['login']}")
                    self.env['res.users'].sudo().create(data_job)


        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")


    def update_res_user_db(self):
        users = self.env['res.users'].search([])
        companies = self.env['res.company'].search([])
        print(len(users))
        for user in users:
            for com in companies:
                if user.old_company_id == com.old_id:
                    user.write({'company_ids': [com.id],
                                'company_id': com.id})
                    # user.write({'company_id': com.id})

    # DONE
    def stage_db(self):
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
                #self.env['hr.recruitment.stage'].create(data)
                stage = self.env['hr.recruitment.stage'].sudo().search([('name','ilike',data['name'])])
                if stage:
                    stage.write({
                        'old_id' : data['old_id']
                    })
                    _logger.info("postoi")

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")
    def update_stage_db(self):
        stages = self.env['hr.recruitment.stage'].sudo().search([])
        jobs = self.env['hr.job'].sudo().search([])
        print(len(stages))
        print(len(jobs))
        for stage in stages:
            for job in jobs:
                if stage.old_job_id == job.old_id:
                    # print(f'Department: {dep.name}, Company: {com.name}')
                    stage.write({'job_ids': [job.id]})

    #DONE
    def department_db(self):
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
    def update_department_db(self):
        departments = self.env['hr.department'].sudo().search([])
        companies = self.env['res.company'].sudo().search([])
        employees = self.env['hr.employee'].sudo().search([])
        print(len(departments))
        print(len(companies))
        for dep in departments:
            for emp in employees:
                if dep.old_manager_id == emp.old_id:
                    dep.write({'manager_id': emp.id})

    # DONE
    def company_db(self):
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

            cursor.execute("Select * FROM res_company LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM res_company; '''
            cursor.execute(query)
            records_applicants = cursor.fetchall()
            print(len(records_applicants))
            for record in records_applicants:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'partner_id':
                        data['old_partner_id'] = record[i]
                        # data[colnames[i]] = 1
                    elif colnames[i] == 'parent_id':
                        # DONE
                        data['old_parent_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]
                for i in range(len(colnames)):
                    if 'rml_' in colnames[i]:
                        data.pop(colnames[i])
                    elif 'account_' in colnames[i]:
                        data.pop(colnames[i])
                    elif 'sale_' in colnames[i]:
                        data.pop(colnames[i])
                    elif 'po_' in colnames[i]:
                        data.pop(colnames[i])
                    elif 'x_' in colnames[i]:
                        data.pop(colnames[i])
                    elif 'social_' in colnames[i]:
                        data.pop(colnames[i])
                    elif 'leave_' in colnames[i]:
                        data.pop(colnames[i])
                    elif 'invoice_' in colnames[i]:
                        data.pop(colnames[i])
                data.pop('accounts_code_digits')
                data.pop('custom_footer')
                data.pop('project_time_mode_id')
                data.pop('overdue_msg')
                data.pop('propagation_minimum_delta')
                data.pop('internal_transit_location_id')
                data.pop('security_lead')
                data.pop('intercompany_user_id')
                data.pop('auto_generate_invoices')
                data.pop('so_from_po')
                data.pop('warehouse_id')
                data.pop('auto_validation')
                data.pop('vat_check_vies')
                data.pop('dearness_allowance')
                data.pop('openupgrade_legacy_12_0_external_report_layout')
                data.pop('nomenclature_id')
                data.pop('timesheet_encode_uom_id')
                data.pop('purchase_template')
                data.pop('stock_template')
                data.pop('fiscalyear_last_month')
                data.pop('font')
                data.pop('resource_calendar_id')
                data.pop('chart_template_id')
                data.pop('currency_exchange_journal_id')
                data.pop('external_report_layout_id')
                companies = self.env['res.company'].search([])
                flag = 0
                for company in companies:
                    if data['name'] in company.name:
                        company.write({'old_id': data['old_id']})
                        flag = 1
                if flag == 0:
                    self.env['res.company'].sudo().create(data)



        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
    def update_company_db(self):
        companies = self.env['res.company'].search([])
        partners = self.env['res.partner'].search([])
        print(len(companies))
        print(len(partners))
        for com in companies:
            for com1 in companies:
                if com.old_parent_id == com1.old_id:
                    com.write({'parent_id': com1.id})
        for com in companies:
            for par in partners:
                if com.old_partner_id == par.old_id:
                    com.write({'partner_id': par.id})

    # DONE
    def employee_db(self):
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
            _logger.info(f'{connection.get_dsn_parameters()}')
            cursor.execute("Select * FROM hr_employee LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM hr_employee; '''
            cursor.execute(query)
            records_applicants = cursor.fetchall()
            print(len(records_applicants))
            users = self.env['res.users'].sudo().search([])
            companies = self.env['res.company'].sudo().search([])
            departments = self.env['hr.department'].sudo().search([])
            jobs = self.env['hr.job'].search([])
            employees = self.env['hr.employee'].sudo().search([])
            _logger.info("HERE HERE HERE")
            _logger.info(f"{len(employees)}")
            _logger.info(f"{len(records_applicants)}")

            for record in records_applicants:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'company_id':
                        for company in companies:
                            if company.old_id == record[i]:
                                data['company_id'] = company.id
                    elif colnames[i] == 'user_id':
                        for user in users:
                            if user.old_id == record[i]:
                                data['user_id'] = user.id
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

                data.pop('message_last_post')
                data.pop('timesheet_cost')
                data.pop('manager')
                data.pop('medic_exam')
                data.pop('vehicle')
                data.pop('account_id')
                data.pop('google_drive_link')
                data.pop('message_main_attachment_id')
                data.pop('resource_calendar_id')
                data.pop('resource_id')
                print(data['name'])
                flag = 0
                if data['name'] == 'ERP Admin':
                    flag += 1
                for employee in employees:
                    if employee.name == data['name']:
                        employee.write({'old_id': data['old_id']})
                        flag += 1
                # if flag == 0:
                #     _logger.info(f"{data['name']}")
                #     self.env['hr.employee'].sudo().create(data)

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
    def employee_db_applicant_check(self):
        try:
            connection = psycopg2.connect(user="odoo",
                                          password="password",
                                          host="localhost",
                                          port="5432",
                                          database="testdb")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            print(connection.get_dsn_parameters(), "\n")

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            print("You are connected to - ", record, "\n")

            cursor.execute("Select * FROM hr_employee LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            for i in range(len(colnames)):
               print(f"Index: {i}, value: {colnames[i]}")

            query = '''SELECT * FROM hr_employee LIMIT 20; '''
            cursor.execute(query)
            records_applicants = cursor.fetchall()
            print(len(records_applicants))
            applicants = self.env['hr.applicant'].sudo().search([])
            print(len(applicants))
            #stages = self.env["hr.recruitment.stage"].sudo().search([])
            for record in records_applicants:
                for applicant in applicants:
                    if record.applicant_id == applicant.old_id:
                        print(applicant.partner_name)
                        #applicant.write({'last_stage_id': stage.id})



        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")
    def update_employee_db(self):
        employees = self.env['hr.employee'].sudo().search([])
        print(len(employees))
        for emp in employees:
            for emp1 in employees:
                if emp.old_coach_id == emp1.old_id:
                    emp.write({'coach_id': emp1.id})
                if emp.old_parent_id == emp1.old_id:
                    emp.write({'parent_id': emp1.id})

    # 3
    def message_mail(self):
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
            _logger.info(f"You are connected to -  {record}")

            cursor.execute("Select * FROM mail_message LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            # print(colnames)
            query = '''SELECT * FROM mail_message where model='hr.applicant'; '''
            cursor.execute(query)
            records_applicants = cursor.fetchall()
            # partners = self.env['res.partner'].sudo().search([])
            users = self.env['res.users'].sudo().search([])
            for record in records_applicants:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'parent_id':
                        data['old_parent_id'] = record[i]
                    elif colnames[i] == 'author_id':
                        partner = self.env['res.partner'].sudo().search([('old_id','=',record[i])])
                        if partner:
                            for p in partner:
                                data['author_id'] = p.id
                                break
                        # for partner in partners:
                        #     if record[i] == partner.old_id:
                        #         data['author_id'] = partner.id
                    # elif colnames[i] == 'child_ids':
                    #     data['old_child_ids'] = record[i]
                    elif colnames[i] == 'moderator_id':
                        for user in users:
                            if record[i] == user.old_id:
                                data['moderator_id'] = user.id
                    # elif colnames[i] == 'notified_partner_ids':
                    #     for partner in partners:
                    #         if record[i] == partner.old_id:
                    #             data['notified_partner_ids'] = partner.id
                    # elif colnames[i] == 'partner_ids':
                    #     for partner in partners:
                    #         if record[i] == partner.old_id:
                    #             data['partner_ids'] = [partner.id]
                    elif colnames[i] == 'subtype_id':
                        data['old_subtype_id'] = record[i]
                    elif colnames[i] == 'res_id':
                        data['old_res_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]
                data.pop('layout')
                data.pop('website_published')
                data.pop('sent_mobile')
                #for pair in data.items():
                #    print(pair)
                messages = self.env['mail.message'].sudo().search([])
                flag = 0
                for message in messages:
                    if data['old_id'] == message.old_id:
                        _logger.info('WRITE')
                        flag += 1
                        # hr_applicant_query = f'''SELECT partner_name FROM hr_applicant where id={data['old_res_id']}; '''
                        # cursor.execute(hr_applicant_query)
                        # record_applicant_name = cursor.fetchall()
                        # for name in record_applicant_name:
                        #     applicant_name = name[0].strip()
                        #     applicant_name = applicant_name.replace("  ", " ")
                        #     _logger.info({applicant_name})
                        #     break
                        # new_applicant_entry = self.env['hr.applicant'].sudo().search([('partner_name', 'ilike', applicant_name)])
                        # for new_id in new_applicant_entry:
                        #     _logger.info({new_id.id})
                        #     message.write({'res_id': new_id.id})
                        #     break
                if flag == 0:
                    _logger.info('CREATE')
                    hr_applicant_query = f'''SELECT partner_name FROM hr_applicant where id={data['old_res_id']}; '''
                    cursor.execute(hr_applicant_query)
                    record_applicant_name = cursor.fetchall()
                    _logger.info(f'{data["old_res_id"]}')
                    for name in record_applicant_name:
                        _logger.info(f"{name[0]}")
                        applicant_name = name[0].strip()
                        applicant_name = applicant_name.replace("  ", " ")
                        break
                    _logger.info(f'{applicant_name}')
                    new_applicant_entry = self.env['hr.applicant'].sudo().search([('partner_name', 'ilike', applicant_name)])
                    for new_id in new_applicant_entry:
                        _logger.info(f'{new_id.id}')
                        data['res_id'] = new_id.id
                        break
                    self.env['mail.message'].sudo().create(data)




        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def mail_message_upgrade(self):
        messages = self.env['mail.message'].sudo().search([])
        for message in messages:
            partners = self.env['res.partner'].sudo().search([('old_id', "=", message.res_id)])
            for partner in partners:
                    message.write({'res_id': partner.id})

    #1
    def hr_applicants_creation_in_res_partner(self):
        _logger.info("DALI RABOTI")
        applicants = self.env['hr.applicant'].sudo().search([])
        data={}
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
                data={}

    # 4
    def update_relation_message_partner(self):
        messages = self.env['mail.message'].sudo().search([('model','=','hr.applicant')])
        _logger.info('update_relation_message_partner')
        try:
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            _logger.info(f'{connection.get_dsn_parameters()}')

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            _logger.info(f"You are connected to - {record}")
            query1 = '''SELECT * FROM mail_message_res_partner_rel; '''
            cursor.execute(query1)
            records_in_relations = cursor.fetchall()
            for message in messages:
                _logger.info(f"ova e res_id na porakata {message.res_id}")
                applicant = self.env['hr.applicant'].sudo().search([('id','=',message.res_id)])
                if applicant.partner_name != '' and applicant.partner_name != False:
                    applicant_name = applicant.partner_name.strip()
                    applicant_name = applicant_name.replace("  ", " ")
                    _logger.info(f"ova e applicant_name {applicant_name}")
                    _logger.info(f"ova e id na applicant {applicant.id}")
                    partners = self.env['res.partner'].sudo().search([('name','=',applicant_name)])
                    for partner in partners:
                        partner_name = partner.name
                        partner_id = partner.id
                        break
                    if type(partner_name) is str and type(partner_id) is int:
                        _logger.info(f"ova e partner_name na {partner_name}")
                        _logger.info(f"ova e partner id  na {partner_id}")
                        temp_touple = (message.id,partner_id)
                        if temp_touple not in records_in_relations:
                            _logger.info(f"message id = {message.id}")
                            _logger.info(f"partner id = {partner_id}")
                            query = f"INSERT INTO mail_message_res_partner_rel(mail_message_id, res_partner_id) VALUES({message.id},{partner_id});"
                            cursor.execute(query)
                            connection.commit()

                _logger.info("\n")
                _logger.info("\n")



        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                #cursor1.close()
                #connection1.close()
                _logger.info("PostgreSQL connection is closed")

    # 5
    def message_subtype(self):
        try:
            _logger.info("MESSAGE SUBTYPE MIGRATE")
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

            cursor.execute("Select * FROM mail_message_subtype LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]

            query = '''SELECT * FROM mail_message_subtype where res_model='hr.applicant'; '''
            cursor.execute(query)
            records_subtypes = cursor.fetchall()

            for record in records_subtypes:
                data={}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    data[colnames[i]]=record[i]
                data.pop('create_uid')
                data.pop('write_uid')
                _logger.info(f"DATATA E {data}")
                _logger.info("\n")
                self.env['mail.message.subtype'].sudo().create(data)

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    # 6
    def applicant_message_subtype_update(self):
        messages = self.env['mail.message'].sudo().search([('model', '=', 'hr.applicant')])
        for message in messages:
            if message.old_subtype_id == 69 or message.old_subtype_id == 70 or message.old_subtype_id == 71:
                _logger.info(f'staroto old_subtype_id {message.old_subtype_id}')
                subtype = self.env['mail.message.subtype'].sudo().search([('old_id', '=', message.old_subtype_id)])
                _logger.info(f'staroto old_id {subtype.old_id}')
                _logger.info(f'novoto subtype_id {subtype.id}')
                message.write({'subtype_id':subtype.id})

    def delete_all_followers_for_hr_applicants_messages(self):
        _logger.info("DELETE ALL FOLLOWRS FOR HR APPLICANT MESSAGES")
        followers = self.env['mail.followers'].sudo().search([('res_model','=','hr.applicant')])
        for follower in followers:
            follower.unlink()

    #UPDATE OLD ID FOR HR APPLiCANTS
    def update_old_id_on_hr_applicants(self):
        try:
            _logger.info("HR APPLICANTS OLD_ID UPDATE")
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
            query = '''SELECT * FROM hr_applicant; '''
            cursor.execute(query)
            records_applicants = cursor.fetchall()
            for record in records_applicants:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'partner_name':
                        _logger.info(f"partner_name = {record[i]}")
                        data['partner_name'] = record[i]
                    elif colnames[i] == 'email_from':
                        _logger.info(f"email_from = {record[i]}")
                        data['email_from'] = record[i]
                applicants = self.env['hr.applicant'].sudo().search([('partner_name','=',data['partner_name'])])
                if applicants:
                    for applicant in applicants:
                        applicant.write({
                            'old_id' : data['old_id']
                        })
                        _logger.info(f"applicant name e {applicant.partner_name}, a id {applicant.id}")

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

    #FOLLOWERS MIGRATE AND UPDATE FOR HR.APPLICANT
    def followers_update_for_applicant_messages(self):
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

    #ATTACHMENTS FOR APPLICANTS
    def attachments_for_applicants(self):
        try:
            _logger.info("ATTACHMENTS MIGRATE")
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

            cursor.execute("Select * FROM ir_attachment LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            # print(colnames)
            query = '''SELECT * FROM ir_attachment where res_model='hr.applicant'; '''
            cursor.execute(query)
            attachments = cursor.fetchall()
            for record in attachments:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'company_id':
                        companies = self.env['res.company'].sudo().search([('old_id','=',record[i])])
                        if companies:
                            for company in companies:
                                data['company_id'] = company.id
                    elif colnames[i] == 'create_uid':
                        users = self.env['res.users'].sudo().search([('old_id','=',record[i])])
                        if users:
                            for user in users:
                                data['create_uid'] = user.id
                    elif colnames[i] == 'write_uid':
                        users = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                        if users:
                            for user in users:
                                data['create_uid'] = user.id
                    elif colnames[i] == 'res_id':
                        applicants = self.env['hr.applicant'].sudo().search([('old_id', '=', record[i])])
                        _logger.info(f"{applicants}")
                        if applicants:
                            for applicant in applicants:
                                data['res_id'] = applicant.id
                    else:
                        data[colnames[i]] = record[i]

                _logger.info(f"{data}")
                data.pop('old_id')
                data.pop('datas_fname')
                data.pop('openupgrade_legacy_11_0_priority')
                data.pop('res_model_name')
                data.pop('active')
                data.pop('activity_data')
                data.pop('website_id')
                self.env['ir.attachment'].sudo().create(data)
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

    #CREATE_DATE and USER_ID UPDATE
    def update_create_date_hr_applicant(self):
        try:
            _logger.info("UPDATE CREATE_DATE and USER_ID HR APPLICANT")
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

            query = '''SELECT id,create_date,user_id FROM hr_applicant; '''
            cursor.execute(query)
            records_applicants = cursor.fetchall()
            for record in records_applicants:
                _logger.info(f"rekordot e {record}")
                applicant = self.env['hr.applicant'].sudo().search([('old_id', '=', record[0])])
                _logger.info(f"aplikantot e {applicant}")
                if applicant:
                    users = self.env['res.users'].sudo().search([('old_id', '=', record[2])])
                    _logger.info(f"userot e {users}")
                    for ap in applicant:
                        if users:
                            for u in users:
                                _logger.info(f"loginot e {u.login}")
                                ap.write({
                                    'create_date' : record[1],
                                    'user_id' : u.id
                                })
                                break
                        else:
                            _logger.info(f"applikantot e {ap}")
                            ap.write({
                                'create_date': record[1],
                            })
                        break
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

    def res_user_update_old_id(self):
        try:
            _logger.info("USERS UPDATE")
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
            cursor.execute("Select * FROM res_users LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT id,login FROM res_users; '''
            cursor.execute(query)
            records_users = cursor.fetchall()
            for record in records_users:
                _logger.info(f"{record}")
                user =  self.env['res.users'].sudo().search([('login', '=', record[1]),'|',
                                            ('active','=',False),('active','=',True)])
                _logger.info(f"login na userot {user.login}, a id {user.id}")
                # user.write({
                #     'old_id' : record[0]
                # })
                _logger.info('\n')
                _logger.info('\n')

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")


    def crm_lead_migrate_db(self):
        try:
            _logger.info("CRM MIGRATE")
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
            cursor.execute("Select * FROM crm_lead LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM crm_lead; '''
            cursor.execute(query)
            records_crm = cursor.fetchall()
            for record in records_crm:
                _logger.info(f"{record}")
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'country_id':
                        data['old_country_id'] = record[i] # KJE TREBA TRANSFER I NA RES.COUNTRY
                    # elif colnames[i] == 'write_uid': # NAOGJA MNOGU SO OLD_ID ISTO
                    #     user_exist = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                    #     if user_exist:
                    #         _logger.info("WRITE UID USER")
                    #         data['write_uid'] = user_exist.id
                    elif colnames[i] == 'team_id':
                        data['old_team_id'] = record[i]
                    elif colnames[i] == 'partner_id':# NAOGJA MNOGU SO OLD_ID ISTO
                        partner_exist = self.env['res.partner'].sudo().search([('old_id', '=', record[i])])
                        if partner_exist:
                            for partner in partner_exist:
                                data['partner_id'] = partner.id
                                break
                    elif colnames[i] == 'company_id':
                        company_exist = self.env['res.company'].sudo().search([('old_id', '=', record[i])])
                        if company_exist:
                            data['company_id'] = company_exist.id
                    # elif colnames[i] == 'create_uid': # NAOGJA MNOGU SO OLD_ID ISTO
                    #     user_exist = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                    #     if user_exist:
                    #         _logger.info("CREATE UID USER")
                    #         data['create_uid'] = user_exist.id
                    elif colnames[i] == 'user_id': # NAOGJA MNOGU SO OLD_ID ISTO
                        user_exist = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                        for user in user_exist:
                            data['user_id'] = user.id
                            break
                    elif colnames[i] == 'stage_id':
                        data['old_stage_id'] = record[i]
                    elif colnames[i] == 'message_main_attachment_id': # PRASAJ ZA ATTACHMENTS
                        data['old_message_main_attachment_id'] = record[i]
                    elif colnames[i] == 'title': #najverojatno kje treba da se sredi
                        data['old_title'] = record[i]
                    elif colnames[i] == 'source_id':
                        data['old_source_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]

                data.pop('date_action_next')
                data.pop('openupgrade_legacy_12_0_opt_out')
                data.pop('message_last_post')
                data.pop('next_activity_id')
                data.pop('fax')
                data.pop('title_action')
                data.pop('date_action')
                data.pop('last_activity_id')
                data.pop('openupgrade_legacy_12_0_activity_date_deadline')
                data.pop('planned_revenue')
                data.pop('contact_lastname')
                data.pop('no_active_activities')
                data.pop('no_scheduled_activities')
                data.pop('last_activity_date')
                crm_lead_exist = self.env['crm.lead'].sudo().search([('old_id', '=', data['old_id'])])
                if crm_lead_exist:
                    _logger.info("EXIST")
                    _logger.info('\n')
                else:
                    _logger.info("CREATE")
                    _logger.info('\n')
                    self.env['crm.lead'].sudo().create(data)

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")


    def crm_lead_tag_migrate_db(self): # PRVIOT PAT NEJKESE OLD_ID I TEAM_ID DA SE STAAT, 2 PATI JA PUSTIV ZA DA SE UPDATNE
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
            _logger.info(f"You are connected to -  {record}")
            cursor.execute("Select * FROM crm_lead_tag LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM crm_lead_tag; '''
            cursor.execute(query)
            records_crm_lead_tag = cursor.fetchall()
            for record in records_crm_lead_tag:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'team_id':
                        data['old_team_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]

                data.pop('create_uid')
                data.pop('write_uid')
                crm_tag_exist =  self.env['crm.tag'].sudo().search([('name', '=', data['name'])])
                if not crm_tag_exist:
                    _logger.info("CREATE")
                    self.env['crm.tag'].sudo().create(data)
                else:
                    _logger.info("EXIST")
                    crm_tag_exist.write({
                        'old_id' : data['old_id'],
                        'old_team_id' : data['old_team_id']
                    })

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")


    def update_relation_crm_lead_tag(self):
        _logger.info('UPDATE RELATION CRM_LEAD - CRM_TAG')
        try:
            connection = psycopg2.connect(user="odoo",
                                          password="odoo",
                                          host="172.19.0.2",
                                          port="5432",
                                          database="najnovaDB")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            _logger.info(f'{connection.get_dsn_parameters()}')

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            _logger.info(f"You are connected to - {record}")
            query1 = '''SELECT * FROM crm_tag_rel; '''
            cursor.execute(query1)
            records_in_relations_v14 = cursor.fetchall()

            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor2 = connection2.cursor()
            # Print PostgreSQL Connection properties
            _logger.info(f'{connection2.get_dsn_parameters()}')

            # Print PostgreSQL version
            cursor2.execute("SELECT version();")
            record = cursor2.fetchone()
            _logger.info(f"You are connected to - {record}")
            query2 = '''SELECT * FROM crm_lead_tag_rel; '''
            cursor2.execute(query2)
            records_in_relations_v12 = cursor2.fetchall()

            for record in records_in_relations_v12:
                _logger.info(f"ova e torkata od v12 {record}")
                _logger.info(f"ova e id na crm_lead {record[0]}")
                _logger.info(f"ova e id na crm_tag {record[1]}")
                kveri = f'''SELECT old_id,id FROM crm_lead where old_id = {record[0]}; '''
                cursor.execute(kveri)
                crm_lead_v14 = cursor.fetchall()
                for rec in crm_lead_v14:
                    _logger.info(f"ova e new id od crm_lead {rec[1]}, a ova e old_id {rec[0]}")
                    crm_lead_new_id = rec[1]
                crm_tag_v14 = self.env['crm.tag'].sudo().search([('old_id', '=', record[1])])
                _logger.info(f"ova e new id od crm_tag {crm_tag_v14.id}, a ova e old_id {crm_tag_v14.old_id}")
                crm_tag_new_id = crm_tag_v14.id
                if type(crm_lead_new_id) is int and type(crm_tag_new_id) is int:
                    tuple_for_relation = (crm_lead_new_id,crm_tag_new_id)
                    _logger.info(f"ova e torkata za relacija {tuple_for_relation}")
                    if tuple_for_relation not in records_in_relations_v14:
                        _logger.info("CREATE")
                        query = f"INSERT INTO crm_tag_rel(lead_id, tag_id) VALUES({crm_lead_new_id},{crm_tag_new_id});"
                        cursor.execute(query)
                        connection.commit()

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                #cursor1.close()
                #connection1.close()
                _logger.info("PostgreSQL connection is closed")

    def crm_stage_migrate_db(self):
        try:
            _logger.info("CRM STAGE MIGRATE")
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
            cursor.execute("Select * FROM crm_stage LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM crm_stage; '''
            cursor.execute(query)
            records_crm_stage = cursor.fetchall()
            for record in records_crm_stage:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'team_id':
                        data['old_team_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]
                data.pop('probability')
                data.pop('create_uid')
                data.pop('write_uid')
                data.pop('on_change')
                data.pop('legend_priority')
                data.pop('type')
                crm_stage_exist = self.env['crm.stage'].sudo().search([('name', '=', data['name'])])
                if not crm_stage_exist:
                    self.env['crm.stage'].sudo().create(data)
                else:
                    crm_stage_exist.write({
                        'old_id' : data['old_id']
                    })


        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")


    def crm_team_migrate_db(self):
        try:
            _logger.info("CRM TEAM MIGRATE")
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
            cursor.execute("Select * FROM crm_team LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM crm_team; '''
            cursor.execute(query)
            records_crm_stage = cursor.fetchall()
            for record in records_crm_stage:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'user_id':
                        data['old_user_id'] = record[i]
                    elif colnames[i] == 'company_id':
                        data['old_company_id'] = record[i]
                    elif colnames[i] == 'alias_id':
                        data['old_alias_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]
                data.pop('working_hours')
                data.pop('message_last_post')
                data.pop('reply_to')
                data.pop('resource_calendar_id')
                data.pop('use_invoices')
                data.pop('team_type')
                data.pop('dashboard_graph_model')
                data.pop('dashboard_graph_group')
                data.pop('dashboard_graph_period')
                data.pop('dashboard_graph_group_pipeline')
                data.pop('message_main_attachment_id')
                data.pop('openupgrade_legacy_12_0_dashboard_graph_model')

                crm_teams = self.env['crm.team'].sudo().search([('name', '=', data['name'])])
                if not crm_teams:
                    _logger.info('CREATE')
                    self.env['crm.team'].sudo().create(data)
                else:
                    crm_teams.write({
                        'old_id' : data['old_id']
                    })


        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def crm_team_stage_rel_update(self):
        _logger.info('UPDATE RELATION CRM_TEAM - CRM_STAGE')
        try:
            connection = psycopg2.connect(user="odoo",
                                          password="odoo",
                                          host="172.19.0.2",
                                          port="5432",
                                          database="najnovaDB")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            _logger.info(f'{connection.get_dsn_parameters()}')

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            _logger.info(f"You are connected to - {record}")
            query1 = '''SELECT * FROM team_stage_rel; '''
            cursor.execute(query1)
            records_in_relations_v14 = cursor.fetchall()

            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor2 = connection2.cursor()
            # Print PostgreSQL Connection properties
            _logger.info(f'{connection2.get_dsn_parameters()}')

            # Print PostgreSQL version
            cursor2.execute("SELECT version();")
            record = cursor2.fetchone()
            _logger.info(f"You are connected to - {record}")
            query2 = '''SELECT * FROM crm_team_stage_rel; '''
            cursor2.execute(query2)
            records_in_relations_v12 = cursor2.fetchall()

            for record in records_in_relations_v12:
                _logger.info(f"ova e torkata od v12 {record}")
                _logger.info(f"ova e id na stage {record[0]}")
                _logger.info(f"ova e id na team {record[1]}")
                query_crm_stage = f'''SELECT name FROM crm_stage where id={record[0]}; '''
                query_crm_team  = f'''SELECT name FROM crm_team where id={record[1]}; '''
                cursor2.execute(query_crm_stage)
                crm_stage_old = cursor2.fetchall()
                _logger.info(f"ova e crm_stage_old od v12 {crm_stage_old}")
                cursor2.execute(query_crm_team)
                crm_team_old = cursor2.fetchall()
                _logger.info(f"ova e crm_team_old od v12 {crm_team_old}")
                crm_stage_new = self.env['crm.stage'].sudo().search([('name', '=', crm_stage_old[0][0])])
                _logger.info(f"{crm_stage_new}")
                crm_team_new = self.env['crm.team'].sudo().search([('name', '=', crm_team_old[0][0])])
                _logger.info(f"{crm_team_new}")
                for rec in crm_stage_new:
                    crm_stage_new_id = rec.id
                tuple_for_relation=(crm_team_new.id,crm_stage_new_id)
                _logger.info(f"torkata za vo relacija {tuple_for_relation}")
                if tuple_for_relation in records_in_relations_v14:
                    _logger.info("CREATE")
                    query = f"INSERT INTO team_stage_rel(helpdesk_team_id, helpdesk_stage_id) VALUES({crm_team_new.id},{crm_stage_new.id});"
                    cursor.execute(query)
                    connection.commit()
                else:
                    _logger.info("EXIST")
                _logger.info("\n")
                _logger.info("\n")

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                #cursor1.close()
                #connection1.close()
                _logger.info("PostgreSQL connection is closed")

    def crm_lead_team_update(self):
        crm_leads = self.env['crm.lead'].sudo().search([])
        for crm_lead in crm_leads:
            _logger.info(f'staroto old_team_id {crm_lead.old_team_id}')
            team = self.env['crm.team'].sudo().search([('old_id', '=', crm_lead.old_team_id)])
            _logger.info(f'staroto old_id {team.old_id}')
            _logger.info(f'novoto team_id {team.id}')
            if team:
                crm_lead.write({'team_id': team.id})

    def crm_lead_stage_update(self):
        crm_leads = self.env['crm.lead'].sudo().search([])
        for crm_lead in crm_leads:
            _logger.info(f'staroto old_stage_id {crm_lead.old_stage_id}')
            stage = self.env['crm.stage'].sudo().search([('old_id', '=', crm_lead.old_stage_id)])
            _logger.info(f'staroto old_id {stage.old_id}')
            _logger.info(f'novoto team_id {stage.id}')
            crm_lead.write({'stage_id': stage.id})

    def res_country_migrate(self):
        try:
            _logger.info("COUNTRY MIGRATE")
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
            cursor.execute("Select * FROM res_country LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM res_country; '''
            cursor.execute(query)
            records_crm = cursor.fetchall()
            for record in records_crm:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'currency_id':
                        data['old_currency_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]
                data.pop('address_view_id')
                data.pop('vat_label')
                country = self.env['res.country'].sudo().search([('name', '=', data['name'])])
                if not country:
                    _logger.info('CREATE')
                    self.env['res.country'].sudo().create(data)
                else:
                    _logger.info('EXIST')
                    country.write({
                        'old_id' : data['old_id']
                    })



        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def res_currency_migrate(self):
        try:
            _logger.info("CURRENCY MIGRATE")
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
            cursor.execute("Select * FROM res_currency LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM res_currency; '''
            cursor.execute(query)
            records_crm = cursor.fetchall()
            for record in records_crm:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    data[colnames[i]] = record[i]
                name = data['name'].strip()
                name = name.replace("  ", " ")
                currency = self.env['res.currency'].sudo().search([('name','=',name),'|',
                                            ('active','=',False),('active','=',True)])
                if not data['symbol']:
                    data['symbol'] = 'nema simbol'
                if not currency:
                    _logger.info('CREATE')
                    self.env['res.currency'].sudo().create(data)
                else:
                    _logger.info('EXIST')
                    currency.write({
                        'old_id' : data['old_id']
                    })



        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def update_country_currency(self):
        countries = self.env['res.country'].sudo().search([])
        for country in countries:
            currency = self.env['res.currency'].sudo().search([('old_id','=',country.old_currency_id)])
            country.write({
                'currency_id' : currency.id
            })

    def update_crm_lead_country(self):
        crm_leads = self.env['crm.lead'].sudo().search([])
        _logger.info('CRM LEAD COUNTRY UPDATE')
        for crm_lead in crm_leads:
            _logger.info(f'staroto old_crm_lead_country_id {crm_lead.old_country_id}')
            country = self.env['res.country'].sudo().search([('old_id', '=', crm_lead.old_country_id)])
            _logger.info(f'staroto old_id {country.old_id}')
            _logger.info(f'novoto country id {country.id}')
            crm_lead.write({
                'country_id': country.id
            })


    #CRM USER_ID DA UPDATNES
    def crm_lead_user_update(self):
        try:
            _logger.info("CRM LEAD USER UPDATE")
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
            cursor.execute("Select * FROM crm_lead LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT id,user_id FROM crm_lead; '''
            cursor.execute(query)
            records_crm = cursor.fetchall()
            for record in records_crm:
                _logger.info(f"old id = {record[0]}, a user_id = {record[1]}")
                crm_lead = self.env['crm.lead'].sudo().search([('old_id', '=', record[0])])
                _logger.info(f"crm_lead old_id {crm_lead.old_id}")
                users = self.env['res.users'].sudo().search([('old_id', '=', record[1])])
                if users:
                    for user in users:
                        _logger.info(f"user id {user.old_id}")
                        crm_lead.write({
                            'user_id' : user.id
                        })
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

    #CRM PORAKITE SE OVA
    def crm_message_update(self):
        _logger.info("CRM MESSAGE UPDATE")
        crm_messages = self.env['mail.message'].sudo().search([('model', '=', 'crm.lead')])
        for crm_message in crm_messages:
            _logger.info(f"res_id = {crm_message.res_id}")
            crm_lead = self.env['crm.lead'].sudo().search([('id', '=', crm_message.res_id)])
            _logger.info(f"crm_lead id = {crm_lead.id}")
            _logger.info(f"userot e so id {crm_lead.user_id.id}")
            _logger.info(f"partnerot e so id {crm_lead.user_id.partner_id.id}")
            partner = self.env['res.partner'].sudo().search([('id', '=', crm_lead.user_id.partner_id.id)])
            _logger.info(f"partnerot e so id {partner.id} i ime {partner.name}")
            if partner:
                crm_message.write({
                    'author_id' : partner.id
                })
            _logger.info("\n")
            _logger.info("\n")
    #CRM ATTACHMENTS
    def crm_attachments_migrate(self):
        try:
            _logger.info("CRM ATTACHMENTS MIGRATE")
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

            cursor.execute("Select * FROM ir_attachment LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            # print(colnames)
            query = '''SELECT * FROM ir_attachment where res_model='crm.lead'; '''
            cursor.execute(query)
            attachments = cursor.fetchall()
            for record in attachments:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'company_id':
                        companies = self.env['res.company'].sudo().search([('old_id', '=', record[i])])
                        if companies:
                            for company in companies:
                                data['company_id'] = company.id
                    elif colnames[i] == 'create_uid':
                        users = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                        if users:
                            for user in users:
                                data['create_uid'] = user.id
                    elif colnames[i] == 'write_uid':
                        users = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                        if users:
                            for user in users:
                                data['create_uid'] = user.id
                    elif colnames[i] == 'res_id':
                        partners = self.env['crm.lead'].sudo().search([('old_id', '=', record[i])])
                        _logger.info(f"{partners}")
                        if partners:
                            for partner in partners:
                                data['res_id'] = partner.id
                    else:
                        data[colnames[i]] = record[i]

                _logger.info(f"{data}")
                data.pop('old_id')
                data.pop('datas_fname')
                data.pop('openupgrade_legacy_11_0_priority')
                data.pop('res_model_name')
                data.pop('active')
                data.pop('activity_data')
                data.pop('website_id')
                self.env['ir.attachment'].sudo().create(data)
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


    def message_author_update_by_name(self):
        try:
            _logger.info("UPDATE MESSAGE AUTHOR ")
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
            messages = self.env['mail.message'].sudo().search([('model', '=', 'hr.applicant')])
            for message in messages:
                if type(message.old_id) is int:
                    _logger.info("MESSAGE IDE")
                    query = f'''SELECT id,author_id FROM mail_message where id={message.old_id}; '''
                    _logger.info("MESSAGE POSLE")
                    cursor.execute(query)
                    message_query_result = cursor.fetchall()
                    if message_query_result:
                        author_id = message_query_result[0][1]
                    else:
                        author_id='string'
                    if type(author_id) is int:
                        _logger.info("AUTHOIR ID")
                        kveri = f'''SELECT name FROM res_partner where id={author_id}; '''
                        cursor.execute(kveri)
                        partner_query_result = cursor.fetchall()
                        partner_name = partner_query_result[0][0]
                        partner_name = partner_name.strip()
                        partner_name = partner_name.replace("  ", " ")
                        _logger.info(f"{partner_query_result}")
                        _logger.info(f"partner name {partner_name}")

                        partner = self.env['res.partner'].sudo().search([('name', 'ilike', partner_name)])
                        if partner:
                            for partn in partner:
                                partner_id = partn.id
                                _logger.info(f"ime na partner {partn.name}, a negovo id {partn.id}")
                                _logger.info("\n")
                                _logger.info("\n")
                            message.write({
                                'author_id' : partner_id,
                            })

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    #AVTORITE NA PORAKITE
    def message_author_update_by_old_id(self):
        try:
            _logger.info("UPDATE MESSAGE AUTHOR ")
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
            messages = self.env['mail.message'].sudo().search([('model', '=', 'hr.applicant')])
            for message in messages:
                if type(message.old_id) is int:
                    _logger.info(f"message old_id {message.old_id} , new id {message.id}")
                    query = f'''SELECT id,author_id,email_from FROM mail_message where id={message.old_id}; '''
                    cursor.execute(query)
                    message_query_result = cursor.fetchall()
                    _logger.info(f"{message_query_result}")
                    if message_query_result:
                        author_id = message_query_result[0][1]
                    else:
                        author_id='string'
                    if type(author_id) is int:
                        _logger.info("AUTHOIR ID")
                        partner = self.env['res.partner'].sudo().search([('old_id', '=', author_id),'|',
                                            ('active','=',False),('active','=',True)])
                        if partner:
                            for partn in partner:
                                partner_id = partn.id
                                _logger.info(f"ime na partner {partn.name}, a negovo id {partn.id}")
                                break
                            message.write({
                                'author_id' : partner_id,
                            })
                    else:
                        _logger.info("FIND AUTHOR ID")
                        if message_query_result:
                            email_from = message_query_result[0][2]
                            email_split = email_from.split("<", 1)
                            _logger.info(f"{email_split}")
                            if len(email_split)==2:
                                email = email_split[1]
                                email = email.replace(">", "")
                                email = email.strip()
                                _logger.info(f'{email}')
                            else:
                                email = email_split[0]
                                email = email.strip()
                                _logger.info(f'{email}')
                            partner = self.env['res.partner'].sudo().search([('email', '=', email),'|',
                                                ('active','=',False),('active','=',True)])
                            if partner:
                                for partn in partner:
                                    partner_id = partn.id
                                    _logger.info(f"ime na partner {partn.name}, a negovo id {partn.id}")
                                    break
                                message.write({
                                    'author_id' : partner_id,
                                })


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

    def update_author_mail_message_for_NULL_author_id(self):
        _logger.info("AUTHOR UPDATE ")
        messages = self.env['mail.message'].sudo().search([('model','=','hr.applicant')])
        for message in messages:
            _logger.info(f"MESSAGE IS {message}")
            _logger.info(f"{message.author_id.id}")
            if message.author_id.id == 49:
                message.write({
                    'author_id' : 390955
                })
        _logger.info("\n")
        _logger.info("\n")

    def res_company_old_id_update(self):
        try:
            _logger.info("RES-COMPANY UPDATE")
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
            companies = self.env['res.company'].sudo().search([])
            for company in companies:
                _logger.info(f"ova e imeto {company.name}")
                name = company.name.strip()
                name = name.replace("  ", " ")
                query = f'''SELECT id,name FROM res_company where name ilike '{name}'; '''
                cursor.execute(query)
                old_company = cursor.fetchall()
                _logger.info(f"{old_company}")
                if old_company:
                    _logger.info(f"OLD ID = {old_company[0][0]}, NAME = {old_company[0][1]}")
                    company.write({
                        'old_id' : old_company[0][0]
                    })
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


    def product_pricelist_migrate(self):
        try:
            _logger.info("PRODUCT-PRICELIST MIGRATE")
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
            cursor.execute("Select * FROM product_pricelist LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM product_pricelist; '''
            cursor.execute(query)
            records_product_pricelist = cursor.fetchall()
            for record in records_product_pricelist:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'company_id':
                        company = self.env['res.company'].sudo().search([('old_id', '=', record[i])])
                        for com in company:
                            data['company_id'] = com.id
                            break
                    elif colnames[i] == 'currency_id':
                        currency = self.env['res.currency'].sudo().search([('old_id','=',record[i])])
                        data['currency_id'] = currency.id
                    else:
                        data[colnames[i]] = record[i]
                name = data['name'].strip()
                name = name.replace("  ", " ")
                # product_pricelist = self.env['product.pricelist'].sudo().search(([('name','=',name),'|',
                #                             ('active','=',False),('active','=',True)]))
                product_pricelist = self.env['product.pricelist'].sudo().search(([('old_id','=',data['old_id'])]))
                if product_pricelist:
                    for pro in product_pricelist:
                        _logger.info('WRITE')
                        pro.write(data)
                else:
                    _logger.info("CREATE")
                    self.env['product.pricelist'].sudo().create(data)


        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def cron_contacts_update(self):
        _logger.info("CRON FUNCTION")
        url = 'https://erp.simplify-erp.com'
        db = 'v12cc'
        username = 'm95@simplify-erp.com'
        password = 'leon'
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        _logger.info(f"verzijata e {common.version()}")
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        models.execute_kw(db, uid, password,
                          'res.partner', 'check_access_rights',
                          ['read'], {'raise_exception': False})
        today = datetime.datetime.today()
        _logger.info(f"denesen datum {today}")
        DD = datetime.timedelta(days=20)
        earlier = today - DD
        _logger.info(f"2 nedeli predhodno {earlier}")
        records_create = models.execute_kw(db, uid, password,
                          'res.partner', 'search',
                          [[['create_date', '>', earlier] , ['create_date','<',today]]])
        records_update = models.execute_kw(db, uid, password,
                          'res.partner', 'search',
                          [[['write_date', '>', earlier] , ['write_date','<',today]]])
        # _logger.info(f"novokreirani records se {len(records_create)}")
        # _logger.info("\n")
        # _logger.info("\n")
        # _logger.info(f"updatirani records se {len(records_update)}")
        all_ids = records_create+records_update
        # _logger.info("\n")
        # _logger.info("\n")
        # _logger.info(f"site records se {all_ids}")

        for id in all_ids:
            [record] = models.execute_kw(db, uid, password,
                                              'res.partner', 'read', [id], {
                                                  'fields': ['firstname', 'lastname', 'company_id', 'phone', 'mobile',
                                                             'email', 'website','x_leadsource','function','parent_id','create_date','write_date']})
            company = self.env['res.company'].sudo().search([('old_id', '=', record['company_id'][0])])
            partner = self.env['res.partner'].sudo().search([('old_id', '=', record['id'])])
            data={}
            _logger.info(f"{record}")
            for rec in record:
                if rec == 'company_id':
                    if company:
                        for c in company:
                            data[rec] = c.id
                else:
                    data[rec] = record[rec]
            if type(record['firstname']) is str and type(record['lastname']) is str:
                data['name'] = record['firstname'] + " " + record['lastname']
            elif type(record['firstname']) is str:
                data['name'] = record['firstname']
            else:
                data['name'] = record['lastname']
            if partner:
                _logger.info("update")
                data.pop("parent_id")
                data.pop('company_id')
                data.pop("id")
                _logger.info(f"{data}")
                partner.write(data)
            else:
                _logger.info("create")
                data['old_id'] = data['id']
                if data["parent_id"] != False:
                    _logger.info(f"{record['parent_id']}")
                    parent = self.env['res.partner'].sudo().search([('old_id', '=', record['parent_id'][0])])
                    data['parent_id'] = parent.id
                data.pop('id')
                data.pop('x_leadsource')
                data.pop('create_date')
                data.pop('write_date')
                data.pop('company_id')
                _logger.info(f"{data}")
                nov_partner=self.env['res.partner'].sudo().create(data)
                _logger.info(f"{nov_partner}")

            _logger.info("\n")
            _logger.info("\n")
        _logger.info("KRAAAAAAAJ")
    #PRASAJ GO SINISHA
    def res_user_migrate_db(self):
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
            _logger.info(f"You are connected to -  {record}")
            cursor.execute("Select * FROM res_users LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = f'''SELECT * FROM res_users; '''
            cursor.execute(query)
            old_users = cursor.fetchall()
            for record in old_users:
                _logger.info(f"{record}")
                data={}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'login':
                        data['login'] = record[i]
                #     elif colnames[i] == 'company_id':
                #         companies = self.env['res.company'].sudo().search([('old_id', '=', record[i])])
                #         for company in companies:
                #             data['company_id'] = company.id
                #             break
                #     elif colnames[i] == 'partner_id':
                #         partners = self.env['res.partner'].sudo().search([('old_id', '=', record[i]), '|',
                #                                                ('active', '=', False), ('active', '=', True)])
                #         for partner in partners:
                #             data['partner_id'] = partner.id
                #             break
                #     else:
                #         data[colnames[i]] = record[i]
                # data.pop('alias_id')
                # data.pop('timesheet_notify')
                # data.pop('sale_team_id')
                # data.pop('google_calendar_token_validity')
                # data.pop('google_calendar_cal_id')
                # data.pop('google_calendar_rtoken')
                # data.pop('google_calendar_last_sync_date')
                # data.pop('google_calendar_token')
                # data.pop('company_id')
                users = self.env['res.users'].sudo().search([('login', '=', data['login']), '|',
                                                               ('active', '=', False), ('active', '=', True)])
                if users:
                    for user in users:
                        _logger.info("UPDATE")
                        user.write(data)
                        break
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

    def stock_location_migrate(self):
        try:
            _logger.info("STOCK-LOCATION MIGRATE")
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
            cursor.execute("Select * FROM stock_location LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM stock_location; '''
            cursor.execute(query)
            records = cursor.fetchall()
            for record in records:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'parent_id':  # KJE TREBA UPDATE
                        data['old_partner_id'] = record[i]
                    elif colnames[i] == 'company_id':
                        companies  = self.env['res.company'].sudo().search([('old_id', '=', record[i])])
                        for company in companies:
                            data['company_id'] = company.id
                            break
                    elif colnames[i] == 'location_id': # KJE TREBA UPDATE
                        data['old_location_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]
                data.pop('parent_left')
                data.pop('parent_right')
                data.pop('putaway_strategy_id')
                data.pop('partner_id')
                _logger.info(f"{data}")
                stock_location = self.env['stock.location'].sudo().search([('name', '=', data['name'])])
                if stock_location:
                    _logger.info("exist")
                else:
                    _logger.info("create")
                    if data['usage'] != 'procurement':
                        stock_barcode = self.env['stock.location'].sudo().search([('barcode', '=', data['barcode'])])
                        _logger.info(f"SO BARKOD {stock_barcode}")
                        if stock_barcode:
                            _logger.info("postoi so barkod takkov")
                        else:
                            self.env['stock.location'].sudo().create(data)
                _logger.info("\n")
                _logger.info("\n")

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"{error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def stock_warehouse_migrate(self):
        try:
            _logger.info("STOCK-LOCATION MIGRATE")
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
            cursor.execute("Select * FROM stock_location LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM stock_location; '''
            cursor.execute(query)
            records = cursor.fetchall()
            for record in records:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'parent_id':  # KJE TREBA UPDATE
                        data['old_partner_id'] = record[i]


        except (Exception, psycopg2.Error) as error:
            _logger.info(f"{error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")


    #OVA TREBA DA GO NAPRAIS
    def sale_order_migrate(self):
        try:
            _logger.info("SALE-ORDER MIGRATE")
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
            cursor.execute("Select * FROM sale_order LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM sale_order; '''
            cursor.execute(query)
            records_sale_order = cursor.fetchall()
            for record in records_sale_order:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'team_id':
                        team = self.env['crm.team'].sudo().search([('old_id', '=', record[i])])
                        for t in team:
                            data['team_id'] = t.id
                            _logger.info("TEAM IMA")
                            break
                    elif colnames[i] == 'partner_id':
                        partner = self.env['res.partner'].sudo().search([('old_id', '=', record[i])])
                        if partner:
                            for p in partner:
                                data['partner_id'] = p.id
                                _logger.info("PARTNER IMA")
                    elif colnames[i] == 'procurement_group_id': # KJE TREBA DA SE UPDATNE
                        data['old_procurement_group_id'] = record[i]
                    elif colnames[i] == 'company_id':
                        company = self.env['res.company'].sudo().search([('old_id', '=', record[i])])
                        if company:
                            _logger.info(f"OLD COMPANY ID E {record[i]}")
                            data['company_id'] = company.id
                            _logger.info(f"NEW COMPANY ID E {company.id}")
                            _logger.info("COMPANY IMA")
                    elif colnames[i] == 'pricelist_id': #MOZE KJE TREBA DA SE UPDAJTNE
                        product_pricelist = self.env['product.pricelist'].sudo().search([('old_id', '=', record[i])])
                        _logger.info(f"{product_pricelist}")
                        if product_pricelist:
                            _logger.info(f"OLD PRICELIST ID E {record[i]}")
                            for p in product_pricelist:
                                _logger.info(f"{p}")
                                _logger.info(f"{p.id}")
                                data['pricelist_id'] = p.id
                                break
                            _logger.info("PRICELIST IMA")
                    elif colnames[i] == 'analytic_account_id':
                        data['old_analytic_account_id'] = record[i] # KJE TREBA DA SE UPDATNE
                    elif colnames[i] == 'payment_term_id':
                        data['old_payment_term_id'] = record[i]
                    elif colnames[i] == 'partner_invoice_id':
                        _logger.info(f"{record[i]}")
                        partner = self.env['res.partner'].sudo().search([('old_id', '=', record[i])])
                        for part in partner:
                            data['partner_invoice_id'] = part.id
                            _logger.info("PARTNER INVOICE IMA")
                            break
                    elif colnames[i] == 'partner_shipping_id':
                        partner = self.env['res.partner'].sudo().search([('old_id', '=', record[i])])
                        for part in partner:
                            data['partner_shipping_id'] = part.id
                            _logger.info("PARTNER SHIPPING IMA")
                            break
                    elif colnames[i] == 'opportunity_id':
                        if record[i]:
                            crm_lead = self.env['crm.lead'].sudo().search([('old_id', '=', record[i])])
                            data['opportunity_id'] = crm_lead.id
                            _logger.info("OPPURTUNITY INVOICE IMA")
                    elif colnames[i] == 'warehouse_id':
                        data['old_warehouse_id'] = record[i] # KJE TREBA DA SE UPDATNE
                    elif colnames[i] == 'user_id':
                        user = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                        data['user_id'] = user.id
                    else:
                        data[colnames[i]] = record[i]
                data.pop('message_last_post')
                data.pop('openupgrade_legacy_12_0_commitment_date')
                data.pop('auto_generated')
                data.pop('auto_purchase_order_id')
                data.pop('margin')
                data.pop('quote_viewed')
                data.pop('require_payment_moved0')
                data.pop('template_id')
                data.pop('openupgrade_legacy_12_0_payment_tx_id')
                data.pop('payment_acquirer_id')
                data.pop('delivery_price')
                data.pop('invoice_shipping_on_delivery')
                data.pop('confirmation_date')
                data.pop('openupgrade_legacy_12_0_activity_date_deadline')
                sale_order = self.env['sale.order'].sudo().search([('old_id', '=',data['old_id'])])
                _logger.info(f"{data}")
                if sale_order:
                    _logger.info('EXIST')
                else:
                    if 'pricelist_id' in data and 'partner_id' in data:
                        _logger.info('CREATE')
                        self.env['sale.order'].sudo().create(data)
                _logger.info("\n")
                _logger.info("\n")

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"{error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def same_fields_check(self,list_v12_fields,list_v14_fields):
        final_list_fields=[]
        for field in list_v12_fields:
            if field in list_v14_fields:
                final_list_fields.append(field)
        return final_list_fields

    #PARTNERS
    def new_company_migrate(self):
        try:
            _logger.info("RES COMPANY MIGRATE")
            cli_commands = tl.config
            connection1 = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor1 = connection1.cursor()
            cursor1.execute("Select * FROM res_company LIMIT 0")
            list_fields_v12 = [desc[0] for desc in cursor1.description]
            # _logger.info(f"fields vo 12ka {list_fields_v12}")


            connection2 = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                          password=cli_commands.get('local_odoo_db_password'),
                                          host="172.19.0.2",
                                          port="5432",
                                          database="najnovaDB-merge")

            cursor2 = connection2.cursor()
            cursor2.execute("Select * FROM res_company LIMIT 0")
            list_fields_v14 = [desc[0] for desc in cursor2.description]


            query = '''SELECT * FROM res_company; '''
            cursor1.execute(query)
            companies = cursor1.fetchall()
            for record in companies:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(list_fields_v12)):
                    if list_fields_v12[i] == 'partner_id':
                        data['old_partner_id'] = record[i]
                    elif list_fields_v12[i] == 'parent_id':
                        data['old_parent_id'] = record[i]
                    else:
                        data[list_fields_v12[i]] = record[i]

                for key in list(data):
                    if key not in list_fields_v14:
                        _logger.info(f"ne e vo 14ka {key}")
                        data.pop(key)
                data.pop('project_time_mode_id')
                data.pop('vat_check_vies')
                data.pop('timesheet_encode_uom_id')
                data.pop('font')
                data.pop('fiscalyear_last_month')
                _logger.info(f"{data}")
                company = self.env['res.company'].search([('old_id','=',data['old_id'])])
                if company:
                    # company.write({'old_id': data['old_id']})
                    company.write(data)
                    _logger.info('\n')
                    _logger.info('\n')
                else:
                    try:
                        self.env['res.company'].sudo().create(data)
                        _logger.info('\n')
                        _logger.info('\n')
                    except (Exception) as error:
                        logging.exception(f"Error while creating a new company: {error} ")
                        _logger.info('\n')
                        _logger.info('\n')
                        continue


        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection1):
                cursor1.close()
                connection1.close()
                print("PostgreSQL connection is closed")

    def new_res_partner_migrate(self):
        try:
            _logger.info("NEW PARTNER MIGRATE")
            cli_commands = tl.config
            connection1 = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor1 = connection1.cursor()
            cursor1.execute("Select * FROM res_partner LIMIT 0")
            list_fields_v12 = [desc[0] for desc in cursor1.description]
            # _logger.info(f"fields vo 12ka {list_fields_v12}")


            connection2 = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                          password=cli_commands.get('local_odoo_db_password'),
                                          host="172.19.0.2",
                                          port="5432",
                                          database="v14-empty")

            cursor2 = connection2.cursor()
            cursor2.execute("Select * FROM res_partner LIMIT 0")
            list_fields_v14 = [desc[0] for desc in cursor2.description]

            query_job = '''SELECT * FROM res_partner; '''
            cursor1.execute(query_job)
            records = cursor1.fetchall()

            for record in records:
                _logger.info(f"rekordot {record}")
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(list_fields_v12)):
                    # print(f'{colnames[i]} : {record[i]}')
                    if list_fields_v12[i] == 'company_id':
                        data['old_company_id'] = record[i]
                    elif list_fields_v12[i] == 'user_id':
                        data['old_user_id'] = record[i]
                    else:
                        data[list_fields_v12[i]] = record[i]
                for key in list(data):
                    if key not in list_fields_v14:
                        data.pop(key)
                data.pop('commercial_partner_id')
                _logger.info(f"FINAL DATA {data}")
                flag = 0
                if data['email']:
                    name = data['name'].strip()
                    name = name.replace("  ", " ")
                    partners = self.env['res.partner'].sudo().search(
                        [('name', "ilike", name), ('email', 'ilike', data['email'])])
                else:
                    name = data['name'].strip()
                    name = name.replace("  ", " ")
                    partners = self.env['res.partner'].sudo().search(
                        [('name', "ilike", name)])
                if partners:
                    for partner in partners:
                        flag = 1
                        _logger.info("EXIST")
                        partner.write({
                            'old_id': data['old_id']
                        })
                        break

                if flag == 0:
                    try:
                        _logger.info("CREATE")
                        self.env['res.partner'].sudo().create(data)
                    except (Exception, psycopg2.Error) as error:
                        _logger.info(f"Error while creating a partner {error}")
                        _logger.info("\n")
                        _logger.info("\n")
                        continue
                _logger.info("\n")
                _logger.info("\n")


        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection1):
                cursor1.close()
                connection1.close()
                print("PostgreSQL connection is closed")

    def new_res_partner_message(self):
        try:
            cli_commands = tl.config
            connection1 = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor1 = connection1.cursor()
            cursor1.execute("Select * FROM mail_message LIMIT 0")
            colnames = [desc[0] for desc in cursor1.description]
            # _logger.info(f"fields vo 12ka {list_fields_v12}")


            connection2 = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                          password=cli_commands.get('local_odoo_db_password'),
                                          host="172.19.0.2",
                                          port="5432",
                                          database="v14-empty")

            cursor2 = connection2.cursor()
            cursor2.execute("Select * FROM mail_message LIMIT 0")
            list_fields_v14 = [desc[0] for desc in cursor2.description]
            # _logger.info(f"fields vo 14ka {list_fields_v14}")

            # colnames = self.same_fields_check(list_fields_v12,list_fields_v14)
            #_logger.info(f"zaednicki fildovi se {colnames}")
            query = '''SELECT * FROM mail_message where model='res.partner'; '''
            cursor1.execute(query)
            records = cursor1.fetchall()
            for record in records:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'parent_id':
                        data['old_parent_id'] = record[i]
                    elif colnames[i] == 'author_id':
                        partner = self.env['res.partner'].sudo().search([('old_id', '=', record[i])])
                        if partner:
                            for p in partner:
                                data['author_id'] = p.id
                                break
                    elif colnames[i] == 'subtype_id':
                        data['old_subtype_id'] = record[i]
                    elif colnames[i] == 'res_id':
                        data['old_res_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]
                for key in list(data):
                    if key not in list_fields_v14:
                        data.pop(key)
                messages = self.env['mail.message'].sudo().search([('old_id', '=', data['old_id'])])
                if messages:
                    for message in messages:
                        if data['old_id'] == message.old_id:
                            _logger.info('WRITE')
                            new_partner_id = self.env['res.partner'].sudo().search(
                                [('old_id', '=', data['old_res_id'])])
                            for new_id in new_partner_id:
                                _logger.info({new_id.id})
                                message.write({'res_id': new_id.id})
                                break
                else:
                    _logger.info('CREATE')
                    new_partner_id = self.env['res.partner'].sudo().search([('old_id', '=', data['old_res_id'])])
                    for new_id in new_partner_id:
                        _logger.info(f'{new_id.id}')
                        data['res_id'] = new_id.id
                        break
                    self.env['mail.message'].sudo().create(data)

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection1):
                cursor1.close()
                connection1.close()
                _logger.info("PostgreSQL connection is closed")

    def new_res_partner_attachments(self):
        try:
            _logger.info("ATTACHMENTS MIGRATE")
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

            cursor.execute("Select * FROM ir_attachment LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            # print(colnames)
            query = '''SELECT * FROM ir_attachment where res_model='res.partner'; '''
            cursor.execute(query)
            attachments = cursor.fetchall()

            connection2 = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                           password=cli_commands.get('local_odoo_db_password'),
                                           host="172.19.0.2",
                                           port="5432",
                                           database="v14-empty")

            cursor2 = connection2.cursor()
            cursor2.execute("Select * FROM ir_attachment LIMIT 0")
            list_fields_v14 = [desc[0] for desc in cursor2.description]
            _logger.info(f"FILDOVI VO 14ka{list_fields_v14}")
            for record in attachments:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'company_id':
                        companies = self.env['res.company'].sudo().search([('old_id', '=', record[i])])
                        if companies:
                            for company in companies:
                                data['company_id'] = company.id
                    elif colnames[i] == 'create_uid':
                        users = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                        if users:
                            for user in users:
                                data['create_uid'] = user.id
                    elif colnames[i] == 'write_uid':
                        users = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                        if users:
                            for user in users:
                                data['create_uid'] = user.id
                    elif colnames[i] == 'res_id':
                        partners = self.env['res.partner'].sudo().search([('old_id', '=', record[i])])
                        _logger.info(f"{partners}")
                        if partners:
                            for partner in partners:
                                data['res_id'] = partner.id
                    else:
                        data[colnames[i]] = record[i]

                for key in list(data):
                    if key not in list_fields_v14:
                        data.pop(key)

                _logger.info(f"DATATA E {data}")
                try:
                    _logger.info("CREATE")
                    self.env['ir.attachment'].sudo().create(data)
                    _logger.info("\n")
                    _logger.info("\n")
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

    def new_res_partner_update(self):
        cli_commands = tl.config
        connection1 = psycopg2.connect(user=cli_commands.get('user_name'),
                                       password=cli_commands.get('local_password'),
                                       host="172.17.0.1",
                                       port="5432",
                                       database="v12cc-sabota")

        cursor1 = connection1.cursor()
        query_job = '''SELECT id,parent_id FROM res_partner; '''
        cursor1.execute(query_job)
        old_partners = cursor1.fetchall()
        for partner in old_partners:
            _logger.info(f"{partner}")
            new_partner = self.env['res.partner'].sudo().search([('old_id','=',partner[0])])
            parent_id = self.env['res.partner'].sudo().search([('old_id','=',partner[1])])
            company = self.env['res.company'].sudo().search([('old_id','=',new_partner.old_company_id)])
            try:
                _logger.info("UPDATE")
                new_partner.write({
                    'parent_id' : parent_id,
                    'company_id' : company.id
                })
                _logger.info('\n')
                _logger.info('\n')
            except (Exception) as error:
                logging.exception(f"Error while updating a partner: {error} ")
                _logger.info('\n')
                _logger.info('\n')
                continue

    #APPLICANTS NEW
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
                #for pair in data.items():
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
                #for pair in data.items():
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
                #for pair in data.items():
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
                            'old_id' : data['old_id'],
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
                    tuple = (data['hr_applicant_id'],data['hr_applicant_category_id'])
                    if tuple not in records_in_relation:
                        _logger.info(f"{tuple}")
                        query1 = f"INSERT INTO hr_applicant_hr_applicant_category_rel(hr_applicant_id, hr_applicant_category_id) VALUES({data['hr_applicant_id']},{data['hr_applicant_category_id']});"
                        #print(query1)
                        cursor1.execute(query1)
                        connection1.commit()


        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                #cursor1.close()
                #connection1.close()
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
                        'old_id' : data_job['old_id']
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
                #self.env['hr.recruitment.stage'].create(data)
                stage = self.env['hr.recruitment.stage'].sudo().search([('name','ilike',data['name'])])
                if stage:
                    stage.write({
                        'old_id' : data['old_id']
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
               if applicant.old_job_id == job.old_id and applicant.old_job_id > 1 :
                   applicant.sudo().write({'job_id': job.id})
            for stage in stages:
               if applicant.old_stage_id == stage.old_id:
                   applicant.sudo().write({'stage_id': stage.id})

    def new_hr_applicants_creation_in_res_partner(self):
        _logger.info("DALI RABOTI")
        applicants = self.env['hr.applicant'].sudo().search([])
        data={}
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
                data={}

    def new_hr_applicant_messages(self):
        try:
            cli_commands = tl.config
            connection1 = psycopg2.connect(user=cli_commands.get('user_name'),
                                           password=cli_commands.get('local_password'),
                                           host="172.17.0.1",
                                           port="5432",
                                           database="v12cc-sabota")

            cursor1 = connection1.cursor()
            cursor1.execute("Select * FROM mail_message LIMIT 0")
            colnames = [desc[0] for desc in cursor1.description]
            # _logger.info(f"fields vo 12ka {list_fields_v12}")

            connection2 = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                           password=cli_commands.get('local_odoo_db_password'),
                                           host="172.19.0.2",
                                           port="5432",
                                           database="v14-empty")

            cursor2 = connection2.cursor()
            cursor2.execute("Select * FROM mail_message LIMIT 0")
            list_fields_v14 = [desc[0] for desc in cursor2.description]

            query = '''SELECT * FROM mail_message where model='hr.applicant'; '''
            cursor1.execute(query)
            records = cursor1.fetchall()
            for record in records:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'parent_id':
                        data['old_parent_id'] = record[i]
                    elif colnames[i] == 'author_id':
                        partner = self.env['res.partner'].sudo().search([('old_id', '=', record[i])])
                        if partner:
                            for p in partner:
                                data['author_id'] = p.id
                                break
                    elif colnames[i] == 'subtype_id':
                        data['old_subtype_id'] = record[i]
                    elif colnames[i] == 'res_id':
                        data['old_res_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]
                for key in list(data):
                    if key not in list_fields_v14:
                        data.pop(key)
                messages = self.env['mail.message'].sudo().search([('old_id', '=', data['old_id'])])
                if messages:
                    for message in messages:
                        if data['old_id'] == message.old_id:
                            _logger.info('WRITE')
                            new_partner_id = self.env['hr.applicant'].sudo().search(
                                [('old_id', '=', data['old_res_id'])])
                            for new_id in new_partner_id:
                                _logger.info({new_id.id})
                                message.write({'res_id': new_id.id})
                                break
                else:
                    _logger.info('CREATE')
                    new_partner_id = self.env['hr.applicant'].sudo().search([('old_id', '=', data['old_res_id'])])
                    for new_id in new_partner_id:
                        _logger.info(f'{new_id.id}')
                        data['res_id'] = new_id.id
                        break
                    self.env['mail.message'].sudo().create(data)

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection1):
                cursor1.close()
                connection1.close()
                _logger.info("PostgreSQL connection is closed")

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

    def new_hr_applicant_attachments(self):
        try:
            _logger.info("ATTACHMENTS MIGRATE")
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

            cursor.execute("Select * FROM ir_attachment LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            # print(colnames)
            query = '''SELECT * FROM ir_attachment where res_model='hr.applicant'; '''
            cursor.execute(query)
            attachments = cursor.fetchall()

            connection2 = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                           password=cli_commands.get('local_odoo_db_password'),
                                           host="172.19.0.2",
                                           port="5432",
                                           database="v14-empty")

            cursor2 = connection2.cursor()
            cursor2.execute("Select * FROM ir_attachment LIMIT 0")
            list_fields_v14 = [desc[0] for desc in cursor2.description]
            _logger.info(f"FILDOVI VO 14ka{list_fields_v14}")
            for record in attachments:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'company_id':
                        companies = self.env['res.company'].sudo().search([('old_id', '=', record[i])])
                        if companies:
                            for company in companies:
                                data['company_id'] = company.id
                    elif colnames[i] == 'create_uid':
                        users = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                        if users:
                            for user in users:
                                data['create_uid'] = user.id
                    elif colnames[i] == 'write_uid':
                        users = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                        if users:
                            for user in users:
                                data['create_uid'] = user.id
                    elif colnames[i] == 'res_id':
                        partners = self.env['hr.applicant'].sudo().search([('old_id', '=', record[i])])
                        _logger.info(f"{partners}")
                        if partners:
                            for partner in partners:
                                data['res_id'] = partner.id
                    else:
                        data[colnames[i]] = record[i]

                for key in list(data):
                    if key not in list_fields_v14:
                        data.pop(key)

                _logger.info(f"DATATA E {data}")
                try:
                    _logger.info("CREATE")
                    self.env['ir.attachment'].sudo().create(data)
                    _logger.info("\n")
                    _logger.info("\n")
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

    #CRM NEW
    def new_crm_lead_migrate(self):
        try:
            _logger.info("CRM LEAD MIGRATE")
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

            cursor.execute("Select * FROM crm_lead LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            # print(colnames)
            query = '''SELECT * FROM crm_lead; '''
            cursor.execute(query)
            records = cursor.fetchall()

            connection2 = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                           password=cli_commands.get('local_odoo_db_password'),
                                           host="172.19.0.2",
                                           port="5432",
                                           database="v14-empty")

            cursor2 = connection2.cursor()
            cursor2.execute("Select * FROM hr_applicant LIMIT 0")
            list_fields_v14 = [desc[0] for desc in cursor2.description]
            # _logger.info(f"FILDOVI VO 14ka {list_fields_v14}")
            for record in records:
                _logger.info(f"{record}")
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'country_id':
                        data['old_country_id'] = record[i] # KJE TREBA TRANSFER I NA RES.COUNTRY
                    elif colnames[i] == 'team_id':
                        data['old_team_id'] = record[i]
                    elif colnames[i] == 'partner_id':# NAOGJA MNOGU SO OLD_ID ISTO
                        partner_exist = self.env['res.partner'].sudo().search([('old_id', '=', record[i])])
                        if partner_exist:
                            for partner in partner_exist:
                                data['partner_id'] = partner.id
                                break
                    elif colnames[i] == 'company_id':
                        company_exist = self.env['res.company'].sudo().search([('old_id', '=', record[i])])
                        if company_exist:
                            data['company_id'] = company_exist.id
                    elif colnames[i] == 'stage_id':
                        data['old_stage_id'] = record[i]
                    elif colnames[i] == 'message_main_attachment_id': # PRASAJ ZA ATTACHMENTS
                        data['old_message_main_attachment_id'] = record[i]
                    elif colnames[i] == 'title': #najverojatno kje treba da se sredi
                        data['old_title'] = record[i]
                    elif colnames[i] == 'source_id':
                        data['old_source_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]

                for key in list(data):
                    if key not in list_fields_v14:
                        data.pop(key)
                data.pop('user_id')
                data.pop('campaign_id')
                _logger.info(f"{data}")
                crm_lead_exist = self.env['crm.lead'].sudo().search([('old_id', '=', data['old_id'])])
                if crm_lead_exist:
                    _logger.info("EXIST")
                    _logger.info('\n')
                else:
                    _logger.info("CREATE")
                    _logger.info('\n')
                    self.env['crm.lead'].sudo().create(data)



        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def new_crm_lead_team_and_country_old_id_update(self):
        try:
            _logger.info("CRM LEAD MIGRATE")
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
            query = '''SELECT id,country_id,team_id FROM crm_lead; '''
            cursor.execute(query)
            records = cursor.fetchall()
            for record in records:
                _logger.info(f"{record}")
                crm_lead = self.env['crm.lead'].sudo().search([('old_id', '=', record[0])])
                if crm_lead:
                    crm_lead.write({
                        'old_country_id' : record[1],
                        'old_team_id' : record[2]
                    })

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def new_crm_lead_tag_migrate_db(self):
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
            _logger.info(f"You are connected to -  {record}")
            cursor.execute("Select * FROM crm_lead_tag LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM crm_lead_tag; '''
            cursor.execute(query)
            records_crm_lead_tag = cursor.fetchall()
            for record in records_crm_lead_tag:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'team_id':
                        data['old_team_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]

                data.pop('create_uid')
                data.pop('write_uid')
                crm_tag_exist =  self.env['crm.tag'].sudo().search([('name', '=', data['name'])])
                if not crm_tag_exist:
                    _logger.info("CREATE")
                    self.env['crm.tag'].sudo().create(data)
                else:
                    _logger.info("EXIST")
                    crm_tag_exist.write({
                        'old_id' : data['old_id'],
                        'old_team_id' : data['old_team_id']
                    })

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def new_update_relation_crm_lead_tag(self):
        _logger.info('UPDATE RELATION CRM_LEAD - CRM_TAG')
        try:
            connection = psycopg2.connect(user="odoo",
                                          password="odoo",
                                          host="172.19.0.2",
                                          port="5432",
                                          database="v14-empty")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            _logger.info(f'{connection.get_dsn_parameters()}')

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            _logger.info(f"You are connected to - {record}")
            query1 = '''SELECT * FROM crm_tag_rel; '''
            cursor.execute(query1)
            records_in_relations_v14 = cursor.fetchall()

            cli_commands = tl.config
            connection2 = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor2 = connection2.cursor()
            # Print PostgreSQL Connection properties
            _logger.info(f'{connection2.get_dsn_parameters()}')

            # Print PostgreSQL version
            cursor2.execute("SELECT version();")
            record = cursor2.fetchone()
            _logger.info(f"You are connected to - {record}")
            query2 = '''SELECT * FROM crm_lead_tag_rel; '''
            cursor2.execute(query2)
            records_in_relations_v12 = cursor2.fetchall()

            for record in records_in_relations_v12:
                _logger.info(f"ova e torkata od v12 {record}")
                _logger.info(f"ova e id na crm_lead {record[0]}")
                _logger.info(f"ova e id na crm_tag {record[1]}")
                kveri = f'''SELECT old_id,id FROM crm_lead where old_id = {record[0]}; '''
                cursor.execute(kveri)
                crm_lead_v14 = cursor.fetchall()
                for rec in crm_lead_v14:
                    _logger.info(f"ova e new id od crm_lead {rec[1]}, a ova e old_id {rec[0]}")
                    crm_lead_new_id = rec[1]
                crm_tag_v14 = self.env['crm.tag'].sudo().search([('old_id', '=', record[1])])
                _logger.info(f"ova e new id od crm_tag {crm_tag_v14.id}, a ova e old_id {crm_tag_v14.old_id}")
                crm_tag_new_id = crm_tag_v14.id
                if type(crm_lead_new_id) is int and type(crm_tag_new_id) is int:
                    tuple_for_relation = (crm_lead_new_id, crm_tag_new_id)
                    _logger.info(f"ova e torkata za relacija {tuple_for_relation}")
                    if tuple_for_relation not in records_in_relations_v14:
                        _logger.info("CREATE")
                        query = f"INSERT INTO crm_tag_rel(lead_id, tag_id) VALUES({crm_lead_new_id},{crm_tag_new_id});"
                        cursor.execute(query)
                        connection.commit()

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

    def new_crm_stage_migrate_db(self):
        try:
            _logger.info("CRM STAGE MIGRATE")
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
            cursor.execute("Select * FROM crm_stage LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM crm_stage; '''
            cursor.execute(query)
            records_crm_stage = cursor.fetchall()

            connection2 = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                           password=cli_commands.get('local_odoo_db_password'),
                                           host="172.19.0.2",
                                           port="5432",
                                           database="v14-empty")

            cursor2 = connection2.cursor()
            cursor2.execute("Select * FROM crm_stage LIMIT 0")
            list_fields_v14 = [desc[0] for desc in cursor2.description]

            for record in records_crm_stage:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'team_id':
                        data['old_team_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]
                for key in list(data):
                    if key not in list_fields_v14:
                        data.pop(key)
                crm_stage_exist = self.env['crm.stage'].sudo().search([('name', '=', data['name'])])
                if not crm_stage_exist:
                    self.env['crm.stage'].sudo().create(data)
                else:
                    crm_stage_exist.write({
                        'old_id' : data['old_id']
                    })


        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def new_crm_team_migrate_db(self):
        try:
            _logger.info("CRM TEAM MIGRATE")
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
            cursor.execute("Select * FROM crm_team LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM crm_team; '''
            cursor.execute(query)
            records_crm_stage = cursor.fetchall()

            connection2 = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                           password=cli_commands.get('local_odoo_db_password'),
                                           host="172.19.0.2",
                                           port="5432",
                                           database="v14-empty")

            cursor2 = connection2.cursor()
            cursor2.execute("Select * FROM crm_stage LIMIT 0")
            list_fields_v14 = [desc[0] for desc in cursor2.description]

            for record in records_crm_stage:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'user_id':
                        data['old_user_id'] = record[i]
                    elif colnames[i] == 'company_id':
                        data['old_company_id'] = record[i]
                    elif colnames[i] == 'alias_id':
                        data['old_alias_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]
                for key in list(data):
                    if key not in list_fields_v14:
                        data.pop(key)
                crm_teams = self.env['crm.team'].sudo().search([('name', '=', data['name'])])
                if not crm_teams:
                    _logger.info('CREATE')
                    self.env['crm.team'].sudo().create(data)
                else:
                    crm_teams.write({
                        'old_id' : data['old_id']
                    })


        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def new_crm_lead_team_update(self):
        crm_leads = self.env['crm.lead'].sudo().search([])
        for crm_lead in crm_leads:
            _logger.info(f'staroto old_team_id {crm_lead.old_team_id}')
            team = self.env['crm.team'].sudo().search([('old_id', '=', crm_lead.old_team_id)])
            _logger.info(f'staroto old_id {team.old_id}')
            _logger.info(f'novoto team_id {team.id}')
            if team:
                crm_lead.write({'team_id': team.id})

    def new_crm_lead_stage_update(self):
        crm_leads = self.env['crm.lead'].sudo().search([])
        for crm_lead in crm_leads:
            _logger.info(f'staroto old_stage_id {crm_lead.old_stage_id}')
            stage = self.env['crm.stage'].sudo().search([('old_id', '=', crm_lead.old_stage_id)])
            _logger.info(f'staroto old_id {stage.old_id}')
            _logger.info(f'novoto team_id {stage.id}')
            crm_lead.write({'stage_id': stage.id})

    def new_res_country_migrate(self):
        try:
            _logger.info("COUNTRY MIGRATE")
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
            cursor.execute("Select * FROM res_country LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM res_country; '''
            cursor.execute(query)
            records_crm = cursor.fetchall()

            connection2 = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                           password=cli_commands.get('local_odoo_db_password'),
                                           host="172.19.0.2",
                                           port="5432",
                                           database="v14-empty")

            cursor2 = connection2.cursor()
            cursor2.execute("Select * FROM crm_stage LIMIT 0")
            list_fields_v14 = [desc[0] for desc in cursor2.description]

            for record in records_crm:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'currency_id':
                        data['old_currency_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]
                for key in list(data):
                    if key not in list_fields_v14:
                        data.pop(key)
                country = self.env['res.country'].sudo().search([('name', '=', data['name'])])
                if not country:
                    _logger.info('CREATE')
                    self.env['res.country'].sudo().create(data)
                else:
                    _logger.info('EXIST')
                    country.write({
                        'old_id' : data['old_id']
                    })

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def new_res_currency_migrate(self):
        try:
            _logger.info("CURRENCY MIGRATE")
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
            cursor.execute("Select * FROM res_currency LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT * FROM res_currency; '''
            cursor.execute(query)
            records_crm = cursor.fetchall()
            for record in records_crm:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    data[colnames[i]] = record[i]
                name = data['name'].strip()
                name = name.replace("  ", " ")
                currency = self.env['res.currency'].sudo().search([('name','=',name),'|',
                                            ('active','=',False),('active','=',True)])
                if not data['symbol']:
                    data['symbol'] = 'nema simbol'
                if not currency:
                    _logger.info('CREATE')
                    self.env['res.currency'].sudo().create(data)
                else:
                    _logger.info('EXIST')
                    currency.write({
                        'old_id' : data['old_id']
                    })

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")

    def new_update_country_currency(self):
        countries = self.env['res.country'].sudo().search([])
        for country in countries:
            currency = self.env['res.currency'].sudo().search([('old_id','=',country.old_currency_id)])
            country.write({
                'currency_id' : currency.id
            })

    def new_update_crm_lead_country(self):
        crm_leads = self.env['crm.lead'].sudo().search([])
        _logger.info('CRM LEAD COUNTRY UPDATE')
        for crm_lead in crm_leads:
            _logger.info(f'staroto old_crm_lead_country_id {crm_lead.old_country_id}')
            country = self.env['res.country'].sudo().search([('old_id', '=', crm_lead.old_country_id)])
            _logger.info(f'staroto old_id {country.old_id}')
            _logger.info(f'novoto country id {country.id}')
            crm_lead.write({
                'country_id': country.id
            })

    #so aleks muabet da napravis
    def new_res_user_db(self):
        try:
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('user_name'),
                                          password=cli_commands.get('local_password'),
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc-sabota")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            # _logger.info(f'{connection.get_dsn_parameters()}')

            # Print PostgreSQL version
            cursor.execute("SELECT version();")
            record = cursor.fetchone()
            print("You are connected to - ", record, "\n")
            cursor.execute("Select * FROM res_users LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query_job = '''SELECT * FROM res_users; '''
            cursor.execute(query_job)
            records_jobs = cursor.fetchall()
            print(len(records_jobs))
            companies = self.env['res.company'].search([])

            connection2 = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                           password=cli_commands.get('local_odoo_db_password'),
                                           host="172.19.0.2",
                                           port="5432",
                                           database="v14-empty")

            cursor2 = connection2.cursor()
            cursor2.execute("Select * FROM crm_stage LIMIT 0")
            list_fields_v14 = [desc[0] for desc in cursor2.description]

            for job in records_jobs:
                _logger.info(f"{job}")
                data_job = {}
                data_job['old_id'] = job[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'partner_id':
                        partner = self.env['res.partner'].sudo().search([('old_id','=',job[i])])
                        for p in partner:
                            data_job['partner_id'] = p.id
                        # data_job['partner_id'] = 1
                    elif colnames[i] == 'company_id':
                        data_job['old_company_id'] = job[i]
                        for company in companies:
                            if job[i] == company.old_id:
                                data_job['company_id'] = company.id
                    else:
                        data_job[colnames[i]] = job[i]
                # for key in list(data_job):
                #     if key not in list_fields_v14:
                #         data_job.pop(key)
                _logger.info(f"{data_job}")
                users_active = self.env['res.users'].sudo().search([])
                users_passive = self.env['res.users'].sudo().search([('active', '=', False)])
                flag = 0
                for user in users_active:
                    if data_job['login'] in user.login:
                        user.write({'old_id': data_job['old_id']})
                        flag += 1
                for user in users_passive:
                    if data_job['login'] in user.login:
                        user.write({'old_id': data_job['old_id']})
                        flag += 1
                if 'name' not in data_job:
                    data_job['name'] = data_job['login']
                _logger.info(f"{data_job}")
                _logger.info(f"{data_job['login']}")
                self.env['res.users'].sudo().create(data_job)


        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")

    def new_crm_lead_user_update(self):
        try:
            _logger.info("CRM LEAD USER UPDATE")
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
            cursor.execute("Select * FROM crm_lead LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            query = '''SELECT id,user_id FROM crm_lead; '''
            cursor.execute(query)
            records_crm = cursor.fetchall()
            for record in records_crm:
                _logger.info(f"old id = {record[0]}, a user_id = {record[1]}")
                crm_lead = self.env['crm.lead'].sudo().search([('old_id', '=', record[0])])
                _logger.info(f"crm_lead old_id {crm_lead.old_id}")
                users = self.env['res.users'].sudo().search([('old_id', '=', record[1])])
                if users:
                    for user in users:
                        _logger.info(f"user id {user.old_id}")
                        crm_lead.write({
                            'user_id': user.id
                        })
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

    def new_crm_messages(self):
        try:
            cli_commands = tl.config
            connection1 = psycopg2.connect(user=cli_commands.get('user_name'),
                                           password=cli_commands.get('local_password'),
                                           host="172.17.0.1",
                                           port="5432",
                                           database="v12cc-sabota")

            cursor1 = connection1.cursor()
            cursor1.execute("Select * FROM mail_message LIMIT 0")
            colnames = [desc[0] for desc in cursor1.description]
            # _logger.info(f"fields vo 12ka {list_fields_v12}")

            connection2 = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                           password=cli_commands.get('local_odoo_db_password'),
                                           host="172.19.0.2",
                                           port="5432",
                                           database="v14-empty")

            cursor2 = connection2.cursor()
            cursor2.execute("Select * FROM mail_message LIMIT 0")
            list_fields_v14 = [desc[0] for desc in cursor2.description]
            # _logger.info(f"fields vo 14ka {list_fields_v14}")

            # colnames = self.same_fields_check(list_fields_v12,list_fields_v14)
            # _logger.info(f"zaednicki fildovi se {colnames}")
            query = '''SELECT * FROM mail_message where model='crm.lead'; '''
            cursor1.execute(query)
            records = cursor1.fetchall()

            for record in records:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'parent_id':
                        data['old_parent_id'] = record[i]
                    elif colnames[i] == 'author_id':
                        partner = self.env['res.partner'].sudo().search([('old_id', '=', record[i])])
                        if partner:
                            for p in partner:
                                data['author_id'] = p.id
                                break
                    elif colnames[i] == 'subtype_id':
                        data['old_subtype_id'] = record[i]
                    elif colnames[i] == 'res_id':
                        data['old_res_id'] = record[i]
                    else:
                        data[colnames[i]] = record[i]
                for key in list(data):
                    if key not in list_fields_v14:
                        data.pop(key)
                data.pop('mail_activity_type_id')
                messages = self.env['mail.message'].sudo().search([('old_id', '=', data['old_id'])])
                if messages:
                    for message in messages:
                        if data['old_id'] == message.old_id:
                            _logger.info('WRITE')
                            new_partner_id = self.env['crm.lead'].sudo().search(
                                [('old_id', '=', data['old_res_id'])])
                            for new_id in new_partner_id:
                                _logger.info({new_id.id})
                                message.write({'res_id': new_id.id})
                                break
                else:
                    _logger.info('CREATE')
                    new_partner_id = self.env['crm.lead'].sudo().search([('old_id', '=', data['old_res_id'])])
                    for new_id in new_partner_id:
                        _logger.info(f'{new_id.id}')
                        data['res_id'] = new_id.id
                        break
                    self.env['mail.message'].sudo().create(data)

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection1):
                cursor1.close()
                connection1.close()
                _logger.info("PostgreSQL connection is closed")

    def new_crm_lead_attachments(self):
        try:
            _logger.info("ATTACHMENTS MIGRATE")
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

            cursor.execute("Select * FROM ir_attachment LIMIT 0")
            colnames = [desc[0] for desc in cursor.description]
            # print(colnames)
            query = '''SELECT * FROM ir_attachment where res_model='crm.lead'; '''
            cursor.execute(query)
            attachments = cursor.fetchall()

            connection2 = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                           password=cli_commands.get('local_odoo_db_password'),
                                           host="172.19.0.2",
                                           port="5432",
                                           database="v14-empty")

            cursor2 = connection2.cursor()
            cursor2.execute("Select * FROM ir_attachment LIMIT 0")
            list_fields_v14 = [desc[0] for desc in cursor2.description]
            _logger.info(f"FILDOVI VO 14ka{list_fields_v14}")
            for record in attachments:
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(colnames)):
                    if colnames[i] == 'company_id':
                        companies = self.env['res.company'].sudo().search([('old_id', '=', record[i])])
                        if companies:
                            for company in companies:
                                data['company_id'] = company.id
                    elif colnames[i] == 'create_uid':
                        users = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                        if users:
                            for user in users:
                                data['create_uid'] = user.id
                    elif colnames[i] == 'write_uid':
                        users = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                        if users:
                            for user in users:
                                data['create_uid'] = user.id
                    elif colnames[i] == 'res_id':
                        partners = self.env['crm.lead'].sudo().search([('old_id', '=', record[i])])
                        _logger.info(f"{partners}")
                        if partners:
                            for partner in partners:
                                data['res_id'] = partner.id
                    else:
                        data[colnames[i]] = record[i]

                for key in list(data):
                    if key not in list_fields_v14:
                        data.pop(key)

                _logger.info(f"DATATA E {data}")
                try:
                    _logger.info("CREATE")
                    self.env['ir.attachment'].sudo().create(data)
                    _logger.info("\n")
                    _logger.info("\n")
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


    def run(self):
        # RES.PARTNER

        self.new_company_migrate()
        self..new_res_partner_migrate()

        # HR.APPLICANT MIGRATION

        self.new_hr_applicant_migrate()
        self.new_hr_applicants_creation_in_res_partner()

        self.new_res_partner_update()  # UPDATING ALL RES.PARTNER RECORDS

        self.new_hr_applicant_language_migrate()
        self.new_hr_applicant_experience_migrate()
        self.new_hr_applicant_education_migrate()
        self.new_hr_applicant_category_migrate()
        self.new_update_relation_applicant_category()
        self.new_hr_job_migrate()
        self.new_hr_department_migrate()
        self.new_update_department_db()
        self.new_hr_employee_migrate()
        self.new_hr_stage_migrate()
        self.new_update_stage()
        self.new_update_hr_applicant_db()
        self.new_followers_update_for_applicant_messages()

        # CRM

        self.new_crm_lead_migrate()
        self.new_crm_lead_team_and_country_old_id_update()
        self.new_crm_lead_tag_migrate_db()
        self.new_update_relation_crm_lead_tag()
        self.new_crm_stage_migrate_db()
        self.new_crm_team_migrate_db()
        self.new_crm_lead_team_update()
        self.new_crm_lead_stage_update()
        self.new_res_country_migrate()
        self.new_res_currency_migrate()
        self.new_update_country_currency()
        self.new_update_crm_lead_country()
        self.new_crm_lead_user_update()

        # ATTACHMENTS AND MESSAGES FOR RES.PARTNER, HR.APPLICANT and CRM

        self.new_res_partner_message()
        self.new_res_partner_attachments()
        self.new_hr_applicant_messages()
        self.new_hr_applicant_attachments()
        self.new_crm_messages()
        self.new_crm_lead_attachments()

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


class DbMigratePartners(models.Model):
    _inherit = "res.partner"
    old_id = fields.Integer(string='id before migration')
    old_company_id = fields.Integer(string='old company id res.company')
    old_user_id = fields.Integer(string='old user id')
    # x_leadsource = fields.Selection(selection_add=[('presence_holiday_absent', 'On leave'),
    #                                                   ('presence_holiday_present', 'Present but on leave')])
    # proba = fields.Integer(string='proba')


class DbMigrateUsers(models.Model):
    _inherit = "res.users"
    old_id = fields.Integer(string='id before migration')
    old_partner_id = fields.Integer(string='old partner id res.partner')
    old_company_id = fields.Integer(string='old company id res.company')


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


class DbMigrateMailMessage(models.Model):
    _inherit = 'mail.message'
    old_id = fields.Integer(string='id before migration')
    old_parent_id = fields.Integer(string='old parent id mail_message')
    old_child_ids = fields.Integer(string='old child_ids mail_message')
    old_subtype_id = fields.Integer(string='old subtype_id mail.message.subtype')
    old_res_id = fields.Integer(string='old res_id mail.message')

class DbMigrateApplicantSubtype(models.Model):
    _inherit = 'mail.message.subtype'
    old_id = fields.Integer(string='id before migration')

class DbMigrateCrm(models.Model):
    _inherit = 'crm.lead'
    old_id = fields.Integer(string='id before migration')
    old_country_id = fields.Integer(string='id of country before migration')
    old_team_id = fields.Integer(string='id of team before migration')
    old_stage_id = fields.Integer(string='id of stage before migration')
    old_message_main_attachment_id = fields.Integer(string='id of attachment before migration')
    old_title = fields.Integer(string='id of title before migration')
    old_source_id = fields.Integer(string='id of source_id before migration')

class DbMigrateCrmLeadTag(models.Model):
    _inherit = 'crm.tag'
    old_id = fields.Integer(string='id before migration')
    old_team_id = fields.Integer(string='id of team before migration')

class DbMigrateCrmStage(models.Model):
    _inherit = 'crm.stage'
    old_id = fields.Integer(string='id before migration')
    old_team_id = fields.Integer(string='id of team before migration')

class DbMigrateCrmTeam(models.Model):
    _inherit = 'crm.team'
    old_id = fields.Integer(string='id before migration')
    old_user_id = fields.Integer(string='id of user_id before migration')
    old_company_id = fields.Integer(string='id of company_id before migration')
    old_alias_id = fields.Integer(string='id of alias_id before migration')

class DbMirateCountry(models.Model):
    _inherit = 'res.country'
    old_id = fields.Integer(string='id before migration')
    old_currency_id = fields.Integer(string='id of currency before migration')

class DbMirateCurrency(models.Model):
    _inherit = 'res.currency'
    old_id = fields.Integer(string='id before migration')

class DbMigrateProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    old_id = fields.Integer(string='id before migration')


class DbMigrateSaleOrder(models.Model):
    _inherit = 'sale.order'
    old_id = fields.Integer(string='id before migration')
    old_procurement_group_id = fields.Integer(string='id of procurement_group_id before migration')
    old_analytic_account_id = fields.Integer(string='id of analytic_account_id before migration')
    old_payment_term_id = fields.Integer(string='id of payment_term_id before migration')
    old_warehouse_id = fields.Integer(string='id of warehouse_id before migration')


class DbStockLocationMigrate(models.Model):
    _inherit = 'stock.location'
    old_id = fields.Integer(string='id before migration')
    old_parent_id = fields.Integer(string='old parent id')
    old_location_id = fields.Integer(string='old parent location')