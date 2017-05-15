apt-get update

apt-get -y install python-dev
apt-get -y install python-pip
apt-get -y install libssl-dev
apt-get -y install libffi-dev
python -m pip install appdirs
pip install -r requirements.txt
pip install rfc3986
