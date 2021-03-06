# nafsdm
# (c) Vilhelm Prytz 2018
# __main__
# get's stuff goooing
# https://github.com/mrkakisen/nafsdm

import logging
import sys
import shutil
import os
import psutil
from daemon import *
from exitDaemon import *
from version import version
from getConfig import getConfig
from versionCheck import checkUpdate
from logPath import logPath

# write our PID
def writePID():
    # get our PID using the psutil libs
    ourPID = os.getpid()

    try:
        f = open("/home/slave-nafsdm/slave.pid", "w")
        f.write(str(ourPID))
        f.close()
    except Exception, e:
        logging.exception("Could not write PID file.")
        logging.critical("Exit due to previous error.")
        gracefulExit(1)

    # log our PID
    logging.info("nafsdm running on PID " + str(ourPID))

def main():
    # logger setup
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # format for logger
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    # add stdout to logger
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # add file handler to logger
    fh = logging.FileHandler(logPath)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # welcome message
    logging.info("*******************************************************")
    logging.info("nafsdm-slave daemon - running version " + version)
    logging.info("*******************************************************")

    logging.info("Running pre-start checks..")

    # before everything, check if no other slave is already running
    if os.path.isfile("/home/slave-nafsdm/slave.pid"):
        try:
            f = open("/home/slave-nafsdm/slave.pid")
        except Exception, e:
            logging.exception("Could not read PID file (" + str(e) + ")")
            logging.critical("Exit due to previous error.")
            exit(1)

        pid = int(f.read())
        f.close()

        logging.info("Found PID " + str(pid) + " in file")

        # verify that there is an active process on that PID
        fail = True
        try:
            p = psutil.Process(pid)
        except Exception, e:
            # throws exception if pid does not
            logging.warning(str(e))
            logging.warning("Invalid PID found - nafsdm will boot anyways")

            # remove the file
            os.remove("/home/slave-nafsdm/slave.pid")

            # writePID function
            writePID()

            fail = False

        # we don't wan't to do this if it turns out the PID is not an active process
        if fail:
            # print error then exit
            logging.critical("Another process of nafsdm is already running on PID " + str(pid))
            logging.critical("nafsdm-slave will not be able to start.")
            exit(1)
    else:
        logging.info("No other instances of nafsdm found.")
        writePID()

    # check if the upgrade script is present (we shouldn't be running if so)
    if os.path.isfile("/home/slave-nafsdm/tempUpgrade/temp_upgrade.sh"):
        logging.warning("Upgrade script was found during pre-start checks. Please delete the upgrade script before runing nafsdm-slave!")
        logging.warning("Note: the script is left there because the config has changed and needs updating.")
        gracefulExit(1)

    # this is the legacy config from 1.0-stable
    if os.path.isfile("/home/slave-nafsdm/config-legacy.conf"):
        logging.warning("Legacy config was found. This probably means that nafsdm has been upgraded but the config hasn't been updated yet.")
        logging.warning("Remove the legacy config when finished.")
        gracefulExit(1)

    # check if the temp folder exists
    if os.path.isdir("/home/slave-nafsdm/temp"):
        logging.debug("Temp folder already exists.")
    else:
        if os.path.isfile("/home/slave-nafsdm/temp"):
            os.remove("/home/slave-nafsdm/temp")
            os.makedirs("/home/slave-nafsdm/temp")
        else:
            os.makedirs("/home/slave-nafsdm/temp")

    # get config
    config = getConfig()

    # check for updates
    checkUpdate(config, None)

    # prestart checks pass
    logging.info("Pre-start checks completed")

    # deprecation
    logging.warning("DEPRECATION 1.3.2-stable is the final release of nafsdm. Use it at your own risk.")

    # run the daemon itself
    runDaemon(config)

if __name__ == "__main__":
    main()
    # graceful exit
    gracefulExit(0)
