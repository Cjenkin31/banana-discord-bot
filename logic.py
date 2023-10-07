import random
from pets import RandomCatAPIPet, RandomPet
def ChooseLocalOrApi():
    if ( random.random() >= .5 ):
        return RandomPet()
    return RandomCatAPIPet()
