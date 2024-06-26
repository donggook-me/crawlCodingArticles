import csv;
import googleapiclient.discovery
import googleapiclient.errors
from datetime import datetime, timedelta


# 유튜브 크롤링은, 자체 제공하는 api 를 활용합니다.
def get_youtube_contents(search_term, api_key):
    api_service_name = "youtube"
    api_version = "v3"
    videos = []

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)

    # Get current time in UTC timezone
    current_time = datetime.utcnow()

    # Get the datetime for 1 week ago from the current time
    one_week_ago = current_time - timedelta(days=10)

    # Search for videos matching the search term and uploaded in the last week, excluding shorts and gaming videos
    page_token = ""
    for _ in range(10):  # execute the query 5 times
        request = youtube.search().list(
            part="snippet",
            type="video",
            q=search_term,
            order="date",
            publishedAfter=one_week_ago.isoformat() + "Z",
            maxResults=50,
            pageToken=page_token,
        )
        response = request.execute()

        for i, item in enumerate(response["items"]):
            video_id = item["id"]["videoId"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_title = item["snippet"]["title"]
            video_channel = item["snippet"]["channelTitle"]
            video_date = item["snippet"]["publishedAt"]
            video_context = item["snippet"]["description"]
            
            # 유튜브 데이터 크롤링시, 코딩, 개발 관련시, 특정 게임과 관련된 영상들, 또는 특정 학원 광고 등의
            # 데이터를 제거하기 위한 포함시키지 않을 키워드들입니다.
            
            keywords_to_exclude = ["아이온", "개발자노트", "던파", "마크", "대규모 패치", 
                                   "패치", "업데이트",  "로벅스",  "게임개발자",  "마인크래프트", 
                                   "카지노", " Live", "컴퓨터학원", "테런" "텔레그램",  
                                   "마인크래프트", "버그", "개발자 노트", "스트리트 파이터", "코딩학원", 
                                   "테마주", "주식", "국비지원", "아카데미",  "#shorts", "live", 
                                   "로블록스", "테일즈런너", "테일즈러너" "테런", "코인"]
            if any(keyword.lower() in video_title for keyword in keywords_to_exclude):
                continue
            
            
            videos.append({
                "video_id" : video_id,
                "video_url": video_url,
                "video_title": video_title,
                "video_channel": video_channel,
                "video_date": video_date,
                "video_context": video_context,
            })

        # Get the next page token to retrieve the next page of results
        page_token = response.get("nextPageToken")
        if not page_token:
            break  # no more results

    return videos

if __name__ == '__main__':
    api_key = "YOUR_API_KEY"
    search_list = ["개발자", "프론트엔드", "백엔드", "비전공자 코딩", "코딩테스트"]
    video_list = []
    content_index = 0

    # Get the current date and format it
    current_date = datetime.now().strftime("%Y%m%d")
    filename = f"contents_youtube_{current_date}.csv"

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['index', 'used', 'title', 'channel', 'date', 'url', 'context', 'keyword']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for keyword in search_list:
            videos = get_youtube_contents(keyword, api_key, content_index)
            video_list.extend(videos)

        
        video_id_list = []
        
        # 나온 결과의 순서를 뒤집어줍니다.
        sorted_video_list = sorted(video_list, key=lambda x: x['video_date'], reverse=True)

        
        # csv 데이터 생성 후, used 라벨을 관리하여, 추후 딥러닝에 활용할 수 있도록 합니다.

        for i, video in enumerate(video_list):
            if video['video_id'] in video_id_list:
                continue
            writer.writerow({
                'index': i,
                'used' : 0,
                'title': video['video_title'],
                'channel': video['video_channel'],
                'date': video['video_date'][:10],
                'url': video['video_url'],
                'context': video['video_context'],
                'keyword': keyword
            })
            video_id_list.append(video['video_id'])
