# Cloud Utilities for Deep Learning ⛅️

## Quickstart

### GPU
```python
import cloud
cloud_env = cloud.env("gcp")

# gpu instances have a dedicated GPU so we don't need to worry
# about preemption or acquiring/releasing accelerators online.

while True:
  # train your model or w/e

cloud_env.down()  # stop the instance (does not delete instance)
```

### TPU
```python
import cloud
cloud_env = cloud.env("gcp")

tpu = cloud_env.tpu.up(preemptible=True)  # acquire the accelerator
# tpu contains info like the tpu's name location state etc.
with True:
  if not tpu.usable():
    tpu.down()  # release the accelerator
    tpu = cloud_env.tpu.up(preemptible=True)  # acquire the accelerator
  else:
    # train your model or w/e
    
tpu.down()  # release the accelerator
cloud_env.down()  # stop the instance (does not delete instance)
	  
```

## Structure

### cloud.env(type)

| param | desc. |
| :------- | :------- |
| type | python string indicating which instance type we are in. (e.g "gcp", "azure", "aws"). |
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
| `self.tpu.down(tpu_name)` | release the TPU with name `tpu_name` |


### cloud.AzureInstance(Instance)

`cloud.Instance` object for Azure.


### cloud.Accelerator

Abstract class for ephemeral accelerated hardware.

### cloud.TPU(Accelerator)

Class for TPU.

| properties | desc. |
| :------- | :------- |
| `self.name` | name of the TPU |
| `self.ip` | IP address of the TPU |
| `self.preemptible` | Boolean |
| **methods** | **desc.** |
| `self.down()` | release this TPU |


