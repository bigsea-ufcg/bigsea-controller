# Description
The Controller service is responsible for managing the applications performance, adjusting the amount of resources allocated to the virtual infrastructure where the applications run, in order to ensure application’s QoS goals.
This service includes the actuator and the controller components.
The Controller, based on metrics such as application progress and CPU usage, decides the amount of resources to allocate to the applications.
The Actuator is responsible for connecting to the underlying infrastructure (such as a Mesos or an OpenStack Sahara platform) and triggering the commands or API calls that allocate or deallocate resources, based on the Controller’s requests.

# Architecture
The complete controller service makes use of three plugins: the Controller plugin, the Actuator plugin and the Metric Source plugin.
The Controller and the Actuator plugins implement the Controller and Actuator components, respectively.
The Metric Source plugin is responsible for getting application metrics from a metric source, such as Monasca, and returning them to the Controller. 
EUBra-BIGSEA includes actuators actuating at three levels (with different application setups): Chronos Frameworks, for repeatable tasks; Marathon frameworks, for long-living tasks; and KVM-based, for those applications not supporting the actuation at the level of the framework.
