import re
import pathlib 
import os
import argparse

"""
This module will remove CREATE OR REPLACE trigger $DML statements from files.
To use this just provide a path or ideally a Python pathlib path to the 'simply' function. 

"""

file = r"""C:\workspace\foo\foo-db\releases\diff_script_files\SchemaComparison\schema-files\DB_ENTITY_DIFF.sql"""

p = pathlib.Path(file)

unwanted = []
starts = []

def simply(p):

    while 1:

        s = findTrigger(p)
        
        if s == None:
            break
        else:
            e = findEnd(s, p)
            removeTrigger(p, s, e)


    print("[+] Program complete.")
    



def findTrigger(p):
    """Give this function a path and the program will search for $DML trigger statements"""
    with open(p, 'r') as f:
        lines = f.readlines()
        
        start = None; 

        for i, line in enumerate(lines):
             
             match = re.search(r'^CREATE\sOR\sREPLACE\strigger.*[$]DML', line)
             if match:
                 print("[+] Match found at line %d. Check it out: %s" % (i, match.group()))
                 start = i
                 break #out of the loop once the first match is found
                 
                 
    return start

def findEnd(start, p):
    """Pass the return value from 'findTriggers' to this function to get the corresponding end of the trigger in terms of line number"""
    with open(p, 'r') as f:
        lines = f.readlines()
    
    print("[+] The trigger begins at line [%d] human" % (start + 1))
    for i in range(start, len(lines)):
        
        match_end = re.search(r"^/$", lines[i])
        
        if match_end:
          print("[++] Found the closing slash of the trigger at line [%d] human." % (i+1))
          
          end = i

          #foo = input("This is the end: %d human" % (i + 1))
          break #out of the inner loop back to the start

    return end

def removeTrigger(p, start, end):
    """This function takes the path and a list of dictionaries returned from 'findEnds'"""
    with open(p, 'r') as f:
        lines = f.readlines()

    print("[+] Start = %s" % start)
    print("[+] End = %s" % end)

    del lines[start: (end+1)]

    print("[+] Trigger removed")

    with open(p, 'w') as dollar:
        for line in lines:
            dollar.write(line)

    import os
    location = os.getcwd()
    print("File %s written to disk here: %s" % (p.name, location))

def findTriggers(p):
    """Give this function a path and the program will search for $DML trigger statements"""
    with open(p, 'r') as f:
        lines = f.readlines()
        
        start = None; end = None;

        for i, line in enumerate(lines):
             
             match = re.search(r'^CREATE\sOR\sREPLACE\strigger.*[$]DML', line)
             if match:
                 print("[+] Match found at line %d. Check it out: %s" % (i, match.group()))
                 start = i
                 starts.append(start)
                 
                 #blah = input("now looking for the ending slash!")
                 match_end = re.search(r"^/$", line)
                 if match_end:
                     print("[++] Found the closing slash of the trigger at line: %d." % i)
                     end = i
    return starts

def findEnds(starts, p):
    """Pass the return value from 'findTriggers' to this function to get the corresponding end of the trigger in terms of line number"""
    with open(p, 'r') as f:
        lines = f.readlines()

    
    for begin in starts:
        print("[+] The trigger begins at line [%d] human" % (begin + 1))
        t = {} #this dictionary will hold start and end line numbers
        t['start'] = begin
        for i in range(begin, len(lines)):
            
            match_end = re.search(r"^/$", lines[i])
            
            if match_end:
              print("[++] Found the closing slash of the trigger at line [%d] human." % (i+1))
              t['end'] = i
              unwanted.append(t)
              end = i

              #foo = input("This is the end: %d human" % (i + 1))
              break #out of the inner loop back to the start

    return unwanted

def removeTriggers(p, rw):
    """This function takes the path and a list of dictionaries returned from 'findEnds'"""
    with open(p, 'r') as f:
        lines = f.readlines()

    for triggers in rw:
        start = triggers['start']
        print("Start -> %s" % lines[start])
        end = triggers['end']
        print("End -> %s" % lines[end])
        x = input("The start is %d and the end is: %s." % (start, end))
        #del lines[start: (end +1)]

    with open("DB_ENTITY-SANS-$DML.sql", 'w') as dollar:
        for line in lines:
            dollar.write(line)


def cleanDir(dir_dump):
    """This will loop through the directory and clean all the SQL files of the $DML triggers. """

    os.chdir(dir_dump)
    p = pathlib.Path('.')
    files = p.glob("*.sql")
    files = list(files)

    for f in files:
        simply(f)

    


#rs = findTriggers(p)
#rw = findEnds(rs, p)
#removeTriggers(p, rw)

#print("[!] Found %d $DML triggers in %s." % (len(starts), (p.name)))
#print("[!] Found %d this many sets of starts and ends" % len(rw))
#print(unwanted)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--remove", help="Please give the directory with all the SQL files to remove the $DML triggers from.", required=False)
    parser.add_argument("-i", dest="interactive", action="store_true", help="Interactive mode. Type this option to specify a path to a SQL file to remove $DML triggers from.")

    args = parser.parse_args()

    if args.remove:
        p = pathlib.Path(str(args.remove).strip())
        cleanDir(p)

    if args.interactive:
        x = input("Please specify a path to remove $DML triggers: ")

        p2 = pathlib.Path(x.strip().replace('"', ''))
        simply(p2)
    


          
    

                 

         

            

        
             
