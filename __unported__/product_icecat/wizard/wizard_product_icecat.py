# -*- encoding: utf-8 -*-
############################################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2010 Zikzakmedia S.L. (<http://www.zikzakmedia.com>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################################

from osv import fields,osv
from tools.translate import _

import os
import re
import cgi
import libxml2
import urllib
import urllib2
from urllib2 import Request, urlopen, URLError, HTTPError
from ftplib import FTP

class product_icecat_wizard(osv.osv_memory):
    _name = 'product.icecat.wizard'

    _columns = {
        'name':fields.boolean('Name'),
        'description':fields.boolean('Description'),
        'description_sale':fields.boolean('Description Śale'),
        'language_id': fields.many2one('res.lang','Language'),
        'image':fields.boolean('Image'),
        'html':fields.boolean('HTML Code'),
        'result': fields.text('Result', readonly=True),
        'resimg': fields.text('Image', readonly=True),
        'state':fields.selection([
            ('first','First'),
            ('done','Done'),
        ],'State'),
    }

    _defaults = {
        'state': lambda *a: 'first',
        'name': lambda *a: 1,
        'description': lambda *a: 1,
        'description_sale': lambda *a: 1,
        'html': lambda *a: 1,
    }

    # ==========================================
    # save XML file into product_icecat/xml dir
    # ==========================================
    def save_file(self, name, value):
        path = os.path.abspath( os.path.dirname(__file__) )
        path += '/icecat/%s' % name
        path = re.sub('wizard/', '', path)
        f = open( path, 'w' )
        try:
            f.write(value)
        finally:
            f.close()
        return path

    # ==========================================
    # Convert HTML to text
    # ==========================================
    def StripTags(self, text): 
         finished = 0 
         while not finished: 
             finished = 1 
             start = text.find("<") 
             if start >= 0: 
                 stop = text[start:].find(">") 
                 if stop >= 0: 
                     text = text[:start] + text[start+stop+1:] 
                     finished = 0 
         return text

    # ==========================================
    # Convert icecat values to OpenERP mapline
    # ==========================================
    def icecat2oerp(self, cr, uid, form, product, icecat, pathxml, language, data, context):

        if form.language_id.code:
            language = form.language_id.code

        doc = libxml2.parseFile(pathxml)

        for prod in doc.xpathEval('//Product'):
            if prod.xpathEval('@ErrorMessage'):
                if prod.xpathEval('@ErrorMessage')[0].content:
                    return prod.xpathEval('@ErrorMessage')[0].content
                    exit

        # product info
        short_summary = doc.xpathEval('//SummaryDescription//ShortSummaryDescription')
        long_summary = doc.xpathEval('//SummaryDescription//LongSummaryDescription')

        short_description = short_summary[0].content
        description = long_summary[0].content
        name = description.split('.')[0]

        for prod in doc.xpathEval('//ProductDescription'):
            if prod.xpathEval('@ShortDesc'):
                short_description = prod.xpathEval('@ShortDesc')[0].content
            if prod.xpathEval('@LongDesc'):
                description = prod.xpathEval('@LongDesc')[0].content

        # product details category
        categoryId  = []
        categoryName  = []
        for cat in doc.xpathEval('//CategoryFeatureGroup'):
            categoryId.append(cat.xpathEval('@ID')[0].content)

        for cat in doc.xpathEval('//CategoryFeatureGroup//FeatureGroup//Name'):
            categoryName.append(cat.xpathEval('@Value')[0].content)

        # join categorys lists
        category = zip(categoryId,categoryName)

        # product details feature
        prodFeatureId  = []
        prodFeatureName = []
        values = {}
        for prod in doc.xpathEval('//ProductFeature'):
            prodFeatureId.append(prod.xpathEval('@CategoryFeatureGroup_ID')[0].content+"#"+prod.xpathEval('@Presentation_Value')[0].content)

        for prod in doc.xpathEval('//ProductFeature//Feature//Name'):
            prodFeatureName.append(prod.xpathEval('@Value')[0].content)

        # ordered id, name & description Product Feature
        prodFeature = {}
        i = 0
        for feature in prodFeatureId:
            if not prodFeatureName[i] == 'Source data-sheet':
                values = feature.split('#')
                if values[1] == "Y":
                    value = _("Yes")
                elif values[1] == "N":
                    value = _("No")
                else:
                    value = values[1]
                if values[0] not in prodFeature:
                    prodFeature[values[0]] = []
                prodFeature[values[0]].append('<strong>'+prodFeatureName[i]+':</strong>'+' '+value)
            i += 1

        mapline_ids = self.pool.get('product.icecat.mapline').search(cr, uid, [('icecat_id', '=', icecat.id)])
        mapline_fields = []
        for mapline_id in mapline_ids:
            mapline = self.pool.get('product.icecat.mapline').browse(cr, uid, mapline_id)
            mapline_fields.append({'icecat':mapline.name,'oerp':mapline.field_id.name})

        #show details product
        #TODO: HTML template use Mako template for not hardcode HTML tags
        mapline_values = []
        for cat in category:
            catID = cat[0]
            catName = cat[1]
            if catID in prodFeature and len(prodFeature[catID]):
                for mapline_field in mapline_fields:
                    if mapline_field['icecat'] == catID:
                        source = '<h3>%s</h3>' % catName
                        i = True
                        for feature in prodFeature[catID]:
                            if i == True:
                                source += '<ul>'
                            source += '<li>%s</li>' % feature
                            i = False
                        source += '</ul>'
                        if not form.html:
                            source = self.StripTags(source)
                        mapline_values.append({'field':mapline_field['oerp'],'source':source})
                    # This is not hardcode. Short description is avaible in antother fields, for example meta_description website fields (magento, djnago,...)
                    if mapline_field['icecat'] == 'ShortSummaryDescription':
                        mapline_values.append({'field':mapline_field['oerp'],'source':short_description})

        # update icecat values at product
        # default values. It is not hardcode ;)
        values = {}

        if form.name:
            trans_name_id = self.pool.get('ir.translation').search(cr, uid, [('lang', '=', language),('name','=','product.template,name'),('res_id','=',product.id)])
            if trans_name_id:
                self.pool.get('ir.translation').write(cr, uid, trans_name_id, {'value': name}, context)
            else:
                values['name'] = name

        if form.description_sale:
            trans_descsale_id = self.pool.get('ir.translation').search(cr, uid, [('lang', '=', language),('name','=','product.template,description_sale'),('res_id','=',product.id)])
            if trans_descsale_id:
                self.pool.get('ir.translation').write(cr, uid, trans_descsale_id, {'value': short_description}, context)
            else:
                values['description_sale'] = short_description

        if form.description:
            if not form.html:
                description = self.StripTags(description)
            trans_description_id = self.pool.get('ir.translation').search(cr, uid, [('lang', '=', language),('name','=','product.template,description'),('res_id','=',product.id)])
            if trans_description_id:
                self.pool.get('ir.translation').write(cr, uid, trans_description_id, {'value': description}, context)
            else:
                values['description'] = description

        # add mapline values calculated
        for mapline_value in mapline_values:
            values[mapline_value['field']] = mapline_value['source']
        
        self.pool.get('product.product').write(cr, uid, [product.id], values, context)

        result = _("Product %s XML Import successfully") % name

        return result

    # ==========================================
    # Convert icecat values to OpenERP mapline
    # ==========================================
    def iceimg2oerpimg(self, cr, uid, form, product, icecat, pathxml, data, context):
        doc = libxml2.parseFile(pathxml)

        #product image
        for prod in doc.xpathEval('//Product'):
            if prod.xpathEval('@HighPic'):
                image = prod.xpathEval('@HighPic')[0].content

        if image:
            fname = image.split('/')
            fname = fname[len(fname)-1]

            path = os.path.abspath( os.path.dirname(__file__) )
            path += '/icecat/%s' % fname
            path = re.sub('wizard/', '', path)

            #download image
            urllib.urlretrieve(image, path)

            #send ftp server
            ftp = FTP(icecat.ftpip)
            ftp.login(icecat.ftpusername, icecat.ftppassword)
            ftp.cwd(icecat.ftpdirectory)
            f=file(path,'rb')
            ftp.storbinary('STOR '+os.path.basename(path),f)
            ftp.quit()

            # add values into product_image
            # product info
            long_summary = doc.xpathEval('//SummaryDescription//LongSummaryDescription')
            description = long_summary[0].content
            name = description.split('.')[0]

            values = {
                'name': name,
                'link': 1,
                'filename': icecat.ftpurl+fname,
                'product_id': product.id,
            }
            self.pool.get('product.images').create(cr, uid, values, context)
            return icecat.ftpurl+fname
        else:
            return _("Not exist %s image") % fname

    # ==========================================
    # wizard
    # =========================================
    def import_xml(self, cr, uid, ids, data, context={}):
        icecat_id = self.pool.get('product.icecat').search(cr, uid, [('active', '=', 1)])[0]
        icecat = self.pool.get('product.icecat').browse(cr, uid, icecat_id)

        form = self.browse(cr, uid, ids[0])

        if not form.language_id:
            language =  self.pool.get('res.users').browse(cr, uid, uid).context_lang
            lang = language.split('_')[0]
        else:
            language = form.language_id.code
            lang = language.split('_')[0]

        resimg = ''

        for prod in data['active_ids']:
            product = self.pool.get('product.product').browse(cr, uid, prod)
            ean = product.ean13

            if ean:
                url = 'http://data.icecat.biz/xml_s3/xml_server3.cgi?ean_upc=%s;lang=%s;output=productxml' % (ean, lang)
                fileName = '%s.xml' % ean

                passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
                # this creates a password manager
                passman.add_password(None, url, icecat.username, icecat.password)

                authhandler = urllib2.HTTPBasicAuthHandler(passman)
                # create the AuthHandler

                openerp = urllib2.build_opener(authhandler)

                urllib2.install_opener(openerp)
                # All calls to urllib2.urlopen will now use our handler

                try:
                    pagehandle = urllib2.urlopen(url)
                    req = urllib2.Request(url)
                    handle = urllib2.urlopen(req)
                    content = handle.read()
                    #save file
                    pathxml = self.save_file( fileName, content )
                    #import values icecat2oerp
                    result = self.icecat2oerp(cr, uid, form, product, icecat, pathxml, language, data, context)
                    #import image icecat2oerp
                    if icecat.ftp and form.image:
                        resimg += self.iceimg2oerpimg(cr, uid, form, product, icecat, pathxml, data, context)
                        resimg += "\n"
                    else:
                        resimg += _("Import image not avaible")
                        resimg += "\n"
                except URLError, e:
                    result = e.code
            else:
                result = _("EAN not avaible")
                resimg = False

        values = {
            'state':'done',
            'result':result,
            'resimg':resimg,
        }
        self.write(cr, uid, ids, values)

        return True

product_icecat_wizard()
