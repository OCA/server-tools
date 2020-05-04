To use this module, you need to:

#. Configure and test you ftp/sftp/lsftp connection
#. Fetch the relevant server.ftp.folder record via it's xmlid
#. Code

``>>> folder = session.env.ref("server_ftp.server_ftp_pull_folder_01_ftp")
>>> folder_server_object = folder.connect()
# folder_server_object is lib.ftp_server.FtpServer object
# You can perform simple operations like ls, put, get, close etc
# with folder_server_object. See lib/abstract_ftp_model.py for more
>>> folder_server_object.listdir()
-rw-rw-r--    1 1001     1001            0 May 06 14:10 a_file.txt
-rw-rw-r--    1 1001     1001            0 May 06 14:21 another_file.txt
>>> server = folder_server_object.get_server()
# server is ftplib.FTP object
# so we can do anything in ftplib
>>> server.dir()
-rw-rw-r--    1 1001     1001            0 May 06 14:10 a_file.txt
-rw-rw-r--    1 1001     1001            0 May 06 14:21 another_file.txt
>>>
>>> folder_server_object.remove("a_file.txt")
>>> folder_server_object.listdir()
-rw-rw-r--    1 1001     1001            0 May 06 14:21 another_file.txt
>>> server.dir()
-rw-rw-r--    1 1001     1001            0 May 06 14:21 another_file.txt
>>> server.delete("another_file.txt")
'250 Delete operation successful.'
>>> folder_server_object.listdir()
>>> server.dir()
>>> folder_server_object.close() == server.quit()``
