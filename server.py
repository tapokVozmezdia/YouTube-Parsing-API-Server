from flask import Flask, jsonify, request

import parsing
import db_handler
import crawlerbot
import misc

class API_server:

    def __init__(self) -> None:
        self.app = Flask('api')

        self.crawler = crawlerbot.Crawler(independent_launch=False)
        params = {
            'dbname' : 'practic_5', 
            'user' : 'postgres', 
            'password' : 'postgres', 
            'host' : 'localhost'
        }
        self._private_handler = db_handler.DB_handler(params=params)
        self._recently_parsed = dict()

        self.get_methods()
        
    def parse(self, region : str = "RU", resource_num : int = 5,
        min_views : int = -1, max_views : int = 2**100) -> None:

        if (len(region) != 2 or resource_num < 0):
            misc.throw_exception("bad parsing request")

        region = region.upper()
        
        self.crawler.start_session()
        self._recently_parsed = self.crawler.parse_chart_for_country(
            region, resource_num, 
            min_views=min_views, 
            max_views=max_views
        )
        self.crawler.end_session()

    def get_methods(self) -> None:
        @self.app.route('/api/v1/videos', methods=['GET'])
        def get_videos() -> None:
            args = request.args.to_dict()
            videos = []

            if (len(args) == 0):
                videos = self._private_handler.get_videos_from_base([])
                return jsonify({"videos": videos})
            
            if ('video_num' in args and len(args) == 1):
                videos = self._private_handler.get_videos_from_base([], limit=int(args['video_num']))
                return jsonify({"videos": videos})
            
            if ('channels' in args):
                if ('video_num' in args and len(args) == 2):
                    videos = self._private_handler.get_videos_from_channels(channels=str(args['channels']), limit=int(args['video_num']))
                if (len(args) == 1):
                    videos = self._private_handler.get_videos_from_channels(channels=str(args['channels']))
                return jsonify({"videos": videos})
            
            if ('regions' in args):
                if ('video_num' in args and len(args) == 2):
                    videos = self._private_handler.get_videos_from_regions(regions=str(args['regions']), limit=int(args['video_num']))
                if (len(args) == 1):
                    videos = self._private_handler.get_videos_from_regions(regions=str(args['regions']))
                return jsonify({"videos": videos})

        @self.app.route('/api/v1/videos/<string:video_id>', methods=['GET'])
        def get_video(video_id) -> None:
            videos = self._private_handler.get_videos_from_base([str(video_id)])
            return jsonify({"videos": videos})
        
        @self.app.route('/api/v1/channels', methods=['GET'])
        def get_channels() -> None:
            args = request.args.to_dict()
            channels = []

            if (len(args) == 0):
                channels = self._private_handler.get_channels_from_base([])
                return jsonify({"channels": channels})
            
            if ('channel_num' in args and len(args) == 1):
                channels = self._private_handler.get_channels_from_base([], limit=int(args['channel_num']))
                return jsonify({"channels": channels})
            
            if ('regions' in args):
                if ('channel_num' in args and len(args) == 2):
                    channels = self._private_handler.get_channels_from_regions(regions=str(args['regions']), limit=int(args['channel_num']))
                if (len(args) == 1):
                    channels = self._private_handler.get_channels_from_regions(regions=str(args['regions']))
                return jsonify({"channels": channels})
            
        @self.app.route('/api/v1/channels/<string:channel_id>', methods=['GET'])
        def get_channel(channel_id) -> None:
            channels = self._private_handler.get_channels_from_base([str(channel_id)])
            return jsonify({"channels": channels})
        
        @self.app.route('/api/v1/search', methods=['GET'])
        def search() -> None:
            args = request.args.to_dict()
            cntr = "RU"
            limit = 5
            inf = -1
            sup = 2**100

            if ("region" in args):
                cntr = str(args["region"])

            if ("video_num" in args):
                limit = int(args["video_num"])

            if ("min_views" in args):
                inf = int(args["min_views"])
            
            if ("max_views" in args):
                sup = int(args["max_views"])

            self.parse(region=cntr, resource_num=limit, min_views=inf, max_views=sup)
            resources = self._recently_parsed
            return jsonify({"resources": resources})

    def service_func(self) -> None:
        pass

    def run(self) -> None:
        self.app.run(debug=False)