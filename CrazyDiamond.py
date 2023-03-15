
import subprocess
import os
import glob
import time
import getopt
import sys
from tqdm import tqdm
import awesome
import pdb



def helpMe():
    """This function tells the end-user how to use the program."""
    print("""

Shin  on  r zy  i mon  -   O  i     n r tor 
    X    . X   X X   X   x.  X XX XX X X    
    X    . X   X X   X   x.  X XX XX X X    
    X    . .   X .   X   x.  X XX XX X .    
    X    . .   X .   X   x.  X XX .X X .    
    X    . .   X .   X   x.  X .. .X X .    
    .    . .   X .   X   x.  X .. .. . .    
                                            
Shine on crazy diamond - DCO/OCP diff generator

    
                                            


    """)

    print('python %s -g"path to dco files" -d"path to where to drop diff scripts"' % sys.argv[0])
    print('python %s --generate"path to dco files" --diff"path to where to drop diff scripts"' % sys.argv[0])
    
    print("")
    print("Give the program a directory of DCO files and a directory to dump the diff scripts. :)")
    
def generateDiffScripts(directory, diff_dump, schema_compare, re_diff=False, filters=False):
    """This function will execute the 'DCO' program by RedGate in a loop. """

    program = ''

   
    if not os.path.exists(diff_dump):
        os.mkdir(diff_dump)
    
    #get the absolute path of the directory
    directory = os.path.abspath(directory) #this is where the config files are for the DML comparisons (main release folder)
    diff_dump = os.path.abspath(diff_dump) #this is where SQL sync scripts are saved (inner release folder)

    #print("The absolute path of the dir with the config files is: %s" % directory)
    #print("The absolute path of the dir to dump the diff scripts is: %s" % diff_dump)

    #check if the directory exists then change directories to it if the dir does exist
    if os.path.exists(directory): #this is where the DCO file is that LowIonConfig created, which should have the correct DML tables to scan
        os.chdir(directory)
    

    if not schema_compare:
        #get all the '.dco' files from the directory
        files = glob.glob("*.dco")
        program = 'dco'
    else:
        files = glob.glob("*.ocp")
        program = 'sco'


    

    for f in tqdm(files):
        print("The file name is: %s" % f)
        
        
        time.sleep(.1) #this is for the tqdm progress bar
        
        file_name = f.split('.')[0]
        
        #make sure to please not re-diff devdba.ap_versions 
        if 'AP_VERSIONS' in file_name and re_diff==True:
            print('[!] Not re-diffing foo_versions data.')
            continue
        
        #check to see if this is the initial diff generation or the re-diff to see if there is an error
        if not re_diff:
            diff_file = file_name + "_diff_script.sql"
        elif re_diff:
            diff_file = file_name + "_RE-DIFF.sql"
            
        path_and_file = diff_dump + os.sep + diff_file
        print("The name of the diff_file is: %s " % (path_and_file))

        #we need to get the filter file name and put this in the ignore_rules variable
        if filters:
            ignore_rules = file_name + "_ignoreRules.scpf"
            print("The name of the filter file is: %s" % ignore_rules)
        
        #pdb.set_trace()

        
        
        #no_output = ' /q /loglevel:verbose '
        if schema_compare:

            if filters:
                #note the /igr option to use a filter file for the sco.exe program - This is in version 5.4.0.2010
                print("[!!!] Calling SCO.exe with filters. This has a bug in the RG software not this script.")
                subprocess.run(['%s ' % program, '/dao', '/project:%s' % f, '/igr:%s' % ignore_rules, '/scriptfile:%s' % path_and_file])
            else:
                print("[+] Calling the SCO.exe program WITHOUT filters.")
                subprocess.run(['%s ' % program, '/dao' ,'/project:%s' % f, '/scriptfile:%s' % path_and_file])
                
        else:
            #subprocess.run(['%s ' % program,'/project:%s' % f, '/scriptfile:%s' % path_and_file],  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(['%s ' % program,'/project:%s' % f, '/scriptfile:%s' % path_and_file]) #print everything to the console
            
        
    print("%d configuration script(s) found. You should have %d diff script(s)." %(len(files), len(files)))
    return len(files) #return the number of configuration files the caller should have




if __name__ == "__main__":

    directory = ''
    diff_dir = ''
    schema_compare = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hg:d:s', ["generate=", "diff=", "schema"])

        for opt, arg in opts:

            if opt in ('-h', '--help'):
                helpMe()
            elif opt in ('-s', '--schema'):
                schema_compare = True
            elif opt in ('-g', '--generate'):
                directory = arg
            elif opt in ('-d', '--diff'):
                diff_dir = arg

    except getopt.GetoptError:
        print("Something went wrong.")
        print("For help executing the program type the following:")
        print("%s -h " % sys.argv[0])

    if len(directory) > 0 and len(diff_dir) > 0:
        generateDiffScripts(directory, diff_dir, schema_compare)
                
    
