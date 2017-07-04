#!/usr/bin/env python
import os, sys, time, shutil, atexit
from selenium import webdriver
from pyvirtualdisplay import Display
import SocketServer, SimpleHTTPServer, threading
import  xattr
from texttable import Texttable
import ssdeep
from progress.bar import Bar

banner = r''' ___   ___                ___             ___
|   | |___|         ___  |___|           |   |
|   |  ___ ______ _|   |_ ___ ______ ____|_  |__
|   |_|_  |  ____|       |   |  __  |      |   /
|       | |____  |-|   |-|   | |__| | |====|   \
|_______|_|______| |___|_|   |_____ |______|_|__\
                     |       |     \|
                     |_______|

by: https://github.com/generaltesler
'''

helpmsg = r'''Listjack - Clickjack testing automation
Usage: sudo ./listjack.py <inputfile>
  where <inputfile> is a newline delimited list of URLs (including the protocol)
  e.g. http://site.com
       https://example.com
'''

if len(sys.argv) !=2:
    print '[-] Too few or too many arguments\n'
    print helpmsg
    sys.exit()

#global vars
cwd = os.getcwd()
epoch = str(int(time.time()))
urls = []

#disable terminal logging for request handler
class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def startserver():
#start local server in '/server' path
    if not os.path.exists(cwd+'/server'):
        os.makedirs(cwd+'/server')
    os.chdir(cwd+'/server')
    global httpd
    httpd = SocketServer.TCPServer(('127.0.0.1', 8080), MyHandler)
    thread = threading.Thread(target = httpd.serve_forever)
    thread.daemon = True
    thread.start()

def makebrowser():
    global display, driver, profile

    #create a hidden display for firefox
    display = Display(visible=0, size=(1920,1080))
    display.start()

    #create Firefox driver; ignore cert error
    profile = webdriver.FirefoxProfile()
    profile.accept_untrusted_certs = True
    driver = webdriver.Firefox(firefox_profile=profile)

def writelocalfile(url):
#writes the URL to the file, overwrites existing file
    template = '<html>Clickjacked!<iframe src="%s" width="99%%" height="99%%"></iframe></html>' % url
    with open(cwd+'/server/cj.html','w') as f:
        f.write(template)

def readin(filename):
    if not os.path.exists(filename):
        print '[-] File does not exist...quitting!'
        sys.exit()
    with open(filename,'r') as f:
        for line in f:
            urls.append(line.strip())

def cleanup():
#when done, kill the driver, display, and server then clean files
    try:
        driver.quit()
    except:
        pass
    try:   
        display.stop()
    except:
        pass
    try:
        httpd.shutdown()
    except:
        pass
    if os.path.exists(cwd+'/server'):
        shutil.rmtree(cwd+'/server')
    if os.path.isfile(cwd+'/geckodriver.log'):
        os.remove(cwd+'/geckodriver.log')

def requestloop(urls):
    urls = set(urls)
    imgdir = '/img_'+epoch
    if not os.path.exists(cwd+imgdir):
        os.makedirs(cwd+imgdir)
    i = 1
    for url in urls:
        writelocalfile(url)
        driver.get('http://127.0.0.1:8080/cj.html')
        name = str(i)+'.png'
        try:
            driver.get_screenshot_as_file(cwd+imgdir+'/'+name)
        except:
            print '[-] Error saving screenshot for: '+url
        xattr.setxattr(cwd+imgdir+'/'+name, 'user.url', url)
        i += 1

def comparetobaseline(image):
    basehash = ssdeep.hash_from_file(cwd+'/baseline.png')
    cjhash = ssdeep.hash_from_file(cwd+'/img_'+epoch+'/'+image)
    comparison = ssdeep.compare(basehash, cjhash)
    
    #value is 0 (dissimilar) to 100 (similar)
    return comparison

def processresults():
    results = Texttable()
    results.add_row(['File', 'Likeness', 'url'])
    i = len(os.listdir(cwd+'/img_'+epoch))
    bar = Bar('[+] Processing', max=i)
    for image in os.listdir(cwd+'/img_'+epoch):
        url = xattr.getxattr(cwd+'/img_'+epoch+'/'+image,'user.url')
        comp = comparetobaseline(image)
        results.add_row([image, comp, url])
        bar.next()
    bar.finish()
    print '[+] Printing results\n'
    print results.draw()
        

atexit.register(cleanup)

#main   
if __name__ == '__main__':
    print banner
    readin(sys.argv[1])
    
    print '[+] Preparing browser and local server'
    try:
        makebrowser()
        startserver()
    except:
        print '[-] Error! Couldn\'t start server and/or browser'
        sys.exit()

    print '[+] Attempting to jack'
    requestloop(urls)
    processresults()
