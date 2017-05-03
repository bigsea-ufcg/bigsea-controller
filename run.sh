script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH="$PYTHONPATH:$script_dir/bigsea-scaler"

python bigsea-scaler/cli/main.py