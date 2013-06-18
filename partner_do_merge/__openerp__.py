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
    'name' : 'Merge Duplicate Partner',                                                                   
    'version' : '0.1',                                                             
    'author': 'OpenERP SA',
    'website': 'http://www.openerp.com',
    'category' : 'Base',                                                          
    'description' : """     
Merge Partners
==============
We can merge duplicates partners and set the new id in all documents of
partner merged

We can merge partner using like mach parameter these fields:
-Email
-VAT
-Company
-Is company
-Name
-Parent Company
                                                                                   
We can select which partner will be the main partner

This feature is in the follow path Sales/Tools/Deduplicate Contacts also is
created an action menu in the partner view
    """,                                                                           
    'images' : [],                                                                 
    'depends' : [
        'base',
        'crm',
    ],                                                                
    'data': [                                                                      
        'wizard/base_partner_merge_view.xml',
    ],                                                                                 
    'js': [                                                                        
    ],                                                                                 
    'qweb' : [                                                                     
    ],                                                                                 
    'css':[                                                                        
    ],                                                                                 
    'demo': [                                                                      
    ],                                                                                 
    'test': [                                                                      
    ],                                                                                                                                                                                                  
    'installable': True,                                                           
    'auto_install': False,                                                         
}                                                                                  
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: 

