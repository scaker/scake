# -*- coding: utf-8 -*-

__version__ = "0.1.0"

import sys
major, minor, micro, _, _ = sys.version_info
if major == 2:
    from scake import Scake
    from auto import AutoScake
    from structure import ScakeDict
else:
    from .scake import Scake
    from .auto import AutoScake
    from .structure import ScakeDict
