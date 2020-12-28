from odoo import models, fields, api, tools as tl
import xmlrpc.client
import os
import json
import logging
import datetime
import psycopg2
_logger = logging.getLogger(__name__)

class DbMigrateCrm(models.Model):
    _inherit = 'crm.lead'
    old_id = fields.Integer(string='id before migration')
    old_country_id = fields.Integer(string='id of country before migration')
    old_team_id = fields.Integer(string='id of team before migration')
    old_stage_id = fields.Integer(string='id of stage before migration')
    old_message_main_attachment_id = fields.Integer(string='id of attachment before migration')
    old_title = fields.Integer(string='id of title before migration')
    old_source_id = fields.Integer(string='id of source_id before migration')

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
                        data['old_country_id'] = record[i]  # KJE TREBA TRANSFER I NA RES.COUNTRY
                    # elif colnames[i] == 'write_uid': # NAOGJA MNOGU SO OLD_ID ISTO
                    #     user_exist = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                    #     if user_exist:
                    #         _logger.info("WRITE UID USER")
                    #         data['write_uid'] = user_exist.id
                    elif colnames[i] == 'team_id':
                        data['old_team_id'] = record[i]
                    elif colnames[i] == 'partner_id':  # NAOGJA MNOGU SO OLD_ID ISTO
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
                    elif colnames[i] == 'user_id':  # NAOGJA MNOGU SO OLD_ID ISTO
                        user_exist = self.env['res.users'].sudo().search([('old_id', '=', record[i])])
                        for user in user_exist:
                            data['user_id'] = user.id
                            break
                    elif colnames[i] == 'stage_id':
                        data['old_stage_id'] = record[i]
                    elif colnames[i] == 'message_main_attachment_id':  # PRASAJ ZA ATTACHMENTS
                        data['old_message_main_attachment_id'] = record[i]
                    elif colnames[i] == 'title':  # najverojatno kje treba da se sredi
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

    def crm_lead_tag_migrate_db(self):  # PRVIOT PAT NEJKESE OLD_ID I TEAM_ID DA SE STAAT, 2 PATI JA PUSTIV ZA DA SE UPDATNE
        try:
            _logger.info("CRM_LEAD_TAG MIGRATE")
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
                crm_tag_exist = self.env['crm.tag'].sudo().search([('name', '=', data['name'])])
                if not crm_tag_exist:
                    _logger.info("CREATE")
                    self.env['crm.tag'].sudo().create(data)
                else:
                    _logger.info("EXIST")
                    crm_tag_exist.write({
                        'old_id': data['old_id'],
                        'old_team_id': data['old_team_id']
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
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                          password=cli_commands.get('local_odoo_db_password'),
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
                        'old_id': data['old_id']
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
                        'old_id': data['old_id']
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
            cli_commands = tl.config
            connection = psycopg2.connect(user=cli_commands.get('local_odoo_db_user'),
                                          password=cli_commands.get('local_odoo_db_password'),
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
                query_crm_team = f'''SELECT name FROM crm_team where id={record[1]}; '''
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
                tuple_for_relation = (crm_team_new.id, crm_stage_new_id)
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
                # cursor1.close()
                # connection1.close()
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
                        'old_id': data['old_id']
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
                currency = self.env['res.currency'].sudo().search([('name', '=', name), '|',
                                                                   ('active', '=', False), ('active', '=', True)])
                if not data['symbol']:
                    data['symbol'] = 'nema simbol'
                if not currency:
                    _logger.info('CREATE')
                    self.env['res.currency'].sudo().create(data)
                else:
                    _logger.info('EXIST')
                    currency.write({
                        'old_id': data['old_id']
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
            currency = self.env['res.currency'].sudo().search([('old_id', '=', country.old_currency_id)])
            country.write({
                'currency_id': currency.id
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