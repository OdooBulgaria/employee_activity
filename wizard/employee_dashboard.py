from openerp.osv import fields, osv
from datetime import datetime
from openerp import SUPERUSER_ID
from pytz import timezone
from lxml import  etree
from openerp.osv.orm import setup_modifiers

class employee_dashboard(osv.osv_memory):
    _name = "employee.dashboard"
    _description = "Employee Dashboard Report"
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res=super(employee_dashboard,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        corporate_ids = self.pool.get('attendance.attendance')._get_user_ids_group(cr,uid,'pls','telecom_corporate')
        if uid not in corporate_ids:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='project_ids']"):
                node.set('domain',"[('project_manager.user_id','in',[uid])]")
                setup_modifiers(node, res['fields']['project_ids'])
                res['arch'] = etree.tostring(doc)
        return res
        
    def print_report(self,cr,uid,ids,context=None):
        
        assert len(ids) == 1 , "This option is supposed to be used for single id"
        domain=[]
        # info =  {'from': '2015-08-16', 'employee_ids': [4, 5, 3], 'project_ids': [1, 2], 'to': '2015-08-16', 'state': False, 'id': 14}
        info = self.read(cr,uid,ids[0],['from','to','state','employee_ids','project_ids'],context)
        domain.append(('date','>=',info.get('from',datetime.now(timezone('Asia/Kolkata')))))
        domain.append(('date','<=',info.get('to',False)))
        employee_ids = info.get('employee_ids',[])
        domain.append(('employee_id','in',employee_ids))
        project_ids = info.get('project_ids',[])
        domain.append(('project_id','in',project_ids))
        state = info.get('state',False)  
        if state:
            domain.append(('state','=',state))
        emp_obj = self.pool.get('employee.activity.line')
        search_ids = emp_obj.search(cr,uid,domain, offset=0, limit=None, order=None, context=None, count=False)
        print "==========================================search_ids",search_ids
        print "================================================================domain",domain
        datas = {
             'ids': search_ids,
             'model': 'employee.activity.line',
             'form': info
                 }
        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'activity_report_aeroo',
                    'datas': datas,
                    'context':context

                }    
    _defaults = {
                 "from":datetime.now(timezone('Asia/Kolkata')),
                 "to":datetime.now(timezone('Asia/Kolkata')),
                 "state":"wip",
                 }
    _columns ={
               'employee_ids':fields.many2many('hr.employee','employee_dashboard_hr_employee_rels','summary_id','employee_id',string = "Employees"),
               'project_ids':fields.many2many('telecom.project','employee_dashboard_telecom_project_rels','summary_id','project_id',string = "Projects"),
               'state':fields.selection([
                              ('completed','Completed'),
                              ('uncompleted','Not Completed'),
                              ('wip',"WIP"),
                              ('unattempted',"Not Attempted"),
                              ],string = "Status"),
               'from':fields.date('From',required=True),
               'to':fields.date('To',required=True),
               }
    