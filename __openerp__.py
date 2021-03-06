# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Telecom Activity Plan',
    'version': '0.1',
    'category': 'telecom management',
    'sequence':1,
    'summary': 'telecom',
    'description': """
    PLS Project Management
    """,
    'author': 'J & G Infosystems',
    'website': 'www.jginfosystems.com',
    'depends': ['base','pls','hr'],
    'data': [
             'employee_activity_data.xml',
             'employee_activity.xml',
             'security/ir.model.access.csv',
             'activity_sequence.xml',
             'dashboard.xml',
             'report/activity_report.xml',
             'wizard/employee_dashboard.xml',
             'telecom.xml',
             'wizard/project_tracker_wizard.xml',
             'report/project_tracker_report.xml'
             
             ],
    'demo': [],
    'test': [],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: