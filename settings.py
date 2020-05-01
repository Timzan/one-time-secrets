import os
import pathlib
import yaml
import motor.motor_asyncio as aiomotor
from typing import Union, Dict
from os import PathLike


BASE_DIR = pathlib.Path(__file__).parent
config_path = BASE_DIR / 'config' / 'config.yaml'
crypt_key_path = BASE_DIR / 'config' / 'key.key'


def get_config(path: PathLike) -> Dict[str, Union[str, int]]:
    """Gets yaml config file and returns Dict

    :param path: Path to config file
    :type path: PathLike
    :return: Dict representation of a config file
    :rtype: dict
    """

    with open(path) as f:
        conf = yaml.safe_load(f)
    return conf


def get_crypt_key(path: PathLike) -> bytes:
    """Gets and returns cryptography key from a file

    :param path: Path to key file
    :type path: PathLike
    :return: String of bytes
    :rtype: bytes
    """

    with open(path, 'rb') as f:
        key = f.read()
    return key


async def init_mongo(conf: Dict[str, Union[str, int]], loop) -> aiomotor.AsyncIOMotorDatabase:
    """Create a new connection to MongoDB

    :param conf: Configuration with *host:port*
    :type conf: dict
    :param loop: Event loop
    :return: Connection to the database
    """
    host = os.environ.get('DOCKER_MACHINE_IP', '127.0.0.1')
    conf['host'] = host
    mongo_uri = f"mongodb://{conf['host']}:{conf['port']}"
    connection = aiomotor.AsyncIOMotorClient(
        mongo_uri,
        io_loop=loop)
    db_name = conf['database']
    return connection[db_name]


config = get_config(config_path)
crypt_key = get_crypt_key(crypt_key_path)


