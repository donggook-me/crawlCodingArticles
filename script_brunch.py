from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import time
import threading
import csv
from datetime import datetime, date

# brunch 사이트 크롤링 코드
def get_brunch(keyword, lock, all_contents):
    url = "https://brunch.co.kr/search"

    driver = webdriver.Chrome()
    driver.get(url)

    search_input = driver.find_element(By.ID, 'txt_search')
    search_input.send_keys(keyword)
    search_input.send_keys(Keys.RETURN)  # Press Enter key to submit form
    
    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '.link_option'))
    )
    
    sort_button = driver.find_element(By.CSS_SELECTOR, 'a[data-type="recency"]')
    sort_button.click()
    
    WebDriverWait(driver, 15).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.list_article.list_common.list_animation li'))
    ) 
    sort_button = driver.find_element(By.CSS_SELECTOR, 'a[data-type="recency"]')
    sort_button.click()
        
    WebDriverWait(driver, 15).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.list_article.list_common.list_animation li'))
    ) 
    
    # 스크롤시, 콘텐츠 데이터 로딩을 위한 대기시간.
    time.sleep(1.5)
    
    # 아래 range count 를 통해, 몇번의 마우스 스크롤을 할 것인지 결정합니다.
    for _ in range(4):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)  # Wait for the page to load more content

    # Wait for the contents to load
    WebDriverWait(driver, 15).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.list_article.list_common.list_animation li'))
    )
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find the <ul> element containing the posts
    ul_element = soup.find('ul', class_='list_article list_common list_animation')
    # Find the individual post elements
    post_elements = ul_element.find_all('li', class_=['list_has_image animation_up_late','animation_up_late'])

    content_list = []

    for post in post_elements:
        title = post.find('strong', class_='tit_subject').get_text(strip=True)
        context = post.find('span', class_='article_content').get_text(strip=True)
        publish_time = post.find('span', class_='publish_time').get_text(strip=True)
        author = post.find('span', class_='txt_by').find_next_sibling('span').get_text(strip=True)
        href = "https://brunch.co.kr" + post.find('a', class_='link_post')['href']
        content_list.append({'search': keyword, 'title': title, 'context': context, 'publish_time': publish_time, 'author': author, 'href': href})


    # Close the driver
    driver.quit()

    with lock:
        all_contents.extend(content_list)
    
    print(f"finish {keyword} thread crawling job - count : {len(all_contents)}")
    
    return content_list

def main():
    search_list = ["개발자", "프론트엔드", "백엔드", "코딩", "코딩테스트", "소프트웨어"]
    # search_list = ["개발자", "프론트엔드", "백엔드"]
    content_index = 0
    all_contents = []  # List to store all contents
    # Performance timers
    start_time = time.time()
    thread_timers = {}
    
  # Create a lock for synchronizing access to future_contents
    lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit keyword queries to the executor and store the Future objects
        future_list = []
        for keyword in search_list:
            print(f"start thread {keyword} ")
            future = executor.submit(get_brunch, keyword, lock, all_contents)
            future_list.append(future)

    # Wait for all the futures to complete
    concurrent.futures.wait(future_list)
    
    for result in future_list:
        print(f"checking future list - {result}")

    # Calculate the overall program execution time
    program_execution_time = time.time() - start_time

    # Remove duplicate items based on href
    unique_contents = []
    seen_hrefs = set()

    for content in all_contents:
        href = content['href']
        if href not in seen_hrefs:
            seen_hrefs.add(href)
            unique_contents.append(content)

    # Define a mapping for English month names to month numbers
    month_mapping = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12'
    }

    # Function to convert the publish_time to a sortable date format
    def convert_publish_time(date_str):
        
        if len(date_str.split()) == 1:
            today = date.today()
            year = str(today.year)
            month = str(today.month).zfill(2)
            day = str(today.day).zfill(2)
            return [year, month, day]

        # Split the date string into day, month, and year
        month, day, year = date_str.split()

        # Convert the month name to the corresponding month number
        month_number = month_mapping.get(month)

        # Create a sortable date string in the format 'YYYY-MM-DD'
        return [year, month_number, day]

    # 브런치 데이터는 여러 키워드 들에서 추출한 것이므로, 순서가 섞여있고, 이를 년도-월-날짜 각각 순서대로
    # 정렬하는 코드입니다. day 의 경우, "-분전", "-시간전" 부분을 고려해야 합니다. 
    
    
    sorted_contents = sorted(unique_contents, key=lambda x: (
        convert_publish_time(x['publish_time'])[0],  # Accessing the year element
        convert_publish_time(x['publish_time'])[1],  # Accessing the month element
        convert_publish_time(x['publish_time'])[2]   # Accessing the day element
    ), reverse=True)

    # Get the current date and format it
    current_date = datetime.now().strftime("%Y%m%d")
    filename = f"contents_brunch_{current_date}.csv"

    # Write the sorted contents to a CSV file
    
    # csv 데이터 생성 후, used 라벨을 관리하여, 추후 딥러닝에 활용할 수 있도록 합니다.
    
    
    with open(filename,  'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['index', 'used', 'title', 'author', 'publish_time', 'href', 'context', 'search']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, content in enumerate(sorted_contents):
            writer.writerow({
                'index': content_index + (i+1),
                'used' : 0,
                'title': content['title'],
                'context': content['context'],
                'publish_time': content['publish_time'],
                'author': content['author'],
                'href': content['href'],
                'search': content['search']
            })
        content_index += len(sorted_contents)

    # Print performance results
    print(f"Overall Program Execution Time: {program_execution_time} seconds")
    for keyword, timer in thread_timers.items():
        print(f"Thread '{keyword}' Execution Time: {timer} seconds")

if __name__ == '__main__':
    main()
    
    
    


    
    
