# filepath: /workspaces/clearsettleAI/test_tensorflow.py
import tensorflow as tf

# Print TensorFlow version
print(f"TensorFlow version: {tf.__version__}")

# Test basic TensorFlow functionality
a = tf.constant(2)
b = tf.constant(3)
c = tf.add(a, b)
print(f"Result of TensorFlow addition: {c.numpy()}")