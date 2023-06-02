from .enum import Limits

"""help-texts for users.models"""
# help-text для email
USERS_HELP_EMAIL = (
    'Обязательно для заполнения. '
    f'Максимум {Limits.MAX_LEN_EMAIL_FIELD} букв.'
)
# help-text для username
USERS_HELP_UNAME = (
    'Обязательно для заполнения. '
    f'От {Limits.MIN_LEN_USERNAME} до {Limits.MAX_LEN_USERS_CHARFIELD} букв.'
)

# help-text для phone_number
USERS_HELP_PNUMBER = (
    'Необходимо указать номер телефона'
)

# help-text для first_name/last_name
USERS_HELP_FNAME = (
    'Обязательно для заполнения. '
    f'Максимум {Limits.MAX_LEN_USERS_CHARFIELD} букв.'
)

NOT_ALLOWED_ME = (
    'Нельзя создать пользователя с '
    'именем: << {username} >> - это имя запрещено!'
)

NOT_ALLOWED_CHAR_MSG = (
    '{chars} недопустимые символы '
    'в имени пользователя {username}.'
)

UNIQUE_USERNAME = 'Пользователь с таким именем уже существует!'


ALREADY_BUY = 'Уже добавлена в корзину'

ALREADY_ACTION = 'Ваш голос уже учтен'

USER_AVATAR = 'Наличие аватара увеличивает к вам доверие'

DUBLICAT_USER = 'Вы уже подписаны на этого пользователя!'

SELF_FOLLOW = 'Вы не можете подписаться на самого себя!'

PHONE_VALIDATE = 'Проверьте корректно ли указан номер телефона'
