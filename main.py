from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# Press Shift+F10 to execute
def find_product_urls(product_type_page):
    urls = []
    product_cards = product_type_page.find_all(attrs={"class": "kib-product-card__content"})
    for element in product_cards:
        url = element.find("a")["href"]
        if url not in urls and "ms.tagdelivery" not in url:
            urls.append(url)
    return urls


def find_page_urls(product_type_page):
    urls = []
    pagination_items = product_type_page.find_all(attrs={"class": "kib-pagination-new__list-item"})
    last_pagination_item = pagination_items[-1]
    num_pages = last_pagination_item.text

    if int(num_pages) > 1:
        last_page_url = "https://www.chewy.com" + last_pagination_item.find("a")["href"]
        urls.append(last_page_url)
        for i in range(int(num_pages) - 1, 1, -1):
            url = last_page_url.replace("p" + num_pages, "p" + str(i))
            if url not in urls:
                urls.append(url)
    return urls


STARTING_URL = "https://www.chewy.com/b/freeze-dried-dehydrated-food-11737"

options = Options()
options.headless = True
options.add_argument("--remote-debugging-port=9222")  #
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_experimental_option('extensionLoadTimeout', 60000)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(STARTING_URL)

try:
    content = driver.page_source
    soup = BeautifulSoup(content, 'html.parser')

    page_urls = find_page_urls(soup)

    product_urls = find_product_urls(soup)

    for page_url in page_urls:
        driver.get(page_url)
        content = driver.page_source
        soup = BeautifulSoup(content, 'html.parser')
        product_urls.extend(find_product_urls(soup))

    product_urls_total = len(product_urls)
    product_urls_processed = 0
    for product_url in product_urls:
        product_urls_processed = product_urls_processed + 1
        driver.get(product_url)
        # TODO: add option urls functionality
        content = driver.page_source
        soup = BeautifulSoup(content, 'html.parser')
        product_name_element = soup.find(attrs={"data-testid": "product-title"})
        if product_name_element is not None:
            brand_name_element = product_name_element.find(attrs={"data-testid": "manufacture-name"})
            product_name = product_name_element.find(attrs={"data-testid": "product-title-heading"}).text.strip()
            if brand_name_element is not None:
                brand_name = brand_name_element.find("a").text.strip()
                print(brand_name)
                product_name = product_name.replace(brand_name, "").strip()
            print(product_name)
            price = soup.find(attrs={"data-testid": "advertised-price"}).text.replace("Chewy Price", "").strip()
            print(price)
            print()
    print("Total products processed: " + str(product_urls_processed))

except exceptions.StaleElementReferenceException as e:
    print(f">> {type(e).__name__}: {e.args}")
except exceptions.NoSuchElementException as e:
    print(f">> {type(e).__name__}: {e.args}")
except exceptions.TimeoutException as e:
    print(f">> {type(e).__name__}: {e.args}")
except exceptions.SessionNotCreatedException as e:
    print(f">> {type(e).__name__}: {e.args}")
except exceptions.WebDriverException as e:
    print(f">> {type(e).__name__}: {e.args}")
except Exception as e:
    print(f">> {type(e).__name__} line {e.__traceback__.tb_lineno} of {__file__}: {e.args}")
except:
    print(f">> General Exception: {STARTING_URL}")

driver.quit()  # closing the browser
