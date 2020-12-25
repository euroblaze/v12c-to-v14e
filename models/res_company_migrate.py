from odoo import models, fields, api
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

    def company_db(self):
        try:
            connection = psycopg2.connect(user="odoo",
                                          password="password",
                                          host="172.17.0.1",
                                          port="5432",
                                          database="v12cc")

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