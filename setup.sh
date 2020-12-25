#/bin/bash

python3 -m venv penv
. penv/bin/activate
pip install -r req.txt
deactivate
