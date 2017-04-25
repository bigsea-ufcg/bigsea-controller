apt-get update

apt-get install python-dev
apt-get install python-pip
pip install -r requirements.txt
pip install rfc3986

export PYTHONPATH="$PYTHONPATH:~/bigsea-scaler/bigsea-scaler"
