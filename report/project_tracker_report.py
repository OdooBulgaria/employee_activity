from openerp.report import report_sxw

class Parser(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context=None):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                'calculate_total_cost':self.calculate_total_cost,
                'calculate_rate_total':self.calculate_rate_total,
                'calculate_advance_paid_to_vendor':self.calculate_advance_paid_to_vendor,
                'calculate_balance_payment':self.calculate_balance_payment,
                'calculate_earned_amount':self.calculate_earned_amount,
                'calculate_total_cost':self.calculate_total_cost,
                
        })

    def calculate_earned_amount(self,objects):
        total = 0.00
        for line in objects:
            total = total + line.earned_amount
        return total
    
    def calculate_balance_payment(self,objects):
        total = 0.00
        for line in objects:
            total = total + line.balance_payment
        return total
    
    def calculate_advance_paid_to_vendor(self,objects):
        total = 0.00
        for line in objects:
            total = total + line.advance_paid_to_vendor
        return total
    
    def calculate_rate_total(self,objects):
        total = 0.00
        for line in objects:
            total = total + line.cost
        return total
    
    def calculate_total_cost(self,objects):
        total = 0.00
        for line in objects:
            total = total + line.total_cost
        return total 