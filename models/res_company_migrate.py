from odoo import models, fields, api, tools as tl
import xmlrpc.client
import os
import json
import logging
import datetime
import psycopg2
_logger = logging.getLogger(__name__)

class DbMigrateCompany(models.Model):
    _inherit = "res.company"
    old_id = fields.Integer(string='id before migration')
    old_partner_id = fields.Integer(string='old partner id res.partner')
    old_parent_id = fields.Integer(string='old parent id res.company')

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
                company = self.env['res.company'].search([('old_id', '=', data['old_id'])])
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



