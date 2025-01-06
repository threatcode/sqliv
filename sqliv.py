# SQLiv v2.1
# Ghost (github.com/Hadesy2k)
# official.ghost@tuta.io

import argparse
import sys
from urllib.parse import urlparse
from typing import List, Optional, Dict, Any

from src import std
from src import scanner
from src import reverseip
from src import serverinfo
from src.web import search
from src.crawler import Crawler


class SQLiv:
    def __init__(self):
        """Initialize search engine instances and crawler"""
        self.bing = search.Bing()
        self.google = search.Google()
        self.yahoo = search.Yahoo()
        self.crawler = Crawler()

    def singlescan(self, url: str) -> Optional[List[Dict[str, Any]]]:
        """
        Scan a single targeted domain for SQL injection vulnerabilities.
        
        Args:
            url: The URL to scan
            
        Returns:
            List of vulnerable URLs and their details if found, None otherwise
        """
        if urlparse(url).query:
            result = scanner.scan([url])
            if result:
                return result
            
            print("")  # Move carriage return to newline
            std.stdout("No SQL injection vulnerability found")
            if not std.stdin("Do you want to crawl and continue scanning? [Y/N]", ["Y", "N"], upper=True) == 'Y':
                return None

        # Crawl and scan the links
        std.stdout(f"Going to crawl {url}")
        urls = self.crawler.crawl(url)

        if not urls:
            std.stdout("Found no suitable URLs to test SQLi")
            return None

        std.stdout(f"Found {len(urls)} URLs from crawling")
        vulnerables = scanner.scan(urls)

        if not vulnerables:
            std.stdout("No SQL injection vulnerability found")
            return None

        return vulnerables

    def process_dork_scan(self, args: argparse.Namespace) -> None:
        """Handle scanning with dork search"""
        std.stdout("Searching for websites with given dork")

        engines = {
            "bing": self.bing,
            "google": self.google,
            "yahoo": self.yahoo
        }

        if args.engine not in engines:
            std.stderr("Invalid search engine")
            sys.exit(1)

        websites = engines[args.engine].search(args.dork, args.page)
        std.stdout(f"{len(websites)} websites found")

        vulnerables = scanner.scan(websites)

        if not vulnerables:
            if args.save_searches:
                std.stdout("Saved as searches.txt")
                std.dump(websites, "searches.txt")
            sys.exit(0)

        std.stdout("Scanning server information")
        self.process_vulnerables(vulnerables)

    def initparser(self) -> argparse.ArgumentParser:
        """Initialize and return argument parser"""
        parser = argparse.ArgumentParser(description='SQLiv - Massive SQL injection vulnerability scanner')
        parser.add_argument("-d", dest="dork", help="SQL injection dork", type=str, metavar="inurl:example")
        parser.add_argument("-e", dest="engine", help="Search engine [Bing, Google, Yahoo]", type=str, metavar="bing, google, yahoo")
        parser.add_argument("-p", dest="page", help="Number of websites to look for in search engine", type=int, default=10, metavar="100")
        parser.add_argument("-t", dest="target", help="Scan target website", type=str, metavar="www.example.com")
        parser.add_argument('-r', dest="reverse", help="Reverse domain lookup", action='store_true')
        parser.add_argument('-o', dest="output", help="Output result to JSON file", type=str, metavar="result.json")
        parser.add_argument('-s', dest="save_searches", help="Save search results even if no vulnerabilities found", action='store_true')
        return parser

    def process_reverse_lookup(self, args: argparse.Namespace) -> None:
        """Handle reverse domain lookup scanning"""
        std.stdout(f"Finding domains with same server as {args.target}")
        domains = reverseip.reverseip(args.target)

        if not domains:
            std.stdout("No domain found with reverse IP lookup")
            sys.exit(0)

        std.stdout(f"Found {len(domains)} websites")
        std.stdout("Scanning multiple websites with crawling will take long")

        if std.stdin("Do you want to save domains? [Y/N]", ["Y", "N"], upper=True) == 'Y':
            std.stdout("Saved as domains.txt")
            std.dump(domains, "domains.txt")

        if not std.stdin("Do you want to start crawling? [Y/N]", ["Y", "N"], upper=True) == 'Y':
            sys.exit(0)

        vulnerables = []
        for domain in domains:
            vulnerables_temp = self.singlescan(domain)
            if vulnerables_temp:
                vulnerables.extend(vulnerables_temp)

        std.stdout("Finished scanning all reverse domains")
        if not vulnerables:
            std.stdout("No vulnerable websites found from reverse domains")
            sys.exit(0)

        std.stdout("Scanning server information")
        self.process_vulnerables(vulnerables)

    def process_vulnerables(self, vulnerables: List) -> None:
        """Process and display vulnerable URLs"""
        vulnerableurls = [result[0] for result in vulnerables]
        table_data = serverinfo.check(vulnerableurls)
        
        # Add database name to info
        for result, info in zip(vulnerables, table_data):
            info.insert(1, result[1])

        std.fullprint(table_data)
        return table_data


def main():
    sqliv = SQLiv()
    parser = sqliv.initparser()
    args = parser.parse_args()

    if args.dork and args.engine:
        sqliv.process_dork_scan(args)
    elif args.target and args.reverse:
        sqliv.process_reverse_lookup(args)
    elif args.target:
        vulnerables = sqliv.singlescan(args.target)
        if not vulnerables:
            sys.exit(0)

        std.stdout("Getting server info of domains (this may take a few minutes)")
        table_data = serverinfo.check([args.target])

        std.printserverinfo(table_data)
        print("")  # Space between tables
        std.normalprint(vulnerables)
        sys.exit(0)
    else:
        parser.print_help()

    if args.output:
        std.dumpjson(table_data, args.output)
        std.stdout(f"Dumped result into {args.output}")


if __name__ == "__main__":
    main()
