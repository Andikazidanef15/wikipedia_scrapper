import time
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WikipediaScrapper:
    def __init__(self, proxy_server:str=''):
        # Configure Chrome options to use the proxy server
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        if proxy_server != '':
            chrome_options.add_argument(f"--proxy-server={proxy_server}")

        # Path to your ChromeDriver
        service = Service('browser/chromedriver.exe')

        # Define driver object
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # Create logger
        self.logger = logging.getLogger(__name__)
    
    def get_phrase_information(self, phrase:str, save_metadata:bool=True):
        self.logger.info(f'Get {phrase} phrase information from Wikipedia')

        # Replace space with + sign
        search_text = phrase.replace(' ', '+')
        
        # Get to the link with limit search set to 500
        self.driver.get(f'https://en.wikipedia.org/w/index.php?title=Special:Search&limit=500&offset=0&ns0=1&search={search_text}')

        # Get page list
        page_list = self.driver.find_elements(by = By.XPATH, value = '//*[@id="mw-content-text"]/div[2]/div[4]/ul/li/div/div[2]/div[1]/a')

        # Get title and link from page list
        title_list = [page.get_attribute('title') for page in page_list]
        link_list = [page.get_attribute('href') for page in page_list]

        # Get content
        content_list = self.driver.find_elements(by = By.XPATH, value = '//*[@id="mw-content-text"]/div[2]/div[4]/ul/li/div/div[2]/div[2]')
        content_list = [content.get_attribute('innerText') for content in content_list]

        # Get created at date
        created_at = self.driver.find_elements(by = By.XPATH, value = '//*[@id="mw-content-text"]/div[2]/div[4]/ul/li/div/div[2]/div[3]')
        created_at = [text.get_attribute('innerText').split(' - ')[1] for text in created_at]

        # Create metadata
        phrase_metadata = [
            {
                'title':title_list[i],
                'link':link_list[i],
                'content':content_list[i],
                'created_at':created_at[i]
            }
            for i in range(len(page_list))
        ]

        # Save metadata
        if save_metadata:
            # Get current datetime
            current_date = datetime.now()
            date_format = current_date.strftime('%Y_%m_%d_%H_%M_%S')
            file_format = phrase.replace(' ','_').lower()
            self.save_metadata(phrase_metadata, f'{file_format}_{date_format}.json')
    
    def get_page_information(self, link_list, result_list:list=[], visited_link_list:list=[]):
        try:
            for link in link_list:
                # Check if link already in the visited link list
                if link in visited_link_list:
                    self.logger.info(f'Skipping {link} as this link is already scrapped')
                    continue
                else:
                    visited_link_list.append(link)

                # Go to the wikipedia
                self.logger.info(f"Get {link.split('/')[-1]} information from Wikipedia")
                time.sleep(2)
                self.driver.get(link)

                # Get title
                # //*[@id="firstHeading"]/i
                title = self.driver.find_element(by = By.XPATH, value = '//*[@id="firstHeading"]').get_attribute("innerText")

                # Get content
                content = self.driver.find_element(by = By.XPATH, value = '//*[@id="mw-content-text"]/div[1]').text

                # Click View History
                try:
                    self.driver.find_element(by = By.XPATH, value = '//*[@id="ca-history"]/a').click()

                    # Sort by oldest update
                    try:
                        self.driver.find_element(by = By.XPATH, value = '//*[@id="mw-content-text"]/div[3]/a[1]').click()

                        # Get created at information
                        created_at = self.driver.find_element(by = By.XPATH, value = '//*[@id="pagehistory"]/ul[1]/li/a').text
                    except:
                        # Get created_date from the last record
                        created_at = self.driver.find_elements(by = By.XPATH, value = '//*[@id="pagehistory"]/ul/li/a')[-1]

                    # Go back to the page
                    self.driver.find_element(by = By.XPATH, value = '//*[@id="ca-nstab-main"]/a').click()
                except:
                    self.logger.info(f'No creation date information since the page is not written')
                    created_at = ''

                # Get reference links
                reference_link_list_object = self.driver.find_elements(by = By.XPATH, value = '//*[@id="mw-content-text"]/div[1]/div/ul/li/a')
                reference_link_list = [link.get_attribute('href') for link in reference_link_list_object]

                # Store the result in dictionary
                scrape_result = {
                    'title': title,
                    'content': content,
                    'see_also': reference_link_list,
                    'created_at': created_at,
                }

                result_list.append(scrape_result)

                # Loop
                ref_link_result = self.get_page_information(reference_link_list, result_list, visited_link_list)
                result_list.extend(ref_link_result)

            return result_list

        except KeyboardInterrupt as e:
            self.logger.info('Keyboard interrupted, saving current metadata')
        
        except Exception as e:
            self.logger.info(f'Error occurred: {e}')

        finally:
            # Save metadata
            filename = visited_link_list[0].split('/')[-1].lower()
            self.save_metadata(result_list, f'{filename}.json')
    
    def save_metadata(self, file:list, file_path:str):
        self.logger.info(f'Save metadata into JSON file')
        # Save metadata
        with open(f'{file_path}', 'w') as fout:
            json.dump(file, fout)
    
    def exit_browser(self):
        # Close browser session
        self.driver.quit()