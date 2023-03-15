"""
Screen scraper application


"""

from bs4 import BeautifulSoup
import urllib
import subprocess
import variable
import os
import pathlib

#since GitLab requires authentication lets copy the html and paste it here
#this is easiest to do by pasting from a file and reading from the file

def getSoup(html="scraped.txt", guimode=False):
    """Read an HTML file and return a BeautifulSoup object."""

    if not guimode:
        with open(html_file, 'r') as scraped:
            html = scraped.read()
    else:
        html = html

    if html:
        soup = BeautifulSoup(html, features="html.parser")
        print("{+] We have soup!")

    return soup

def findInfo(soup):
    """Find the info we want the file changes in certain install types."""

    important = []
    strong_tags = soup.findAll('strong')

    for element in strong_tags:
        if 'data-title' in element.attrs:
            print(f"[+] element: {element}")
            print(f"[+] element['data-title'] = {element['data-title']}")
            important.append(element['data-title'])

    return important

def findDir(branch):
    
    directory = None

    try:
        
        out = subprocess.run(['C:\\cygwin64\\bin\\bash', '-lc', f'FindPath.sh {branch}'], #absolute path to bash is for Umesh
        encoding='utf8', capture_output=True)

        print(f"'out.stdout' = {repr(out.stdout)}")
        if out.stderr:
            print(f"Error in ScrapedSchemas.findDir = {out.stderr}")
            
        lines = out.stdout.split("\n") #split on new-lines
        for line in lines:
            print(line)
            if line.startswith("The directory is:"):
                directory = line.split(":")[1] #get the second element after split creates a list
                print(f"Found the directory = {directory}")

    except Exception as de:
        print(f"[+] Exception thrown trying to determine directory structure: {de}")

    if directory:
        print(f"[+] Searching this directory = {directory}")
        return directory.strip() #remove trailing and leading white-spaces
    else:
        print(f"[!] Directory not found! ScrapedSchemas.findDir() finished unsuccessfully.")
        return

def translate_report(even_more_data):
    """This function creates an HTML report for changes found that Redgate cannot produce diff scripts for. These changes are from the SYS and SYSTEM schemas. """
    try:
        print("#" * 10 + " Trying to create the translation report " + "#" * 10)
        f = open('TRANSLATION_REPORT.html', 'w')
        f.write("<!DOCTYPE html>\n")
        f.write("""<html lang="en">\n""")
        f.write("<head>\n")
        f.write("<title>Translation Report</title>\n")
        f.write("<style> table, th, td {border: 1px solid black;} H1 {text-align: center} .LG {background-color:LawnGreen} tr:hover {background-color:#f5f5f5;}</style>\n")
        
        f.write("</head>\n")
        f.write("<body>\n")

        f.write('<table style="width:100%">\n')
        f.write('<tr><th style="background-color:White;">Lost in Translation - Changes in (SYS and SYSTEM)</th></tr>\n')

        for data in even_more_data:
            f.write("<tr> <td>{}</td>  </tr>\n".format(data))
                
        f.write('</table>\n')

        

        f.write("</body>\n")
        f.write("</html>")
        f.close()
    except Exception as e:
        print("[!] The following exception was thrown: ", e)

    else:
        #no exceptions thrown - translation report probably written to disk
        c = os.getcwd()
        p = pathlib.Path(os.path.join(c, 'TRANSLATION_REPORT.html'))
        if p.exists():
            print("[+] Translation report successfully written to disk here: ", str(p))
        else:
            print("!" * 10 + f" Translation report was not written to disk here: {str(p)} " + "!" * 10)

    

    
    

def translate(endless_data):
    """If there are SYS or SYSTEM changes we need figure out which schemas this actually effects.
       In this function anything is possible. In this function we will translate the SYS and SYSTEM changes
       to the schema that was effected. """
    if endless_data:
        if isinstance(endless_data, str):
            endless_data = endless_data.split(r"/")
            
    if endless_data:
        print(f"[?] Translating this: {endless_data}")
        print("[i] Data type of endless_data is: ", type(endless_data))
        if isinstance(endless_data, list):
            schema_name = endless_data[-1].split(".")[0].strip() #the schema name should be the last element in the list
            print("[i] Returning this: ", schema_name)
            return schema_name

def getDiffInfo(important_stuff, directory):
    """parse the important_stuff passed in to find which schemas to scan """
    #print(f"important_stuff is of type: {type(important_stuff)}")

    #print(f"An element of important_stuff is of type: {type(important_stuff[0])}")

    
    just_schema_dml = set()
    just_schema_ddl = set()
    
    install_types = ['conf', 'core', 'dot', 'gen']

    translation_data = set()
    
    for stuff in important_stuff:

        for itype in install_types:
            #print(fr"Searching this path: {directory}/{itype}")
            if stuff.startswith(rf"{directory}/{itype}"):
                inner_stuff = stuff.split(r"/")
                last_thing = inner_stuff[-1]
                #last_thing = remove_new_line(last_thing) #remove new-line chars if this was data is from a file
                #print(f"[+] '{itype}' last_thing = {repr(last_thing)}")
                if last_thing.endswith('.csv'):
                    if len(stuff) > 4:
                        schema = inner_stuff[3]
                        just_schema_dml.add(schema)
                        
                   
                else:
                    if len(stuff) > 4:
                        ddl_schema = inner_stuff[3]
                        if ddl_schema == "SYS" or ddl_schema == "SYSTEM":
                            #"translate" the SYS and SYSTEM code changes in this block
                            if last_thing.endswith(".usr") or last_thing.endswith("_usr.gnt"):
                               print(f"[+] Found a .usr or _usr.gnt file.") 

                               dsn = translate(stuff)
                               if dsn:
                                  just_schema_ddl.add(dsn)
                                  print(f"[i] Translated DDL schema. Adding {dsn} to schemas to compare.")
                            elif last_thing.endswith(".acl") or last_thing.endswith(".rol") or last_thing.endswith(".dblink") or \
                                last_thing.endswith(".dir") or last_thing.endswith("_rol.grnt"):
                                    print(f"[+] Found a change for the translation report: ", stuff)
                                    #create a report
                                    translation_data.add(stuff)
                                    print("[+] Creating a report for SYS and SYTEM changes.")
                        else:
                            #Add all other DDL schemas that are not SYS or SYSTEM to the list of DDL schemas to compare in the diff script generation
                            just_schema_ddl.add(ddl_schema)
                            
                            

        

    if translation_data:
        print("[+] Translation data found...")
        translate_report(translation_data) #create the translation report if the 'translation_data' set is not empty
    #remove SYS and SYSTEM
    else:
        print("[-] No need for a translation report.")

    
    if 'SYS' in just_schema_dml:
        print("Removing 'SYS' from DML")
        just_schema_dml.remove('SYS')
        

    if 'SYSTEM' in just_schema_dml:
        print("Removing 'SYSTEM' from DML")
        just_schema_dml.remove('SYSTEM')
        
    #Caution: Duane points out that a bug potentially exists for DDL if a change in 'sys' or 'system' is not matched by an actual schema change then the changes for that schema are skipped/missed
    #Please see Kanban card with title, "EPIC03 - 5. RedGate DML diff scripts missing new tables/columns in existing schemas".
    if 'SYS' in just_schema_ddl:
        print("Removing 'SYS' from DDL")
        just_schema_ddl.remove('SYS')

    if 'SYSTEM' in just_schema_ddl:
        print("Removing 'SYSTEM' from DDL")
        just_schema_ddl.remove('SYSTEM')
            
    print("*" * 42)
    if not just_schema_dml:
        print("[!] There are not any DML schemas to compare for this release.")
    else:
        print("[+] DML to scan:")
        for number, things in enumerate(just_schema_dml):
            print(number + 1,things)
        print("*" * 42)

    if not just_schema_ddl:
        print("[!] There are not any DDL schemas to compare for this release.")
    else:
        print("[+] DDL to scan:")
        for number, things in enumerate(just_schema_ddl):
            print(number + 1,things)

    print("*" * 42)

    return just_schema_dml, just_schema_ddl


def get_git_diff(branch1, branch2):
    """This will find the differences between the branches. The diffs are returned as a list to the caller."""

    
    #fetch the branches from origin
    try: 
        #fetch all to get new branches. 
        p_instance = subprocess.run(['git', 'fetch', '--all'], check=True, capture_output=False)
    except subprocess.CalledProcessError as CPE:
        print(f"Exception thrown doing a 'git fetch --all'. Please see the following exception: {CPE}")
        #try 1 more time without checking for errors
        print("[+] Re-trying 'git fetch --all'.")
        p_instance = subprocess.run(['git', 'fetch', '--all'], capture_output=False)

    #get the git log output - this will stop the program on error 
    git_commit_out = subprocess.run(['git', 'diff', f'origin/{branch1}..origin/{branch2}', '--name-only' ], \
                                 check=True,capture_output=True, text=True, encoding='utf8')
    
    out = git_commit_out.stdout.split("\n") #put the output into a list

    return out

def remove_new_line(line):
    """Use this function to remove trailing new-line characters (\n)"""
   
    import re
    my_re = re.compile(r'[\n]') #find new-line characters

        
    new_line = my_re.sub("", line)

    return new_line

def WhatToScan(branch1, branch2):
    """Function that calls other functions to automate finding the schemas to scan. DML is the first thing in the returned value. DDL is the second return value."""

    output = get_git_diff(branch1, branch2)
    dir1 = findDir(branch1)
    dml, ddl = getDiffInfo(output, dir1)
    return dml, ddl 
            
            

if __name__ == "__main__":
    my_soup = getSoup()
    important = findInfo(my_soup)
    getDiffInfo(important)

    

        

        

