"""Scraper functions for Anime1.me downloader"""

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote

def get_search_result(keyword):
    """Loop through all pages of search result on Anime1.me """
    animes = []
    search_result = None

    while True:
        search_url = search_result['previous_page_url'] \
            if search_result else 'https://anime1.me/?s=' + keyword
        search_result_html = requests.get(search_url).text
        search_result = extract_search_results(search_result_html)
        animes += search_result['animes_info']

        if not search_result['previous_page_url']:
            break

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

def get_player_url(video_detail_url):
    """Get player link from video detail page"""
    video_detail_html = requests.get(video_detail_url).text
    soup = BeautifulSoup(video_detail_html, 'html.parser')
    play_button = soup.find('button', { 'class': 'loadvideo' })
    return play_button.attrs['data-src'] if play_button is not None else None

def get_player_data(player_url):
    """Get player data from player"""
    player_html = requests.get(player_url).text
    data = re.findall(r'x\.send\(\'d=(.+)\'\)', player_html)
    return unquote(data[0], 'utf-8') if data else None

def get_video_stream(video_detail_url):
    player_url = get_player_url(video_detail_url)
    player_data = get_player_data(player_url) if player_url is not None else None

    if not player_data:
        return None

    # Initialize request client for storing cookies
    client = requests.session()
    video_file_info = client.post(
        'https://v.anime1.me/api',
        data={ 'd': player_data }
    ).json()

    if not 'l' in video_file_info.keys():
        return None

    # Get video stream
    video_stream = client.get('https:' + video_file_info['l'], stream=True)

    return {
        'stream': video_stream,
        'file_name': (video_file_info['l'].split('/'))[-1],
        'file_size_in_bytes': int(video_stream.headers.get('content-length', 0))
    } if video_stream.status_code == 200 else None
