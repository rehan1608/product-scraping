import requests
from bs4 import BeautifulSoup
import csv

# Scrape data from multiple pages of product listings
def scrape_products(url, num_pages):
    base_url = url.split('/dp')[0]
    products = []
    for i in range(1, num_pages+1):
        page_num = i + 1
        page_url = f"{base_url}&page={page_num}"
        
        # Check if the page_url starts with a valid scheme
        if not page_url.startswith('https://'):
            page_url = 'https://' + page_url.lstrip('/')
        response = requests.get(page_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        results = soup.find_all('div', {'data-component-type': 's-search-result'})
        for r in results:
            product = {}
            # Get product URL
            url = r.find('a', {'class': 'a-link-normal s-no-outline'})['href']
            product['URL'] = 'https://www.amazon.in' + url
            # Get product name
            product['Name'] = r.find('span', {'class': 'a-size-medium a-color-base a-text-normal'}).text.strip()
            # Get product price
            price = r.find('span', {'class': 'a-price-whole'})
            if price:
                product['Price'] = price.text.strip()
            else:
                product['Price'] = ''
            # Get product rating
            rating = r.find('span', {'class': 'a-icon-alt'})
            if rating:
                product['Rating'] = rating.text.split()[0]
            else:
                product['Rating'] = ''
            # Get number of reviews
            num_reviews = r.find('span', {'class': 'a-size-base'})
            if num_reviews:
                product['Number of reviews'] = num_reviews.text.strip()
            else:
                product['Number of reviews'] = ''
            products.append(product)
    return products

# Scrape data from product detail pages
def scrape_product_details(products):
    for p in products:
        response = requests.get(p['URL'])

        soup = BeautifulSoup(response.content, 'html.parser')

        # Get ASIN
        asin = soup.find('input', {'id': 'ASIN'})
        if asin is not None:
            p['ASIN'] = asin['value']
        else:
            p['ASIN'] = ''
        
        # Get product description
        description = soup.find('div', {'id': 'productDescription'})
        if description:
            p['Description'] = description.text.strip()
        else:
            p['Description'] = ''
        # Get manufacturer
        manufacturer = soup.find('a', {'id': 'bylineInfo'})
        if manufacturer:
            p['Manufacturer'] = manufacturer.text.strip()
        else:
            p['Manufacturer'] = ''
    return products

# Export data to CSV file
def export_to_csv(products):
    with open('amazon_products.csv', mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['URL', 'Name', 'Price', 'Rating', 'Number of reviews', 'ASIN', 'Description', 'Manufacturer']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for p in products:
            writer.writerow(p)

# Main function
def main():
    url = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1'
    num_pages = 50
    products = scrape_products(url, num_pages)
    products = scrape_product_details(products)
    export_to_csv(products)

if __name__ == '__main__':
    main()
