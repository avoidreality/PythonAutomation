"""
This should help automate the unit-tests.

aspersions - An attack on the character or integrity of something.

Unit tests help with the integrity of the code. This module should
help by not having people casting aspersions about poorly written code. :D

The following four steps install the pdb, switch to the correct branch, generate the schema data, and commit-stage-push the code to GitLab.
Step 1: reinstall_pdb3(pdb3)
Step 2: switch_branches(branch_name)
Step 3: foo_proc()
Step 4: git_bot()

6/3/2020 
ksmith

"""

import logging
import os
import subprocess
import re
import time
import argparse

import pdb_bot
import clean_pdbs
import ConnectToOracle
import awesome

WORKTREE3= "C:\\workspace\\foo\\foo-db_FOOPDB3"

#logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

aspersions_logger = logging.getLogger('aspersions-log')
if not aspersions_logger.handlers:
    aspersions_fh = logging.FileHandler('aspersions-debug.log')
    aspersions_logger.setLevel(logging.DEBUG)
    aspersions_fh.setFormatter(formatter)
    aspersions_logger.addHandler(aspersions_fh) #add the file handler to the logger

def reinstall_pdb3(pdb3):
    """ Remove the PDB in slot 3. Clean PDB3. Load PDB3. Make sure PDB3 is open. Supply the name of the PDB to load to the 'pdb3' parameter.""" 
    
    #Let's remove the PDB and then load a new PDB
    #
    #first get this current directory to switch back to later
    current_dir = os.getcwd()
    aspersions_logger.debug(f"The current directory is: {current_dir}")
    
    aspersions_logger.info("Removing PDB 3 now. This will take several minutes.")
    print("[+] Removing PDB3 now.")
    pdb_bot.remove_the_pdb(3)
    
    aspersions_logger.info("Bouncing the database and cleaning any files found in PDB3.")
    print("Bouncing the database and cleaning any files found in PDB3.")

    #delete any leftover files in PDB 3 - bounce the Oracle DB
    clean_pdbs.clean_a_pdb(3) 

    # load the PDBs
    #1st lets check if we have the names of the PDBs to load if not the program will stop
    assert pdb3, "You need to specify PDB3 please."
    
    aspersions_logger.info(f"Now loading {pdb3} in slot 3.")
    print(f"[+] Now loading {pdb3} in slot 3.")
    
    pdb_bot.load_the_pdb(3, repr(pdb3))

    
    #after the load/unload PDB business is complete switch back to the main directory so the script will run as expected
    os.chdir(current_dir)
    current_dir = os.getcwd()
    aspersions_logger.debug(f"Done cleaning the databases. Back to work... The current directory is: {current_dir}")


    #make sure PDB3 is open - need to write more code in pdb_bot.py to make sure just a single module is open.
    print("")
    print("*" * 70)
    print("[+] Making sure the PDB3 is open.")
    print("*" * 70)
    #make sure databases are in READWRITE mode
    pdb_bot.open_pdb3()
    print("*" * 70)
    print("*" * 70)

def foo_proc():
    """Execute the foo procedure in the SCRIPT_GEN package to generate the 'wtp' schema. """

    magic_wand, potter_connection = ConnectToOracle.db_stuff("bizzPDB3") #get a cursor, the object that can query the database

    whoami = magic_wand.execute("SELECT SYS_CONTEXT ('USERENV', 'SESSION_USER') FROM DUAL")
    print("The current user is: %s " % str(whoami.fetchone()))
    whereami = magic_wand.execute("select name from v$services")

    if whereami:
        name = whereami.fetchone()
        if name:
           print(f"[+] Name: {name}")
         

    magic_wand.callproc('script_gen.schemas', ['wtp', 'WTP'])

    print(f"'magic_wand' return type = {type(magic_wand)}")
    print(f"'magic_wand' = {magic_wand}")

    magic_wand.close() #close the cursor - free up database resources

def switch_branches(branch_name):
    """Switch branches to the correct branches to push changes to."""

    #step 0 - Make sure we are in the correct repository - I think we need to use the bizzPDB3 .git repo because this is where the changes will happen.
    os.chdir(WORKTREE3)

    #step 0.5 
    #lets fetch new branches first
    print("[+] Fetching new branches from origin.")
    fetch_output = subprocess.run(["git", "fetch", "--all"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if fetch_output.stdout:
        print(f"[+] Fetch output stdout = {fetch_output.stdout}")
    if fetch_output.stderr:
        print(f"[+] Fetch output stderr = {fetch_output.stderr}")
    #step 1 - Let's see if the current branch is the correct branch.
    current_b = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if current_b.stdout:
        print(f" current_b.stdout = {repr(current_b.stdout)}")
        if current_b.stdout == branch_name + "\n":
            print(f"[+] The current branch is the branch you wanted to check out. Excellent. Current branch is: {current_b.stdout} ")
            return
        else:
            """
            #find the difference and tell the end-user about it
            print(f"The length of current_b is: {len(current_b.stdout)}")
            print(f"The length of branch_name is: {len(branch_name)}")
            for i,v in enumerate(current_b.stdout):
                print(i, repr(v), ' ', end='')

            for i,v in enumerate(branch_name):
                print(i,repr(v), ' ', end='')

            print()

            
            for i,v in enumerate(current_b.stdout):
                
                if i < len(current_b.stdout) and i < len(branch_name):
                    if current_b.stdout[i] != branch_name[i]:
                        print(f"'Current_b' does not match 'branch_name' at character:{i} with value: {v}.")
            """ 
            print(f"[+] Checking out branch: {branch_name}")
            #i may want to add the "--track" switch and pre-pend "orgin/" to the 'branch_name' for a remote branch. I am not sure though. 6/11/2020.
            check_ret = subprocess.run(['git', 'checkout', branch_name], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if check_ret.stdout:
                print(f"[+] stdout: {check_ret.stdout}")
            elif check_ret.stderr:
                print(f"[+] stderr: {check_ret.stderr} ")

            return
            
    elif current_b.stderr:
        print(f"[!] Branch not changed. Error. STDERR - current_b: {current_b.stderr}")
        return

    

def git_bot():
    """Check in the correct stuff to Git. This should be run after the PDB is loaded, the branch is checked out,
       and after the foo_proc() has been executed.
    
    """
    parsed_stdout = ''
    parsed_stderr = ''

    os.chdir(WORKTREE3) #change to PDB3's .git directory 

    #The one-liner below works great in Cygwin and cmd.exe :) This finds the interesting lines.
    #win_output = subprocess.run(['git', 'status', '|', 'findstr', 'install/wtp/WTP/WT_*'], shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, text=True)

    #The one-line below works great in Cygwin since Cygwin has the 'grep' command. This also finds the interesting lines but only works on Cygwin
    nx_output = subprocess.run(['git', 'status', '|', 'grep', r'install/wtp/WTP/WT_*'],  stdout=subprocess.PIPE, stdin=subprocess.PIPE, text=True)

    #parse the unix output- we already have to use unix to load the PDB. :)
    if nx_output.stdout:
        parsed_stdout = nx_output.stdout
        print(f"[+] parsed_stdout = {parsed_stdout}")

        parsed_output_list = parsed_stdout.split()

        print("#" * 70)
        print("Important files".center(70))
        print("#" * 70)

        count = 0 #count important files found
        #lets try to only find the lines with the 'WT_' files
        files_to_stage = [] 
        for line in parsed_output_list:
            mods = re.search(r"WT_.*$", line)
            if mods:
                count += 1
                print(f"[+] Staging this file: {line}")
                stage_out = subprocess.run(['git', 'add', line], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) #stage the relevant files
                files_to_stage.append(line)
                print(f"[+] Stage STDOUT: {stage_out.stdout}")
                print(f"[-] Stage STDERR: {stage_out.stderr}")
                print(f"[+] {line} staged.")
                
                
                

        if count == 0:
            print("[+] No important files found. This maybe a problem Mr Burns.")
        elif count > 0:
            print("[+] Committing important files staged.")
            subprocess.run(['git', 'commit', '-m', f'Committing these files via Python: {files_to_stage}'], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"[+] Pushing changes to GitLab.")
            push_return = subprocess.run(['git', 'push'], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if push_return.stdout:
                print(f"[+] STDOUT PUSH_RETURN: {push_return.stdout}")
            if push_return.stderr:
                print(f"[-] STDERR PUSH_RETURN: {push_return.stderr}")

        print("#" * 70)
        print("Excellent! Process complete.".center(70))
        print("#" * 70)

    if nx_output.stderr:
        parsed_stderr = nx_output.stderr
        print(f"[+] parsed_stderr = {parsed_stderr}")


def create_branch(new_branch, rc_branch, token):
    """ This uses the GitLab API V4 REST API to create a branch. The "new_branch" is created off of the "rc_branch" using the "token" for authentication. """
    import requests

    URL = "https://gitlab.foohosted.com/api/v4/projects/fizz%2Ffizz-db/repository/branches"
    JSON = {}
    HEADERS = {}
    HEADERS['Private-Token'] = token
    JSON['ref'] = rc_branch
    JSON['branch'] = new_branch

    reply = requests.post(url=URL, headers=HEADERS, data=JSON)
    

    print(f"Is the reply OK? Answer: {reply.ok}")
    print("*" * 70)
    print(f"create_branch reply: {reply.content}")
    print("*" * 70)

    return reply.ok, new_branch

def check_build_output(build_number):
    """Pass in a build number and the code will give information on if the build was successful or not.
       If this is a branch the return value will be "True, None".
       If this is a database build the return value will be "True, fizz-db-2.11.6-foobar" for example. So if the 2nd return value is not none
       this is an artifact or database build and not just a branch build. 
    """

    #inject the URL with the 'build_number' - do not try this at home. :)
    import requests
    import re

    URL = f"http://hostname.foo.local:8080/job/CI__fizz__fizz-db/{build_number}/logText/progressiveText?start=0"

    reply = requests.get(url=URL)
    branch = None

    if reply.ok:
        output = reply.text.split('\r\n')
        
        for line in output:
            
            branch_name = re.search(r"^☀ gitlabSourceBranch=", line)
            if branch_name:
                print(f'[+] Branch Name Found for #{build_number}: {line}')
                branch = line.split("=")[1] #get the branch name after the equals sign. This should be element 1.
                print(f'[+] Branch name for build #{build_number} = {branch}')
                
            found = re.search(r'Finished: SUCCESS', line)
            if found:
                print(f'[+] Build #{build_number} successful!')
                #print(line)
                return "SUCCESS", branch

            fail_found = re.search(r'Finished: FAILURE', line)
            if fail_found:
                print(f"[-] Build #{build_number} Failure!")
                return "FAILURE", branch

        return "INCOMPLETE", branch #return this if the branch is found but the "Finished: <STATE>" line was not found. This means the branch is currently building most likely.
    else:
        print("[-] The reply was not ok. Please check build_number and try again.")
        return "BADHTTP-REPLY", branch #return False if the URL did not return successfully.


def build_branch(branch_name):
    """Call Jenkins's REST API to start a manual rebuild.
       This is the same as accessing the web interface at the following URL:http://hostname.foo.local:8080/job/REBUILD_CI_PROJECT/
    """
    import requests

    URL = f"http://hostname.foo.local:8080/job/REBUILD_CI_PROJECT/buildWithParameters?NAMESPACE_AND_PROJECT=fizz/fizz-db&GIT_BRANCH={branch_name}"

    reply = requests.post(url=URL)

    if reply.ok:
        print("[+] The build should be starting... ")
        print("Please check the following page: hostname:8080/job/CI__fizz__fizz-db/")
    else:
        print("[!] Something went wrong! Did you enter the correct 'branch_name'?")

    return reply.ok

def find_jenkins_builds():
    """Use the Jenkins REST API and XPATH to find the first 10 builds recently built."""

    import requests

    build_numbers = [] 
    
    #loop through the and get the first ten build numbers - return them to the caller
    for i in range(11):
        URL = f"http://hostname-vmli.foo.local:8080/job/CI__fizz__fizz-db/api/xml?xpath=//build[{i}]/number"
        reply = requests.get(URL)

        if reply.ok:
            print(f"[+] {i}.) Jenkins build number found: {reply.text}")
            build_num = re.findall('[0-9]+', reply.text)
            if build_num:
                build_numbers.append(*build_num)
            


    return build_numbers

def build_status(branch_name, build_number=None, timeout=40):
    """This function should poll the Jenkins server every few seconds for 40 minutes max to determine if the build was successfully built.
       #60 minute timeout - A build should not take more than this time, but could if there is a queue on Jenkins.

    """

    start_time = time.time()
    

    my_build = None #find your build and then check the status of the build
    my_build_number = None
    done = False
    TIME = timeout * 60 
    
    

    build_numbers = find_jenkins_builds() # get the first 10 builds on Jenkins as build numbers
    for number in build_numbers:
        finished_state, branch_found = check_build_output(number)
        
        if branch_found:
            #print(f"This is what is in 'branch_found': {branch_found}")
            if branch_found.strip() == branch_name.strip():
                print("*" * 80)
                print(f"[+] Target branch {branch_name} from build {number} found!")
                print("[!] Now we need to make sure the build is complete.")
                print("*" * 80)
                my_build = branch_found.strip()
                my_build_number = number
                break


    if not my_build:
        print("[!] Branch not found.")
        return my_build, my_build_number, False #if the branch is not found return (None, None, False) - False means the build is not complete

    #if the build fails the we should return before waiting for a timeout
    
        
    while not done and my_build and my_build_number: #do this until we find the build and 'my_build' is not empty - 'my_build' will be empty if if this is just a branch and not a pdb
        if round(time.time() - start_time) > TIME:
            print("[!] Timeout reached in 'build_status' function.")
            return my_build, my_build_number, False
        
        print("[+] Checking to see if the build is complete...")
        elapsed_time = time.time() - start_time
        time_left = TIME - elapsed_time
        print(f"[+] Timeout in: {round(time_left/60,1)} minutes.")
        finished, vip_branch = check_build_output(my_build_number)
        if finished == "SUCCESS":
            print("*" * 80)
            print("[+] The build is complete.")
            print("*" * 80)
            done = True
            return my_build, my_build_number, True #return the build name, build#, and True that the build completed
        elif finished == "FAILURE": #this code would be reached if we were waiting and then the build failed. 
            print("!" * 80)
            print("[!] The build failed.")
            print("!" * 80)
            done = True #exit from the endless loop and get on with your programmatic life. (:
            return my_build, my_build_number, False #return my_build, my_build_number, and False that the build failed
        else:
            print(f"[!] Still waiting for the build {my_build_number} to complete. Build not finished. 'finished' = {finished}")
            

        time.sleep(30) #sleep for 30 seconds - do not poll constantly


def merge_request(target_branch,source_branch, name, token):
    """Create a merge request. The 'name' variable is the title of the merge request. The 'token' is a GitLab launch code that will expire.
       The 'target_branch' is the branch to merge into or merge destination. The 'source_branch' is the branch to merge into another branch.
       "I'll stop the world and merge with you...the future is open wide." 
    """
    #comments below show how to merge with GitLab using cURL. :)
    #curl --request POST --header "Private-Token: WJdkXyzLRCAYJGP6-pFK"
    #"https://gitlab.foo.com/api/v4/projects/fizz%2Ffizz-db/merge_requests?target_branch=fizz-db-2.11.6-rest-computer-man&source_branch=fizz-db-2.11.6-rest-foobar&title=rest-merge-request-foobar"
    import requests
    HEADER = {}
    HEADER["Private-Token"] = token

    URL = f"https://gitlab.foohosted.com/api/v4/projects/fizz%2Ffizz-db/merge_requests?target_branch={target_branch}&source_branch={source_branch}&title={name}"

    reply = requests.post(url=URL, headers=HEADER)

    if reply.ok:
        print("[+] Merge request reply is OK.")
    else:
        print("{+] Merge request reply is not OK.")
        
def run(new_branch, rc_branch, token, pdb3, merge_title, debug):
    """This function will call the other functions to do what Duane wants the computer to do.
       
        1.) Create branch off the RC branch - create_branch()
        2.) Build the branch - build_branch()
        Build the database with the instructions at step 3 shown in the URL below:
        https://gitlab.foohosted.com/fizz/fizz-db/-/wikis/start-jenkins-build
        3.) Make sure Jenkins build succeeds - build_status()
        4.) Load the PDB in slot 3 - reinstall_pdb3() #this depends on step 2
        5.) Log into PDB3 as foo/foo and run the following one-liner: execute SCRIPT_GEN.schemas('wtp','wtp') - switch_branches() + foo_proc()
        6.) Stage-Commit-Push bizzPDB3 - git_bot()
        7.) Ensure build succeeds on the Jenkins build server - build_status()
        8.) Create a merge-request  - merge_request
    """
    print("[+] Run function engaged.")

    #step 1 - create the branch
    print(f"[+] Creating new branch: {new_branch}.")
    create_branch(new_branch=new_branch, rc_branch=rc_branch, token=token)

    awesome.slowdown()

    #step 2 - build the branch
    print("[+] Building the branch.")
    build_branch(branch_name=new_branch)

    if debug: 
        awesome.slowdown()

    #step 2.5 - sleep
    print(f"[+] Sleeping for 120 seconds to give Jenkins some time to materialize the build for {new_branch}")
    time.sleep(120)

    print("[+] Confirming the build is successful.")
    #step 3 - confirm build
    my_build, my_build_number, build_state = build_status(new_branch)
    if my_build and my_build_number and not build_state:
        print(f"[!] Build {my_build_number} with name {my_build} is having problems.")
    elif my_build and my_build_number and build_state:
        print(f"[+] The build {my_build_number} is a success for {new_branch} with branch name {my_build_number}") 
    else:
        print(f"[!] The build failed for {new_branch}.")
        exit() #Stop the program if the build failed. The build must be successful to continue with the following steps.

    if debug: 
        awesome.slowdown()

    #step 4 - load PDB in slot 3 - This could take place at step 1, in the background, since this will take a while
    print("[+] Loading PDB3 with the new build.")
    reinstall_pdb3(pdb3)

    if debug:
        awesome.slowdown()

    print("[+] Switching to new branch and generating SQL scripts.")
    #step 5 - switch Git branches and execute the SCRIPT_GEN procedure
    switch_branches(new_branch)
    foo_proc()

    if debug:
        awesome.slowdown()

    print("[+] Stage, committing, and pushing files to origin.")
    #step 6 - stage-commit-push to bizzpdb3
    git_bot() #this should start a build because [ci-skip] is not in the commit message

    if debug:
        awesome.slowdown()

    print("[+] Sleeping for 120 seconds to give Jenkins some time to get up from the atrium and create the build.")
    time.sleep(120)

    print("[+] Seeing if build succeeds.")
    #step 7 - check if the build succeeds
    build, build_number, build_state = build_status(new_branch)
    if build and build_number and not build_state:
        print(f"[!] Build {build_number} with name {build} is having problems.")
    elif build and build_number and build_state:
        print(f"[+] The build {build_number} is a success for {new_branch} with branch name {build}") 
    else:
        print(f"[!] The build failed for {new_branch}.")

    if debug:
       awesome.slowdown()

    print("[+] Creating merge request.")
    #step 8 - create merge request
    merge_request(target_branch=rc_branch, source_branch=new_branch,name=merge_title, token=token)
    

    print("[+] Run function complete.")
        

if __name__ == "__main__":
          print("*" * 70)
          print("This program will only work from a Cygwin shell on Windows.")
          print("*" * 70)
          started = time.time()

          parser = argparse.ArgumentParser(description="A module to automate unit-test reports or something.")

          parser.add_argument("--debug", "-d", action="store_true", help="Use this option to step through the run method.")
          parser.add_argument("branch", action="store", help="Specify your new branch to create and make changes to.")
          parser.add_argument("target_branch", action="store", help="Specify the RC1 to merge to.")
          parser.add_argument("token", action="store", help="Specify your GitLab authentication token.")
          parser.add_argument("merge_title", action="store", help="Give your merge a fancy title please.")
          parser.add_argument("pdb3_name", action="store", help="Please give the name of your PDB to load in slot 3.")

          parsed = parser.parse_args()

          try: 
              run(new_branch=parsed.branch, rc_branch=parsed.target_branch, token=parsed.token, \
                  pdb3=parsed.pdb3_name, merge_title=parsed.merge_title, debug=parsed.debug)

          except Exception as e:
              print("[+] Wham kablam bang! The tin man falls down the stairs and rusts into garbage in the blink of the scarecrow's eye." +
                    "The yellow brick road must be here somewhere. Don't give up.\n" +
                    f"This exception was thrown: {e}")

          print("[+] Program complete.")
          print(f"[+] Program ran for {round((time.time() - started) / 60, 2)} minutes.")
          

