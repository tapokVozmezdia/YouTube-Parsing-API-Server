import requests
import psycopg2

import misc
import parsing
import db_handler
import datetime

class Crawler:
    def __init__(self, independent_launch : bool = True) -> None:
        self._update_requests_num(on_launch=True)

        self.def_reg = 'RU'
        self.def_lim = 5

        self._independent_launch = independent_launch

    def __del__(self) ->None:
        self._update_requests_num(on_del=True)

    # THIS FUNCTION IS ONLY TO BE USED BY CRAWLER!!!
    def _update_requests_num(self, on_launch : bool = False, 
        on_del : bool = False, on_check : bool = False) -> int:
        try:
            f = open('stats.stats', mode='r+')
        except:
            f = open('stats.stats', mode='w+')
            f.write("\
                date 0\
                active_crawlers 0\
                requests_made 0\
            ")
        new_content = ""

        request_flag = False
        request_num = -1

        boot_flag = (on_del or on_launch)

        for line in f:
            params = line.split(' ')

            if (len(params) != 2 and len(params) != 0):
                misc.throw_exception('stats reading failure')

            if (params[0] == 'date'):
                if (datetime.datetime.today().strftime('%Y-%m-%d') != params[1][:-1]):
                    params[1] = str(datetime.datetime.today().strftime('%Y-%m-%d')) + '\n'
                    request_flag = True

            if (params[0] == 'requests_made'):
                if (on_check):
                    request_num = int(params[1][:-1])
                elif (not request_flag and not boot_flag):
                    params[1] = f'{str(int(params[1]) + 1) + '\n'}'
                    request_num = int(params[1][:-1])
                elif (request_flag):
                    params[1] = '1\n'
                    request_num = int(params[1][:-1])
                else:
                    request_num = int(params[1][:-1])

            if (params[0] == 'active_crawlers' and on_launch == True):
                print("YOOOOOOOOOOOOOOOOOOO")
                if (int(params[1][:-1]) != 0):
                    misc.throw_exception('trying to launch a second crawler')
                else:
                    params[1] = '1\n'

            if (params[0] == 'active_crawlers' and on_del == True):
                if (int(params[1][:-1]) != 1):
                    misc.throw_exception('crawler closing failure')
                else:
                    params[1] = '0\n'   
            
            n_line = params[0] + ' ' + params[1]
            new_content += n_line 

        f.close()

        f = open('stats.stats', mode='w+')
        f.write(new_content)
        f.close()

        if (request_num == -1):
            misc.throw_exception('stats reading error')

        return request_num

    def _get_parsing_details(self):
        try:
            f = open('config.config', mode='r+')
        except:
            f = open('config.config', mode='w+')
            f.write("\
                region RU\
                search_limit 5\
            ")
        new_content = ""

        for line in f:
            params = line.split(' ')

            if (len(params) != 2 or len(params) != 0):
                misc.throw_exception('config reading failure')

            if (params[0] == 'region'):
                self.def_reg = params[1][:-1]
            if (params[1] == 'search_limit'):
                self.def_lim = params[1][:-1]

            new_content += line 

        f.close()

        f = open('config.config', mode='w+')
        f.write(new_content)
        f.close()

    def start_session(self) -> None:
        self.params = {
            'dbname' : 'practic_5', 
            'user' : 'postgres', 
            'password' : 'postgres', 
            'host' : 'localhost'
        }
        self.handler = db_handler.DB_handler(params=self.params)

    def end_session(self) -> None:
        self.handler.close_connection()

    def parse_chart_for_country(self, country : str = 'RU', max_results : int = 5,
        min_views : int = -1, max_views : int = 2**100) -> dict:

        if (self._independent_launch):
            country = self.def_reg
            max_results = self.def_lim

        if (self._update_requests_num(on_check=True) >= 5000):
            misc.throw_exception('request limit exceeded')

        parsed_data = parsing.request_chart(country_code=country, max_results=max_results)
        self._update_requests_num(on_launch=False, on_del=False)

        videos = parsed_data[0]
        channels = parsed_data[1]
        

        to_return_vids = []

        videos_added = 0
        channels_added = 0

        for i in range(0, len(channels)):
            channel = parsing.extract_data_from_channel_resource(channels[i], country)
            if (not self.handler.check_if_channel_exists(channel['channel_id'])):
                channels_added += 1
            self.handler.process_channel(channel=channel)

        for i in range(0, len(videos)):
            video = parsing.extract_data_from_video_resource(videos[i], from_chart=True)
            if (not self.handler.check_if_video_exists(video['video_id'])):
                videos_added += 1
            if (int(video['view_count']) < min_views or int(video['view_count']) > max_views):
                continue
            
            self.handler.process_video(video=video)

            video_cpy = video.copy()
            video_cpy.pop('channel_id')
            video_cpy['channel'] = self.handler.get_channels_from_base([str(video['channel_id'])])[0]
            to_return_vids.append(video_cpy)

        return {
            "videos" : to_return_vids,
            "search" : {
                "videos_parsed" : len(videos),
                "channels_parsed" : len(channels),
                "videos_added" : videos_added,
                "channels_added" : channels_added
            }
        }