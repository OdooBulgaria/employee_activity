from openerp.osv import fields, osv
from datetime import datetime
from openerp import SUPERUSER_ID
from pytz import timezone

class project_tracker_wizard(osv.osv_memory):
    _name = "project.tracker.wizard"
    _description = "Project Tracker Report"
    
    def print_report(self,cr,uid,ids,context=None):
        assert len(ids) == 1 , "This option is supposed to be used for single wizard id"
        domain=[]
        # info =  {'from': '2015-08-16', 'employee_ids': [4, 5, 3], 'project_ids': [1, 2], 'to': '2015-08-16', 'state': False, 'id': 14}
        info = self.read(cr,uid,ids[0],['project_ids','circle_ids','choice_selection'],context)
        
        if info.get('choice_selection',False) == 'project':
            project_ids = info.get('project_ids',[])
            domain.append(('project_id','in',project_ids))
            
        if info.get('choice_selection',False) == 'circle':
            circle_ids = info.get('circle_ids',[])
            domain.append(('project_id.circle','in',circle_ids))
        
        line_obj = self.pool.get('activity.line.line')
        search_ids = line_obj.search(cr,uid,domain, offset=0, limit=None, order=None, context=None, count=False)
        datas = {
             'ids': search_ids,
             'model': 'activity.line.line',
             'form': info
                 }
        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'project_tracker_report_aeroo',
                    'datas': datas,
                    'context':context

                }            
    _columns={
              'choice_selection':fields.selection([
                                                   ('project',"Project"),
                                                   ('circle',"Circle"),
                                                   ],string = "Filter By",required=True),
              'project_ids':fields.many2many('telecom.project','project_tracker_wizard_rel','wizard_id','project_id','Projects'),
              'circle_ids':fields.many2many('telecom.circle','project_tracke_circle_wizard_rel','wizard_id','project_id','Circle')
              }
