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
            # _logger.info(f"zaednicki fildovi se {colnames}")
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
                data.pop('layout')
                data.pop('website_published')
                data.pop('sent_mobile')
                data.pop('mail_activity_type_id')
                data.pop('mail_server_id')
                # for pair in data.items():
                #    print(pair)
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
    def update_relation_message_partner(self):
        messages = self.env['mail.message'].sudo().search([('model','=','hr.applicant')])
        _logger.info('update_relation_message_partner')
        try:
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                           password=cli_commands.get('local_odoo_db_password'),
                                           host="172.19.0.2",
                                           port="5432",
                                           database="najnovaDB-sabota")

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

    def applicant_message_subtype_update(self):
        messages = self.env['mail.message'].sudo().search([('model', '=', 'hr.applicant')])
        for message in messages:
            if message.old_subtype_id == 69 or message.old_subtype_id == 70 or message.old_subtype_id == 71:
                _logger.info(f'staroto old_subtype_id {message.old_subtype_id}')
                subtype = self.env['mail.message.subtype'].sudo().search([('old_id', '=', message.old_subtype_id)])
                _logger.info(f'staroto old_id {subtype.old_id}')
                _logger.info(f'novoto subtype_id {subtype.id}')
                message.write({'subtype_id':subtype.id})

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
                    'author_id': partner.id
                })
            _logger.info("\n")
            _logger.info("\n")

class DbMigrateApplicantSubtype(models.Model):
    _inherit = 'mail.message.subtype'
    old_id = fields.Integer(string='id before migration')