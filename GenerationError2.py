import ConnectToOracle
import CrazyDiamond
from awesome import slowdown
import awesome
import ReDiff
import argparse
import logging
import time
import sys
import pathlib
import os

#logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

gen_error_logger = logging.getLogger('generation_error-log')
if not gen_error_logger.handlers:
    gen_error_fh = logging.FileHandler('generation_error.log')
    gen_error_logger.setLevel(logging.DEBUG)
    gen_error_fh.setFormatter(formatter)
    gen_error_logger.addHandler(gen_error_fh) #add the file handler to the logger


def bornToDeploy(start_dir, deployment_script, rediff_hq, inter=True):
    """ """
   

    os.chdir(rediff_hq) # this is the dir where the deployment script is. Change here before executing the script.

    if inter:
        print("[!] Directory changed to the following dir: %s " % rediff_hq)
        gen_error_logger.info('[!] Directory changed to the following dir: %s ' % rediff_hq)
        slowdown()
                          
    #deploy the deployment_script
    if inter:
        print("Deploying the code to the database to see if errors were fixed.")
        slowdown()

    if inter:
        print("[!] The data type of 'deployment_script.name' is: %s" % str(type(deployment_script.name)))
        slowdown()
        print("")
        print("[!] The deployment script is: %s" % deployment_script.name)
        slowdown()
    #Actually deploy the code and keep a log with 'deployment_log' which is passed to the error_report function

    deployment_log = '' #need this variable for the return value of 'connectFor...' functions below
    if going_up: #upgrade
        #do this:
        deployment_log = ConnectToOracle.connectForAUpgrade(deployment_script.name)
    else: #downgrade
        #do that
        deployment_log = ConnectToOracle.connectForADowngrade(deployment_script.name)

    if inter:
        print("The re-diff error check deployment is complete.")
        slowdown()
       
    gen_error_logger.info("Code deployed to the database.")

    if inter:
        print("[!] Changing back to directory the script started in. Which is: %s" % start_dir)
    gen_error_logger.info("[!] Changing back to directory the script started in. Which is: %s" % start_dir)
        
    os.chdir(start_dir)


def generation_error(deployment_script, csv="", dco="", rediff_hq="a directory path to re-diffs",
                     ocp_dir="path to ocp configs", going_up=True, schema=False, inter=False, redeploy=True):
    """This should handle the 'diff generation error handling' from
    step 9 to ll from this page: http://hostname.company.local/foo/foo-db/wikis/diff-generation-error-handling
    9.)  Deploy fixed diff/sync scripts via the deployment script overwriting previous deployment log
    10.) Re-Diff - overwrite the previous re-diff scripts
    11.) Run report on re-diffs
    """

    
    start_dir = os.getcwd()
    start_dir = pathlib.Path(start_dir).absolute()

    if inter:
        print("[!] The starting directory of the program is: %s " % start_dir)
        gen_error_logger.info("[!] The starting directory of the program is: %s " % start_dir)
        slowdown()

    type_of_script = "typecasted"
    if going_up:
        type_of_script = "UPGRADE"
    else:
        type_of_script = 'DOWNGRADE'

    

    #deploy function call here
    if redeploy:
        gen_error_logger.info("Deploying %s deployment script to the database now." % type_of_script)
        bornToDeploy(start_dir, deployment_script, rediff_hq, inter=inter)
    
    print("[+] Re-Diffing...")
    gen_error_logger.info("[+] Re-Diffing now...")

    

    
    if inter:
        print("Getting the location of the DUMP DIR.")
        
    gen_error_logger.info("Getting the location of the DUMP DIR.")
    DUMP_DIR = awesome.createDumpDir() #creates the dump_dir one dir back from where script executed

    #figure out the folder name under the 'DUMP_DIR' - this is where the re-re-diff scripts are written
    if going_up and not schema:
        d_dump = 'upgrade_bonanza_dml'
    elif not going_up and not schema:
        d_dump = 'downgrade_bonanza_dml'
    elif going_up and schema:
        d_dump = 'upgrade_bonanza_ddl'
    elif not going_up and schema:
        d_dump = 'downgrade_bonanza_ddl'

    gen_error_logger.info("The name of the folder for the directory is: %s." % d_dump)
    
    if not schema:
        #generate the DCO files for this release again
        gen_error_logger.info("Generating configuration files for the DML comparisons.")
        p_csv = pathlib.Path(csv) #change this to a pathlib object that Python3 can better handle
        p_dco = pathlib.Path(dco)

        if inter:
            print("[!] Generating configuration files for the DML comparisons.")
            print("p_csv = %s" % p_csv)
            print("p_dco = %s" % p_dco)
            slowdown()
            
        awesome.batchConfig(csv_file=p_csv, dco_dir=p_dco) #creates a folder 1 directory back relative to where executed 0_o
        gen_error_logger.info("Generating DCO config for DML comparisons complete.")
        if inter:
            print("Generating DCO config for DML comparisons complete.")


    #disable the constraints in the database only for the DML deployment
    if not schema:
        if inter:
            print("First we need to disable circular constraints for the re-diff.")
            slowdown()
        print("Disabling circular foreign key constraints now for re-diff!")
        gen_error_logger.info("Disabling circular foreign key constraints now for re-diff!")
        ConnectToOracle.disableCircularConstraints()
        print("Circular foreign key constraints knocked out for re-diff.")
        gen_error_logger.info("Circular foreign key constraints knocked out for re-diff.")

    
    gen_error_logger.info("""[!] Go and get a glass of water. The diff scripts are regenerating now
                          at the following location: %s.""" % rediff_hq)
    if inter:
        print("""[!] Go and get a glass of water. The diff scripts are regenerating now
                          at the following location: %s.""" % rediff_hq)
    
    
    
    #Regenerate the the diff scripts to see if anything has changed 
    if not schema:
        if inter:
            print("Calling the CrazyDiamond.generateDiffScripts()again for DML; to make sure scripts are OK.")
        CrazyDiamond.generateDiffScripts(DUMP_DIR, diff_dump=rediff_hq, schema_compare=schema,re_diff=True)
    else:
        if inter:
            print("Calling CrazyDiamond.generateDiffScripts() again for DDL comparison; to make sure scripts are OK.")
        CrazyDiamond.generateDiffScripts(ocp_dir, diff_dump=rediff_hq, schema_compare=schema, re_diff=True)

    gen_error_logger.info("RE_DIFF generation complete.")
    print("RE_DIFF generation complete.")

    #Re-enable the constraints in the database after the DML deployment
    if not schema:
        if inter:
            print("We need to re-enable the circular constraints now after the re-diff.")
            slowdown()
        print("Turning circular foreign key constraints back on after the re-diff.")            
        ConnectToOracle.enableCircularConstraints()
        print("Circular foreign key constraints back on after re-diff.")
        
    #now I could write code to check the length of the file and determine if the file ends with
    #a commit statement. All blank DML sync scripts have 15 lines and end with a "COMMIT;" as of now.
    #This could be changed in the configuration of RedGate (RG) though. The end-user could simply
    #compare the new diff scripts that are generated. SCO blanks have a length of 5 lines.
    #A simple count for the length of the file in terms of lines of text inside it maybe an effective check. 
    
    if inter:
        print("[!] Going to calculate the differences between the re-diffs and the diffs now. This is the great smurf war your history teacher bored you with.")
    
    gen_error_logger.info("[!] Going to calculate the differences between the re-diffs and the diffs now. This is the great smurf war your history teacher bored you with.")

    #all_re_diffs = rediff_hq / "*_RE-DIFF.sql"
    #print("[!] The new path to search for RE-DIFFs is: %s" % all_re_diffs)
    #slowdown()
    
    rediff_files = rediff_hq.rglob("*_RE-DIFF.sql") # get the directory where the diff scripts are
    rediff_files = list(rediff_files) #change the generator to a list
    if inter:
        print("Found the following _RE-DIFF.sql files: ")
        for files in rediff_files:
            print(files)
        slowdown()
        print("Ending printing long list of files found that end with '_RE-DIFF.sql'.")

    if inter:
        print("Going to check the RE_DIFF files to see if they match the initial diffs.")

    gen_error_logger.info("Going to check the RE_DIFF files to see if they match the initial diffs.")

    if schema:
        for f in rediff_files:
            #print("The type of f is: %s" % type(f.read_text()))
            #print("f = %s" % str(f.read_text()))
            #print("f = %s" % repr(f))
            #string_f = f.read_text()
            string_f = str(f.resolve()) #change the pathlib object to a string
            #print('string_f = %s' % repr(string_f))
            
            length = ReDiff.file_length(string_f)
            #print("The length is: %d" % length)
            if length == 0:
                pass
            elif length != 5:
                print("[!] This file may have a problem %s" % f)
                gen_error_logger.debug("[!] This file may have a problem %s" %f)
            
    else:
        for f in rediff_files:
            
            string_f = str(f.resolve()) #change the pathlib object to a string
            length = ReDiff.file_length(string_f)
            
            if length == 0:
                pass
            elif length != 15:
                print("[!] This file may have a problem %s" %f)
                gen_error_logger.debug("[!] This file may have a problem %s" %f)
            

    
    gen_error_logger.debug("[+] Error check complete!")
    print("[+] Error check complete!")

    

if __name__ == "__main__":
    
    gen_error_logger.info("""
                                 _   _                                        
                                | | (_)                                       
  __ _  ___ _ __   ___ _ __ __ _| |_ _  ___  _ __     ___ _ __ _ __ ___  _ __ 
 / _` |/ _ \ '_ \ / _ \ '__/ _` | __| |/ _ \| '_ \   / _ \ '__| '__/ _ \| '__|
| (_| |  __/ | | |  __/ | | (_| | |_| | (_) | | | | |  __/ |  | | | (_) | |   
 \__, |\___|_| |_|\___|_|  \__,_|\__|_|\___/|_| |_|  \___|_|  |_|  \___/|_|   
  __/ |                                                                       
 |___/                                                                         


    """)
    gen_error_logger.info("GenerationError starting up at: %s" % time.asctime())
    gen_error_logger.info("Program called with the following arguments: %s" % sys.argv[:])

    #for some reason options that do not require arguments need to precede the arguments
    #that require arguments for the script to work as designed. So --going_up before --dscript, etc.
    error_parser = argparse.ArgumentParser(prog="GenerationError", description="Re-diffing re-diffs to see if deployment errors are resolved.",
                                           epilog='"All the king\'s horses and all the king\'s men could not put humpty-dumpty\'s head together again."')

   
    error_parser.add_argument('--dscript',
                             metavar = "deployment_script.sql",
                             help="Path to the deployment_script.sql and also the filename", required=True)

    error_parser.version = "Generation Error Version 1.0"
    error_parser.add_argument('--csv', metavar="SDATA_LIST.csv", help="Path to and including SDATA_LIST.csv")
    error_parser.add_argument('--dco', help="The RedGate DCO configuration files for DML. Not a specific file, the dir.")    
    error_parser.add_argument('--ocp', help="The RedGate OCP configuration file location. Not a specific file the dir holding them all.")
    error_parser.add_argument('--going_up', help="specify if this is an upgrade or downgrade. Using this argument means upgrade not using this argument means downgrade.", action='store_true')
    error_parser.add_argument('--schema', action="store_true", help="If this is specified this is for Schema comparisons if not specified then the comparison is DML.")
    error_parser.add_argument('--inter', action="store_true", help="If this is specified interactive mode is enabled.")
    error_parser.add_argument('--no-deploy', dest='nein', action="store_false", help="Use this as one of the first commands to not re-deploy the code")
    args = error_parser.parse_args() #see what the end-user passed in
    
    deployment_script = args.dscript #get the deployment script

    d = pathlib.Path(deployment_script) # change the path passed in to something more readable for Python3

    if not d.is_dir(): #find out if this is a directory
        print("") #print empty space for readability
        print("[*] The deployment script appears to be a file and not a directory.")
        gen_error_logger.info("[*] The deployment script appears to be a file and not a directory.")

    rediff_location = d.absolute().parent #get the directory that the deployment script is in. This is where all the 're-diff' files are.

    print("[*] The 'rediff_location' based on the deployment script is: %s" % rediff_location)
    gen_error_logger.info("[*] The 'rediff_location' based on the deployment script is: %s" % rediff_location)
    

    

    if args.inter:
        print("\n")
        if args.csv:
            print("You entered this for the 'csv' arg: %s" % args.csv)
        if args.dco:
            print("You entered this for the 'dco' arg: %s" % args.dco)
        if args.ocp:
            print("You entered this for the 'ocp' arg: %s" % args.ocp)
        if args.going_up:
            print("'going_up' = %s" % args.going_up)
        if args.schema:
            print("'schema' = %s" % args.schema)
        if args.inter:
            print("'inter' = %s" % args.inter)
        if deployment_script:
            print("You entered this for the deployment script location: %s" % deployment_script)
        if args.nein or not args.nein:
            print("'redeploy' = %s" % args.nein)

    #change the DCO, OCP, and CSV paths into readable paths for Python3 with pathlib
    if args.dco:
        dco_p = pathlib.Path(args.dco)
        if not dco_p.is_dir():
            print("[!] The DCO path you gave me is not a directory. Exiting.")
            gen_error_logger.info("[!] What was passed in for the DCO path is not a directory.")
            exit()

    if args.ocp:
        ocp_p = pathlib.Path(args.ocp)
        if not ocp_p.is_dir():
            print("[!] The OCP path you gave me is not a directory. Exiting.")
            gen_error_logger.info("[!] What was passed in for the OCP path is not a directory.")
            exit()

    if args.csv:
        csv_p = pathlib.Path(args.csv)
        if not csv_p.is_file():
            print("[!] The CSV file you gave is not a file. Program exiting.")
            gen_error_logger.info("[!] The CSV file you gave is not a file. Program exiting.")
            exit()
            
            
    
    
    #upgrade DDL re-diff
    if deployment_script and args.going_up and args.ocp and args.schema:
        gen_error_logger.info("Starting UPGRADE DDL re-diff process with the following args: %s" % args)
        print("[+] Upgrade DDL detected.")
        generation_error(deployment_script=d, schema=True, going_up=args.going_up,
                        ocp_dir=ocp_p, rediff_hq=rediff_location, inter=args.inter, redeploy=args.nein)

    #downgrade DDL re-diff
    if deployment_script and args.ocp and args.schema and not args.going_up:
        print("[-] Downgrade DDL detected.")
        gen_error_logger.info("Starting a DOWNGRADE DDL re-diff process with the following args: %s" % args)
        generation_error(deployment_script=d, schema=True, going_up=args.going_up,
                        ocp_dir=ocp_p, rediff_hq=rediff_location, inter=args.inter, redeploy=args.nein)

    #upgrade DML re-diff
    if deployment_script and args.dco and not args.schema and args.going_up and args.csv:
        print("[+] Upgrade DML detected.")
        gen_error_logger.info("Starting UPGRADE DML re-diff process with the following args: %s" % args)
        generation_error(deployment_script=d, schema=args.schema, going_up=args.going_up,
                        dco=dco_p, csv=args.csv, rediff_hq=rediff_location, inter=args.inter, redeploy=args.nein)
            
    #downgrade DML re-diff
    if deployment_script and args.dco and not args.schema and not args.going_up and args.csv:
        gen_error_logger.info("Starting DOWNGRADE DML re-diff process with the following args: %s" % args)
        print("[-] Downgrade DML detected.")
        generation_error(deployment_script=d, schema=args.schema, going_up=args.going_up,
                        dco=dco_p, csv=args.csv, rediff_hq=rediff_location, inter=args.inter, redeploy=args.nein)
    
    print("[*] Program complete.")
    gen_error_logger.info("[*] GenerationError stopping at: %s" % time.asctime())
    
