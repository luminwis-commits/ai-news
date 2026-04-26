import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 상수 정의
ZDNET_AI_URL = "https://zdnet.co.kr/news/?category=ai"
BASE_URL = "https://zdnet.co.kr"
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
NEWS_COUNT_LIMIT = 5

def fetchAiNews():
    """
    지디넷코리아 AI 섹션에서 최신 뉴스 5개를 가져옵니다.
    """
    try:
        response = requests.get(ZDNET_AI_URL)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        newsElements = soup.select('.newsPost')[:NEWS_COUNT_LIMIT]
        
        newsList = []
        for element in newsElements:
            titleElement = element.select_one('.assetText h3')
            linkElement = element.select_one('.assetText > a')
            
            if titleElement and linkElement:
                title = titleElement.get_text(strip=True)
                link = BASE_URL + linkElement['href']
                newsList.append({"title": title, "link": link})
                
        return newsList
    except Exception as e:
        print(f"뉴스 크롤링 중 에러 발생: {e}")
        return []

def formatSlackMessage(newsList):
    """
    뉴스 목록을 슬랙 메시지 블록 형식으로 변환합니다.
    """
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🤖 지디넷코리아 AI 최신 뉴스",
                "emoji": True
            }
        },
        {"type": "divider"}
    ]
    
    for news in newsList:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*<{news['link']}|{news['title']}>*"
            }
        })
        
    return {"blocks": blocks}

def sendToSlack(message):
    """
    슬랙 웹훅을 통해 메시지를 전송합니다.
    """
    if not SLACK_WEBHOOK_URL or SLACK_WEBHOOK_URL == "your_slack_webhook_url_here":
        print("에러: SLACK_WEBHOOK_URL이 설정되지 않았습니다. .env 파일을 확인하세요.")
        return

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=message)
        response.raise_for_status()
        print("슬랙 메시지 전송 성공!")
    except Exception as e:
        print(f"슬랙 전송 중 에러 발생: {e}")

def main():
    print("AI 뉴스 크롤링 시작...")
    newsList = fetchAiNews()
    
    if not newsList:
        print("가져온 뉴스가 없습니다.")
        return
        
    print(f"{len(newsList)}개의 뉴스를 찾았습니다.")
    for i, news in enumerate(newsList, 1):
        print(f"{i}. {news['title']}")
        
    slackMessage = formatSlackMessage(newsList)
    sendToSlack(slackMessage)

if __name__ == "__main__":
    main()
