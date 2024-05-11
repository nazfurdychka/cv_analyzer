from google.cloud import firestore
from .request_models import UserSettings

db = firestore.Client()
collection_name = 'user_settings'
chat_id_field_name = 'chatId'
probability_ranges_count_field_name = 'probabilityRangesCount'
default_probability_ranges_count = 2


def save_user_settings(user_settings: UserSettings):
    data = user_settings.dict()
    doc_ref = db.collection(collection_name).document(user_settings.chatId)
    doc_ref.set(data)

    return doc_ref.id


def get_user_settings(chat_id: str):
    user_settings_docs = db.collection(collection_name).where(chat_id_field_name, '==', chat_id).stream()

    for doc in user_settings_docs:
        if doc.exists:
            return doc.to_dict()

    return {chat_id_field_name: chat_id, probability_ranges_count_field_name: default_probability_ranges_count}
