#! /usr/bin/env python3
#  Rather than try javaws, lets just download the jars and run them locally

import logging
import os
import platform
import re
import socket
import subprocess
import sys
import tempfile
import urllib.parse
import zipfile

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

login_url = "{s}://{svr}/rpc/WEBSES/create.asp"
jnlp_url = "{s}://{svr}/Java/jviewer.jnlp?EXTRNIP={svr}&JNLPSTR=JViewer"
jar_base_url = "{s}://{svr}/Java/release/"
main_class = "com.ami.kvm.jviewer.JViewer"


#  Make it easy to just put in host name and auto add the '-ipmi'
#  Returns IP address
def get_ipaddr(address):
    try:  # Is a valid ipv4 address
        socket.inet_aton(address)
        return address
    except OSError:
        if "-ipmi" in address:
            return socket.gethostbyname(address)
        elif "." in address:
            return socket.gethostbyname(address.replace(".", "-ipmi.", 1))
        else:
            return socket.gethostbyname(address + "-ipmi")


#  Follow redirects probably to a https website and then use https rather than http
def scheme_test(server):
    r = requests.get(url=("http://{svr}".format(svr=server)), verify=False)
    return urllib.parse.urlparse(r.url).scheme


# Download the 3 files that are needed. Always named the same, so no
# need to parse jnlp xml
def download_jars(scheme, server, tmpdir):
    system = platform.system()
    if system == "Linux":
        natives = "Linux_x86_"
    elif system == "Windows":
        natives = "Win"
    elif system == "Darwin":
        natives = "Mac"
    else:
        raise Exception("OS not supported: " + system)
    natives += platform.architecture()[0][:2] + ".jar"

    for jar in ["JViewer.jar", "JViewer-SOC.jar", natives]:
        jar_path = os.path.join(tmpdir, jar)
        base = jar_base_url.format(s=scheme, svr=server)
        r = requests.get(base + jar, verify=False)
        # r.raise_for_status()
        with open(jar_path, "wb") as f:
            logging.info("downloading %s -> %s" % (base + jar, jar_path))
            f.write(r.content)
        if jar == natives:
            logging.debug("extracting %s" % jar_path)
            try:
                with zipfile.ZipFile(jar_path, "r") as natives_jar:
                    natives_jar.extractall(path=tmpdir)
            except zipfile.BadZipFile:
                logging.error("NO NATIVE LIBS FOUND FOR {}".format(jar))


#  Get a session cookie
#  Download the jnlp file to get command line args
#  Run local java with args
def run_jviewer(scheme, server, tmpdir):
    credentials = {"WEBVAR_USERNAME": "admin", "WEBVAR_PASSWORD": "admin"}
    login_response = requests.post(
        login_url.format(s=scheme, svr=server), data=credentials, verify=False
    )
    session_cookie = re.search(
        "'SESSION_COOKIE' : '([a-zA-Z0-9]+)'", login_response.text
    ).group(1)

    jnlp_request = requests.get(
        jnlp_url.format(s=scheme, svr=server),
        headers={"Cookie": "SessionCookie=%s" % session_cookie},
        verify=False,
    )
    with open(tmpdir + "/jviewer.jnlp", "wb") as jnlpfile:
        jnlpfile.write(jnlp_request.content)

    args = [
        "java",
        "-Djava.library.path=" + tmpdir,
        "-cp",
        os.path.join(tmpdir, "*"),
        main_class,
    ]
    args += re.findall(
        "<argument>([^<]+)", jnlp_request.text
    )  # Fixes some machines that use malformed xml
    logging.info(" ".join(args))
    subprocess.run(args)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    server = sys.argv[1] if len(sys.argv) > 1 else input("Server: ")
    ip = get_ipaddr(server)
    scheme = scheme_test(ip)
    with tempfile.TemporaryDirectory(prefix="jviewer-starter") as td:
        download_jars(scheme, ip, td)
        run_jviewer(scheme, ip, td)
