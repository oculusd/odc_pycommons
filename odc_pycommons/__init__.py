# Copyright (c) 2018. All rights reserved. OculusD.com, Inc. Please refer to the LICENSE.txt file for full license information. Licensed in terms of the GPLv3 License.

import pathlib
import os
from datetime import datetime


def get_utc_timestamp(with_decimal: bool=False):
    epoch = datetime(1970,1,1,0,0,0)
    now = datetime.utcnow()
    timestamp = (now - epoch).total_seconds()
    if with_decimal:
        return timestamp
    return int(timestamp)


HOME = '{}{}.oculusdcli'.format(
    str(pathlib.Path.home()),
    os.sep
)


# EOF