import tensorflow as tf


def get_autoencoder(params, lr):
  """Callable model function compatible with Experiment API."""

  def autoencoder(features, labels, mode):
    with tf.variable_scope("ae"):
      x = features["inputs"]
      data_shape = x.shape.as_list()

      if len(x.shape) > 2:
        x = tf.reshape(x, [params.batch_size, -1])

      data_size = x.shape.as_list()[1]
      for layer_width in params.enc_layers:
        x = tf.layers.dense(
            x,
            layer_width,
            activation=params.activation,
            kernel_initializer=tf.glorot_normal_initializer())

      for layer_width in params.dec_layers:
        x = tf.layers.dense(
            x,
            layer_width,
            activation=params.activation,
            kernel_initializer=tf.glorot_normal_initializer())

      x = tf.layers.dense(
          x,
          data_size,
          activation=params.activation,
          kernel_initializer=tf.glorot_normal_initializer())

      if mode == tf.contrib.learn.ModeKeys.TRAIN:
        x = tf.nn.dropout(x, 1 - params.dropout)

      x = tf.reshape(x, data_shape)

      if len(x.shape) == 4 and len(labels.shape) == 4:
        tf.summary.image("inp/rcn/tar",
                         tf.concat([features["inputs"], x, labels], axis=2))

      mse_loss = tf.losses.mean_squared_error(labels, x)
      weight_reg = tf.add_n(
          [tf.nn.l2_loss(w) for w in tf.trainable_variables()])
      tf.summary.scalar("reconstr_err", mse_loss)
      total_loss = mse_loss + weight_reg * params.l2_loss

      gs = tf.contrib.framework.get_global_step()

      tf.summary.scalar("lr", lr)
      train_op = tf.contrib.layers.optimize_loss(
          name="training",
          loss=total_loss,
          global_step=gs,
          learning_rate=lr,
          clip_gradients=params.clip_grad_norm,
          optimizer=tf.contrib.estimator.TowerOptimizer(
              tf.train.AdamOptimizer(lr)),
          colocate_gradients_with_ops=True)

      return tf.estimator.EstimatorSpec(
          mode=mode, predictions=x, loss=total_loss, train_op=train_op)

  return autoencoder