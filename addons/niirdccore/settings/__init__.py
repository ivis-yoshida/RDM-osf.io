import logging
from .defaults import *  # noqa


logger = logging.getLogger(__name__)
DMR_URL = 'https://dev1.dmr.nii.ac.jp/'

try:
    from .local import *  # noqa
except ImportError:
    logger.warn('No local.py settings file found')
