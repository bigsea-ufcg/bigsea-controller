# Actuator plugin - "kvm"
This plugin uses ssh to access instances in remote hosts and modify the amount of allocated resources.

## Configuration
The "kvm" plugin requires the following parameters in "controller.cfg"

* **compute_nodes**: The ips of the compute nodes, separated by comma.
* **keypair_compute_nodes**: The path of the key used to access the compute nodes.

### Example 

```
[actuator]
compute_nodes = 0.0.0.1, 0.0.0.2, 0.0.0.3
keypair_compute_nodes = /home/ubuntu/.ssh/key
```
