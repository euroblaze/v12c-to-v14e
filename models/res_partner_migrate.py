from odoo import models, fields, api, tools as tl
import xmlrpc.client
import os
import json
import logging
import datetime
import psycopg2
_logger = logging.getLogger(__name__)

class DbMigratePartners(models.Model):
    _inherit = "res.partner"
    old_id = fields.Integer(string='id before migration')
    old_company_id = fields.Integer(string='old company id res.company')
    old_user_id = fields.Integer(string='old user id')

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
            # _logger.info(f"fields vo 14ka {list_fields_v14}")

            colnames_final = self.same_fields_check(list_fields_v12,list_fields_v14)
            # _logger.info(f"zaednicki fildovi se {colnames}")

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
                final_data={}
                for field in colnames_final:
                    if field in data:
                        final_data[field] = data[field]
                final_data['old_id'] = data['old_id']
                final_data['old_company_id'] = data['old_company_id']
                final_data['old_user_id'] = data['old_user_id']
                final_data.pop('invoice_warn')
                final_data.pop('lang')
                final_data.pop('industry_id')
                final_data.pop('partner_gid')
                final_data.pop('additional_info')
                final_data.pop('is_published')
                final_data.pop('picking_warn')
                final_data.pop('type')
                final_data.pop('commercial_partner_id')
                final_data.pop('parent_id')
                final_data.pop('team_id')
                final_data.pop('title')
                final_data.pop('state_id')
                final_data.pop('date')
                final_data.pop('signup_expiration')
                final_data.pop('message_main_attachment_id')
                final_data.pop('country_id')
                _logger.info(f"FINAL DATA {final_data}")
                flag = 0
                if final_data['email']:
                    name = final_data['name'].strip()
                    name = name.replace("  ", " ")
                    partners = self.env['res.partner'].sudo().search(
                        [('name', "ilike", name), ('email', 'ilike', final_data['email'])])
                else:
                    name = final_data['name'].strip()
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
                        self.env['res.partner'].sudo().create(final_data)
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
            new_partner = self.env['res.partner'].sudo().search([('old_id', '=', partner[0])])
            parent_id = self.env['res.partner'].sudo().search([('old_id', '=', partner[1])])
            company = self.env['res.company'].sudo().search([('old_id', '=', new_partner.old_company_id)])
            try:
                _logger.info("UPDATE")
                new_partner.write({
                    'parent_id': parent_id,
                    'company_id': company.id
                })
                _logger.info('\n')
                _logger.info('\n')
            except (Exception) as error:
                logging.exception(f"Error while updating a partner: {error} ")
                _logger.info('\n')
                _logger.info('\n')
                continue