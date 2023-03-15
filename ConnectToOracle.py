import subprocess
import cx_Oracle
import getpass
import pathlib
import logging
import re
import variable

#logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

db_logger = logging.getLogger('connect-to-oracle-log')
if not db_logger.handlers:
    db_fh = logging.FileHandler('connect-to-oracle-debug.log')
    db_logger.setLevel(logging.DEBUG)
    db_fh.setFormatter(formatter)
    db_logger.addHandler(db_fh) #add the file handler to the logger



def docker_cred() -> str:
    """Use this to get into the Docker container DB as SYSTEM or SYS. This assumes you have this path on your computer: C:\docker\pdb_tools\set_parms.md """

    
    try:
        docker_path = pathlib.Path(r"C:\docker\pdb_tools")
        docker_path = docker_path / r"set_parms.md"

        if docker_path.is_file():
            important_file = None
            with open(docker_path) as the_file:
                important_file = the_file.readlines()

            for line in important_file:
                found_line = re.search(r'ORACLE_PWD', line)
                if found_line:
                    password = line.split("|")
                    password = password[3].strip()
                    #print(f"[+] Password is: {password}")
                    
                    return password
        else:
            print("[-] File not found.")
            raise Exception("The 'set_parms.md' file was not found to access the Docker container database.")

    except Exception as e:
        print(f"Exception thrown in 'docker_cred'. Exception is -> {e}")
        raise Exception("Unable to Authenticate to the Docker container database.")
    


def get_in() -> str:
    """Get the database password stored on disk. C:\\Users\\<yourUserName>\\Desktop\crystal_skull.txt"""
    
    from_file = '' 
    try:
        username = getpass.getuser().strip()
        p = pathlib.Path(r'C:\Users')
        p = p / username / r'Desktop/crystal_skull.txt'
        
        
        if p.is_file():
            f = open(p, 'r')
            from_file = f.read()
            f.close()
            return from_file
        else:
            print("[-] Password file not found. Looking for %s." % str(p))
            exit()
        
    except Exception as e:
        print(f"Exception thrown reading password file: {e}")


def db_stuff(pdb, docker=None):
    """connect to the database as 'devdba' """

    PDB = pdb
    HOST = 'localhost'

    try:
        ret = subprocess.run('docker -v', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, encoding='utf-8')
        if ret.stdout.startswith("Docker version "):
            print("[*] This is a local docker connection.")
            db_logger.debug("[*] This is a local docker connection.")
            HOST = 'localhost'
        elif ret.stderr.startswith(r"'docker' is not recognized"):
            HOST = 'dockerhost'
            print("[*] This is a remote docker connection. We are in the cloud.")
            db_logger.debug("[*] This is a remote docker connection. We are in the cloud.")
            
        else:
            db_logger.debug("[!] How did the code get here in ConnectToOracle.db_stuff()")
            print("[!] How did the code get here in ConnectToOracle.db_stuff()")
            
    except Exception as dse:
        print("[!] Exception thrown determining if local or remote connection.")
        
    

    if docker:
        if variable.MODE == "foo":
            
            if pdb == "fooPDB1":
                SERVICE_NAME = "foopdb1.the_biz.local"
            elif pdb == "fooPDB2":
                SERVICE_NAME = "fooPDB2.the_biz.local"
                    
            if docker == "ORADB12R1_OEL":
                PORT = '1521'
            elif docker == "Oradb19r3Apx20r1":
                PORT = '1523'
                 
        elif variable.MODE == "egg":
            
            if pdb == "eggPB1":
                SERVICE_NAME = "eggpdb1.the_biz.local"
            elif pdb == "eggPDB2":
                SERVICE_NAME = "eggpdb2.the_biz.local"
                
            if docker == "ORADB12R1_OEL":
                PORT = '1521'       
            elif docker == "Oradb19r3Apx20r1":
                PORT = '1523'
            elif docker == "Ora19r3":
                PORT = "1524"
            
        elif variable.MODE == "MONO":
            if docker == "Ora19r3":
                PORT = '1524'       
            elif docker == "Oradb19r3Apx20r1":
                PORT = "1523"
                
            if pdb == "BLAHDB1":
                SERVICE_NAME = "BLAHPDB1.the_biz.local"   
            elif pdb == "BLAHPDB2":
                SERVICE_NAME = "BLAHPDB2.the_biz.local"
                
                    
                    
                    
            
    else: #not docker - doubtful this code will be used but the code is here anyway
        if variable.MODE == "foo":
            PORT = '1521'
            if pdb == "fooPDB1":
                SERVICE_NAME = "foopdb1.the_biz.local"
                
            elif pdb == "fooPDB2":
                SERVICE_NAME = "foopdb2.the_biz.local"
                
            elif pdb == "fooPDB3":
                SERVICE_NAME = "foopdb3.the_biz.local"
                
            else:
                print("[-] The code in 'db_stuff' should not of reached this point.")
                print("[-] Please specify a valid PDB.")
                exit()
        elif variable.MODE == "egg":
            PORT = '1524'
            if pdb == "eggPDB1":
                SERVICE_NAME = "eggpdb1.the_biz.local"
            elif pdb == "eggPDB2":
                SERVICE_NAME = "eggpdb2.the_biz.local"
            elif pdb == "eggPDB3":
                SERVICE_NAME = "eggpdb3.the_biz.local"
            else:
                print("[-] The code in 'db_stuff' should not of reached this point.")
                print("[-] Please specify a valid PDB.")
                exit()
            
            
        
    
    database = cx_Oracle.makedsn(HOST, PORT, service_name=SERVICE_NAME)
    connection = cx_Oracle.connect(user='username', password="password", dsn=database)
    db_logger.debug("Connected to database %s as username" % SERVICE_NAME)
    cursor1 = connection.cursor()

    return cursor1, connection        
        

def toggle_circular_constraints(enable=True, docker_mode=None):
     """Turn the circular constraints on and off. Pass in whether to enable or disable the circular constraints."""

     db_logger.info("[+] At the top of the 'toggle_circular_constraints' function.")

     for pdb in variable.PDBS:

         db_logger.debug(f"About to connect to pdb = {pdb}")
         db_logger.debug(f"For the connection docker_mode = {docker_mode}")
         cursor_t, connection1 = db_stuff(pdb,docker_mode)
         cursor_t.callproc("dbms_output.enable")

         #these variables are for writing to a file later
         name = None
         timestamp = None
         


         if enable:
             toggle = "ENABLE"
         else:
             toggle = "DISABLE"

         returned_stuff = [''] * 4
         #returned_stuff[0] = cursor_t.execute(f'alter session set container = {pdb}')
         #db_logger.debug(f"Setting the container to {pdb} returned the following: {returned_stuff[0]}")
         returned_stuff[0] = cursor_t.execute("SELECT SYS_CONTEXT ('USERENV', 'SESSION_USER') FROM DUAL")
         db_logger.debug("The current user is: %s " % str(returned_stuff[0]))
         returned_stuff[1] = cursor_t.execute("select name from v$services")

         if returned_stuff[1]:
             name = returned_stuff[1].fetchone()
             if name:
                 print(f"[+] Name: {name}")
                 db_logger.debug(f"[+] Current pdb name: {name}")
             
         returned_stuff[2] = cursor_t.execute("select to_char(current_date, 'DD-MM-YYYY HH:MI:SS') from dual")

         if returned_stuff[2]:
             timestamp = returned_stuff[2].fetchone()
             if timestamp:
                 print(f"[+] Timestamp: {timestamp}")
                 db_logger.debug(f"[+] The time as of now: {timestamp}")
             
         try:
            #outValue = cursor_t.var(str, 1000000)
            returned_stuff[3] = cursor_t.callproc("DEVDBA.circular_fks", [toggle])


            """
            try:
                outValueParsed = str(outValue)
                parsed_out = outValueParsed.split('alter')
                
            except Exception as e:
                db_logger.error("[-] Error trying to parse outValue -> %s" % str(e))

            if outValue:
                db_logger.debug("*" * 40)
                db_logger.debug("outValue")
                db_logger.debug("*" * 40)
                for i,v in enumerate(parsed_out):
                    if i == 0:
                        db_logger.debug(v)
                    else:
                        db_logger.debug('alter' + v)
                db_logger.debug("*" * 40)
                print("[+] Check log for the outValue")
            """

            #print(f"[++] returned_stuff[3] = {returned_stuff[3]} data-type of returned_stuff[3] = {type(returned_stuff[3])}")
            if returned_stuff[3]:
                
                print(f"[+] Circular_Fks Procedure returned this value = {returned_stuff[3]}")
                db_logger.debug(f"[+] Circular_fks Procedure returned this value = {returned_stuff[3]}")
            
            else:
                print("[-] Nothing returned from the procedure.")
                db_logger.debug("[-] Nothing returned from the circular_fks procedure.")
         except Exception as e:
            #read the dbms_output buffer here and print it to the console if an exception is thrown
            
            
            db_logger.error(f"[+] Problems with PDB: {pdb}")
            db_logger.error("[+] In the exception block.")
            db_logger.error("[+] This is the exception: %s" % str(e))
            print("[+] In the exception block.")
            print("[+] This is the exception: %s" % str(e))
            print("\n\n\n")

            #The following code Duane found and is from here: https://gist.github.com/TerryMooreII/3773572 - Ty Terry! :)
            #begin Terry's code
            statusVar = cursor_t.var(cx_Oracle.NUMBER)
            lineVar = cursor_t.var(cx_Oracle.STRING)
            while True:
                cursor_t.callproc("dbms_output.get_line", (lineVar, statusVar))
                #print(f"[+] statusVar = {statusVar}")
                if statusVar.getvalue() != 0:
                    break
                print(lineVar.getvalue())
                db_logger.error(lineVar.getValue())
                

            #end Terry's code. :D 
            
            
            assert "ORA-20001" not in str(e), f"Error trying to {toggle} the circular constraints."


         print(f"[+] Circular-constraint state: {toggle} for pluggable-database(PDB): {pdb}")
         db_logger.info(f"[+] Circular-constraint state: {toggle} for pluggable-database(PDB): {pdb}")
         cursor_t.close() #explicitly close the open cursor
         db_logger.debug("[+] Database cursor closed.")

         

     db_logger.info("[+] toggle_circular_constraints function complete.")
     return returned_stuff


def connectForAUpgrade(upgrade_script):
    """This function should connect to PDB1 - upgrade - on the localhost.
       This function also creates a log file named "upgrade_deployment.log". 
    """
    
    sqlplus_script = """connect / AS SYSDBA
    column name format A30;
    spool upgrade_deployment.log
    alter session set container = fooPDB1;
    select name from v$services;
    select systimestamp from v$services;
    select sys_context('USERENV', 'CON_NAME') from v$services;
    prompt "Going to execute a script now!"
    @@%s
    spool off
    """ % (upgrade_script)
    
    run_sqlplus(sqlplus_script)

    return "upgrade_deployment.log"


def connectForADowngrade(downgrade_script):
    """This function should connect to PDB2 and then execute a script. This function also creates
       a log file named, "downgrade_deployment.log". 
    """
    sqlplus_script = """connect / AS SYSDBA
    column name format A30;
    spool downgrade_deployment.log
    alter session set container = fooPDB2;
    select name from v$services;
    select systimestamp from v$services;
    select sys_context('USERENV', 'CON_NAME') from v$services;
    prompt "Going to execute a script now!"
    @@%s
    spool off
    """ % (downgrade_script)
    
    run_sqlplus(sqlplus_script)

    return "downgrade_deployment.log"

def docker_deploy(script, container_d='ORADB12R1_OEL', up=True, ddl_release=True):
    """deploy a SQL release to a container database. Call 'docker_copy' or 'docker cp' first to get the deployment script over to the container. :)"""

    db_logger.debug("At the top of the 'docker_deploy' function.")
    
    D_PDB = None
    direction = None
    sqlplus_script = None
    scripts_path = None
    
    if up:
        db_logger.debug("This is an upgrade deployment to the docker container.")
        
        direction = "upgrade"
        
        if variable.MODE == "foo":
            D_PDB = 'fooPDB1'
            scripts_path = r"/workspace/foo/foo-db/install/core/"
        elif variable.MODE == "egg":
            D_PDB = "eggPDB1"
            scripts_path = r"/workspace/eggHorizon/egg-db/install/core/"
        elif variable.MODE == "MONO":
            D_PDB = "RHRZPDB1"
            scripts_path = r"/workspace/monorepo/egghorizon/egg-db/install/core/"

        db_logger.debug(f"MODE = {variable.MODE}, D_PDB = {D_PDB}, scripts_path = {scripts_path}, direction = {direction}")
            
            
    else:
        db_logger.debug("This is a downgrade deployment to the docker container.")
        
        direction = "downgrade"
        
        if variable.MODE == "foo":
            D_PDB = 'fooPDB2'
            scripts_path = r"/workspace/foo/foo-db/install/core/"
        elif variable.MODE == "egg":
            D_PDB = "eggPDB2"
            scripts_path = r"/workspace/eggHorizon/egg-db/install/core/"
        elif variable.MODE == "MONO":
            D_PDB = "RHRZPDB2"
            scripts_path = r"/workspace/monorepo/egghorizon/egg-db/install/core/"
            

        db_logger.debug(f"MODE = {variable.MODE}, D_PDB = {D_PDB}, scripts_path = {scripts_path}, direction = {direction}")            
            
        

    if ddl_release:
        db_logger.debug("Creating the DDL script.")

        sqlplus_script = f"""
        column name format A30;
        spool {direction}_docker_deployment.log
        alter session set container = {D_PDB};
        select name from v$services;
        select systimestamp from v$services;
        prompt listing host directory
        host dir;
        prompt host directory listing complete
        select sys_context('USERENV', 'CON_NAME') from v$services;
        prompt "Going to execute a script now!"
        set serveroutput on size unlimited
        @@{script}
        set serveroutput on size unlimited
        prompt Recompiling the database now.
        @{scripts_path}compile_all.sql
        prompt Re-compilation complete.
        prompt Obtaining invalids now.
        @{scripts_path}list_invalids.sql
        prompt Invalids should be listed.
        prompt DDL Deployment complete.
        
        spool off
        """
    else:
        db_logger.debug("Creating the DML script.")
        
        sqlplus_script = f"""
        column name format A30;
        spool {direction}_docker_deployment.log
        alter session set container = {D_PDB};
        select name from v$services;
        select systimestamp from v$services;
        prompt listing host directory
        host dir;
        prompt host directory listing complete
        select sys_context('USERENV', 'CON_NAME') from v$services;
        prompt "Going to execute a script now!"
        @@{script}
        prompt DML deployment complete.
        spool off
        """
        

    #put the script in the home folder of the docker container before trying to deploy
    
    db_logger.debug("Calling 'docker_run_sqlplus' to deploy this script just created.")
    stdout, stderr = docker_run_sqlplus(sqlplus_script, container_d)
    db_logger.debug("Call to 'docker_run_sqlplus' complete.")

    return f"{direction}_docker_deployment.log", stdout, stderr


def docker_copy(container_d="ORADB12R1_OEL", source=r"C:\Users\ksmith\Desktop\test_docker_db\foobar.sql", target="/home/oracle/"):
    """Copy the deployment script to the Docker container $home folder """
    
    copy_feedback =  subprocess.Popen(f'docker cp {source} {container_d.strip()}:{target} ', stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True, text=True)

    out, err = copy_feedback.communicate()

    return out, err


def docker_copy_host(destination, source=r"/home/oracle/hello.txt", container_d="ORADB12R1_OEL"):
    """Copy files from the container to the host operating-system (OS)"""

    copy_host_feedback = subprocess.Popen(f"docker cp {container_d.strip()}:{source} {destination}", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            shell=True, text=True)

    out, err = copy_host_feedback.communicate()

    return out, err
    

def docker_run_sqlplus(sqlplus_script, container_d):
    """Run a sql command or a group of commands against the docker container database using sqlplus. """

    db_logger.debug("At the top of the 'docker_run_sqlplus' script.")
    
    #test which CDB to connect to based on the container_d passed in? Ex: if Oradb19r3Apx20r1 then use TNS name alias CDB19R3LOCAL
    if container_d == "Oradb19r3Apx20r1":
        
        
        if variable.MODE == "foo":
            print("[*] Deploying to the Oradb19r3Apx20r1 container with TNS name alias CDB19R3LOCAL")
            db_logger.debug("[*] Deploying to the Oradb19r3Apx20r1 container with TNS name alias CDB19R3LOCAL")
            TNS_ALIAS = "CDB19R3LOCAL"
        else:
            print("[*] Deploying to the Oradb19r3Apx20r1 container with TNS name alias eggPDB1LOCAL")
            db_logger.debug("[*] Deploying to the Oradb19r3Apx20r1 container with TNS name alias eggPDB1LOCAL")
            TNS_ALIAS = "eggPDB1LOCAL"
            
    elif container_d == "Ora19r3":
        if variable.MODE == "egg":
            print("[*] Deploying to the Ora19r3 container with TNS name alias eggPDB1R3LOCAL ")
            db_logger.debug("[*] Deploying to the Ora19r3 container with TNS name alias eggPDB1R3LOCAL ")
            TNS_ALIAS = "eggPDB1R3LOCAL"
        elif variable.MODE == "MONO":
            print("[*] Deploying to the Ora19r3 container with TNS name alias CDB19NAREMOTE ")
            db_logger.debug("[*] Deploying to the Ora19r3 container with TNS name alias CDB19NAREMOTE")
            TNS_ALIAS = "CDB19NAREMOTE"
        else:
            print(f"[!] There is currently not a TNS_ALIAS for Git repository {variable.MODE} for container {container_d}. Please update ConnectToOracle.docker_run_sqlplus.")
            db_logger.debug(f"[!] There is currently not a TNS_ALIAS for Git repository {variable.MODE} for container {container_d}. Please update ConnectToOracle.docker_run_sqlplus.")
            raise Exception("TNS_ALIAS currently not available. Please update 'ConnectToOracle.docker_run_sqlplus' :).")
    else:
        print("[!] The script does not recognize this container. Please add code to this function (ConnectToOracle.docker_run_sqlplus) for the new container.")
        db_logger.debug("[!] The script does not recognize this container. Please add code to this function (ConnectToOracle.docker_run_sqlplus) for the new container.")
        exit()


    db_logger.debug("Getting the Docker credentials.")
    password = docker_cred()

    db_logger.debug(f"Connecting to the container database: {TNS_ALIAS}")
    docker_handle = subprocess.Popen(f'sqlplus system/{password}@{TNS_ALIAS}', stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     shell=True, text=True)

    db_logger.debug("Deploying script.")
    stdout, stderr = docker_handle.communicate(sqlplus_script.strip()) #execute the script on the database and get the standard out and error streams
    db_logger.debug("Script deployed.")

    return stdout,stderr
    
def run_sqlplus(sqlplus_script):
    """ Run a sql command or group of commands against database using sqlplus """

    p = subprocess.Popen(['sqlplus', '/nolog'], stdin=subprocess.PIPE,
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    (stdout, stderr) = p.communicate(sqlplus_script.encode('utf-8'))

    stdout_lines = stdout.decode('utf-8').split('\n')

    return stdout_lines




def fix_persistent_show_stopper(docker_mode=None):
    """ Connect to to both PDB1 and PDB2 and run the same update statement to prevent a table from appearing in the circular_check_vw view that stops the release."""

    db_logger.debug('[+] At the top of "fix_persistent_show_stopper".')
    
    for pdb in variable.PDBS:

        db_logger.debug(f'[+] The current PDB is {pdb}')
        #get cursor
        fix_cursor, connection_fix = db_stuff(pdb, docker_mode)

        fix_cursor.execute("""update devdba.circular_list
    set  p_const = (select p_const
                   from  devdba.circular_list_vw
                   where fk_const = 'FKNHESQVNYIWP5WICJYJSTMVP9F')
    where fk_const = 'FKNHESQVNYIWP5WICJYJSTMVP9F'
        """)

        connection_fix.commit()
        

        fix_cursor.close()
        db_logger.debug("[+] Update to devdba.circular_list complete.")

        


if __name__ == "__main__":

    end_user = 'silver_surfer'
    print("Starting program!")
    import time
    print(("%s" % time.asctime()))
    print("\n")
    

    sqlplus_script = """connect / AS SYSDBA
     column name format A30;
     select name, sys_context('USERENV', 'CON_NAME'), systimestamp from v$database;
     select name, pdb from v$services;
     show con_name;
     prompt "%s was here!"
     prompt ""

     alter session set container = fooPDB1;
     select name, pdb from v$services;
     show con_name;
     prompt "Going to execute a script now!"
     @@foobar.sql
    """ % (end_user) 

    sqlplus_output = run_sqlplus(sqlplus_script)

    for line in sqlplus_output:
        print(line)

    print("program complete.")
