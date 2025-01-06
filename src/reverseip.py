# Reverse Domain Lookup

import sys
import urllib.parse
import urllib.request
import json
from urllib.parse import urlparse

from web import useragents


def reverseip(url):
    """return domains from given the same server"""

    # get only domain name
    url = urlparse(url).netloc if urlparse(url).netloc != '' else urlparse(url).path.split("/")[0]

    source = "http://domains.yougetsignal.com/domains.php"
    useragent = useragents.get()
    contenttype = "application/x-www-form-urlencoded; charset=UTF-8"

    # POST method
    opener = urllib.request.build_opener(
        urllib.request.HTTPHandler(), urllib.request.HTTPSHandler())
    data = urllib.parse.urlencode([('remoteAddress', url), ('key', '')]).encode('utf-8')

    request = urllib.request.Request(source, data)
    request.add_header("Content-type", contenttype)
    request.add_header("User-Agent", useragent)

    try:
        result = urllib.request.urlopen(request).read().decode('utf-8')

    except urllib.error.HTTPError as e:
        print("[{}] HTTP error".format(e.code), file=sys.stderr)

    except urllib.error.URLError as e:
        print("URL error, {}".format(e.reason), file=sys.stderr)

    except:
        print("HTTP exception", file=sys.stderr)

    obj = json.loads(result)

    # if successful
    if obj["status"] == 'Success':
        domains = []
        for domain in obj["domainArray"]:
            domains.append(domain[0])
        return domains

    print("[ERR] {}".format(obj["message"]), file=sys.stderr)
    return []
