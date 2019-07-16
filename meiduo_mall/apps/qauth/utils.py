# 对openid进行加密
# 导包
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from meiduo_mall import settings


def get_access_token(open_id):
    # 创建对象
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=300)
    # 对数据进行处理
    data = {
        'token': open_id
    }
    # 加密
    token = s.dumps(data)
    return token.decode()


# 对openid进行检测
def check_openid_token(open_id):
    # 创建对象
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=300)
    open_id = s.loads(open_id)
    open_id = open_id['token']
    return open_id
