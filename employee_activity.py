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
    
    name = fields.Char("Sequence",readonly="1")
    employee_id = fields.Many2one('hr.employee',string = "Employee",required=True)
    job_id = fields.Many2one(relation = 'hr.job',related = "employee_id.job_id",string = "Designation",store = True)
    project_id = fields.Many2one('telecom.project' ,string = "Project",required=True )
    mobile_phone = fields.Char(related = "employee_id.mobile_phone" ,string = "Project")
    work_location = fields.Char(related = "employee_id.work_location",string = "Base Location")
    current_location = fields.Char('Current Location')
    site_id = fields.Many2one('project.site','Site')
    site_code = fields.Char(related = "site_id.site_id",string="Site ID",readonly=True)
    work_description = fields.Many2one('project.description.line')
    activity_line = fields.Many2one('activity.line')
    state = fields.Selection([
                              ('completed','Completed'),
                              ('uncompleted','Not Completed'),
                              ('wip',"WIP"),
                              ('unattempted',"Not Attempted"),
                              ],string = "Status",default = "wip")
    remarks = fields.Text('Remarks')
    reporting_time_site = fields.Datetime('Reporting Time on Site')
    return_time_site = fields.Datetime('Returning Time from Site')
    distance_site_location = fields.Float("Distance Between Site & Location")
    local_conveyance = fields.Float('Local Conveyance (LC)')
    travelling_allowance = fields.Float("Traveling Allowance Applied (TA)")
    daily_allowance = fields.Float("Daily Allowance (DA)")
    lodging = fields.Float('Lodging')
    multiple_employees = fields.Many2many('hr.employee','ativity_line_hr_employee_rel','line_id','employee_id','Replicate Activity')
    date = fields.Datetime("Date",default = datetime.now(timezone('Asia/Kolkata')).date(),required=True)
    