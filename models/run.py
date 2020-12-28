from odoo import models, fields, api
import xmlrpc.client
import os
import json
import logging
import datetime
import psycopg2
_logger = logging.getLogger(__name__)

class run_script(models.Model):

    def run(self):
        # RES.PARTNER

        self.env["res.partner"].res_partner_db()
        self.env["res.partner"].update_res_partner()
        self.env["mail.message"].res_partner_messages()
        self.env["mail.message"].res_partner_attachemnts()


        # HR.APPLICANT MIGRATION

        self.env["hr.applicant"].applicant_db()
        self.env["hr.applicant"].applicant_language()
        self.env["hr.applicant"].applicant_experience()
        self.env["hr.applicant"].applicant_education()
        self.env["hr.applicant"].applicant_category()
        self.env["hr.applicant"].update_relation_applicant_category()
        self.env["hr.applicant"].job_db()
        self.env["hr.applicant"].update_job_helper()
        self.env["hr.applicant"].update_job_db()
        self.env["hr.applicant"].stage_db()
        self.env["hr.applicant"].update_stage_db()
        self.env["hr.applicant"].department_db()
        self.env["hr.applicant"].update_department_db()
        self.env["res.company"].company_db()
        self.env["res.company"].update_company_db()
        self.env["hr.applicant"].update_hr_applicant_db()
        self.env["hr.applicant"].hr_applicants_creation_in_res_partner()
        self.env["mail.message"].message_mail()
        self.env["mail.message"].update_relation_message_partner()
        self.env["mail.message"].message_subtype()
        self.env["mail.message"].applicant_message_subtype_update()
        self.env["hr.applicant"].delete_all_followers_for_hr_applicants_messages()
        self.env["hr.applicant"].followers_update_for_applicant_messages()
        self.env["mail.message"].attachments_for_applicants()


        #CRM

        self.env["crm.lead"].crm_lead_migrate_db()
        self.env["crm.lead"].crm_lead_tag_migrate_db()
        self.env["crm.lead"].update_relation_crm_lead_tag()
        self.env["crm.lead"].crm_stage_migrate_db()
        self.env["crm.lead"].crm_team_migrate_db()
        self.env["crm.lead"].crm_team_stage_rel_update()
        self.env["crm.lead"].crm_lead_team_update()
        self.env["crm.lead"].crm_lead_stage_update()
        self.env["crm.lead"].res_country_migrate()
        self.env["crm.lead"].res_currency_migrate()
        self.env["crm.lead"].update_country_currency()
        self.env["crm.lead"].update_crm_lead_country()
        self.env["crm.lead"].crm_lead_user_update()
        self.env["mail.message"].crm_message_update()










