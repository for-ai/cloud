# Cloud Utilities for Deep Learning ⛅️

A super lightweight cloud management tool designed with deep learning applications in mind.

This project is still a work in progress. We welcome all contributions, suggestions, and use-cases. Reach out to us over GitHub or at team@for.ai with ideas!

## Quickstart

### Install:

```
git clone git@github.com:for-ai/cloud.git
sudo pip install -e cloud
```

### Config:

See `configs/cloud.toml-*` for instructions on how to authenticate for each provider (Google Cloud, AWS EC2, and Azure).

Place your completed configuration file (named `cloud.toml`) in either root `/` or `$HOME`. Otherwise, provide a full path to the file in `$CLOUD_CFG`.

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

tpu = cloud.instance.tpu.up(preemptible=True)  # acquire the accelerator
while True:
  if not tpu.usable:
    tpu.delete(async=True)  # release the accelerator in the background
    tpu = cloud.instance.tpu.up(preemptible=True)  # acquire a new accelerator
  else:
    # train your model or w/e
    
cloud.down()  # release all resources, then stop the instance (does not delete instance)
```

---

# Documentation

### cloud.connect(arg=None)
Takes/Creates a `cloud.Instance` object and sets `cloud.instance` to it. 

| param | desc. |
| :------- | :------- |
| arg | One of: |
|     | - None (default), will infer from `config.toml` |
|     | - cloud.Instance object. |
| **returns** | **desc.** |
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
| `down_cmd ` | list of str, command to stop this resource. Passed to subprocess.run |
| `delete_cmd ` | list of str, command to delete this resource. Passed to subprocess.run |
| `usable ` | bool, whether this resource is usable |
| **methods** | **desc.** |
| `down()` | stop the resource. Note: this should not necessarily delete this resource |
| `delete(confirm=True)` | delete this resource |

### cloud.Instance(Resource)

An object representing a cloud instance with a set of Resources that can be allocated/deallocated.

| properties | desc. |
| :------- | :------- |
| `resource_managers` | list of ResourceManagers |

### cloud.ResourceManager

Class for managing the creation and maintanence of `cloud.Resources`.

| properties | desc. |
| :------- | :------- |
| `resource_cls ` | `cloud.Resource` type, the class of the resource to be managed |
| `up_cmd ` | list of str, command to create a resource. Passed to subprocess.run |
| `preemptible_flag ` | str, flag to append to `up_cmd` in order to request a preemptible version of a resource |
| `resources ` | list of `cloud.Resource`s, managed resources |
| **methods** | **desc.** |
| `__init__(instance, resource_cls)` | `instance`: the `cloud.Instance` object operating this ResourceManager  |
|  | `resource_cls `: the `cloud.Resource` class this object manages |
| `add(*args, **kwargs)` | add an existing resource to this manager |
| `remove(*args, **kwargs)` | remove an existing resource from this manager |
| `up(preemptible=True)` | allocate and manage a new instance of `resource_cls ` |

## Google Cloud

Our GCPInstance requires that your instances have `gcloud` installed and properly authenticated so that `gcloud alpha compute tpus create`

### cloud.GCPInstance(Instance)

A `cloud.Instance` object for Google Cloud instances.

| properties | desc. |
| :------- | :------- |
| `tpu ` | `cloud.TPUManager`, a resource manager for this instance's TPUs |
| `up_cmd ` | list of str, command to create a resource. Passed to subprocess.run |
| `preemptible_flag ` | str, flag to append to `up_cmd` in order to request a preemptible version of a resource |
| `resources ` | list of `cloud.Resource`s, managed resources |
| **methods** | **desc.** |
| `__init__(instance, resource_cls)` | `instance`: the `cloud.Instance` object operating this ResourceManager  |
|  | `resource_cls `: the `cloud.Resource` class this object manages |
| `add(*args, **kwargs)` | add an existing resource to this manager |
| `remove(*args, **kwargs)` | remove an existing resource from this manager |
| `up(preemptible=True)` | allocate and manage a new instance of `resource_cls ` |


### cloud.TPU(Resource)

Resource class for TPU accelerators.

| properties | desc. |
| :------- | :------- |
| `ip` | str, IP address of the TPU |
| `preemptible` | bool, whether this TPU is preemptible or not |
| `details` | dict {str: str}, properties of this TPU |

### cloud.TPUManager(ResourceManager)

ResourceManager class for TPU accelerators.

| properties | desc. |
| :------- | :------- |
| `names` | list of str, names of the managed TPUs |
| `ips` | list of str, ips of the managed TPUs |
| **methods** | **desc.** |
| `__init__(instance)` | `instance`: the `cloud.GCPInstance` object operating this TPUManager  |


