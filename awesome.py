import Direction
import ChangeDirection
import CrazyDiamond
import MetaSQL
import RemoveJunkFromScript
import LowIonConfig
import ConnectToOracle
import ErrorReport
import apv
import ReDiff
import LostSchemas
import seven
import pdb_bot
import clean_pdbs

#included with Python
import logging
import time
import threading
import math
import builtins
import getopt
import sys
import os
import glob
import time
import pathlib

#logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

awesome_logger = logging.getLogger('awesome-log')
if not awesome_logger.handlers:
    awesome_fh = logging.FileHandler('awesome-debug.log')
    awesome_logger.setLevel(logging.DEBUG)
    awesome_fh.setFormatter(formatter)
    awesome_logger.addHandler(awesome_fh) #add the file handler to the logger



#create a log file for schemas missing
missing_schema_logger = logging.getLogger('missing_schemas')
if not missing_schema_logger.handlers:
    missing_schema_fh = logging.FileHandler('missing_schemas_dco_ocp_bonanza.log')
    missing_schema_logger.setLevel(logging.DEBUG)
    missing_schema_fh.setFormatter(formatter)
    missing_schema_logger.addHandler(missing_schema_fh) #add the file handler to the logger


#global variables
DUMP_DIR = ''
DEBUG = False
MISSING_SCHEMA = [] #this can be useful during DML to figure out if RC is present to avoid an error when modify ap_versions table in RC.
O_LIST = None

def whiteRabbit():
    """Change the color of the command prompt while the program is executing. Only works on W$"""

    for i in range(60):
        os.system('color %d' % i)
        time.sleep(.01)

    os.system('color 3') # back to black background with blue-ish text

class TimeProcess:

    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False
        
    def runtime(self):
        """This should give the runtime of a process"""
        try:
            start = time.time()
            while True and self._running:
                elapsed_time = round(time.time() - start) #seconds - floating point
                if elapsed_time > 59:
                    sys.stdout.write(f'Process runtime: {round(elapsed_time/60)} minutes')
                else:
                    sys.stdout.write(f"Process runtime: {round(elapsed_time)} seconds")
                sys.stdout.flush()
                time.sleep(0.1)
                sys.stdout.write('\r')
                time.sleep(3)
        except KeyboardInterrupt as ki:
            print("\nStopping")


class spin:

    def __init__(self):
        """Initialize the thread class with this variable that can control thread execution. """
        self._run = True

    def spun(self):
        """Call this function to stop the spinning function thread """
        self._run = False
    
    def spinning_cursor(self):
        """This function is a generator that can create an ASCII spinner."""
        while True:
            for cursor in '|/-\\':
                yield cursor

    def spinning(self):
        """Create an ASCII spinner.  """
        spinner = self.spinning_cursor()
        #print("Working...")
        try:
            while True and self._run:
                sys.stdout.write(next(spinner))
                sys.stdout.flush()
                time.sleep(0.1)
                sys.stdout.write('\b')
        except KeyboardInterrupt as ki:
            print("\nStopping!")

def slowdown():
    """Ask the user if they want to continue with the program."""
    x = input("Do you want to continue?(y/n)")
    if x.lower().startswith('y'):
        pass
    else:
        exit()

def setDebug():
    global DEBUG
    DEBUG = True

def setOList(location):
    global O_LIST
    O_LIST = location

def removeWrapper(directory, rediff=False):
    """Wrapper function to call another function to clean a group of deployment scripts. """
    
    directory = os.path.abspath(directory)
    os.chdir(directory)

    
    if DEBUG:
        awesome_logger.debug("The script, %s, changed to this directory, %s, in batch mode." % (sys.argv[0], directory))

    if rediff:
        files = glob.glob("*RE-DIFF.sql")
    else:
        files = glob.glob("*.sql")

    if DEBUG:
        awesome_logger.debug("Found these files in batch mode: %s" % files)
    for f in files:
        RemoveJunkFromScript.rmJunk(f)


def getDown(directory):
    """Make the configuration files downgrade configuration files. The directory passed in should
       be where the configuration files are kept.
    """
    try:
        os.chdir(directory)
    except Exception as e:
        print(f"Caught this exception -> {e}")
        exit()
        
    if DEBUG:
        awesome_logger.debug("The current directory is: %s" % os.getcwd())
    files = [glob.glob(e) for e in ["*.dco", "*.ocp"]]
    for f in files:
        for x in f:
            if DEBUG:
                awesome_logger.debug("Making this file [%s] a downgrade. " % str(x))
            Direction.goDown(x)
            
            

def getUp(directory):
    """ Make the configuration files upgrade configs. The directory passed in should be where the
        configuration files are stored.
    """
    try:
        os.chdir(directory)
    except Exception as e:
        print(f"Caught this exception -> {e}")
        exit()
    if DEBUG:
        awesome_logger.debug("The current directory is: %s" % os.getcwd())
    files = [glob.glob(e) for e in ["*.dco", "*.ocp"]]
    for f in files:
        for k in f:
            if DEBUG:
                awesome_logger.debug("Making this file [%s] an upgrade." % str(k))
            Direction.goUP(k)
            
            

def deleteDirtyFiles(absolutepath, inter=False):
    """This function will clean 'dirty' SQL scripts from a directory specified absolutely. """
        
    #Do not delete any of the 'cleaned' files
    files_to_not_delete = glob.glob(absolutepath + os.sep +'*Clean.sql')
    
    #in order to not delete the deployment script, when this function is re-run
    #on the re-diff files, add the CBT-MetaSQL*.sql deployment script to the files to save
    deployment_not_to_delete = glob.glob(absolutepath + os.sep + "CBT-MetaSQL*.sql")

    #do not delete the error report during re-diff
    error_png_image = glob.glob(absolutepath + os.sep + "error_report.png")

    #do not delete the log files during re-diff
    logs = glob.glob(absolutepath + os.sep + "*.log")

    #do not delete .dco files (the Red-gate DML configuration files)
    dcos = glob.glob(absolutepath + os.sep + "*.dco")

    files_to_not_delete = files_to_not_delete + deployment_not_to_delete + error_png_image + logs + dcos #combine the lists
    
    files_to_keep = []
    for k in files_to_not_delete:
        
        files_to_keep.append(k.split(os.sep)[-1]) #grab just the filename from the absolute path


    
    awesome_logger.debug("-" * 80)
    awesome_logger.debug('These are the files to keep (just the names):')
    for keep in files_to_keep:
        awesome_logger.debug(keep)
        awesome_logger.debug("-" * 80)
        
    all_files = os.listdir(absolutepath)#get all the files in the directory

    if DEBUG:
        awesome_logger.debug("These are the files to keep!")
        for f in files_to_not_delete: #this list contains the full path to the file and the filename.
            awesome_logger.debug(f)

    if DEBUG:
        awesome_logger.debug("-" * 80)
        awesome_logger.debug("These are all the files in the directory!")
        for a in all_files:
            awesome_logger.debug(a)

            awesome_logger.debug("-" * 80)

    #delete 'dirty' files from directory with clean diff scripts.
    for af in all_files: 
        if (af not in files_to_keep):
            if inter:
                print("Need to remove this file (y) to continue: %s" % str(af))
                slowdown()
                
            
            awesome_logger.debug("[!] Need to remove this file: %s" % str(af))
            os.remove(af) #remove the file
            awesome_logger.debug("[-] File, [%s], removed!" % str(af))
            
            if inter:
                print("[-] File, [%s], removed!" % str(af))

def singleConfig(csv_file, dco_file, dump_dir, v_4_verbose=False):
    """This function calls the module that creates the dynamic DCO config. This only creates a single config at a time.
       Currently, there is no option for a verbose mode. Use --debug instead of the depreciated -v mode.
       Although, you can use the -v mode to get a lot more console output from LowIonConfig.
    """
    
    current_dir = os.path.abspath(os.getcwd()) #get the path where the script is executed
    dump_dir = createDumpDir() #create the dump directory 
    
    if DEBUG:
        awesome_logger.debug("Calling this function 'LowIonConfig.compareIt(csv_file, dco_file)'. Verbose mode is 'False'.")
        
    LowIonConfig.compareIt(csv_file, dco_file, path_to_config=dump_dir,tmpDir=current_dir, v_4_verbose=v_4_verbose)
    
    if DEBUG:
        awesome_logger.debug("Finished calling the compareIt() function in LowIonConfig.")
    
    

def batchConfig(csv_file, dco_dir, dump_dir=DUMP_DIR, inter=False):
    """Modify which tables are compared in DML scans"""

    awesome_logger.debug("[+] At the top of the 'batchConfig' function.")

    awesome_logger.debug("The dump_dir parameter = %s" % dump_dir)
    
    current_dir = os.getcwd()
    current_dir = os.path.abspath(current_dir)
    awesome_logger.info(f"[+] The current directory is: {current_dir}")
    csv_file = os.path.abspath(csv_file) #get the path of the CSV of the current directory. What if a path is specified for the CSV file? 0_o
    awesome_logger.info(f"[+] The 'csv_file' = {csv_file}")
    

    #The 'dco_dir' is populated with the '-g' or '--group' option
    dco_dir = os.path.abspath(dco_dir)
    awesome_logger.info(f"Changing directories to the 'dco_dir' located here: {dco_dir}")
    os.chdir(dco_dir)
    
    awesome_logger.debug("The current directory is: %s" % os.getcwd())
    if inter:
        print("The current directory is: %s" % os.getcwd())
        slowdown()

    #find the DCO files in the current directory
    files = glob.glob('*.dco')
    
    awesome_logger.debug("This is the list of files found: %s " % files)

    
    if inter:
        print("Found these files: %s" % files)
        slowdown()

##    #return a list of schemas passing in the csv file path/name and the install type
##    lost_dcos = LostSchemas.LostSchemas()
##    schemas = lost_dcos.readSchemaCSV(pathToCSV=csv_file)
##    schemas = set(schemas) #just get unique values :)
##
##    #find files that are missing from the comparison
##    for s in schemas:
##        filename = (s+'.dco')
##        if filename not in files:
##            MISSING_SCHEMA.append(filename)
##            print("The following schema is missing a RedGate DCO configuration file in 'bonanza' mode: %s" % filename)
##            missing_schema_logger.error("The following schema is missing a RedGate DCO configuration file in 'bonanza' mode: %s" % filename)
        
    #loop through the files dynamically creating the configuration files for this release
    for f in files:
        
        os.chdir(dco_dir)
        
        awesome_logger.debug("Currently comparing this file: %s with this SDATA_LIST: %s. " % (f, csv_file))
        LowIonConfig.compareIt(csv_file=csv_file, dco_file=f, path_to_config=dump_dir, tmpDir=dco_dir, inter=inter)
        awesome_logger.debug("Done processing this file %s " % f)
        
    
    awesome_logger.debug("Files should be written here: %s " % os.path.abspath(DUMP_DIR))
    if inter:
        print("Files should be written here: %s " % os.path.abspath(DUMP_DIR))
        slowdown()

    
def instructions():
    """This function explains how to use the program. """
    print("""

To make sure you are using this program correctly.
Make sure you have the previous version in PDB1 and the later version
or release candidate (RC) in PDB2. The ASCII art illustration below shows
that the earlier version should be in PDB1 and the later version should
be in PDB2. 

         ____                       ____
        |    |                     |    |
        |    |           --->      |    |
        |____|           <---      |____|
   Earlier version PDB1         Later version PDB2








    """)


def iNeedHelp():
    """Print out some helpful information on how to use the program. """
    
    print("To generate a configuration file for your specific release type the following:\n")
    print("%s --csv SDATA_LIST.csv --dco configuration.dco\n" % sys.argv[0])
    print("To generate a group of configuration files for data compare execute the following command:\n")
    print('%s --csv SDATA_LIST.csv --group "path to dco files"\n' % sys.argv[0])
    print('*' * 80)
    print("To generate the diff scripts from configuration files for schema compare run the following commands:\n")
    print('%s -x -s --configLoot <path-to-config-files> --dumpDir <path to folder where you want to write your diff scripts> \n' % sys.argv[0])
    print('To generate the diff scripts from configuration files for data compare run the following command:\n')
    print('%s -x --configLoot <path-to-config-files> --dumpDir <path to folder where you want to write your diff scripts> \n' % sys.argv[0])
    print("*" * 80)
    print("To show the instructions for the program enter the following command:\n")
    print('%s --instructions\n' % sys.argv[0])
    print('*' * 80)
    print('To figure out if the configuration file is a downgrade or an upgrade type the following:\n')
    print('%s --direction <path to configuration file>\n' % sys.argv[0])
    print('To figure out if a group of configuration files are downgrade or upgrade run the following command:\n')
    print('%s --directionDir <path to directory with config files>\n' % sys.argv[0])
    print('*' * 80)
    print("To change the direction of a single configuration file type the following command:\n")
    print('%s --chdir <path to configuration file>\n' % sys.argv[0])
    print("To change the direction, if the scripts are up or down, of a group of configuration files type the following command:\n")
    print('%s --chdirBatchMode <path to directory with configuration files>\n' % sys.argv[0])
    print('*' * 80)
    print("To remove 'sys.blah' objects from a diff script, a single diff script use the following command:\n")
    print('%s --remove <path to configuration file>\n' % sys.argv[0])
    print("To remove 'sys.blah' objects from a group of diff files in a folder use the following command:\n")
    print('%s --removeDir <path to configuration file>\n' % sys.argv[0])
    print('*' * 80)
    print("To create a deployment script type the following command:")
    print('%s --deploymentScript <path to diff scripts>\n' % sys.argv[0])
    print("*" * 80)
    print("To make a group of configuration files (DCO or OCP) upgrade configurations do as follows.")
    print('''%s --up "<path to configuration files>"''' % sys.argv[0])
    print("To make a group of configuration files (DCO or OCP) downgrade configurations do as follows.")
    print("""%s --down "<path to configuration files>" """ % sys.argv[0])
    print("*" * 80)
    print('b o n a n z a mode - the default mode of the program. ')
    print("--bonanzaOff will shut off the 'bonanza mode' but I am not sure the use case for this. Have fun...")
    print("The 'Bonanza' mode allows one to create upgrades or downgrades at once for either DML or DDL.")
    print("To create upgrade DML scripts in Bonanza mode enter the following command.")
    print("""%s --high --csv "<path to SDATA_LIST.csv>" --group "<path to DCOs>" """ % sys.argv[0])
    print("To create downgrade DML script in Bonanza mode enter the following command.")
    print("""%s --low --csv "<path to SDATA_LIST.csv>" --group "<path to DCOs>""" % sys.argv[0])
    print("To create downgrade DDL scripts in Bonanza mode enter the following command.")
    print("""%s -s --low --csv "<path to SCHEMA_LIST.csv>" --group "<path to OCPs>" """ % sys.argv[0])
    print("To create upgrade DDL scripts in Bonanza mode enter the following command.")
    print("""%s -s --high --csv "<path to SCHEMA_LIST.csv>" --group "<path to OCPs>" """ % sys.argv[0])
    print("*" * 80)
    print("If you want to set the OBJECT_LIST location to a different location for RG Schema Comparisons, execute the following in your other 'bonanza' style command")
    print(r"%s --setObjectList '<C:\pathTo\the\OBJECT_LIST.csv>'" % sys.argv[0])
    print("")
    print("For example to use this in the field outside of a lab setting type the following\n ")
    print(r"""%s -s --high --csv "<path to SCHEMA_LIST.csv>" --group "<path to OCPs>" --setObjectList '<C:\pathTo\the\OBJECT_LIST.csv>'""" % sys.argv[0])
    print("*" * 80)
    print("*" * 6 + " interactive mode " + "*" * 6)
    print("""To call the script in interactive mode try the command below. Add this to bonanza mode.""")
    print("""%s --interactive""" % sys.argv[0])
    print("*" * 80)
    print("*" * 6 + " DEBUG Mode " + "*" * 6 )
    print("""%s --debug""" % sys.argv[0])
    print("""*Note:* To use debug mode this must be the first option specified. """)
    print("*" * 80)
    print("""To enable rediffs please use the following option. """)
    print("""%s --rediff""" % sys.argv[0])
    print("*" * 80)
    print("Specify --pdb1 to load a pluggable database (PDB) in slot 1.")
    print("Specify --pdb2 to load a pluggable database (PDB) in slot 2.")

    
def createDumpDir(dirName=None):
    """This directory creates a directory where the diff scripts are written to disk."""

    if DEBUG:
        awesome_logger.debug("In the 'createDumpDir' function.")

    #go back 1 directory to the 'releases' folder and then create this folder
    if dirName:
        dump_dir = ".." + os.sep + dirName
        if not os.path.exists(dump_dir):
            os.mkdir(dump_dir)

        path_to_generated_scripts = os.path.abspath(dump_dir)

    else:
        
        dump_dir = '..' + os.sep + 'ProgrammaticallyGeneratedConfigurationScripts-LowIonConfig'
        if not os.path.exists(dump_dir):
            os.mkdir(dump_dir)
                
        path_to_generated_scripts = os.path.abspath(dump_dir)

    return path_to_generated_scripts


def Bonanza(csv_file, dco_dir, vertical_direction=True, schema=False, inter=False, object_list=O_LIST, rdiff=False, gui=False, pdb1='', pdb2='', robomode=False):
    """Function to automate the creation of upgrade DML and DDL scripts. """

    groupMode=True

    #start ASCII spinner if not in interactive mode or gui mode 
    if not inter and not gui:
        t = threading.Thread(target=spinning)
        t.daemon = True
        t.start()

    print("[+] Bonanza mode engaged!")
 
    
    awesome_logger.debug("[+] Bonanza mode engaged!")

    if inter:
        print("Bonanza interactive mode engaged!")
        
        print("""

                 _                                      
                | |                                     
                | |__   ___  _ __   __ _ _ __  ______ _ 
                | '_ \ / _ \| '_ \ / _` | '_ \|_  / _` |
                | |_) | (_) | | | | (_| | | | |/ / (_| |
                |_.__/ \___/|_| |_|\__,_|_| |_/___\__,_| !!! >o<
                                                        



        """)
        slowdown()

    awesome_logger.debug("""

                 _                                      
                | |                                     
                | |__   ___  _ __   __ _ _ __  ______ _ 
                | '_ \ / _ \| '_ \ / _` | '_ \|_  / _` |
                | |_) | (_) | | | | (_| | | | |/ / (_| |
                |_.__/ \___/|_| |_|\__,_|_| |_/___\__,_| !!! >o<
                                                        



        """)

    awesome_logger.debug("The time is: %s" % time.asctime())

    if robomode:

        awesome_logger.debug("[+] Robomode engaged - programmatically loading PDBs now.")
        #Let's remove the PDBs and then load the new PDBs
        #
        #first get this current directory to switch back to later
        current_dir = os.getcwd()
        awesome_logger.debug(f"The current directory is: {current_dir}")
        
        awesome_logger.debug("Removing PDB 1 now. This will take several minutes.")
        pdb_bot.remove_the_pdb(1)
        awesome_logger.debug("Removing PDB 2 now. This will take several minutes.")
        pdb_bot.remove_the_pdb(2)

        #delete any leftover files in the PDBs - bounce the Oracle DB
        clean_pdbs.clean_pdbs()

        # load the PDBs
        #1st lets check if we have the names of the PDBs to load if not the program will stop
        if pdb1 and pdb2:
            awesome_logger.debug(f"Now loading {pdb1} in slot 1.")
            pdb_bot.load_the_pdb(1, pdb1)
            awesome_logger.debug(f"Now loading {pdb2} in slot 2.")
            pdb_bot.load_the_pdb(2, pdb2)


        #after the load/unload PDB business is complete switch back to the main directory so the script will run as expected
        os.chdir(current_dir)
        current_dir = os.getcwd()
        awesome_logger.debug(f"The current directory is: {current_dir}")
    
    #Rest of the code after loading and unloading the PDBs

    if inter:
        print("object_list = %s" % object_list)
        slowdown()

    
    awesome_logger.debug("object_list = %s" % object_list)
    
    if inter:    
        #fix spacing here
        if vertical_direction:
            print("This is an upgrade!")
        else:
            print("This is a downgrade!")
        if schema:
            print("This is a DDL comparison")
        else:
            print("This is a DML comparison")
    if inter:
        slowdown()


    if vertical_direction:
        awesome_logger.debug("This is an upgrade!")
    else:
        awesome_logger.debug("This is a downgrade!")
    if schema:
        awesome_logger.debug("This is a DDL comparison")
    else:
        awesome_logger.debug("This is a DML comparison")

    if inter:
        print("Creating DUMP_DIR global variable.")

    awesome_logger.debug("Creating DUMP_DIR global variable.")

    global DUMP_DIR
    DUMP_DIR = createDumpDir() 

    
    if inter:
        print("The DUMP_DIR is located here: %s" % os.path.abspath(DUMP_DIR))
        slowdown()

    awesome_logger.debug("The DUMP_DIR is located here: %s" % os.path.abspath(DUMP_DIR))

    #check for  missing DCO configuration files
    lost_dco = LostSchemas.LostSchemas()
    r_set = lost_dco.checkDCO(SDATA_CSV=csv_file) #returns a set of unique schema names if executed appropriately 

    dco_files = glob.glob(dco_dir + os.sep + '*.dco')
    awesome_logger.info("[*] Found the following DCO configuration files: {}".format(dco_files))
    missing_dco = []

    dco_names = []
    for df in dco_files:
        dco_names.append(df.split(os.sep)[-1]) #just get the last element after splitting on the OS path seperator. This should be the filename. :)

    for ds in r_set:
        config_name = ds + '.dco'
        if config_name not in dco_names:
            missing_dco.append(config_name)

    missing_schema_logger.debug("These DCO configuration files are not present: {}".format(missing_dco))
            
        

            

    
    
    #generate the DCO files based on the SDATA_LIST.csv
    
       
    if len(csv_file) > 0 and (groupMode == True) and not schema:
        #The groupMode command line switch takes an argument that should be the dir of DCO files
        if not inter:
            awesome_logger.debug("Calling the 'batchConfig()' function")
            batchConfig(csv_file, dco_dir, dump_dir=DUMP_DIR)
            awesome_logger.debug("The 'batchConfig(csv_file, dco_dir, inter)' function has completed.")
            awesome_logger.debug("The 'csv_file' variable is: %s" % csv_file)
            awesome_logger.debug("The 'dco_dir' variable is: %s" % dco_dir)
        else:
            print("Calling the 'batchConfig()' function in interactive mode.")
            batchConfig(csv_file, dco_dir, dump_dir=DUMP_DIR, inter=inter)
            print("The 'batchConfig(csv_file, dco_dir, inter)' function has completed.")
            print("The 'csv_file' variable is: %s" % csv_file)
            print("The 'dco_dir' variable is: %s" % dco_dir)
            slowdown()
        
       

        
    else:
        if inter:
            print("Schema comparison so no need to create programmatically generated config files as of now.")
            print("DUMP_DIR global variable set!")

        awesome_logger.debug("Schema comparison so no need to create programmatically generated config files as of now.")
        awesome_logger.debug("DUMP_DIR global variable set!")

        #The else block is for OCP - Schema Compare for Oracle - comparisons
            
        #start checking if all schema OCP configuration files are present
            
        #see if there is a missing configuration script the end-user should know about
        lost = LostSchemas.LostSchemas()
  
        schemas = lost.readSchemaCSV(pathToCSV=csv_file) #this returns the schemas in 'core' that have the 'X' 
        schemas = set(schemas) #only get unique values - this is not a problem with SCHEMA_LIST.csv but just in case
        awesome_logger.debug("[+] Found the following schemas in the csv file passed into the 'csv' argument: %s" % schemas)
        if inter:
            if len(schemas) > 0:
                print("[+] Found the following schemas in the csv file passed into the 'csv' argument: %s" % schemas)
            else:
                print("[-] The schemas list is empty. You may want to look at the SCHEMA_LIST.csv file passed into the --csv argument.")

        if len(schemas) > 0:
            awesome_logger.debug("[+] Found the following schemas in the csv file passed into the 'csv' argument: %s" % schemas)
        else:
            awesome_logger.debug("[-] The schemas list is empty. You may want to look at the SCHEMA_LIST.csv file passed into the --csv argument.")


        #get the files that are in the directory with the OCPs (diff_script_files)
        files = glob.glob(dco_dir + os.sep + '*.ocp')

        file_names = []
        for f in files:
            file_names.append(f.split(os.sep)[-1]) #just get the last element after splitting on the OS path seperator. This should be the filename. :)

        if inter:
            print("[+] Found the following file_names: %s" % file_names)
        awesome_logger.debug("[+] Found the following file_names: %s" % file_names)
        
        #prints out what is found in the 'diff_script_files\SchemaComparison' folder 
        if inter or DEBUG:
            print("Found the following '.ocp' files: ")
            for ocp_file in file_names:
                print(ocp_file)
                
        awesome_logger.debug("Found the following '.ocp' files")
        for f in file_names:
            awesome_logger.debug(f)

        #this bit of code actually compares what is found in the SCHEMA_LIST.csv and what is in the config folder
        missing_schemas = []
        for s in schemas:
            schema_config = s + '.ocp'
            if schema_config not in file_names:
                if inter:
                    print("The following schema is missing a RedGate OCP configuration file in 'bonanza' mode: %s" % schema_config)
                missing_schemas.append(schema_config)

        if len(missing_schemas) > 0:   
            missing_schema_logger.error("The following schema is missing a RedGate OCP configuration file in 'bonanza' mode: %s" % missing_schemas)
                
        if inter:
            print("[+] These are all the schemas missing: %s" % missing_schemas)

        awesome_logger.debug("[+] These are all the schemas missing: %s" % missing_schemas)

        #done with checking if schema files are present

        #Try to dynamically configure the schema filters
        #first get the relevant rows
        if inter:
            print("Going to try and filter the OCP configuration files.")

        awesome_logger.debug("Going to try and filter the OCP configuration files.")
        
        try:
            if inter:
                print("The object_list variable = %s " % str(object_list))
                slowdown()

            awesome_logger.debug("The object_list variable = %s " % str(object_list))

            if O_LIST != None:
                if inter:
                    print("[+] O_LIST = %s" % str(O_LIST))
                awesome_logger.debug("[+] O_LIST = %s" % str(O_LIST))
                import RGFilter
                #find the rows with the "all_ocps" call from OBJECT_LIST.csv then update with the filters
                important_rows = RGFilter.all_ocps(ocp_directory=dco_dir, object_list=object_list,interactive=inter) #in this case 'dco_dir' is the ocp_dir
                awesome_logger.debug("This is in the important rows: %s" % important_rows)
                RGFilter.update_filters(important_rows, schema_files=dco_dir, interactive=inter) #The 'dco_dir' actually contains the ocp_dir in this case
                if inter:
                    print("Done applying filters to OCP configuration files.")

                awesome_logger.debug("Done applying filters to OCP configuration files.")
        except Exception as e:
            print("There was a problem creating the OCP filters for RG")
            awesome_logger.debug("There was a problem creating the OCP filters for RG")
            print("Please see the following error/exception: %s." % str(e))
            awesome_logger.debug("Please see the following error/exception: %s." % str(e))

        

        
        

        
    
    if inter:
        print("Need to check if uber important global variable was set (DUMP_DIR)")
        slowdown()

    awesome_logger.debug("Need to check if uber important global variable was set (DUMP_DIR)")
        
    
    #'DUMP_DIR' - This variable is set in the "batchConfig()" function and in this function 0_o.
    try:
        if len(DUMP_DIR) <= 0:
            if inter:
                print("The DUMP_DIR global variable has not been assigned a value. Exiting program. Error.")
            awesome_logger.debug("In Bonanza Mode - The DUMP_DIR global variable has not been assigned a value. Exiting program. Error.")
            exit()
        else:
            if inter:
              print("'DUMP_DIR' variable set.")
              print("The value of 'DUMP_DIR' is: %s" % DUMP_DIR)
            
            awesome_logger.debug("In Bonanza Mode - DUMP_DIR variable set! :)")
    except Exception as e:
        print("Exception thrown: %s" % str(e))
        awesome_logger.debug("Exception thrown: %s" % str(e))

    

    if inter:
        slowdown()

    if vertical_direction and not schema:
        if inter:
            print("The 'getUp(dump_dir)' function will be called at this point for DML.")
        awesome_logger.debug("The 'getUp(dump_dir)' function will be called at this point for DML.")
        getUp(DUMP_DIR)
        if inter:
            print("The getUp function was called for DML.")
        awesome_logger.debug("The getUp function was called for DML.")
    elif not vertical_direction and not schema:
        if inter:
            print("The 'getDown(dump_dir)' function will be called at this point for DML.")
        awesome_logger.debug("The 'getDown(dump_dir)' function will be called at this point for DML.")
        getDown(DUMP_DIR)
        if inter:
            print("The getDown function was called for DML.")
        awesome_logger.debug("The getDown function was called for DML.")
    elif vertical_direction and schema:
        getUp(dco_dir)
        if inter:
            print("The getUp(dco_dir) function was called for DDL.")
        awesome_logger.debug("The getUp(dco_dir) function was called for DDL.")
    elif not vertical_direction and schema:
        getDown(dco_dir)
        if inter:
            print("The getDown(dco_dir) function was called for DDL.")
        awesome_logger.debug("The getDown(dco_dir) function was called for DDL.")

    
        
    if inter:
        slowdown()
    
    #Generate the diff scripts 
    #create the file name based on up/down and schema or data
    if inter:
        print("determining file name...")

    awesome_logger.debug("determining file name...")
    if vertical_direction and not schema:
        d_dump = 'upgrade_bonanza_dml'
    elif not vertical_direction and not schema:
        d_dump = 'downgrade_bonanza_dml'
    elif vertical_direction and schema:
        d_dump = 'upgrade_bonanza_ddl'
    elif not vertical_direction and schema:
        d_dump = 'downgrade_bonanza_ddl'

   
    
    if inter:
        print("This file name chosen is: %s " % d_dump)
        print("")
        print("generating the diff scripts with the following arguments to 'generateDiffScripts':")
        print("DUMP_DIR = %s" % DUMP_DIR)
        print("diff_dump = %s" % d_dump)
        print("schema_compare = %s" % schema)
        if schema:
            print("ocp_dir = %s" % dco_dir)
        else:
            print("dco_dir = %s" % dco_dir)
    
        slowdown()

    awesome_logger.debug("This file name chosen is: %s " % d_dump)
    awesome_logger.debug("")
    awesome_logger.debug("generating the diff scripts with the following arguments to 'generateDiffScripts':")
    awesome_logger.debug("DUMP_DIR = %s" % DUMP_DIR)
    awesome_logger.debug("diff_dump = %s" % d_dump)
    awesome_logger.debug("schema_compare = %s" % schema)
    if schema:
        awesome_logger.debug("ocp_dir = %s" % dco_dir)
                
    else:
        awesome_logger.debug("dco_dir = %s" % dco_dir)

   

    #disable the constraints in the database to create the diff scripts for DML
    if not schema:
        if inter:
            print("First we need to disable circular constraints.")
            slowdown()
        print("Disabling circular foreign key constraints now!")
        awesome_logger.debug("Disabling circular foreign key constraints now!")
        ConnectToOracle.toggle_circular_constraints(enable=False)
        print("Circular foreign key constraints disabled.")
        awesome_logger.debug("Circular foreign key constraints disabled.")

    

   
   
    if not schema:
        if inter:
            print("Calling the CrazyDiamond.generateDiffScripts() for DML comparison")
        awesome_logger.debug("Calling the CrazyDiamond.generateDiffScripts() for DML comparison")
        CrazyDiamond.generateDiffScripts(DUMP_DIR, diff_dump=d_dump, schema_compare=schema)
    else:
        if inter:
            print("Calling CrazyDiamond.generateDiffScripts for DDL comparison")
        awesome_logger.debug("Calling CrazyDiamond.generateDiffScripts for DDL comparison")
        if O_LIST == None:
            filters = False
            awesome_logger.debug("[+] Not using filters for DDL comparison.")
        else:
            filters = True
            awesome_logger.debug("[+] Filters engaged for DDL comparison")
            
        CrazyDiamond.generateDiffScripts(dco_dir, diff_dump=DUMP_DIR + os.sep + d_dump, schema_compare=schema, filters=False)

    
    
    #Re-enable the constraints in the database after creating the diff scripts for DML
    if not schema:
        if inter:
            print("We need to re-enable the circular constraints now.")
            slowdown()
        awesome_logger.debug("Turning circular foreign key constraints back on.")
        print("Turning circular foreign key constraints back on.")            
        ConnectToOracle.toggle_circular_constraints()
        print("Circular foreign key constraints back on.")
        awesome_logger.debug("Circular foreign key constraints back on.")
        
   
    #update the ap_versions table here - only execute this code for DML not schema (DDL) :)
    
    
    if not schema and "RITE_COMMON.dco" not in missing_dco:
        awesome_logger.info("updating 'rite_common.ap_versions' table programmatically")
        if vertical_direction:
            vert = "UPGRADE"
        else:
            vert = "DOWNGRADE"

        awesome_logger.info(f"[+] This is a {vert} operation.")

        if inter:
            print("[+] Updating the 'ap_versions' table rows and deleting 'ap_versions' delete statements now in RC DML sync/diff scripts.")
            slowdown()

        awesome_logger.debug("[+] Updating the 'ap_versions' table rows and deleting 'ap_versions' delete statements now in RC DML sync/diff scripts.")
                             

        p = pathlib.Path(DUMP_DIR + os.sep + d_dump + os.sep + "RITE_COMMON__diff_script.sql")
        if p.exists():
            apv.rc_apv(DUMP_DIR + os.sep + d_dump + os.sep + "RITE_COMMON__diff_script.sql", vert)
        else:
            awesome_logger.debug("[-] The RITE_COMMON diff script does not exist here: %s " % DUMP_DIR + os.sep + d_dump + os.sep + "RITE_COMMON__diff_script.sql")
        
        if p.exists():
            if inter:
                print("[+] Updating 'ap_versions' in rite_common sync/diff DML scripts complete.")
                slowdown()
            awesome_logger.debug("[+] Updating 'ap_versions' in rite_common sync/diff DML scripts complete.")

    
    
    #Sanitize the diff scripts
    path_ = DUMP_DIR + os.sep + d_dump
    if inter:
        print("The function to remove the junk from the scripts should be called at this point.")
        slowdown()
    awesome_logger.debug("The function to remove the junk from the scripts should be called at this point.")
    
    if inter:
        print('''The "removeWrapper('%s')" function will need to be called.''' % path_)
    awesome_logger.debug('''The "removeWrapper('%s')" function will need to be called.''' % path_)
    removeWrapper(path_)
    

    if inter:
        print("'removeWrapper()' function complete.")
        slowdown()
    awesome_logger.debug("'removeWrapper()' function complete.")

   

    #need to add code to remove the previous scripts that are not cleaned...
    if inter:
        deleteDirtyFiles(DUMP_DIR + os.sep + d_dump, inter=True) #call the function in interactive mode to step through each file deletion
    else:
        deleteDirtyFiles(DUMP_DIR + os.sep + d_dump)


    #remove the ALTER  COMPILE statements and the RC.CONSTS$ package specification and package body - These functions do not alter the file names - danger
    if schema:
        awesome_logger.debug("Attemping to remove ALTER COMPILE statements from diff scripts.")
        RemoveJunkFromScript.rmCompile(DUMP_DIR + os.sep + d_dump)
        awesome_logger.debug("rmCompile() call to remove ALTER COMPILE statements complete.")
        #awesome_logger.debug("Attempting to remove REVOKE statements from schema diff scripts.")
        #RemoveJunkFromScript.rmRevoke(DUMP_DIR + os.sep + d_dump)
        #awesome_logger.debug("rmRevoke() call to remove REVOKE statements complete.")

        #find out if rite_common is present then remove the consts$ package if so
        find_rc_ddl = pathlib.Path(DUMP_DIR + os.sep + d_dump)
        rc_file = find_rc_ddl.glob("RITE_COMMON_diff_script.sqlClean.sql")
        rc_file = list(rc_file)
        if rc_file: #this should fire only if rc_file has more than zero elements. 
            #make sure the consts$ package is not included in final diff scripts
            RemoveJunkFromScript.rmConsts(rc_file[0]) #just pass the first, and hopefully only, element which should be the path and file of RC

    if not schema:
        #remove the COMPILE statements from Red-gate generated scripts
        awesome_logger.debug("Starting the process to remove COMMIT statements from DML diff scripts.")
        RemoveJunkFromScript.rmCommit(DUMP_DIR + os.sep + d_dump)
        awesome_logger.debug("rmCommit() call to remove COMMIT statements complete.")

    
    
    #Create the deployment script
    
    if inter:
        print("Now the deployment script should be created.")
        
        print("This is the function call MetaSQL.heyHoLetsGo(%s)" % path_)
        slowdown()

    awesome_logger.debug("Now the deployment script should be created.")
    awesome_logger.debug("This is the function call MetaSQL.heyHoLetsGo(%s)" % path_)
        
    deployment_script = MetaSQL.heyHoLetsGo(path_)

    
   
    
    #deploy the deployment_script
    if inter:
        print("Deploying the code to the database.")
        slowdown()

    awesome_logger.debug("Deploying the code to the database.")

    
   
    #Actually deploy the code and keep a log with 'deployment_log' which is passed to the error_report function
    
    deployment_log = '' #need this variable for the return value of 'connectFor...' functions below
    if vertical_direction: #upgrade
        #do this:
        deployment_log = ConnectToOracle.connectForAUpgrade(deployment_script)
    else: #downgrade
        #do this
        deployment_log = ConnectToOracle.connectForADowngrade(deployment_script)

    
    
    if inter:
        print("The deployment is complete.")
        print("Generating error report.")
        slowdown()

    awesome_logger.debug("The deployment is complete.")
    awesome_logger.debug("Generating error report.")

   
    
    #create the error report
    errors = ErrorReport.error_report(deployment_log)
    
    if inter:
        print("Error report created.")

    awesome_logger.debug("Error report created.")
    awesome_logger.debug("[!] Number of ORAs: %d" % errors[0])
    awesome_logger.debug("[!] Total errors: %d" % errors[-1])

    if rdiff:
        if inter:
            print("[+] Re-Diffing...")
            
        awesome_logger.debug("[+] Re-Diffing...") 
        
        #disable the constraints in the database only for the DML deployment
        if not schema:
            if inter:
                print("First we need to disable circular constraints again for the re-diff.")
                slowdown()
            awesome_logger.debug("First we need to disable circular constraints again for the re-diff.")
            print("Disabling circular foreign key constraints now for re-diff!")
            awesome_logger.debug("Disabling circular foreign key constraints now for re-diff!")
            ConnectToOracle.toggle_circular_constraints(enable=False)
            print("Circular foreign key constraints knocked out for re-diff.")
            awesome_logger.debug("Circular foreign key constraints knocked out for re-diff.")
           
          
        #Regenerate the the diff scripts to see if anything has changed 
        if not schema:
            if inter:
                print("Calling the CrazyDiamond.generateDiffScripts()again for DML; to make sure scripts are OK.")
            awesome_logger.debug("Calling the CrazyDiamond.generateDiffScripts()again for DML; to make sure scripts are OK.")                
            CrazyDiamond.generateDiffScripts(DUMP_DIR, diff_dump=DUMP_DIR + os.sep + d_dump, schema_compare=schema,re_diff=True)
        else:
            if inter:
                print("Calling CrazyDiamond.generateDiffScripts() again for DDL comparison; to make sure scripts are OK.")
            awesome_logger.debug("Calling CrazyDiamond.generateDiffScripts() again for DDL comparison; to make sure scripts are OK.")         
            CrazyDiamond.generateDiffScripts(dco_dir, diff_dump=DUMP_DIR + os.sep + d_dump, schema_compare=schema, re_diff=True)



        #Re-enable the constraints in the database after the DML deployment
        if not schema:
            if inter:
                print("We need to re-enable the circular constraints now after the re-diff.")
                slowdown()
            awesome_logger.debug("We need to re-enable the circular constraints now after the re-diff.")
            print("Turning circular foreign key constraints back on after the re-diff.")
            awesome_logger.debug("Turning circular foreign key constraints back on after the re-diff.")
            ConnectToOracle.toggle_circular_constraints(enable=True)
            print("Circular foreign key constraints back on after re-diff.")
            awesome_logger.debug("Circular foreign key constraints back on after re-diff.")
            


        #clean the re-diff scripts
        path_ = DUMP_DIR + os.sep + d_dump
        if inter:
            print("The function to remove the junk from the scripts should be called at this point. This time for the re-diff scripts.")
            slowdown()
        awesome_logger.debug("The function to remove the junk from the scripts should be called at this point. This time for the re-diff scripts.")
        
        if inter:
            print('''The "removeWrapper('%s', rediff=True)" function will need to be called.''' % path_)
        awesome_logger.debug('''The "removeWrapper('%s', rediff=True)" function will need to be called.''' % path_)
        removeWrapper(path_, rediff=True)

        #clean the directory of RE-DIFF.sql scripts that were not cleaned of "sys buffer gremlins"
        if inter:
            deleteDirtyFiles(DUMP_DIR + os.sep + d_dump, inter=True) #call the function in interactive mode to step through each file deletion
        else:
            deleteDirtyFiles(DUMP_DIR + os.sep + d_dump)
            
        #now I could write code to check the length of the file and determine if the file ends with
        #a commit statement. All blank DML sync scripts have 15 lines and end with a "COMMIT;" as of now.
        #This could be changed in the configuration of RedGate (RG) though. The end-user could simply
        #compare the new diff scripts that are generated. SCO blanks have a length of 5 lines.
        #A simple count for the length of the file in terms of lines of text inside it maybe an effect check. 

        #only see if the 'cleaned' re-diff files are empty
        rediff_files = glob.glob(DUMP_DIR + os.sep + d_dump + os.sep + "*_RE-DIFF.sqlClean.sql") # get the directory where the diff scripts are
        
        if schema:
            for f in rediff_files:
                length = ReDiff.file_length(f)
                if length == 0:
                    pass
                elif length != 5:
                    print("This file may have a problem %s" % f)
                    awesome_logger.debug("This file may have a problem %s" %f)
                
        else:
            for f in rediff_files:
                length = ReDiff.file_length(f)
                if length == 0:
                    pass
                elif length != 15:
                    print("This file may have a problem %s" %f)
                    awesome_logger.debug("This file may have a problem %s" %f)


    if not inter and not gui:
        t.join(timeout=1) #Stop the ASCII spinner thread
            
    
    
    
    awesome_logger.debug("[+] Bonanza mode complete!")
    print("\n")
    print("[+] Bonanza mode complete!")
   



if __name__ == "__main__":
    groupMode = False
    v_4_verbose = False
    schema_compare = False
    execute = False
    bonanza = True
    csv_file = ''
    dco_file = ''
    dco_dir = ''
    dump_dir = ''
    config_loot = ''
    direction = True
    sco_compare = False
    inter = False
    rdiff = False
    pdb1_name = ''
    pdb2_name = ''
    robot_mode = False

    awesome_logger.debug("=" * 99)
    awesome_logger.debug("Program called like so: %s" % str(sys.argv[:]))
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], 'ic:d:g:hvrsx', ['instructions', 'robot', 'direction=',
                                                                    'directionDir=', 'chdir=',
                                                                    'chdirBatchMode=', 'dumpDir=',
                                                                    'configLoot=', 'remove=', 'removeDir=',
                                                                      'deploymentScript=', 'up=',
                                                                      'down=', 'BonanzaOff', 'high',
                                                                      'low', 'interactive', 'debug',
                                                                     'whiteRabbit', 'setObjectList=', 'rediff',

                                                                    'help', 'csv=', 'dco=', 'group=', 'pdb1=', 'pdb2='])

        for opt, arg in opts:

            
            if opt in ('--BonanzaOff'):
                bonanza = False
            elif opt in ('-h'):
                instructions()
                iNeedHelp()
            elif opt in ('--interactive'): #interactive mode
                inter = True
            elif opt in ('--whiteRabbit'): #only works with cmd.exe or powershell probably - windows thing
                wr = threading.Thread(target=whiteRabbit)
                #wr.daemon = True
                wr.start()
            elif opt in ('--debug'): #debug mode
                DEBUG = True
                awesome_logger.debug('DEBUG mode engaged!')
            elif opt in ('--high'):
                direction = True #upgrade
            elif opt in ('--low'):
                direction = False #downgrade
            elif opt in ('-i', '--instructions'):
                instructions()
            elif opt in ('--remove'):
                RemoveJunkFromScript.rmJunk(arg)
            elif opt in ('--deploymentScript'):
                MetaSQL.heyHoLetsGo(arg)
            elif opt in ('--removeDir'):
                directory = arg
                removeWrapper(directory)
            elif opt in ('-c', '--csv'):
                csv_file = arg
            elif opt in ('-d', '--dco'):
                dco_file = arg
            elif opt in ('-g', '--group'):
                groupMode = True
                dco_dir = arg
            elif opt in ('--up'):
                directory = arg
                getUp(directory)
            elif opt in ('--down'):
                directory = arg
                getDown(directory)
            elif opt in ('-x'):
                execute = True
            elif opt in ('-s'):
                schema_compare = True
            elif opt in ('-v', '--verbose'):
                v_4_verbose = True
            elif opt in ('--dumpDir'):
                dump_dir = arg
            elif opt in ('--configLoot'):
                config_loot = arg
            elif opt in ('--help'):
                instructions()
                iNeedHelp()
            elif opt in ('--chdir'):
                ChangeDirection.ChangeDirection(arg)
            elif opt in ('--chdirBatchMode'):
               directory = arg
               os.chdir(directory) #change directory to where the DCO files are
               print("The current directory is: %s" % os.getcwd())
               files = [glob.glob(e) for e in ["*.dco", "*.ocp"]] #put all the files that end with '.dco' into this list 'files'
               print("This is in the 'files' list: %s" % files)
               for f in files: #loop through the files and detect direction
                   for f in f:
                       print("\n")
                       print("----")
                       print("Currently processing this file: %s" % str(f))
                       ChangeDirection.ChangeDirection(f)
                       print("----")
            elif opt in ('--direction'):
                Direction.detectDirection(arg)
            elif opt in ('--directionDir'):
               directory = arg
               os.chdir(directory) #change directory to where the DCO files are
               print("The current directory is: %s" % os.getcwd())
               files = [glob.glob(e) for e in ["*.dco", "*.ocp"]] #put all the files that end with '.dco' into this list 'files'
               print("This is in the 'files' list: %s" % files)
               for f in files: #loop through the files and detect direction
                   for f in f:
                       print("\n")
                       print("----")
                       print("Currently processing this file: %s" % str(f))
                       Direction.detectDirection(f)
                       print("----")
            elif opt in ('--setObjectList'):
                setOList(arg)
                if inter:
                    print("Setting the O_LIST variable to: %s" % arg)
                    print("O_LIST = " + O_LIST)
                    slowdown()
            elif opt in ('--rediff'):
                rdiff=True
                if inter:
                    print("Setting 'rdiff' to True.")
                    print("This will enable re-diffs.")
            elif opt in ('--pdb1'):
                pdb1_name = arg
                awesome_logger.debug(f"pdb1 string passed in from the command line is: {pdb1_name}")
            elif opt in ('--pdb2'):
                pdb2_name = arg
                awesome_logger.debug(f"pdb2 string passed in from the command line is: {pdb2_name}")
            elif opt in ('--robot'):
                robot_mode = True
                
                
                

    except getopt.GetoptError as shatner:
        print("There was some type of error running the program. The error is: %s" % shatner)
        print("Please check out this help screen.")
        instructions()
        iNeedHelp()

    #This section calls the main function of the program to up/down DML/DDL at once depending on args passed in to program - very automated man
    if (bonanza == True) and (execute == False) and (groupMode == True) and (len(csv_file) > 0):
        if robot_mode and pdb1_name and pdb2_name:
            Bonanza(csv_file, dco_dir, vertical_direction=direction, schema=schema_compare, inter=inter, object_list=O_LIST, rdiff=rdiff, pdb1=pdb1_name, pdb2=pdb2_name, robomode=robot_mode)
        else:
            Bonanza(csv_file, dco_dir, vertical_direction=direction, schema=schema_compare, inter=inter, object_list=O_LIST, rdiff=rdiff)
            

    #This section will create diff scripts
    if (execute):
        print("[+] The execute mode has been enabled.")
        print("The schemaCompare variable = %s " % schema_compare)
        print("The directory to dump the diff scripts is: %s " % dump_dir)
        print("The directory with all of the DCO/OCP configuration files is: %s " % config_loot)
        CrazyDiamond.generateDiffScripts(config_loot, dump_dir, schema_compare)
        
    #This section will create a DCO file programmatically for a single schema
    if len(csv_file) > 0 and len(dco_file) > 0 and (groupMode == False):
        singleConfig(csv_file, dco_file, dump_dir, v_4_verbose)

    #This section will create a group of configuration files, DCO, for a directory of DCO files
    if len(csv_file) > 0 and (groupMode == True) and (bonanza != True):
        print("Creating the configuration files in batch mode.")
        batchConfig(csv_file, dco_dir)
       
        

    
    
    
