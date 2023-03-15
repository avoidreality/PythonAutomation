import winreg
import os

def find_oracle_home():
    """Find the Oracle Home on the current Windows system. """
    reg_handle = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) #None for the computer name is a local connection

    access_key = winreg.OpenKey(reg_handle, r'SOFTWARE\ORACLE')

    for i in range(20):
        try:
            key = winreg.EnumKey(access_key, i)
            if "OraClient19Home" in key:
                print(f"[+] Found the Oracle home! -> {key}")
                global ORA_HOME
                ORA_HOME = key
        except Exception as e:
            break

    if ORA_HOME:
        ora_home_key = winreg.OpenKey(reg_handle, r'SOFTWARE\ORACLE' + os.sep \
                                      + ORA_HOME.strip())
        if ora_home_key:
            print("[+] Success ora_home_key set")
        else:
            print("[-] Uh oh. ora_home_key not set.")
            
    ##    for i in range(30):
    ##        try:
    ##            key = winreg.EnumKey(ora_home_key, i)
    ##            print(f"[+] Found this key -> {key}")
    ##        except Exception as e:
    ##            break
        v = winreg.QueryValueEx(ora_home_key, 'ORACLE_HOME_NAME')
        if v:
            print(f"[+] Found the value for ORACLE_HOME_NAME = {v}")
            if isinstance(v, tuple):
                if len(v) == 2:
                    oracle_home = v[0]
                    oracle_home = oracle_home.split("_")[0]
                    print(f"[+] The Oracle home is: {oracle_home}")
                    return oracle_home
        else:
            print("[-] Did not find the oracle home value.")
    else:
        print(f"[-] ORA_HOME not found. ORA_HOME = {ORA_HOME}")

if __name__ == "__main__":
    find_oracle_home()
        
        
