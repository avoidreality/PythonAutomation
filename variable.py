#global variables can be defined here and used across modules

DIFF_SCRIPTS = None
SDATA_LIST = None
MODE = None
DOCKER_DCO = None
IGR_DIR = None
SCHEMA_LIST = None
DCO_DIR = None
OCP_DIR = None
PDBS = None
GIT_REPO = None
RELEASE_DIR = None
TENANT = None


def init():
    global DIFF_SCRIPTS
    DIFF_SCRIPTS = None

    global SDATA_LIST
    SDATA_LIST = None

    global MODE
    MODE = None

    global DOCKER_DCO
    DOCKER_DCO = None

    global IGR_DIR
    IGR_DIR = None

    global SCHEMA_LIST
    SCHEMA_LIST = None

    global DCO_DIR
    DCO_DIR = None

    global OCP_DIR
    OCP_DIR = None

    global PDBS
    PDBS = None

    global GIT_REPO
    GIT_REPO = None

    global RELEASE_DIR
    RELEASE_DIR = None

    global TENANT
    TENANT = None


def toggle_variables(mode):
    """Give the caller the location of the diff scripts and other assets based on the mode passed in """

    global DIFF_SCRIPTS
    global SDATA_LIST
    global DOCKER_DCO
    global IGR_DIR
    global SCHEMA_LIST
    global MODE
    global GIT_REPO
    global DCO_DIR
    global OCP_DIR
    global PDBS
    global RELEASE_DIR
    
    
    if mode == "foo":
        DIFF_SCRIPTS = "C:\\workspace\\foo\\foo-db\\releases\\diff_scripts"
        SDATA_LIST = "C:\\workspace\\foo\\foo-db_fooPDB2\\install\\gen\\DEVDBA\\SDATA_LIST.csv"
        DOCKER_DCO = "C:\\workspace\\foo\\foo-db\\releases\\diff_script_files\\DockerDataComparison\\diff_this"
        IGR_DIR = "C:\\workspace\\foo\\foo-db\\releases\\diff_script_files\\SchemaComparison\\schema-ignore-objects"
        SCHEMA_LIST = r"C:\workspace\foo\foo-db_fooPDB2\install\gen\DEVDBA\SCHEMA_LIST.csv"
        DCO_DIR=r"C:\workspace\foo\foo-db\releases\diff_script_files\DataComparison\diff_this"
        OCP_DIR=r"C:\workspace\foo\foo-db\releases\diff_script_files\SchemaComparison\schema-files\diff_this"
        PDBS = ['fooPDB1', 'fooPDB2']
        MODE = "foo"
        GIT_REPO = "C:\\workspace\\foo\\foo-db"
        RELEASE_DIR = "C:\\workspace\\foo\\foo-db\\releases"
        TENANT_LIST = r"C:\workspace\foo\foo-db_fooPDB2\install\tenant_config.xml"
        
        
    elif mode == "EGG_MODE":
        DIFF_SCRIPTS = "C:\\workspace\\monorepo\\newhorizon\\EGG-db\\releases\\diff_scripts"
        SDATA_LIST = "C:\\workspace\\monorepo\\newhorizon_EGGPDB2\\EGG-db\\install\\gen\\DEVDBA\\SDATA_LIST.csv"
        DOCKER_DCO = r"C:\workspace\monorepo\newhorizon\EGG-db\releases\diff_script_files\DockerDataComparison\\diff_this"
        IGR_DIR = "C:\\workspace\\monorepo\\newhorizon\\EGG-db\\releases\\diff_script_files\\SchemaComparison\\schema-ignore-objects"
        SCHEMA_LIST = r"C:\\workspace\\monorepo\\newhorizon_EGGPDB2\\EGG-db\\install\\gen\\DEVDBA\\SCHEMA_LIST.csv"
        TENANT_LIST = r"C:\\workspace\\monorepo\\newhorizon_EGGPDB2\\EGG-db\\install\\tenant_config.xml"
        #DCO_DIR=r"C:\workspace\foo\foo-db\releases\diff_script_files\DataComparison\diff_this"
        #OCP_DIR=r"C:\workspace\foo\foo-db\releases\diff_script_files\SchemaComparison\schema-files\diff_this"
        
        PDBS = ['EGGPDB1', 'EGGPDB2']
        MODE = "MONO"
        GIT_REPO = "C:\\workspace\\monorepo\\newhorizon"
        RELEASE_DIR = "C:\\workspace\\monorepo\\newhorizon\\EGG-db\\releases"
        
    else:
        DIFF_SCRIPTS = "C:\\workspace\\newhorizon\\EGG-db\\releases\\diff_scripts"
        SDATA_LIST = r"C:\workspace\newhorizon\EGG-db_EGGPDB2\install\gen\DEVDBA\SDATA_LIST.csv"
        DOCKER_DCO = r"C:\workspace\newhorizon\EGG-db\releases\diff_script_files\DockerDataComparison\diff_this"
        IGR_DIR = r"C:\workspace\newhorizon\EGG-db\releases\diff_script_files\SchemaComparison\schema-ignore-objects"
        SCHEMA_LIST = r"C:\workspace\newhorizon\EGG-db_EGGPDB2\install\gen\DEVDBA\SCHEMA_LIST.csv"
        PDBS = ['EGGPDB1', 'EGGPDB2']
        MODE = "EGG"
        GIT_REPO = "C:\\workspace\\newhorizon\\EGG-db"
        RELEASE_DIR = "C:\\workspace\\newhorizon\\EGG-db\\releases"
        TENANT_LIST = r"C:\workspace\newhorizon\EGG-db_EGGPDB2\install\\tenant_config.xml"
        
    
