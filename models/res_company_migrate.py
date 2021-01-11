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
            # _logger.info(f"fields vo 14ka {list_fields_v14}")

            colnames = self.same_fields_check(list_fields_v12, list_fields_v14)
            # _logger.info(f"zaednicki fildovi se {colnames}")

            query = '''SELECT * FROM res_company; '''
            cursor1.execute(query)
            companies = cursor1.fetchall()
            for record in companies:
                _logger.info(f"{record}")
                data = {}
                data['old_id'] = record[0]
                for i in range(1, len(list_fields_v12)):
                    if list_fields_v12[i] == 'partner_id':
                        partner = self.env['res.partner'].search([('old_id', '=', record[i])])
                        for p in partner:
                            data['partner_id'] = p.id
                            break
                        data['old_partner_id'] = record[i]
                    elif list_fields_v12[i] == 'parent_id':
                        partner = self.env['res.partner'].search([('old_id', '=', record[i])])
                        for p in partner:
                            data['parent_id'] = p.id
                            break
                        data['old_parent_id'] = record[i]
                    else:
                        data[list_fields_v12[i]] = record[i]
                final_data = {}
                for field in colnames:
                    if field in data:
                        final_data[field] = data[field]
                final_data['old_id'] = data['old_id']
                company = self.env['res.company'].search([('old_id', '=', final_data['old_id'])])
                final_data.pop('project_time_mode_id')
                final_data.pop('internal_transit_location_id')
                final_data.pop('security_lead')
                final_data.pop('vat_check_vies')
                final_data.pop('nomenclature_id')
                final_data.pop('timesheet_encode_uom_id')
                final_data.pop('fiscalyear_last_month')
                final_data.pop('font')
                final_data.pop('resource_calendar_id')
                final_data.pop('chart_template_id')
                final_data.pop('currency_exchange_journal_id')
                final_data.pop('external_report_layout_id')
                final_data.pop('parent_id')
                for i in range(len(colnames)):
                    if 'rml_' in colnames[i]:
                        final_data.pop(colnames[i])
                    elif 'account_' in colnames[i]:
                        final_data.pop(colnames[i])
                    elif 'sale_' in colnames[i]:
                        final_data.pop(colnames[i])
                    elif 'po_' in colnames[i]:
                        final_data.pop(colnames[i])
                    elif 'x_' in colnames[i]:
                        final_data.pop(colnames[i])
                    elif 'social_' in colnames[i]:
                        final_data.pop(colnames[i])
                    elif 'leave_' in colnames[i]:
                        final_data.pop(colnames[i])
                    elif 'invoice_' in colnames[i]:
                        final_data.pop(colnames[i])
                _logger.info(f"{final_data}")
                if company:
                    company.write({'old_id': final_data['old_id']})
                    _logger.info('\n')
                    _logger.info('\n')
                else:
                    try:
                        self.env['res.company'].sudo().create(final_data)
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



