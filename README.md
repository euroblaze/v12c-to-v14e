**Basic informations**

This module  can be used for migrating res.partner, hr.applicant and CRM from v12 Odoo to v14 Odoo. With the migration on res.partner, hr.applicant and CRM, new fields are created  on that models. Тhese fields  represent the relational IDs from the old database and their names begin with OLD. This old_id is used for searching the newly created record, once the record is found, the new id of the record will be taken and used for establishing correct relations between models.

Examples:

1. Id of record in old v12 database would be stored in v14 database as old_id.
2. Author_id which is foreign key in mail.message model, pointing to res.partner, would be stored as old_author_id.

old_author_id will be used for finding correct author of the message in v14 database and after, when the author is found,  the new_id of author will be taken and message will be updated with author_id equalized to new_id.


**IMPORTANT**

*This module migrates only basic fields, all of data for custom fields are dropped, also some relation which is not important are dropped. 20% to 30% of the module’s code needs to be modified for migrating different databases.
It is deeply recommend every function to be run one by one.*

**Restoring the old v12 database:**

After downloading the backup of v12 database from odoo, database needs to be restore locally before migrating. Commands used for restoring the database are:

1. `create database databasename`

2.1 `psql databasename < backup.sql`

2.2 `pg_restore -d databasename < backup.dump`

The second step is chosen based on the backup’s extension. if backup is stored as .sql, then the restoring of the database is done by 2.1 step, else if backup is stored as .dump, then restoring of the database is done by 2.2 step.

After restoring, the database can be accessed locally.

**Connecting to the old v12 database:**

Connection to the v12 database is done on each function separately. For connection is used python library psycopg2. Credentials which are used for access, are stored in odoo.conf file. Command used for establishing the connection is:

```
from odoo import tools as tl

cli_commands = tl.config
 
connection =  # command for connecting with database v12cc-sabota psycopg2.connect(user=cli_commands.get('user_name'),
                              password=cli_commands.get('local_password'),
                              host="172.17.0.1",
                              port="5432",
                              database="v12cc-sabota")
```
`from odoo import tools as tl` - This line of code is used for importing tools from odoo, which are used for establishing connection with odoo.conf

```
connection = psycopg2.connect(user=cli_commands.get('user_name'),
                              password=cli_commands.get('local_password'),
                              host="172.17.0.1",
                              port="5432",
                              database="v12cc-sabota")
```
These lines of code are used for connection to the database (in this case the database's name is v12cc-sabota)

`user=cli_commands.get('user_name')` - this command is used for taking parametar value for user, which is stored in odoo.conf as 'user_name'.

`password=cli_commands.get('local_password')` - same as user (the description above this)

**Migrating of res.partner:**

For migrating res.partner, res.company needs to be migrated first. 

`def new_company_migrate(self):`

This function migrates all companies from v12 to v14. First step is company migration because later while creating res.partner, correct company needs to be set for the created partner. 
*Execution time for this function is fast.*

`def new_res_partner_migrate(self)`

This function migrates/creates res.partner from v12 to v14. This function creates all res.patner records from v12 to v14.

Also before creation, the function checks if the partner exist.

*For 100 000 contacts, execution time is from 8-10 hours.*


`def new_res_partner_message(self): `

This function migrates messages from v12 to v14 where res_model is res.partner. If every partner is created with previous function and if the data is not mixed, every message will be created with correct res_id and with correct author_id. 
For our database, new functions had to be created to update the author and res_id because the data is mixed and not consistent in v12. 

*Execution time for this function is 18-23 hours for our database.*

`def new_res_partner_attachments(self):`

This function migrates attachments from v12 to v14 where res_model is res.partner. If every partner is correctly created before, every attachment will be migrated correctly. 

*Execution time for this function on our database is 13-15 hours *

`def new_res_partner_update(self):`

This function is used for updating res.partner model. Parent_Id field and Company_Id field are updated. 

*The parent_id and company_id update was done as author_id in the example in basic informations.


**Migrating of hr.applicant:**

`def new_hr_applicant_migrate(self):`

This function migrates model hr.applicant from v12 to v14.  Applicants are created with еmpty values for any relation which, after, these relational fields will be updated with correct value.

*Execution time for our database is 6-7 hours.*


`def new_hr_applicant_language_migrate(self):`

This function migrates languages for applicants and in the same time updates every applicant with the correct languages which are set for the applicant.

*Execution time is fast*

`def new_hr_applicant_experience_migrate(self):`

This function migrates experience for applicants and in the same time update every applicant with the correct experience. 

*Execution time is fast*


`def new_hr_applicant_education_migrate(self):`

This function migrates education for applicants and in same time updates every applicant with the correct education which he has.

*Execution time is fast.*

`def new_hr_applicant_category_migrate(self):`

This function migrate hr.applicant.category (tags) for applicants. 

*Execution time is fast.*

`def new_update_relation_applicant_category(self):`

Because hr.applicant.category is many2many relation with hr.applicant, It have to be manuely updated in database.

*Execution time is fast.*

`def new_hr_job_migrate(self):`

This function migrates all jobs from v12 to v14.

*Execution time is fast.*

`def new_hr_department_migrate(self):`

This function migrates all departments from v12 to v14.

*Execution time is fast.*

`def new_update_department_db(self):`

This function updates menager_id for all departments.

*Execution time is fast.*

`def new_hr_employee_migrate(self):`

This function migrates employees from v12 to v14.

*Execution time is fast.*

`def new_hr_stage_migrate(self):`

This function migrates all stages from v12 to v14.

*Execution time is fast.*

`def new_update_stage(self):`

This function updates job_id relation for every stage.

*Execution time is fast.*

`def new_update_hr_applicant_db(self):`

This function updates hr.applicant important relational fields as:

- department_id
- job_id
- stage_id
- company_id

*Execution time is 7-8 hours.*

`def new_hr_applicants_creation_in_res_partner(self):`

This function, for each applicant creates res.partner record if it does not exist. 
This function is created for our specific database because  all of the hr.applicant  records did not exist in the res.partner model. 
In normal conditions this fuction does not need to be executed.

*Execution time is 3-4 hours.*


`def new_hr_applicant_messages(self):`

This function migrates messages from v12 to v14 where res_model is hr.applicant. If every partner is created with previous function and if the data is not mixed, every message will be created with correct res_id and with correct author_id. 
For our database, new functions had to be created to update the author and res_id because the data is mixed and not consistent in v12. 

*Execution time for this function is 7-8 hours for our database.*



`def new_followers_update_for_applicant_messages(self)`

This function migrates followers from v12 to v14 for every applicant.

*Execution time is fast.*

`def new_hr_applicant_attachments(self)`

This function migrates attachments from v12 to v14 where res_model is hr.applicant. 

*Execution time for this function on our database is 6-8 hours .*


**Migrating of CRM:**

`def new_crm_lead_migrate(self):`

This function migrates crm.lead from v12 to v14.

*Execution time is 1-2 hours for our database.*

`def new_crm_lead_team_and_country_old_id_update(self):`

This function is used for finding old_ids from v12 database, for country_id and team_id for each crm.lead record. Again as it was explained atthe beginning of the documentation, old_ids are needed later. After migration of teams and countries, old_ids will be used for updating new_id on country_id and team_id accordingly.

*Execution time is 1 hour.*

`def new_crm_lead_tag_migrate_db(self):`

This function migrates crm.tags from v12 to v14.

*Execution time is fast.*

`def new_update_relation_crm_lead_tag(self)`

This function is used for updating many2many relation between crm.lead and crm.lead.tag model.

*Execution time is 30 minutes.*

`def new_crm_stage_migrate_db(self):`

This function migrates crm.stage model from v12 to v14.

*Execution time is fast.*

`def new_crm_team_migrate_db(self):`

This function migrates crm.team model from v12 to v14.

*Execution time is fast.*

`def new_crm_lead_team_update(self):`

This function updates team_id for each crm.lead record using old_team_id in crm.lead model.

*Execution time is fast.*

`def new_crm_lead_stage_update(self):`

This function updates stage_id for each crm.lead record using old_stage_id in crm.lead model.
 
*Execution time is fast.*


`def new_res_country_migrate(self):`

This function migrates res.country model from v12 to v14.

*Execution time is fast.*

`def new_res_currency_migrate(self):`

This function migrates res.currency model from v12 to v14.

*Execution time is fast.*

`def new_update_country_currency(self):`

This function updates currency_id for each res.country record using old_currency_id in res.country model.

*Execution time is fast.*

`def new_update_crm_lead_country(self):`

This function updates country_id for each crm.lead record using old_country_id in crm.lead model.

*Execution time is fast.*

`def new_crm_lead_user_update(self):`

This function updates user_id for each crm.lead record.

**IMPORTANT**
*This function only works if res.users are migrated before.
Execution time is 1 hour.*


`def new_crm_messages(self):`

This function migrates messages from v12 to v14 where res_model is crm.lead. If every partner is created correctly and if the data is not mixed, every message will be created with correct res_id and with correct author_id. 

*Execution time for this function is 2-3 hours for our database.*

`def new_crm_lead_attachments(self):`

This function migrates attachments from v12 to v14 where res_model is crm.lead. 

*Execution time for this function on our database is 2-3 hours.*
