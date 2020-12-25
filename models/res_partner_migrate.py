from odoo import models, fields, api
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


    def res_partner_db(self):
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

                if flag == 0:
                    _logger.info('CREATE')
                    self.env['res.partner'].create(data)
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