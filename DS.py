import os
import os.path
from os import path
import pathlib
import sys
import time
import random
import string
import pyprimes
from Crypto.Util import number
from Crypto.Hash import SHA3_256

def Setup(candidate_p_count = 1, verbose = False):
    bitSizeP = 2048
    bitSizeQ = 224

    isPFound = False

    # Generate q and p:
    while isPFound == False:
        q = number.getPrime(bitSizeQ, os.urandom)
        p = 0

        maxP = (2**bitSizeP) - 1
        k = (maxP - 1) // q

        candidates = []

        while k > 1:
            k = k - 1
            p = (k*q) + 1

            if number.isPrime(p):
                isPFound = True
                candidates.append(p)
            
            if len(candidates) >= candidate_p_count:
                break
        
        p = random.choice(candidates)

    # Generate g:
    g = 1
    exponent = (p - 1) // q

    while g == 1:
        alpha = random.randint(1, p - 1)
        g = pow(alpha, exponent, p)

    if verbose:
        print("q: %d \n\np: %d \n\ng: %d" %(q, p, g))

    return q, p, g

def KeyGen(q, p, g):
    alpha = random.randint(0, q - 1)
    beta = pow(g, alpha, p)
    return alpha, beta

def GenerateOrRead(fileName, verbose = False):
    file = open(fileName, "a+")
    file.close()

    if os.stat(fileName).st_size == 0:
        q, p, g = Setup(verbose=True)
        fileStr = str(q) + '\n' + str(p) + '\n' + str(g)

        file = open(fileName, "w")
        file.write(fileStr)
        file.close()

    file = open(fileName, "r")
    q = int(file.readline())
    p = int(file.readline())
    g = int(file.readline())

    if verbose:
        print("q: %d \n\np: %d \n\ng: %d" %(q, p, g))

    return q, p, g

def random_string(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def egcd(a, b):
    x,y, u,v = 0,1, 1,0
    while a != 0:
        q, r = b//a, b%a
        m, n = x-u*q, y-v*q
        b,a, x,y, u,v = a,r, u,v, m,n
    gcd = b
    return gcd, x, y

def modinv(a, m):
    if a < 0:
        a = a+m
    gcd, x, y = egcd(a, m)
    if gcd != 1:
        return None  # modular inverse does not exist
    else:
        return x % m

def SignGen(message, q, p, g, alpha):  # generating signature
    k = random.randint(0, q-2)  # select random number for k
    r = pow(g, k, p)  # calculate r
    sha_obj1 = SHA3_256.new()  # create a SHA3_256 object
    data1 = (str(message) + str(r)).encode('utf-8')  # concatenate the string with r and encode the new string into byte format
    h = sha_obj1.update(data1)  # hash the encoded string
    h_hex = h.hexdigest()  # make the hash turn into hex format
    h_int = int(h_hex, 16)  # convert hex to decimal
    del sha_obj1
    s = ((alpha * h_int) + k) % q  # calculate the s value
    return s,h_int

def SignVer(message, s, h, q, p, g, beta):  # verification of the signature
    new_h = -h
    while new_h < 0:
        new_h += p-1
    first = pow(g, s, p)
    second = pow(beta, new_h, p)
    v = (first * second)% p  # calculate v
    sha_obj2 = SHA3_256.new()  # create a SHA3_256 object
    data2 = (str(message) + str(v)).encode('utf-8')  # concatenate the string with v and encode the new string into byte format
    h_tilde = sha_obj2.update(data2)  # hash the encoded string
    h_tilde_hex = h_tilde.hexdigest()  # make the hash turn into hex format
    h_tilde_int = int(h_tilde_hex, 16)  # convert hex to decimal
    del sha_obj2
    print(h%q)
    print(h_tilde_int%q)
    print(q)
    if (h%q) == (h_tilde_int % q):  # if h_tilde is equal to h in modulo q, then verification is successful
        return 0
        # print("ACCEPT")
    else:  # for all the other cases, verification is not successful
        return 1
        # print("REJECT")
