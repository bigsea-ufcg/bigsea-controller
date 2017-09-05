# BigSea WP3 - Controller

The Controller service is responsible for managing the applications performance, adjusting the amount of resources allocated to the virtual infrastructure where the applications run, in order to ensure application’s QoS goals.

This service includes the actuator and the controller components. The Controller, based on metrics such as application progress and CPU usage, decides the amount of resources to allocate to the applications. The Actuator is responsible for connecting to the underlying infrastructure (such as a Mesos or an OpenStack Sahara platform) and triggering the commands or API calls that allocate or deallocate resources, based on the Controller’s requests.

# Deploy

To install, configure and run the Controller component you will need a virtual machine with the configurations described below.

**Minimal configuration**
```
OS: Ubuntu 14.04
CPU: 1 core
Memory: 2GB of RAM
Disk: 20GB
```

In the virtual machine that you want to install the Controller follow the steps below:

## Install
1. Install git
    ```bash
    $ sudo apt-get install git
    ```
2. Clone the BigSea Controller repository
    ```bash
    $ git clone https://github.com/bigsea-ufcg/bigsea-controller.git
    ```
3. Access the bigsea-controller folder and run the setup script
    ```bash
    $ ./setup.sh # You must run this command as superuser to install some requirements
    ```

## Configure

A configuration file is required to run the Controller. You can find a template in the main directory called controller.cfg.template, rename the template to controller.cfg. Make sure to fill up all fields before run.

```
[flask]
host = <host_ip>
port = <port_number>

[actuator]
compute_nodes = 
keypair_compute_nodes =
tunnel_ports = 
actuator_port = 
iops_reference = 
bs_reference =  

[monasca]
monasca_endpoint = http://<ip:port>
username = <monasca_user>
password = <password>
project_name = <monasca_project_name>
auth_url = http://<ip>:<port>/v3/
api_version = 2_0
```

## Run
Start the service running the run.sh script.
```
$ ./run.sh
```

## API usage

## General information
This section defines the API usage. 

## Endpoints

### Prepare Environment

`POST scaler/setup_env`

Sets the amount of resources allocated to instances. 

This call expects a JSON on the body with the client’s specification of the instances to adjust.

#### Request parameters

```javascript
{
	"plugin":<actuation plugin>,
	"vm_id0":cap0,
	"vm_id1":cap1,
	...
	"vm_idn":capn
}
```

#### Request example

```javascript
{
	"plugin":"kvm",
	"ffc16820-d3c8-47c3-b9b0-9d5aeacbcd49":50,
	"01c23a15-f21b-4cf0-9065-e36b590bf16c":70
}
```

### Start Scaling

`POST scaler/start_scaling/<app_id>`

Adds the application to the set of applications the Controller scales. 

This call expects a JSON on the body with the controller plugin parameters.

#### Request parameters

| Name | Type | Description |
| --- | --- | --- |
| plugin | string | The Controller plugin to use |
| scaling_parameters | dictionary | A dictionary containing all the parameters for the scaling plugin |


#### Request example

```javascript
{
	"plugin":"proportional",
	"scaling_parameters":
				{"actuator":"kvm", 
				"metric_source":"monasca",
				"instances":["ffc16820-d3c8-47c3-b9b0-9d5aeacbcd49", "01c23a15-f21b-4cf0-9065-e36b590bf16c"],
				"check_interval":10,
				"trigger_down":10,
				"trigger_up":10,
				"min_cap":10,
				"max_cap":100,
				"metric_rounding":2
				"heuristic_options":options}
}
```

### Stop scaling

`POST scaler/stop_scaling/<app_id>`

Removes the application from the set of applications the Controller scales.


## Plugins

### Controller plugins available

[Progress error controller](doc/progress-error.md)

[Proportional controller](doc/proportional-controller.md)

[Proportional derivative controller](doc/proportional-derivative-controller.md)

### Actuation plugins available

[KVM actuator](doc/kvm-actuator.md)

[KVM I/O actuator](doc/kvm-io-actuator.md)

### Metric source plugins available

[Monasca metric source](doc/monasca-metric-source.md)
