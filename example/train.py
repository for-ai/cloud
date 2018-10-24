import tensorflow as tf
import os.path
import sys

import cloud

from model import get_autoencoder
from data import get_mnist


def main():
  run_config = tf.contrib.learn.RunConfig(save_checkpoints_steps=1000)

  hparams = tf.contrib.training.HParams(
      type="image",
      batch_size=64,
      learning_rate=0.01,
      lr_scheme="exp",
      delay=0,
      staircased=False,
      learning_rate_decay_interval=2000,
      learning_rate_decay_rate=0.1,
      clip_grad_norm=1.0,
      l2_loss=0.0,
      label_smoothing=0.1,
      init_scheme="random",
      warmup_steps=10000,
      encoder_depth=2,
      decoder_depth=2,
      hidden_size=100,
      is_ae=True,
      activation=tf.nn.sigmoid,
      enc_layers=[50, 50],
      dec_layers=[50],
      label_shape=[1],
      dropout=0,
      channels=1,
      input_shape=[28, 28, 1],
      output_shape=[28, 28, 1])

  train_input_fn = get_mnist("tmp/data", hparams, training=True)
  eval_input_fn = get_mnist("tmp/data", hparams, training=False)

  estimator = tf.estimator.Estimator(
      model_fn=get_autoencoder(hparams, 0.01),
      model_dir="tmp/run",
      config=run_config)

  estimator.train(train_input_fn, steps=100)
  estimator.evaluate(eval_input_fn, steps=10)


if __name__ == "__main__":
  FLAGS = tf.app.flags.FLAGS
  cloud.connect()
  main()
  cloud.down()