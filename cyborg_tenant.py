"""
The module, this very module, will look through the C:\workspace\monorepo\foohorizon\foo-db\install\tenant_config.xml
and find all the tenants. Then this script will call big_bang.py creating a release for each tenant found.

Part of the design goal of this module is to have something start the script and then handle supplying which tenants are needed for a particular release.
Should I pass in the branches for PDB1 and PDB2 to this module? 
"""

import xml.etree.ElementTree as ET
import awesome
import threading
import eviljenkins
import ctypes
import time
import argparse
import logging
import os
import subprocess
import FindOraHome as home


#logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

cyborg_logger = logging.getLogger('cyborg-log')
if not cyborg_logger.handlers:
    cyborg_fh = logging.FileHandler('cyborg-debug.log')
    cyborg_logger.setLevel(logging.DEBUG)
    cyborg_fh.setFormatter(formatter)
    cyborg_logger.addHandler(cyborg_fh) 

def findContainer(branch):
    """This function finds the Docker container currently in use. Pass a branch, most likely pass PDB1 or PDB2."""
    
    docker = None

    try:
        
        out = subprocess.run(['C:\\cygwin64\\bin\\bash', '-lc', f'FindPath.sh {branch}'], #absolute path to bash is for Umesh
        encoding='utf8', capture_output=True)

        #print(f"'out.stdout' = {repr(out.stdout)}")
        lines = out.stdout.split("\n") #split on new-lines
        for line in lines:
            #print(f"[+] line = {line}")
            if line.startswith("The Docker container is:"):
                docker = line.split(":")[1] #get the second element after split creates a list
                #print(f"Found the container = {container}")

    except Exception as de:
        print(f"[+] Exception thrown trying to determine directory structure: {de}")

    print(f"[+] The Docker container = {docker}")
    return docker.strip() #remove trailing and leading white-spaces



def cyborg_run(pdb1, pdb2, tenant="kdot",save=False, experimental=False, fast=False, inter=False):
    """Run a KDot tenant build while finding the schemas programmatically """

    print("[+] Cyborg run starting...")
    
    import variable
    variable.init()
    
    #find which agency this is for.
    if pdb1.startswith('foo-db'):
        variable.MODE = "foo"
    elif pdb1.startswith('fizz-db'):
        variable.MODE = "fizz"
    elif pdb1.startswith('fizzhorizon'):
        #get current directory and see if mono is in it
        current_dir = os.getcwd()
        if 'monorepo' in current_dir:
            variable.MODE = "MONO"

    print(f"[+] Current mode = {variable.MODE}")
            
    variable.toggle_variables(variable.MODE) #toggle the variables
   
    import ScrapedSchemas
    dml, ddl = ScrapedSchemas.WhatToScan(pdb1, pdb2)
   
    if ddl:
        print(f"[+] The following DDL schemas are being compared: {ddl}")
    else:
        print(f"[!] There are not any DDL schemas for this release between {pdb1} and {pdb2}")

    if not dml and not ddl:
        print("[+] There are not any DDL or DML schemas to scan. Program shutting down.")
        exit(1)
        

    import big_bang
    big_bang.DDL_SCHEMAS = list(ddl) #give big_bang.py the DDL schemas to compare
    big_bang.NEW_PARADIGM = True #Docker mode
    big_bang.TENANT = tenant 

    variable.TENANT = tenant

    big_bang.SAVEPOINT = save

    if experimental:
       print(f"[+] Running in experimental mode!")

    big_bang.EXPERIMENT = experimental

    if fast:
        print(f"[+] Running in fast cyborg mode with re-diffs not included.")
        big_bang.FAST = fast


    if not save:
        #run this thread to get the readme.md if this is not a savepoint. 
        print("[*] R2D2 starting...creating folders, release readmes and environment report.")
        import r2d2
        if pdb1.strip() == "fizzhorizon-test":
            r2d2_thread_NBM = threading.Thread(target=r2d2.newBranchingModelFolders, kwargs={"base_dir":variable.RELEASE_DIR, '''tenant''':variable.TENANT})
            r2d2_thread_NBM.name="R2D2 Thread - Cyborg Run - NewBranchingModel"
            r2d2_thread_NBM.start()

        else: #create folders the "standard way"
            r2d2_thread = threading.Thread(target=r2d2.autoFolders, args=(pdb1, pdb2, variable.RELEASE_DIR)) 
            r2d2_thread.name="R2d2 Thread - Cyborg Run - Standard Way"
            r2d2_thread.start()

    docker_container = findContainer(pdb2)

    print(f"[+] pdb1=", pdb1)
    print(f"[+] pdb2=", pdb2)
    print(f"[+] savepoint=", save)
    print(f"[+] docker_mode=", docker_container)

    if big_bang.DDL_SCHEMAS: #normal mode with DDL and DML
        big_bang.big_bang(pdb1=pdb1, pdb2=pdb2, savepoint=save, docker_mode=docker_container, inter=inter)
    else: #DML only mode
        big_bang.DML_ONLY = True
        big_bang.big_bang(pdb1=pdb1, pdb2=pdb2, savepoint=save, docker_mode=docker_container, inter=inter)
        

    print("[+] Cyborg run complete.")
    

def findTenants():
    """Find the tenants and return them to the caller. Initialize the variable module with the repo you want tenant info on (variable.toggle_variables(variable.MODE))"""

    tenants_found = set()
    
    tree = ET.parse(variable.TENANT_LIST)
    root = tree.getroot()
    for tenant in root.findall('properties/tenants'):
        for name in tenant.findall('tenant'):
            print(f"[+] Found this tenant -> {name.text}")
            tenants_found.add(name.text)

    return tenants_found
        
def run_s(pdb1, pdb2, docker_container="Ora19r3", fast=False, ddl_schemas=['NO_OWNER', 'SELF_OWNER'], ddl_only=False, savepoint=False):
    """This function should run builds sequentially. This function calls findTenants() to find which tenants have PL/SQL code to compare."""

    cyborg_logger.info("[+] At the top of the 'run_s' function.")
    import big_bang
    import variable
    import r2d2

    variable.init() #initialize the variables

    #find which agency this is for.
    if pdb1.startswith('foo-db'):
        variable.MODE = "foo"
    elif pdb1.startswith('fizz-db'):
        variable.MODE = "fizz"
    elif pdb2.startswith('fizzhorizon'):
       variable.MODE = "MONO"

    cyborg_logger.debug(f"[+] MODE set to: {variable.MODE}")

    variable.toggle_variables(variable.MODE) #toggle the variables

    cyborg_logger.debug("[+] Variables toggled.")
    
    tenants = findTenants() #find which tenants are in this PDB

    cyborg_logger.debug(f"[+] These are the tenants found: {tenants}")

    for tenant in tenants:
        print(f"[+] cyborg_tenant is about to compare this tenant: {tenant}")
        cyborg_logger.info(f"[+] cyborg_tenant is about to compare this tenant: {tenant}")
        big_bang.NEW_PARADIGM = True #configurationless dynamic DDL mode
        print(f"[+] Configurationless DDL scans enabled: {big_bang.NEW_PARADIGM}")
        cyborg_logger.info(f"[+] Configurationless DDL scans enabled: {big_bang.NEW_PARADIGM}")
        big_bang.TENTANT = tenant #the tenant to use in the load process
        print(f"[+] Loading this tenant: {big_bang.TENTANT}")
        cyborg_logger.info(f"[+] Loading this tenant: {big_bang.TENTANT}")
        variable.TENANT = tenant
        print(f"[+] Global tenant variable set to {variable.TENANT}")
        cyborg_logger.info(f"[+] Global tenant variable set to {variable.TENANT}")
        big_bang.DDL_ONLY = ddl_only
        cyborg_logger.info(f"[+] DDL_ONLY mode = {big_bang.DDL_ONLY}")
        print(f"[+] DDL_ONLY mode = {big_bang.DDL_ONLY}")
        
        big_bang.FAST = fast #no re-diffs for this release - default setting is no re-diffs
        print(f"[+] Fast mode engaged: {big_bang.FAST}")
        cyborg_logger.info(f"[+] Fast mode engaged: {big_bang.FAST}")
        big_bang.DOCKER_ENGAGED = docker_container #the docker container for this run
        print(f"[+] Docker container = {big_bang.DOCKER_ENGAGED}")
        cyborg_logger.info(f"[+] Docker container = {big_bang.DOCKER_ENGAGED}")
        big_bang.DDL_SCHEMAS = ddl_schemas #This list should be populated by sometype of Git report in the future
        print(f"[+] Scanning the following DDL schemas = {big_bang.DDL_SCHEMAS}")
        cyborg_logger.info(f"[+] Scanning the following DDL schemas = {big_bang.DDL_SCHEMAS}")
        if savepoint:
            print(f"[+] This is a savepoint execution: {savepoint} for tenant: {big_bang.TENTANT} because there was an error.")
            cyborg_logger.info(f"[+] This is a savepoint execution: {savepoint} for tenant: {big_bang.TENTANT} because there was an error.")
        #awesome.slowdown()
        print("[+] Starting the process...")
        cyborg_logger.info("[+] Starting the process...")

        print("[*] R2D2 starting...")
        cyborg_logger.info("[*] R2D2 starting...")
        r2d2_thread = threading.Timer(1.0,r2d2.autoFolders, args=(pdb1, pdb2, variable.RELEASE_DIR)) #wait 1 second before calling the autoFolders function
        r2d2_thread.name="R2d2 Thread-CyborgTenant"
        r2d2_thread.start()

        cyborg_logger.info("[+] Calling big_bang.big_bang now")
        big_bang.big_bang(pdb1=pdb1, pdb2=pdb2, docker_mode=docker_container, savepoint=savepoint) #generate the diff scripts

        print("[+] Updating the readme.txt files with the driver script name.")
        cyborg_logger.info("[+] Updating the readme.txt files with the driver script name.")
        try:
            r2d2.updateReadMe() #update the readme files for the upgrade and downgrade folders
        except Exception as readme_exception:
            print("[+] Exception thrown in cyborg_tenant.run_s -> {readme_exception}")
            cyborg_logger.error("[+] Exception thrown in cyborg_tenant.run_s -> {readme_exception}")

        print(f"[+] Process complete for {tenant}.")
        cyborg_logger.info(f"[+] Process complete for {tenant}.")
        if savepoint:
            savepoint = False
            print("[+] Setting the savepoint back to False for the next tenant.")
            cyborg_logger.info("[+] Setting the savepoint back to False for the next tenant.")

        for thread_id, thread in threading._active.items():
            if isinstance(thread, threading.Thread):
                if thread.name == "spinning":
                    ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit)) #this weirdness should kill the thread that continues to spin from awesome.py via big_bang.py
    print("""
       |_   _  ._ _    _|_  _  ._   _. ._ _|_ 
 (_ \/ |_) (_) | (_|    |_ (/_ | | (_| | | |_ 
    /             _|                          

    """)
    cyborg_logger.info("""
       |_   _  ._ _    _|_  _  ._   _. ._ _|_ 
 (_ \/ |_) (_) | (_|    |_ (/_ | | (_| | | |_ 
    /             _|                          

    """)
    print("cyborg tenant complete.")
    cyborg_logger.info("cyborg tenant complete.")

if __name__ == "__main__":
    start = time.time()

    parse = argparse.ArgumentParser(description="""A module to create Redgate diff scripts for multiple tenants sequentially or without human intervention.
                                    """)

    parse.add_argument("--pdb1", action="store", help="Specify PDB1. Example: fizzhorizon-2.0.0-RELEASE",required=True)
    parse.add_argument("--pdb2", action="store", help="Specify PDB2. Example: fizzhorizon-2.0.1-RC1", required=True)
    parse.add_argument("--savepoint", action="store_true", default=False, help="Use this to restart the program after correcting a problem that causes the program to crash.")
    parse.add_argument("--ddl-only", "-o", action="store_true", dest="ddlonly", default=False, help="Use this for diffs that do not have DML differences. Use this for DDL only diffs")
    parse.add_argument("--schema", "-s", action="append", required=False, help="Enter a schema to scan. Use this option for each schema to scan. This method is faster and does not require configuration files.")
    parse.add_argument("--docker", "-d", action="store", help="Please specify the Docker container with the container DB to connect to. Currently supported containers: Oradb19r3Apx20r1, Ora19r3. CTO update needed if container not listed.")
    parse.add_argument("--fast", "-f", action="store_true", default=False, help="Use this to not re-diff. (Fast mode)")
    parse.add_argument("--run", "-r", action="store_true", default=False, help="This starts a single diff script run without human intervention. Specify PDB1, PDB2, tenant, and Docker container. Tenant defaults to 'kdot'. Docker container defaults to 'Ora19r3'.")
    parse.add_argument("--tenant", "-t", action="store", dest="tenant", default=None, help="Specify a tenant to generate diff scripts for.")
    args = parse.parse_args()

    if args.pdb1 and args.pdb2 and not args.run:
         print("""
       |_   _  ._ _    _|_  _  ._   _. ._ _|_ 
 (_ \/ |_) (_) | (_|    |_ (/_ | | (_| | | |_ 
    /             _|                          

        """)
         if args.docker:
             run_s(pdb1=args.pdb1, pdb2=args.pdb2, docker_container=args.docker, fast=args.fast, ddl_schemas=args.schema, ddl_only=args.ddlonly, \
               savepoint=args.savepoint)
         else: #use default docker container
             run_s(pdb1=args.pdb1, pdb2=args.pdb2, fast=args.fast, ddl_schemas=args.schema, ddl_only=args.ddlonly, \
               savepoint=args.savepoint)
             
    elif args.run and args.pdb1 and args.pdb2: #cyborg_run mode
        print("[+] Cyborg run mode starting...")
        if not args.docker and not args.tenant:
            cyborg_run(args.pdb1, args.pdb2)
        elif args.docker:
            cyborg_run(args.pdb1, args.pdb2, docker=args.docker)
        elif args.tenant:
            cyborg_run(args.pdb1, args.pdb2, tenant=args.tenant)
        elif args.tenant and args.docker:
            cyborg_run(args.pdb1, args.pdb2, tenant=args.tenant, docker=args.docker)
            
            
            
        
    else:
        print("[-] I did not understand that. Please type the module name and then -h for a help menu. Thank-you for reading this. Man is obsolete.")

    total = time.time() - start
    print(f"Cyborg ran for {total} seconds or about {total/60} minutes")
    cyborg_logger.info(f"Cyborg ran for {total} seconds or about {total/60} minutes")

    
        
        
