from datetime import datetime, date
import csv, os


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

# 브런치 데이터는 여러 키워드 들에서 추출한 것이므로, 순서가 섞여있고, 이를 년도-월-날짜 각각 순서대로
# 정렬하는 코드입니다. day 의 경우, "-분전", "-시간전" 부분을 고려해야 합니다. 
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


def writeToCsv(filename, sorted_contents):
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(filename,  'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['index', 'used', 'title', 'author', 'publish_time', 'href', 'context', 'search']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, content in enumerate(sorted_contents):
            writer.writerow({
                'index': i+1,
                'used' : 0,
                'title': content['title'],
                'context': content['context'],
                'publish_time': content['publish_time'],
                'author': content['author'],
                'href': content['href'],
                'search': content['search']
            })



