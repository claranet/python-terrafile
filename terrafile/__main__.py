import os
import sys

from terrafile import update_modules

if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    path = os.getcwd()

update_modules(path)
