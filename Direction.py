import xml.etree.ElementTree as ET
import getopt
import sys
import os
import glob

def helpMe():
    print("Examples:")
    print(" ")
    print("%s -d <configuration_file.dco>" % sys.argv[0])
    print("%s --direction <configuration.ocp>" % sys.argv[0])
    print("%s --group <directory of DCO files>" % sys.argv[0])
    print("%s -g <directory of DCO files>" % sys.argv[0])
    print("Please try running the program again.")


def goUP(path):
    """This script should create an upgrade configuration based on the default RedGate configuration where
       the earlier PDB is in PDB1 and the later release is in PDB2. 
    """
    try:
        
        tree = ET.parse(path)
        root = tree.getroot()

        ret = root.findall('.//direction')
        direction = ret[0]

        if direction.text != "From1To2":
            direction.text = "From1To2"
            #print("[+] Setting this file [%s] to an upgrade configuration." % str(path))

            #print("[+] Writing these changes to disk")
            tree.write(path)
            #print("[+] Changes written to disk")

    except IOError as ioe:
        print("IO/Error - The file you specified does not seem to exist.")
    except Exception as e:
        print("There was some exception. This is the exception: %s" % str(e))
        helpMe()

def goDown(path):
    """This script should create a downgrade configuration DCO file based on default RedGate configuration
       with the earlier PDB in PDB1 and the later PDB in PDB2.
    """
    try:
        tree = ET.parse(path)
        root = tree.getroot()

        ret = root.findall('.//direction')
        direction = ret[0]

        if direction.text != "From2To1":
            direction.text = "From2To1"
            #print("[+] Setting this file [%s] to a downgrade configuration." % str(path))

            #print("[+] Writing these changes to disk")
            tree.write(path)
            #print("[+] Changes written to disk")

        
    except IOError as ioe:
        print("IO/Error - The file you specified does not seem to exist.")
    except Exception as e:
        print("There was some exception. This is the exception: %s" % str(e))
        helpMe()
    

def detectDirection(path):
    """This script will tell you if the configuration file is an upgrade or a downgrade """
    try:
        tree = ET.parse(path)
        root = tree.getroot()

        ret = root.findall('.//direction')
        direction = ret[0]

        if direction.text == "From2To1":
            print("")
            print("This is a downgrade configuration.")
            print("The direction is %s " % direction.text)
        elif(direction.text == "From1To2"):
            print("")
            print("This is an upgrade configuration.")
            print("The direction is %s " % direction.text)
        else:
            print("")
            print("The direction could not be determined.")
            print("The direction is apparently: '%s'. This does not make sense though." % direction.text)
            print("Please check your configuration file. Something is very wrong, but do not worry - be happy. :)")
    

    except IOError as ioe:
        print("The file you specified does not seem to exist.")
    except Exception as e:
        print("Something is wrong with how you are running the program.")
        helpMe()


if __name__ == "__main__":
    
   try:
       opts, args = getopt.gnu_getopt(sys.argv[1:], 'd:hg:', ["direction=", "group=", "help"])

       for opt, arg in opts:
           if opt in ('-d', '--direction'):
               detectDirection(arg)
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
                       detectDirection(f)
                       print("----")
                   
           elif opt in ('-h', '--help'):
               helpMe()
   except getopt.GetoptError:
        print("Something went wrong trying to execute the program.")
        helpMe()
