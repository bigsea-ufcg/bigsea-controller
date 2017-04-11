*** HOW TO START THE SCALER ***

$ python cli/main.py

The scaler listens on port 5112


*** HOW TO USE THE SCALER API ***

Requests

* Prepare environment
Type: post
Format: <host_ip>:5112/scaler/setup_env

Sets the correct amount of resources to instances. It expects a json 
with format {'vm_id':cap}.

* Start scaling
Type: post
Format: <host_ip>:5112/scaler/start_scaling/<app_id>

Adds the application to the set of applications the scaler scales. It
a json with format {'instances':[vm-id-0,vm-id-1]}

* Stop scaling
Type: post
Format: <host_ip>:5112/scaler/stop_scaling/<app_id>

Removes the application from the set of applications the scaler scales.