# coding: utf-8

import os, sys, platform, cgi, socket, pip

def pyinfo():
    output  = '<!DOCTYPE html>\n'
    output += '<html>'
    output +=  '<head>'
    output +=   '<title>pyinfo()</title>'
    output +=   '<meta name="robots" content="noindex,nofollow,noarchive,nosnippet">'
    output +=    styles()
    output +=  '</head>'
    output +=  '<body>'
    output +=   '<div>'
    output +=     section_title()

    output +=     '<h2>System</h2>'
    output +=     section_system()

    output +=     '<h2>OS Internals</h2>'
    output +=     section_os_internals()

    output +=     '<h2>Python Internals</h2>'
    output +=     section_py_internals()

    output +=     '<h2>Python PIP</h2>'
    output +=     section_python()

    output +=     '<h2>WSGI Environment</h2>'
    output +=     section_environ()

    output +=     '<h2>Database support</h2>'
    output +=     section_database()

    output +=     '<h2>Compression and archiving</h2>'
    output +=     section_compression()

    if sys.modules.has_key('ldap'):
        output += '<h2>LDAP support</h2>'
        output += section_ldap()

    if sys.modules.has_key('socket'):
        output += '<h2>Socket</h2>'
        output += section_socket()

    output +=     '<h2>Multimedia support</h2>'
    output +=     section_multimedia()

    output +=     '<h2>Copyright</h2>'
    output +=     section_copyright()

    output +=   '</div>'
    output +=  '</body>'
    output += '</html>'
    return output

def styles():
    css  = '<style type="text/css">'
    css +=  'body{background-color:#fff;color:#000}'
    css +=  'body,td,th,h1,h2{font-family:sans-serif}'
    css +=  'pre{margin:0px;font-family:monospace}'
    css +=  'a:link{color:#009;text-decoration:none;background-color:#fff}'
    css +=  'a:hover{text-decoration:underline}'
    css +=  '.center{text-align:center}'
    css +=  '.center table{margin-left:auto;margin-right:auto;text-align:left}'
    css +=  '.center th{text-align:center !important}'
    css +=  'td,th{border:1px solid #999999;font-size:75%;vertical-align:baseline}'
    css +=  'h1{font-size:150%}'
    css +=  'h2{font-size:125%}'
    css +=  '.p{text-align:left}'
    css +=  '.e{width:30%;background-color:#ffffcc;font-weight:bold;color:#000}'
    css +=  '.h{background:url(\'http://python.org/images/header-bg2.png\') repeat-x;font-weight:bold;color:#000}'
    css +=  '.v{background-color:#f2f2f2;color:#000}'
    css +=  '.vr{background-color:#cccccc;text-align:right;color:#000}'
    css +=  'img{float:right;border:0px;}'
    css +=  'hr{width:600px;background-color:#ccc;border:0px;height:1px;color:#000}'
    css += '</style>'
    return css

def table(html):
    return '''<table
               class="table table-hover table-condensed">
                %s
            </table><br>''' % html

def makecells(data):
    html = ''
    while data:
        html += '<tr><td class="e">%s</td><td class="v">%s</td></tr>' % (data.pop(0), data.pop(0))
    return table(html)

def imported(module):
    if sys.modules.has_key(module):
        return 'enabled'
    return 'disabled'

def section_title():
    html  = '<tr class="h"><td>'
    html +=  '<a href="http://python.org/"><img border="0" src="http://python.org/images/python-logo.gif"></a>'
    html +=  '<h1 class="p">Python %s</h1>' % platform.python_version()
    html += '</td></tr>'
    return table(html)

def section_system():
    data = []
    if hasattr(sys, 'subversion'): data += 'Python Subversion', ', '.join(sys.subversion)
    if platform.dist()[0] != '' and platform.dist()[1] != '':
        data += 'OS Version', '%s %s (%s %s)' % (platform.system(), platform.release(), platform.dist()[0].capitalize(), platform.dist()[1])
    else:
        data += 'OS Version', '%s %s' % (platform.system(), platform.release())
    if hasattr(sys, 'executable'): data += 'Executable', sys.executable
    data += 'Build Date', platform.python_build()[1]
    data += 'Compiler', platform.python_compiler()
    if hasattr(sys, 'api_version'): data += 'Python API', sys.api_version
    return makecells(data)

def section_python():
    data = []
    pip_data = pip.get_installed_distributions()
    for d in pip_data:
        data += ["%s %s" % (d.project_name, d.version), d.location]
    return makecells(data)

def section_py_internals():
    data = []
    if hasattr(sys, 'builtin_module_names'):
        data += 'Built-in Modules', ', '.join(sys.builtin_module_names)
    data += 'Byte Order', sys.byteorder + ' endian'
    if hasattr(sys, 'getcheckinterval'):
        data += 'Check Interval', sys.getcheckinterval()
    if hasattr(sys, 'getfilesystemencoding'):
        data += 'File System Encoding', sys.getfilesystemencoding()
    data += 'Maximum Integer Size', str(sys.maxint) + ' (%s)' % str(hex(sys.maxint)).upper().replace("X", "x")
    if hasattr(sys, 'getrecursionlimit'):
        data += 'Maximum Recursion Depth', sys.getrecursionlimit()
    if hasattr(sys, 'tracebacklimit'):
        data += 'Maximum Traceback Limit', sys.tracebacklimit
    else:
        data += 'Maximum Traceback Limit', '1000'
    data += 'Maximum Unicode Code Point', sys.maxunicode

    return makecells(data)

def section_os_internals():
    data = []
    if hasattr(os, 'getcwd'):     data += 'Current Working Directory', os.getcwd()
    if hasattr(os, 'getegid'):    data += 'Effective Group ID', os.getegid()
    if hasattr(os, 'geteuid'):    data += 'Effective User ID', os.geteuid()
    if hasattr(os, 'getgid'):     data += 'Group ID', os.getgid()
    if hasattr(os, 'getgroups'):  data += 'Group Membership', ', '.join(map(str, os.getgroups()))
    if hasattr(os, 'linesep'):    data += 'Line Seperator', repr(os.linesep)[1:-1]
    if hasattr(os, 'getloadavg'): data += 'Load Average', ', '.join(map(str, map(lambda x: round(x, 2), os.getloadavg())))
    if hasattr(os, 'pathsep'):    data += 'Path Seperator', os.pathsep
    try:
        if hasattr(os, 'getpid') and hasattr(os, 'getppid'):
            data += 'Process ID', ('%s (parent: %s)' % (os.getpid(), os.getppid()))
    except: pass
    if hasattr(os, 'getuid'): data += 'User ID', os.getuid()
    return makecells(data)

def section_environ():
    envvars = os.environ.keys()
    envvars.sort()
    data = []
    for envvar in envvars:
        data += envvar, cgi.escape(str(os.environ[envvar]))
    return makecells(data)

def section_database():
    data  = []
    data += 'DB2/Informix (ibm_db)',      imported('ibm_db')
    data += 'MSSQL (adodbapi)',           imported('adodbapi')
    data += 'MySQL (MySQL-Python)',       imported('MySQLdb')
    data += 'ODBC (mxODBC)',              imported('mxODBC')
    data += 'Oracle (cx_Oracle)',         imported('cx_Oracle')
    data += 'PostgreSQL (PyGreSQL)',      imported('pgdb')
    data += 'PostgreSQL (psycopg2)',      imported('psycopg2')
    data += 'Python Data Objects (PyDO)', imported('PyDO')
    data += 'SAP DB (sapdbapi)',          imported('sapdbapi')
    data += 'SQLite3',                    imported('sqlite3')
    return makecells(data)

def section_compression():
    data  = []
    data += 'Bzip2 Support', imported('bz2')
    data += 'Gzip Support',  imported('gzip')
    data += 'Tar Support',   imported('tarfile')
    data += 'Zip Support',   imported('zipfile')
    data += 'Zlib Support',  imported('zlib')
    return makecells(data)

def section_ldap():
    data = []
    try:
        import urls
        import ldap

        data += 'Python-LDAP Version' % urls['Python-LDAP'], ldap.__version__
        data += 'API Version',                               ldap.API_VERSION
        data += 'Default Protocol Version',                  ldap.VERSION
        data += 'Minimum Protocol Version',                  ldap.VERSION_MIN
        data += 'Maximum Protocol Version',                  ldap.VERSION_MAX
        data += 'SASL Support (Cyrus-SASL)',                 ldap.SASL_AVAIL
        data += 'TLS Support (OpenSSL)',                     ldap.TLS_AVAIL
        data += 'Vendor Version',                            ldap.VENDOR_VERSION
    except:
        data += 'No Ldap Support', 'Na'
    return makecells(data)

def section_socket():
    data  = []
    data += 'Hostname', socket.gethostname()
    data += 'Hostname (fully qualified)', socket.gethostbyaddr(socket.gethostname())[0]
    try:
        data += 'IP Address', socket.gethostbyname(socket.gethostname())
    except: pass
    data += 'IPv6 Support', getattr(socket, 'has_ipv6', False)
    data += 'SSL Support', hasattr(socket, 'ssl')
    return makecells(data)

def section_multimedia():
    data  = []
    data += 'AIFF Support',                    imported('aifc')
    data += 'Color System Conversion Support', imported('colorsys')
    data += 'curses Support',                  imported('curses')
    data += 'IFF Chunk Support',               imported('chunk')
    data += 'Image Header Support',            imported('imghdr')
    data += 'OSS Audio Device Support',        imported('ossaudiodev')
    data += 'Raw Audio Support',               imported('audioop')
    data += 'Raw Image Support',               imported('imageop')
    data += 'SGI RGB Support',                 imported('rgbimg')
    data += 'Sound Header Support',            imported('sndhdr')
    data += 'Sun Audio Device Support',        imported('sunaudiodev')
    data += 'Sun AU Support',                  imported('sunau')
    data += 'Wave Support',                    imported('wave')
    return makecells(data)

def section_copyright():
    html = '<tr class="v"><td>%s</td></tr>' % sys.copyright.replace('\n\n', '<br>').replace('\r\n', '<br />').replace('(c)', '&copy;')
    return table(html)

optional_modules_list = [
    'Cookie',
    'zlib', 'gzip', 'bz2', 'zipfile', 'tarfile',
    'ldap',
    'socket',
    'audioop', 'curses', 'imageop', 'aifc', 'sunau', 'wave', 'chunk', 'colorsys', 'rgbimg', 'imghdr', 'sndhdr', 'ossaudiodev', 'sunaudiodev',
    'adodbapi', 'cx_Oracle', 'ibm_db', 'mxODBC', 'MySQLdb', 'pgdb', 'PyDO', 'sapdbapi', 'sqlite3'
]
for i in optional_modules_list:
    try:
        module = __import__(i)
        sys.modules[i] = module
        globals()[i] = module
    except: pass
