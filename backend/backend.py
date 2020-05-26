import pymongo


class User:
    def __init__(self):
        self.__client = pymongo.MongoClient('localhost', 27017)
        self.__db = self.__client.my_database  # CreateDB
        self.__user = self.__db.user  # Create collection

    def refresh_db(self):
        """
        Refreshes DB - only for maintenance purpose
        """
        self.__db = self.__client.my_database  # CreateDB
        self.__client.drop_database(self.__db)  # [Refresh] Delete
        self.__db = self.__client.my_database  # [Refresh] Re-CreateDB

    def __get_sequence(self, name: str) -> int:
        """
        Obtains sequence value in "_id" field of given collection name
        :param name: Collection name
        :type: str
        :return: Sequence value
        :type: int
        """
        collection = self.__db.sequences
        document = collection.find_one_and_update({"_id": name}, {"$inc": {"value": 1}}, return_document=True)
        try:
            sequence = int(document["value"])
        except TypeError:
            sequence = 0
            collection.insert_one({'_id': name, "value": sequence})
        return sequence

    def create(self, doc: dict):
        """
        :param doc: Example {'email': 'jsmith@domain.com', 'password':'myPassword', 'fname': 'John', 'lname': 'Smith'}
        :type: dict
        :return:
        """
        if not isinstance(doc, dict):
            return {'Message': ['Error: doc should be instance of dict.']}
        try:
            doc['_id'] = self.__get_sequence('user')
            self.__user.insert_one(doc)
            return doc
        except pymongo.errors.ServerSelectionTimeoutError:
            return {'Message': ['Error: Check DB connection.']}

    def get(self, args: dict):
        if not isinstance(args, dict):
            return {'Message': ['Error: args should be instance of dict.']}
        results = {}
        k = 0
        try:
            r = self.__user.find(args)
            for doc in r:
                results[k] = doc
                k += 1
            return results
        except pymongo.errors.ServerSelectionTimeoutError:
            return {'Message': ['TimeoutError: Check DB connection.']}

    def get_id(self, _id: int):
        if not isinstance(_id, int):
            return {'Message': ['Error: _id should be instance of int.']}
        try:
            return self.__user.find_one({'_id': _id})
        except pymongo.errors.ServerSelectionTimeoutError:
            return {'Message': ['TimeoutError: Check DB connection.']}

    def update(self, _id: int, update: dict):
        if not isinstance(_id, int):
            return {'Message': ['Error: _id should be instance of int.']}
        if not isinstance(update, dict):
            return {'Message': ['Error: update should be instance of dict.']}
        try:
            return self.__user.update_one({'_id': _id}, {"$set": update}, upsert=True)
        except pymongo.errors.ServerSelectionTimeoutError:
            return {'Message': ['TimeoutError: Check DB connection.']}

    def delete(self, _id: int):
        if not isinstance(_id, int):
            return {'Message': ['Error: _id should be instance of int.']}
        try:
            return self.__user.delete_one({'_id': _id})
        except pymongo.errors.ServerSelectionTimeoutError:
            return {'Message': ['TimeoutError: Check DB connection.']}
