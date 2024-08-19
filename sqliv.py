# SQLiv v2.0
# Ghost (github.com/Hadesy2k)
# official.ghost@tuta.io

import argparse
from urllib.parse import urlparse  # Updated for Python 3

from src import std
from src import scanner
from src import reverseip
from src import serverinfo
from src.web import search
from src.crawler import Crawler

# search engine instance
bing = search.Bing()
google = search.Google()
yahoo = search.Yahoo()

# crawler instance
crawler = Crawler()

def singlescan(url):
    """Instance to scan a single targeted domain."""
    if urlparse(url).query != '':
        result = scanner.scan([url])
        if result:
            return result
        else:
            print("")  # Move carriage return to newline
            std.stdout("No SQL injection vulnerability found")
            option = std.stdin("Do you want to crawl and continue scanning? [Y/N]", ["Y", "N"], upper=True)

            if option == 'N':
                return False

    # Crawl and scan the links
    std.stdout(f"Going to crawl {url}")
    urls = crawler.crawl(url)

    if not urls:
        std.stdout("Found no suitable URLs to test SQLi")
        return False

    std.stdout(f"Found {len(urls)} URLs from crawling")
    vulnerables = scanner.scan(urls)

    if not vulnerables:
        std.stdout("No SQL injection vulnerability found")
        return False

    return vulnerables

def initparser():
    """Initialize parser arguments."""
    global parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", dest="dork", help="SQL injection dork", type=str, metavar="inurl:example")
    parser.add_argument("-e", dest="engine", help="Search engine [Bing, Google, and Yahoo]", type=str, metavar="bing, google, yahoo")
    parser.add_argument("-p", dest="page", help="Number of websites to look for in search engine", type=int, default=10, metavar="100")
    parser.add_argument("-t", dest="target", help="Scan target website", type=str, metavar="www.example.com")
    parser.add_argument('-r', dest="reverse", help="Reverse domain", action='store_true')
    parser.add_argument('-o', dest="output", help="Output result into JSON", type=str, metavar="result.json")
    parser.add_argument('-s', action='store_true', help="Output search even if there are no results")

if __name__ == "__main__":
    initparser()
    args = parser.parse_args()

    # Find random SQLi by dork
    if args.dork and args.engine:
        std.stdout("Searching for websites with given dork")

        # Get websites based on search engine
        if args.engine in ["bing", "google", "yahoo"]:
            websites = eval(args.engine).search(args.dork, args.page)
        else:
            std.stderr("Invalid search engine")
            exit(1)

        std.stdout(f"{len(websites)} websites found")

        vulnerables = scanner.scan(websites)

        if not vulnerables:
            if args.s:
                std.stdout("Saved as searches.txt")
                std.dump(websites, "searches.txt")
            exit(0)

        std.stdout("Scanning server information")

        vulnerableurls = [result[0] for result in vulnerables]
        table_data = serverinfo.check(vulnerableurls)
        # Add DB name to info
        for result, info in zip(vulnerables, table_data):
            info.insert(1, result[1])  # Database name

        std.fullprint(table_data)

    # Do reverse domain of given site
    elif args.target and args.reverse:
        std.stdout(f"Finding domains with the same server as {args.target}")
        domains = reverseip.reverseip(args.target)

        if not domains:
            std.stdout("No domain found with reversing IP")
            exit(0)

        std.stdout(f"Found {len(domains)} websites")

        # Ask whether the user wants to save domains
        std.stdout("Scanning multiple websites with crawling will take long")
        option = std.stdin("Do you want to save domains? [Y/N]", ["Y", "N"], upper=True)

        if option == 'Y':
            std.stdout("Saved as domains.txt")
            std.dump(domains, "domains.txt")

        # Ask whether the user wants to crawl one by one or exit
        option = std.stdin("Do you want to start crawling? [Y/N]", ["Y", "N"], upper=True)

        if option == 'N':
            exit(0)

        vulnerables = []
        for domain in domains:
            vulnerables_temp = singlescan(domain)
            if vulnerables_temp:
                vulnerables += vulnerables_temp

        std.stdout("Finished scanning all reverse domains")
        if not vulnerables:
            std.stdout("No vulnerable websites from reverse domains")
            exit(0)

        std.stdout("Scanning server information")

        vulnerableurls = [result[0] for result in vulnerables]
        table_data = serverinfo.check(vulnerableurls)
        # Add DB name to info
        for result, info in zip(vulnerables, table_data):
            info.insert(1, result[1])  # Database name

        std.fullprint(table_data)

    # Scan SQLi of given site
    elif args.target:
        vulnerables = singlescan(args.target)

        if not vulnerables:
            exit(0)

        std.stdout("Getting server info of domains can take a few mins")
        table_data = serverinfo.check([args.target])

        std.printserverinfo(table_data)
        print("")  # Give space between two tables
        std.normalprint(vulnerables)
        exit(0)

    # Print help message if no parameter is provided
    else:
        parser.print_help()

    # Dump result into JSON if specified
    if args.output:
        std.dumpjson(table_data, args.output)
        std.stdout(f"Dumped result into {args.output}")
