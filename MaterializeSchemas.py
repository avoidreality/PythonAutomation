import xml.etree.ElementTree as ET
import LostSchemas
import pathlib
import os

#step 1 read in the schemas
#step 2 get the template
#step 3 create a OCP file for each schema found from the template

SCHEMAS = [] #global variable to hold all the schemas
schema_list = ".." + os.sep + '..' + os.sep + '..' + os.sep + 'foo-db_foo2' + os.sep + 'install' + os.sep+ 'gen' + os.sep + 'USERNAME' + os.sep + 'SCHEMA_LIST.csv'

def getSchemas(pathToCSV=schema_list):
    """This is a wrapper function to get the schemas via the LostSchemas module"""
    lost = LostSchemas.LostSchemas()
    schemas = lost.readSchemaCSV(pathToCSV=pathToCSV)
    global SCHEMAS
    SCHEMAS = schemas
    return schemas


def createSchemas():
    """ This function creates schema configuration files based on all the schemas found.  """

    p = pathlib.Path()
    

    for s in SCHEMAS:
        print(os.getcwd())
        tree = ET.parse('..' + os.sep + 'diff_script_files' + os.sep + 'SchemaTemplate' + os.sep + 'EMPTY_TEMPLATE.ocp') #load the template
        root = tree.getroot()

        ret = root.findall('.//schemaMapping')
        
        for i in ret:
            source_schema = i.find('./source/string').text.strip()
            print("source_schema = %s " % source_schema)
            destination_schema = i.find('./destination/string').text.strip()
            print("destination_schema = %s" % destination_schema)

            #import awesome
            #awesome.slowdown()
            
            #look for the default schema in the template file 
            if source_schema.strip() and destination_schema.strip() == "YOUR SCHEMA NAME HERE":
                print("[+] Template found. Re-writing template now.")
                i.find('./source/string').text = s
                i.find('./destination/string').text = s

        #check if the path exists if the path does not exist create the path
            
        if not pathlib.Path('..' + os.sep + 'diff_script_files' + os.sep + 'ProgrammaticOCP').exists():
            os.mkdir('..' + os.sep + 'diff_script_files' + os.sep + 'ProgrammaticOCP')

        

        #write the new configuration file 
        tree.write('..' + os.sep + 'diff_script_files' + os.sep + 'ProgrammaticOCP' + os.sep + s + '.ocp')

       


if __name__ == "__main__":
    print("Program starting...")
    getSchemas()
    createSchemas()
    

        
    #createSchemas()
    print("Program complete.")
    
            
    
    
