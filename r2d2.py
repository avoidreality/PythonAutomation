#Create release artifacts programmatically like a genius instead of like a cretin.
import os
import re
import subprocess
import GitReportConfigurationFiles
import shutil
import logging
import threading
import pathlib
import variable
import tempfile

#logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

r2d2_logger = logging.getLogger('r2d2-log')
if not r2d2_logger.handlers:
    r2d2_fh = logging.FileHandler('r2d2-debug.log')
    r2d2_logger.setLevel(logging.DEBUG)
    r2d2_fh.setFormatter(formatter)
    r2d2_logger.addHandler(r2d2_fh) #add the file handler to the logger


def createReleaseFolder(pdb2):
    """This function takes a pdb2 name and returns the release folder name. Exceptional situation are not considered here as this is not a public API. """
   #pdb2 will be something like foo-db-2.11.0-RC1 or EGGS-2.1.6-RC1
    #This means a folder like this is needed: 2.11.0-RC1 - step 1. (The folder actually needs to be like this 2.11.0-RELEASE)
    if variable.MODE == "FOO":
        release_folder = pdb2.split("foo-db-")[1] #get the second element in the list from the split on the agency prefix and put this token in the variable
    else:
        release_folder = pdb2.split('EGGS-')[1] 

    #now replace the tailing "RC" part of the string most likely currently in 'release_folder'. This is step 2. The 'release_folder' variable should now be like so 2.11.0-RELEASE.
    release_folder = re.sub("RC[0-9]", "RELEASE", release_folder)

    return release_folder

def autoFolders(pdb1, pdb2, base_dir=r"C:\\workspace\foo\foo-db\releases"):
    """Pass in the pdb information and the base information. From here the
       the function will create folders for the release.
    """

    if not os.path.isdir(base_dir):
        print("[!] The base directory does not exist. Automatic folders for the release cannot be created. Function ending.")
        return

    #pdb2 will be something like foo-db-2.11.0-RC1
    #This means a folder like this is needed: 2.11.0-RC1 - step 1. (The folder actually needs to be like this 2.11.0-RELEASE)
    if variable.MODE == "FOO":
        release_folder = pdb2.split("foo-db-")[1] #get the second element in the list from the split on the agency prefix and put this token in the variable
    elif variable.MODE == "RITE":
        release_folder = pdb2.split('EGGS-')[1]
    elif variable.MODE == "MONO":
        release_folder = pdb2.split('ritehorizon-')[1]
        

    #now replace the tailing "RC" part of the string most likely currently in 'release_folder'. This is step 2. The 'release_folder' variable should now be like so 2.11.0-RELEASE.
    release_folder = re.sub("RC[0-9]", "RELEASE", release_folder)

    if os.path.exists(base_dir + os.sep + release_folder):
        pass    
    else:
        os.mkdir(base_dir + os.sep + release_folder)
        print(f'[+] Creating the release folder here: {base_dir + os.sep + release_folder}')

    #write this path to disk for later look-up to create the readme.txt files ^_~
    with open(variable.DIFF_SCRIPTS + os.sep + 'current_software_release.txt', 'w') as cs:
        cs.write(base_dir + os.sep + release_folder)

    
    #Make the sub-folders under the main release folders :D
    #upgrade will be "Upgrade from pdb1"
    #downgrade will be "Downgrade to pdb1"
    #'pdb1' should be something like: foo-db-9.3.1-RELEASE. This does not need to be changed. Awesome.
    upgrade_folder = f"Upgrade from {pdb1.strip()}"
    downgrade_folder = f"Downgrade to {pdb1.strip()}"

    tenant_folder = None
    if variable.TENANT:
        if variable.TENANT == "dot":
            #create the dot folder structure
            tenant_folder = "dot"
        elif variable.TENANT == "rnd":
            #create the rnd folder structure
            tenant_folder = "rnd"
        else:
            print("[+] I am not aware of this tenant. Default folder structure will be used for this situation.")

    
    if not variable.TENANT:
        #make the folders! Hooray. :)
        up_folder = base_dir + os.sep + release_folder + os.sep + upgrade_folder
        up_path = pathlib.Path(up_folder)
        if up_path.exists():
            print("The upgrade folder already exists.")
        else:
            os.mkdir(up_folder)

        down_folder = base_dir + os.sep + release_folder + os.sep + downgrade_folder
        down_path = pathlib.Path(down_folder)
        if down_path.exists():
            print("The downgrade folder already exists.")
        else:
            os.mkdir(down_folder)

        with open(variable.DIFF_SCRIPTS + os.sep + 'release_folders.txt', 'w') as rf: #write the Upgrade from ... Downgrade to ... folders to disk for later use by scan.py, big_bang.py, and maybe crazydiamond.py. This is better than a variable in case of a crash.
            rf.write(up_folder + "\n")
            rf.write(down_folder)
    else: #tenant
        tenant_up_folder = base_dir + os.sep + release_folder + os.sep + tenant_folder + os.sep + upgrade_folder
        ten_up_path = pathlib.Path(tenant_up_folder)
        if ten_up_path.exists():
            print("The upgrade tenant path already exists.")
        else:
            os.makedirs(tenant_up_folder) #create the folder
        

        tenant_down_folder = base_dir + os.sep + release_folder + os.sep + tenant_folder + os.sep + downgrade_folder
        ten_down_path = pathlib.Path(tenant_down_folder)
        if ten_down_path.exists():
            print("The downgrade tenant path already exists.")
        else:
            os.makedirs(tenant_down_folder) #create the folder

        with open(variable.DIFF_SCRIPTS + os.sep + 'release_folders.txt', 'w') as trf:
            trf.write(tenant_up_folder + '\n')
            trf.write(tenant_down_folder)

    #move the translation report if this report exists
    #if there is a translation report move the report inside the tenant folder or the release folder
    print("Figuring out if a translation report needs to be added to the release (NBM mode)...")
    build_path = pathlib.Path(base_dir)
    release_path = build_path / release_folder
    
    tr = pathlib.Path(os.path.join(variable.DIFF_SCRIPTS,"TRANSLATION_REPORT.html"))
    if tr.exists():
        print("*" * 5 + " There is a translation report " + "*" * 5)
        if variable.TENANT:
            normal_tenant_path = release_path / tenant_folder
            tenant_treport = normal_tenant_path / "TRANSLATION_REPORT.html" #create a pathlib Path object to the TRANSLATION_REPORT.html in the tenant folder. This is where the file should be packaged in the release.
            shutil.move(tr, tenant_treport)
            print(f"[+] Translation report moved to {tenant_treport}")
        else:
            t_release = release_path / "TRANSLATION_REPORT.html"
            shutil.move(tr, t_release)
            print(f"[+] Translation report moved to {t_release}")
    else:
        print("[-] Translation report not found.")

    releaseReadMe(base_dir + os.sep + release_folder, pdb1, pdb2)#create the release readme.md file from the parsed and computed info

    #start new thread for the environment report
    if variable.TENANT:
        
        env_thread = threading.Thread(target=EnvReport, args=(base_dir + os.sep + release_folder + os.sep + tenant_folder, pdb1, pdb2,))
    else:
        env_thread = threading.Thread(target=EnvReport, args=(base_dir + os.sep + release_folder, pdb1, pdb2,))
    env_thread.name ="Environment_Report_Thread"
    env_thread.start()

    


def releaseReadMe(release_directory, pdb1, pdb2):
    """By passing in the release directory and the release_name the readme.md can be created."""

    readme_markdown_template = """## YourRelease Release Notes

### Overview:
No Summary Available.    

### Details:
"""
    p = pathlib.Path(release_directory)
    release_name = p.name
    

    print(f"release_name = {release_name}")

    #substitute "YourRelease" in the template string with the 'release_name'
    readme_markdown_template = re.sub("YourRelease", release_name, readme_markdown_template)

    with open(release_directory + os.sep + 'readme.md', 'w') as rrm:
        rrm.write(readme_markdown_template)


    #step 1 change directories to the foo-db repository where the .git folder is

    print(f"[+] Changing directories to: {variable.GIT_REPO}")
    os.chdir(variable.GIT_REPO)
    print(f"[+] Current directory = {os.getcwd()}")

    try: 
        #fetch all to get new branches. 
        p_instance = subprocess.run(['git', 'fetch', '--all'], check=True, capture_output=False)
    except subprocess.CalledProcessError as CPE:
        print(f"Exception thrown doing a 'git fetch --all'. Please see the following exception: {CPE}")
        #try 1 more time without checking for errors
        print("[+] Re-trying 'git fetch --all'.")
        p_instance = subprocess.run(['git', 'fetch', '--all'], capture_output=False)
        
    git_log_out = None
    #get the git log output
    try:
        git_log_out = subprocess.run(['git', 'log', f'origin/{pdb1}..origin/{pdb2}', '''--pretty=format:"%h %s"''' ], \
                                 check=False,capture_output=True, text=True, encoding='utf8')
    except Exception as gloe:
        print(f"[+] There was an exception thrown obtaining the 'git log' output. Exception: {gloe}")

    #parse the std out and put this data into a list data structure
    out = None
    if git_log_out:
        try:
            out = git_log_out.stdout.split("\n") #put the output into a list
        except Exception as out_ex:
            print(f"[!] There was an exception parsing the standard output of 'git log'. Check it out: {out_ex}")

        if out:
            #clean the out(put) of lines we do not want
            lines_to_delete = ["Merge branch '", "Merge remote-tracking branch '", "Commit performed by Jenkins build", "Commit performed by post-receive trigger."]

            #remove the lines from the git log
            for pattern in lines_to_delete:
                for line_num, line in reversed(list(enumerate(out))): #search in reverse so as the elements are deleted nothing is lost
                    #print(f"[*] Searching for this pattern: {pattern} in this line: {line}")
                    match1 = re.search(pattern, line)
                    if match1:
                        #print("Match Found:", match1)
                        del out[line_num]

        ##    print("These are the lines in 'out' now.")
        ##    for element in out:
        ##        print(repr(element))

            #write the git log to the end of the readme.md file
            with open(release_directory + os.sep + 'readme.md', 'a') as readm:
               for line in out:
                   readm.write(line.strip() + "\n")

    duanes_shell(pdb1, pdb2, release_directory)


def unix_line_endings(file=r"/cygdrive/c/workspace/foo/foo-db/releases/diff_scripts/show_file_changes.sh"):
    """This function will change the line endings from Windows carriage-return new-line to just the *nix new-line (line-feed).
    This code is from here: https://stackoverflow.com/questions/36422107/how-to-convert-crlf-to-lf-on-a-windows-machine-in-python
    Thanks winklerrr. I made the code a function and test to make sure the file exists. Thank-you me, myself, and I.
    """
    # replacement strings
    WINDOWS_LINE_ENDING = b'\r\n'
    UNIX_LINE_ENDING = b'\n'

    path = pathlib.Path(file)

    if path.exists():
        pass
    else:
        print("The file does not exist. Nothing to change to Unix line-endings. Returning.")
        return

    # relative or absolute file path, e.g.:
    file_path = file

    with open(file_path, 'rb') as open_file:
        content = open_file.read()
    
    content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

    with open(file_path, 'wb') as open_file:
        open_file.write(content)


def duanes_shell(pdb1, pdb2, release_directory):
    """Execute Duane's shell script 'show_file_changes.sh' to show changes between the 2 branches regarding new users,etc."""

    r2d2_logger.info("At the top of r2d2.duanes_shell.")

##    r2d2_logger.info('About to change the line endings from Unix to Windows!')
##    unix_line_endings(variable.DIFF_SCRIPTS + os.sep + 'show_file_changes.sh') #change the Windows end-of-line (EOL) characters GitExtensions adds to Unix line-feeds Cygwin can work with
##    r2d2_logger.info('Line endings changed.')
    
    standard = None
    errors_everywhere = None
    #run the scripts
    
    diff_path = pathlib.Path(variable.DIFF_SCRIPTS) #change the path that may be escaped incorrectly to a pathlib object
    

    start_dir = os.getcwd()
    r2d2_logger.debug(f'[+] The start directory is: {start_dir}')
    if diff_path.exists():
        os.chdir(diff_path)
    else:
        print(f"[+] Cannot call 'show_file_changes.sh'. This path cannot be found: {diff_path}")
        r2d2_logger.debug(f"[+] Cannot call 'show_file_changes.sh'. This path cannot be found: {diff_path}")
        
    r2d2_logger.debug(f'[+] Changing directories to: {diff_path}')
    
    shell_out = subprocess.run(['bash', '-c',  \
                                f'./show_file_changes.sh "/SYS/" "{pdb1.strip()}" "{pdb2.strip()}"'], \
                               text=True, capture_output=True)

    if shell_out.stdout:
        standard = shell_out.stdout.split("\n")

    if standard:
        with open(str(release_directory) + os.sep + 'readme.md', 'a') as space:
            space.write("\n\n") #add some blank space 
        with open(str(release_directory) + os.sep + 'readme.md', 'a') as destructo:
            for line in standard:
                destructo.write(line.strip() + "\n") #write the output of Dr. Destruct-o's shell script
        r2d2_logger.debug(f"[+] There was standard output. The readme.md is now updated with Duane's shell script. The readme.md is located here {str(release_directory) + os.sep + 'readme.md'}.")

    if shell_out.stderr:
        errors_everywhere = shell_out.stderr.split("\n")

        for error in errors_everywhere:
            r2d2_logger.error(f"[!] Error in duanes_shell -> {error}")

    if start_dir != os.getcwd():
        os.chdir(start_dir)
        r2d2_logger.debug(f'[+] Changing directories back to {start_dir}')
    else:
        r2d2_logger.debug('[+] Start directory and the current working directory are the same. No need to change dirs.')
        
    r2d2_logger.info('r2d2.duanes_shell complete.')

    
    

def EnvReport(release_directory, plug1, plug2):
    """Create the environment report and move the report to the correct location in the release folder."""

    if plug1 is None or plug2 is None:
        r2d2_logger.error(f"plug1 = {repr(plug1)} plug2= {repr(plug2)} Something is in error. Python says these variables are None.")

    
    #put a lock here to make this process atomic
    lock = threading.Lock()
    print("[*] Locking thread to create environment report")
    with lock:
        print(f"[*] Inside env rpt lock. Start. Current dir: {os.getcwd()}")
        GitReportConfigurationFiles.checkStartDir()
        GitReportConfigurationFiles.allInAll(plug1, plug2)
        print(f"[*] Inside env rpt lock. End. Current dir: {os.getcwd()}")
        
    print("[*] Releasing thread lock for environment report.")

    #now the report should be in the following directory, because that is what the "checkStartDir" function did:C:\workspace\foo\foo-db
    #move the report to the release_directory
    try:
        print("[i] Moving Environment Report to current release dir.")
        shutil.move(variable.GIT_REPO + os.sep + "ENVIRONMENT_REPORT.html", release_directory)
        print("[i] Environment report moved successfully.")
        r2d2_logger.info("[i] Environment Report moved to %s" % release_directory)
    except shutil.Error as se:
        print(f"[!] Error moving the Environment report: {se}")
        r2d2_logger.error(f"[!] Got this error moving the environment report:  {se}")
        r2d2_logger.error(f"[!] The environment report may already exist at this location: {release_directory}")

    return

def findDrivers(release_folder):
    """Try and use the glob module to quickly find the CBT files for DDL and DML."""
    import glob


    #Should an absolute path be passed in for the value of 'release_folder' or does a relative path work?
    wp = pathlib.WindowsPath(release_folder)
    files = os.listdir(wp)

    driver_scripts = dict()
    important_dirs = dict()

    #search through ddl and dml folders, but first find these things
    for f in files:
        thing = wp / f
        if thing.is_dir():
            if 'ddl' in thing.name:
                important_dirs['DDL'] = (thing.name, thing)
                #print(f"This is DDL! thing.name = {thing.name}. thing = {thing}")
            if 'dml' in thing.name:
                important_dirs['DML'] = (thing.name, thing)
                #print(f"This is DML! thing.name = {thing.name}. thing = {thing}")

    for k,v in important_dirs.items():
        if k == "DML":
            found = v[1].rglob("CBT-MetaSQL*sql")
            result = list(found) #change the generator to a list
            #print(f"[+]DML! result = {result}")
            if len(result) > 0:
                driver_scripts["DML"] = result[0].name
            else:
                driver_scripts["DML"] = "NA"
        else:
            driver_scripts["DML"] = "NA"
                
        if k == "DDL":
            found = v[1].rglob("CBT-MetaSQL*sql")
            result = list(found) #change the generator to a list
            #print(f"[+] DDL! result = {result}")
            if len(result) > 0:
                driver_scripts["DDL"] = result[0].name
            else:
                driver_scripts["DDL"] = "NA"
        else:
            driver_scripts["DDL"] = "NA"
                
                
    return driver_scripts
            
def updateReadMe(release_directory=None):
    """This function will be given the release directory and from there the function will look through the folder structure and create readme files for the upgrade and downgrade."""

    #This is the readme template to modify and write to disk
    up_readme_template = """To upgrade please follow these simple steps.

Step 1.) DDL 

::::DDL::::
1.) Change directories to "upgrade_bigbang_ddl"
2.) Execute the following script: 

Step 2.) DML 

::::DML::::
1.) Change directories to "upgrade_bigbang_dml"
2.) Execute the following script:
"""


    #first figure out the release folder location - if nothing was passed into the function open the file created in the 'autoFolders()' function.
    if release_directory is None:
        with open(variable.DIFF_SCRIPTS + os.sep + 'current_software_release.txt', 'r') as spread_wings_taking_flight:
            release_directory = spread_wings_taking_flight.read()

    if variable.TENANT:
        #add the tenant to the end of the release_directory path for tenant releases! :)
        release_directory = release_directory + os.sep + variable.TENANT

    #test to see if the path found in the filesystem is a path on the operating-system (OS)
    r2d2_logger.info(f"This is the release_directory = {release_directory}")
    print(f"This is the release_directory = {release_directory}")
    
    import pathlib
    p = pathlib.Path(release_directory)

    if p.exists():
        r2d2_logger.info("The release folder exists.")
    else:
        r2d2_logger.error("The release folder does not exist. There are not any readmes to update. Returning.")
        return

    #go to the folder and inspect to see what is there
    os.chdir(release_directory)

    dirs = os.scandir('.') #list everything in the main release folder

    dirs_list = list(dirs) #change the generator to a list

    directories = set() #store the directories found here

    #this loop tests if something is a directory and then adds the directory to the directories set
    for thing in dirs_list:
        if thing.is_dir():
            directories.add(thing.name)
            r2d2_logger.info(f"[*] Adding this to directories: {thing.name}")

    
    
    if len(directories) == 2: #excellent. We have an up and down folder as desgined.
        pass
    else:
        r2d2_logger.error("There is not an upgrade and a downgrade folder. Something is wrong.")


    upgrade_folders = None
    downgrade_folders = None

    #find the upgrade - where to write the upgrade readme.txt
    upgrade_folder = [x for x in directories if x.startswith("Upgrade")]
    r2d2_logger.info(f"upgrade_folder = {upgrade_folder}")
    if len(upgrade_folder) > 0:
        upgrade_folders = upgrade_folder[0]
    else:
        r2d2_logger.debug("No upgrades for this release?")

    #find the downgrade - where to write the downgrade readme.txt
    downgrade_folder = [x for x in directories if x.startswith("Downgrade")]
    r2d2_logger.info(f"downgrade_folder = {downgrade_folder}")
    if len(downgrade_folder) > 0:
       downgrade_folders = downgrade_folder[0]
    else:
        r2d2_logger.debug("No downgrades for this release?")

        
    #update the upgrade readme.txt file
    if upgrade_folders:
        driver_info = findDrivers(upgrade_folders) #call this function to inspect the folders in main Upgrade folder
        
        up_lines = up_readme_template.split("\n")#split the string on the new-line characters and create a list
        dml_line = up_lines[12]
        ddl_line = up_lines[6]
        
        #update the string with the driver script names
        #UPGRADE Scripts
        if 'DML' in driver_info:
            if driver_info['DML'].startswith("CBT"):
                up_lines[12] = dml_line + driver_info['DML'] #add the driver script name to the line
            else:
                up_lines[12] = dml_line + "NA"

        if "DDL" in driver_info:
            if driver_info['DDL'].startswith("CBT"):
                up_lines[6] = ddl_line + driver_info['DDL']
            else:
                up_lines[6] = ddl_line + "NA" #add NA to the end if the driver script was not found

        #write the readme file to the correct spot
        print(f"Trying to write to this file: {release_directory + os.sep + upgrade_folders}") 
        with open(release_directory + os.sep + upgrade_folders + os.sep + 'readme.txt', 'w') as wuf:
            for line in up_lines:
                wuf.write(line + "\n")
    

    #update the downgrade readme.txt file
    if downgrade_folders:
        driver_info = findDrivers(downgrade_folders)

        down_readme_template = re.sub('upgrade', 'downgrade', up_readme_template) #just substitute 'downgrade' for 'upgrade' in the up-template and we have the downgrade template! :)

        down_lines = down_readme_template.split("\n")
        dml_line = down_lines[12]
        ddl_line = down_lines[6]

        if 'DML' in driver_info:
            if driver_info['DML'].startswith("CBT"):
                down_lines[12] = dml_line + driver_info['DML'] #add the driver script name to the line
            else:
                down_lines[12] = dml_line + "NA"

        if "DDL" in driver_info:
            if driver_info['DDL'].startswith("CBT"):
                down_lines[6] = ddl_line + driver_info['DDL']
            else:
                down_lines[6] = ddl_line + "NA" #add NA to the end if the driver script was not found

        #write the readme file to the correct spot
        print(f"Trying to write to the read me in this folder: {release_directory + os.sep + downgrade_folders}") 
        with open(release_directory + os.sep + downgrade_folders + os.sep + 'readme.txt', 'w') as wdf:
            for line in down_lines:
                wdf.write(line + "\n")

    r2d2_logger.info("[*] Update readme complete.")

def moveFolders(pdb2,staging=r"C:\workspace\foo\foo-db\releases\bigbang"):
    """Move the release folders generated by the scripts to the correct location."""

    staging_path = pathlib.WindowsPath(staging)

    files = os.listdir(staging_path)

    upgrade_files = set()
    downgrade_files = set()
    upgrade_folder = None
    downgrade_folder = None

    for directory in files:
        if "upgrade" in directory:
            upgrade_files.add(directory)
        if "downgrade" in directory:
            downgrade_files.add(directory)

    
    #move the files to the correct release folder and the upgrade or downgrade folder in this release folder
    release = createReleaseFolder(pdb2)
    release_path = staging_path.joinpath(r"C:\workspace\foo\foo-db\releases")
    release_path = release_path / release
    if release_path.exists():
        print("[*] The release path exists.")
    else:
        print("[!] The release path does not exist.")
        return

    release_path_files = os.listdir(release_path)
    for d in release_path_files:
        if "Upgrade" in d:
            upgrade_folder = d
        if "Downgrade" in d:
            downgrade_folder = d

    up_path = release_path / upgrade_folder
    if up_path.exists():
        print(f"The upgrade folder exists: {up_path}")
        for up_dir in upgrade_files:
            shutil.move(staging + os.sep + up_dir, up_path)
    else:
        print("The upgrade folder was not found.")

    down_path = release_path / downgrade_folder

    if down_path.exists():
        print(f"The downgrade folder exists: {down_path}")
        for down_dir in downgrade_files:
            try:
                shutil.move(staging + os.sep + down_dir, down_path) #a process is hanging on to the downgrade_dml folder that throws an exception but moves the folder. although an empty folder remains.
            except Exception as de:
                print(f"An exception was thrown moving the downgrade scripts folder: {down_dir}. The exception was {de}")
    else:
        print("The downgrade folder was not found.")

def getBuildHash(branch='test'):
    """ Look in settings.xml on the GitLab server for the release number and the hash. This returns the release number and hash as a string. """
    import requests
    import re
    import xml.etree.ElementTree as ET

    token = None

    #look up token in pdb_tools
    # Windows path:C:\docker\pdb_tools\set_parms.md
    set_parms = pathlib.Path('/docker/pdb_tools/set_parms.md')

    if set_parms.exists():
        text = set_parms.read_text()
        #print(f"[+] The type of 'text' is: {type(text)}") #This returns a string
        #print(f"[+] 'text' = {text}")
        # use regular expressions (RE) to get the password
        lines = text.split('\n')
        for line in lines:
            match = re.findall("gitlab token", line)
            if match:
                #print(f"[+] Found it: {line}")
                split_line = line.split("|")
                token = split_line[2]
                if token:
                    token = token.strip()
                    #print(f"[+] token = {token}")
                
            
    else:
        print("[!] docker/pdb_tools/set_parms.md file not found!")
        raise Exception('set_parms.md not found.')
    
    if token:

        curl_args = ['curl', '-fsS', '--connect-timeout', '5', '--header', f'PRIVATE-TOKEN:{token}', #token variable is here! :)
                     f'https://gitlab.megacorp.com/api/v4/projects/719/repository/files/settings.xml/raw?ref=ritehorizon-{branch}']
        
        output = subprocess.run(curl_args,capture_output=True, text=True)

        if output.stdout:
            xml = output.stdout #'xml' is a string
            root = ET.fromstring(xml)
            
            for version in root.iter('eggdb.version'):
                #print(version.text)
                return version.text #this returns a str data-type btw when used as designed on this computer at least ^_#
        else:
            print("[-] There was not any standard output for some reason when trying to find the settings.xml file for the ritehorizon-test branch.")
    else:
        print(f"[+] Something went wrong the token was not found to connect to GitLab in r2d2.getBuildHash()")

def custom_folder_init():
    """Create folders under releases/custom_sql as needed. """
    release_path = pathlib.Path(variable.RELEASE_DIR)

    custom_path = release_path / "custom_sql"

    migration_folders = {'upgrade_PreDDL', 'upgrade_PostDDL', 'upgrade_PreDML', 'upgrade_PostDML', \
                         'downgrade_PreDDL', 'downgrade_PostDDL', 'downgrade_PreDML', 'downgrade_PostDML'}
    if not custom_path.exists():
        raise Exception('The "custom_sql" folder does not exist. Please create releases/custom_sql and then continue.')
    
    for folder in migration_folders:
        the_folder = custom_path / folder
        if not the_folder.exists():
            print(f"[+] This folder '{the_folder}' does not exist. Creating the folder now.")
            the_folder.mkdir()


def getReleaseData(release_name):
    """Pass in a release_name with a pattern like this #_#.#.#-8charhexhash for the new branching model and you receive the release number! Huzzah."""
    if isinstance(release_name, str):
        release_name = release_name.strip()
        release_number = int(release_name[0]) #get the first element of the string, which should be the release number at this point in the algorithm, the rhythm, the rhythm!
        return release_number, release_name[1:]


def calculate_previous(release_dictionary, release):
    """Pass in a dictionary of releases and a specific release. From this data the previous release is returned. """
    current_release_number = None
    #make sure the release dictionary is sorted
    release_numbers = sorted(release_dictionary.keys())
    for release_num in release_numbers:
        if release_dictionary[release_num] == release:
            current_release_number = release_num

    if current_release_number:
        previous_release_number = current_release_number - 1
        try:
            previous_release = release_dictionary[previous_release_number]
        except Exception as calculate_error:
            print(f"[!] The previous release could not be determined exception thrown in r2d2.calculate_previous(). Exception: {calculate_error}")
            #latest_dev_release = getBuildHash(branch='dev')
            #return latest_dev_release
            return "Previous Version Unknown"

        else:
            return previous_release 

def versioning(path_to_release, nue):
    """Pass in the path object so the script knows where to create the versions.txt file. This file will contain the version for PDB1 and PDB2. PDB1 is always the test branch
       PDB2 is always the dev branch. """

    test_version = getBuildHash()
    dev_version = getBuildHash(branch="dev")

    versions_path = path_to_release / "versions.txt"

    versions_template = f"""*****Versions for PDB1 and PDB2.*****
PDB1 always refers to the test branch with the current design. PDB2 refers to the development, or dev, branch with the current design.

PDB1:{test_version}
PDB2:{dev_version}

Previous Release: {nue - 1} 
Current Release: {nue}

    """

    if path_to_release.exists():
        with open(str(versions_path), 'w') as ptr:
            ptr.write(versions_template)
    else:
        print(f"[+] The path to the release does not exist. Error in r2d2.versioning.")
        raise Exception("Path to release folder to write versions.txt does not exist.")



def newBranchingModelFolders(base_dir=r"C:/workspace/monorepo/newhorizon/egg-db/releases", tenant="dot"):
    """Create folders for the new branching model. Initialize the variable module with variable.toggle_variables before calling this function. Additionally, the variable.TENANT variable needs to be set."""

    remove_empty_folders(base_dir) # Adding this to remove empty release folders that sometimes are created during failed testing.

    releases = set() #only unique release #s, no duplicates in a set data-structure
    versions = dict()
    found = False
    release_numbers = []
    new_release_folder = None
    previous = None
    sorted_release = None
    initial = False
    custom_sql = "custom_sql"
    
    #create a Path object - maybe OS agnostic but the path needs to be the same on both OSes
    base_path = pathlib.Path(base_dir) #This becomes a WindowsPath object on Windows, example: if os.name == 'nt'

    print("[+] Getting test version and hash data")
    #find out what the latest test version-hash data is and compare this to folders already created
    latest_test_release = getBuildHash(branch='test')
    print(f"[+] Test version and hash data retrieval complete: {latest_test_release}")

    if latest_test_release == None:
        raise Exception("The test hash retrieved equals None. This will not work. Stopping program.")

    

    if os.getcwd() != str(base_path):
        print(f"[+] Changing locations on the computer. The new path is: {base_path}")
        os.chdir(base_path)

    print(f"[+] Looking for releases already in this directory: {os.getcwd()}")

    #look for release folders and put them in the 'releases' set
    files = os.listdir('.') 
    for file in files:
        fm = re.fullmatch(r'\d+', file) #the release folder will just be a positive integer, a whole-number greater than zero or equal to zero
        if fm:
            print(f"[+] This release directory was found: {file}")
            file_name = fm.group() #get the name
            #add the file, hopefully the release folder, to the releases set
            releases.add(file_name) 
            
    if len(releases) > 0:
        print(f"[+] These are the releases found: {releases}")
        print(f"[+] Sorting the releases now.")
        sorted_release = sorted(releases) #this will sort ascending and return a list of the release numbers
        print(f"[+] Finding the highest release number now.")
    else:
        print("[+] There were not any releases found.")
    
    #calculate the new release #
    if sorted_release and len(sorted_release) >= 1:
        latest_release = int(sorted_release[-1]) #get the last number in the list, the highest number! Also, change the str to an int.
        new_release_number = latest_release + 1
       
        
    else:
        latest_release = 0
        new_release_number = 0
        

    print(f"[+] The latest release number is: {latest_release}")
    print(f"[+] The new release number is: {new_release_number}")
    

    print("[+] Determining whether to create a new folder or overwrite a previous release folder.")
    #For this new folder and release structure we need to analyze the versions.txt file
    if len(releases) > 0:
        rpath = base_path / str(latest_release) #only concerned with latest release - create a path to the latest release
        files_in_rp = os.listdir(rpath) #look through this release directory
        if 'versions.txt' in files_in_rp: #is the versions.txt file in this directory?
            rpv = rpath / 'versions.txt' #create a new path
            with open(str(rpv)) as arrr: # open the versions.txt file
                v_contents = arrr.readlines() #read the lines into the v_contents variable

            #parse the contents of the versions.txt now stored in 'v_contents'
            for line in v_contents: #loop over the lines of the file
                if line.startswith("PDB1:"): 
                    print("[+] Found PDB1 - the last test release version data.")
                    last_test_version = line.partition("PDB1:")[2].strip() #the 3rd tuple element will be the version data
                    print(f"[i] Latest test version: {last_test_version} from release number {str(latest_release)}")
                    r2d2_logger.info(f"[i] Latest test version: {last_test_version} from release number {str(latest_release)}")
                    break #stop iterating in the loop
                    

            if last_test_version:
                #compare this to the current test version
                print(f"[?] Does {last_test_version} equal {latest_test_release} ?")
                if last_test_version == latest_test_release:
                    print("[=] Yes, the version of the last test release is the same as the current test release.")
                    print("[+] Re-creating folders...overwriting previous release folders...deleting and re-creating...")
                    found = True
                    new_release_number -= 1 #subtract the number added previously since we are not creating a new release folder
                    new_release_folder = base_path / str(latest_release) #define the release folder for later processing
                else:
                    print(f"[!=] Nope, {last_test_version} is not equal to {latest_test_release}")

                if found: #delete the subfolders in for a re-build basically
                    files = os.listdir(new_release_folder) #this should be a tenant folder, a readme.md, and a versions.txt files
                    print(f"[!] Found the following files to remove: {files}")

                    if files: #only delete if there are files under the 'new_release_folder'
                        for file in files:
                            rm_path = new_release_folder / file
                            
                            if rm_path.exists():
                                print(f"[i] This path exists: {rm_path}")
                                if rm_path.is_dir():
                                   if file == variable.TENANT: # do not delete the dot directory
                                       for root, subdirs, file in os.walk(rm_path):
                                           if root.endswith(variable.TENANT): #do not delete the tenant folder
                                               if file:
                                                   for f in file:
                                                       print("[+] Deleting this: ", f) 
                                                       os.unlink(os.path.join(root,f)) #this will delete the Environment Report.html and any file directly under the tenant folder
                                               print(f"[i] Found these subfolders under {variable.TENANT}: ", subdirs)
                                           
                                           elif root.endswith('custom_sql'): # do not delete the 'custom_sql' folder
                                               print("[+] Found the 'custom_sql' folder.")
                                               continue
                                           else:
                                               print("[!] Removing entire directory: ", root) #delete any directories under <tenant>/custom_sql
                                               rp = pathlib.Path(root)
                                               if rp.exists():
                                                   shutil.rmtree(rp) #root is a str most likely
                                                   print("[-] Deleting this directory: ", str(rp))
                                               else:
                                                   print("Cannot remove dir. The path does not exist: ", str(rp))
                                               print("[+] Removing subdirectories = ", subdirs)
                                               print("[+] Removing files = ", file)
                                               #breakpoint()
                                               if file:
                                                   for f in file: #delete any files under <tenant>/custom_sql
                                                       print("[+] Should I delete this file?", f)
                                                       #os.unlink(f)                                          
                                if rm_path.is_file():
                                    rm_path.unlink()
                                    print(f"[i] File {rm_path} removed.")
                            else:
                                print(f"[!] This path does not exist: {rm_path}. Achtung.")

    else:
       #create an initial release if there are not any releases in the 'releases' data-structure
       print("[+] Creating initial release.")
       if latest_release == 0:
           new_release_folder = base_path / str(latest_release) #start counting the releases at zero

           new_release_folder.mkdir() #make the directory
           initial = True

    
    if not found and not initial: #the test release version is new and there are multiple versions already created
        print("[+] Creating the new release directory!")
        #none of the previous conditions should be true. This is a new release
        #create a new release folder.
        new_cool_folder = new_release_number
        print(f"[+] The new release folder name is: {new_cool_folder}")

        

        new_release_folder = base_path / str(new_cool_folder)
        new_release_folder.mkdir() #actually create the new folder on disk

        #adding release to 'releases' in order to find the previous release
        
        
        
       


    if new_release_folder:
        #write this path to disk for later look-up to create the readme.txt files ^_~
        with open(variable.DIFF_SCRIPTS + os.sep + 'current_software_release.txt', 'w') as cs:
            cs.write(str(new_release_folder)) #Convert path object (Windows path on my laptop) to a str to write to disk
    else:
        raise Exception("The new_release_folder was not found! Exception thrown from r2d2.newBranchingModelFolders()")
        



    print(f"[+] The new release folder is: {new_release_folder}")

    #Add the tenant directory
    tenant_folder = None
    if variable.TENANT:
        if variable.TENANT == "dot":
            #create the dot folder structure
            tenant_folder = "dot"
        elif variable.TENANT == "rnd":
            #create the rnd folder structure
            tenant_folder = "rnd"
        else:
            print(f"[!] I am not aware of this tenant: {variable.TENANT}. Please add new code for this.")
            raise Exception('Unknown tenant')
    else:
        print(f"[!] The tenant variable is not set. This needs to be set for the new branching model. Program shutting down.")
        raise Exception("variable.TENANT not defined for new branching model")


    tenant_path = new_release_folder / tenant_folder #create the tenant path

    if not tenant_path.exists():
        tenant_path.mkdir() #create the tenant folder
        print(f"[+] Tenant folder created at this location: {tenant_path}")
    else:
        print("[+] The tenant folder already exists. This is a re-creation of a folder because of same test version: ", found)

    #if there is a translation report move the report inside the tenant folder
    print("Figuring out if a translation report needs to be added to the release (NBM mode)...")
    
    
    tr = pathlib.Path(os.path.join(variable.DIFF_SCRIPTS, "TRANSLATION_REPORT.html"))
    if tr.exists():
        print("*" * 5 + " There is a translation report " + "*" * 5)
        shutil.move(os.path.join(variable.DIFF_SCRIPTS, "TRANSLATION_REPORT.html"), os.path.join(tenant_path, "TRANSLATION_REPORT.html"))
        print(f"[+] Translation report moved to {tenant_path}")
    else:
        print("[-] Translation report NOT found.")
    
        
    #calculate the previous release
   
    if new_release_number == 0:
        previous = "Egg"
    else:
        previous = new_release_number - 1
        
        
    upgrade_folder = f"Upgrade from {previous}"
    downgrade_folder = f"Downgrade to {previous}"

    upgrade_path = tenant_path / upgrade_folder
    downgrade_path = tenant_path / downgrade_folder

    #create the upgrade and downgrade directories
    upgrade_path.mkdir() 
    downgrade_path.mkdir()

    with open(variable.DIFF_SCRIPTS + os.sep + 'release_folders.txt', 'w') as up_down_folders:
        up_down_folders.write(str(upgrade_path) + '\n')
        up_down_folders.write(str(downgrade_path))

    
    custom_path = tenant_path / custom_sql # Not necessary to create this (shutil.copytree will handle it).

    releaseReadMe(str(new_release_folder),'ritehorizon-test', 'ritehorizon-dev')#create the release readme.md file from the parsed and computed info

    #create the versions.txt file
    versioning(new_release_folder, new_release_number) 

    #start new thread for the environment report
    if variable.TENANT:
        
        env_thread = threading.Thread(target=EnvReport, args=(str(tenant_path), 'ritehorizon-test', 'ritehorizon-dev',))
    else:
        env_thread = threading.Thread(target=EnvReport, args=(str(new_release_folder), 'ritehorizon-test', 'ritehorizon-dev',))

    env_thread.name ="Environment_Report_Thread"
    env_thread.start()

    #Move this "custom_sql" files, if any to "custom_sql" for the current release
    print("[i] Looking for 'custom_sql' files now.")
    move_custom_with_exclusion(custom_path)
    print("[+] newBranchingModelFolders function complete. Hope you were not expecting much here, you may be happily surprised if so.")
                
                
def move_custom_with_exclusion(custom_path):
    """Move any SQL files found in the 'releases' directory to the 'custom_sql' folder in the current release.
       'custom_path' should be the URL of the 'custom_sql' folder in the release directory.
       'custom_path' should be a 'str' or a pathlib.Path object, preferably pathlib.Path.
    """
    dev_custom_sql_path = pathlib.Path(variable.RELEASE_DIR) / "custom_sql"
    
    if dev_custom_sql_path.exists():
        pass # The 'custom_sql' folder was found under 'releases'.
    else:
        print(f"[!] Error the release directory 'custom_sql' folder does not exist - r2d2.move_custom(). Cannot find {dev_custom_sql_path}")
        r2d2_logger.error(f"[!] Error the release directory 'custom_sql' folder does not exist - r2d2.move_custom(). Cannot find {dev_custom_sql_path}")
        return    
        
    # If the data-type of 'custom_path' is a string, as it is with testing, then change this variable to a Path object.
    if isinstance(custom_path, str):
        custom_path = pathlib.Path(custom_path)
    try:
        print(f"[+] Copying {dev_custom_sql_path} to {custom_path}.")
        shutil.copytree(dev_custom_sql_path, custom_path, ignore=shutil.ignore_patterns('*.gitkeep'), 
                        dirs_exist_ok=True)  
    except Exception as copy_error:
        print(f"[!] Encountered copy error: {copy_error}")
        exit(1)

    # r=root, d=directories, f=files
    for r, d, f in os.walk(dev_custom_sql_path):
        for file in f:
            if not file.endswith(".gitkeep"): # Don't want to move .gitkeep files.
                source_file_path = os.path.join(r, file)
                print(f"Removing: {source_file_path}")
                os.remove(source_file_path)
    
    print("[+] Function move_custom_with_exclusion is complete.")


def remove_empty_folders(path_abs):
    try:
        walk = list(os.walk(path_abs))
        for path, _, _ in walk[::-1]:
            if len(os.listdir(path)) == 0:
                shutil.rmtree(path)
    except Exception as remove_error:
        print(f"[!] Encountered remove error: {remove_error}")
        exit(1)