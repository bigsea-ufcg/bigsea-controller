1. Write a new python class

It must implement the methods __init__, start_application_scaling and stop_application_scaling.

__init__(self, application_id, parameters)
Creates a new controller which scales the given application using the given parameters.
app_id: application id to scale.
parameters: a dictionary containing scaling parameters.

	Example:

{
"instances": [instance_id_0, instance_id_1, …, instance_id_n],
"check_interval": 5,
"trigger_down": 10,
"trigger_up": 10,
"min_cap": 10,
"max_cap": 100,
"actuation_size": 25,
"metric_rounding": 2,
"actuator": “basic”,
"metric_source": “monasca”,
“application_type”: “os_generic”
}

start_application_scaling(self)
Starts scaling for an application.
This method is used as a run method by a thread.

stop_application_scaling(self)
Stops scaling of an application.

Example:

class MyController:

    def __init__(self, application_id, parameters):
        # set things up
        pass

    def start_application_scaling(self):
        # scaling logic
        pass
            
    def stop_application_scaling(self):
        # stop logic
        pass


2. Add the class to scaler project into the plugins directory.

3. Edit Controller_Builder
Add a new condition to get_controller. Instantiate the plugin using the new condition.

Example:

...
elif name == "mycontroller":
            # prepare parameters
            return MyController(application_id, parameters)
...

The string used in the condition must be passed in the request to start scaling as the value to “plugin” parameter.

The example of scaler plugin contained in the repository is composed of two classes: the Generic_Controller and the Generic_Alarm. The Generic_Alarm contains the logic used to adjust the amount of resources allocated to applications. The Generic_Controller dictates the pace of the scaling process. It controls when Generic_Alarm is called to check the application state and when is necessary to wait.

The Actuator plugin

Our actuation plugin (“basic”) can act on KVM virtual machines, getting and changing the amount of allocated resources through virsh. It uses SSH to access the compute nodes.


The “basic” plugin implements the following methods.

prepare_environment(self, vm_data)
Sets up environment properties, like allocated resources, using vm_data as parameter. Usually is used before starting the application.

In the “basic” plugin implementation, vm_data is a map “virtual machine to CPU cap“. The plugin uses this map to set the cap of each vm.


adjust_resources(self, vm_data)
Modifies the environment properties using vm_data as parameter. Usually is used when the application is already running.

In the “basic” plugin implementation, vm_data is a map “virtual machine to CPU cap“. The plugin uses this map to set the cap of each vm.

get_allocated_resources(self, vm_id)
It returns the cap of the given virtual machine.

An example of actuator plugin is available in the scaler repository.
