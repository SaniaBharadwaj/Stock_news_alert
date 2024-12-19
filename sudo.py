# while True:
#     schedule.run_pending()
#     time.sleep(60)


def get_stock_news(stock_sym):
    url = f"https://newsapi.org/v2/everything?q={stock_sym}&from=2024-10-25&sortBy=popularity&apiKey={NEWS_API_KEY}"

    response = requests.get(url)
    
    if response.status_code !=200:
        print(f'Error fetching news for {stock_sym}: {response.json()}')
        return
    news_data = response.json()
    if news_data['status'] == 'ok':
        articles = news_data["articles"]

        if articles:
            article = articles[0]
            titl = article.get('title','No title available')
            author = article.get('author', 'Unknown author')
            source = article.get('source', {}).get('name',"Unknown source")
            date_pub = article.get('publishedAt', 'Unknown date')

            if date_pub != "Unknown date":
                date_pub = datetime.fromisoformat(date_pub[:-1]).strftime('%Y-%m-%d %H:%M:%S')

                print(f"\n---{stock_sym}---")

                print(f"Title : {titl}")
                print(f"Author : {author}")
                print(f"Date published : {date_pub}")
                print(f"Source : {source}")

                print(f"URL{article.get('url', 'No URL available')}")
                print("-------------------------------------------------------------------------------------------------")

            else:
                print(f"No popular news found for {stock_sym}.")

        else:
            print(f"Failed to fetch news")

for stock in stocks:
    get_stock_news(stock)

