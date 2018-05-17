# Metric Source plugin - "monasca"

This plugin uses the monasca client library to get metrics from an available monasca deployment.

## Configuration

The "monasca" plugin requires the following parameters in "scaler.cfg"

* **monasca_endpoint**: The endpoint for the Monasca's service.

* **username**: The username with permissions to publish and get metrics from monasca.

* **password**: The above-mentioned user's password.

* **project_name**: The above-mentioned user's keystone project.

* **auth_url**: The keystone authentication endpoint.

* **api_version**: Monasca API version.

## Example
```
[monasca]
monasca_endpoint = http://1.1.1.1:8070
username = monasca
password = monasca
project_name = monasca-project
auth_url = http://2.2.2.2:5000/v3/
api_version = 2_0
```
