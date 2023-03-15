import subprocess
import re
import pathlib
import os
import argparse
import variable

f1 = None
s = None
e = None

#start_dir = os.getcwd()

#p = pathlib.Path(r'C:\workspace\foo\foo-db') #script should always be executed in the main worktree

#os.chdir(p)

#print("[+] The current dir is: %s" % os.getcwd())


def checkStartDir():
    """ """

    start_dir = os.getcwd()

    start_path = pathlib.Path(start_dir)

    p = pathlib.Path(variable.GIT_REPO) #script should always be executed in the main worktree of the Git repository

    if start_path != p:
        os.chdir(p)
        print("[+] The current dir is now: %s. We are ready to rock." % os.getcwd())

def head(file):
    """This method imitates the bourne again shell (BASH) program 'head'."""
    f = open(file)
    lines = f.readlines()

    return lines[0]


def slowdown():
    """just pause for a moment and breath deep."""
    x = input("Do you want to continue? (y/n) ")
    if x.lower().startswith('y'):
        pass
    else:
        exit()

def get_diff_info(first, second, environment, verbose=False):
    """Given the arguments passed in, first and second, the git diff data should be returned
       and a report created.
    """
    
    if variable.MODE == "MONO":
        command = """git diff -U0 origin/{}..origin/{} -- EGGS/install/{}""".format(first, second, environment)
    else:
        command = """git diff -U0 origin/{}..origin/{} -- install/{}""".format(first, second, environment)

    try:
        r = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) # This seems to prevent the UnicodeDecodeError
        #r = subprocess.getoutput(command) #this can throw a UnicodeDecodeError
    except Exception as eg:
        print(f"[!] There was an exception running the 'git diff' command to create the environment report. The exception was: {eg}")

    #if this returns successfully the output should be a String
    #I want to parse the string more easily by turning the string to a list

    r_output = r.communicate() #retrieve the output
    output_string = r_output[0] #all output seems to be in the first tuple
    try: 
        output_string = output_string.decode('utf-8') #convert from bytes to strings
    except UnicodeDecodeError as UDE:
        print(f"This exception was thrown trying to decode the bytes string to utf-8: {UDE}")
    finally:
        output_string = str(output_string)
        
    output = output_string.split("\n")

    if verbose:
        #print the output
        for line in output:
            print(line)

    #lets try to write a re to only find the lines that were added
    #These lines will begin with a plus symbol followed by a line number

    #store matches of added lines of source code in the following list
    matches = []

    

    for line in output:
        
        tmp_code = []
        
        
        file_name = re.search('^[+]{3}.*$', line)
        
        if file_name:
            #print("[+] Found this file: %s" % line)
            file = line

        #the line may begin with a plus or a minus possibly followed by a dash maybe with a double quote followed by word characters. Is this your card, I mean line?
        match = re.search('''^[+|-][-]?["]?\w+''', line) 
              
        if match:
            #print("[*] Match found!")
            #print("[+] " + line + " in file: %s" % file)
            data = {}
            data[file] = line
            matches.append(data)
                      
    
##    print("\n")
##    print("*" * 49)
##    print("*" * 10 + " Found the following matches " + "*" * 10)
##    for match in matches:
##        print(match)
##    
##        
##    print("*" * 49)
##    print("")
    

    

    return matches


def allInAll(first, second):
    """Just create the table from the matches based on the first branch second branch and the environment variables."""

    f = open('ENVIRONMENT_REPORT.html', 'w')
    f.write("<!DOCTYPE html>\n")
    f.write("""<html lang="en">\n""")
    f.write("<head>\n")
    f.write("<title>Environment Report</title>\n")
    f.write("<style> table, th, td {border: 1px solid black;} H1 {text-align: center} .FB {background-color:FireBrick} .SG {background-color:SeaGreen} tr:hover {background-color:#f5f5f5;}</style>\n")
    f.write("</head>\n")
    f.write("<body>\n")

    if variable.MODE == "FOO":
        environments = ['lcl', 'dev', 'prod', 'test', 'trn', 'uat', 'cit', 'sit']
    elif variable.MODE == "MONO":
        if variable.TENANT == 'dot':
            environments = ['dot']
        elif variable.TENANT == 'rnd':
            environments = ['rnd']
    elif variable.MODE == "EGGS":
        environments = ['lcl', 'dev', 'prod', 'test', 'trn', 'uat', 'cit', 'sit', 'dot', 'rnd']
        
        
    if environments:
        for env in environments:
            matches = get_diff_info(first, second, env)
            print("[+] Now processing {} environment from {}".format(env,os.getcwd()))
            #slowdown()
            
            
            f.write("<h1>Code Changes Between {} and {} in {}</h1>\n".format(first,second,env))
            f.write('<table style="width:100%">\n')
            f.write('<tr><th>+/-</th><th>File</th><th>Code Changes Between {} and {} in {}</th></tr>\n'.format(first,second,env))
            
            for match in matches:
                k,v = match.popitem()
                
                line = v
                #print("k = {}".format(k))

                color = 'DeepPink'
                
                if line[0].strip() == '+':
                    color = 'SG'
                    #print("in if color = %s" % color)
                else:
                    color = 'FB'
                    #print("In else and line[0] = %s" % line[0])
                f.write("<tr> <td class={}>{}</td> <td>{}</td> <td>{}</td> </tr>\n".format(color,line[0],k, line))

            

            f.write('</table>\n')

    f.write("</body>\n")
    f.write("</html>")
    f.close()

    print("[+] ENVIRONMENT_REPORT.html for all environments written to disk at the following location: %s" % os.getcwd())



def createReport(matches):
    """Create an HTML report showing lines that have been added to the branch based on the git diff command."""
    
    os.chdir(start_dir)
    
    with open('ENVIRONMENT_REPORT.html', 'w') as f:
        f.write("<!DOCTYPE html>")
        f.write("<html>")
        f.write("<head>")
        f.write("<title>Environment Report</title>")
        f.write("<style> table, th, td {border: 1px solid black;} H1 {text-align: center}</style>")
        f.write("</head>")
        f.write("<body>")
        f.write("<h1>Code Changes Between {} and {} in {}</h1>".format(f1,s,e))
        f.write('<table style="width:100%">')
        f.write('<tr><th>+/-</th><th>File</th><th>Code Changes Between {} and {} in {}</th></tr>'.format(f1,s,e))
        
        for match in matches:
            k,v = match.popitem()
            
            line = v
            print("'line[0] = {} and the type is: {}. ASCII = {}".format(line[0], type(line[0]), line[0].isascii()))

            color = 'DeepPink'
            
            if line[0].strip() == '+':
                color = 'SeaGreen'
                print("in if color = %s" % color)
            else:
                color = 'FireBrick'
                print("In else and line[0] = %s" % line[0])
            f.write("<tr> <td bgcolor={}>{}</td> <td>{}</td> <td>{}</td> </tr>".format(color,line[0],k, line))

        

        f.write('</table>')

        f.write("</body>")
        f.write("</html>")

    print("[+] ENVIRONMENT_REPORT.html written to disk at the following location: %s" % os.getcwd())






if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--first', help="Enter the first branch to diff")
    parser.add_argument('--second', help="Enter the second branch to diff")
    parser.add_argument('--env', help="Enter the environment to check. Example: lcl, dev, prod, test, trn, uat ")

    args = parser.parse_args()
    print(args)

    first = args.first
    print(f"The first branch is: {first}")
    f1 = first

    second = args.second
    print(f"[+] The second branch is: {second}")
    s = second

    environment = args.env
    print(f"[+] The environment is: {environment}")
    e = environment

    if (e == "all"):
        """Loop through all the environments and generate a report for each"""
        print("[+] All in all mode engaged.")
        checkStartDir()
        allInAll(f1, s)
    #generate report
    else:
        checkStartDir()
        m = get_diff_info(first, second, environment)
        createReport(m)

    #--first foo-db-2.2.8 --second foo-db-2.1.0 --env lcl
    

    
    

    
    


        






