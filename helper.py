from bs4 import BeautifulSoup
import httpx
import threading

BASE_URL = 'https://expowest24.smallworldlabs.com'

GEOAPIFY_API = '8923fefc90c24aa1bbe6bb22b302d39b'

def start_threading(links, items, error_items):
    thread_list = []
    for link in links:
        thread = threading.Thread(target=send_requests, args=(link, items, error_items),)
        thread_list.append(thread)
        thread_list[-1].start()
    for thread in thread_list:
        thread.join()

def append_or_pass(item: dict, list_: list):
    if item is None:
        pass
    else:
        list_.append(item)

def save_link(page):
    soup = BeautifulSoup(page.content(), 'lxml')
    links = []
    for x in soup.select('a.generic-option-link'):
        if 'Booth' in x.get_text(strip=True):
            pass
        else:
            links.append(f"{BASE_URL}{x['href']}")
    print(f'{len(links)} Links saved')
    return links

def get_address(query):
    print(f'Address query: {query}')
    ADDRESS_URL = f'https://api.geoapify.com/v1/geocode/search?text={query}&lang=en&apiKey={GEOAPIFY_API}'
    resp = httpx.get(ADDRESS_URL)
    print(f'Address url: {ADDRESS_URL}')
    json_data = resp.json()
    try:
        city = json_data['features'][0]['properties']['city']
    except:
        city = None
    try:
        zipcode = json_data['features'][0]['properties']['postcode']
    except:
        zipcode = None
    try:
        area = json_data['features'][0]['properties']['district']
    except:
        area = None
    try:
        country = json_data['features'][0]['properties']['country']
    except:
        country = None
    return city, zipcode, area, country

def get_content(str_, soup):
    for x in soup.select('.row.small.no-gutters.mb-3'):
        if str_ in x.text:
            return x.get_text(" ", strip=True).replace(str_, '').strip()
    return None

def extract_data(soup):
    item = {}
    company_name = get_content('Name', soup)
    domain = get_content('Website', soup)
    address = get_content('Address', soup)
    organisation_member_list = ', '.join([x.get_text(strip=True) for x in soup.select('a[data-object-type="Organizations_Member"]')])
    booth = soup.select_one('.generic-option').get_text(strip=True).replace('Booth #', '').strip()
    brand = get_content('Brand', soup)
    city, zipcode, area, country = get_address(address)
    item = {
        'Company name': company_name,
        'Brand name': brand,
        'Booth number': booth,
        'Domain': domain,
        'Address': address,
        'Headquarters City': city,
        'Headquarters Country': country,
        'Headquarters zipcode': zipcode,
        'Area': area,
        'Organization member list': organisation_member_list
    }
    return item

def send_requests(link, items, error_items):
    error_item = None
    item = None
    print(f'Link: {link}')
    for i in range(10):
        try:
            resp = httpx.get(link)
            soup = BeautifulSoup(resp.text, 'lxml')
            item  = extract_data(soup)
            break
        except Exception as e:
            if i == 9:
                error_item = {
                    'url': link,
                    'error': e
                }
            print(f'Retrying.... : {e}')
            pass
    append_or_pass(item, items)
    append_or_pass(error_item, error_items)


