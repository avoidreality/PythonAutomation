import xml.etree.ElementTree as ET
import getopt
import sys
import glob
import os

def helpMe():
    """This function explains how to use the program """
    print("\n ")
    print("""
 _____ _                   ____  _             _   _         
|     | |_ ___ ___ ___ ___|    \|_|___ ___ ___| |_|_|___ ___ 
|   --|   | .'|   | . | -_|  |  | |  _| -_|  _|  _| | . |   |
|_____|_|_|__,|_|_|_  |___|____/|_|_| |___|___|_| |_|___|_|_|
                  |___|                                      

    """)
    print("To use this program do the following...")
    print(('%s --config "C:\\User\Desktop\Config.dco"' % sys.argv[0]))
    print('%s -c "C:\\User\Desktop\Config.ocp"' % sys.argv[0])
    print("%s --group <directory of DCO files>" % sys.argv[0])
    print("%s -g <directory of DCO files>" % sys.argv[0])
    print("Please try running the program again.")

def ChangeDirection(path="WORKFLOW_OWNER_WedDec12158362018.dco"):
    """This script will change the direction of the comparison in the configuration file. """
    print('This is the path = %s' % path)

    
    
    tree = ET.parse(path)
    root = tree.getroot()

    ret = root.findall('.//direction')

    direction = ret[0]
    print("The direction is %s " % direction.text)
    

    
    if direction.text == "From1To2":
        direction.text = "From2To1"
    else:
        direction.text = "From1To2"

    ret2 = root.findall('.//direction')
    direction2 = ret[0]

    print("The direction is now: %s " % direction2.text)
    print("Writing configuration file to disk")
    tree.write(path)
    


if __name__ == "__main__":

    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "c:hg:", ["group=", "help","config="])

        for opt, arg in opts:
            if opt in ('-c', '--config'):
                the_path = arg
                ChangeDirection(the_path)
            if opt in ('-g', '--group'):
               directory = arg
               os.chdir(directory) #change directory to where the DCO files are
               print("The current directory is: %s" % os.getcwd())
               files = [glob.glob(e) for e in ["*.dco", "*.ocp"]] #put all the files that end with '.dco' into this list 'files'
               print("This is in the 'files' list: %s" % files)
               for f in files: #loop through the files and detect direction
                   for f in f:
                       print("\n")
                       print("----")
                       print("Currently processing this file: %s" % str(f))
                       ChangeDirection(f)
                       print("----")
                
            elif opt in ('-h', '--help'):
                helpMe()
                
    except getopt.GetoptError:
        print("Something went wrong trying to execute this program.")
        helpMe()
    
