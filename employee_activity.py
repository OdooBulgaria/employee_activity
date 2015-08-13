from openerp import models, fields, api, _
from openerp import SUPERUSER_ID
from datetime import datetime
from pytz import timezone
from openerp.exceptions import except_orm

class telecom_project(models.Model):
    _inherit = "telecom.project"
    _description = "Activity Functionality"
    employee_activity_lines = fields.One2many('employee.activity.line','project_id')
                
    
class employee_activity(models.Model):
    _name = "employee.activity.line"
    _description = "Employee Activity Line"
    
    def create(self,cr,uid,vals,context=None):
        return super(employee_activity,self).create(cr,uid,vals,context)
    
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
        present_ids = employee_status_line.search(cr,SUPERUSER_ID,[
                                                                   ('date','=',datetime.now(timezone('Asia/Kolkata')).date()),
                                                                   ('employee_id','child_of',user_info.get('emp_id',False)[0]),
                                                                   ('state','in',['present','tour']),
                                                                   ('line_id.state','=','submitted')
                                                                   ],offset=0, limit=None, order=None, context=None, count=False)
        if present_ids:
            # returns list of dictionary[{'employee_id':(id_employee,employee_name),id:id_employee_status_line}]
            employee = employee_status_line.read(cr,uid,present_ids,['employee_id','current_project'],context) 
#             employee_ids = map(lambda x:x.get('employee_id')[0],employee)
            # Find their unclosed activities
            for i in employee:
                activity_ids = self.search(cr,SUPERUSER_ID,[
                                                            ('employee_id','=',i.get('employee_id',False)[0]),
                                                            ('state','in',['uncompleted','wip','unattempted']),
                                                            ],offset=0, limit=None, order=None, context=None, count=False)
                activity_info = self.read(cr,SUPERUSER_ID,activity_ids,[],context)
                res.update({
                            i.get('employee_id',False)[0]:{
                                                            'current_project':i.get('current_project',False),
                                                            'employee_id':i.get('employee_id',False)[0],
                                                            'name':i.get('employee_id',False)[1],
                                                            'activities':activity_info
                                                          }
                            })
        else:
            raise except_orm(_('Action Plan'),_('No Emmployees Present'))
        return res
    
    employee_id = fields.Many2one('hr.employee',string = "Employee",required=True)
    job_id = fields.Many2one(relation = 'hr.job',related = "employee_id.job_id",string = "Designation",store = True)
    project_id = fields.Many2one('telecom.project' ,string = "Project" )
    mobile_phone = fields.Char(related = "employee_id.mobile_phone" ,string = "Project")
    work_location = fields.Char(related = "employee_id.work_location",string = "Base Location")
    current_location = fields.Char('Current Location')
    site_id = fields.Char('Site ID')
    site_name = fields.Char('Site Name')
    work_description = fields.Many2one('project.description.line')
    activity_line = fields.Many2one('activity.line')
    state = fields.Selection([
                              ('completed','Completed'),
                              ('uncompleted','Not Completed'),
                              ('wip',"WIP"),
                              ('unattempted',"Not Attempted"),
                              ],string = "Status")
    remarks = fields.Text('Remarks')
    reporting_time_site = fields.Datetime('Reporting Time on Site')
    return_time_site = fields.Datetime('Returning Time from Site')
    distance_site_location = fields.Float("Distance Between Site & Location")
    local_conveyance = fields.Float('Local Conveyance (LC)')
    travelling_allowance = fields.Float("Travelling Allowance Applied (TA)")
    daily_allowance = fields.Float("Daily Allowance (DA)")
    lodging = fields.Float('Lodging')
    multiple_employees = fields.Many2many('hr.employee','ativity_line_hr_employee_rel','line_id','employee_id','Replicate Activity')
    date = fields.Date("Date",default = datetime.now(timezone('Asia/Kolkata')).date())
    