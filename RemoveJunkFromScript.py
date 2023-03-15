
"""
    This script should delete sys.gtblahblah_buffer statements.
    This can also delete ALTER COMPILE statements, consts$ package, and commit statements from DDL or DML diff/sync scripts.
    This script should also delete sys.qtblahblah_buffer statements from a
    specified file.
    
"""

import re
import getopt
import sys
import os
import pathlib
import logging

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
junk_logger = logging.getLogger('junk-log')
if not junk_logger.handlers:
    junk_fh = logging.FileHandler('rm_junk-debug.log')
    junk_logger.setLevel(logging.DEBUG)
    junk_fh.setFormatter(formatter)
    junk_logger.addHandler(junk_fh)


def rmConsts(file):
    """Remove the consts$ specification and package body. """

    junk_logger.info("Starting function. rmConsts()")

    #import awesome #for the slowdown debugging function

    start, end = 0,0

    #first read in the file

    with open(file) as f:
        rc = f.readlines()

    #print("File read in")
    
    for lineno, line in enumerate(rc):
        find_start = re.search("^CREATE OR REPLACE PACKAGE.*foo_bars.\"CONSTS\$\"$", line)
        if find_start:
           if "BODY" in line:
               #print("\n[+] Found start of consts$ body.")
               junk_logger.debug("[+] Found start of consts$ body.")
           else:
               #print("[+] Found start of consts$ specification.")
               junk_logger.debug("[+] Found start of consts$ specification.")
           #print(f"[+] start line# {lineno} line: {line}")
           junk_logger.debug(f"[+] start line# {lineno} line: {line}")
           #awesome.slowdown()
           start = lineno
           

        find_end = re.search("^END CONSTS\$;$", line)
        if find_end:
            #print("[+] Found end of consts$")
            #print(f"[+] end line# {lineno} line: {line}")
            junk_logger.debug("[+] Found end of consts$")
            junk_logger.debug(f"[+] end line# {lineno} line: {line}")
            #awesome.slowdown()
            end = lineno
        

            #add code to delete lines here
            if start and end:
                #print(f"[+] Going to delete lines {start} to {end+2}") #delete 2 more at the end because the slice operator does not include the last line and to delete the slash
                junk_logger.debug(f"[+] Going to delete lines {start} to {end+2}")
                del rc[start:(end+2)]
                start, end = 0,0 #re-initialize 
                
                #print("Writing what remains of this file to disk.")
                junk_logger.debug("Writing what remains of this file to disk.")
                with open(file, 'w') as new_file:
                    for line in rc:
                        new_file.write(line)

                junk_logger.info("Calling this function again. rmConsts() ")
                rmConsts(file)
                return
            else:
                junk_logger.debug("Either a start or end was found but not both. Exiting function.")
                return

    print(f"[+] Process complete. All CONSTS$ package objects shoule be cleaned from {file}.")
    junk_logger.info(f"[+] Process complete. All CONSTS$ package objects shoule be cleaned from {file}.")
    return
            

def rmCommit(path):
    """This function removes "commit;" statements from files. This is designed to remove commit statements from Red-gate generated DML scripts.
       Currently, there is not an option to remove 'commit' statements from DML deployment scripts in Red-gate's Data Compare for Oracle 5. 
    """
    count = 0 #let us go ahead and count how man commits were removed
    
    junk_logger.debug("The path passed is: %s" % str(path))
    
    p = pathlib.Path(path)

    #find the files that end with sql in the current dir
    found = p.glob("*.sql")
    found = list(found) #change the generator to a list

    junk_logger.debug("These are the SQL files found:%s" % found)

    for file in found: #loop over the files found that end in .sql and remove the commit statements and write the clean files to disk

        filename = file.name #a path object should have a 'name' attribute
        junk_logger.debug("Looking through this file now: %s" % filename)

        new_file = []
        
        
        with open(file, 'r') as f:
            lines = f.readlines()

        for lineno, line in enumerate(lines):
            searching = re.search(r'^COMMIT;$', line)
            if searching:
                count = count + 1
                del lines[lineno] #do not add a blank line. delete the line. 
                
            else:
                new_file.append(line)

        if count > 0: #only write the file to disk and print the number of ALTER statements found if more than zero ALTER statements were found
            with open(file, 'w') as pristine:
                for line in new_file:
                    pristine.write(line)
                print("[+] %d commit statements removed from file:%s and written to disk." % (count, filename))
                junk_logger.info("[+] %d commit statements removed from file:%s and written to disk." % (count, filename))
        else:
            junk_logger.info("[-] No commit statements found.")

    return count
    
    
    

def rmRevoke(path):
    """This function removes REVOKE statements from Schema Compare for Oracle (SCO) deployment scripts.
       Pass in a directory to this function. ***Beware that any SQL files with a line with REVOKE in them
       will be silently altered on disk. ***

    """
    count = 0 #count how many 'REVOKE' statements are removed

    junk_logger.debug(f"The path passed in to 'rmRemove' is {path}.")

    p = pathlib.Path(path)

    #find the files that end with 'sql' in the current directory
    found = p.glob('*.sql')
    found = list(found) #change the generator to a list

    junk_logger.debug(f"These are the SQL files found: {found}")

    for file in found:
        filename = file.name #a path object should have a 'name' attribute
        junk_logger.debug(f"Looking through this file now for 'REVOKE' statements: {filename}")

        new_file = []

        with open(file, 'r') as f:
            lines = f.readlines()

        for lnum, l in enumerate(lines):
            found = re.search(r'^REVOKE\s.*', l)
            if found:
                count += 1
                del lines[lnum]
            else:
                new_file.append(l)

        if count > 0:
             with open(file, 'w') as pristine:
                for line in new_file:
                    pristine.write(line)
                print(f"[+] {count} REVOKE statements removed from file: {filename} and written to disk.")
                junk_logger.info(f"[+] {count} REVOKE statements removed from file: {filename} and written to disk.")
        else:
            junk_logger.info("[-] No REVOKE statements found.")

    return count

def rmWeirdo(path):
    """This function will remove the objects Abijit calls "weirdo" from tag_owner DDL scripts. The object always throws an ORA on deployment and looks like this:
       GRANT EXECUTE ON tag_owner."SYSTPrUAOk0/yE47gUwMAEayYNA==" TO PUBLIC;

       The object morphs! Although the object always begins with "SYS" and ends with "=="

       Nothing against weirdos though... Be weird, be you! :) Learn to program a computer too. I do not have any more life advice at the present time. I am rusting in a robot scrap yard.
    """
    count_weirdo = 0
    junk_logger.debug(f"The path passed to 'rmWeirdo' is: {path}")

    p = pathlib.Path(path)

    found = p.glob("TAG_OWNER*.sql") #only looking for Dr. Strange in the tag_owner schema
    found = list(found)

    if len(found) > 0:
        print("[+] We may have a possible interesting weirdo object. Please stand by while we scan every part of this vessel.")
        print(f"[+] Number of possible files containing weirdo objects: {len(found)}")

        for file in found: #should be only 1 file but someone could of created multiple diffs and generated 1 to X number of tag_owner diff scripts
            print(f"[+] Currently processing this file: {file}")

            filename = file.name #a path object should have a 'name' attribute
            junk_logger.debug("Looking through this file now: %s" % filename)

            new_file = []
        
        
            with open(file, 'r') as f:
                lines = f.readlines()

            for lineno, l in enumerate(lines):
                weirdo_grant = re.search('^GRANT EXECUTE ON tag_owner.\"SYSTP(.*)==\" TO PUBLIC;$', l)
                if weirdo_grant:
                    print("[+] Weirdo object removed sirs.")
                    count_weirdo +=  1
                    del lines[lineno]
                else:
                    new_file.append(l)

            if count_weirdo > 0: #only write a new file if a "weirdo object" was found
                with open(file, 'w') as pristine:
                    for line in new_file:
                        pristine.write(line)
                    print("[+] %d WEIRDO objects removed from file:%s and written to disk." % (count_weirdo, filename))
                    junk_logger.info("[+] %d WEIRDO objects removed from file:%s and written to disk." % (count_weirdo, filename))
            else:
                junk_logger.info("[-] No WEIRDO objects found sir.")
                
              
            
        
        
    else:
        print("[-] No interesting weirdo objects present.")
        junk_logger.info("[+] TAG_OWNER schema not present. No interesting weirdo objects to filter.")
        return
    
    

def rmCompile(path):
    """This function will remove ALTER blah.blah COMPILE statements from DDL diff scripts generated by SCO.exe.
       Just pass in the path and then this function will look for anything ending with .sql and remove lines that
       begin with ALTER and end in COMPILE. This takes a directory to look through. Careful, the function alters things without asking. 

    """
    count = 0 #keep track of ALTER PACKAGE COMPILE statements - well count them...
    junk_logger.debug("The path passed is: %s" % str(path))
    
    p = pathlib.Path(path)

    #find the files that end with sql in the current dir
    found = p.glob("*.sql")
    found = list(found) #change the generator to a list

    junk_logger.debug("These are the SQL files found:%s" % found)

    for file in found: #loop over the files found that end in .sql and remove the ALTER COMPILE statements and write the clean files to disk

        filename = file.name #a path object should have a 'name' attribute
        junk_logger.debug("Looking through this file now: %s" % filename)

        new_file = []
        
        
        with open(file, 'r') as f:
            lines = f.readlines()

        for lineno, l in enumerate(lines):
            searching = re.search(r'^ALTER.*COMPILE.*;$', l)
            if searching:
                count = count + 1
                del lines[lineno]
            else:
                new_file.append(l)

        if count > 0: #only write the file to disk and print the number of ALTER statements found if more than zero ALTER statements were found
            with open(file, 'w') as pristine:
                for line in new_file:
                    pristine.write(line)
                print("[+] %d ALTER COMPILE statements removed from file:%s and written to disk." % (count, filename))
                junk_logger.info("[+] %d ALTER COMPILE statements removed from file:%s and written to disk." % (count, filename))
        else:
            junk_logger.info("[-] No ALTER COMPILE statements found.")

    return count


def rmJunk(path):
    """ This is the function that removes sys.gtblahblah_buffer or sys.qtblahblah_buffer. """

    #open the file and read the lines of the file into the variable 'L'
    f = open(path)
    L = f.readlines()

    #get the file name from a path
    filename = path.split('/')[-1]
    #print("The filename is: %s " % filename)

    #create a list to hold the lines of the new file
    new_file = []

    #search for the lines we do not want
    for lineno, line in enumerate(L):
        searchObject = re.search(r'sys[.][g|q]t\d{1,}_buffer', line)
        if searchObject:
            del L[lineno]
        else:
            #print(repr(line))
            new_file.append(line)

    #write the lines of the new file to disk
    with open(filename + 'Clean.sql', 'w') as f:
        for j in new_file:
            f.write(j)



def helpMe():
    """How to use this script"""
    print("""

              ____                                     _             _    
             |  _ \ ___ _ __ ___   _____   _____      | |_   _ _ __ | | __
             | |_) / _ \ '_ ` _ \ / _ \ \ / / _ \  _  | | | | | '_ \| |/ /
             |  _ <  __/ | | | | | (_) \ V /  __/ | |_| | |_| | | | |   < 
             |_| \_\___|_| |_| |_|\___/ \_/ \___|  \___/ \__,_|_| |_|_|\_\
                                                              

    """)
    print("""

This script removes "sys.gt12345_buffer" objects from SQL deployment scripts generated by RedGate.
    
The 'r' option says to remove the file you specify. Please include the full path to the file.

To use this program use the following option:
%s -r <path to SQL file to clean>
    """ % sys.argv[0])

    print("To run the program execute the program in the following way:")
    print("%s -b <dir>" % sys.argv[0])
    print("%s --batch <dir>" % sys.argv[0])
    


if __name__ == "__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ctrhb:', ['batch='])

        for opt, arg in opts:

            if opt in ('-t'):
                path = """C:/workspace/foo-db_PDB2/releases/2.2.0-RELEASE/Upgrade from 2.1.0-RELEASE/core"""
                import os
                os.chdir(path)
                print(os.getcwd())

                f = path + '/' + "7_foo_barz-schema-localhost_1521_pdb2.megacorp.local-localhost_1521_pdb1.megacorp.local.sql"
                rmJunk(f)
                
            elif opt in ('-r'):
                f = input('Please specify the path to the file: ')
                rmJunk(f)

            elif opt in ('-h'):
                helpMe()

            elif opt in ('-c'):
                f = input("Paste path to the file to remove ALTER statements here: ")
                rmCompile(f)

            elif opt in ('-b', '--batch'):
                directory = arg
                import os
                directory = os.path.abspath(directory)
                os.chdir(directory)
                print("The script, %s, changed to this directory, %s, in batch mode." % (sys.argv[0], directory))
                import glob
                files = glob.glob("*.sql")
                print("Found these files in batch mode: %s" % files)
                for f in files:
                    rmJunk(f)

    except getopt.GetoptError as e:
        print("Please try again. Something went wrong executing the program.")
        print("This exception was thrown: %s. " % str(e))
        print("%s -h" % sys.argv[0]) 
        
    
    
