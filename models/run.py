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

        self.env["res.company"].new_company_migrate()
        self.env["res.partner"].new_res_partner_migrate()

        # HR.APPLICANT MIGRATION

        self.env["hr.applicant"].new_hr_applicant_migrate()
        self.env["hr.applicant"].new_hr_applicants_creation_in_res_partner()

        self.env["res.partner"].new_res_partner_update() #UPDATING ALL RES.PARTNER RECORDS

        self.env["hr.applicant"].new_hr_applicant_language_migrate()
        self.env["hr.applicant"].new_hr_applicant_experience_migrate()
        self.env["hr.applicant"].new_hr_applicant_education_migrate()
        self.env["hr.applicant"].new_hr_applicant_category_migrate()
        self.env["hr.applicant"].new_update_relation_applicant_category()
        self.env["hr.applicant"].new_hr_job_migrate()
        self.env["hr.applicant"].new_hr_department_migrate()
        self.env["hr.applicant"].new_update_department_db()
        self.env["hr.applicant"].new_hr_employee_migrate()
        self.env["hr.applicant"].new_hr_stage_migrate()
        self.env["hr.applicant"].new_update_stage()
        self.env["hr.applicant"].new_update_hr_applicant_db()
        self.env["hr.applicant"].new_followers_update_for_applicant_messages()

        #CRM

        self.env["crm.lead"].new_crm_lead_migrate()
        self.env["crm.lead"].new_crm_lead_team_and_country_old_id_update()
        self.env["crm.lead"].new_crm_lead_tag_migrate_db()
        self.env["crm.lead"].new_update_relation_crm_lead_tag()
        self.env["crm.lead"].new_crm_stage_migrate_db()
        self.env["crm.lead"].new_crm_team_migrate_db()
        self.env["crm.lead"].new_crm_lead_team_update()
        self.env["crm.lead"].new_crm_lead_stage_update()
        self.env["crm.lead"].new_res_country_migrate()
        self.env["crm.lead"].new_res_currency_migrate()
        self.env["crm.lead"].new_update_country_currency()
        self.env["crm.lead"].new_update_crm_lead_country()
        self.env["crm.lead"].new_crm_lead_user_update()

        # ATTACHMENTS AND MESSAGES FOR RES.PARTNER, HR.APPLICANT and CRM

        self.env["mail.message"].new_res_partner_message()
        self.env["mail.message"].new_res_partner_attachments()
        self.env["mail.message"].new_hr_applicant_messages()
        self.env["mail.message"].new_hr_applicant_attachments()
        self.env["mail.message"].new_crm_messages()
        self.env["mail.message"].new_crm_lead_attachments()













