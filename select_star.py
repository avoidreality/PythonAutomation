"""
This code is to test querying an Oracle database.

The program will select * from a database table. If there are any results
from the query one action will happen. If there are not any results
another action will happen.

Module design notes:
If nothing is returned from the SQL query this is good according to Duane's design.
If rows are returned then an error message is displayed as well as the rows. 

"""

import cx_Oracle
import getpass
import pathlib

USER = 'sys'
PASSWORD = ''
HOST = '127.0.0.1'
PORT = '1521'
PDB1 = 'foopdb1.megacorp.local'
PDB2 = 'foopdb2.megacorp.local'

def get_in():
    """Get the password from a file on disk. This requires a file located here C:\\Users\\username\\Desktop\\crystal_skull.txt containing the target DB password. """
    try:
        username = getpass.getuser().strip()
        #print("username = %s" % username)
        p = pathlib.Path(r'C:\Users')
        p = p / username / r'Desktop/crystal_skull.txt'
        
        
        if p.is_file():
            f = open(p, 'r')
            from_file = f.read()
            f.close()
        else:
            print("[-] Password file not found. Looking for %s." % str(p))
            exit()
        
    except Exception as e:
        print("Exception thrown reading password file")

    return from_file

def connect():
    """Connect to the database and return the connection handle"""
    

    #connect to the database mojo
    database = cx_Oracle.makedsn(HOST, PORT, service_name=PDB1)
    db_connection = cx_Oracle.connect(user=USER, password=get_in(), dsn=database, mode=cx_Oracle.SYSDBA)

    #query a table
    cursor_handle = db_connection.cursor()
    return cursor_handle

def select_star(cursor_handle, inject_me=None):
#cursor_handle.execute("""select * from sys_params where ROWNUM < 4""")

    if inject_me:
        cursor_handle.execute(inject_me)
    else:
        cursor_handle.execute("""select * from kyle_tab""") #this line will crash the program if the table does not exist. The program should fail anyway if this is the case.

    if cursor_handle:
        rows = set()
        for row in cursor_handle:
            rows.add(row)

        print("[+] Number of rows return: %d " % int(len(rows)))

        if rows: 

            print("[!] ERROR - Rows returned:")
            for row in rows:
                print("[+] [ROW] -> %s [DATATYPE] -> %s" %
                      (str(row), type(row))
                      )
        else:
            print("[+] There were not any rows returned.")
            #print("""Read the "Zen of Python" instead of database rows!\n""")
            #import this
                

if __name__ == "__main__":

    #test usage shown below - just run this module to execute
    cursor1 = connect()
    select_star(cursor1, "SELECT * FROM sys_params WHERE ROWNUM < 3")
    

