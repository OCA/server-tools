# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 solutions2use (<http://www.solutions2use.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import fields, orm
import httplib2
from apiclient import discovery
from oauth2client import file
import dateutil.parser
import pytz
import logging


logger = logging.getLogger('google_meeting')


class CrmMeeting(orm.Model):

    _name = 'crm.meeting'
    _inherit = 'crm.meeting'
    _columns = {
        'google_event_id': fields.char('Google Calendar Event ID'),
        'google_sequence': fields.integer('Sequence for update'),
    }

    _defaults = {
        'google_event_id': False,
        'google_sequence': 0,
    }

    def create(self, cr, uid, vals, context=None):

        if context is None:
            context = {}

        if context.get('stop_google_calendar_sync', False):
            event_id = super(CrmMeeting, self).create(cr, uid, vals, context)
            return event_id

        instance_pool = self.pool.get('google.api.calendar')
        instance = False
        # lp bug #1297881: added this 'if' because user_id
        # is not a required field
        if vals.get('user_id', False):
            instance = instance_pool.search(
                cr, uid, [('user_id', '=', vals['user_id'])])
        if not instance:
            event_id = super(CrmMeeting, self).create(cr, uid, vals, context)
            return event_id

        instance = instance_pool.browse(cr, uid, instance[0])
        try:
            storage = file.Storage(instance.account_id.credential_path)
            credentials = storage.get()
            http = httplib2.Http()
            http = credentials.authorize(http)
            service = discovery.build('calendar', 'v3', http=http)

            start_utc = dateutil.parser.parse(vals['date'])
            end_utc = dateutil.parser.parse(vals['date_deadline'])
            if vals.get('allday', False):
                tz = (
                    pytz.timezone(instance.user_id.tz)
                    if instance.user_id.tz else pytz.utc
                )
                # convert start in user's timezone
                start = pytz.utc.localize(start_utc).astimezone(tz)
                # convert end in user's timezone
                end = pytz.utc.localize(end_utc).astimezone(tz)
                new_event = {
                    'summary': vals['name'],
                    'description': vals.get('description', ''),
                    'location': vals.get('location', ''),
                    'start': {'date': start.strftime('%Y-%m-%d')},
                    'end': {'date': end.strftime('%Y-%m-%d')},
                }
            else:
                new_event = {
                    'summary': vals['name'],
                    'description': vals.get('description', ''),
                    'location': vals.get('location', ''),
                    'start': {
                        'dateTime': start_utc.strftime(
                            '%Y-%m-%dT%H:%M:%S.000Z'
                        )},
                    'end': {
                        'dateTime': end_utc.strftime(
                            '%Y-%m-%dT%H:%M:%S.000Z'
                        )},
                }
            new_event = service.events().insert(
                calendarId=instance.calendar_id,
                body=new_event, sendNotifications=False).execute()
            vals['google_event_id'] = new_event['id']
        except:
            vals['google_event_id'] = False
            logger.error(
                u'Insert google calendar event failed in create '
                u'method for CrmMeeting.')

        event_id = super(CrmMeeting, self).create(cr, uid, vals, context)
        return event_id

    def write(self, cr, uid, ids, vals, context=None):

        if context is None:
            context = {}

        if not ids:
            return True

        if isinstance(ids, (int, long)):
            ids = [ids]

        if context.get('stop_google_calendar_sync', False):
            res = super(CrmMeeting, self).write(
                cr, uid, ids, vals, context=context)
            return res

        for id in ids:
            # try to sync these events with google calendar
            if any(
                k in vals
                for k in ['name', 'description', 'location',
                          'date', 'date_deadline']
            ):
                google_sequence = self.read(
                    cr, uid, id, ['google_sequence'])['google_sequence']
                vals['google_sequence'] = google_sequence + 1
                super(CrmMeeting, self).write(
                    cr, uid, id, vals, context=context)

                event = self.browse(cr, uid, id)
                if event.google_event_id and event.user_id:
                    instance_pool = self.pool.get('google.api.calendar')
                    instance = instance_pool.search(
                        cr, uid, [('user_id', '=', event.user_id.id)])
                    if instance:
                        instance = instance_pool.browse(cr, uid, instance[0])
                        try:
                            storage = file.Storage(
                                instance.account_id.credential_path)
                            credentials = storage.get()
                            http = httplib2.Http()
                            http = credentials.authorize(http)
                            service = discovery.build(
                                'calendar', 'v3', http=http)

                            start_utc = dateutil.parser.parse(event.date)
                            end_utc = dateutil.parser.parse(
                                event.date_deadline)
                            if event.allday:
                                tz = (
                                    pytz.timezone(instance.user_id.tz)
                                    if instance.user_id.tz else pytz.utc
                                )
                                # convert start in user's timezone
                                start = pytz.utc.localize(
                                    start_utc).astimezone(tz)
                                # convert end in user's timezone
                                end = pytz.utc.localize(
                                    end_utc).astimezone(tz)
                                upd_event = {
                                    'summary': event.name,
                                    'description': (
                                        event.description
                                        if event.description else ''
                                    ),
                                    'location': event.location,
                                    'start': {'date': start.strftime(
                                        '%Y-%m-%d')},
                                    'end': {'date': end.strftime(
                                        '%Y-%m-%d')},
                                    'sequence': event.google_sequence,
                                }
                            else:
                                upd_event = {
                                    'summary': event.name,
                                    'description': (
                                        event.description
                                        if event.description else ''
                                    ),
                                    'location': event.location,
                                    'start': {'dateTime': start_utc.strftime(
                                        '%Y-%m-%dT%H:%M:%S.000Z')},
                                    'end': {'dateTime': end_utc.strftime(
                                        '%Y-%m-%dT%H:%M:%S.000Z'), },
                                    'sequence': event.google_sequence,
                                }

                            service.events().update(
                                calendarId=instance.calendar_id,
                                eventId=event.google_event_id,
                                body=upd_event,
                                sendNotifications=False).execute()
                        except:
                            logger.error(
                                u'Update google calendar event failed '
                                u'for id [%s] .' % (event.google_event_id))
            else:
                super(CrmMeeting, self).write(
                    cr, uid, id, vals, context=context)

        return True

    def unlink(self, cr, uid, ids, context=None):

        if context is None:
            context = {}

        if context.get('stop_google_calendar_sync', False):
            return self.unlink(self, cr, uid, ids, context=context)

        del_pool = self.pool.get('crm.meeting.deleted')

        geventids = self.read(
            cr, uid, ids, ['google_event_id', 'user_id'], context=context)
        for id in geventids:
            if id['google_event_id'] and id['user_id']:

                instance_pool = self.pool.get('google.api.calendar')
                instance = instance_pool.search(
                    cr, uid, [('user_id', '=', id['user_id'][0])])
                if instance:
                    instance = instance_pool.browse(cr, uid, instance[0])
                    try:
                        storage = file.Storage(
                            instance.account_id.credential_path)
                        credentials = storage.get()
                        http = httplib2.Http()
                        http = credentials.authorize(http)
                        service = discovery.build('calendar', 'v3', http=http)
                        service.events().delete(
                            calendarId=instance.calendar_id,
                            eventId=id['google_event_id']).execute()
                    except:
                        vals = {'google_event_id': id['google_event_id'],
                                'user_id': id['user_id'][0]}
                        del_pool.create(cr, uid, vals)

        return self.unlink(self, cr, uid, ids, context=context)
