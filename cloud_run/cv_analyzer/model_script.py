import tensorflow as tf
from keras.preprocessing.sequence import pad_sequences
import os
from google.cloud import storage
import pickle

destination_subdirectory = 'model'
model_filename = 'lstm.keras'
pickle_filename = 'tokenizer.pkl'

BUCKET_NAME = os.environ["DATASET_NAME"]


def download_model_files():
    if not os.path.exists(destination_subdirectory):
        os.makedirs(destination_subdirectory)

    destination_model_file_path = os.path.join(destination_subdirectory, model_filename)
    destination_pickle_file_path = os.path.join(destination_subdirectory, pickle_filename)
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)

    if not os.path.exists(destination_model_file_path):
        blob = bucket.blob(model_filename)
        blob.download_to_filename(destination_model_file_path)
    if not os.path.exists(destination_pickle_file_path):
        blob = bucket.blob(pickle_filename)
        blob.download_to_filename(destination_pickle_file_path)


download_model_files()

model = tf.keras.models.load_model(os.path.join(destination_subdirectory, model_filename))

with open(os.path.join(destination_subdirectory, pickle_filename), 'rb') as handle:
    loaded_tokenizer = pickle.load(handle)


def predict(text_entry):
    maxlen = 600
    new_texts_seq = loaded_tokenizer.texts_to_sequences(text_entry)
    new_texts_pad = pad_sequences(new_texts_seq, maxlen=maxlen)
    predictions = model.predict(new_texts_pad)
    return predictions[0][0]
