"""Search and download anime on anime1.me"""

import os
import sys
import re
import concurrent.futures
from urllib.parse import unquote
import requests
from bs4 import BeautifulSoup
from PyInquirer import prompt
# FIXME: Use pip published version of Halo when #155 is merged
# https://github.com/manrajgrover/halo/pull/155
from halo import Halo

# Custom exception types
class Error(Exception):
    """Base class for other exceptions"""
    pass

class EmptySearchResultError(Error):
    """Raised when search result is empty in search_animes_on_anime1()"""
    pass

class NoVideoFoundError(Error):
    """Raised when search result is empty in download_video()"""
    pass

class VideoStreamConnectionError(Error):
    """Raised when video stream connection isn't returning status code 200 in download_video()"""
    pass

def main():
    """Main entry function that display questions to guide user through the download journey"""
    print('== 歡迎使用 Anime1.me 下載器 ==\n')

    answer1 = prompt([{
        'type': 'input',
        'name': 'keyword',
        'message': '請輸入搜尋關鍵字（例如：刀劍神域）',
        'validate': lambda value: value != '' or '請輸入搜尋關鍵字！'
    }])

    anime_list = search_anime(answer1['keyword'])
    category_list = get_unique_categories(anime_list)

    answer2 = prompt([{
        'type': 'list',
        'name': 'category',
        'message': '你想下載哪一套動畫？',
        'choices': category_list
    }])

    answer3 = prompt([{
        'type': 'checkbox',
        'name': 'episode',
        'message': '請選擇要下載的集數',
        'choices': [
            { 'name': anime['title'] } for anime in anime_list \
                if anime['category'] == answer2['category']
        ],
        # Below line is not working due to issue #171 in PyInquirer
        # https://github.com/CITGuru/PyInquirer/issues/171
        # FIXME: Consider switching to python-inquirer when python-inquirer's issue #115 is resolved
        # 'validate': lambda value: len(value) > 0 or '請選擇最少一個選項！'
    }])

    # Create video directory for saving downloaded videos
    current_directory = os.getcwd()
    video_directory = os.path.join(current_directory, r'video', answer2['category'])

    if not os.path.exists(video_directory):
        os.makedirs(video_directory)

    # Start download
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(
            download_video,
            [anime for anime in anime_list if anime['title'] in answer3['episode']]
        )

    print('\n== 所有下載已經完成，多謝使用 Anime1.me 下載器 ==')

def search_anime(keyword):
    """Handler to retrieve search result on anime1.me"""
    spinner = Halo(text='搜尋中，請耐心等候⋯⋯', spinner='dots')
    animes = []

    try:
        spinner.start()

        # Loop through all pages of search result
        search_result = None

        while True:
            search_url = search_result['previous_page_url'] \
                if search_result else 'https://anime1.me/?s=' + keyword
            search_result_html = requests.get(search_url).text
            search_result = extract_search_results(search_result_html)
            animes += search_result['animes_info']

            if not search_result['previous_page_url']:
                break

        spinner.stop()

        # Exit if there is no search result
        if not animes:
            raise EmptySearchResultError

        spinner.succeed('搜尋完成！')

    except EmptySearchResultError:
        spinner.fail('抱歉，您輸入的關鍵字找不到任何東西！')
        sys.exit(0)
    except BaseException as error:
        spinner.fail(f'抱歉，搜尋過程中出現了未知錯誤 (除錯訊息：{error=}, {type(error)=})')
        raise

    return animes

def extract_search_results(html):
    """Extract anime list from html"""
    animes_info = []

    soup = BeautifulSoup(html, 'html.parser')
    search_result = soup.find(id='content').find_all('article')

    if not search_result:
        return {
            'previous_page_url': None,
            'animes_info': []
        }

    # Loop through each search result item to get anime information
    for anime in search_result:
        anime_info = anime.find('header').find('h2').find('a')
        anime_title = anime_info.text
        anime_url = anime_info.attrs['href']

        anime_category_info = anime.find('footer').find('span', { 'class': 'cat-links' })
        anime_category = anime_category_info.find('a').text \
            if anime_category_info is not None else None

        if anime_title is not None and anime_url is not None:
            # filter for standalone anime links
            valid_anime_url_pattern = re.compile(r'^https:\/\/anime1\.me\/\d+$')
            if valid_anime_url_pattern.search(anime_url):
                animes_info.append({
                    'title': anime_title,
                    'url': anime_url,
                    'category': anime_category
                })

    pagination = soup.find('div', {'class': 'nav-previous'})

    return {
        'previous_page_url': pagination.find('a').attrs['href'] if pagination is not None else None,
        'animes_info': animes_info
    }

def get_unique_categories(anime_list):
    """Traverse within result returned from search_anime() to get unique category names"""
    category_list = []

    for anime in anime_list:
        if anime['category'] not in category_list:
            category_list.append(anime['category'])

    return category_list

def download_video(anime_info):
    """Retrieve player url and save the video file to disk storage"""
    spinner = Halo(text=f'{anime_info["title"]}: 開始下載⋯⋯', spinner='dots')

    try:
        spinner.start()

        # Get player link from video info page
        video_detail_html = requests.get(anime_info['url']).text
        soup = BeautifulSoup(video_detail_html, 'html.parser')
        play_button = soup.find('button', { 'class': 'loadvideo' })
        player_url = play_button.attrs['data-src'] if play_button is not None else None

        # Exit if no player link is found
        if not player_url:
            raise NoVideoFoundError

        player_html = requests.get(player_url).text
        player_request_body = re.findall(r'x\.send\(\'d=(.+)\'\)', player_html)

        # Exit if no player data found
        if not player_request_body:
            raise NoVideoFoundError

        # Initialize request client for storing cookies
        client = requests.session()
        player_data = client.post(
            'https://v.anime1.me/api',
            data={ 'd': unquote(player_request_body[0], 'utf-8') }
        ).json()

        # Exit for unexpected API response
        if not player_data['l']:
            raise NoVideoFoundError

        # Get video stream
        video_stream = client.get('https:' + player_data['l'], stream=True)

        if video_stream.status_code != 200:
            raise NoVideoFoundError

        # Save video stream to video directory
        file_name = (player_data['l'].split('/'))[-1]
        file_path = os.path.join(current_directory, r'video', anime_info["category"], file_name)
        file_size_in_bytes= int(video_stream.headers.get('content-length', 0))

        with open(file_path, 'wb') as file:
            block_size = 1024
            downloaded_byte = 0

            for data in video_stream.iter_content(block_size):
                downloaded_byte += len(data)
                progress_percentage = int((downloaded_byte / file_size_in_bytes) * 100)
                spinner.text = f'{anime_info["title"]}: 正在下載（進度：{progress_percentage}%）'
                file.write(data)

        spinner.succeed(f'{anime_info["title"]}: 下載完成')
    except NoVideoFoundError:
        spinner.fail(f'{anime_info["title"]}: 找不到影片地址，略過下載')
    except VideoStreamConnectionError:
        spinner.fail(f'{anime_info["title"]}: 無法加載影片，請稍後重試')
    except KeyboardInterrupt:
        spinner.fail('退出程式，取消所有下載')
        sys.exit(0)
    except BaseException as error:
        spinner.fail(f'{anime_info["title"]}: 下載過程中出現了未知錯誤，請稍後重試 (除錯訊息：{error=}, {type(error)=})')

if __name__ == '__main__':
    main()
