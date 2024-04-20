import logging
import os

LOG_FORMAT='%(asctime)s :: %(levelname)s :: %(message)s'

def consoleLogger(module):
    
    dir_name = f"etl/logs/"
    os.makedirs(dir_name, exist_ok=True)
    
    with open(dir_name + f"{module}.log", "w") as f:
        f.write("")
    
    logging.basicConfig(
        filename=dir_name + f"{module}.log",
        level=logging.DEBUG,
        format=LOG_FORMAT,
        datefmt='%Y-%m-%d %H:%M:%S' 
    )
    
    consoleLog = logging.getLogger("consoleLogger")
    consoleLog.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT)
    ch.setFormatter(formatter)
    
    consoleLog.addHandler(ch)
    
    return consoleLog
        
def loggingInfo(msg, module):
    if logging.getLogger("consoleLogger").hasHandlers():
        logger = logging.getLogger("consoleLogger")
    else:
        logger = consoleLogger(module=module)
    
    logger.info(msg=msg)


def loggingError(msg, module):
    if logging.getLogger("consoleLogger").hasHandlers():
        logger = logging.getLogger("consoleLogger")
    else:
        logger = consoleLogger(module=module)
    
    logger.error(msg=msg)
    
def loggingWarn(msg,module):
    if logging.getLogger("consoleLogger").hasHandlers():
        logger = logging.getLogger("consoleLogger")
    else:
        logger = consoleLogger(module=module)
    
    logger.warning(msg=msg)    