#  REST API Endpoints
This section provides a detailed list of avaliable endpoints in Controller REST API.

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
