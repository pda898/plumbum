#/bin/sh

cd "${0%/*}"
. penv/bin/activate
python3 main.py "$@"
deactivate
