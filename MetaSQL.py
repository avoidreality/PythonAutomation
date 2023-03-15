import os
import glob
import time
import re
import getopt
import sys
from subprocess import Popen

def sorted_nicely(l):
    """This function will sort the alphanumeric file names like a human"""
    #I found this function here: https://arcpy.wordpress.com/2012/05/11/sorting-alphanumeric-strings-in-python/

    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key = alphanum_key)

def helpMe():
    """The obligatory help info about the program. """

    print("""
                         
                  
                                                                                   
 _|      _|              _|                      _|_|_|    _|_|      _|            
 _|_|  _|_|    _|_|    _|_|_|_|    _|_|_|      _|        _|    _|    _|            
 _|  _|  _|  _|_|_|_|    _|      _|    _|        _|_|    _|  _|_|    _|            
 _|      _|  _|          _|      _|    _|            _|  _|    _|    _|            
 _|      _|    _|_|_|      _|_|    _|_|_|      _|_|_|      _|_|  _|  _|_|_|_|      
                                                                                   
                                                                                   

    Meta SQL
    by Trash Software
    """)
   
    print("'%s -m <path to diff scripts>' to create a deployment script" % (sys.argv[0]))


def docker_transport(directory_to_scripts, container_d):
    """Send the deployment script and diff scripts to the Docker container."""

    import ConnectToOracle as CTO
    
    #Find all the SQL files
    all_sqls = glob.glob(directory_to_scripts + os.sep + "*.sql")

    just_filenames = set() 
    for file in all_sqls:
        just_filenames.add(file.split(os.sep)[-1]) #split on the path seperator and return the last thing in the path - the filename :)

    print("Found these files and preparing them for transport to the Docker container, the exotic paradise for SQL files.")
    for sql_file in just_filenames:
        print(f"\n[+] {sql_file}")

    for sql_file in just_filenames:
        CTO.docker_copy(container_d=container_d, source=sql_file) #This will copy the sql_file in the loop to the container_d container to the /home/oracle folder

    


def heyHoLetsGo(directoryOfDiffScripts):
    """ This function creates a deployment script """
    you_are_here = os.path.abspath(os.getcwd()) #the path, absolute path, where the script was executed

    print(f"[+] Greetings from heyHoLetsGo! You are currently here: {you_are_here}")
    print(f"The directory passsed into hhlg is: {directoryOfDiffScripts}")

    #now let us try to find all of the SQL files in the "dump directory"
    r = glob.glob(directoryOfDiffScripts + os.sep + '*.sql')

    #just get the filenames from the paths
    filenames = []
    for k in r:
        filenames.append(k.split(os.sep)[-1])

    print("These are the filenames")
    for f in filenames:
        print(f)
        print("\n")
    
    #try to sort the paths with filenames based on the filename only - this is alphabetical order currently - useless sort probably
    sorted_filenames = sorted_nicely(filenames)

    """
    for i in sorted_filenames:
        print(directoryOfDiffScripts + os.sep + i)
        print("\n")
    """

    

    #get a unique timestamp for filename
    s = time.asctime().replace(' ', '').replace(':', '') #replace the spaces and colons with nothing for a better looking filename
    #write the files to a sql file - This writes everything to the desktop.
    file_meta = 'CBT-MetaSQL%s.sql' % str(s)
    with open(file_meta, 'w') as f:
        f.write('--Start %s\n' % str(file_meta))
        f.write('set define off\n') #this is so the SQL script being created does not stop and ask for input during DB deployments with sqlplus
        for i in sorted_filenames:
            
            f.write("prompt @@%s start\n" % i)
            f.write("@@%s\n" % i)
            f.write("prompt @@%s end\n" % i)
            f.write("\n")

        f.write('--End %s\n' % str(file_meta))
        #print("The file has been written to disk at the following location: %s" % (you_are_here + os.sep + file_meta))

    return file_meta #return the filename 
    
def deploy(d_script):
    """ Deploy a SQL file to the database """
    #session = Popen('sqlplus', '-S', '/ AS SYSDBA'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    #session.stdin.write('spool %s.log' % d_script)
    #session.stdin.write('@%s' % d_script)
    #session.stdin.write('spool off')
    #r = session.communicate()
    r = "Deploying to the database is not currently needed."
    return r
    
    

if __name__ == "__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'cdhm:', ["create", "deploy", "help"])

        for opt, arg in opts:
            if opt in ('-c', '--create'):
                
                heyHoLetsGo()
            elif opt in ('-d', '--deploy'):
                #deploy the script
                name = input('Please type the name of the deployment script: ')
                deploy(name)
            elif opt in ('-h', '--help'):
                helpMe()
            elif opt in ('-m'):
                heyHoLetsGo(arg)

    except getopt.GetoptError:
        print("For help running the program type the following:")
        print("%s -h " % (sys.argv[0]))
