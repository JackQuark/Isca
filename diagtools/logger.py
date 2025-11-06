# Log helper for Isca
# author: Quark
# ==================================================
import logging
# ==================================================

log = logging.getLogger('isca')
log.setLevel(logging.DEBUG)
if not log.handlers:
    stdout = logging.StreamHandler()
    stdout.setLevel(logging.DEBUG)
    stdout.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    log.addHandler(stdout)
    
class Logger(object):
    log = log