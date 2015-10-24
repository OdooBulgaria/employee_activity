from openerp import models, fields, api, _
from openerp import SUPERUSER_ID

class telecom_project(models.Model):
    _inherit = "telecom.project"
    _description = "Activity Functionality"
    employee_activity_lines = fields.One2many('employee.activity.line','project_id')

    def list_project(self, cr, uid, context=None):
        result = []
        list_ids = self.pool.get('attendance.attendance').fetch_ids_user(cr,uid,context)
        if list_ids:
            ng = dict(self.pool.get('telecom.project').name_search(cr,uid,'',[('id','in',list_ids[0][2])]))
        else:
            list_ids = self.pool.get("telecom.project").search(cr,uid,[], offset=0, limit=None, order=None, context=None, count=False)
            ng = dict(self.pool.get('telecom.project').name_search(cr,uid,'',[('id','in',list_ids)]))            
        if ng:
            ids = ng.keys()
            for project in self.pool.get('telecom.project').browse(cr, uid, ids, context=context):
                result.append((project.id,ng[project.id]))
        return result
    
class activity_line_line(models.Model):
    _inherit = "activity.line.line"
    _description = "Employee Activity Module"
    _inherits = {
                 'project.tracker': 'tracker_line_id'
    }

    @api.one
    @api.onchange('bill_percent')
    def onchange_bill_percent(self):
        bill_amount = (self.bill_percent/100)*self.per_unit_price
        self.bill_amount = bill_amount
    
    @api.one
    @api.depends()
    def _get_amount_earned(self):
        total_activity_line_line = len(self.line_id.activity_line_line)
        if total_activity_line_line > 0:
            self.earned_amount = self.line_id.cost / float(total_activity_line_line)
        else:
            self.earned_amount = 0
   
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
        for id in self.sudo().employee_activity_line:
            total_cost = total_cost + id.total_cost
        self.sudo().total_cost = round(total_cost,3)
         
    def name_get(self,cr,uid,ids,context=None):
        res = []
        uid = 1
        records = self.read(cr,uid,ids,['line_id','type','vendor_id'],context)
#         info [{'line_id': (1, u'Activity1[Site 1]'), 'vendor_id': False, 'site_id': (1, u'Site 1'), 'id': 1, 'type': u'inhouse'}]
        for info in records:
            name = (info.get('line_id',False) and info.get('line_id',False)[1] or 'No Activity defined') + ('[' + info.get('type',False) + ']')  
            if info.get('vendor_id',False) and info.get('type',False) == 'vendor' :
                name  = name + info.get('vendor_id',False)[1]
            res.append((info.get('id',False),name))
        return res

    def unlink(self,cr,uid,ids,context=None):
        tracker = self.pool.get('project.tracker')
        for id in self.browse(cr,uid,ids,context):
            if id.tracker_line_id:
                tracker.unlink(cr,uid,[id.tracker_line_id.id])
        return super(activity_line_line,self).unlink(cr,uid,ids,context)
    
    def create(self,cr,uid,vals,context=None):
        line_item_id=vals.get('line_id',False)
        activity_line_obj=self.pool.get('activity.line').browse(cr,uid,line_item_id,context)
        if not vals.get('IPR_no',False) or vals.get('IPR_no',False) == '/':
            sequence = self.pool.get('ir.sequence').get(cr,uid,'Project.Tracker.IPR.No',context=None) or '/'
            vals.update({
                         'IPR_no':sequence
                         })        
        tracker_id=self.pool.get('project.tracker').create(cr,uid,{
              'work_description_id':activity_line_obj.activity_line.description_id.id,
              'site_id': vals.get('site_id',False),
              'site_name':vals.get('site_id',False) and self.pool.get('project.site').browse(cr,uid,vals.get('site_id'),context) or False,
              'po_status':False,
              'activity_planned':vals.get('line_id'),
              'done_by':False,
              'IPR_no':vals.get('IPR_no','/'),
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
    tracker_line_id = fields.Many2one('project.tracker',string='Tracker Line',ondelete="cascade",required=True,select=True)
    earned_amount = fields.Float(compute = "_get_amount_earned",string = "Earnings")
    bill_percent = fields.Float('Percent Billed')
    bill_amount= fields.Float('Billed Amount')