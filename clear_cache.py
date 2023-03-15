#! /usr/bin/python

import shutil
import os 
import getopt
import sys 

#This program uses the shutil module's 'rmtree(path)' to remove the folder and sub-folders of the 'cache' and 'tmp' directories

"""

This program should be copied onto the Linux test server that has a WebLogic server on it and executed if you want to "clear the cache". 

"""


SERVER_PATH= "/app/oracle/Oracle/Middleware/Oracle_Home/user_projects/domains/base_domain/servers" 

def domain_info():
    print("*" * 40)
    print("These are all the servers in the domain sirs:")
    print(os.listdir(SERVER_PATH))
    print("*" * 40)

def get_path():
    """Get the path to the servers """ 
    return SERVER_PATH

def set_path(your_path):
    """Set the path of the environment variable, SERVER_PATH. """
    global SERVER_PATH
    SERVER_PATH = your_path



def nuke_cache(app):
    print("[+] This is the app to delete the cache for: %s " % app)
    os.chdir(SERVER_PATH)
    try:
        os.chdir(app)
    except Exception, e:
        print("Exception thrown trying to change dirs to the app: %s" % str(e))

    print("The current directory is: %s " % os.getcwd())
    print("These are the files in the directory: ")
    print(os.listdir(os.getcwd()))

    files = os.listdir(os.getcwd())
    for f in files: 
       if f == "tmp":
          print("Found the 'tmp' directory.")
          print("This is the stat information:")
          print(os.stat(f))
          shutil.rmtree(f)
          print("[+] 'tmp' directory removed.")
       elif f == 'cache':
          print("Found the 'cache' directory.")
          print("This is the stat information:")
          print(os.stat(f))
          shutil.rmtree(f)
          print("[+] 'cache' directory removed.")


def help():
    print("*" * 40 )
    print("How to use this program.")
    print("%s -s <App Server Name>" % sys.argv[0])
    print("This will delete the 'tmp' and 'cache' folders under the target managed server.")
    print("*" * 40) 


def main(argv):
    
     #print("Got the following in main  %s " % argv)
     #print("")
     try:
        opts, args = getopt.getopt(argv[1:], "hs:", ["--server="])
    
     except getopt.GetoptError: 
        help()
        sys.exit(2)

     #print("opts = %s" % opts)
     #print("args = %s" % args)

     for opt, arg in opts: 
        if opt == "-s":
           nuke_cache(arg)

        if opt == "-h":
           help()
          


if __name__ == "__main__":
    #print("Got the following args: %s" % str(sys.argv[:]))    
    main(sys.argv[:])
print("[+] Program complete.") 
