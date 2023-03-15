import matplotlib.pyplot as plt;
import matplotlib.patches as mpatches
import re
import numpy as np
import os

def error_report(path_to_deployment_log):
    """This function takes the path to a log file and generates an error report with a pie chart. """

    f = open(path_to_deployment_log)
    L = f.readlines()
    f.close()

    #initialize error counting variables
    total_errors = 0.0
    ora = 0.0
    sql = 0.0
    sp2 = 0.0
    pl2 = 0.0
    tns = 0.0

    
    for line in L:
        searchObject = re.search(r'(ORA-|SQL-|SP2-|PL2-|TNS-)', line)
        if searchObject:
          total_errors = total_errors + 1.0
          type_of_error = searchObject.group()
          print("The type of error is: %s " % type_of_error)
          if (type_of_error.startswith("ORA-")):
              ora = ora + 1.0
          elif (type_of_error.startswith("SQL-")):
              sql = sql + 1.0
          elif (type_of_error.startswith("SP2-")):
              sp2 = sp2 + 1.0
          elif (type_of_error.startswith("PL2-")):
              pl2 = pl2 + 1.0
          elif (type_of_error.startswith("TNS-")):
              tns = tns + 1.0
          
        else:
          pass

    

   
    #print("The total number of errors is %s" % total_errors)
    #print("Number of ORA errors: %d" % ora)
    #print("Number of SQL errors: %d" % sql)
    #print("Number of SP2 errors: %d" % sp2)
    #print("Number of PL2 errors: %d" % pl2)
    #print("Number of TNS errors: %d" % tns)

    #create bar chart
    error_tracking = ('ORA', 'SQL', 'SP2', 'PL2', 'TNS')
    y_pos = np.arange(len(error_tracking))
  
    different_errors = [ora, sql , sp2, pl2, tns]

    plt.bar(y_pos, different_errors, align='center', alpha=0.5)
    plt.xticks(y_pos, error_tracking)
    plt.ylabel('Number of errors in deployment')
    plt.title('Different errors that could be thrown during a database deployment')
    meta_data = mpatches.Patch(label="Total errors: %d. ORAs: %d, SQL: %d, SP2: %d, PL2: %d, TNS: %d" % (total_errors, ora, sql, sp2, pl2, tns))
    plt.legend(handles=[meta_data])

    #test if the file exists
    filename = 'error_report.png'
    count = 1
    if os.path.exists(filename):
        
        while os.path.exists(filename):
            filename = 'error_report%d.png' % count
            count += 1
    else:
        pass
    
    plt.savefig(filename)
    plt.close() #adding this in hopes it will fix running this module back to back in "big_bang" mode. :)
    
    #print("[+] A bar chart was saved, named %s, to disk describing the number of errors found." % filename)
    different_errors.append(total_errors) #add the total_errors count to the list after the report is calculated for the caller
    return different_errors
    
if __name__ == "__main__":
    error_report("upgrade_pdb1_to_pdb2_deployment.log")
    

