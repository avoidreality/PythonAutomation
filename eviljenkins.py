import jenkins
import variable
import re
import requests
#https://python-jenkins.readthedocs.io/en/latest/api.html


repo_job = None

def getServer(repo):
    """Return the Jenkins server to the caller based on the repo name."""
    jenkins_server = None 
    if not repo == "MONO":
        jenkins_server = "http://hostname.foo.local:8080"
    else:
        jenkins_server = "http://hostname.foo.local:8083"

    return jenkins_server

def getJob():
    if variable.MODE == "fizz":
        repo_job = "CI__fizz__fizz-db"
    elif variable.MODE == "MONO":
        repo_job = "CI__monorepo__newhorizon"
    elif variable.MODE == "MARS":
        repo_job = "CI__newhorizon__mars-db"

    return repo_job

def last_build():
    """Return the last build from the fizz-db repository on Jenkins """

    repo_job = getJob()
    #print(f"[+] repo_job in last_build = {repo_job}")
    #print(f"[+] variable.MODE in last_build = {variable.MODE}")

    
    jenkins_server = getServer(variable.MODE)
    
    this_jenkins = jenkins.Jenkins(jenkins_server)
    db_builds = this_jenkins.get_job_info(repo_job)
    return db_builds['lastBuild']['number'] #return the last build number

def find_test_results(jenkins_server="http://ahostname.foo.local:8083", build_number=758,
                      repo_job="CI__monorepo__newhorizon"):
    """Try and find the test results for this build! :) Returns number of test failures, number of tests, and usability (true,false). """

    
    your_jenkins = jenkins.Jenkins(jenkins_server)
    build_info = your_jenkins.get_build_info(name=repo_job, number=build_number)
    action_list = build_info['actions']

    for i,e in enumerate(action_list):
        if isinstance(e, dict):
            try:
                if e['_class'] == 'hudson.tasks.junit.TestResultAction':
                    print("*" * 30) 
                    print("FOUND IT!")
                    print(e)
                    print("*" * 30)
                    if e['failCount'] != 0 or e['totalCount'] < 80000:
                        print(f"[!] Build {build_number} is not usable there are too many fails or not enough tests. Number of fails: {e['failCount']}. Number of tests: {e['totalCount']}")
                        print("There needs to be zero failures and over 80K tests to use an unstable build.")
                        usable = False
                    else:
                        print(f"[*] Build {build_number} is usable.")
                        usable = True
                    return e['failCount'], e['totalCount'], usable
            except Exception as e:
                #print(f"This exception was thrown: {e}")
                pass


def find_your_build(my_build, interactive=False, test=True, experimental=False):
    """This function takes in a build as an argument then searches Jenkins for this build. If found the description is returned to the caller. """

    import time

    result = None
    currently_building = None

    possible_matches = [] #this can store builds that are not successful but are a match

    repo_job = getJob()
    
    #get last build number and start searching from the top for my_build
    last = last_build()

    jenkins_server = getServer(variable.MODE)
    your_jenkins = jenkins.Jenkins(jenkins_server)
    
    count = last
    notfound = True
    timeout = time.time() + 60 * 2 #timeout is 2 minutes 
    while notfound and time.time() < timeout: #run while the release is not found and the timeout is not expired
        
        try:
            #print(f"[+] repo_job in find_your_build = {repo_job}")
            #print(f"[+] variable.MODE in find_your_build = {variable.MODE}")
            print(f"[+] Looking up build number {count}")
            build_info = your_jenkins.get_build_info(name=repo_job, number=count)
        except (requests.exceptions.HTTPError, jenkins.NotFoundException, jenkins.JenkinsException) as e:
            print(f"This exception was thrown in eviljenkins.find_your_build: {e}")
            if f"job[CI__monorepo__newhorizon] number[{count}] does not exist" in str(e):
                print("[+] The build does not exist. Inconveivable. Going to next build now.")
                if (count <= last) and (count > 1):
                    count -= 1 #go to the next build
                    continue
                elif not test:
                    print(f"[!] All builds searched through on {repo_job}. The build '{my_build}' was apparently not found. Please try test mode, there may be an 'unstable' build that is usable.")
                    
                    assert notfound == False,"Your build was not found!"
                else:
                    print(f"[!] All builds searched through on {repo_job}. The build '{my_build}' was apparently not found.")
                    
                    assert notfound == False,"Your build was not found!"
                    
            else:
                break
            
        print(f"Description = {build_info['description']}")
        #print(f"Descrption type = {type(build_info['description'])}")

        if build_info['description']:
            release_data = match = re.search(r"\[.*\]", build_info['description'])
            if release_data:
                #parse the data between the brackets 0.0
                release_brackets = release_data.group()
                print(f"[+] 'release_brackets' = {release_brackets}")
                if test: #this condition does not care if this is a "Branch" or a "Release"
                    print(f"[+] Test mode engaged found something: {release_brackets}")
                    
                elif 'Branch' in release_brackets: #we are interested in 'Artifacts' not Branches :)
                    #count = count - 1
                    #continue
                    pass
                elif 'Artifact' not in release_brackets: #only looking for 'Artifacts'
                    count = count -1
                    continue
                else:
                    print(f'[+] Artifact found: {release_brackets}')
                
                match = re.search(r"\[.*\]", release_brackets) 
                if match:
                    if test:
                        try:
                            newstring = release_brackets.split("[Branch:")[1]
                            newstring = re.sub("]", "", newstring)
                            newstring = newstring.strip()
                        except:
                            print("Exception trying to parse test scenario: {release_brackets}")
                            try:
                                newstring = release_brackets.split("[Artifact:")[1]
                                newstring = re.sub("]", "", newstring)
                                newstring = newstring.strip()
                            except:
                                print(f"Exception trying to parse test scenario: {release_brackets}")
                                newstring = release_brackets
                        
                    else:
                        releaseY = release_brackets.split("[Artifact:")
                        newstring = re.sub("]", "", releaseY[1]) #substitute the ']' for an empty string in the second element of list 'releaseY'.
                        newstring = newstring.strip()
                    print(f"[+] newstring = {newstring}")

                    if "<br>" in newstring:
                        print("[+] Line break found in the string. This may be a manual re-build.")
                        #remove any thing created on a manual re-build that would effect the rest of the logic that follows
                        try:
                            newstring = newstring.split("<br>")[0] #get the first elment in the list that is created
                        except Exception as be:
                            print("[!] Exception thrown trying to split the string on a line break.")
                    
                    #search only for RC1 or RELEASE branches
                    if my_build in newstring:
                        print(f"[+] We may have a match here people: {newstring} looks very much like {my_build}")
                    else:
                        print(f"[-] {my_build} != {newstring}")
                        count = count - 1
                        continue #go to the next build - no need parse everything if this is not a match
                    
                    if ('RC1' in newstring):
                        
                        #print("[+] Found an RC1 or a RELEASE branch.")
                        #test to see if RC1 is in the correct spot
                        
                        #match RC1
                        match_rc1 = re.search(r"^\w+-\d+.\d+.\d+-RC1\s+#[0-9a-f]{8}$", newstring)
                        if match_rc1:
                            print("[+] Authentic RC1 branch found.")

                        elif experimental: #putting this in to test newhorizon-2.3.19-RC1-DCO_Generation
                            pass #this allows a getting a branch like this: newhorizon-2.3.19-RC1-DCO_Generation *Note 'test' should also be set to True.
                            
                        else:
                            print(fr"[+] {newstring} is apparently not *the* RC1 branch")
                            count -= 1
                            continue
                    elif ('RELEASE' in newstring) and not experimental: #if experimental is True and test is True then we can get branches like this: newhorizon-2.3.18-ARELEASE-DCO_Generation

                        #test to see if RELEASE is in the correct spot just before the hexadecimal (a-fA-F0-9) hash. :)
                        #match the RELEASE
                        match_rel = re.search(r"^\w+-\d+.\d+.\d+-RELEASE\s+#[0-9a-f]{8}$", newstring)
                        if match_rel:
                            print("[+] Authentic RELEASE branch found.")
                        else:
                            print(fr"[!] {newstring} is apparently not *the* RELEASE branch.")
                            count -= 1
                            continue
                            

                        
                    elif newstring == 'newhorizon-dev':
                        print("[+] Found the New Branching Model branch 'newhorizon-dev'")
                        notfound = False

                    elif 'newhorizon-dev' in newstring:
                        r = re.match(r'newhorizon-dev\s+#[a-fA-F0-9]{8}', newstring)
                        if not r:
                            print("[+] This looks similar but is not the actual branch we want -> ", newstring)
                            count -= 1
                            continue 

                    elif newstring == "newhorizon-test":
                        print("[+] Found the New Branching Model branch 'newhorizon-test'")
                        notfound = False

                    elif 'newhorizon-test' in newstring:
                        rr = re.match(r'newhorizon-test\s+#[a-fA-F0-9]{8}', newstring)
                        if not rr:
                            print("[+] This looks similar but is not the actual branch we want -> ", newstring)
                            count -= 1
                            continue 

                        

                    elif test:
                        #why do I want to the code to reach this point again?
                        print(f"[+] Found your test branch but not necessarily the build! This is build {newstring}.")
                         
                        
                    else:
                        print(f"[+] Code in else block for : {newstring}")
                        count = count - 1 
                        continue #continue to the next branch if RC1 or RELEASE not in the string 'newstring' and this is not a 'test'.
                       
                    print("[+] Checking the hexadecimal hash.")
                    last_8 = newstring[-8:]
                    hex_match = re.search(r'[0-9a-f]{8}', last_8)
                    if hex_match: #this is probably a hexedecimal number - if the code gets here everything was parsed correctly
      
                        print("[*] Suitable build found! :) ")
                        print(f"[*] The hash found is: {last_8}")

                        if test:
                            #remove the space and # sign as well as the hash
                            newstring = newstring.split(" ")[0].strip() 
                            print(f"[+] The test branch appears to be: {newstring}")
                       
                
                        if my_build in build_info['description']:

                             build_number = build_info['number']
                             
                             result = build_info['result'] #assign result a value
                             print(f"[+] result = {result}")
                             #do not use failed builds (at the present time)
                             if result == "FAILURE":
                                 print("[!] Continuing to the next build. We cannot use builds that built on Jenkins with a result equaling 'FAILURE' at the present time.")
                                 count -= 1
                                 continue #go to the next build
                                 
                             
                             currently_building = build_info['building'] #assign currently_building a value
                             print(f"[+] currently_building = {currently_building}")
                             
                             if interactive:
                                print("[!] Is this your build?")
                                print(f"[*] {build_info['description']}")
                                x = input("(Y/N): ")
                                if x.upper().startswith("Y"):
                                    print("[*] Excellent! Your build was located.")
                                    print("[*] Please see the build info as follows: ")
                                    #print(build_info['displayName'])
                                    #print(build_info['description'])
                                    
                                    print(f"Your build is build number {build_number}.")
                                    print(f"The {build_number} build state is: {result}")
                                    print(f"{build_number} is currently building: {currently_building}")
                                    notfound = False
                                    
                                    return last_8
                                    
                            
                                else:
                                    print("[!] Build not found.")

                             else:
                                if result.strip() == "SUCCESS" and currently_building == False:
                                    print("[*] Suitable build found! :) ")
                                    print(f"[*] {build_info['description']}")
                                    print(f"[*] Your build is build number {build_number}.")
                                    print(f"[*] The {build_number} build was a {result}")
                                    print(f"[*] {build_number} is currently building: {currently_building}")
                                    
                                    notfound = False #break the endless loop
                                    return last_8
                                elif result and currently_building == False and test: #this build was not a success, the build is complete
                                    print(f"[*] Unstable build ({build_number}) found in test mode.")
                                    print("Not advisable to use this for diff scripts or a parachute.")
                                    print(f"[*] {build_info['description']}")
                                    possible_matches.append({build_number: build_info['description']})

                                    fails, tests, usable = find_test_results(jenkins_server=jenkins_server, build_number=build_number, repo_job=repo_job)
                                    
                                    if usable:
                                        #remove this later - as we probably do not want to use unstable builds. Although, Duane's ld_pdb.sh script will load an unstable build. ^_#
                                        notfound = False #break the endless loop
                                        return last_8
                                    else:
                                        #raise Exception(f'Build {build_number} did not pass all tests! Number of fails found: {fails}. ')
                                        print(f"[!] Using this build though there are {fails} unit-test fails out of {tests} tests. Build technically usable: {usable}")
                                        notfound = False #break the endless loop
                                        return last_8
                                        
                                    
                                
                                else:
                                    print("[!] Something went wrong. Does not compute. *Sparks flying components breaking*.")
                        else:
                            print("Build not found.")
                            count = count - 1
                            continue
            
                
                
                
            
                
        count = count  - 1
        print("Code reached the outermost decrement statement.")


    

def grep_build_hash(build_description):
    """This will parse the output of the 'find_your_build' function and return the hash of the build for the new ld_pdb.sh script that uses a hash environment variable for accuracy in batch mode."""
  
    
    import re
    label = None
    build_hash = None
    #print(f"[+] 'build_description' is of type: {type(build_description)}") #string type
    print(f"[+] 'build_description' = {build_description}")

    assert build_description != None, "The build was not found nothing to grep. Quitting from eviljenkins.grep_build_hash"

    #find the 8 hexadecimal hash in the build_description string amongst all the other crap
    #first split the strings based on the brackets.
    new_description = build_description.split("[")
    new_description2 = ''.join(new_description)
    description = new_description2.split("]")
    #print(f"new_description = {description}")

    #\w+-db-\d+.\d+.\d+-\w+-\w+
    for line in description:
        find_label = re.search(r"\w+-db-\d+.\d+.\d+-.*-\w{8}", line)

        if find_label:
            print("[*] Release label found: ", line)
            label = find_label.group()
            print("[*] The label is: ", label)
            break #stop the boat, loop, whatever. :)
        else:
            print("[-] Release label not found.")

    if label:
        build_hash = label.split("-")[-1] #split the string into a list then return the last element in the list that should be a hash
        print("[*] The hash is: ", build_hash)

    return build_hash
        
        
def getHash(release="fizz-db-2.17.5-RELEASE"):
    """Pass in a release to this function and receive a hash for the release. """
    build_description = find_your_build(release)
    build_hash = grep_build_hash(build_description)
    return build_hash
    
    

if __name__ == "__main__":
    print("For the monorepo 'test' mode needs to always be used or the build will not be found.")
    variable.init() #initialize the variable module
    NoGo = True
    while NoGo:
        a_build = input("Enter a build please. Example - (newhorizon-2.3.4-RC1): ")
        if a_build.startswith('mars-db'):
            variable.toggle_variables('MARS')
            print("[+] mars-db found")
            NoGo = False
        elif a_build.startswith('fizz-db'):
            variable.toggle_variables('fizz')
            print("[+] fizz-db found")
            NoGo = False
        elif a_build.startswith('newhorizon'):
            variable.toggle_variables('MONO')
            print("[+] monorepo found")
            NoGo = False
        else:
            print("[+] I did not understand. Please enter either a fizz-db, newhorizon, or a mars-db repo. ")

    #print(f"[+] a_build = {a_build}")
    #print(f"[+] MODE = {variable.MODE}")

    answer = input("Do you want interactive mode? (Y/N): ")
    if answer.upper().startswith("Y"):
        inter = True
    else:
        inter = False
    answer2 = input("Test mode: (Y/N): ")
    if answer2.upper().startswith("Y"):
        test=True
    else:
        test=False

    answer3 = input("Experimental mode: (Y/N): ")
    if answer3.upper().startswith("Y"):
        exp = True
    else:
        exp = False 
    build_hash = find_your_build(a_build, interactive=inter, test=test, experimental=exp)
    print(f"[*] The build hash is: {build_hash}")
                
    

    


