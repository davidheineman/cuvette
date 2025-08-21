from beaker import Beaker, Experiment

beaker = Beaker.from_env()

user = beaker.user

print(beaker)