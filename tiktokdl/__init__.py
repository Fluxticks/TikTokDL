from tiktokdl import *

import sys
if sys.version_info[0] == 3 and sys.version_info[1] < 9:
    import logging
    logging.warning(
        "Python 3.8.x is only supported using insecure SSL. Please update python to 3.9.x!"
    )
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
