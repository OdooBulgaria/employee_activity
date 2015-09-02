from openerp import models, fields, api, _
from openerp import SUPERUSER_ID

class telecom_project(models.Model):
    _inherit = "telecom.project"
    _description = "Activity Functionality"
    employee_activity_lines = fields.One2many('employee.activity.line','project_id')
                

class activity_line_line(models.Model):
    _inherit = "activity.line.line"
    _inherits = {
                 'project.tracker': 'tracker_line_id'
    }

    @api.one
    @api.depends(
                'employee_activity_line.employee_id.emp_type',
                'cost',
                'employee_activity_line.local_conveyance_approved',
                'employee_activity_line.travelling_allowance_approved',
                'employee_activity_line.daily_allowance_approved',
                'employee_activity_line.lodging_approved',
                'type'
                 )
    def _compute_total_cost(self):
        total_cost = 0
        for id in self.employee_activity_line:
            total_cost = total_cost + id.total_cost
        self.total_cost = round(total_cost,3)
         
    def name_get(self,cr,uid,ids,context=None):
        res = []
        records = self.read(cr,uid,ids,['line_id','type','vendor_id'],context)
#         info [{'line_id': (1, u'Activity1[Site 1]'), 'vendor_id': False, 'site_id': (1, u'Site 1'), 'id': 1, 'type': u'inhouse'}]
        for info in records:
            name = (info.get('line_id',False) and info.get('line_id',False)[1] or 'No Activity defined') + ('[' + info.get('type',False) + ']')  
            if info.get('vendor_id',False) and info.get('type',False) == 'vendor' :
                name  = name + info.get('vendor_id',False)[1]
            res.append((info.get('id',False),name))
        return res

    def create(self,cr,uid,vals,context=None):
        line_item_id=vals.get('line_id',False)
        activity_line_obj=self.pool.get('activity.line').browse(cr,uid,line_item_id,context)
        tracker_id=self.pool.get('project.tracker').create(cr,uid,{
              'work_description_id':activity_line_obj.activity_line.description_id.id,
              'IPR_no':False,
              'IPR_date':False,
              'site_id': vals.get('site_id',False),
              'site_name':vals.get('site_id',False) and self.pool.get('project.site').browse(cr,uid,vals.get('site_id'),context) or False,
              'po_status':False,
              'activity_planned':vals.get('line_id'),
              'per_unit_Price':0.0,
              'advance_paid_to_vendor':0.0,
              'done_by':False,
              'activity_start_date':False,
              'activity_end_date':False,
              'wcc_sign_off_status':False,
              'wcc_sign_off_date':False,
              'quality_document_uploaded_on_P6':False,
              'quality_document_uploaded_date':False,
              'cql_approval_status':False,
              'pd_approval_status':False,
              })
        vals.update({'tracker_line_id':tracker_id})
        return super(activity_line_line,self).create(cr,uid,vals,context)

#     earned = fields.Float(compute = _get_total_earned,string = "Earning")
    employee_activity_line = fields.One2many('employee.activity.line','activity_line',"Activities")
    total_cost = fields.Float(compute = _compute_total_cost,string = "Total Expenses")
    tracker_line_id = fields.Many2one('project.tracker',string='Tracker Line',ondelete="cascade",required=True)