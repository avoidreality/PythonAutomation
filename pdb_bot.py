"""
    This module handles loading and unloading PDBs without a human's help.
    Humans destroy everything anyway, so this should make the process better.
    :)

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !! This works in a Cygwin shell. This will not work in CMD.exe. !!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
"""

import subprocess
import os
import cx_Oracle
import getpass
import pathlib
import logging
import sys
import re

TOOLS_DIR = "/usr/local/bin"
CYGWIN_PATH = "C:\\cygwin64"

PDB3 = 'FOOPDB3'
SERVICE_NAME = "orcl.megacorp.local"
PDBS = ['FOOPDB1', 'FOOPDB2']
HOST = 'localhost'
PORT = '1521'

#logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

pdb_bot_logger = logging.getLogger('pdb-bot-log')
if not pdb_bot_logger.handlers:
    pdb_bot_fh = logging.FileHandler('pdb-bot-debug.log')
    pdb_bot_logger.setLevel(logging.DEBUG)
    pdb_bot_fh.setFormatter(formatter)
    pdb_bot_logger.addHandler(pdb_bot_fh) #add the file handler to the logger


def get_in() -> str:
    "Get the password stored on disk. Write your database password on your desktop in a file named 'crystal_skull.txt' and this will work. :) "
    
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
            print("[-] pdb_bot.py - get_in() - > Password file not found. Looking for %s." % str(p))
            pdb_bot_logger.debug("[-] pdb_bot.py - get_in() - >  Password file not found. Looking for %s." % str(p))
            exit()
        
    except Exception as e:
        print(f"Exception thrown reading password file: {e}")
        pdb_bot_logger.debug(f"Exception thrown reading password file: {e}")


def open_pdb3() -> int:
    """ This opens PDB3 on the localhost. """

    pdb_bot_logger.info("[+] At the top of the 'open_pdb3' function.")

    database = cx_Oracle.makedsn(HOST, PORT, service_name=SERVICE_NAME)
    connection = cx_Oracle.connect(user='sys', password=get_in(), dsn=database, mode=cx_Oracle.SYSDBA)

    pdb_bot_logger.info("Database connection established.")
    query = connection.cursor()

    pdb_bot_logger.info("Database cursor obtained.")

    #first check what state the PDBs are in
    rows = query.execute("select name, open_mode from v$pdbs")
    rows_r = list(rows)
    
    pdb_bot_logger.debug("[+] 'rows_r' = %s" % str(rows_r))
    pdb_bot_logger.debug(f"[+] 'rows' = {repr(rows)}")

    #check to see if FOOPDB3 even exists in the container database (CDB)

    count = 0
    for row in rows_r:
        if isinstance(row, tuple):
            for element in row:
                if element == "FOOPDB3":
                    count = count + 1

    assert count == 1, "FOOPDB3 not found. Something went wrong somewhere." #if count != 1 This message is printed and the program ends.


    #loop through the results and open FOOPDB3 if needed
    for row in rows_r:
        #print(f"[+] Type: {type(row)} Row value: {row}")
        if "FOOPDB3" in row:
            print(f"[+] Found FOOPDB3")
            pdb_bot_logger.debug(f"[+] Found FOOPDB3")
            print(f"[+] {row}")
            pdb_bot_logger.debug(f"[+] {row}")
            if isinstance(row, tuple):
                if len(row) == 2:
                    pdb_state = row[1]
                    if pdb_state != "READ WRITE":
                        print(f"[+] Opening PDB3.")
                        try:
                            query.execute("alter pluggable database FOOPDB3 open")
                            print("[+] PDB3 should be open.")
                            pdb_bot_logger.info("[+] PDB3 should be open.")
                            return 0
                        except cx_Oracle.DatabaseError as de:
                            print(f"[!] There was an error opening PDB3. Error = {de}")
                            pdb_bot_logger.error(f"[!] There was an error opening PDB3. Error = {de}")
                    else:
                        print("[+] PDB3 is in READ WRITE. PDB3 is open.")
                        print(f"[+] PDB3 state = {pdb_state}")
                        pdb_bot_logger.debug("[+] PDB3 is in READ WRITE. PDB3 is open.")
                        pdb_bot_logger.debug(f"[+] PDB3 state = {pdb_state}")
                        return 0
                else:
                    print("[-] The length of the row is not 2. Something is wrong.")
                    pdb_bot_logger.error("[-] The length of the row is not 2. Something is wrong.")
                    return 1
            else:
                print("[-] The row is not a tuple. Very strange. Nothing good can come of this. Please debug.")
                pdb_bot_logger.error("[-] The row is not a tuple. Very strange. Nothing good can come of this. Please debug.")
                return 1
               

def open_the_pdbs() -> None:
    """This opens PDBs 1 and 2 on the loopback address."""

    pdb_bot_logger.info("[+] At the top of the 'open_pdbs' function.")

    pdb1_state = ""
    pdb2_state = ""

    database = cx_Oracle.makedsn(HOST, PORT, service_name=SERVICE_NAME)
    connection = cx_Oracle.connect(user='sys', password=get_in(), dsn=database, mode=cx_Oracle.SYSDBA)

    pdb_bot_logger.info("Database connection established.")
    query = connection.cursor()

    pdb_bot_logger.info("Database cursor obtained.")

    #first check what state the PDBs are in
    rows = query.execute("select name, open_mode from v$pdbs")
    rows_r = list(rows)
    
    pdb_bot_logger.debug("[+] 'rows_r' = %s" % str(rows_r))
    pdb_bot_logger.debug(f"[+] 'rows' = {repr(rows)}")
    
    count = 0
    for row in rows_r:
        pdb_bot_logger.debug(f"Current row: {row} type = {type(row)}")
        if isinstance(row, tuple):
            for element in row:
                if element == "FOOPDB1":
                    count = count + 1
                if element == "FOOPDB2":
                    count = count + 1
                    
        

    assert count == 2,"Something is wrong with your PDBs. FOOPDB1 and FOOPDB2 not found. Shutting down from open_the_pdbs function."
    
    pdb_bot_logger.debug(f"Query returns: {rows_r}")
    for row in rows_r:
        if "FOOPDB1" in row:
            pdb_bot_logger.debug(row)
            pdb1_state = row[1]
            pdb_bot_logger.debug(f"pdb1_state = {pdb1_state}")
    
        if "FOOPDB2" in row:
            pdb_bot_logger.debug(row)
            pdb2_state = row[1]
            pdb_bot_logger.debug(f"pdb2_state = {pdb2_state}")
        
    

    try:
        for pdb in PDBS:
            if pdb == PDBS[0] and pdb1_state != "READ WRITE":
                pdb_bot_logger.debug(f"{PDBS[0]} closed. Opening now. ")
                query.execute(f"alter pluggable database {pdb} open")
            
                
            elif pdb == PDBS[1] and pdb2_state != "READ WRITE":
                pdb_bot_logger.debug(f"{PDBS[1]} closed. Opening now. ")
                query.execute(f"alter pluggable database {pdb} open")
            else:
                pdb_bot_logger.debug(f"{pdb} is already open.")
                
    except cx_Oracle.DatabaseError as de:
        pdb_bot_logger.debug(f"[!] Exception thrown trying to open pdbs -> {de}")
        print(f"[!] Exception thrown trying to open pdbs -> {de}")
        exit()


    pdb_bot_logger.info('[+] open_the_pdbs() function complete.')

def docker_wide_open(container="ORADB12R1_OEL", pdb="FOOPDB1"):
    """ Open the PDBs in a docker container with subprocess. """

    pdb_bot_logger.info("[+] Starting 'docker_wide_open' function now.")
    print(f"[+] Trying to open {pdb} in Docker container {container} now.")

    docker_con2 = subprocess.Popen(f'docker exec -i {container} bash', text=True, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    

    q1 = "sqlplus / as sysdba\n" #without the new-line character at the end this does not work. wow. 0_o
    q2 = f"alter pluggable database {pdb} open;\n"

    docker_con2.stdin.write(q1)
    docker_con2.stdin.write(q2)
    docker_con2.stdin.close()
    
    
    std_lines2 = docker_con2.stdout.readlines()
    sterr_lines2 = docker_con2.stderr.readlines()

    
    if len(std_lines2) > 0:
        print(f"[+] The PDB {pdb} should be open.")
        
    for line in std_lines2:
        print(f"[+] STDOUT - {line}")

    for line in sterr_lines2:
        print(f"[+] STERR - {line}")

    print("[+] 'docker_wide_open' function complete.")

    


def docker_open_pdbs(container="ORADB12R1_OEL"):
    """Make sure the PDBs are in Read/Write mode in the container database."""

    PDB2_RW = False
    PDB1_RW = False
    
    pdb_bot_logger.info("[+] At the top of the 'docker_open_pdbs' function.")

    pdb1_state = ""
    pdb2_state = ""

    
    docker_con = subprocess.Popen(f'docker exec -i {container} bash', text=True, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    

    query1 = "sqlplus / as sysdba\n" #without the new-line character at the end this does not work. wow. 0_o
   
    query2 = "show pdbs"
    
    
    docker_con.stdin.write(query1)
    docker_con.stdin.write(query2)
    docker_con.stdin.close()
    
    print(f"[+] Data type of docker_con.stdout: {type(docker_con.stdout)}")
    std_lines = docker_con.stdout.readlines()
    print(f"[+] 'std_lines' is of data type: {type(std_lines)}")
    print(f"[+] len(std_lines) = {len(std_lines)}")

    sterr_lines = docker_con.stderr.readlines()
    
    
    for line in std_lines:
        print(f"[+] STDOUT = {line}")

    for line in sterr_lines:
        print(f"[+] STDERR = {line}")

    
    count = 0
    for row in std_lines:
        pdb_bot_logger.debug(f"Current row: {row} type = {type(row)}")
        db1_match = re.search(r'FOOPDB1', row)
        if db1_match:
            count = count + 1
            print("Found FOOPDB1")
            print(f"[+] {row}")
            rw_mode = re.search(r"READ WRITE", row)
            if rw_mode:
                PDB1_RW = True
                print("[+] PDB1 is in READ WRITE mode.")

        db2_match = re.search(r"FOOPDB2", row)
        if db2_match:
            count = count + 1
            print("Found FOOPDB2")
            print(f"[+] {row}")
            rw_mode = re.search(r"READ WRITE", row)
            if rw_mode:
                PDB2_RW = True
                print("[+] PDB2 is in READ WRITE mode.")
                    
        

    assert count == 2,"Something is wrong with your PDBs. FOOPDB1 and FOOPDB2 not found. Shutting down from docker_open_pdbs function."
    
    

    try:
        for pdb in PDBS:
            if pdb == PDBS[0] and not PDB1_RW:
                pdb_bot_logger.debug(f"{PDBS[0]} closed. Opening now. ")
                print(f"[-]{PDBS[0]} closed. Opening now. ")
                #query.execute(f"alter pluggable database {pdb} open")
                docker_wide_open(container=container, pdb=pdb)
            
                
            elif pdb == PDBS[1] and not PDB2_RW:
                pdb_bot_logger.debug(f"{PDBS[1]} closed. Opening now. ")
                print(f"[-] {PDBS[1]} closed. Opening now. ")
                #query.execute(f"alter pluggable database {pdb} open")
                docker_wide_open(container=container, pdb=pdb)
                
            else:
                pdb_bot_logger.debug(f"{pdb} is already open.")
                print(f"[+]{pdb} is already open.")
                
    except Exception as e:
        pdb_bot_logger.debug(f"[!] Exception thrown trying to open the docker container pdbs -> {e}")
        print(f"[!] Exception thrown trying to open the docker container pdbs -> {e}")
        exit()


    pdb_bot_logger.info('[+] docker_open_pdbs() function complete.')
    


def docker_remove_pdb(branch: str, slot_number: int, debug=True) -> None:
    """Remove the PDB from the Docker container database. This should be executed in a Cygwin shell since BASH is invoked. This calls Cygwin's version of BASH instead of WSL's. """
   
    os.environ['PDB_FORCE_FETCH_DONE'] = 'N'
    os.environ['PDB_FORCE_REMOVE'] = 'Y'

    print(f"[+] Now removing {branch} from slot {slot_number}")
    pdb_bot_logger.info(f"[+] Now removing {branch} from slot {slot_number}")
    
    docker_output = subprocess.Popen(['C:\\cygwin64\\bin\\bash', '-l', '-c', f'rm_pdb.sh {branch} {slot_number}'], shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     stdin=subprocess.PIPE, encoding="utf-8")
    

    #print(f"[Info] The type of Python object of 'docker_output.stdout' = {type(docker_output.stdout)}")
    #docker_output.stdout is a string. 

    if debug:
        for line in docker_output.stdout:
            sys.stdout.flush()
            print(f"[-] DOCKER STDOUT = {line}")

    for err_lines in docker_output.stderr:   
        sys.stderr.flush()
        print(f"[+] DOCKER STDERROR = {err_lines}")
        if "Completed" in err_lines:
            print(f"[+] PDB {number} is probably removed.")
            
    print(f"[*] Removing PDB for branch {branch} complete.")
       

def remove_the_pdb(number: int) -> None:
    """Remove the PDB programmatically. The function uses typesafety and takes an integer. The slot number is the argument to pass to the function. """

    #print("[+] Current working directory is: %s" % os.getcwd())
    #chdir to the cygwin tools dir
    #print("Changing directories...")
    os.chdir(CYGWIN_PATH + TOOLS_DIR)
    #print("[+] Current working directory is: %s" % os.getcwd())
    #print("Printing the directory contents now.")
    #print(os.listdir('.'))

    
    print("[+] Attempting to remove the pdb now.")
    output = subprocess.run(['bash', '-l', '-c', 'cw_rm_pdb.sh %s foo-db' % str(number), '<', '%s' % os.devnull], shell=True, text=True,
                            capture_output=True)
    if output.stdout:
        print("[+] OK: %s " % output.stdout)
        print("[+] PDB in slot #%d should be removed." % number)
        return
    if output.stderr:
        print("{-] Error: %s " % output.stderr)
        print("[-] PDB probably not removed at slot number %d" % number)


def docker_load_basic_batch(number: int, name: str, debug=False, experiment=False, force_this_hash=None) -> None:
    """Load the PDB into a Docker container database. This requires Cygwin and the 'ld_pdb.sh' script."""

    import eviljenkins
    import variable
    
        
    
    
    
    if number != 1 and not big_bang.DEV_MODE:
        pdb_bot_logger.debug(f"[+] Finding build '{name}' on Jenkins now.")
        pdb_hash = eviljenkins.find_your_build(name, test=True, experimental=experiment) #if test is set to True then builds outside of RC1 and RELEASE will be looked for. Also, "Branches" can be loaded from monorepo which are actually PDBs. :)
        pdb_bot_logger.debug(f"[+] The PDB was apparently found and the hash is: {pdb_hash}")
    
    os.environ['PDB_FORCE_FETCH_DONE'] = 'N'

    if 'PDB_FORCE_HASH' not in os.environ: #this (PDB_FORCE_HASH) maybe set by Amber in the Linux implementation that autoamtes diff-script generation
        print(f"[+] Creating a new environment variable and initializing this variable as follows: PDB_FORCE_HASH = {pdb_hash}")
        os.environ['PDB_FORCE_HASH'] = pdb_hash #if this is not set then set this to the value eviljenkins.find_your_build() found.
        print(f"[+] PDB_FORCE_HASH set to {os.environ['PDB_FORCE_HASH']}")
    elif os.environ['PDB_FORCE_HASH'] == None:
        print(f"[+] PDB_FORCE_HASH is None. Setting this environment variable to: {pdb_hash}")
        os.environ['PDB_FORCE_HASH'] = pdb_hash
        print(f"[+] PDB_FORCE_HASH set to {os.environ['PDB_FORCE_HASH']}")
    elif big_bang.DEV_MODE and number == 1 and ('PDB_FORCE_HASH' not in os.environ or os.environ["PDB_FORCE_HASH"] == None or os.environ['PDB_FORCE_HASH']):
        print("[+] Dev mode engaged. Loading this hash into PDB1: ", big_bang.DEV_MODE)
        os.environ['PDB_FORCE_HASH'] = big_bang.DEV_MODE
    else:
        print(f"[+] Re-initializing PDB_FORCE_HASH to {pdb_hash}")
        os.environ['PDB_FORCE_HASH'] = pdb_hash
        print(f"[+] PDB_FORCE_HASH set to {os.environ['PDB_FORCE_HASH']}")


    #os.environ['PDB_CHECK_HASH'] = pdb_hash

    os.environ['PDB_FORCE_LOAD'] = 'Y'
    os.environ['PDB_FORCE_APEX'] = 'N'

    if debug:
        pdb_bot_logger.debug("In debug mode in the docker_load_basic_batch function.")
        pdb_bot_logger.debug(f"Creating file to write to  in this directory: {variable.DIFF_SCRIPTS}")
        dl_out = open(variable.DIFF_SCRIPTS + 'docker_load.log', 'w') #write the logs here because they are too big to hold in memory

        try:

            docker_load = subprocess.run(['C:\\cygwin64\\bin\\bash', '-l', '-c', f'ld_pdb.sh {name} {number}'],text=True, stdout=dl_out,
                                      stderr=dl_out, timeout=420) #timeout is set for 420 seconds, which is 7 minutes
        except Exception as dle:
            print(f"[!] Hot damn. The process did not return a zero. Something is awry. Please see the following exception: {dle} ")
            print("Is this a tenant build but not specified on the command line? Run the help menu to see this option (-h)")
            pdb_bot_logger.debug("This can happen when the program freezes waiting for user input for a tenant release! python big_bang.py -h for tenant options.")
            raise Exception(f'PDB {name} not loaded. ld_pdb.sh did not return a zero. Meltdown.') 

        print("[+] Please wait, loading the pdb now into the container database.")

        out, err = docker_load.communicate()

        if out:
            sys.stdout.flush()
            print(f"[+] STDOUT 'docker_load_pdb_echo' = {out}")
       

        print("[+] No deadlocks here.")
        print("[+] Now reading file the function produced.")
        with open("docker_load.log", 'r') as dl:
            file = dl.readlines()

        for line in file:
            print(line)
    elif variable.TENANT:
        
        print(f"[+] Please grab some tea, I am loading the pdb, {name}, with the tenant hooha now.")
        pdb_bot_logger.debug(f"[+] Please grab some tea, I am loading the pdb, {name}, with the tenant hooha now.")
        
        try:
            docker_load = subprocess.run(['C:\\cygwin64\\bin\\bash', '-l', '-c', f'ld_pdb.sh {name} {number} {variable.TENANT}'],check=True)
        except Exception as tle:
            print(f"[!] Uh oh. Something went wrong loading the pdb with the tenant. The exception is: {tle}")
            pdb_bot_logger.debug(f"[!] Uh oh. Something went wrong loading the pdb with the tenant. The exception is: {tle}")
            
            raise Exception(f"PDB {name} not loaded the exception thrown was: {tle}")
            
    else:
        raise Exception("Please specify a tenant to load a PDB - pdb_bot.docker_load_basic_batch ")
        #the code below this will not run with the exception raised. Currently, from testing this code is not loading a tenanteless build in the monorepo. 9/14/2021
        import time
        print(f"[+] Please wait, loading the pdb now into the container database. No tenants specified. Start time: {time.asctime()} ")
        pdb_bot_logger.debug(f"[+] Please wait, loading the pdb now into the container database. No tenants specified. Start time: {time.asctime()}")
        import threading
        import awesome
        tp = awesome.TimeProcess() #shows an dynamic runtime counter in the shell
        time_process = threading.Thread(target=tp.runtime)
        
        
        try:
            time_process.start()
            start_time = time.time()
            
            docker_load = subprocess.run(['C:\\cygwin64\\bin\\bash', '-l', '-c', f'ld_pdb.sh {name} {number}'],check=True, text=True, capture_output=True, timeout=420)
            
        except Exception as dle:
            print(f"[!] Hot damn. The process did not return a zero. Something is awry. Please see the following exception: {dle}")
            print("Is this a tenant build but not specified on the command line? Run the help menu to see this option (-h)")
            pdb_bot_logger.debug(f"[!] Hot damn. The process did not return a zero. Something is awry. Please see the following exception: {dle} ")
            pdb_bot_logger.debug("This can happen when the program freezes waiting for user input for a tenant release! python big_bang.py -h for tenant options.")
            
            raise Exception(f'PDB {name} not loaded. ld_pdb.sh did not return a zero. Meltdown.')

        finally:
            tp.terminate() #stop the thread


        print(f"[+] Loading PDB without tenant complete. This took around {round((time.time() - start_time) / 60)} minute(s)  or around {round(time.time() - start_time)} seconds to run.")
        pdb_bot_logger.info(f"[+] Loading PDB without tenant complete. This took around {round((time.time() - start_time) / 60)} minute(s)  or around {round(time.time() - start_time)} seconds to run.")

       
            
        

    print("[+]docker_load_basic_batch complete.")
    
   


def docker_load_pdb(number: int, name: str) -> None:
    """Load the PDB into a Docker container database. This requires Cygwin and the 'ld_pdb.sh' script."""

    docker_load = subprocess.Popen(['bash', '-l', '-c', f'ld_pdb.sh {name} {number}'], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

    docker_load.stdin.write(b"Y")

    out, err = docker_load.communicate(timeout=120)

    #turn the bytes into strings
    import clean_pdbs
    out_string = clean_pdbs.byte_me(out)
    out_string = out_string.split("\n") #try and create lines of text instead of one long line of text
    err_string = clean_pdbs.byte_me(err)
    err_string = err_string.split("\n")

    if out:
        for outs in out_string:
            print(f"[i] STDOUT - DOCKER LOAD PDB - {outs}")
            sys.stdout.flush()
    ##        if "ERROR" in docker_load.stdout:
    ##            print("!" * 80)
    ##            print(f"[-] The PDB, {name} is probably not loaded in the Docker container. Please check.")
    ##            print("!" * 80)
    ##            sys.stdout.flush()
            #if "Completed" in out:
                #print(f"[+] PDB {name} probably loaded in the Docker container database.")

    if err:
        for errs in err_string:
            print(f"[i] STDERR - DOCKER STDERR - From the error stream when loading the PDB {name}. The error is {errs}")
            sys.stderr.flush()
            print("[i] These errors maybe a non-issue")

                                 
    

def load_the_pdb(number: int, name: str) -> None:
    """Load the PDB. Pass the slot number and the PDB name to this function. """

    #print("[+] Current working directory is: %s" % os.getcwd())
    #chdir to the cygwin tools dir
    #print("Changing directories...")
    os.chdir(CYGWIN_PATH + TOOLS_DIR)
    #print("[+] Current working directory is: %s" % os.getcwd())
    #print("Printing the directory contents now.")
    #print(os.listdir('.'))

    print(f"[+] Attempting to load PDB {name} in slot {number} now.")
    load = subprocess.Popen(['bash', '-l', '-c', 'cw_ld_pdb.sh %s %s' % (str(number), name), '<', '%s' % os.devnull], shell=True, text=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for std_line in load.stdout:
        print(f"[i] STDOUT - Good vibrations loading the PDB = {std_line}")
        sys.stdout.flush()
        if "Error" in std_line:
            print("!" * 80)
            print("[-] The PDB is probably not loaded. Please check.")
            print("!" * 80)
            sys.stdout.flush()
            

    for stderr_line in load.stderr:
        print(f"[i] STDERR - Bad vibrations loading the PDB = {stderr_line}")
        sys.stderr.flush()


def rm_19_pdb(pdb="FOOPDB1", branch=None, container=None):
    """Delete a pdb in the container if the rm_pdb.sh script does not.
       If a container is supplied this will use the docker command.
       If a branch is supplied this works in the cloud. This function is obsolete now. The shell scripts are capable of deleting all artifacts.
    """

    if container:
        rm_pdb = subprocess.Popen(['docker', 'exec', '-i', f'{container}', '/bin/bash'], shell=True, text=True, encoding='utf-8', stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

        rm_pdb.stdin.write(f'rm -rf /opt/oracle/oradata/CDB19R3/{pdb}')

        out, err = rm_pdb.communicate()

        if out:
            sys.stdout.flush()
            print(f"[+] STDOUT - RM PDB = {out}")

        if err:
            sys.stderr.flush()
            print(f"[-] STDERR - RM PDB = {err}")

        print("[+] rm_19_pdb complete.")
        return
    elif branch:
        
        rm_ssh_pdb = subprocess.Popen(['ssh', 'dockerhost'], text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    
       
        rm_ssh_pdb.stdin.write(f'ls /opt/oracle/oradata/CDB19R3/{pdb}') #test listing this directory
        

        out, err = rm_ssh_pdb.communicate()

        if out:
            sys.stdout.flush()
            print(f"[+] STDOUT - RM PDB = {out}")

        if err:
            sys.stderr.flush()
            print(f"[-] STDERR - RM PDB = {err}")

        print("[+] rm_19_pdb complete.")


def list_pdbs():
    """ This will list pdbs and return branch and container info on pdb1 and pdb2 """

    import variable
    pdb1 = {}
    pdb2 = {}
    ls_pdbs = subprocess.Popen(['bash', '-l','-c', 'ls_pdb.sh'],shell=True, text=True, encoding="utf-8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = ls_pdbs.communicate()

    out_lines = out.split("\n") #create lines on new-lines instead of one big string
    pdb_bot_logger.debug(f"[+] These are the lines returns from the command: \n {out_lines}")

    #find the branches
    for line in out_lines:
        m1 = None
        m2 = None
        
        if variable.MODE == "foo":
            m1 = re.search(r'foo/foo-db_FOOPDB1', line)
        elif variable.MODE == "RITE":
            m1 = re.search(r'newhorizon/egg-db_EGGS1', line)
        elif variable.MODE == "MONO":
            m1 = re.search(r'monorepo/newhorizon_M4RZPDB1', line)
            
        if m1:
            print(f"[+] {variable.MODE}PDB1 found: %s" % line)
            branch = line.split()
            print(f"[+] 'branch'  = {branch}")
            print(f"[+] len(branch) = {len(branch)}")
            if len(branch) == 3:
                pdb1['branch_1'] = branch[1]
                pdb1['container'] = branch[2]
            elif len(branch) == 2:
                pdb1['branch_1'] = branch[1]
            elif len(branch) == 4: # This is for PDB Tools Version 4.62
                pdb1['branch_1'] = branch[1]
                pdb1['container'] = branch[2]
                container = pdb1['container']
                container = container.replace("(", "").replace(":", "")
                pdb1['container'] = container 
                
        else:
            #print(f"[-] 'm1' was now found. Match not found for PDB1 in {variable.MODE}. 'm1' = {m1}")
            #pdb_bot_logger.debug(f"[-] 'm1' was now found. Match not found for PDB1 in {variable.MODE}. 'm1' = {m1}")
            pass
            
        if variable.MODE == "foo":
            m2 = re.search(r'foo/foo-db_FOOPDB2', line)
        elif variable.MODE == "RITE":
            m2 = re.search(r'newhorizon/EGGS_EGGS2', line)
        elif variable.MODE == "MONO":
            m2 = re.search(r'monorepo/newhorizon_M4RZPDB2', line)
            
        if m2:
            print(f"[+] {variable.MODE}PDB2 found: %s" % line)
            branch2 = line.split()
            print(f"[+] 'branch2' = {branch2}")
            print(f"[+] len(branch2) = {len(branch2)}")
            if len(branch2) == 3:
                pdb2['branch_2'] = branch2[1]
                pdb2['container'] = branch2[2]
            elif len(branch2) == 2:
                pdb2['branch_2'] = branch2[1]
            elif len(branch2) == 4: # this is for PDB Tools Version 4.62
                pdb2['branch_2'] = branch2[1]
                pdb2['container'] = branch2[2]
                container2 = pdb2['container']
                container2 = container2.replace("(", "").replace(":", "")
                pdb2['container'] = container2
                
        else:
            #print(f"[-] 'm2' was now found. Match not found for PDB2 in {variable.MODE}. 'm2' = {m2}")
            #pdb_bot_logger.debug(f"[-] 'm2' was now found. Match not found for PDB2 in {variable.MODE}. 'm2' = {m2}")
            pass
            
        
               
    if out:
        print(f"[+] STDOUT ls_pdbs = {out}")

    if err:
        print(f"[-] STDERR ls_pdbs = {err}")

    return pdb1, pdb2
        
    


if __name__ == "__main__":
    big_decision = input("Remove or Load? (R | L): ")

    if big_decision.upper().startswith("R"):
        num = input("Which PDB to remove? (1 | 2): ")
        print("[+] Calling 'remove_the_pdb' function now.")
        remove_the_pdb(int(num))
        print("[+] Program complete.")

    elif big_decision.upper().startswith("L"):
        num = input("Which slot to load the PDB? ")
        name = input(f"Which PDB to load in slot {num}? ")
        load_the_pdb(int(num), name)
        print("[+] Program complete.")



    
    
    
    
    
    
