# BIGSEA Asperathos - Controller

## Overview
The Controller is responsible for adjusting the amount of resources allocated to the virtual infrastructure where the applications run, in order to guarantee application’s QoS.

To more info, see [details.md](https://github.com/bigsea-ufcg/bigsea-controller/tree/refactor/docs/details.md)

## How does it works?
The controller is implemented following a **plugin architecture**, providing flexibility to add or remove plugins when necessary. It works with usage of three types of plugins: **Actuator**, **Controller** and **Metric Source**.
* The **Controller**, based on metrics such as application progress and CPU usage, decides the amount of resources to allocate to the applications.
* The **Actuator** is responsible for connecting to the underlying infrastructure (such as a Mesos or an OpenStack Sahara platform) and triggering the commands or API calls that allocate or deallocate resources, based on the Controller’s requests.
* The **Metric Source** plugin is responsible for getting application metrics from a metric source, such as Monasca, and returning them to the Controller.

## How to develop a plugin?
See [plugin-development.md](https://github.com/bigsea-ufcg/bigsea-controller/tree/refactor/docs/plugin-development.md).

## Requirements
* Python 2.7 or Python 3.5
* Linux packages: python-dev and python-pip
* Python packages: setuptools, tox and flake8

To **apt** distros, you can use [pre-install.sh](https://github.com/bigsea-ufcg/bigsea-controller/tree/refactor/tools/pre-install.sh) to install the requirements.

## Install
First of all, install **git**. After, you just need to clone the [Controller repository](https://github.com/bigsea-ufcg/bigsea-controller.git) in your machine.

### Configuration
A configuration file is required to run the Controller. **Edit and fill your controller.cfg in the root of Controller directory.** Make sure you have fill up all fields before run.
You can find a template in [config-example.md](https://github.com/bigsea-ufcg/bigsea-controller/tree/refactor/docs/config-example.md). 

### Run
In the Controller root directory, start the service using tox command:
```
$ tox -e venv -- controller
```

## Controller REST API
Endpoints is avaliable on [restapi-endpoints.md](https://github.com/bigsea-ufcg/bigsea-controller/tree/refactor/docs/restapi-endpoints.md) documentation.

## Avaliable plugins
### Controller
* [Progress error](https://github.com/bigsea-ufcg/bigsea-controller/tree/refactor/docs/plugins/progress-error.md)
* [Proportional](https://github.com/bigsea-ufcg/bigsea-controller/tree/refactor/docs/plugins/proportional-controller.md)
* [Proportional derivative](https://github.com/bigsea-ufcg/bigsea-controller/tree/refactor/docs/plugins/proportional-derivative-controller.md)
* [Proportional integrative derivative](https://github.com/bigsea-ufcg/bigsea-controller/tree/refactor/docs/plugins/pid-controller.md)

### Actuator
* [KVM](https://github.com/bigsea-ufcg/bigsea-controller/tree/refactor/docs/plugins/kvm-actuator.md)
* [KVM I/O](https://github.com/bigsea-ufcg/bigsea-controller/tree/refactor/docs/plugins/kvm-io-actuator.md)

### Metric source
* [Monasca](https://github.com/bigsea-ufcg/bigsea-controller/tree/refactor/docs/plugins/monasca-metric-source.md)
