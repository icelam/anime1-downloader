"""Search and download anime on anime1.me"""

import os
import sys
import logging
import traceback
import concurrent.futures
import configparser
from PyInquirer import prompt
# FIXME: Use pip published version of Halo when #155 is merged
# https://github.com/manrajgrover/halo/pull/155
from halo import Halo
from cli.exceptions import (
    ConfigFileNotFoundError, EmptySearchResultError, NoVideoFoundError, VideoStreamConnectionError
)
from cli.scraper import get_search_result, get_video_stream
from cli.constants import CLI_VERSION

# Logging configuration
logging.basicConfig(
    filename='anime1download.log',
    format='[%(asctime)s]\t%(levelname)s\t%(message)s',
    datefmt='%d/%b/%Y:%H:%M:%S %z',
    level=logging.INFO,
    encoding='utf8'
)

# Load configurations
try:
    config_path = os.path.join(os.getcwd(), 'config.ini')

    if not os.path.exists(config_path):
        raise ConfigFileNotFoundError(os.getcwd())

    config = configparser.ConfigParser()
    config.read(config_path)
    logging.info('已載入 config.ini: %s', dict(config.items("CLI")))
except ConfigFileNotFoundError as application_load_error:
    logging.error(application_load_error)
    print(f'\033[91m✖\033[0m {application_load_error}')
    sys.exit(0)
except Exception as application_load_error: # pylint: disable=broad-except
    load_error_traceback_string = '\\n'.join(traceback.format_exc().splitlines()) # pylint: disable=invalid-name
    logging.error(
        '無法啟動程式 (除錯訊息：error=%s, type(error)=%s, traceback=%s)',
        application_load_error,
        type(application_load_error),
        load_error_traceback_string
    )
    print(
        '\033[91m✖\033[0m 無法啟動程式 ' +
        f'(除錯訊息：error={application_load_error}, ' +
        f'ftype(error)={type(application_load_error)}, ' +
        f'traceback={load_error_traceback_string})'
    )
    sys.exit(0)

def start():
    """Main entry function that display questions to guide user through the download journey"""
    print(f'== 歡迎使用 Anime1.me 下載器 v{CLI_VERSION} ==\n')

    answer1 = prompt([{
        'type': 'input',
        'name': 'keyword',
        'message': '請輸入搜尋關鍵字（例如：刀劍神域）',
        'validate': lambda value: value != '' or '請輸入搜尋關鍵字！'
    }])

    if not answer1:
        logging.info('使用者取消輸入搜尋關鍵字')
        sys.exit(0)

    logging.info('開始搜尋與「%s」相關的動畫', answer1["keyword"])

    anime_list = search_anime(answer1['keyword'])
    category_list = list({anime['category'] for anime in anime_list})

    logging.info('完成搜尋與「%s」相關的動畫: %s', answer1["keyword"], anime_list)

    answer2 = prompt([{
        'type': 'list',
        'name': 'category',
        'message': '你想下載哪一套動畫？',
        'choices': category_list
    }])

    if not answer2:
        logging.info('使用者取消選擇要下載的動畫')
        sys.exit(0)

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
        # FIXME: Consider switching to python-inquirer when python-inquirer's issue #171 is resolved
        # 'validate': lambda value: len(value) > 0 or '請選擇最少一個選項！'
    }])

    if not answer3:
        logging.info('使用者取消選擇要下載的集數')
        sys.exit(0)

    selected_episode = [anime for anime in anime_list if anime['title'] in answer3['episode']]

    logging.info('開始下載動畫「%s」: %s', answer2["category"], selected_episode)

    # Create video directory for saving downloaded videos
    video_directory = os.path.join(
        os.getcwd(),
        config.get('CLI', 'VIDEO_DIRECTORY'),
        answer2['category']
    )

    if not os.path.exists(video_directory):
        logging.info('路徑 %s 不存在，開始創建', video_directory)
        os.makedirs(video_directory)

    # Start download
    max_parallel_download = int(config.get('CLI', 'MAX_PARALLEL_DOWNLOAD'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel_download) as executor:
        executor.map(
            download_video,
            selected_episode
        )

    print('\n== 所有下載已經完成，多謝使用 Anime1.me 下載器 ==')
    logging.info('所有下載已經完成')

def search_anime(keyword):
    """Handler to retrieve search result on anime1.me"""

    spinner = Halo(text='搜尋中，請耐心等候⋯⋯', spinner='dots')

    try:
        spinner.start()
        animes = get_search_result(keyword)
        spinner.stop()

        if not animes:
            raise EmptySearchResultError(keyword)

        spinner.succeed('搜尋完成！')

        return animes
    except EmptySearchResultError as error:
        spinner.fail('抱歉，您輸入的關鍵字找不到任何東西！')
        logging.warning(error)
        sys.exit(0)
    except Exception as error: # pylint: disable=broad-except
        spinner.fail(f'抱歉，搜尋過程中出現了未知錯誤 (除錯訊息：{error=}, {type(error)=})')
        traceback_string = '\\n'.join(traceback.format_exc().splitlines())
        logging.error(
            '搜尋過程中出現了未知錯誤 (除錯訊息：error=%s, type(error)=%s, traceback=%s)',
            error,
            type(error),
            traceback_string
        )
        sys.exit(1)

def download_video(anime_info):
    """Retrieve player url and save the video file to disk storage"""
    spinner = Halo(text=f'{anime_info["title"]}: 開始下載⋯⋯', spinner='dots')

    try:
        spinner.start()

        video_stream_info = get_video_stream(anime_info['url'])

        if not video_stream_info['stream']:
            raise NoVideoFoundError(video_stream_info)

        if video_stream_info['stream'].status_code != 200:
            raise VideoStreamConnectionError(video_stream_info)

        # Save video stream to video directory
        file_path = os.path.join(
            os.getcwd(),
            config.get('CLI', 'VIDEO_DIRECTORY'),
            anime_info["category"],
            video_stream_info['file_name']
        )

        with open(file_path, 'wb') as file:
            block_size = 1024
            downloaded_byte = 0

            for data in video_stream_info['stream'].iter_content(block_size):
                downloaded_byte += len(data)
                progress = (downloaded_byte / video_stream_info['file_size_in_bytes']) * 100
                spinner.text = f'{anime_info["title"]}: 正在下載（進度：{int(progress)}%）'
                file.write(data)

        spinner.succeed(f'{anime_info["title"]}: 下載完成')
    except NoVideoFoundError as error:
        spinner.fail(f'{anime_info["title"]}: 找不到影片地址，略過下載')
        logging.error(error)
    except VideoStreamConnectionError as error:
        spinner.fail(f'{anime_info["title"]}: 無法加載影片，請稍後重試')
        logging.error(error)
    except KeyboardInterrupt:
        spinner.fail('退出程式，取消所有下載')
        logging.info(error)
        sys.exit(0)
    except Exception as error: # pylint: disable=broad-except
        spinner.fail(f'{anime_info["title"]}: 下載過程中出現了未知錯誤，請稍後重試 (除錯訊息：{error=}, {type(error)=})')
        traceback_string = '\\n'.join(traceback.format_exc().splitlines())
        logging.error(
            '下載過程中出現了未知錯誤 (除錯訊息：error=%s, type(error)=%s, traceback=%s)',
            error,
            type(error),
            traceback_string
        )
