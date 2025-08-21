from beaker import Beaker

def get_default_user():
    beaker: Beaker = Beaker.from_env()
    user = beaker.account.name
    return user