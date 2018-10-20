# Cloud Utilities for Deep Learning ⛅️

A very light-weight cloud management tool designed with deep learning applications in mind.

This project is still a work in progress. We welcome all contributions, suggestions, and use-cases. Reach out to us over GitHub or at team@for.ai with ideas!

## Quickstart

Install:
```
git clone git@github.com:for-ai/cloud.git
sudo pip install -e cloud
```

### GPU
```python
import cloud
cloud.connect("gcp")

# gpu instances have a dedicated GPU so we don't need to worry
# about preemption or acquiring/releasing accelerators online.

while True:
  # train your model or w/e

cloud.disconnect()  # stop the instance (does not delete instance)
```

### TPU
```python
import cloud
cloud.connect("gcp")

tpu = cloud.instance.tpu.up(preemptible=True)  # acquire the accelerator
# tpu contains info like the tpu's name location state etc.
with True:
  if not tpu.usable():
    tpu.down()  # release the accelerator
    tpu = cloud.instance.tpu.up(preemptible=True)  # acquire the accelerator
  else:
    # train your model or w/e
    
cloud.disconnect()  # release all resources, then stop the instance (does not delete instance)
```

## Structure

### cloud.connect(arg)

| param | desc. |
| :------- | :------- |
| arg | One of: |
|     | - python string indicating which instance type we are in. (e.g "gcp", "azure", "aws"). |
|     | - cloud.Instance object. |
| **returns** | **desc.** |
| cloud_env | a cloud.Instance.  |

### cloud.Instance

An object containing information about the instance it lives in + utilities for resource management.

| properties | desc. |
| :------- | :------- |
| `self.name` | name of the instance |
| **methods** | **desc.** |
| `self.down()` | stop the instance. Note: this does not necessarily delete all associate resources (e.g harddrives are should be preserved) |
| `self.delete()` | delete the instance and **all** associated reasources |

### cloud.GCPInstance(Instance)

`cloud.Instance` object for GCP.

| methods | desc. |
| :------- | :------- |
| `self.tpu.up(preemptible=False)` | acquire a TPU with optional preemptibility. |

### cloud.Resource

Abstract class for (possibly ephemeral) accelerated hardware and the like.

### cloud.ResourceManager

Class for managing the creation and maintanence of `cloud.Resources`.

### cloud.TPU(Resource)

Class for TPU.

| properties | desc. |
| :------- | :------- |
| `self.name` | name of the TPU |
| `self.ip` | IP address of the TPU |
| `self.preemptible` | Boolean |
| **methods** | **desc.** |
| `self.down()` | release this TPU |


