import hashlib
import numpy
import mmh3 # returns 32 bit integer with second argument as a seed  mmh: https://github.com/hajimes/mmh3

default_size = 10000000

class BloomFilter():
    def __init__(self):
        self.table = numpy.zeros(default_size)
        with open("100k-common-passwords.txt") as f:
            passwords = [line.strip() for line in f.readlines()]
        
        for password in passwords:
            self.add(password)
        
    def add(self, password):
        for index in BloomFilter.get_hashes(password):
            self.table[index] = 1
            
    def get_hashes(password):
        hash1 = BloomFilter.mmh_hash(password, seed=378)
        hash2 = BloomFilter.mmh_hash(password, seed=25)
        hash3 = BloomFilter.lib_hash(password, salt="CSDS444")
        hash4 = BloomFilter.lib_hash(password, salt="Computer Security")
        return hash1, hash2, hash3, hash4
        
    def mmh_hash(password, seed, size=default_size): 
        hash1 = mmh3.hash(password, seed)
        return hash1 % size
    
    def lib_hash(password, salt, size=default_size): 
    
        m = hashlib.sha256()
        salted_pass = salt + password
        m.update(salted_pass.encode('utf-8'))

        return int(m.hexdigest(), 32) % size

bloom = BloomFilter()

def bloom_filter_validate(password):
    for index in BloomFilter.get_hashes(password):
        if bloom.table[index] == 0:
            return True
    return False
        

def validate_password(password1, password2):
    if len(password1) < 6:
        return False, "Password must be at least 6 characters."
    noLetter = True
    noNumber = True
    for c in password1:
        if c.isalpha(): #Checks that password contains at least 1 letter
            noLetter = False
        elif c.isdigit(): #Checks that password contains at least 1 number
            noNumber = False

    if noLetter:
        return False, "Password must contain at least 1 letter"
    if noNumber:
        return False, "Password must contain at least 1 number"
    if password1 != password2:
        return False, "Passwords must match."
    if not bloom_filter_validate(password1):
        return False, "Password is too common (did not pass bloom filter)."
    return True, "Password accepted."
    