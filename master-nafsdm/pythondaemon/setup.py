# nafsdm
# setup
# masterd setup functions

# imports
import subprocess
from daemonlog import log
import os, random, string

# unused function, but will leave in here if it will be needed
def generatePassword(length=30):
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (os.urandom(1024))

    return(''.join(random.choice(chars) for i in range(length)))

def setupSSH():
    #generatedPassword = generatePassword()
    try:
        output = subprocess.check_output(["mkdir", "/home/master-nafsdm/.ssh"])
        output = subprocess.check_output(["ssh-keygen ", "-t", "rsa", "-b", "4096", "-C", "'DNS manager'", "-N", "''", "-f", "'/home/master-nafsdm/.ssh/nafsdm_rsa'", "-q"])
        output = subprocess.check_output(["cp", "/home/master-nafsdm/.ssh/dns_manager_rsa.pub", "/home/master-nafsdm/.ssh/authorized_keys"])
    except Exception, e:
        log("FATAL: Some error ocurred during SSH key generation.")

    log("To continue, please copy /home/master-nafsdm/nafsdm_rsa to all slaves /home/slave-nafsdm/.ssh/master_key")
    exit(1)