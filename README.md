## Требования

**Python 3.7+**

**MongoDB**

**Docker**

## Установка

```bash
$ git clone git@github.com:Timzan/one-time-secrets.git
```
```bash
$ cd one-time-secrets
```

## Запуск

Сборка и запуск контейнера:

```bash
$ docker-compose up
```
Конфигурация - 'config/config.yaml'

Ключ для шифрования/дешифрования - 'config/key.key'

Указать IP-адрес docker машины как переменную окружения в Dockerfile (по умолчанию: 192.168.99.100).

POST запрос на 

	http://192.168.99.100:5000/generate

"secret" - секрет

"code_phrase" - кодовая фраза

"lifetime" (необязательно)  - время жизни секрета в секундах 

Возвращает "secret_key"

Пример:

```JSON
{
  "secret": "My very secret example",
  "code_phrase": "code word example",
  "lifetime": 180
}
```

```JSON
{
 "secret_key": "pWP57QnGFjLAWRXkWbcYgG5khoSppaSd"
}
```

POST запрос на 

	http://192.168.99.100:5000/secrets/{secret_key}


"code_phrase" - кодовая фраза

Возвращает "secret"


```JSON
{
  "code_phrase": "code word example"
}
```

```JSON
{
  "secret": "My very secret example"
}
```




