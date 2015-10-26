from openerp import models, fields, api, _
from openerp import SUPERUSER_ID
from datetime import datetime
from pytz import timezone
from openerp.exceptions import except_orm
import time

class employee_activity(models.Model):
    _name = "employee.activity.line"
    _description = "Employee Activity Line"
    
    def run_cron_employee_activity_line(self,cr,uid,ids=None,context=None):
        current_timedate = datetime.now()
        mail_obj=self.pool.get('mail.mail')
        send_mail=[]
        line_ids=self.search(cr, uid, args=[], offset=0, limit=None, order=None, context=None, count=False)
        overly_aged={}
        if line_ids:
            groups = self.pool.get('ir.model.data').get_object_reference(cr, uid,'pls','telecom_corporate')[1]
            user_group = self.pool.get('res.groups').browse(cr,uid,groups)
            user_ids = map(int,user_group.users or [])
            corporate_ids = []
            if user_ids:
                for j in user_ids:
                    corporate_ids.append(self.pool.get('res.users').read(cr,uid,j,['partner_id'],context=None).get('partner_id',False)[0])
            for i in line_ids:
                line_obj=self.browse(cr,uid,i,context=None)
                activity_date=line_obj.date
                time_diff = current_timedate - datetime.strptime(activity_date,"%Y-%m-%d %H:%M:%S")
                aging24 = divmod(time_diff.days*86400 + time_diff.seconds,86400)
                if line_obj.is_mail_sent_48 != True and aging24[0] > 2 :
                    email_to_ids = []
                    email_to_ids = email_to_ids + corporate_ids
                    str1 = ""
                    str1 = "This activity was created ",(aging24[0])," days ",(aging24[1]/3600)," hours ",((aging24[1]%3600)/60)," minutes ago on ",activity_date,"\n\nActivity Line : ",line_obj.name ,"\nResponsible Employee : ",line_obj.employee_id.name, "\nSite Name: ",line_obj.site_id.name , "\nSite ID: ",line_obj.site_code,"\n\nPlease take immediate action"
                    overly_aged.update({i:str1})
                    project_managers_ids=line_obj.project_id.project_manager
                    if project_managers_ids:
                        for pm_id in project_managers_ids:
                            email_to_ids.append(pm_id.user_id.partner_id.id)
                    email_to_ids = list(set(email_to_ids))
                    mail_id=mail_obj.create(cr,uid,{
                                                  'subject':line_obj.name+ " - Employee Activity Line Exceeded 48 hours Limit",
                                                  'recipient_ids':[(6,0,email_to_ids)],
                                                  'body_html':str1,
                                                 },context=None)
                    send_mail.append(mail_id)
                    self.write(cr,uid,i,{'state':'uncompleted','is_mail_sent_48':True},context)
                elif line_obj.is_mail_sent_24 != True and aging24[0]>0 and aging24[0] < 2 :
                    email_to_ids = []
                    email_to_ids = email_to_ids + corporate_ids
                    str1 = "This activity was created ",aging24[0]," days ",(aging24[1]/3600)," hours ",((aging24[1]%3600)/60)," minutes ago on ",activity_date,"\n\nActivity Line : ", line_obj.name ,"\nResponsible Employee : ",line_obj.employee_id.name, "\nSite Name: ",line_obj.site_id.name , "\nSite ID: ",line_obj.site_code,"\n\nPlease take the necessary action"
                    overly_aged.update({i:str1})
                    project_managers_ids=line_obj.project_id.project_manager
                    if project_managers_ids:
                        for pm_id in project_managers_ids:
                            email_to_ids.append(pm_id.user_id.partner_id.id)
                    email_to_ids = list(set(email_to_ids))
                    mail_id=mail_obj.create(cr,uid,{
                                                  'subject':line_obj.name+ " - Employee Activity Line Exceeded Time Limit",
                                                  'recipient_ids':[(6,0,email_to_ids)],
                                                  'body_html':str1,
                                                 },context=None)
                    send_mail.append(mail_id)
                    self.write(cr,uid,i,{'is_mail_sent_24':True},context)
        mail_obj.send(cr, uid, send_mail, auto_commit=False, raise_exception=False, context=None)
        return True
    
    def _check_work_description(self,cr,uid,ids,context=None):
        for i in self.browse(cr,uid,ids,context):
            if i.work_description.id in i.project_id.line_id.ids :
                return True
        return False
    
    def _check_activity_line(self,cr,uid,ids,context=None):
        for i in self.browse(cr,uid,ids,context):
            if i.activity_line.line_id.activity_line.id == i.work_description.id :
                return True
        return False
    
    def _check_activity_line_site_id(self,cr,uid,ids,context=None):
        for i in self.browse(cr,uid,ids,context):
            if i.site_id.id == i.activity_line.site_id.id :
                            return True
        return False
    _constraints = [
        (_check_work_description, 'Work description does not belong to Project selected', ['work_description']),
        (_check_activity_line, 'Activity line is not under work description', ['activity_line']),
        (_check_activity_line_site_id, 'This Activity line is not available for the selected site ID', ['activity_line']),
    ]
     
    def open_form_activity(self,cr,uid,id,context=None):
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'employee_activity', 'view_employee_activity_corporate')
        return {
            'view_mode': 'form',
            'view_id': view_id,
            'res_id':id[0],
            'view_type': 'form',
            'res_model': 'employee.activity.line',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]',
        }    
        
    # Called from javascript for activity dashboard to return the list of projects,employee names,circle
    def list_caption(self,cr,uid,context=None):
        # if corporate_ids then no restriction else child_of projects,employees and no circle
        # if no circle then an indication will be sent from python to not render circle list 
        # return the format [(1, u'Project1'), (2, u'Project2'), (3, u'Project3')] for each catoegory
        corporate_ids = self.pool.get('attendance.attendance')._get_user_ids_group(cr,uid,'pls','telecom_corporate')
        project = self.pool.get('telecom.project')
        circle = self.pool.get('telecom.circle')
        employee = self.pool.get('hr.employee')
        
        res = {}
        project_ids = False
        circle_ids = False
        employee_ids = False
        res.update({'project':project_ids,'circle':False,'employee':False})
        # Get the employee ID of the user
        employee_id =self.pool.get("attendance.line")._get_employee_id(cr,uid,context)
        # if the employee a corporate person then search for all projects else return only those under hhim
        if uid not in corporate_ids:
            project_ids = project.search(cr,SUPERUSER_ID,[('project_manager','child_of',[employee_id],)], offset=0, limit=None, order=None, context=None, count=False)
            employee_ids = employee.search(cr,SUPERUSER_ID,[('parent_id','child_of',employee_id)], offset=0, limit=None, order=None, context=None, count=False)
        else:
            project_ids = project.search(cr,SUPERUSER_ID,[], offset=0, limit=None, order=None, context=None, count=False)
            circle_ids = project.search(cr,SUPERUSER_ID,[], offset=0, limit=None, order=None, context=None, count=False)
            employee_ids = employee.search(cr,SUPERUSER_ID,[], offset=0, limit=None, order=None, context=None, count=False)
        res.update({
                    "project":project_ids and project.name_get(cr,uid,project_ids,context) or False,
                    "circle": circle_ids and circle.name_get(cr,uid,circle_ids,context)or False,
                    "employee":employee_ids and employee.name_get(cr,uid,employee_ids,context)     
                    })
            #{'project': [(1, u'Project1'), (2, u'Project2'), (3, u'Project3'), (4, u'New Project')]}
        return res
    
    def name_get(self, cr, uid, ids, context=None):
        res = super(employee_activity,self).name_get(cr,uid,ids,context)
#         res = [(2, 'employee.activity.line,2')]
        return res
    
    def create(self,cr,uid,vals,context=None):
        vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'employee.activity.line') or '/'
        if not vals.get('date',False):
            vals.update({'date':datetime.now(timezone('Asia/Kolkata'))})
        activity_line_id=super(employee_activity,self).create(cr,uid,vals,context)
        employee_ids=vals.get('multiple_employees',False)
        if employee_ids:
            for i in employee_ids[0][2] :
                defaults={'employee_id':i,
                          'multiple_employees':False
                          }
                self.copy(cr, uid, activity_line_id, defaults,context=None)
        return activity_line_id
    
    def list_employees_activity_data(self,cr,uid,context=None):
        '''
            If the uid id cicle head or project manager then they will see only those employees under them
            If they are corporate ids then they will see all the employee activities
            search for empoloyee_status_line where 
                1. date = today and  
                2. the employee_id = child of user and 
                3. state = present or tour and 
                4. their project attendance is taken
            Then once the employee status line is obtained then find all the work in progress activities for the these employees
            Get the all the fields of the activities and return a dictionary
            
            {
                employee_id1:{'name':Name,[{A1},{A2},{A3}-------]
                -
                -
                -
            }
            
        '''
        res = {}
        employee_obj = self.pool.get('res.users')
        user_info = employee_obj.read(cr,uid,uid,['emp_id'],context)
        if not user_info.get('emp_id',False):
            raise except_orm(_('Invalid user Configuration'),_('Sorry!!! No Employee attached to the user. Please contact the admin panel'))            
        corporate_ids = self.pool.get('attendance.attendance')._get_user_ids_group(cr,uid,'pls','telecom_corporate')
        employee_status_line = self.pool.get('employee.status.line')
        if uid in corporate_ids:
                    present_ids = employee_status_line.search(cr,SUPERUSER_ID,[
                                                                   ('date','=',datetime.now(timezone('Asia/Kolkata')).date()),
                                                                   ('state','in',['present','tour']),
                                                                   ('line_id.state','=','submitted')
                                                                   ],offset=0, limit=None, order=None, context=None, count=False)
        else:
            present_ids = employee_status_line.search(cr,SUPERUSER_ID,[
                                                                   ('date','=',datetime.now(timezone('Asia/Kolkata')).date()),
                                                                   ('employee_id','child_of',user_info.get('emp_id',False)[0]),                                                                   
                                                                   ('state','in',['present','tour']),
                                                                   ('line_id.state','=','submitted')
                                                                   ],offset=0, limit=None, order=None, context=None, count=False)
        if present_ids:
            employee = employee_status_line.browse(cr,uid,present_ids,context)
            for i in employee:
                activity_ids = self.search(cr,SUPERUSER_ID,[
                                                            ('employee_id','=',i.employee_id.id),
                                                            ('state','in',['uncompleted','wip','unattempted','draft',False]),
                                                            ],offset=0, limit=None, order=None, context=None, count=False)
                activity_info = self.read(cr,SUPERUSER_ID,activity_ids,[],context)
                res.update({
                            i.employee_id.id:{
                                                'user_employee_id':user_info.get('emp_id',False)[0],
                                                'current_project':(i.employee_id.current_project.id,i.employee_id.current_project.name),
                                                'employee_id':i.employee_id.id,
                                                'name':i.employee_id.name,
                                                'activities':activity_info,
                                                'type':i.employee_id.emp_type.lower(),
                                          }
                            })                
                
        else:
            raise except_orm(_('Action Plan'),_('No Employees Present'))
        return res
    
    @api.one
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.per_day_salary_employee = self.employee_id.cost_to_company_day
        
    @api.one
    @api.onchange('project_id')
    def onchange_project_id(self):
        self.activity_line = False
        self.work_description = False
        
    @api.one
    @api.depends(
        'local_conveyance_approved',
        'travelling_allowance_approved',
        'daily_allowance_approved',
        'lodging_approved',
        'employee_id',
        'employee_id.emp_type',
        'activity_line.cost',
        'activity_line.type'
    )
    def _get_total_cost(self):
        total_cost = self.misc_approved + self.local_conveyance_approved + self.travelling_allowance_approved + self.daily_allowance_approved + self.lodging_approved
        if self.employee_id.emp_type == "inhouse":
            self.total_cost = round(total_cost,3)
        elif self.employee_id.emp_type == "vendor":
            self.total_cost = round((self.activity_line.cost + self.misc_approved),3) 
    
    name = fields.Char("Sequence",readonly="1")
    IPR_no = fields.Char(string='IPR No.',store=True,related='activity_line.tracker_line_id.IPR_no',relation='project.tracker')
    employee_id = fields.Many2one('hr.employee',string = "Employee",required=True)
    emp_type = fields.Selection(related = "employee_id.emp_type",string = 'Employee Type',store=True,readonly=True)
    job_id = fields.Many2one(relation = 'hr.job',related = "employee_id.job_id",string = "Designation",store = True)
    project_id = fields.Many2one('telecom.project' ,string = "Project",required=True )
    mobile_phone = fields.Char(related = "employee_id.mobile_phone" ,string = "Project")
    work_location = fields.Char(related = "employee_id.work_location",string = "Base Location")
    current_location = fields.Char('Current Location')
    site_id = fields.Many2one('project.site','Site')
    site_code = fields.Char(related = "site_id.site_id",string="Site ID",readonly=True)
    work_description = fields.Many2one('project.description.line')
    description_id = fields.Many2one(relation="work.description",related="work_description.description_id",string = "Description Line Item",store=True,invisible=True)# Just for the purpose of domains
    activity_line = fields.Many2one('activity.line.line',required=True,string="Activity Planned")
    state = fields.Selection([('draft','Draft'),
                              ('completed','Completed'),
                              ('uncompleted','Not Completed'),
                              ('wip',"WIP"),
                              ('unattempted',"Not Attempted"),
                              ],string = "Status",default = "draft")
    remarks = fields.Text('Remarks')
    reporting_time_site = fields.Datetime('Reporting Time on Site')
    return_time_site = fields.Datetime('Returning Time from Site')
    distance_site_location = fields.Float("Distance Between Site & Location")
    local_conveyance = fields.Float('LC Applied')
    travelling_allowance = fields.Float("TA Applied")
    daily_allowance = fields.Float("DA Applied")
    lodging = fields.Float('Lodging Applied')
    misc_applied = fields.Float('Miscellaneous Applied')
    multiple_employees = fields.Many2many('hr.employee','ativity_line_hr_employee_rel','line_id','employee_id','Add More Employees')
    date = fields.Datetime("Date",default = datetime.now(),required=True)
    total_cost = fields.Float(compute="_get_total_cost",string = "Total Cost")
    circle_id = fields.Many2one(relation = 'telecom.circle',related = "project_id.circle",string = "Circle",store = True)
    local_conveyance_approved = fields.Float('LC Approved')
    travelling_allowance_approved = fields.Float("TA Approved")
    daily_allowance_approved = fields.Float("DA Approved")
    lodging_approved = fields.Float("Lodging Approved")
    misc_approved = fields.Float('Miscellaneous Approved')
    per_day_salary_employee = fields.Float('Employee Salary Per Day')
    is_mail_sent_24 = fields.Boolean("Is mail sent",default = False)
    is_mail_sent_48 = fields.Boolean("Is mail sent",default = False)
    
