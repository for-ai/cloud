import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data


def get_mnist(data_source, params, training):
  """Input function for MNIST image data."""

  mnist = input_data.read_data_sets(data_source, one_hot=True)

  data_set = mnist.train if training else mnist.test

  def _input_fn():
    input_images = tf.constant(data_set.images)

    input_labels = tf.constant(
        data_set.labels) if not params.is_ae else tf.constant(data_set.images)

    image, label = tf.train.slice_input_producer([input_images, input_labels])

    imageBatch, labelBatch = tf.train.batch(
        [image, label], batch_size=params.batch_size)

    return {"inputs": imageBatch}, labelBatch

  return _input_fn