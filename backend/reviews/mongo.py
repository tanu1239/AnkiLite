from pymongo import MongoClient

_client = MongoClient("mongodb://localhost:27017")
_db = _client["anki_lite"]
reviews_col = _db["reviews"]
