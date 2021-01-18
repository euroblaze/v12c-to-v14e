from odoo import models, fields, api ,  tools as tl
import xmlrpc.client
import os
import json
import logging
import datetime
import psycopg2
_logger = logging.getLogger(__name__)

class DbMigrateMailMessage(models.Model):
    _inherit = 'mail.message'
    old_id = fields.Integer(string='id before migration')
    old_parent_id = fields.Integer(string='old parent id mail_message')
    old_child_ids = fields.Integer(string='old child_ids mail_message')
    old_subtype_id = fields.Integer(string='old subtype_id mail.message.subtype')
    old_res_id = fields.Integer(string='old res_id mail.message')

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

class DbMigrateApplicantSubtype(models.Model):
    _inherit = 'mail.message.subtype'
    old_id = fields.Integer(string='id before migration')