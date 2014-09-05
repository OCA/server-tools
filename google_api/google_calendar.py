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
from openerp.tools.translate import _

import argparse
import httplib2
from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

import dateutil.parser
import pytz
import logging


logger = logging.getLogger('google_api')


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


class CrmMeetingDeleted(orm.Model):

    _name = 'crm.meeting.deleted'
    _columns = {
        'google_event_id': fields.char('Google Calendar Event ID'),
        'user_id': fields.many2one('res.users', 'User'),
    }


class GoogleApiAccount(orm.Model):

    _name = 'google.api.account'
    _columns = {
        'name': fields.char('Account', size=50, required=True),
        'secrets_path': fields.char('Secrets path', size=100, required=True),
        'credential_path': fields.char(
            'Credential path', size=100, required=True),
        'synchronize': fields.boolean('Auto synchronize'),
        'use_local_browser': fields.boolean(
            'Use local browser',
            help="""If you can not run a local browser on the machine where
            Odoo-Server is running on, please deactivate this option.
            For getting authorized you must start Odoo-Server in
            interactive mode. After clicking on 'Authorize' you willbe asked
            to enter a verification code."""
        ),
    }

    _defaults = {
        'secrets_path': 'client_secrets.json',
        'credential_path': 'credentials.dat',
        'synchronize': True,
        'use_local_browser': True,
    }

    def do_authorize(self, cr, uid, ids, context=None):

        account = self.browse(cr, uid, ids[0])

        FLOW = client.flow_from_clientsecrets(
            account.secrets_path,
            scope=[
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/calendar.readonly',
                'https://www.google.com/m8/feeds',
            ],
            message=tools.message_if_missing(account.secrets_path)
        )

        storage = file.Storage(account.credential_path)
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            parser = argparse.ArgumentParser(
                description=__doc__,
                formatter_class=argparse.RawDescriptionHelpFormatter,
                parents=[tools.argparser]
            )
            if not account.use_local_browser:
                flags = parser.parse_args(['--noauth_local_webserver'])
            else:
                flags = parser.parse_args([])
            credentials = tools.run_flow(FLOW, storage, flags)

        raise orm.except_orm(
            _(u'Done.'),
            _(u'Please verify if your credential file is created or updated.'))


class GoogleApiCalendar(orm.Model):

    _name = 'google.api.calendar'
    _columns = {
        'account_id': fields.many2one(
            'google.api.account', 'Account', required=True),
        'user_id': fields.many2one(
            'res.users', 'User', required=True),
        'calendar_id': fields.char(
            'Google calendar id', size=100, required=True),
    }

    _sql_constraints = [
        (
            'pu-key-1',
            'UNIQUE (user_id)',
            'User already assigned to a google calendar!'
        ),
        (
            'pu-key-2',
            'UNIQUE (calendar_id)',
            'Google calendar already assigned to another user!'
        ),
    ]

    def do_synchronize(self, cr, uid, ids, context=None):

        instance = self.browse(cr, uid, ids[0])

        meeting_pool = self.pool.get('crm.meeting')
        del_pool = self.pool.get('crm.meeting.deleted')

        try:
            storage = file.Storage(instance.account_id.credential_path)
            credentials = storage.get()
            http = httplib2.Http()
            http = credentials.authorize(http)
        except:
            raise orm.except_orm(
                _(u'Authorize failed'),
                _(
                    u'The credentials have been revoked or expired, '
                    u'please authorize your account.'
                )
            )

        # construct the service object for the interacting
        # with the Calendar API.
        service = discovery.build(
            'calendar', 'v3', http=http)

        # build a list with all google-events-id present in
        # crm_meeting for this user
        google_event_ids = meeting_pool.search(
            cr, uid,
            [
                ('user_id', '=', instance.user_id.id),
                ('google_event_id', '!=', False)
            ]
        )
        data = meeting_pool.read(
            cr, uid, google_event_ids, ['google_event_id'])
        google_event_ids = []
        for item in data:
            google_event_ids.append(item['google_event_id'])

        # first sync events from google with crm_meeting
        page_token = None
        while True:
            events = service.events().list(
                calendarId=instance.calendar_id,
                pageToken=page_token).execute()
            for event in events['items']:
                is_deleted = del_pool.search(
                    cr, uid,
                    [
                        ('user_id', '=', instance.user_id.id),
                        ('google_event_id', '=', event['id'])
                    ]
                )
                if not is_deleted:
                    # check if google event already in openerp
                    crm_meeting = meeting_pool.search(
                        cr, uid,
                        [
                            ('user_id', '=', instance.user_id.id),
                            ('google_event_id', '=', event['id'])
                        ]
                    )
                    if crm_meeting:
                        if event.get('updated', False):
                            updated_google = dateutil.parser.parse(
                                event['updated']).astimezone(
                                    pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
                            updated_oe = meeting_pool.read(
                                cr, uid, crm_meeting[0], ['write_date'])
                            updated_oe = dateutil.parser.parse(
                                updated_oe['write_date']).strftime(
                                    '%Y-%m-%d %H:%M:%S')
                            # in this case do nothing,
                            #everything is synchronized
                            if updated_google == updated_oe:
                                if event['id'] in google_event_ids:
                                    google_event_ids.remove(event['id'])
                                continue
                            # check if we have to overwrite google
                            # with data from crm_meeting
                            if updated_google < updated_oe:
                                updated_event = meeting_pool.browse(
                                    cr, uid, crm_meeting[0])
                                start_utc = dateutil.parser.parse(
                                    updated_event.date)
                                end_utc = dateutil.parser.parse(
                                    updated_event.date_deadline)
                                if updated_event.allday:
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
                                    event = {
                                        'summary': updated_event.name,
                                        'description': (
                                            updated_event.description
                                            if updated_event.description
                                            else ''
                                        ),
                                        'location': updated_event.location,
                                        'start': {'date': start.strftime(
                                            '%Y-%m-%d')},
                                        'end': {
                                            'date': end.strftime('%Y-%m-%d')},
                                        'sequence':
                                        updated_event.google_sequence,
                                    }
                                else:
                                    event = {
                                        'summary': updated_event.name,
                                        'description': (
                                            updated_event.description
                                            if updated_event.description
                                            else ''
                                        ),
                                        'location': updated_event.location,
                                        'start': {
                                            'dateTime': start_utc.strftime(
                                                '%Y-%m-%dT%H:%M:%S.000Z')},
                                        'end': {
                                            'dateTime': end_utc.strftime(
                                                '%Y-%m-%dT%H:%M:%S.000Z')},
                                        'sequence':
                                        updated_event.google_sequence,
                                    }

                                try:
                                    service.events().update(
                                        calendarId=instance.calendar_id,
                                        eventId=updated_event.google_event_id,
                                        body=event,
                                        sendNotifications=False).execute()
                                except:
                                    logger.error(
                                        u'Update google calendar event failed '
                                        u'for id [%s] .'
                                        % (updated_event.google_event_id))

                                meeting_pool.write(
                                    cr, uid, updated_event.id,
                                    {
                                        'google_sequence':
                                        updated_event.google_sequence + 1
                                    },
                                    context={
                                        'stop_google_calendar_sync': 'True'})
                                if (
                                    updated_event.google_event_id
                                    in google_event_ids
                                ):
                                    google_event_ids.remove(
                                        updated_event.google_event_id)

                                continue

                    # convert dateTime to utc, skip events from google calendar
                    # when not all fields are present
                    if not ('start' in event and 'end' in event):
                        logger.error(
                            u'skipped event from google calendar due to '
                            u'missing fields. Event: %s' % (str(event)))
                        continue

                    start = event['start']
                    end = event['end']
                    if 'dateTime' in start:
                        start_utc = dateutil.parser.parse(
                            start['dateTime']).astimezone(pytz.utc)
                        end_utc = dateutil.parser.parse(
                            end['dateTime']).astimezone(pytz.utc)
                        diff = end_utc - start_utc
                        duration = round(
                            float(diff.days) * 24
                            + (float(diff.seconds) / 3600), 2)
                        allday = False
                    elif 'date'in start:
                        tz = (
                            pytz.timezone(instance.user_id.tz)
                            if instance.user_id.tz else pytz.utc
                        )
                        start_utc = dateutil.parser.parse(start['date'])
                        start_utc = pytz.utc.localize(start_utc).astimezone(tz)
                        # change start's time to 00:00:00
                        start_utc = start_utc.replace(
                            hour=0, minute=0, second=0)

                        end_utc = dateutil.parser.parse(end['date'])
                        end_utc = pytz.utc.localize(end_utc).astimezone(tz)
                        # change start's time to 00:00:00
                        end_utc = end_utc.replace(
                            hour=0, minute=0, second=0)

                        diff = end_utc - start_utc
                        duration = round(
                            float(diff.days) * 24
                            + (float(diff.seconds) / 3600), 2)
                        allday = True
                        # convert start back to utc
                        start_utc = start_utc.astimezone(pytz.utc)
                        # convert end back to utc
                        end_utc = end_utc.astimezone(pytz.utc)

                    if crm_meeting:
                        if event.get('updated', False):
                            updated_google = dateutil.parser.parse(
                                event['updated']).astimezone(
                                    pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
                            updated_oe = meeting_pool.read(
                                cr, uid, crm_meeting[0], ['write_date'])
                            updated_oe = dateutil.parser.parse(
                                updated_oe['write_date']).strftime(
                                    '%Y-%m-%d %H:%M:%S')
                            # overwrite crm_meeting with data from google
                            if updated_google > updated_oe:
                                meeting_pool.write(
                                    cr, uid, crm_meeting,
                                    {
                                        'name': event.get('summary', ''),
                                        'description': event.get(
                                            'description', ''),
                                        'date': start_utc.strftime(
                                            '%Y-%m-%d %H:%M:%S'),
                                        'date_deadline': end_utc.strftime(
                                            '%Y-%m-%d %H:%M:%S'),
                                        'duration': duration,
                                        'allday': allday,
                                        'location': event.get(
                                            'location', '')
                                    },
                                    context={
                                        'stop_google_calendar_sync': 'True'})
                        else:
                            meeting_pool.write(
                                cr, uid, crm_meeting,
                                {
                                    'name': event.get('summary', ''),
                                    'description': event.get('description'),
                                    'date': start_utc.strftime(
                                        '%Y-%m-%d %H:%M:%S'),
                                    'date_deadline': end_utc.strftime(
                                        '%Y-%m-%d %H:%M:%S'),
                                    'duration': duration,
                                    'allday': allday,
                                    'location': event.get('location', '')
                                },
                                context={
                                    'stop_google_calendar_sync': 'True'})
                    else:
                        meeting_pool.create(
                            cr, uid,
                            {
                                'user_id': instance.user_id.id,
                                'name': event.get('summary', ''),
                                'description': event.get('description'),
                                'date': start_utc.strftime(
                                    '%Y-%m-%d %H:%M:%S'),
                                'date_deadline': end_utc.strftime(
                                    '%Y-%m-%d %H:%M:%S'),
                                'duration': duration,
                                'allday': allday,
                                'location': event.get('location', ''),
                                'google_event_id': event['id']
                            }, context={'stop_google_calendar_sync': 'True'})
                    if event['id'] in google_event_ids:
                        google_event_ids.remove(event['id'])
            page_token = events.get('nextPageToken')
            if not page_token:
                break

        # now sync new crm_meetings with google
        new_events = meeting_pool.search(
            cr, uid,
            [
                ('user_id', '=', instance.user_id.id),
                ('google_event_id', '=', False)
            ]
        )
        for new_event in meeting_pool.browse(cr, uid, new_events):
            start_utc = dateutil.parser.parse(new_event.date)
            end_utc = dateutil.parser.parse(new_event.date_deadline)
            if new_event.allday:
                tz = (
                    pytz.timezone(instance.user_id.tz)
                    if instance.user_id.tz else pytz.utc
                )
                # convert start in user's timezone
                start = pytz.utc.localize(start_utc).astimezone(tz)
                # convert end in user's timezone
                end = pytz.utc.localize(end_utc).astimezone(tz)
                event = {
                    'summary': new_event.name,
                    'description': (
                        new_event.description
                        if new_event.description else ''
                    ),
                    'location': new_event.location,
                    'start': {
                        'date': start.strftime('%Y-%m-%d')},
                    'end': {
                        'date': end.strftime('%Y-%m-%d')},
                }
            else:
                event = {
                    'summary': new_event.name,
                    'description': (
                        new_event.description
                        if new_event.description else ''
                    ),
                    'location': new_event.location,
                    'start': {
                        'dateTime': start_utc.strftime(
                            '%Y-%m-%dT%H:%M:%S.000Z')},
                    'end': {
                        'dateTime': end_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                    },
                }

            try:
                google_new_event = service.events().insert(
                    calendarId=instance.calendar_id,
                    body=event, sendNotifications=False).execute()
            except:
                logger.error(
                    u'Insert google calendar event failed for crm_meeting id '
                    u'[%d] .' % (new_event.id))
                google_new_event = False

            if google_new_event:
                meeting_pool.write(
                    cr, uid, new_event.id,
                    {'google_event_id': google_new_event['id']})

        # delete events in google calendar which were deleted
        # in Odoo for this user
        delids = del_pool.search(
            cr, uid, [('user_id', '=', instance.user_id.id)])
        for del_event in del_pool.browse(cr, uid, delids):
            try:
                service.events().delete(
                    calendarId=instance.calendar_id,
                    eventId=del_event.google_event_id).execute()
            except:
                # handle it
                logger.error(
                    u'Delete google calendar event failed for id [%s] .'
                    % (del_event.google_event_id))
        del_pool.unlink(cr, uid, delids)

        # now delete all events from crm_meeting which were not updated and/or
        # created by google calendar, this ones are deleted in google calendar
        for gid in google_event_ids:
            delids = meeting_pool.search(
                cr, uid,
                [
                    ('user_id', '=', instance.user_id.id),
                    ('google_event_id', '=', gid)
                ]
            )
            meeting_pool.unlink(
                cr, uid, delids, context={'stop_google_calendar_sync': 'True'})

        return True

    def synchronize_accounts(self, cr, uid, ids=False, context=None):
        """WARNING: meant for cron usage only"""

        account_pool = self.pool.get('google.api.account')
        instance_pool = self.pool.get('google.api.calendar')

        accounts = account_pool.search(cr, uid, [('synchronize', '=', True)])
        for account_id in accounts:
            instances = instance_pool.search(
                cr, uid, [('account_id', '=', account_id)])
            for instance_id in instances:
                try:
                    instance_pool.do_synchronize(
                        cr, uid, [instance_id], context=None)
                except:
                    logger.error('Auto synchronizing failed.')
