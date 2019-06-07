import urllib.request, urllib.error, urllib.parse
import threading
import queue

threads         = 250
target_url      = "http://testphp.vulnweb.com"
wordlist_file   = "/usr/share/wordlists/dirbuster/all.txt" # change this
resume          = None
user_agent      = "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) Gecko/20100101 Firefox/19.0"


def build_wordlist(wordlist_file):

    # read in the word list
    fd = open(wordlist_file, "rb")
    raw_words = fd.readlines()
    fd.close()

    found_resume = False
    words        = queue.Queue()

    for word in raw_words:

        word = word.rstrip()

        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print("Resuming wordlist from: %s" % resume)

        else:
            words.put(word)

    return words


def dir_bruter(word_queue, extensions=None):
    while not word_queue.empty():
        attempt = word_queue.get()

        attempt_list = []

        # check to see if there isa file extension; if not,
        # it's a directory path we're bruting
        if "." not in str(attempt):
            attempt_list.append("/%s/" % attempt)
        else:
            attempt_list.append("/%s" % attempt)

        # if we want to bruteforce extensions
        if extensions:
            for extension in extensions:
                attempt_list.append("/%s%s" % (attempt, extension))

        # iterate over our list of attempts
        for brute in attempt_list:

            url = "%s%s" % (target_url, urllib.parse.quote(brute))

            try:
                headers = {
                    'User-Agent': user_agent
                }
                r = urllib.request.Request(url, headers=headers)

                response = urllib.request.urlopen(r)

                if len(response.read()):
                    print("[%d] => %s" % (response.code, url))

            except urllib.error.URLError as e:

                if hasattr(e, 'code') and e.code != 404:
                    print("!!! %d => %s" % (e.code, url))

                pass


word_queue = build_wordlist(wordlist_file)
#extensions = [".php", ".bak", ".orig", ".inc"]

for i in range(threads):
    t = threading.Thread(target=dir_bruter, args=(word_queue,))
    t.start()