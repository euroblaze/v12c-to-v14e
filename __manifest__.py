{
'name':'DB Migrate',
'description':'this module is made for migration on res_partner,hr.applicant,crm,sales. Also this module add new custom fields which contain old ids from previous database.',
'author':'Simplify-ERP®',
'category':'tehnical',
'summary':'Data migrate from 12 to 14',
'images':"static/src/img/recycling-symbol-icon-twotone-light-green.png",
'depends':['base', 'hr_recruitment', 'mail', 'website', 'website_form', 'website_partner', 'hr_applicant'],
'data':['views/form_view.xml',
        'views/view.xml'
        ]
 }
