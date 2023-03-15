
# shhhhhuuuuu bang!
#feel free to specify your Python interpreter above these superfilous comments

"""
Author:ksmith
Date:3/18/2020
Note:This is designed to be run on Windows in a Cygwin shell.



"""
import awesome
import LostSchemas
import pdb_bot
import ReDiff
import ConnectToOracle
import RemoveJunkFromScript
import MetaSQL
import ErrorReport
import logging
import clean_pdbs
import CrazyDiamond
import apv
import scan
import LowIonConfig
import r2d2
import variable
import DetectDDLChange
import Direction

#"batteries included" modules
import glob
import threading
import argparse
import time
import os
import pathlib
import re

#logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

big_bang_logger = logging.getLogger('big-bang-log')
if not big_bang_logger.handlers:
    bigbang_fh = logging.FileHandler('big-bang-debug.log')
    big_bang_logger.setLevel(logging.DEBUG)
    bigbang_fh.setFormatter(formatter)
    big_bang_logger.addHandler(bigbang_fh) #add the file handler to the logger


#globals
DUMP_DIR = None
DOCKER_ENGAGED = None
FAST = False
NUMBER_OF_STEPS = 12
START_DIR = None
DDL_ONLY = False
DML_ONLY = False
PDB1 = None
PDB2 = None
TENANT = None
EXPERIMENT = False
SAVEPOINT = False

#globals for new paradigm - no minimum builds or configuration files needed mode. This mode is designed with speed as the goal. 
DDL_SCHEMAS = [] # a list of schemas to scan for the DDL
NEW_PARADIGM = False #if this is true new-paradigm mode is engaged




def build_team_bot(ddl_scripts, dml_scripts, up=True):
    """
    This function will handle deploying the DDL and then the DML and also creating the error report with the deployment log files.
    The location of the scripts should be passed into the ddl and dml parameters.
    """

    big_bang_logger.info("ACHTUNG BABY - At the top of the 'build_team_bot' function.")
    big_bang_logger.info("~" * 30)
    big_bang_logger.info(f"[+] The build team bot obtained the following things 'ddl_scripts' - type: {type(ddl_scripts)} value: {ddl_scripts}")
    big_bang_logger.info(f"[+] The build team bot obtained the following things 'dml_scipts' - type: {type(dml_scripts)} value: {dml_scripts}")
    big_bang_logger.info("~" * 30)

    up_ddl_log = None
    up_dml_log = None

    down_ddl_log = None
    down_dml_log = None
    
    if up and dml_scripts:
        big_bang_logger.debug("[+] Build team bot is deploying *upgrade* DML code now.")
        up_dml_log = deploy(dml_scripts, ddl_release=False)
        big_bang_logger.debug("[+] Done deploying the upgrade DML code now.")
    elif up and ddl_scripts:
        big_bang_logger.debug("[+] Build team bot is deploying *upgrade* DDL code now.")
        up_ddl_log = deploy(ddl_scripts)
        big_bang_logger.debug("[+] Done deploying the upgrade DDL code now.")
    elif not up and dml_scripts:
        big_bang_logger.debug("[+] Build team bot is deploying *downgrade* DML code now.")
        down_dml_log = deploy(dml_scripts, up=False, ddl_release=False)
        big_bang_logger.debug("[+] Build team bot is done deploying downgrade DML code now.")
    elif not up and ddl_scripts:
        big_bang_logger.debug("[+] Build team bot is deploying *downgrade* DDL code now.")
        down_ddl_log = deploy(ddl_scripts, up=False) #deploy() returns the deployment log
        big_bang_logger.debug("[+] Build team bot is done deploying downgrade DDL code now.")
    else:
        big_bang_logger.debug("[?] Not sure why the build-team bot is in this state. 0_o")
       
        

    
    if up_ddl_log:
        big_bang_logger.debug("[+] Creating error report for upgrade DDL deployment.")
        os.chdir(ddl_scripts)
        human_error(up_ddl_log)
    if up_dml_log:
        big_bang_logger.debug("[+] Creating error report for upgrade DML deployment.")
        os.chdir(dml_scripts)
        human_error(up_dml_log)
    if down_ddl_log:
        big_bang_logger.debug("[+] Creating error report for downgrade DDL deployment.")
        os.chdir(ddl_scripts)
        human_error(down_ddl_log)
    if down_dml_log:
        big_bang_logger.debug("[+] Creating error report for downgrade DML deployment.")
        os.chdir(dml_scripts)
        human_error(down_dml_log)

def inner_folder(up=True):
    """Read the file on disk created by the r2d2 thread at the start of the script. If up is True then the upgrade path is returned. If up is not True then the downgrade is returned to the caller. """
    

    import variable
    #get the release folder name for an upgrade or a downgrade
    rf = pathlib.Path(variable.DIFF_SCRIPTS + os.sep + 'release_folders.txt')
    if rf.exists():
        big_bang_logger.debug(f"The release_folders.txt file exists here: {variable.DIFF_SCRIPTS + os.sep + 'release_folders.txt'}")
    else:
        raise Exception("Missing 'release_folders.txt' exception")
    
    with open(variable.DIFF_SCRIPTS + os.sep + 'release_folders.txt') as trf:
        lines = trf.readlines()

    if len(lines) == 2:
        if up: #upgrade
            target_inner_folder = lines[0]
        else:
            target_inner_folder = lines[1]
            
        #remove any trailing new-line (linefeed) characters that could cause bugs, errors, timesinks

        a_re = re.compile(r'[\n]')
        target_inner_folder = a_re.sub("", target_inner_folder) #replace new-line with an empty string - remove the linefeed
        big_bang_logger.debug(f"[+] The 'target_inner_folder' is: {target_inner_folder}")
    else:
        print(f"[!] Something unexpected is happening with the {variable.DIFF_SCRIPTS + os.sep + release_folders.txt} file. There are not exactly 2 lines. :/")
        big_bang_logger.debug("[!] Something unexpected is happening with the release_folders.txt file. There are not exactly 2 lines. :/")
        
        

    return target_inner_folder
    
    

def dml(up=True, inter=False):
    """This function handles creating the DML with Redgate. """

    if DUMP_DIR:
        if inter:
            print(f"[+] The DUMP_DIR variable is set and equals: {DUMP_DIR}")
        big_bang_logger.debug(f"[+] The DUMP_DIR variable is set and equals: {DUMP_DIR}")
    else:
        step2()
        print(f"[+] Creating the DUMP_DIR variable. DUMP_DIR = {DUMP_DIR}. This maybe a savepoint execution.")
        if SAVEPOINT:
            print("[+] This is a savepoint execution.")
            
        big_bang_logger.debug("[+] Creating the DUMP_DIR variable. This maybe a savepoint execution.")

    #1.) Call Duane's code that generates the DCO
    import LowIonConfig as Low
    import shutil

    #3.) Create the file names
    #create the file name based on up/down
    if inter:
        print("determining file name...")

    big_bang_logger.debug("determining file name...")
    if up:
        d_dump = 'upgrade_bigbang_dml'
    elif not up:
        d_dump = 'downgrade_bigbang_dml'

    target_inner_folder = inner_folder(up=up) #this function returns the absolute path to "Upgrade from..." folder if up is True and the "Downgrade to..." folder if up is False

    #create the folder, the d_dump folder :)
    if not os.path.exists(target_inner_folder + os.sep + d_dump):
        print(f"[+] Creating this directory: {target_inner_folder + os.sep + d_dump}")
        big_bang_logger.debug(f"[+] Creating this directory: {target_inner_folder + os.sep + d_dump}")
        os.mkdir(target_inner_folder + os.sep + d_dump)

 

    #info on the file name chosen and other variables - too much info (TMI)
    if inter:
        print("This file name chosen is: %s " % d_dump)
        print("")
        print("generating the diff scripts with the following arguments to 'generateDiffScripts':")
        print("target_inner_folder = %s" % target_inner_folder)
        print("diff_dump = %s" % d_dump)
        print("dco_dir = %s" % variable.DOCKER_DCO)
    
        awesome.slowdown()

    big_bang_logger.debug("This file name chosen is: %s " % d_dump)
    big_bang_logger.debug("")
    big_bang_logger.debug("generating the diff scripts with the following arguments to 'generateDiffScripts':")
    big_bang_logger.debug("target_inner_folder = %s" % target_inner_folder)
    big_bang_logger.debug("diff_dump = %s" % d_dump)
    big_bang_logger.debug("dco_dir = %s" % variable.DOCKER_DCO)

    exists = False
    if SAVEPOINT:
        #check to see if any of the DCO files have already been created
        if up:
            #check for Upgrade_All.dco
            file = glob.glob(target_inner_folder + os.sep + d_dump + os.sep + "Upgrade_All.dco")
            if file:
                print(f"[+] This is a savepoint. The {file} already exists. No need to re-create it.")
                exists = True
        else:
            #check for Downgrade_All.dco
            file = glob.glob(target_inner_folder + os.sep + d_dump + os.sep + "Downgrade_All.dco")
            if file:
                print(f"[+] This is a savepoint. The {file} already exists. No need to re-create it.")
                exists = True

    if not exists: #The DCO does not yet exist
        if variable.TENANT:
            Low.dynamic_dco(upgrade=up, install_type=variable.TENANT) #add the tenant here somehow to the other install types.

        else:
           Low.dynamic_dco(upgrade=up) #this will create the filename and generate the DCO/XML configuration file
    
    if up:
        dco_file_name = "Upgrade_All.dco"
    else:
        dco_file_name = "Downgrade_All.dco"

    print(f"[+] Copying {dco_file_name} from {variable.DOCKER_DCO + os.sep + dco_file_name} to {target_inner_folder + os.sep + d_dump}.")
    if not os.path.exists(target_inner_folder + os.sep + d_dump):
        print(f"[+] The folder/path {target_inner_folder + os.sep + d_dump} does not exist. Hard to copy a file to a destination that does not exist.")
        big_bang_logg.debug(f"[+] The folder/path {target_inner_folder + os.sep + d_dump} does not exist. Hard to copy a file to a destination that does not exist.")
    shutil.copy(variable.DOCKER_DCO + os.sep + dco_file_name, target_inner_folder + os.sep + d_dump) #copy the file to the upgrade_bigbang_dml folder or downgrade_bigbang_dml folder from the DOCKER_DCO dir
    print("[+] Copy file complete.")
    
    #4. Remove persistent circular_check_vw showstopper
    if variable.MODE == "MONO":
        pass #these showstoppers do not exist in the monorepo! 
    else:
        print("[+] Removing persistent DML show stoppers in both PDBS.")
        big_bang_logger.debug("[+] Removing persistent DML show stoppers in both PDBS.")
        ConnectToOracle.fix_persistent_show_stopper(docker_mode=DOCKER_ENGAGED)

    #4.5 Add the ap_versions DCO file to the files to compare - this is the file outside of the normal DCO process
    LowIonConfig.update_apv(apv_dco_file=variable.DOCKER_DCO + os.sep + "AP_VERSIONS.dco" ,drop_zone=target_inner_folder + os.sep + d_dump)

    #4.6) Change the 'networkAlias' or tnsnames thing so Redgate can connect to the container database
    print("[+] Changing the networkAlias elements in the DCO configuration files.")
    big_bang_logger.debug("[+] Changing the networkAlias elements in the DCO configuration files.")
    junk = [LowIonConfig.toggle_network(file, docker_name=DOCKER_ENGAGED) for file in glob.glob(target_inner_folder + os.sep + d_dump + os.sep + '*.dco')] #get the '.dco' files in the inner inner DML folders
    big_bang_logger.debug("[+] networkAlias change complete.")

    #4.7 make the AP_VERSIONS an upgrade or a downgrade
    if up:
        print("[+] Making AP_VERSIONS.dco an upgrade.")
        Direction.goUP(target_inner_folder + os.sep + d_dump + os.sep + "AP_VERSIONS_.dco") #LowIonConfig.update_apv() will add a "_.dco" to the file name
    else:
        print("[+] Making AP_VERSIONS.dco a downgrade.")
        Direction.goDown(target_inner_folder + os.sep + d_dump + os.sep + "AP_VERSIONS_.dco")
  

    #5.) Disable/Enable Circular Contraints on the database
    #disable the constraints in the database to create the diff scripts for DML
    if inter:
        print("First we need to disable circular constraints.")
        awesome.slowdown()
        
    print("Disabling circular foreign key constraints now!")
    big_bang_logger.debug("Removing circular foreign key constraints now!")
    ConnectToOracle.toggle_circular_constraints(enable=False, docker_mode=DOCKER_ENGAGED)
    print("Circular foreign key constraints removed.")
    big_bang_logger.debug("Circular foreign key constraints removed.")

    
    
    if inter:
        print("Calling the CrazyDiamond.generateDiffScripts() to generate the DML diff scripts")


    
    big_bang_logger.debug("[+] Generating DML scripts now.")
    if up:
        config_files = CrazyDiamond.generateDiffScripts(target_inner_folder + os.sep + d_dump, diff_dump=target_inner_folder + os.sep + d_dump, schema_compare=False)
    else:
        config_files = CrazyDiamond.generateDiffScripts(target_inner_folder + os.sep + d_dump, diff_dump=target_inner_folder + os.sep + d_dump, schema_compare=False)
        

    print(f"[+] {config_files} found. This should be the number of diff scripts also.")
    
    #Re-enable the constraints in the database after creating the diff scripts for DML
    
    if inter:
        print("We need to re-enable the circular constraints now.")
        awesome.slowdown()
    big_bang_logger.debug("Turning circular foreign key constraints back on.")
    print("Turning circular foreign key constraints back on.")            
    ConnectToOracle.toggle_circular_constraints(enable=True, docker_mode=DOCKER_ENGAGED)
    print("Circular foreign key constraints back on.")
    big_bang_logger.debug("Circular foreign key constraints back on.")
        
   
    #update the ap_versions table 
    p = pathlib.Path(target_inner_folder + os.sep + d_dump + os.sep + "AP_VERSIONS__diff_script.sql")
    if p.exists():
        if up:
            vert = "UPGRADE"
        else:
            vert = "DOWNGRADE"

        big_bang_logger.info(f"[+] updating 'devdba.ap_versions' table programmatically for a {vert}.")

        if inter:
            print("[+] Updating the 'ap_versions' table rows and deleting 'ap_versions' delete statements now in DEVDBA DML sync/diff scripts.")
            awesome.slowdown()

        big_bang_logger.debug("[+] Updating the 'ap_versions' table rows and deleting 'ap_versions' delete statements now in DEVDBA DML sync/diff scripts.")
                                     
        apv.rc_apv(target_inner_folder + os.sep + d_dump + os.sep + "AP_VERSIONS__diff_script.sql", vert)
        big_bang_logger.debug("Found the AP_VERSIONS__diff_script.sql file and attempted to update the 'ap_versions' table and delete rows.")
    
        if inter:
            print("[+] Updating 'ap_versions' in AP_VERSIONS sync/diff DML scripts complete.")
            awesome.slowdown()
        big_bang_logger.debug("[+] Updating 'ap_versions' in AP_VERSIONS sync/diff DML scripts complete.")
    else:
        big_bang_logger.debug("[-] The AP_VERSIONS diff script does not exist here: %s " % target_inner_folder + os.sep + d_dump + os.sep + "AP_VERSIONS__diff_script.sql")
        big_bang_logger.info("Maybe AP_VERSIONS was not included in the diff?")

    if config_files > 0:
        #5.) Clean the scripts
        big_bang_logger.debug("[+] Cleaning scripts now.")
        warm_shower(target_inner_folder + os.sep + d_dump) 

        #.6) Remove the COMMIT statements from DML
        big_bang_logger.debug("[+] Removing commit statements from DML now.")
        RemoveJunkFromScript.rmCommit(target_inner_folder + os.sep + d_dump) 

        print("[+] DML scripts created.")
        big_bang_logger.debug("[+] DML scripts created.")
        
        return target_inner_folder + os.sep + d_dump #give the location where the deployment scripts are
   
    else:
        print("0 configuration files were found. Nothing to clean. DML scripts not generated. :/")

    print("[+] DML function complete.")
    big_bang_logger.info("[+] DML function complete.")
    
def ddl(up=True, inter=False):
    """This function handles creating the DDL with Redgate."""

    big_bang_logger.debug("At the top of the 'ddl' function.")
    if up:
        big_bang_logger.debug("This is a DDL upgrade.")
    else:
        big_bang_logger.debug("This is a DDL downgrade.")
        
    big_bang_logger.debug(f"SCHEMA_LIST = {variable.SCHEMA_LIST}")
    big_bang_logger.debug(f"OCP_DIR = {variable.OCP_DIR}")
    big_bang_logger.debug(f"NEW_PARADIGM MODE = {NEW_PARADIGM}")
    big_bang_logger.debug(f"DOCKER_ENGAGED = {DOCKER_ENGAGED}")

    if not DUMP_DIR:
        big_bang_logger.debug(f"Creating the DUMP_DIR now in ddl()")
        step2() #create the DUMP_DIR. The program can get to this from a savepoint.

    if not NEW_PARADIGM:
        
        big_bang_logger.debug(f"DUMP_DIR = {DUMP_DIR}")

        files = None #This is used to hold the OCP files found by glob

        #1.) Check for missing schemas
        
        #start checking if all schema OCP configuration files are present
            
        #see if there is a missing configuration file the end-user should know about
        lost = LostSchemas.LostSchemas()
        schemas = lost.readSchemaCSV(pathToCSV=variable.SCHEMA_LIST) #this returns the schemas in 'core' that have the 'X'. The ones we want.
        schemas = set(schemas) #only get unique values - sets run faster than lists also :)
     
        
        if len(schemas) > 0:
            big_bang_logger.debug("[+] Found the following schemas in the csv: %s" % schemas)
            if inter:
                 print("[+] Found the following schemas in the csv file: %s" % schemas)
        else:
            big_bang_logger.debug("[-] The schemas list is empty. You may want to look at the SCHEMA_LIST.csv file passed into the program or hardcoded somewhere.")
            if inter:
                print("[-] The schemas list is empty. You may want to look at the SCHEMA_LIST.csv file passed into the program or hardcoded somewhere.")


        
        #Find the OCPs, the "diff_script_files".
        files = glob.glob(variable.OCP_DIR + os.sep + '*.ocp') 
        
        #get the file names
        file_names = set()
        for f in files:
            file_names.add(f.split(os.sep)[-1]) #just get the last element after splitting on the OS path seperator. This should be the filename. :)

        if inter:
            print("[+] Found the following OCP files in the OCP_DIR: %s" % file_names)
        big_bang_logger.debug("[+] Found the following OCP files in the OCP_DIR: %s" % file_names)
        
        #this bit of code actually compares what is found in the SCHEMA_LIST.csv and what is in the config folder
        missing_schemas = set()
        for s in schemas: #'schemas' holds the schema names found in the SCHEMA_LIST.csv, the schemas with the 'X'
            schema_config = s + '.ocp'
            if schema_config not in file_names:
                missing_schemas.add(schema_config)

        if len(missing_schemas) > 0:   
            big_bang_logger.error("[!] MISSING OCP(s): %s" % missing_schemas)
                
            if inter:
                print("[+] These are all the schemas missing: %s" % missing_schemas)

        #2.) Create configuration files for upgrade or downgrade
        if up:
            awesome.getUp(variable.OCP_DIR)
            if inter:
                print("The getUp(ocp_dir) function was called for DDL.")
            big_bang_logger.debug("The getUp(ocp_dir) function was called for DDL.")
        
        else:
            awesome.getDown(variable.OCP_DIR)
            if inter:
                print("The getDown(ocp_dir) function was called for DDL.")
            big_bang_logger.debug("The getDown(ocp_dir) function was called for DDL.")
            

    if up:
        d_dump = 'upgrade_bigbang_ddl'
    else:
        d_dump = 'downgrade_bigbang_ddl'
        
    big_bang_logger.debug("Creating the inner folders")
    #call new function here to get the folder to write to, the inner release folder - this changes on upgrade or downgrade
    target_inner_folder = inner_folder(up=up)
 
    
        

    #Create the deployment scripts
    if NEW_PARADIGM:
        #loop through the list of schemas from the command line and generate the diff scripts. :)
        big_bang_logger.debug("[+] Now starting the 'ddl_scan' in new paradigm mode.")
        for schema in DDL_SCHEMAS:
            scan.ddl_scan(schema_name=schema,diff_dir=variable.IGR_DIR, dump_dir=target_inner_folder + os.sep + d_dump,
                         direction=up, rediff=False, docker_mode=DOCKER_ENGAGED)
        
        big_bang_logger.debug("[+] DDL Scan complete in new paradigm mode.")
        

    else:
        big_bang_logger.debug("[+] DDL script generation in CrazyDiamond.")
        CrazyDiamond.generateDiffScripts(variable.OCP_DIR, diff_dump=DUMP_DIR + os.sep + d_dump, schema_compare=True, filters=False)  

    #Clean the up ddl scripts
    big_bang_logger.debug(f"[+] Calling 'warm_shower' now. Cleaning: {target_inner_folder + os.sep + d_dump}")
    warm_shower(target_inner_folder + os.sep + d_dump) 

    #removing weirdo objects
    big_bang_logger.debug(f"[+] Removing any 'weirdo objects' from big_bang mode now! Removing from: {target_inner_folder + os.sep + d_dump}")
    RemoveJunkFromScript.rmWeirdo(target_inner_folder + os.sep + d_dump)

    #Remove alter compile statements
    big_bang_logger.debug(f"[+] Calling 'take_out_trash' now. Removing garbage from this directory: {target_inner_folder + os.sep + d_dump}")
    take_out_trash(target_inner_folder + os.sep + d_dump)

   
    

    if not NEW_PARADIGM:
        big_bang_logger.debug("[+] Removing consts$ package now.")
        #Remove the consts$ package
        #find out if rite_common is present then remove the consts$ package if so
        find_rc_ddl = pathlib.Path(DUMP_DIR + os.sep + d_dump)
        rc_file = find_rc_ddl.glob("RITE_COMMON_diff_script.sqlClean.sql")
        rc_file = list(rc_file)
        if rc_file: #this should fire only if rc_file has more than zero elements. 
            #make sure the consts$ package is not included in final diff scripts
            big_bang_logger.debug("Preparing to remove consts$ package. The length of list 'rc_file' is %d " % len(rc_file))
            big_bang_logger.debug("This is what is in the 'rc_file': %s " % rc_file)
            RemoveJunkFromScript.rmConsts(rc_file[0]) #just pass the first, and hopefully only, element which should be the path and file of RC


    big_bang_logger.debug("[+] DDL function complete.")
   
    return target_inner_folder + os.sep + d_dump #return location of deployment scripts
        
def warm_shower(deployment_script_location, rediff=False,inter=False):
    """Pass in the path to this function and the function will clean the scripts found."""
    #Sanitize the diff scripts
    big_bang_logger.info("[+] At the top of the warm_shower function.")
    
    #I maybe able to uncomment this and not pass in the path...
    #path_ = DUMP_DIR + os.sep + d_dump
    
    path_ = deployment_script_location
    
    if inter:
        print("The function to remove the junk from the scripts should be called at this point.")
        awesome.slowdown()
    big_bang_logger.debug("The function to remove the junk from the scripts should be called at this point.")
    
    if inter:
        print('''The "removeWrapper('%s')" function will need to be called.''' % path_)
    big_bang_logger.debug('''The "removeWrapper('%s')" function will need to be called.''' % path_)
    awesome.removeWrapper(path_, rediff=rediff)
    

    if inter:
        print("'removeWrapper()' function complete.")
        awesome.slowdown()
    big_bang_logger.debug("'removeWrapper()' function complete.")

   

    #need to add code to remove the previous scripts that are not cleaned...
    if inter:
        awesome.deleteDirtyFiles(path_, inter=True) #call the function in interactive mode to step through each file deletion
    else:
        big_bang_logger.debug(f"[-] Calling awesome.deleteDirtFiles(path_) - path_ = {path_}")
        awesome.deleteDirtyFiles(path_)
    big_bang_logger.info("[+] warm_shower function complete.")



def take_out_trash(path_to_deployment_scripts):
    """Remove ALTER COMPILE statements from the code. This function is only for DDL scans. This function does change files on disk without asking. Yikes."""
    #remove the ALTER  COMPILE statements. This function does not alter the file names

    big_bang_logger.debug("[+] At the top of the 'take_out_trash' function.")
    
    big_bang_logger.debug("Attemping to remove ALTER COMPILE statements from diff scripts.")
    RemoveJunkFromScript.rmCompile(path_to_deployment_scripts)
    big_bang_logger.debug("rmCompile() call to remove ALTER COMPILE statements complete.")
    #big_bang_logger.debug("Attempting to remove REVOKE statements from schema diff scripts.")
    #RemoveJunkFromScript.rmRevoke(DUMP_DIR + os.sep + d_dump)
    #big_bang_logger.debug("rmRevoke() call to remove REVOKE statements complete.")

    if not NEW_PARADIGM:
        big_bang_logger.debug("Checking if RiteCommon is in the release.")
        #find out if rite_common is present then remove the consts$ package if so
        find_rc_ddl = pathlib.Path(path_to_deployment_scripts)
        rc_file = find_rc_ddl.glob("RITE_COMMON_diff_script.sqlClean.sql")
        rc_file = list(rc_file)
        if rc_file: #this should fire only if rc_file has more than zero elements.
            big_bang_logger.debug("Found the RITE_COMMON_diff_script.sqlClean.sql file.")
            #make sure the consts$ package is not included in final diff scripts
            RemoveJunkFromScript.rmConsts(rc_file[0]) #just pass the first, and hopefully only, element which should be the path and file of RC
            big_bang_logger.debug("Function to remove consts$ package complete.")

    big_bang_logger.debug("[+] 'take_out_trash' function complete.")

    
def deploy(path_, up=True, inter=False, ddl_release=True):
    """Deploy the code to the database. The path_ parameter needs to be the directory with the code to deploy. The up parameter determines if
       the deployment is an upgrade or not. 
    """
     #Create the deployment script

     #::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
     #I need to switch dirs to the location of the deployment scripts as hhlg and connectForA* write to disk - TODO
     #Is this as simple as os.chdir(path_) ???? (Answer: Yes)
     #::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    os.chdir(path_)
    big_bang_logger.debug(f"At the top of the deploy function after the dir change. The dir is now: {os.getcwd()}")
    

    print(f"[+] The path_ passed in is {path_}")
    
    if inter:
        print("Now the deployment script should be created.")
        
        print("This is the function call MetaSQL.heyHoLetsGo(%s)" % path_)
        awesome.slowdown()

    big_bang_logger.debug("Now the deployment script should be created.")
    big_bang_logger.debug("This is the function call MetaSQL.heyHoLetsGo(%s)" % path_)
        
    deployment_script = MetaSQL.heyHoLetsGo(path_)
    
    #deploy the deployment_script
    if inter:
        print("Deploying the code to the database.")
        awesome.slowdown()

    big_bang_logger.debug("Deploying the code to the database.")
    print("[+] Deploying the code to the database.")

    #Actually deploy the code and keep a log with 'deployment_log' which is passed to the error_report function in 'human_error()'
    
    deployment_log = '' #need this variable for the return value of 'connectFor...' functions below
    if up: #upgrade
        if DOCKER_ENGAGED: #docker mode with a docker container database
            #the scripts need to be copied to the container first and then deployed
            #print("[+] Docker mode engaged! Transporting SQL to Docker container now sir.")
            #MetaSQL.docker_transport(directory_to_scripts=path_, container_d=DOCKER_ENGAGED)
            print("[+] Deploying to the Docker container database now.")
            deployment_log, stdout, sterr = ConnectToOracle.docker_deploy(script=deployment_script, container_d=DOCKER_ENGAGED, \
                                                                          up=up, ddl_release=ddl_release)

            #put the deployment log from the container into the folder on the host
            #ConnectToOracle.docker_copy_host(destination=path_, source=f"/home/oracle/{deployment_log}", container_d=DOCKER_ENGAGED)
            print("[+] Docker deployment complete.")
            
        else: #normal mode with a host database
            deployment_log = ConnectToOracle.connectForAUpgrade(deployment_script)
    else: #downgrade
        if DOCKER_ENGAGED: #docker mode with a docker container database
            #the scripts need to be copied to the container first and then deployed
            #print("[+] Docker mode engaged! Transporting SQL to Docker container now sir.")
            #MetaSQL.docker_transport(directory_to_scripts=path_, container_d=DOCKER_ENGAGED)
            print("[+] Deploying to the Docker container database now.")
            deployment_log, stdout, sterr = ConnectToOracle.docker_deploy(script=deployment_script, container_d=DOCKER_ENGAGED, up=up, ddl_release=ddl_release)

            #put the deployment log from the Docker container into the folder
            #ConnectToOracle.docker_copy_host(destination=path_, source=f"/home/oracle/{deployment_log}", container_d=DOCKER_ENGAGED)
            print("[+] Docker deployment complete.")
            
        else: #normal mode with a host database
            deployment_log = ConnectToOracle.connectForADowngrade(deployment_script)

    print("[+] Deployment complete.")

    return deployment_log

def human_error(deployment_log, inter=False):
    """Find out how many errors there are in the deployment log and create a pretty bar chart. Write a small text file with the errors too. As of the present time
       the bar chart is not accurate when executing 'big_bang'. 
    """
    if inter:
        print("Generating error report.")
        awesome.slowdown()

    
    big_bang_logger.debug("Generating error report. At the start of the 'human_error' function.")

    #create the error report
    errors = ErrorReport.error_report(deployment_log) #in docker mode the script blows up here. I need to copy the file back to the host OS.

    big_bang_logger.debug("[+] Error report created from ErrorReport.error_report(deployment_log).")
    
    if inter:
        print("Error report created.")
        awesome.slowdown()

    big_bang_logger.debug("Error report created.")
    big_bang_logger.debug("[!] Number of ORAs: %d" % errors[0])
    print(f"[!] Number of ORAs: {errors[0]}")
    big_bang_logger.debug("[!] Total errors: %d" % errors[-1])
##  big_bang_logger.debug("Writing 'deployment_error_metrics.txt' to disk for code review.")


##    with open("deployment_error_metrics.txt", 'w') as f:
##        f.write("*" * 60)
##        f.write("\n")
##        f.write("DATABASE DEPLOYMENT ERRORS\n")
##        f.write("*" * 60)
##        f.write("\n")
##
##        f.write("[+] Number of ORA errors: %d\n" % errors[0])
##        f.write("[+] Number of SQL errors: %d\n" % errors[1])
##        f.write("[+] Number of SP2 errors: %d\n" % errors[2])
##        f.write("[+] Number of PL2 errors: %d\n" % errors[3])
##        f.write("[+] Number of TNS errors: %d\n" % errors[4])
##        f.write("[+] TOTAL ERRORS: %d\n" % errors[-1])
##        f.write("")
##        f.write("Error report complete - %s\n" % str(time.asctime()))
##        
    big_bang_logger.info("'human_error' function complete.")

    return errors


def rediff(up=True, inter=False):
    """Diff the databases again and see if they are synchronized."""

    print("""
        eeeee  eeee      eeeee e  eeee eeee 
        8   8  8         8   8 8  8    8    
        8eee8e 8eee eeee 8e  8 8e 8eee 8eee 
        88   8 88        88  8 88 88   88   
        88   8 88ee      88ee8 88 88   88


    """)

    big_bang_logger.debug("""

        eeeee  eeee      eeeee e  eeee eeee 
        8   8  8         8   8 8  8    8    
        8eee8e 8eee eeee 8e  8 8e 8eee 8eee 
        88   8 88        88  8 88 88   88   
        88   8 88ee      88ee8 88 88   88



    """)

    clean_set = set()
    
    if inter:
        print("[+] Re-Diffing...")

    if not DUMP_DIR:
        step2() #make sure this global variable is set if called from a savepoint or on its own

    direction = None
    if up:
        direction = "upgrade"
    else:
        direction = "downgrade"
        
    big_bang_logger.debug(f"[+] Re-Diffing...{direction}")
    big_bang_logger.debug(f"[+] The current directory is: {os.getcwd()}")

    
    #find the "inner folder" this could be in a tenant folder or not
    inner = inner_folder(up=up)
    big_bang_logger.debug(f"[+] The 'inner' folder location in the rediff() function is: {inner}")
    
    #generate deployment scripts again
    if up:

        
        
        if NEW_PARADIGM:
            big_bang_logger.debug("[+] RE-DIFF DDL script generation. Upgrade. New Paradigm mode.")
            for schema in DDL_SCHEMAS:
                scan.ddl_scan(schema_name=schema, diff_dir=variable.IGR_DIR, dump_dir=inner + os.sep + "upgrade_bigbang_ddl",
                              direction=up, rediff=True, docker_mode=DOCKER_ENGAGED)
            
        else:
            #rediff_up_ddl =  ddl(ddl_scripts, diff_again=True, inter=inter)
            big_bang_logger.debug("[+] RE-DIFF DDL script generation. Upgrade.")
            CrazyDiamond.generateDiffScripts(OCP_DIR, diff_dump=inner + os.sep + "upgrade_bigbang_ddl",
                                             schema_compare=True, filters=False, re_diff=True)

        

        if NEW_PARADIGM:
            if variable.MODE != "MONO":
                big_bang_logger.debug("Removing persistent show stopper for re-diff. This is probably already removed during the initial diff.")
                ConnectToOracle.fix_persistent_show_stopper(docker_mode=DOCKER_ENGAGED)
                
            big_bang_logger.debug("Removing circular constraints now - [Docker Mode].")
            ConnectToOracle.toggle_circular_constraints(enable=False, docker_mode=DOCKER_ENGAGED)
            print("Circular foreign key constraints removed.")
            big_bang_logger.debug("Circular foreign key constraints removed.")
        else:
            big_bang_logger.debug("Removing circular constraints now.")
            ConnectToOracle.toggle_circular_constraints(enable=False)
            print("Circular foreign key constraints removed.")
            big_bang_logger.debug("Circular foreign key constraints removed.")

        
        big_bang_logger.debug("[+] RE-DIFFing DML now. Upgrade.")
        CrazyDiamond.generateDiffScripts(os.path.join(inner, "upgrade_bigbang_dml"), diff_dump=inner + os.sep + "upgrade_bigbang_dml", schema_compare=False, re_diff=True)

        #adding cyclic constraints after re-diffing the DML.
        if NEW_PARADIGM:
            #adding cyclic constraints after re-diffing the DML.
            print("Enabling circular foreign key constraints now for the re-diff in DOCKER MODE!")
            big_bang_logger.debug("Enabling circular foreign key constraints now in DOCKER MODE!")
            ConnectToOracle.toggle_circular_constraints(enable=True, docker_mode=DOCKER_ENGAGED)
            print("Circular foreign key constraints enabled in DOCKER MODE!")
            big_bang_logger.debug("Circular foreign key constraints enabled in DOCKER MODE!")

        else:
            #adding cyclic constraints after re-diffing the DML.
            print("Enabling circular foreign key constraints now for the re-diff!")
            big_bang_logger.debug("Enabling circular foreign key constraints now!")
            ConnectToOracle.toggle_circular_constraints(enable=True)
            print("Circular foreign key constraints enabled.")
            big_bang_logger.debug("Circular foreign key constraints enabled.")
        

        #add the directories to the upgrade scripts to later iterate through to determine if the databases are mirrored or not
        clean_set.add(inner + os.sep + "upgrade_bigbang_ddl")
        clean_set.add(inner + os.sep + "upgrade_bigbang_dml") 
       
    else:
        if NEW_PARADIGM:
            big_bang_logger.debug("[+] RE-DIFF DDL script generation. Downgrade. New Paradigm mode.")
            for schema in DDL_SCHEMAS:
                scan.ddl_scan(schema_name=schema, diff_dir=variable.IGR_DIR, dump_dir=inner + os.sep + "downgrade_bigbang_ddl",
                              direction=up, rediff=True, docker_mode=DOCKER_ENGAGED)

        else:
            big_bang_logger.debug("[+] RE-DIFF DDL script generation. Downgrade DDL.")
            CrazyDiamond.generateDiffScripts(OCP_DIR, diff_dump=inner + os.sep + "downgrade_bigbang_ddl", schema_compare=True, filters=False, re_diff=True)

        

        print("Disabling circular foreign key constraints now for a re-diff!")
        big_bang_logger.debug("Removing circular foreign key constraints now for a re-diff!")

        if NEW_PARADIGM:
            if not variable.MODE == "MONO":
                big_bang_logger.debug("Removing persistent show stopper for re-diff. This is probably already removed during the initial diff.")
                ConnectToOracle.fix_persistent_show_stopper(docker_mode=DOCKER_ENGAGED)
                
            big_bang_logger.debug("Removing circular constraints now - [Docker Mode].")
            ConnectToOracle.toggle_circular_constraints(enable=False, docker_mode=DOCKER_ENGAGED)
            print("Circular constraints removed for re-diff!")
        else:
            ConnectToOracle.toggle_circular_constraints(enable=False)
            print("Circular foreign key constraints removed for re-diff.")
            big_bang_logger.debug("Circular foreign key constraints removed for re-diff.")

        
        big_bang_logger.debug("[+] RE-DIFFing DML now. Downgrade DML.")
        print("[+] RE-DIFFing DML now. Downgrade DML.")
        CrazyDiamond.generateDiffScripts(os.path.join(inner, "downgrade_bigbang_dml"), diff_dump=inner + os.sep + "downgrade_bigbang_dml", schema_compare=False, re_diff=True)

        if NEW_PARADIGM:
             #adding cyclic constraints after re-diffing the DML.
            print("Enabling circular foreign key constraints now for the re-diff in DOCKER MODE!")
            big_bang_logger.debug("Enabling circular foreign key constraints now in DOCKER MODE!")
            ConnectToOracle.toggle_circular_constraints(enable=True, docker_mode=DOCKER_ENGAGED)
            print("Circular foreign key constraints enabled in DOCKER MODE!")
            big_bang_logger.debug("Circular foreign key constraints enabled in DOCKER MODE!")

        else:
            #adding cyclic constraints after re-diffing the DML.
            print("Enabling circular foreign key constraints now for the re-diff!")
            big_bang_logger.debug("Enabling circular foreign key constraints now!")
            ConnectToOracle.toggle_circular_constraints(enable=True)
            print("Circular foreign key constraints enabled.")
            big_bang_logger.debug("Circular foreign key constraints enabled.")

       


        #add the directories to the downgrade scripts, to later check if the files in these directories are empty or 'clean'
        clean_set.add(inner + os.sep + "downgrade_bigbang_ddl")
        clean_set.add(inner + os.sep + "downgrade_bigbang_dml")
        big_bang_logger.debug(f'clean_set = {clean_set}')

    #clean the files here - remove the junk, commit statements, alter compile, and consts$ package
    if up:
        big_bang_logger.info("Cleaning the upgrade re-diffs.")
        warm_shower(inner + os.sep + 'upgrade_bigbang_ddl', rediff=True) #remove sys.gt213434_ objects
        take_out_trash(inner + os.sep + 'upgrade_bigbang_ddl') #remove 'alter compile' from DDL and consts$ from DDL
        warm_shower(inner + os.sep + 'upgrade_bigbang_dml', rediff=True)
        big_bang_logger.debug("[+] Removing commit statements from RE-DIFF DML upgrade scripts now.")
        RemoveJunkFromScript.rmCommit(inner + os.sep + 'upgrade_bigbang_dml')
        big_bang_logger.info("Upgrade re-diffs cleaned.")
        
    else:
        big_bang_logger.info("Cleaning the downgrade re-diffs.")
        warm_shower(inner + os.sep + 'downgrade_bigbang_ddl',rediff=True)
        take_out_trash(inner + os.sep + 'downgrade_bigbang_ddl')
        warm_shower(inner + os.sep + 'downgrade_bigbang_dml', rediff=True)
        big_bang_logger.debug("[+] Removing commit statements from RE-DIFF DML downgrade scripts now.")
        RemoveJunkFromScript.rmCommit(inner + os.sep + 'downgrade_bigbang_dml')
        big_bang_logger.debug("Downgrade re-diffs cleaned.")

    
    #now I could write code to check the length of the file and determine if the file ends with
    #a commit statement. All blank DML sync scripts have 15 lines and end with a "COMMIT;" as of now.
    #This could be changed in the configuration of RedGate (RG) though. The end-user could simply
    #compare the new diff scripts that are generated. SCO blanks have a length of 5 lines.
    #A simple count for the length of the file in terms of lines of text inside it maybe an effective check.

    
    for file in clean_set:

        big_bang_logger.info(f"[+] Currently looking at this directory to see if the re-diffs are empty: {file}. If re-diff file is empty then the initial diff-script was a complete success.")
    
        #only see if the 'cleaned' re-diff files are empty
        rediff_files = glob.glob(file + os.sep + "*_RE-DIFF.sqlClean.sql") # get the directory where the diff scripts are
        directory = file.split(os.sep)[-1]
        big_bang_logger.debug(f"[+] Studying re-diff scripts in this directory: {directory}")
        
        if 'ddl' in directory:
            big_bang_logger.debug("[+] This is a DDL re-diff test.")
            
            
            
            for f in rediff_files:
                length = ReDiff.file_length(f)
                big_bang_logger.debug(f"[+] File: {f} has a {length} lines.")
                if length > 0:
                    print(f"[!] {length} lines detected. This file may have a problem: {f}")
                    big_bang_logger.debug(f"[!]{length} lines detected. This re-diff file may have a problem: {f}")
                elif length == None:
                    print(f"[!] None returned. There may be a problem with this file: {f}")
                    big_bang_logger.error(f"[!] None returned. There may be a problem with this file: {f}")
                else:
                    big_bang_logger.debug(f"[!] Something may of went wrong studying the re-diff for the DDL process. It is possible 0 re-diffs were produced. For DDL this means there are not any differences. Re-diff success! :)")
            if len(rediff_files) == 0:
                print(f"[+] Success there were not any re-diffs for the DDL in {directory}.")
                big_bang_logger.info(f"[+] Success there were not any re-diffs for the DDL in {directory}.")
                
        else:
            big_bang_logger.debug("[+] This is a DML re-diff test.")
            for f in rediff_files:
                length = ReDiff.file_length(f)
                big_bang_logger.debug(f"[+] File: {f} has a {length} lines.")
                if length == 0:
                    big_bang_logger.debug(f"[!] This file in the re-diff check has zero lines: {f} in directory: {directory}")
                elif length != 14:
                    print(f"[!] This file may have a problem %s. This code is in the {directory} directory." %f)
                    big_bang_logger.debug(f"[!] This re-diff file may have a problem %s. This code is in the {directory} directory." %f)
                elif length == 14:
                    big_bang_logger.info(f"[+] RE-DIFF clean for DML script: {f.split(os.sep)[-1]} in {directory}.")
                    print(f"[+] RE-DIFF clean for DML script: {f.split(os.sep)[-1]} in {directory}.")
                elif length == None:
                    print(f"[!] None returned. There is a problem with this file: {f} in {directory}.")
                    big_bang_logger.error(f"[!] None returned. There is a problem with this file: {f} in {directory}.")
                else:
                    print(f"[?] The Re-diff has this many lines: {length}. You may want to check it out here {directory}.")
                    big_bang_logger.error(f"[?] The Re-diff has this many lines: {length}. You may want to check it out here {directory}.")
                    
                    
                    
                    

    big_bang_logger.debug("[+] Re-diff function complete.")
    big_bang_logger.debug(f"[+] Current directory is: {os.getcwd()}")
        

def step1(pdb1, pdb2):
    """ Step 1 in this process. Remove the PDBs.  Load the new PDBs. """

    big_bang_logger.info("[+] Step 1 starting.")
    
    #Let's remove the PDBs and then load the new PDBs
    #
    #first get this current directory to switch back to later
    current_dir = os.getcwd()
    global START_DIR
    START_DIR = current_dir

    #save the starting directory of the script to a file in case the program is called from a savepoint and this state data is needed
    with open(variable.DIFF_SCRIPTS + os.sep + 'START_DIR.txt', 'w') as sd:
        sd.write(current_dir)
    
    
    big_bang_logger.debug(f"The current directory is: {current_dir}")

    if DOCKER_ENGAGED:
        big_bang_logger.info("[+] Docker mode is engaged.")
        print('[+] Docker mode is engaged.')

    #1st lets check if we have the names of the PDBs to load if not the program will stop
    assert pdb1 and pdb2, "You need to specify values for pdb1 and pdb2"
    
    
    big_bang_logger.info("Removing PDB 1 now. This will take several minutes.")
    print("[+] Removing PDB1 now.")

    #remove whatever is there - with the pdb_bot.list_pdbs() function's help. ^_$
    pdb1_current, pdb2_current = pdb_bot.list_pdbs()

    if DOCKER_ENGAGED:
        #call the remove pdb for the docker container
        
        print(f"Removing {pdb1_current['branch_1']} now.")
        big_bang_logger.debug(f"Removing {pdb1_current['branch_1']} now.")
        pdb_bot.docker_remove_pdb(branch=pdb1_current['branch_1'], slot_number=1, debug=False)
        
    else:
        pdb_bot.remove_the_pdb(1)

        
    big_bang_logger.info("Removing PDB 2 now. This will take several minutes.")

    print(f"[+] Removing PDB2 {'branch_2'} now.")
    if DOCKER_ENGAGED:
        #call the remove pdb for the docker container
        pdb_bot.docker_remove_pdb(branch=pdb2_current['branch_2'], slot_number=2, debug=False)
        
    else:
        pdb_bot.remove_the_pdb(2)

    
    # load the PDBs

    big_bang_logger.info(f"Now loading {pdb1} in slot 1.")
    print(f"[+] Now loading {pdb1} in slot 1.")

    if DOCKER_ENGAGED:
        big_bang_logger.debug(f"[+] Now loading {pdb1} into slot 1 in the container database.")
        print(f"[+] Now loading the PDB1 {pdb1} in the container database.")
        pdb_bot.docker_load_basic_batch(1, pdb1, experiment=EXPERIMENT)
    else:
        print(f"[+] Now loading the PDB1 {pdb1} in the host DBMS.")
        pdb_bot.load_the_pdb(1, pdb1)

    big_bang_logger.info(f"Now loading {pdb2} in slot 2.")
    print(f"[+] Now loading {pdb2} in slot 2.")

    if DOCKER_ENGAGED:
        big_bang_logger.debug(f"[+] Now loading {pdb2} into slot 2 in the container database.")
        print(f"[+] Now loading {pdb2} into slot 2 in the container database.")
        pdb_bot.docker_load_basic_batch(2, pdb2, experiment=EXPERIMENT)
    else:
        print("[+] Now loading PDB2 {pdb2} in slot 2 on the host DBMS.")
        pdb_bot.load_the_pdb(2, pdb2)
        
    

    #after the load/unload PDB business is complete switch back to the main directory so the script will run as expected
    os.chdir(current_dir)
    current_dir = os.getcwd()
    big_bang_logger.info(f"Load/Unload PDB process complete. Current directory is: {current_dir}")

    big_bang_logger.debug("[+] Checking to see if both PDBs are loaded.")
    p1, p2 = pdb_bot.list_pdbs()

    assert "Do-Not-Use" not in p1['branch_1'], "PDB1 is not loaded."
    assert "Do-Not-Use" not in p2['branch_2'], "PDB2 is not loaded."

    
    big_bang_logger.debug("[+] Both PDBs seem to be loaded.")
    

    big_bang_logger.info("[+] Step 1 complete.")

def step2():
    """ create the dump directory"""

    big_bang_logger.info("[+] Step 2 start.")
    print("[+] Creating the dump directory in step 2.")
    
    #create the directory where we will put the deployment scripts
    big_bang_logger.debug("Creating DUMP_DIR global variable.")

    global DUMP_DIR #set the global variable
    #check if a file has been written to disk if this file is present we can use the release folder in the file as the 'dump directory'
    release_location = pathlib.Path(variable.DIFF_SCRIPTS)
    release_file = release_location / 'current_software_release.txt'
    if release_file.exists():
        with open(release_file) as rf:
            release_folder = rf.readlines()

        release_folder = release_folder[0]
        my_re = re.compile(r'[\n]') #find new-line characters
        release_folder = my_re.sub("", release_folder) #substitute an empty string where a new-line character is found
        DUMP_DIR = release_folder
        big_bang_logger.debug(f"DUMP_DIR set to the release folder. DUMP_DIR = {DUMP_DIR}")

        

    else:
        DUMP_DIR = awesome.createDumpDir("bigbang") 

    big_bang_logger.debug("The DUMP_DIR is located here: %s" % os.path.abspath(DUMP_DIR))
    print(f"[+] The DUMP_DIR is located here: %s" % os.path.abspath(DUMP_DIR))
    big_bang_logger.info("[+] Step 2 complete.")

def step3(inter=False):
    """ Create the DDL - Both up/down DDL can be created at once.  """

    if not DML_ONLY:
        big_bang_logger.info("[+] Step 3 start.")
        
        #create the DDL up/down scripts - seems to work :) 3/27/2020
        print("[+] Starting the DDL process.")
        big_bang_logger.debug("[+] Starting the DDL process.")
        up_ddl = ddl() #create upgrade - Location of the scripts returned.
        down_ddl = ddl(up=False) #create downgrade
        print("[+] Test - DDL process complete. ")
        big_bang_logger.debug("[-] Test - DDL process complete ")

        with open(variable.DIFF_SCRIPTS + os.sep + 'step3.txt', 'w') as fw:
            fw.write(up_ddl)
            fw.write("\n")
            fw.write(down_ddl)

        big_bang_logger.info("[+] Step 3 complete.")
    else:
        big_bang_logger.info("[+] DML only mode engaged. Skipping step 3.")
        print("[+] DML only mode engaged.")

def step4():
    """Deploy the upgrade DDL code. """
    if not DML_ONLY:
        
        my_re = re.compile(r'[\n]') #find new-line characters

        up_ddl = None
        with open(variable.DIFF_SCRIPTS + os.sep + 'step3.txt', 'r') as s3:
            up_ddl = s3.readlines()

        up_ddl = up_ddl[0]
        up_ddl = my_re.sub("", up_ddl) #substitute an empty string where a new-line character is found
            
        #deploy the code
        print("[-] Test - deployment here.")
        build_team_bot(up_ddl, None) #upgrade DDL - this function also generates the error report
    else:
        big_bang_logger.info("[+] DML only mode engaged. Skipping step 4.")
        print("[+] DML only mode engaged. No need to deploy any DDL code.")
        

def step5(inter=False):
    """ Create the upgrade DML """
    if DDL_ONLY:
        print("[+] DDL only mode engaged.")
    else:
        
        #create the DML upgrade scripts


        big_bang_logger.debug("[+] Starting the upgrade DML process.")
        print("[+] Starting the upgrade DML process.")
        up_dml = dml() #dml - create upgrade DML scripts. Location of the scripts returned.
        print("[+] DML upgrade scripts generated.")
        big_bang_logger.debug("[+] DML upgrade scripts generated.")

        with open(variable.DIFF_SCRIPTS + os.sep +'step5.txt', 'w') as fw:
            fw.write(up_dml)

def step6():
    """Deploy the upgrade DML code. """
    if DDL_ONLY:
        print("[+] DDL only mode engaged.")
    else:
        
        import re
        my_re = re.compile(r'[\n]') #find new-line characters

        up_dml = None
        with open(variable.DIFF_SCRIPTS + os.sep + 'step5.txt', 'r') as s4:
            up_dml = s4.readlines()

        up_dml = up_dml[0]
        up_dml = my_re.sub("", up_dml) 
            
        #deploy the code
        print("[-] Test - deployment here.")
        build_team_bot(None, up_dml) #upgrade DML - this function also generates the error report

def step7():
    """ Re-diff both DDL and DML upgrade scripts. This does not deploy any code to any databases."""
    if FAST or DML_ONLY or DDL_ONLY:
        print("[+] Fast mode engaged. No-rediffs required.")
        big_bang_logger.info("Fast mode engaged. No-rediffs required.")
    else:
         #rediff here
        big_bang_logger.debug("*" * 40)
        big_bang_logger.debug("[+] Now re-diffing DDL/DML upgrade scripts.")
        big_bang_logger.debug("*" * 40)
        print("*" * 40)
        print("[+] Now re-diffing DDL/DML upgrade scripts.")
        print("*" * 40) 
        rediff(up=True) #upgrade re-diff
        print("*" * 40)
        print("[+] Re-diffing upgrade DDL/DML complete")
        print("*" * 40)
        big_bang_logger.debug("*" * 40)
        big_bang_logger.debug("[+] Re-diffing upgrade DDL/DML complete")
        big_bang_logger.debug("*" * 40)

def step8(pdb1):
    """ Flashback PDB1 so that PDB1 is returned to the way we found PDB1."""
    
    print("*" * 40)
    print("[+] Flashing back PDB1.")
    print("*" * 40)
    big_bang_logger.debug("*" * 40)
    big_bang_logger.debug("[+] Flashing back PDB1.")
    big_bang_logger.debug("*" * 40)

    import subprocess
    import re

    os.environ['PDB_FORCE_FLASHBACK'] = 'Y'

    
    try:
        big_bang_logger.debug("[+] Calling flashback script now.")
        print("[+] Calling flashback script now.")
        
        docker_load = subprocess.run(['C:\\cygwin64\\bin\\bash', '-l', '-c', f'flashback_pdb.sh {pdb1} 1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) #adding the slot number so the linked worktrees are not needed

        big_bang_logger.debug("[+] Flashback script complete!")
        print("[+] Flashback script complete!")

        st = docker_load.stdout
        er = docker_load.stderr
        #add a regex to find an ORA and not random output that says ORA
      
        error_found = re.search(r'ORA-\d{5}', er)
        standard_out_error = re.search(r'ORA-\d{5}', st)

        if error_found:
            print("*" * 50)
            print("[!] There is a database error in the error stream!")
            print(er)
            print("*" * 50)
            raise Exception('ORA detected in database flashback process in the error stream.')
        else:
            print("[+] No errors found in the error stream.")

        if standard_out_error:
            print("*" * 50)
            print("[!] There is a database error in the standard output!")
            print(st)
            print("*" * 50)
            raise Exception('ORA detected in database flashback process in the standard output stream.')
        else:
            print("[+] No errors found in the standard output stream.")
        
        
        if not error_found and not standard_out_error:
            print("*" * 40)
            print("[+] Flashback complete.")
            print("*" * 40)

        
    except Exception as fbe:
        print("*" * 50)
        print(f"[!] Exception thrown attempting to flashback {pdb1}. The exception is: {fbe}")
        print("*" * 50)
        big_bang_logger.debug(f"[!]Exception thrown attempting to flashback {pdb1}. The exception is: {fbe}")
        
        big_bang_logger.debug(f"Going to try and reload PDB1 since the flasback process encountered errors.")
        print("Going to try and reload PDB1 since the flashback process encountered errors.")



        #change back to "diff_scripts" directory so docker_load.log is written in this folder instead of the upgrade dml folder. ^_+
       
        #If the START_DIR is populated then use this value. Otherwise, look in the START_DIR.txt for the starting dir data and switch to that location.
        if START_DIR:
            os.chdir(START_DIR)
            print(f"[*] START_DIR = {START_DIR}")
        else:
            print(f"[*] START_DIR = {START_DIR}")
            import re
            my_re = re.compile(r'[\n]') #find new-line characters
            diff_dir = variable.DIFF_SCRIPTS
            diff_scripts_path = pathlib.Path(diff_dir)
            if os.getcwd() == diff_scripts_path:
                print("[+] In the correct directory.")
                
            else:
                print(f"[*] Changing directories. The current directory is: {os.getcwd()}")
                os.chdir(diff_dir)
                
            print(f"[*] The current directory is: {os.getcwd()}")
            files = os.listdir('.')
            if 'START_DIR.txt' in files:
                print("[*] START_DIR.txt file found! :) ")
            else:
                print("[*] START_DIR.txt not found!")

            the_file = diff_scripts_path / "START_DIR.txt"
            if the_file.exists():
                with open("START_DIR.txt", 'r') as sd:
                    line = sd.readline().strip()
                    print(f"[*] Line to parse to determine START_DIR is: {line}")
                    print(f"line now  = {line}")
                    start_data = my_re.sub("", line)#remove new-line characters
                    os.chdir(start_data)
            else:
                print(f"[-] Did not find the 'START_DIR.txt' at the following path: {diff_scripts_path}")
                pdb_bot_logger.debug(f"[-] Did not find the 'START_DIR.txt' at the following path: {diff_scripts_path}")
            
                    
        big_bang_logger.debug("[+] Reloading PDB1.")
        big_bang_logger.info("Removing PDB 1 now. This will take several minutes.")


        #remove whatever is there - with the pdb_bot.list_pdbs() function's help. ^_$
        pdb1_current, pdb2_current = pdb_bot.list_pdbs()

        if DOCKER_ENGAGED:
            #call the remove pdb for the docker container
            pdb_bot.docker_remove_pdb(branch=pdb1_current['branch_1'], slot_number=1)
            #delete any files
            #pdb_bot.rm_19_pdb(pdb="fooPDB1", container=DOCKER_ENGAGED)
        else:
            pdb_bot.remove_the_pdb(1)


        if DOCKER_ENGAGED:
            big_bang_logger.debug(f"[+] Now loading {pdb1} into slot 1 in the container database.")
            print(f"[+] Now loading the PDB1 {pdb1} in the container database.")
            pdb_bot.docker_load_basic_batch(1, pdb1)
        else:
            print(f"[+] Now loading the PDB1 {pdb1} in the host DBMS.")


        print(f"[+] {pdb1} should be re-loaded.")
        big_bang_logger.debug(f"[+] {pdb1} should now be re-loaded.")


  

def step9():
    """Deploy downgrade scripts (DDL). """
    
    if not DML_ONLY:
        print("*" * 40)
        print("[+] Deploying the downgrade DDL scripts now.")
        print("*" * 40)

        import re
        my_re = re.compile(r'[\n]') #find new-line characters

        down_ddl = None
        with open(variable.DIFF_SCRIPTS + os.sep + 'step3.txt', 'r') as s3:
            down_ddl = s3.readlines()

        down_ddl = down_ddl[1]
        down_ddl = my_re.sub("", down_ddl) #substitute an empty string where a new-line character is found

    ##    down_dml = None
    ##    with open(r'C:\workspace\foo\foo-db\releases\diff_scripts\step4.txt', 'r') as s4:
    ##        down_dml = s4.readlines()
    ##
    ##    down_dml = down_dml[1]
    ##    down_dml = my_re.sub("", down_dml) 

        #deploy downgrade scripts and get error report
        build_team_bot(down_ddl, None, up=False)

        print("*"* 40)
        print("[+] Downgrade scripts (DDL) deployed.")
        print("*" * 40)
    else:
        print("[+] DML only mode engaged. There are not any DDL scripts to deploy.")
        big_bang_logger.debug("[+] DML only mode engaged. There are not any DDL scripts to deploy.")

def step10():
    """Generate the downgrade DML scripts now that the downgrade DDL is generated and deployed."""
    if DDL_ONLY:
        print("[+] DDL only mode engaged.")
    else:
        #create the DML down scripts
        big_bang_logger.debug("[+] Starting the DML downgrade process.")
        print("*" * 40)
        print("[+] Starting the DML downgrade process.")
        print("*" * 40)
        
        down_dml = dml(up=False) #the location of the scripts is returned to the caller
        print("[+] Downgrade DML generated.")
        big_bang_logger.debug("[+] Downgrade DML generated.")

        big_bang_logger.debug("Saving DML downgrade script location to disk.")
        with open(variable.DIFF_SCRIPTS + os.sep + 'step10.txt', 'w') as fw:
            fw.write(down_dml)

def step11():
    """ Deploy the downgrade DML scripts now."""
    if DDL_ONLY:
        print("[+] DDL only mode engaged.")
    else:
        
        print("*" * 40)
        print("[+] Deploying the downgrade DML scripts now.")
        print("*" * 40)

        import re
        my_re = re.compile(r'[\n]') #find new-line characters

        down_ddl = None
        with open(variable.DIFF_SCRIPTS + os.sep + 'step10.txt', 'r') as s11:
            down_dml = s11.readlines()

        down_dml = down_dml[0]
        down_dml = my_re.sub("", down_dml) #substitute an empty string where a new-line character is found

        #deploy downgrade scripts and get error report
        build_team_bot(None, down_dml, up=False)

        print("*"* 40)
        print("[+] Downgrade scripts (DML) deployed.")
        print("*" * 40)
 

def step12():
    """Re-diffing now."""
     #rediff
    if FAST or DDL_ONLY or DML_ONLY:
        print("[+] Fast mode engaged. No-rediffs required.")
        big_bang_logger.info("Fast mode engaged. No-rediffs required.")

    else:
        print("*" * 40)
        print("[+] RE-DIFFING downgrade scripts now.")
        big_bang_logger.info("[+] RE-DIFFING downgrade scripts now.")
        print("*" * 40)
        rediff(up=False)
        print("*" * 40)
        print("[+] RE-DIFFING complete.")
        big_bang_logger.info("[+] RE-DIFFING complete.")
        print("*" * 40)

def baby_steps(number: int) -> int:
    """Execute a single small step based on an integer passed into the function.
    It maybe important to note that the steps called are the functions in this module.
    """

    if number == 1:
        step1(PDB1, PDB2)
    elif number == 2:
        step2()
    elif number == 3:
        step3()
    elif number == 4:
        step4()
    elif number == 5:
        step5()
    elif number == 6:
        step6()
    elif number == 7:
        step7()
    elif number == 8:
        step8(PDB1)
    elif number == 9:
        step9()
    elif number == 10:
        step10()
    elif number == 11:
        step11()
    elif number == 12:
        step12()
    else:
        print("I am not aware of a step %d." % number)

    return number

def save_me(last_step):
    """Save the last complete step to disk. """
    print("[!] Writing savepoint. last_step = %s" % str(last_step))
    last_step = str(last_step)
    f = open(variable.DIFF_SCRIPTS + os.sep + 'savepoint.txt', 'w')
    f.write(last_step)
    f.flush()
    f.close()



def big_bang(
             inter=False,
             pdb1='',
             pdb2='', 
             savepoint=False,
             docker_mode=None
             ):
    
    global PDB1, PDB2
    PDB1 = pdb1
    PDB2 = pdb2
    s = None
    

    


    #start ASCII spinner if not in interactive mode or gui mode 
    if not inter:
        s = awesome.spin()
        spin_t = threading.Thread(target=s.spinning)
        spin_t.name = "spinning"
        spin_t.start()

    print("[+]Big Bang mode engaged !")
 
    
    big_bang_logger.debug("[+] Big Bang mode engaged!")

    if docker_mode:
        big_bang_logger.debug("[+] Docker mode engaged!")
        global DOCKER_ENGAGED
        DOCKER_ENGAGED = docker_mode #pass the name of the container to this global variable
        

    if inter:
        print("Big Bang interactive mode engaged!")
        
        print("""
             ____ ____ ____ _________ ____ ____ ____ ____ 
            ||B |||i |||g |||       |||B |||a |||n |||g ||
            ||__|||__|||__|||_______|||__|||__|||__|||__||
            |/__\|/__\|/__\|/_______\|/__\|/__\|/__\|/__\|
                                              
                                    

        """)
        awesome.slowdown()

    big_bang_logger.info("""
                 __ ____ ____ _________ ____ ____ ____ ____ 
                ||B |||i |||g |||       |||B |||a |||n |||g ||
                ||__|||__|||__|||_______|||__|||__|||__|||__||
                |/__\|/__\|/__\|/_______\|/__\|/__\|/__\|/__\|
                                              
                                    
        """)

    big_bang_logger.debug("The time is: %s" % time.asctime())

    

    
    last_step = 1 
    try:
        #if not a save point go through the whole list
        if not savepoint:
            for number in range(1,NUMBER_OF_STEPS + 1):
                print("[+] Now executing step #%d" % number)
                last_step = baby_steps(number)

                print(f"last_step = {last_step}")
                save_me(last_step)
            
        #else if a save point go through the list starting at the last step that failed
        else:
            #get the savepoint
            lstep = None
            with open(variable.DIFF_SCRIPTS + os.sep + 'savepoint.txt', 'r') as sp:
                lstep = sp.readlines()[0]

            import re
            a_re = re.compile(r'[\n]')
            lstep = a_re.sub("", lstep) #remove new-line characters
            lstep = int(lstep) #cast to int
            lstep += 1 #start at the step that previous failed. This should be the last successful step plus 1 more. :)
            print("[+] Starting from savepoint at step #%d" % lstep)
            if lstep > NUMBER_OF_STEPS:
                print("There are no more steps to complete. You have reached the end. Great job. Start over again if you want.")
                print("There is in fact no step %d. Sorry folks." % lstep)
                exit()
                
            for number in range(lstep, NUMBER_OF_STEPS + 1):
                print("[+] Now executing step #%d from savepoint" % number)
                
                last_step = baby_steps(number)

                
                print(f"last_step = {last_step}")
                save_me(last_step)
                if last_step == 12:
                    print("[+] You have reached the last step on this galactic voyage, err I mean diff script generation project. Congratulations!")
                    big_bang_logger.info("[+] You have reached the last step on this galactic voyage, err I mean diff script generation project. Congratulations!")
                
        
    except Exception as e:
        print(f"Exception thrown in steps block: {e}")
        

    finally:
        if s:
          s.spun() #Stop the ASCII spinner thread
        
    if not inter:
        if s:
          s.spun() #Stop the ASCII spinner thread
            
    
    big_bang_logger.debug("[+] Big Bang mode complete!")
    print("\n")
    print("[+] Big Bang mode complete!")

if __name__ == "__main__":

    
    big_bang_logger.debug("Program start time: %s" % time.asctime())
    start = time.time()
    big_bang_logger.info("Let's go!")
    big_bang_logger.info(r"""

                          /\_/\
                         ( o.o )
                          > ^ <

                          """)
    
    parse = argparse.ArgumentParser(description="""A module to complete the generation of upgrade and downgrade DDL and DML scripts in one shot.
                                                   This module requires a BASH shell. Use Cygwin if on W$.

                                                   BASIC USAGE:
                                                   python big_bang.py --bigbang --pdb1 <foo-db-4.2.0-RELEASE --pdb2 <foo-db-4.2.1-RC1> -s rite_common
                                                   BASIC SAVE POINT USAGE:
                                                   python big_bang.py --bigbang --pdb1 <foo-db-1.3.1.2-RELEASE> --pdb2 <foo-db-1.3.1.3-RC1> -s rite_common --savepoint

                                    """)

    
    parse.add_argument("--bigbang", action="store_true", default=False, help="Use this argument with the pdb args to execute the program as designed.")
    parse.add_argument("--pdb1", action="store", help="Please specify the PDB to load in slot 1.")
    parse.add_argument("--pdb2", action="store", help="Please specify the PDB to load in slot 2.")
    parse.add_argument("--debug", action="store_true", default=False, help="Debug the module's command line arguments.")
    parse.add_argument("--savepoint", action="store_true", default=False, help="Continue with a diff script generation from a savepoint.")
    parse.add_argument("--schema", "-s", action="append", help="Enter a schema to scan. Use this option for each schema to scan. This method is faster and does not require configuration files.")
    parse.add_argument("--docker", "-d", action="store", help="Please specify the Docker container with the container DB to connect to. Currently supported containers: Oradb19r3Apx20r1, Ora19r3. CTO update needed if container not listed.")
    parse.add_argument("--fast", "-f", action="store_true", default=False, help="Use this to not re-diff. (Fast mode)")
    parse.add_argument("--ddl-only", "-o", action="store_true", dest="ddlonly", default=False, help="Use this for diffs that do not have DML differences. Use this for DDL only diffs")
    parse.add_argument("--tenant", "-t", action="store", dest="tenant", help="Specify a tenant for the multitenant paradigm.")
    parse.add_argument("--dml-only", action="store_true", default=False, dest="dmlonly", help="Use this option to only diff DML")
    parse.add_argument("--experimental", "-e", action="store_true", default=False, dest="EXP", help="Specify this option to obtain strange PDBs with names that deviate from the normal pattern such as: ritehorizon-2.3.19-RC1-DCO_Generation")
    parse.add_argument("--new-branching-model", "-m", action="store_true", default=False, dest="newbranchingmodel", help="Use this option to have New Branching Model folder structure")
    

    args = parse.parse_args()

    if args.debug:
        print("This is what is going on with 'argparse': %s" % args)
        print("")

    elif args.bigbang and not args.docker:
        if args.fast:
            print("[+] Fast mode engaged!")
            big_bang_logger.debug("Re-diffs are not engaged for fast mode.")
            FAST = True 
        else:
            big_bang_logger.debug("Re-diffs are engaged for normal mode.")
        print("[+] Using configuration files for DDL.")
        print("This option does not work at anymore with the new paradigm. Use --docker mode! Also, for DDL please use -s or --schema to generate DDL.")
        big_bang_logger.debug("This option does not work at anymore with the new paradigm. Use --docker mode! Also, for DDL please use -s or --schema to generate DDL.")
        exit()
        #the next step will not execute
        big_bang(pdb1=args.pdb1, pdb2=args.pdb2, savepoint=args.savepoint, docker_mode=args.docker)

        
        
        
        
    elif args.bigbang and args.docker:
        assert args.docker in ['Ora19r3', 'Oradb19r3Apx20r1'], f"{args.docker} not recognized as a suitable container. Try again."

        #initialize global variable module
        variable.init()
            
        #find which agency this is for.
        if args.pdb1.startswith('foo-db'):
            variable.MODE = "foo"
        elif args.pdb1.startswith('bar-db'):
            variable.MODE = "RITE"
        elif args.pdb2.startswith('spamhorizon'):
            #get current directory and see if mono is in it
            variable.MODE = "MONO" 
            
                
        
        
        variable.toggle_variables(variable.MODE) #toggle the variables
        big_bang_logger.debug(f"[+] MODE set to {variable.MODE}")

        if args.schema:
            DDL_SCHEMAS = [x.upper() for x in args.schema] #add the schemas from the CLI to the global variable - First use a list comprehension to make everything passed in uppercase. :)
        if not args.schema and not args.dmlonly:
            print("[+] Did you forget to use the -s option to add DDL schemas to compare? Did you forget to use --dml-only mode? Something is messed up with this logic. Program shutting down.")
            exit() 
        NEW_PARADIGM = True
        big_bang_logger.debug("[+] New Paradigm mode engaged.")
        print("[+] New Paradigm mode engaged.")
        if DDL_SCHEMAS:
            print(f"[+] DDL_SCHEMAS = {DDL_SCHEMAS}")
            print(f"[+] Looking for 'ignore rules' files here: {variable.IGR_DIR}")
            big_bang_logger.debug(f"[+] DDL_SCHEMAS = {DDL_SCHEMAS}")
            big_bang_logger.debug(f"[+] Looking for 'ignore rules' files here: {variable.IGR_DIR}")
        if args.docker:
            print(f"[+] DOCKER ENGAGED!")
            big_bang_logger.debug(f"[+] DOCKER_ENGAGED = {args.docker}")
        else:
          print(f"[+] Not using Docker for this release. args.docker = {args.docker}")
          big_bang_logger.debug(f"[+] Not using Docker for this diff. args.docker = {args.docker}")
          print("*" * 100)
          print(f"[+] Currently Docker mode is the only way. Program shutting down now.")
          print("*" * 100)
          big_bang_logger.debug(f"[+] Currently Docker mode is the only way. Program shutting down now.")
          exit()

        if args.fast:
            print("[+] Fast mode engaged!")
            big_bang_logger.debug("Re-diffs are not engaged for fast mode.")
            FAST = True
        else:
            big_bang_logger.debug("Re-diffs are engaged for normal mode.")

        if args.ddlonly:
            print("[+] This is a DDL only diff.")
            big_bang_logger.debug("[+] DDL only diff engaged.")
            DDL_ONLY = True
        if args.tenant:
            TENANT = args.tenant
            print(f"[+] tenant = {TENANT}")
            big_bang_logger.debug(f"[+] tenant = {TENANT}")
            big_bang_logger.debug("[+] Tenant specified on the command line")
            variable.TENANT = TENANT
        if args.dmlonly:
            print("[+] This is a DML only diff.")
            big_bang_logger.debug("[+] DML only diff engaged.")
            DML_ONLY = True
        if args.EXP:
            print("[+] Experimental mode engaged!")
            big_bang_logger.debug("[+] Experimental mode engaged!")
            EXPERIMENT = True
        if args.savepoint:
            print("[+] Savepoint mode engaged!")
            big_bang_logger.debug("[+] Savepoint mode engaged!")
            SAVEPOINT = True
            

       

        big_bang_logger.debug(f"[+] This is a diff for {variable.MODE}")
        big_bang_logger.debug(f"[+] This is the diff script location: {variable.DIFF_SCRIPTS}")
        big_bang_logger.debug(f"[+] SDATA_LIST = {variable.SDATA_LIST}")
        big_bang_logger.debug(f"[+] DOCKER_DCO = {variable.DOCKER_DCO}")
        big_bang_logger.debug(f"[+] IGR_DIR = {variable.IGR_DIR}")
        big_bang_logger.debug(f"[+] SCHEMA_LIST = {variable.SCHEMA_LIST}")
        big_bang_logger.debug(f"[+] RELEASE_DIR = {variable.RELEASE_DIR}")

        
        if not args.savepoint and not args.newbranchingmodel:
            #this does not need to run multiple times normally
            print("[*] R2D2 starting...")
            r2d2_thread = threading.Timer(1.0,r2d2.autoFolders, args=(args.pdb1, args.pdb2, variable.RELEASE_DIR)) #wait 1 seconds before calling the autoFolders function
            r2d2_thread.name="R2d2 Thread"
            r2d2_thread.start()
        elif not args.savepoint and args.newbranchingmodel and TENANT:
            print("[*] R2D2 new-branching-model mode starting up...")
            r2d2_NBM = threading.Thread(target=r2d2.newBranchingModelFolders, kwargs={"base_dir":variable.RELEASE_DIR, '''tenant''':variable.TENANT})
            r2d2_NBM.name="R2D2 Thread - big_bang - NewBranchingModel"
            r2d2_NBM.start()
        
            
        

        
        
        print("[*] Main thread starting the diff script generation...")
        big_bang(pdb1=args.pdb1, pdb2=args.pdb2, savepoint=args.savepoint, docker_mode=args.docker)

        try: 
            #move the folders to the release folders (this also removes the folders from the 'bigbang' folder except for 1 of the downgrade folders because the process holds onto the files
            #time.sleep(5) #sleep for 5 seconds to try and prevent a process from still accessing the downgrade_dml folder
            
            #r2d2.moveFolders(args.pdb2)
            #update the readme files
            r2d2.updateReadMe()
        except Exception as final_steps_exception:
            print(f"[!] Exception thrown trying to complete the final steps. Did the main loop crash first? The exception is: {final_steps_exception}")

        
        
        

    else:
        print("[+] Boop bleep blop.")
        print("[+] The ultimate answer is 42 but what is the ultimate question to the meaning of life, the universe, and everything that gives the answer 42?")
        print("[?] Are you executing this program from a Unix shell? Do so please and type -h as a parameter to this module on the command line.")

    print("")
    big_bang_logger.debug("Program stop time: %s" % time.asctime())
    total_time = time.time() - start
    print("[+] The program took %s seconds to run. This is about %s minutes." % (str(total_time), str(total_time / 60)))
    big_bang_logger.debug("[+] The program took %s seconds to run. This is about %s minutes." % (str(total_time), str(total_time / 60)))

    
