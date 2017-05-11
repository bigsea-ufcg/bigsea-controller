# BigSea Scaler

### HOW TO START THE SCALER ###

* Configure the controller.cfg providing the following info:
```
[flask]
# The ip used by the flask server
host = <host ip>
# The port used by the flask server
port = <host port>
```
* Some scaler plugins may require additional parameters. Please, check the plugins documentation.
* Run the main python file to start the service.

```
$ python bigsea-scaler/cli/main.py
```

### HOW TO USE THE SCALER API ###


#### Prepare Environment

Type: post
Format: /scaler/setup_env

Sets the amount of resources to instances. 

Request body:
```javascript
{
	"plugin":<actuation plugin>,
	"vm_id0":cap0,
	"vm_id1":cap1
}
```

#### Start Scaling

Type: post
Format: /scaler/start_scaling/<app_id>

Adds the application to the set of applications the scaler scales. 

Request body:
```javascript
{
	"plugin":<scaling plugin>,
	"actuator":<actuation plugin>,
	"metric_source":<metrics plugin>,
	"instances":["vm_id0", "vm_id1"],
	"scaling-parameter-key0":"scaling-parameter-value0",
	...
	"scaling-parameter-keyN":"scaling-parameter-valueN"
}
```

Scaling plugins available:
[Single application controller](doc/single-application-controller.md)
[Progress error controller](doc/progress-error.md)

Actuation plugins available:
[KVM actuator](doc/kvm-actuator.md)

#### Stop scaling

Type: post
Format: /scaler/stop_scaling/<app_id>

Removes the application from the set of applications the scaler scales.
