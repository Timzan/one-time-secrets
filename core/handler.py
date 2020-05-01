import secrets
import string
import datetime
import motor.motor_asyncio as aiomotor
from bson import ObjectId
from aiohttp import web
from typing import Optional
from core.utils import validate_secret_key, generate_phrase_hash, check_phrase_hash, encrypt_secret, decrypt_secret


alphabet = string.ascii_letters + string.digits


class MyHandler:
    """
    Custom request handler.
    """

    def __init__(self, mongo: aiomotor.AsyncIOMotorDatabase) -> None:
        self._mongo = mongo

    @property
    def mongo(self):
        return self._mongo

    async def generate(self, request: web.Request) -> web.Response:
        """Gets secret and code phrase as a request and returns corresponding response.
        Creates document in the database if request is correct. Expects JSON as a request.

        :param request: JSON request object.
        :return: JSON response
        """
        if request.method != 'POST':
            return web.json_response({'error': 'method not allowed'}, status=405)
        try:
            data = await request.json()
            lifetime: Optional[int] = None
            try:
                lifetime = data['lifetime']
            except KeyError:
                pass
            if len(data) > 2 and not lifetime:
                raise Exception(f'Number of keys: {len(data)}. Define lifetime or remove excess key.')
            elif len(data) > 3:
                raise Exception(f'Number of keys: {len(data)}. Too many keys')
            secret = data['secret']
            code_phrase = data['code_phrase']
            if not isinstance(secret, str) or not isinstance(code_phrase, str):
                raise TypeError('secret and code phrase must be string')
            if lifetime and not isinstance(lifetime, int):
                raise TypeError('lifetime must be integer')
            timestamp = datetime.datetime.utcnow()
            secret_key = ''.join(secrets.choice(alphabet) for i in range(32))
            encrypted_secret = encrypt_secret(secret)
            await self.mongo.secret.insert_one({
                'encrypted_secret': encrypted_secret,
                'code_phrase_hash': generate_phrase_hash(code_phrase),
                'secret_key': secret_key,
                f'date_{secret_key}': timestamp
            })
            if lifetime:
                await self.mongo.secret.create_index(f'date_{secret_key}', name=secret_key, expireAfterSeconds=lifetime,
                                                     background=True,
                                                     partialFilterExpression={'secret_key': {'$eq': secret_key}})
            return web.json_response({
                "secret_key": secret_key
            })
        except KeyError as e:
            return web.json_response({
                'error_type': str(type(e)),
                'missing_key': str(e),
            }, status=400)
        except Exception as e:
            return web.json_response({
                'error_type': str(type(e)),
                'error_msg': str(e)
            }, status=400)

    async def return_secret(self, request: web.Request) -> web.Response:
        """Gets secret key as a request and returns corresponding response.
        Returns secret if secret key is correct. Removes secret from database after successful response.


        :param request: JSON request object.
        :return: JSON response.
        """
        if request.method != 'POST':
            return web.json_response({'error': 'method not allowed'}, status=405)
        secret_key = request.match_info['secret_key']
        error = await validate_secret_key(self.mongo, secret_key)
        if error:
            return web.json_response({'error': error})
        try:
            data = await request.json()
            if len(data) > 1:
                raise Exception('too many keys')
            code_phrase = data['code_phrase']
            if not isinstance(code_phrase, str):
                raise TypeError('code phrase must be string')
            result = await self.mongo.secret.find_one(
                {

                    'secret_key': secret_key
                },
                {
                    '_id': 1,
                    'encrypted_secret': 1,
                    'code_phrase_hash': 1,
                }
            )
            if not check_phrase_hash(result['code_phrase_hash'], code_phrase):
                raise ValueError('wrong code phrase')
            if result is None:
                raise TypeError('there is no such secret')
            secret = decrypt_secret(result['encrypted_secret'])
            await self.mongo.secret.delete_one({'_id': ObjectId(result['_id'])})
            return web.json_response({'secret': secret})
        except KeyError as e:
            return web.json_response({
                'error_type': str(type(e)),
                'missing_key': str(e),
            }, status=400)
        except Exception as e:
            return web.json_response({
                'error_type': str(type(e)),
                'error_msg': str(e),
            }, status=400)


@web.middleware
async def error_middleware(request: web.Request, handler) -> web.Response:
    """ Handles 404 error. Return corresponding JSON response.

    :param request: Request object
    :param handler: Default request handler
    :return: JSON response
    """

    try:
        response = await handler(request)
        if response.status != 404:
            return response
        message = response.message
    except web.HTTPException as ex:
        if ex.status != 404:
            raise
        message = ex.reason
    return web.json_response({'error': message}, status=404)



