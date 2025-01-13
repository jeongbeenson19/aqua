def is_collection_exists(db, collection_name):
    """Check if a collection exists in the MongoDB database."""
    return collection_name in db.list_collection_names()
