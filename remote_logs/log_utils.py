# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (www.openerp.com)
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


import logging
from threading import Lock

class FIFOHandler(logging.handlers.BufferingHandler):
    """ A variation of the BufferingHandler, FIFO behaviour
    
    """
    
    def __init__(self, capacity, fill_thres=0.75):
        """ Initialize a handler with capacity and fill percentage.
            
            capacity is the number of records to hold maximum.
            fill_thres is the percentage of capacity to hold afer a flush
            
            We also keep a position counter, to let callers how much the
            FIFO has rolled.
        """
        super(FIFOHandler, self).__init__(capacity)
        self._min_recs = int(capacity * fill_thres)
        self._counter = 0
        self._bufferlock = Lock()
        
    def flush(self):
        try:
            if not self._bufferlock.acquire(False):
                return
            pos = len(self.buffer) - self._min_recs
            if pos <= 0:
                return
            self.buffer = self.buffer[pos:]
            self._counter += pos
            self._bufferlock.release()
        except Exception:
            self._bufferlock.release()
        
    def has_records(self, offset):
        """ Check if the FIFO contains any records above the offset mark
        
            With a negative offset, it will merely tell if there is any
            records in the buffer.
        """
        if offset < 0:
            return (len(self.buffer) > 0)
        return (self._counter + len(self.buffer)) > offset

    def get_cur_pos(self):
        return self._counter

    def get_records_fmt(self, offset, limit=None):
        """ Retrieve the formatted records after some mark
        """
        
        try:
            self._bufferlock.acquire()
            if offset > 0:
                pos = offset - self._counter
            else:
                pos = len(self.buffer) + offset

            if pos < 0: # snip?
                pos = 0
            
            while pos < len(self.buffer):
                yield self.format(self.buffer[pos])
                pos += 1
                if limit is not None and pos > limit:
                    break
        finally:
            self._bufferlock.release()

    def emit(self, record):
        super(FIFOHandler, self).emit(record)

class MachineFormatter(logging.Formatter):
    """ Machine-parseable log output, in plain text stream.
    
    In order to have parsers analyze the output of the logs, have
    the following format:
        logger[|level]> msg...
        + msg after newline
        :@ First exception line
        :+ second exception line ...
    
    It should be simple and well defined for the other side.
    """
    
    def format(self, record):
        """ Format to stream """
        
        levelstr = ''
        if record.levelno != logging.INFO:
            levelstr = '|%d' % record.levelno

        try:
            msgtxt = record.getMessage().replace('\n','\n+ ')
        except TypeError:
            print "Message:", record.msg
            msgtxt = record.msg

        s = "%s%s> %s" % ( record.name, levelstr, msgtxt)

        if record.exc_info and not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            s+= '\n:@ %s' % record.exc_text.replace('\n','\n:+ ')

        # return s.decode('utf-8')
        return s

#eof