import cloud
from cloud import registry as reg
from cloud import Instance


def connect(arg):

  if isinstance(arg, str):
    cloud.instance = reg.retrieve(arg)
  elif isinstance(arg, Instance):
    cloud.instance = arg()
  else:
    raise Exception(f"Unknown input type: {type(arg)}."
                    " Please provide a string or Instance object.")


def down():
  cloud.instance.down()
  

def delete(confirm=True):
  cloud.instance.delete(confirm)
