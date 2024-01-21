from bs4 import BeautifulSoup
from selenium import webdriver

# Press Shift+F10 to execute
URL = "https://www.chewy.com/brands/fussie-cat-6778"

driver = webdriver.Chrome()
driver.get(URL)

content = driver.page_source
soup = BeautifulSoup(content, 'html.parser')

product_cards = soup.find_all(attrs={"class": "kib-product-card__content"})

product_urls = []
for element in product_cards:
    print(element)

    url = element.find("a")["href"]
    if url not in product_urls:
        product_urls.append(url)

for product_url in product_urls:
    print(product_url)

driver.quit()  # closing the browser
