import trafaret as t
from trafaret.contrib.object_id import MongoId
from trafaret.contrib.rfc_3339 import DateTime


secret: t.Dict = t.Dict({
    t.Key('_id'): MongoId(),
    t.Key('encrypted_secret'): t.Bytes(),
    t.Key('code_phrase_hash'): t.String(),
    t.Key('secret_key'): t.String(),
    # t.Key('creation_date'): DateTime(),
})


async def get_secret_id(secret_collection, secret_key):
    """ Gets secret key and returns corresponding secret's id.

    :param secret_collection: MongoDB collection
    :param secret_key: Given secret key
    :return: Secret's id if it exists. Else None.
    """

    rv = await (secret_collection.find_one(
        {'secret_key': secret_key},
        {'_id': 1}))
    return rv['_id'] if rv else None
