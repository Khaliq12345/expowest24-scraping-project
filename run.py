from playwright.sync_api import sync_playwright
import helper
import pandas as pd

#constant
NEXT_PAGE = 'a.pager-right-next.pager-item.pager-right'
BASE_URL = "https://expowest24.smallworldlabs.com/exhibitors"
DATA_FOLDER = 'data'

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(BASE_URL, timeout=100000)
        print(page.title())
        while True:
            #links = helper.save_link(page)
            df = pd.read_excel('errors.xlsx')
            links = df['url']
            helper.start_threading(links, items, error_items)               
            if page.is_visible(NEXT_PAGE):
                page.click(NEXT_PAGE)
                page.wait_for_timeout(3000)
            else:
                print('No more new page')
                break
        browser.close()
    
if __name__ == '__main__':
    items = []
    error_items = []
    main()
    df = pd.DataFrame(items)
    df_error = pd.DataFrame(error_items)
    df.to_excel(f'{DATA_FOLDER}/expowest24_exhibitor.xlsx', index=False)
    df_error.to_excel(f'{DATA_FOLDER}/errors.xlsx', index=False)
    print('Done!')