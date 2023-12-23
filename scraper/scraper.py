from .parser import parse_table
from playwright.sync_api import sync_playwright, TimeoutError
from bs4 import BeautifulSoup

from .renfe_data import RenfeData

"""
import logging

if not os.path.exists('logs'):
    os.makedirs('logs')

logfile = datetime.now().strftime('scraper_%H_%M_%d_%m_%Y.log')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(f'logs/{logfile}', mode='w')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s]: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
"""

RENFE_HOME = "https://www.renfe.com/es/es"
RENFE_SEARCH_URL = "https://venta.renfe.com/vol/search.do"


# Selectors for https://venta.renfe.com/vol/search.do
IDA_TABLE_SELECTOR = "#listaTrenesTBodyIda > tr"
VUELTA_LINK_SELECTOR = 'a[title="Trenes Trayecto Vuelta"]'
VUELTA_TABLE_SELECTOR = "#listaTrenesTBodyVuelta > tr"


class RenfeScraper:
    """
    Scraper for the Renfe website. It uses Selenium to interact with the page.

    The steps that the scraper follows are:
    1. Go to the Renfe home page
    2. Search for the origin and destination stations
    3. Search for the departure and return dates

    This part could be looped until the tickets are found
        4. Wait for the results page to load
        5. Parse the results page
        6. Filter the results according to the given filter

    """

    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.train_data = []
        self.renfe_data = None

    def __repr__(self):
        data = ""
        for train in self.train_data:
            data += "\nTrain:\n"
            for k, v in train.items():
                data += f"\t{k}: {v}\n"
        return f"RenfeScraper({data})"

    def find_trains(self, renfe_data: RenfeData):
        print("Searching for trains...")
        self.renfe_data = renfe_data
        page = self.page
        page.goto(RENFE_HOME)
        # brute forcing the search through hidden inputs
        page.get_by_title("Buscar billete").evaluate(
            "button => button.removeAttribute('disabled')")
        page.locator("#destination").click()
        for k, v in renfe_data.get_post_data().items():
            page.evaluate('''object => {
                const element = document.querySelector(object.selector);
                if (element) {
                    element.value = object.value;
                }
            }''', {"selector": f'[name="{k}"]', "value": v})
        page.click("text=Buscar billete")
        page.wait_for_url("https://venta.renfe.com/vol/search.do**")
        self.page = page

    def get_results(self):
        if not self.page.url.startswith(RENFE_SEARCH_URL):
            self.find_trains(self.renfe_data)
        page = self.page
        # load both train tables
        try:
            page.wait_for_selector(IDA_TABLE_SELECTOR, timeout=10000)
        except TimeoutError:
            print("No trains found for the query")
            print(self.renfe_data)
            return []
        if not self.renfe_data.oneway:
            buttons = page.locator(VUELTA_LINK_SELECTOR).all()
            for button in buttons:
                if button.is_visible():
                    button.click(force=True)
                    page.wait_for_selector(VUELTA_TABLE_SELECTOR)
            # get the train tables
        self._get_train_data(page.content())
        return self.train_data

    def _get_train_data(self, page_content):
        soup = BeautifulSoup(page_content, 'html.parser')
        tbody_ida = soup.find("tbody", id="listaTrenesTBodyIda")
        tbody_vuelta = soup.find("tbody", id="listaTrenesTBodyVuelta")
        ida_trains = tbody_ida.find_all("tr", class_="trayectoRow")
        vuelta_trains = tbody_vuelta.find_all("tr", class_="trayectoRow")
        ida_data = parse_table(ida_trains, "ida")
        vuelta_data = parse_table(vuelta_trains, "vuelta")
        self.train_data = ida_data + vuelta_data

    def wait_and_refresh(self, seconds):
        print(f"Waiting {seconds} seconds...")
        self.page.wait_for_timeout(seconds * 1000)
        self.page.reload()

    def stop(self):
        self.browser.close()
        self.playwright.stop()
