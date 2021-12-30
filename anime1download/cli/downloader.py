"""Search and download anime on anime1.me"""

import os
import sys
import concurrent.futures
from PyInquirer import prompt
# FIXME: Use pip published version of Halo when #155 is merged
# https://github.com/manrajgrover/halo/pull/155
from halo import Halo
from cli.exceptions import (
    EmptySearchResultError, NoVideoFoundError, VideoStreamConnectionError
)
from cli.scraper import get_search_result, get_video_stream

def start():
    """Main entry function that display questions to guide user through the download journey"""
    print('== 歡迎使用 Anime1.me 下載器 ==\n')

    answer1 = prompt([{
        'type': 'input',
        'name': 'keyword',
        'message': '請輸入搜尋關鍵字（例如：刀劍神域）',
        'validate': lambda value: value != '' or '請輸入搜尋關鍵字！'
    }])

    anime_list = search_anime(answer1['keyword'])
    category_list = list({category for category in [anime['category'] for anime in anime_list]})

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
    video_directory = os.path.join(
        os.getcwd(),
        os.environ.get('VIDEO_DIRECTORY'),
        answer2['category']
    )

    if not os.path.exists(video_directory):
        os.makedirs(video_directory)

    # Start download
    max_parallel_download = int(os.environ.get('MAX_PARALLEL_DOWNLOAD'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel_download) as executor:
        executor.map(
            download_video,
            [anime for anime in anime_list if anime['title'] in answer3['episode']]
        )

    print('\n== 所有下載已經完成，多謝使用 Anime1.me 下載器 ==')

def search_anime(keyword):
    """Handler to retrieve search result on anime1.me"""
    spinner = Halo(text='搜尋中，請耐心等候⋯⋯', spinner='dots')

    try:
        spinner.start()
        animes = get_search_result(keyword)
        spinner.stop()

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

def download_video(anime_info):
    """Retrieve player url and save the video file to disk storage"""
    spinner = Halo(text=f'{anime_info["title"]}: 開始下載⋯⋯', spinner='dots')

    try:
        spinner.start()

        video_stream_info = get_video_stream(anime_info['url'])

        if not video_stream_info:
            raise NoVideoFoundError

        # Save video stream to video directory
        file_path = os.path.join(
            os.getcwd(),
            os.environ.get('VIDEO_DIRECTORY'),
            anime_info["category"],
            video_stream_info['file_name']
        )

        with open(file_path, 'wb') as file:
            block_size = 1024
            downloaded_byte = 0

            for data in video_stream_info['stream'].iter_content(block_size):
                downloaded_byte += len(data)
                progress_percentage = (downloaded_byte / video_stream_info['file_size_in_bytes']) * 100
                spinner.text = f'{anime_info["title"]}: 正在下載（進度：{int(progress_percentage)}%）'
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
