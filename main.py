import logging
import argparse
from datetime import datetime
from concurrent_log_handler import ConcurrentRotatingFileHandler

from src.scrapper import WikipediaScrapper
from config.env import getenv

PROXY_URL = getenv('PROXY_URL', default='http://localhost:9919')

#setup logging to file
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d %B %Y %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        ConcurrentRotatingFileHandler(
            filename='./logs/WikipediaScrapper.log',
            mode='a',
            maxBytes=20 * 1024 * 1024,
            backupCount=3
        )
    ],
)
parser = argparse.ArgumentParser(description='Wikipedia scrapper for phrase search and page information')
parser.add_argument("--proxy_url", "-u", type=str, default=PROXY_URL, help='Proxy URL to connect with Wikipedia website')
parser.add_argument("--phrase", "-p", type=str, default='', help='Scrape search phrase result in Wikipedia search page')
parser.add_argument("--links", "-l", type=str, default='', help='Scrape page information including relevant link')

args = parser.parse_args()

def main():
    logger = logging.getLogger("Main")
    logger.info('*'*45 + ' START ' + '*'*45)

    start_main = datetime.now()
    exit_status = 0

    try:
        proxy_url = args.proxy_url
        phrase = args.phrase
        links = args.links.split(',')
        links = [link.strip() for link in links]
        
        if phrase != '':
            # Define wikipedia scrapper
            scrapper = WikipediaScrapper(proxy_url)

            # Collect data using scrapper
            scrapper.get_phrase_information(phrase)

            # Quit browser
            scrapper.exit_browser()
        
        if links != ['']:
            # Define wikipedia scrapper
            scrapper = WikipediaScrapper(proxy_url)

            # Collect data using scrapper
            scrapper.get_page_information(links)

            # Quit browser
            scrapper.exit_browser()
    
    except BaseException as e:
        exit_status = 1
        logger.exception(e)
        raise e

    finally:
        end_main = datetime.now()
        logger.info(f'Exited after {end_main - start_main} with status {exit_status}')
        logger.info('*'*45 + ' FINISH ' + '*'*45)

if __name__ == '__main__':
    main()