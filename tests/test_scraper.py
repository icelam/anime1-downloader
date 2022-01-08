"""Unit tests for scraper functions"""

# pylint: disable=line-too-long

import os
from pathlib import Path
import unittest
import responses
from anime1download.cli.scraper import (
    get_search_result,
    extract_search_results,
    get_player_url,
    get_player_data,
    get_video_stream
)

# Retrive mock response to be use in test
def get_mock_response(file_name):
    """Get mock response from file"""
    file_path = os.path.join(
        os.getcwd(), 'tests', 'mocks', file_name
    )
    return Path(file_path).read_text(encoding='utf8')

search_result_mock_response = get_mock_response('search-result-single-page.html')
search_result_paginatated_mock_response_1 = get_mock_response('search-result-multiple-page-1.html')
search_result_paginatated_mock_response_2 = get_mock_response('search-result-multiple-page-2.html')
empty_search_result_mock_response = get_mock_response('search-result-empty.html')
season_detail_mock_response = get_mock_response('season-detail.html')
video1_detail_mock_response = get_mock_response(os.path.join('video1', 'video-detail.html'))
player1_mock_response = get_mock_response(os.path.join('video1', 'player.html'))
player1_api_mock_response = get_mock_response(os.path.join('video1', 'player-api.json'))
video2_detail_mock_response = get_mock_response(os.path.join('video2', 'video-detail.html'))
player2_mock_response = get_mock_response(os.path.join('video2', 'player.html'))
player_api_failed_response = get_mock_response(os.path.join('player-api-invalid-signature.json'))

class TestGetSearchResult(unittest.TestCase):
    """Test for get_search_result()"""
    def setUp(self):
        """Configure test and mock request response"""
        self.maxDiff = None

        responses.add(
            responses.GET,
            'https://anime1.me/?s=%E5%BA%8F%E5%88%97%E7%88%AD%E6%88%B0',
            body=search_result_mock_response,
            status=200
        )

        responses.add(
            responses.GET,
            'https://anime1.me/?s=ssss',
            body=search_result_paginatated_mock_response_1,
            status=200
        )

        responses.add(
            responses.GET,
            'https://anime1.me/page/2?s=ssss',
            body=search_result_paginatated_mock_response_2,
            status=200
        )

        responses.add(
            responses.GET,
            'https://anime1.me/?s=random_string',
            body=empty_search_result_mock_response,
            status=200
        )

    @responses.activate
    def test_get_search_result(self):
        """Test that it searches and returns list of animes without pagination"""
        result = get_search_result('序列爭戰')
        self.assertEqual(
            result,
            [
                {
                    'category': '刀劍神域劇場版 -序列爭戰-',
                    'title': '刀劍神域劇場版 -序列爭戰- [劇場版]',
                    'url': 'https://anime1.me/3205'
                }
            ]
        )

    @responses.activate
    def test_get_search_result_paginated(self):
        """Test that it searches and returns list of animes with pagination"""
        result = get_search_result('ssss')
        self.assertEqual(
            result,
            [
                {
                    "title": "SSSS.DYNAZENON [12]",
                    "url": "https://anime1.me/15372",
                    "category": "SSSS.DYNAZENON"
                },
                {
                    "title": "SSSS.DYNAZENON [11]",
                    "url": "https://anime1.me/15315",
                    "category": "SSSS.DYNAZENON"
                },
                {
                    "title": "SSSS.DYNAZENON [10]",
                    "url": "https://anime1.me/15262",
                    "category": "SSSS.DYNAZENON"
                },
                {
                    "title": "SSSS.DYNAZENON [09]",
                    "url": "https://anime1.me/15211",
                    "category": "SSSS.DYNAZENON"
                },
                {
                    "title": "SSSS.DYNAZENON [08]",
                    "url": "https://anime1.me/15151",
                    "category": "SSSS.DYNAZENON"
                },
                {
                    "title": "SSSS.DYNAZENON [07]",
                    "url": "https://anime1.me/15098",
                    "category": "SSSS.DYNAZENON"
                },
                {
                    "title": "SSSS.DYNAZENON [06]",
                    "url": "https://anime1.me/15047",
                    "category": "SSSS.DYNAZENON"
                },
                {
                    "title": "SSSS.DYNAZENON [05]",
                    "url": "https://anime1.me/14986",
                    "category": "SSSS.DYNAZENON"
                },
                {
                    "title": "SSSS.DYNAZENON [04]",
                    "url": "https://anime1.me/14937",
                    "category": "SSSS.DYNAZENON"
                },
                {
                    "title": "SSSS.DYNAZENON [03]",
                    "url": "https://anime1.me/14879",
                    "category": "SSSS.DYNAZENON"
                },
                {
                    "title": "SSSS.DYNAZENON [02]",
                    "url": "https://anime1.me/14813",
                    "category": "SSSS.DYNAZENON"
                },
                {
                    "title": "SSSS.DYNAZENON [01]",
                    "url": "https://anime1.me/14765",
                    "category": "SSSS.DYNAZENON"
                },
                {
                    "title": "SSSS.GRIDMAN [12]",
                    "url": "https://anime1.me/7849",
                    "category": "SSSS.GRIDMAN"
                },
                {
                    "title": "SSSS.GRIDMAN [11]",
                    "url": "https://anime1.me/7679",
                    "category": "SSSS.GRIDMAN"
                },
                {
                    "title": "SSSS.GRIDMAN [10]",
                    "url": "https://anime1.me/7591",
                    "category": "SSSS.GRIDMAN"
                },
                {
                    "title": "SSSS.GRIDMAN [09]",
                    "url": "https://anime1.me/7491",
                    "category": "SSSS.GRIDMAN"
                },
                {
                    "title": "SSSS.GRIDMAN [08]",
                    "url": "https://anime1.me/7421",
                    "category": "SSSS.GRIDMAN"
                },
                {
                    "title": "SSSS.GRIDMAN [07]",
                    "url": "https://anime1.me/7313",
                    "category": "SSSS.GRIDMAN"
                },
                {
                    "title": "SSSS.GRIDMAN [06]",
                    "url": "https://anime1.me/7228",
                    "category": "SSSS.GRIDMAN"
                },
                {
                    "title": "SSSS.GRIDMAN [05]",
                    "url": "https://anime1.me/7159",
                    "category": "SSSS.GRIDMAN"
                },
                {
                    "title": "SSSS.GRIDMAN [04]",
                    "url": "https://anime1.me/7086",
                    "category": "SSSS.GRIDMAN"
                },
                {
                    "title": "SSSS.GRIDMAN [03]",
                    "url": "https://anime1.me/6988",
                    "category": "SSSS.GRIDMAN"
                },
                {
                    "title": "SSSS.GRIDMAN [02]",
                    "url": "https://anime1.me/6873",
                    "category": "SSSS.GRIDMAN"
                },
                {
                    "title": "SSSS.GRIDMAN [01]",
                    "url": "https://anime1.me/6767",
                    "category": "SSSS.GRIDMAN"
                }
            ]
        )

    @responses.activate
    def test_get_search_result_without_match(self):
        """Test that it can handles search results without match"""
        result = get_search_result('random_string')
        self.assertEqual(
            result,
            []
        )

class TestExtractSearchResult(unittest.TestCase):
    """Test for extract_search_results()"""
    def setUp(self):
        """Configure test"""
        self.maxDiff = None

    def test_extract_search_results(self):
        """Test that it return anime list from HTML string"""
        result = extract_search_results(search_result_mock_response)
        self.assertEqual(
            result,
            {
                'previous_page_url': None,
                'animes_info': [
                    {
                        'category': '刀劍神域劇場版 -序列爭戰-',
                        'title': '刀劍神域劇場版 -序列爭戰- [劇場版]',
                        'url': 'https://anime1.me/3205'
                    }
                ]
            }
        )
    def test_extract_search_results_paginated(self):
        """Test that it return anime list and pagination info from HTML string"""
        result = extract_search_results(search_result_paginatated_mock_response_1)
        self.assertEqual(
            result,
            {
                'previous_page_url': 'https://anime1.me/page/2?s=ssss',
                'animes_info': [
                    {
                        "title": "SSSS.DYNAZENON [12]",
                        "url": "https://anime1.me/15372",
                        "category": "SSSS.DYNAZENON"
                    },
                    {
                        "title": "SSSS.DYNAZENON [11]",
                        "url": "https://anime1.me/15315",
                        "category": "SSSS.DYNAZENON"
                    },
                    {
                        "title": "SSSS.DYNAZENON [10]",
                        "url": "https://anime1.me/15262",
                        "category": "SSSS.DYNAZENON"
                    },
                    {
                        "title": "SSSS.DYNAZENON [09]",
                        "url": "https://anime1.me/15211",
                        "category": "SSSS.DYNAZENON"
                    },
                    {
                        "title": "SSSS.DYNAZENON [08]",
                        "url": "https://anime1.me/15151",
                        "category": "SSSS.DYNAZENON"
                    },
                    {
                        "title": "SSSS.DYNAZENON [07]",
                        "url": "https://anime1.me/15098",
                        "category": "SSSS.DYNAZENON"
                    },
                    {
                        "title": "SSSS.DYNAZENON [06]",
                        "url": "https://anime1.me/15047",
                        "category": "SSSS.DYNAZENON"
                    },
                    {
                        "title": "SSSS.DYNAZENON [05]",
                        "url": "https://anime1.me/14986",
                        "category": "SSSS.DYNAZENON"
                    },
                    {
                        "title": "SSSS.DYNAZENON [04]",
                        "url": "https://anime1.me/14937",
                        "category": "SSSS.DYNAZENON"
                    },
                    {
                        "title": "SSSS.DYNAZENON [03]",
                        "url": "https://anime1.me/14879",
                        "category": "SSSS.DYNAZENON"
                    },
                    {
                        "title": "SSSS.DYNAZENON [02]",
                        "url": "https://anime1.me/14813",
                        "category": "SSSS.DYNAZENON"
                    },
                    {
                        "title": "SSSS.DYNAZENON [01]",
                        "url": "https://anime1.me/14765",
                        "category": "SSSS.DYNAZENON"
                    },
                    {
                        "title": "SSSS.GRIDMAN [12]",
                        "url": "https://anime1.me/7849",
                        "category": "SSSS.GRIDMAN"
                    },
                    {
                        "title": "SSSS.GRIDMAN [11]",
                        "url": "https://anime1.me/7679",
                        "category": "SSSS.GRIDMAN"
                    }
                ]
            }
        )
    def test_extract_search_results_without_match(self):
        """Test that it can handles search results without match"""
        result = extract_search_results(empty_search_result_mock_response)
        self.assertEqual(result, { 'previous_page_url': None, 'animes_info': [] })

class TestGetPlayerUrl(unittest.TestCase):
    """Test for get_player_url()"""
    def setUp(self):
        """Configure test and mock request response"""
        responses.add(
            responses.GET,
            'https://anime1.me/6965',
            body=video1_detail_mock_response,
            status=200
        )

        responses.add(
            responses.GET,
            'https://anime1.me/2018%e5%b9%b4%e7%a7%8b%e5%ad%a3%e6%96%b0%e7%95%aa',
            body=season_detail_mock_response,
            status=200
        )

    @responses.activate
    def test_get_player_url(self):
        """Test that it returns player url if play button is found"""
        result = get_player_url('https://anime1.me/6965')
        self.assertEqual(result, 'https://v.anime1.me/watch?v=tS8VG')

    @responses.activate
    def test_get_player_url_without_play_button(self):
        """Test that it returns None for page without play button"""
        result = get_player_url('https://anime1.me/2018%e5%b9%b4%e7%a7%8b%e5%ad%a3%e6%96%b0%e7%95%aa')
        self.assertIsNone(result)

class TestGetPlayerData(unittest.TestCase):
    """Test for get_player_data()"""
    def setUp(self):
        """Configure test and mock request response"""
        responses.add(
            responses.GET,
            'https://v.anime1.me/watch?v=tS8VG',
            body=player1_mock_response,
            status=200
        )

        responses.add(
            responses.GET,
            'https://anime1.me/2018%e5%b9%b4%e7%a7%8b%e5%ad%a3%e6%96%b0%e7%95%aa',
            body=season_detail_mock_response,
            status=200
        )

    @responses.activate
    def test_get_player_data(self):
        """Test that it returns player url if play button is found"""
        result = get_player_data('https://v.anime1.me/watch?v=tS8VG')
        self.assertEqual(
            result,
            '{"c":"450","e":"1","t":1641037437,"p":0,"s":"70a6a7cffc009b1599de0009822b400c"}'
        )

    @responses.activate
    def test_get_player_data_exception_handling(self):
        """Test that it returns player url if play button is found"""
        result = get_player_url('https://anime1.me/2018%e5%b9%b4%e7%a7%8b%e5%ad%a3%e6%96%b0%e7%95%aa')
        self.assertIsNone(result)

class TestGetVideoStream(unittest.TestCase):
    """Test for get_video_stream()"""
    def setUp(self):
        """Configure test and mock request response"""
        # Video 1 mock
        responses.add(
            responses.GET,
            'https://anime1.me/6965',
            body=video1_detail_mock_response,
            status=200
        )

        responses.add(
            responses.GET,
            'https://v.anime1.me/watch?v=tS8VG',
            body=player1_mock_response,
            status=200
        )

        responses.add(
            responses.POST,
            'https://v.anime1.me/api',
            body=player1_api_mock_response,
            match=[
                responses.matchers.urlencoded_params_matcher({
                    'd': '{"c":"450","e":"1","t":1641037437,"p":0,"s":"70a6a7cffc009b1599de0009822b400c"}'
                })
            ],
            status=200
        )

        responses.add(
            responses.GET,
            'https://pekora.v.anime1.me/450/1.mp4',
            body=b'This is a mocked video.',
            status=200,
            auto_calculate_content_length=True
        )

        # Video 2 mock
        responses.add(
            responses.GET,
            'https://anime1.me/6966',
            body=video2_detail_mock_response,
            status=200
        )

        responses.add(
            responses.GET,
            'https://v.anime1.me/watch?v=_bBHU',
            body=player2_mock_response,
            status=200
        )

        responses.add(
            responses.POST,
            'https://v.anime1.me/api',
            body=player_api_failed_response,
            match=[
                responses.matchers.urlencoded_params_matcher({
                    'd': '{"c":"403","e":"3","t":1641042078,"p":0,"s":"b7818f6857e44d303e9f0f3b37e70194"}'
                })
            ],
            status=403
        )

        # Season detail page mock
        responses.add(
            responses.GET,
            'https://anime1.me/2018%e5%b9%b4%e7%a7%8b%e5%ad%a3%e6%96%b0%e7%95%aa',
            body=season_detail_mock_response,
            status=200
        )

    @responses.activate
    def test_get_video_stream(self):
        """Test that it returns video stream with file name and file size"""
        result = get_video_stream('https://anime1.me/6965')
        self.assertEqual(result['player_url'], 'https://v.anime1.me/watch?v=tS8VG')
        self.assertEqual(result['player_data'], '{"c":"450","e":"1","t":1641037437,"p":0,"s":"70a6a7cffc009b1599de0009822b400c"}')
        self.assertEqual(result['player_api_response']['l'], '//pekora.v.anime1.me/450/1.mp4')
        self.assertEqual(result['stream'].status_code, 200)
        self.assertEqual(result['file_name'], '1.mp4')
        self.assertEqual(result['file_size_in_bytes'], 23)

    @responses.activate
    def test_get_video_stream_invalid_video_signature(self):
        """Test that it return None when video signature is invalid"""
        result = get_video_stream('https://anime1.me/6966')
        self.assertEqual(result['player_url'], 'https://v.anime1.me/watch?v=_bBHU')
        self.assertEqual(result['player_data'], '{"c":"403","e":"3","t":1641042078,"p":0,"s":"b7818f6857e44d303e9f0f3b37e70194"}')
        self.assertEqual(result['player_api_response']['success'], False)
        self.assertEqual(result['player_api_response']['errors'], ['Signature invalid.'])
        self.assertEqual(result['stream'], None)
        self.assertEqual(result['file_name'], None)
        self.assertEqual(result['file_size_in_bytes'], None)

    @responses.activate
    def test_get_video_stream_invalid_video_detail_url(self):
        """Test that it return None when video detail url is invalid"""
        result = get_video_stream('https://anime1.me/2018%e5%b9%b4%e7%a7%8b%e5%ad%a3%e6%96%b0%e7%95%aa')
        self.assertEqual(result['player_url'], None)
        self.assertEqual(result['player_data'], None)
        self.assertEqual(result['player_api_response'], None)
        self.assertEqual(result['stream'], None)
        self.assertEqual(result['file_name'], None)
        self.assertEqual(result['file_size_in_bytes'], None)

if __name__ == '__main__':
    unittest.main()
