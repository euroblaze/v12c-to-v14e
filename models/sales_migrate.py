from odoo import models, fields, api , tools as tl
import xmlrpc.client
import os
import json
import logging
import datetime
import psycopg2
_logger = logging.getLogger(__name__)

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


    def product_pricelist_migrate(self):
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
                        currency = self.env['res.currency'].sudo().search([('old_id', '=', record[i])])
                        data['currency_id'] = currency.id
                    else:
                        data[colnames[i]] = record[i]
                name = data['name'].strip()
                name = name.replace("  ", " ")
                product_pricelist = self.env['product.pricelist'].sudo().search(([('name', '=', name), '|',
                                                                                  ('active', '=', False),
                                                                                  ('active', '=', True)]))
                if product_pricelist:
                    for pro in product_pricelist:
                        _logger.info('WRITE')
                        pro.write({
                            'old_id': data['old_id']
                        })
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
                        data['team_id'] = team.id
                        _logger.info("TEAM IMA")
                    elif colnames[i] == 'partner_id':
                        partner = self.env['res.partner'].sudo().search([('old_id', '=', record[i])])
                        data['partner_id'] = partner.id
                        _logger.info("PARTNER IMA")
                    elif colnames[i] == 'procurement_group_id': # KJE TREBA DA SE UPDATNE
                        data['old_procurement_group_id'] = record[i]
                    elif colnames[i] == 'company_id':
                        company = self.env['res.company'].sudo().search([('old_id', '=', record[i])])
                        data['company_id'] = company.id
                        _logger.info("COMPANY IMA")
                    elif colnames[i] == 'pricelist_id': #MOZE KJE TREBA DA SE UPDAJTNE
                        product_pricelist = self.env['product.pricelist'].sudo().search([('old_id', '=', record[i])])
                        data['pricelist_id'] = product_pricelist.id
                        _logger.info("PRICELIST IMA")
                    elif colnames[i] == 'analytic_account_id':
                        data['old_analytic_account_id'] = record[i] # KJE TREBA DA SE UPDATNE
                    elif colnames[i] == 'payment_term_id':
                        data['old_payment_term_id'] = record[i]
                    elif colnames[i] == 'partner_invoice_id':
                        _logger.info(f"{record[i]}")
                        partner = self.env['res.partner'].sudo().search([('old_id', '=', record[i])])
                        data['partner_invoice_id'] = partner[i]
                        _logger.info("PARTNER INVOICE IMA")
                    elif colnames[i] == 'partner_shipping_id':
                        partner = self.env['res.partner'].sudo().search([('old_id', '=', record[i])])
                        data['partner_shipping_id'] = partner[i]
                        _logger.info("PARTNER SHIPPING IMA")
                    elif colnames[i] == 'opportunity_id':
                        if record[i]:
                            crm_lead = self.env['crm.lead'].sudo().search([('old_id', '=', record[i])])
                            data['opportunity_id'] = crm_lead.id
                            _logger.info("OPPURTUNITY INVOICE IMA")
                    elif colnames[i] == 'warehouse_id':
                        data['old_warehouse_id'] = record[i] # KJE TREBA DA SE UPDATNE
                    else:
                        data[colnames[i]] = record[i]
                sale_order = self.env['sale.order'].sudo().search([('old_id', '=',data['old_id'])])
                if sale_order:
                    _logger.info('EXIST')
                else:
                    _logger.info('CREATE')
                    self.env['sale.order'].sudo().create(data)

        except (Exception, psycopg2.Error) as error:
            _logger.info(f"Error while connecting to PostgreSQL {error}")

        finally:
            # closing database connection.
            if (connection):
                cursor.close()
                connection.close()
                _logger.info("PostgreSQL connection is closed")