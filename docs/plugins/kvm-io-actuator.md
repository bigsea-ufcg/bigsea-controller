# Actuator plugin - "kvm-io"

This plugin uses ssh to access instances in remote hosts and modify the amount of allocated resources.

## Configuration

The "kvm-io" plugin requires the following parameters in "controller.cfg"

#### compute_nodes

The ips of the compute nodes, separated by comma.

#### keypair_compute_nodes

The path of the key used to access the compute nodes.

#### iops_reference

The max possible disk throughput (iops) that can be allocated to a virtual machine.

#### bs_reference 

The max possible disk throughput, in bytes/sec, that can be allocated to a virtual machine.
  
## Example 

```
[actuator]
compute_nodes = 0.0.0.1, 0.0.0.2, 0.0.0.3
keypair_compute_nodes = /home/ubuntu/.ssh/key
iops_reference = 100
bs_reference = 50000
```
