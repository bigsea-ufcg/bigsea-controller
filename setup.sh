apt-get update

apt-get -y install python-dev
apt-get -y install python-pip
pip install -r requirements.txt
pip install rfc3986

export PYTHONPATH="$PYTHONPATH:/home/ubuntu/bigsea-scaler/bigsea-scaler"
