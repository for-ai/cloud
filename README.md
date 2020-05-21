# Cloud Utilities for Deep Learning ⛅️ 

A super lightweight cloud management tool designed with deep learning applications in mind.


**Built with the belief that managing cloud resources should be as easy as:**

```python
import cloud

cloud.connect()
train_my_network()
cloud.down()
```

We welcome all contributions, suggestions, and use-cases. Reach out to us over GitHub or at team@for.ai with ideas!

## Contents
- [Quickstart](#quickstart)
    - [Install](#install)
    - [Config](#config)
    - [Usage](#usage)
- [Documentation](#documentation)
    - [Amazon EC2](#amazon-ec2)
    - [Azure](#azure)
    - [Google Cloud](#google-cloud)

## Quickstart

### Install:
Sort of stable:
```python
sudo pip install dl-cloud
```
Bleeding edge:
```python
git clone git@github.com:for-ai/cloud.git
sudo pip install -e cloud
```

### Config:

See `configs/cloud.toml-*` for instructions on how to authenticate for each provider (Google Cloud, AWS EC2, and Azure).

Place your completed configuration file (named `cloud.toml`) in either root `/` or `$HOME`. Otherwise, provide a full path to the file in `$CLOUD_CFG`.

If you use GCP as a provider for your `cloud.toml` it will use GCP Instance metadata APIs to fetch APIs. If you want to configure for Google Cloud Build, please use; 
```toml
is_gcb = true
zone = '{{DESIRED_ZONE}}' 
```

### Usage:
#### GPU
```python
import cloud
cloud.connect()

# gpu instances have a dedicated GPU so we don't need to worry
# about preemption or acquiring/releasing accelerators online.

while True:
  # train your model or w/e

cloud.down()  # stop the instance (does not delete instance)
```

#### TPU (Only on GCP)
```python
import cloud
cloud.connect()

tpu = cloud.instance.tpu.get(preemptible=True)  # acquire an accelerator
while True:
  if not tpu.usable:
    tpu.delete(background=True)  # release the accelerator in the background
    tpu = cloud.instance.tpu.get(preemptible=True)  # acquire a new accelerator
  else:
    # train your model or w/e
    
cloud.down()  # release all resources, then stop the instance (does not delete instance)
```

---

# Documentation

### cloud.connect()
Takes/Creates a `cloud.Instance` object and sets `cloud.instance` to it. 

| **returns** | **desc.** |
| :------- | :------- |
| cloud_env | a cloud.Instance.  |

### cloud.down()
Calls `cloud.instance.down()`.

### cloud.delete(confirm=True)
Calls `cloud.instance.delete(confirm)`.

### cloud.Resource
Takes/Creates a `cloud.Instance` object and sets `cloud.instance` to it. 

| properties | desc. |
| :------- | :------- |
| `name` | str, name of the instance |
| `usable ` | bool, whether this resource is usable |
| **methods** | **desc.** |
| `up(background=False)` | start an existing stopped resource |
| `down(background=False)` | stop the resource. Note: this should not necessarily delete this resource |
| `delete(background=False)` | delete this resource |

### cloud.Instance(Resource)

An object representing a cloud instance with a set of Resources that can be allocated/deallocated.

| properties | desc. |
| :------- | :------- |
| `resource_managers` | list of ResourceManagers |
| **methods** | **desc.** |
| `down(background=False, delete_resources=True)` | stop this instance and optionally delete all managed resources |
| `delete(background=False, confirm=True)` | delete this instance with optional user confirmation |

### cloud.ResourceManager

Class for managing the creation and maintanence of `cloud.Resources`.

| properties | desc. |
| :------- | :------- |
| `instance ` | `cloud.Instance` instance owning this resource manager |
| `resource_cls ` | `cloud.Resource` type, the class of the resource to be managed |
| `resources ` | list of `cloud.Resource`s, managed resources |
| **methods** | **desc.** |
| `__init__(instance, resource_cls)` | `instance`: the `cloud.Instance` object operating this ResourceManager  |
|  | `resource_cls `: the `cloud.Resource` class this object manages |
| `add(*args, **kwargs)` | add an existing resource to this manager |
| `remove(*args, **kwargs)` | remove an existing resource from this manager |

## Amazon EC2
### cloud.AWSInstance(Instance)

A `cloud.Instance` object for AWS EC2 instances.

## Azure
### cloud.AzureInstance(Instance)

A `cloud.Instance` object for Microsoft Azure instances.

## Google Cloud

Our GCPInstance requires that your instances have `gcloud` installed and properly authenticated so that `gcloud alpha compute tpus create test_name` runs without issue.

### cloud.GCPInstance(Instance)

A `cloud.Instance` object for Google Cloud instances.

| properties | desc. |
| :------- | :------- |
| `tpu ` | `cloud.TPUManager`, a resource manager for this instance's TPUs |
| `resource_managers ` | list of owned `cloud.ResourceManager`s |
| **methods** | **desc.** |
| `__init__(collect_existing_tpus=True, **kwargs)` | `collect_existing_tpus `: bool, whether to add existing TPUs to this manager  |
|  | `**kwargs `: passed to `cloud.Instance`'s initializer |


### cloud.TPU(Resource)

Resource class for TPU accelerators.

| properties | desc. |
| :------- | :------- |
| `ip` | str, IP address of the TPU |
| `preemptible` | bool, whether this TPU is preemptible or not |
| `details` | dict {str: str}, properties of this TPU |
| **methods** | **desc.** |
| `up(background=False)` | start this TPU |
| `down(background=False)` | stop this TPU |
| `delete(background=False)` | delete this TPU |

### cloud.TPUManager(ResourceManager)

ResourceManager class for TPU accelerators.

| properties | desc. |
| :------- | :------- |
| `names` | list of str, names of the managed TPUs |
| `ips` | list of str, ips of the managed TPUs |
| **methods** | **desc.** |
| `__init__(instance, collect_existing=True)` | `instance`: the `cloud.GCPInstance` object operating this TPUManager  |
|  | `collect_existing`: bool, whether to add existing TPUs to this manager |
| `clean(background=True)` | delete all managed TPUs with unhealthy states  |
| `get(preemptible=True)` | get an available TPU, or create one using `up()` if none exist |
| `up(preemptible=True, background=False)` | allocate and manage a new instance of `resource_cls ` |
