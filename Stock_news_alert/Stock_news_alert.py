import sys
import os
import threading
import requests
import schedule
import keyboard
from colorama import Fore

import time
import subprocess
from datetime import datetime, timedelta
from win10toast import ToastNotifier 
# from plyer import notification

stocks = ["SAREGAMA", "ZOMATO", "GTL Infrastructure","Ratan Tata"]

#Use Api key
NEWS_API_KEY = "Pehle NEWS API SE API KEY GENERATE KAR BEY , DEVELOPER LOG PADHWO NAHI BHULIYO"

notified_arti = {}

auto_fetch_event = threading.Event()

theme = 'light'

def main():
    news_initial()
    auto_thread = threading.Thread(target=auto_fetch,daemon=True)
    auto_thread.start()
    
    while True:
        time.sleep(1)
        try:
            print_menu()
            choice_ = input(Fore.CYAN +  "Choose an Option: " + Fore.RESET).strip()
            if choice_ == '1':
                add_stock()
            elif choice_ == '2':
                remove_stock()
            elif choice_ =='3':
                toggle_theme()
            elif choice_ == "4":
                track_all()
            elif choice_ == '5':
                print("Exiting...")
                break
            # elif not choice_:
            #     print("Invalid choice try again.")
            else:
                auto_thread.start()
                if keyboard.is_pressed('enter'):
                    print_menu()
                    auto_fetch_event.set()
                    time.sleep(1)
                    auto_fetch()

        except:
            clear_articles()
            print(Fore.LIGHTCYAN_EX + "                                               Dozo..                                      ")

        auto_fetch_event.clear()

def send_notification(stock_name, article_title):
    toster = ToastNotifier()
    try:
        # notification.notify(title = f"New article for {stock_name}", message = f"{article_title}",app_name = 'Stock Tracking', timeout= 15)
        toster.show_toast(title = f"new article for {stock_name}", msg = f"{article_title}", duration= 15)


    except:
        print("Error in running Win10Toaster can't use notification")
    task_schedule() 

def task_schedule():
    task_name = "StockNewsTracker"
    try:
        subprocess.run(f"schtasks /run /tn {task_name}", shell=True, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Failed to trigger task: {e}")

def print_menu():
    print(Fore.LIGHTYELLOW_EX + "\n                                          ---Stock News Tracker---" + Fore.RESET)

    print(Fore.YELLOW + "1.Add a new stock")
    print("2.remove a new stock")
    print("3.Toggle Light/Dark Mode")
    print("4.Check for News Updates")
    print("5.Exit" + Fore.RESET)
    print('\n')
    # print("Current theme:", "Dark" if theme == 'dark' else "light")
    print(Fore.LIGHTCYAN_EX + " Tracked stocks: ".join(stocks) + Fore.RESET)
    print("\n")

#Choices

def add_stock():
    stock = input("Enter the stock symbol to add:").strip().upper()

    if stock not in stocks:
        stocks.append(stock)
        print(f"Added {stock} to the tracking list.")

def remove_stock():
    stock = input("Enter the stock symbol to remove:").strip().upper()

    if stock in stocks:
        stocks.remove(stock)
        print(f"Removed {stock} from the tracking list.")

    else:
        print(f"{stock} is not in the list.")

os.system("color 0B")

def toggle_theme():
    while True:
        try:
            # choice = input("\n     DARK OR BLUE? \n")
            print("\n Here's comes the theme choice: FOR DARK = background()text() and VICE VERSA \n")
            print("\n 0 = black 1 = blue 2 = green 3 = aqua 4 = red 5 = purple 6 = yellow 7 = white 8 = gray 9 = light blue ,\n A = Light Green B = Light Aqua C = Light red D = Light Purple E = Light Yellow F = Bright White \n")
            color_combi = input("please select code to proceed! : ")
            os.system(f"color {color_combi}")
            break
            # if choice == 'dark':
            #     os.system(color_combi)
            # elif choice == 'light':
            #     os.system(color_combi)
        except:
            break

    clear_articles()

    #Functionalities
def fetch_news_from_all_sources(stock_sym,time_range):

    for stock in stock_sym:
        url = f"https://newsapi.org/v2/everything?q={stock}&language=en&sortBy=popularity&apiKey={NEWS_API_KEY}"
        response = requests.get(url)

        news_data = response.json()
        if response.status_code !=200:
            print(Fore.LIGHTRED_EX + f"Error fetching news for {stock}: {response.status_code} -\n \n{news_data['message']}" + Fore.RESET)
            texty = "\n             YOU HAVE EXCEED THE LIMIT OF 100 API CALLS PER DAY, DO YOU EVEN HAVE MONEY TO BUY PREMINUM!?"
            print(Fore.RED + texty + Fore.RESET)
            return
           
        if news_data['status'] == 'ok' and 'articles' in news_data:
            articles = news_data['articles']
            print(Fore.CYAN + f"\nFound {len(articles)} new articles for {stock}:" + Fore.RESET)
            new_arti = False

            currentTime = datetime.now()

            for article in articles:
                arti_date = article.get('publishedAt', 'None')
                arti_date = datetime.strptime(article['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")

                # if arti_date:
                #     arti_date = datetime.fromisoformat(arti_date[:-1])

                time_diff = currentTime - arti_date
                # print(arti_date)
                # print(time_diff)
                if time_diff <= timedelta(hours = time_range):
                    
                    article_id = article.get('url','')

                    if article_id not in notified_arti:
                        notified_arti[article_id] = True

                        new_arti = True

                        titlee = article.get('title','No title available')
                        author = article.get('author','Unknown author')
                        source = article.get('source', {}).get('name', 'Unknown source')
                        descr = article.get('description', 'No description available')
                        content = article.get('content','No content available')
                        date_pub = arti_date.strftime("%Y-%m-%d %H:%M:%S")

                        url = article.get('url', 'No URL available')

                        display_article(stocks,titlee,author,source,date_pub,descr,content,url)

                        send_notification(stock , titlee)
                            
                       
        try:
            if not new_arti:

                print(Fore.LIGHTWHITE_EX + f"No new articles for {stock} in the last {time_range} hours.\n" + Fore.RESET)

            else:
                print(f"All updated news within {time_range} hours {stock}")
        except:
            print('Failed to fetech news , please try again later..')

#AUTO FETCHING        
def auto_fetch():
    while True:
        auto_fetch_event.wait(timeout=10)
        if not auto_fetch_event.is_set():
            print(Fore.LIGHTYELLOW_EX + "\n                                 Auto Checking for new articles, please wait..." + Fore.RESET)
            news_priodic()
            time.sleep(3600)

def news_initial():
    print(Fore.LIGHTYELLOW_EX + "         ********************************ALL UPDATED NEWS FOR LAST 24 HOURS**************************************" + Fore.RESET)
    fetch_news_from_all_sources(stocks,48)
    
def news_priodic():
    fetch_news_from_all_sources(stocks,2)

#HTML
def display_article(stock_sym,title,author,source,date_pub,descr,content,url):

    for stock in stock_sym:
        # headers = {"User-Agent" : "Mozilla/5.0"}
        header = f"\n---{stock}---"
        details = f"Title : {title}\nAuthor : {author}\nPubilshed : {date_pub}\nSource : {source}\nDescription : {descr}\nContent : {content}\nURL : {url}"
        seperator = Fore.GREEN + "-----------------------------------------------------------------------------------------" + Fore.RESET

        print(header)
        print("\n")
        print(details)
        print(seperator)

#CONDITIONS
def clear_articles():
    os.system('cls')
    print(Fore.LIGHTGREEN_EX + "Previous articles cleared." + Fore.RESET)

#START
def  track_all():
    global notified_arti
    notified_arti = {}
    print(Fore.LIGHTCYAN_EX + "\nChecking for updates from all sources..." + Fore.RESET)
    fetch_news_from_all_sources(stocks,2)

# schedule.every(1).minute.do(track_all, NEWS_API_KEY)

if __name__ == "__main__":
    main()
    task_schedule()

