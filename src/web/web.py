#import sys
import urllib.request
from urllib.parse import urlparse

import useragents


def gethtml(url, lastURL=False):
    """return HTML of the given url"""

    if not (url.startswith("http://") or url.startswith("https://")):
        url = "http://" + url

    header = useragents.get()
    request = urllib.request.Request(url, None, header)
    html = None

    try:
        reply = urllib.request.urlopen(request, timeout=10)

    except urllib.error.HTTPError as e:
        # read html content anyway for reply with HTTP500
        if e.getcode() == 500:
            html = e.read()
        #print >> sys.stderr, "[{}] HTTP error".format(e.code)
        pass

    except urllib.error.URLError as e:
        #print >> sys.stderr, "URL error, {}".format(e.reason)
        pass

    except KeyboardInterrupt:
        raise KeyboardInterrupt

    except:
        #print >> sys.stderr, "HTTP exception"
        pass

    else:
        html = reply.read()

    if html:
        if lastURL == True:
            return (html, reply.url)
        else:
            return html

    return False
