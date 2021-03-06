from openerp.osv import fields, osv
from datetime import datetime
from openerp import SUPERUSER_ID

class project_tracker(osv.osv):
    _name = 'project.tracker'
    
    def unlink(self,cr,uid,ids,context=None):
        return True
    
    def _compute_unit_price(self,cr,uid,ids,name,args,context=None):
        uid = SUPERUSER_ID
        res = {}
        for record in self.browse(cr,uid,ids,context):
            res.update({
                        record.id:record.activity_planned.cost
                        })
        return res
    
    def _get_employees_id(self,cr,uid,ids,name,args,context=None):
        uid = SUPERUSER_ID
        res = {x:[] for x in ids}
        line_obj = self.pool.get('activity.line.line')
        line = line_obj.search(cr,uid,[('tracker_line_id','in',ids)],offset=0, limit=None, order=None, context=None, count=False)
        for record in line_obj.browse(cr,uid,line,context):
            for activity in record.employee_activity_line:
                res.update({
                            record.tracker_line_id.id:map(lambda x:x.employee_id.id,record.employee_activity_line)
                            })
        
        return res
         
    _columns={
              'IPR_no':fields.char('IPR No'),
              'IPR_date':fields.datetime(string='IPR Date'),
              'po_status':fields.selection(string='PO Status',selection=[('Available','Available'),
                                                                    ('Not Available','Not Available'),
                                                                    ]),
              'activity_planned':fields.many2one('activity.line',string='Activity Planned',ondelete="cascade",required=True,select=True),
              'per_unit_price':fields.function(_compute_unit_price,type="float",string='PLS Per unit Price'),
              'done_by':fields.function(_get_employees_id,string = "Done By",type="many2many",relation="hr.employee"),
              'activity_start_date':fields.datetime(string='Activity Start Date'),
              'activity_end_date':fields.datetime(string='Activity End Date'),
              'wcc_sign_off_status':fields.selection(string='WCC sign off status',selection=[('Yes','Yes'),('No','No')]),
              'wcc_sign_off_date':fields.datetime(string='WCC Sign off Date'),
              'quality_document_uploaded_on_P6':fields.selection(string='Quality Document uploaded on P6',selection=[('Yes','Yes'),('No','No')]),
              'quality_document_uploaded_date':fields.datetime(string='Quality Document Uploaded date'),
              'cql_aproval_date':fields.date(string="CQL Approval Date"),
              'cpm_aproval_date':fields.date(string="CPM Approval Date"),
              'im_approval_date':fields.date(string='IM Approval Date',selection=[('yes','Yes'),('no','No')]),
              'pd_approval_date':fields.date('PD Approval Date'),
              'invoice_date':fields.date('Invoice Date'),
              'vendor_payment_remark':fields.text('Vendor Payment Remark')
              }
    _defaults = {
                'IPR_no':'/',
                'IPR_date':datetime.now(),
                }