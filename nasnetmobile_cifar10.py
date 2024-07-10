# -*- coding: utf-8 -*-
"""NasNetMobile_cifar10.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1McNrtbDVybxry4WrDFcmhij6iUF20ZTg
"""

import numpy as np
import tensorflow_datasets as tfds
import tensorflow as tf  # For tf.data
import matplotlib.pyplot as plt
from keras import layers
from keras.applications import NASNetMobile

IMG_SIZE = 224
BATCH_SIZE = 16

# Load CIFAR-10 dataset
dataset_name = "cifar10"
(ds_train, ds_test), ds_info = tfds.load(
    dataset_name, split=["train[:800]", "test[:200]"], with_info=True, as_supervised=True
)
NUM_CLASSES = ds_info.features["label"].num_classes

# Resize images to IMG_SIZE
size = (IMG_SIZE, IMG_SIZE)
ds_train = ds_train.map(lambda image, label: (tf.image.resize(image, size), label))
ds_test = ds_test.map(lambda image, label: (tf.image.resize(image, size), label))

# Display some sample images
for i, (image, label) in enumerate(ds_train.take(9)):
    ax = plt.subplot(3, 3, i + 1)
    plt.imshow(image.numpy().astype("uint8"))
    plt.title("{}".format(label.numpy()))
    plt.axis("off")
plt.show()

# Define image augmentation layers
img_augmentation_layers = [
    layers.RandomRotation(factor=0.15),
    layers.RandomTranslation(height_factor=0.1, width_factor=0.1),
    layers.RandomFlip(),
    layers.RandomContrast(factor=0.1),
]

# Function to apply augmentation
def img_augmentation(images):
    for layer in img_augmentation_layers:
        images = layer(images)
    return images

# Display some augmented images
for image, label in ds_train.take(1):
    for i in range(9):
        ax = plt.subplot(3, 3, i + 1)
        aug_img = img_augmentation(np.expand_dims(image.numpy(), axis=0))
        aug_img = np.array(aug_img)
        plt.imshow(aug_img[0].astype("uint8"))
        plt.title("{}".format(label.numpy()))
        plt.axis("off")
plt.show()

# Preprocess training data
def input_preprocess_train(image, label):
    image = img_augmentation(image)
    label = tf.one_hot(label, NUM_CLASSES)
    return image, label

# Preprocess test data
def input_preprocess_test(image, label):
    label = tf.one_hot(label, NUM_CLASSES)
    return image, label

# Prepare datasets
ds_train = ds_train.map(input_preprocess_train, num_parallel_calls=tf.data.AUTOTUNE)
ds_train = ds_train.batch(batch_size=BATCH_SIZE, drop_remainder=False)
ds_train = ds_train.prefetch(tf.data.AUTOTUNE)

ds_test = ds_test.map(input_preprocess_test, num_parallel_calls=tf.data.AUTOTUNE)
ds_test = ds_test.batch(batch_size=BATCH_SIZE, drop_remainder=False)

# Define model
model = NASNetMobile(
    include_top=True,
    weights=None,
    classes=NUM_CLASSES,
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
)
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

model.summary()

# Train model
epochs = 10
hist = model.fit(ds_train, epochs=epochs, validation_data=ds_test)