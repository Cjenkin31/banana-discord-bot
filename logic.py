import random
from pets import RandomCatAPIPet, RandomPet
def ChooseLocalOrApi():
    return RandomCatAPIPet()
    if ( random() >= .5 ):
        return RandomPet()
    return RandomCatAPIPet()
