import psycopg2
import misc

class DB_handler:
    def __init__(self, params : dict) -> None:
        if ('dbname' not in params 
            or 'user' not in params
            or 'password' not in params
            or 'host' not in params):
            misc.throw_exception('DB CONNECTION FAILED')

        self.connection = psycopg2.connect(
            dbname=params['dbname'], 
            user=params['user'], 
            password=params['password'], 
            host=params['host']
        )

        self.cursor = self.connection.cursor()
        print("=======\nDB CONNECTION SUCCESSFUL\n=======")

    def execute_query(self, query : str) -> None:
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except:
            misc.throw_exception("database query failed")

    def get_column_titles(self) -> list:
        titles = [desc[0] for desc in self.cursor.description]
        return titles
    
    def get_query_result(self) -> list:
        return self.cursor.fetchall()

    # check if video is stored in the database
    def check_if_video_exists(self, id : str) -> bool:
        query = 'SELECT * FROM videos\n'
        query += 'WHERE video_id = ' 
        query += ("'" + id + "'")

        self.execute_query(query=query)
        result = self.get_query_result()
        if (len(result) > 0):
            return True
        else:
            return False
        
    # check if channel is stored in the database
    def check_if_channel_exists(self, id : str) -> bool:
        query = 'SELECT * FROM channels\n'
        query += 'WHERE channel_id = ' 
        query += ("'" + id + "'")

        self.execute_query(query=query)
        result = self.get_query_result()
        if (len(result) > 0):
            return True
        else:
            return False

    # для каналов, извлеченных из бд
    def get_preprocessed_channels(self, channels : list):
        processed_channels = []
        for i in range(0, len(channels)):
            subject = channels[i]
            chn = {}
            chn['channel_id'] = str(subject[0])
            chn['subscriber_count'] = int(subject[1])
            chn['subscriber_count_hidden'] = bool(subject[2])
            chn['video_count'] = int(subject[3])
            chn['total_views'] = int(subject[4])
            chn['region'] = str(subject[5])
            processed_channels.append(chn)
        
        return processed_channels

    def get_channels_from_base(self, ids : list = [], limit : int = -1):
        def_lim = 5
        
        if (limit != -1 and limit >= 0):
            def_lim = limit

        if (len(ids) < 0):
            misc.throw_exception("DB HANDLER ERROR")

        if (len(ids) == 0):
            query = f"SELECT * FROM channels ORDER BY subscriber_count DESC\nLIMIT {def_lim};"
            self.execute_query(query=query)
            return self.get_preprocessed_channels(self.get_query_result())

        query = "SELECT * FROM channels WHERE\n"
        query += "channel_id IN ("
        j = 1
        for i in range(0, len(ids)):
            query += f"'{ids[i]}'"
            if (j != len(ids)):
                query += ", "
            j+=1
        query += f");"

        self.execute_query(query=query)
        return self.get_preprocessed_channels(self.get_query_result())
    
    def get_channels_from_regions(self, regions : str, limit : int = 5):
        if (len(regions) == 0):
            misc.throw_exception("DB HANDLER ERROR")

        ids = (regions.split(","))

        query = "SELECT * FROM channels WHERE region IN ("
        j = 1
        for i in range(0, len(ids)):
            query += f"'{ids[i]}'"
            if (j != len(ids)):
                query += ", "
            j+=1
        query += f") ORDER BY subscriber_count DESC\nLIMIT {limit};"

        self.execute_query(query=query)
        return self.get_preprocessed_channels(self.get_query_result())

    # для видео, извлеченных из бд
    def get_preprocessed_videos(self, videos : list):
        processed_videos = []
        for i in range(0, len(videos)):
            subject = videos[i]
            vid = {}
            vid['video_id'] = str(subject[0])
            vid['video_name'] = str(subject[1])
            vid['channel'] = dict()
            vid['view_count'] = str(subject[3])
            vid['like_count'] = str(subject[4])
            vid['dislike_count'] = str(subject[5])
            vid['like_ratio'] = str(subject[6])
            vid['comment_count'] = str(subject[7])

            vid['channel'] = self.get_channels_from_base([str(subject[2])])[0]

            processed_videos.append(vid)
        
        return processed_videos

    def get_videos_from_base(self, ids : list = [], limit : int = 5):
        if (len(ids) < 0):
            misc.throw_exception("DB HANDLER ERROR")

        if (len(ids) == 0):
            query = f"SELECT * FROM videos ORDER BY view_count DESC\nLIMIT {limit};"
            self.execute_query(query=query)
            return self.get_preprocessed_videos(self.get_query_result())

        query = "SELECT * FROM videos WHERE\n"
        query += "video_id IN ("
        j = 1
        for i in range(0, len(ids)):
            query += f"'{ids[i]}'"
            if (j != len(ids)):
                query += ", "
            j+=1
        query += ");"

        self.execute_query(query=query)
        return self.get_preprocessed_videos(self.get_query_result())
    
    def get_videos_from_channels(self, channels : str, limit : int = 5):
        if (len(channels) == 0):
            misc.throw_exception("DB HANDLER ERROR")

        ids = (channels.split(","))

        query = "SELECT * FROM videos WHERE\n"
        query += "channel_id IN ("
        j = 1
        for i in range(0, len(ids)):
            query += f"'{ids[i]}'"
            if (j != len(ids)):
                query += ", "
            j+=1
        query += f") ORDER BY view_count DESC\nLIMIT {limit};"

        self.execute_query(query=query)
        return self.get_preprocessed_videos(self.get_query_result())
    
    def get_videos_from_regions(self, regions : str, limit : int = 5):
        if (len(regions) == 0):
            misc.throw_exception("DB HANDLER ERROR")

        ids = (regions.split(","))

        query = "SELECT * FROM videos WHERE\n"
        query += "channel_id IN ("
        query += "SELECT channel_id FROM channels WHERE region IN ("
        j = 1
        for i in range(0, len(ids)):
            query += f"'{ids[i]}'"
            if (j != len(ids)):
                query += ", "
            j+=1
        query += ")"
        query += f") ORDER BY view_count DESC\nLIMIT {limit};"

        self.execute_query(query=query)
        return self.get_preprocessed_videos(self.get_query_result())
        
    def insert_video(self, video : dict) -> None:
        query = ""
        query += 'INSERT INTO videos VALUES\n('
        query += f"'{video['video_id']}', "
        query += f"'{video['video_name']}', "
        query += f"'{video['channel_id']}', "
        query += f"{video['view_count']}, "
        query += f"{video['like_count']}, "
        query += f"{video['dislike_count']}, "
        query += f"{video['like_ratio']}, "
        query += f"{video['comment_count']}, "
        query += f"'{video['trended_on']}');"

        self.execute_query(query)
        
    def update_video(self, video : dict) -> None:
        query = ""
        query += "UPDATE videos\n"
        query += f"SET view_count = {video['view_count']}, "
        query += f"like_count = {video['like_count']}, "
        query += f"dislike_count = {video['dislike_count']}, "
        query += f"like_ratio = {video['like_ratio']}, "
        query += f"comment_count = {video['comment_count']}, "
        query += f"trended_on = '{video['trended_on']}'\n"
        query += (f"WHERE video_id = '{video['video_id']}';")

        self.execute_query(query)

    def insert_channel(self, channel : dict) -> None:
        query = ""
        query += 'INSERT INTO channels VALUES\n('
        query += f"'{channel['channel_id']}', "
        query += f"{channel['subscriber_count']}, "
        query += f"{channel['subscriber_count_hidden']}, "
        query += f"{channel['video_count']}, "
        query += f"{channel['total_views']}, "
        query += f"'{channel['region']}');"

        self.execute_query(query)

    def update_channel(self, channel : dict) -> None:
        query = ""
        query += "UPDATE channels\n"
        query += f"SET subscriber_count = {channel['subscriber_count']}, "
        query += f"video_count = {channel['video_count']}, "
        query += f"total_views = {channel['total_views']}\n"
        query += (f"WHERE channel_id = '{channel['channel_id']}';")
        
        self.execute_query(query)

    def process_video(self, video : dict) -> None:
        if self.check_if_video_exists(video['video_id']) == False:
            self.insert_video(video=video)
        else:
            self.update_video(video=video)

    def process_channel(self, channel : dict) -> None:
        if self.check_if_channel_exists(channel['channel_id']) == False:
            self.insert_channel(channel=channel)
        else:
            self.update_channel(channel=channel)
        
    def print_table(self, table_name : str) -> None:
        self.cursor.execute("SELECT * FROM " + table_name)
        result = self.get_query_result()
        misc.print_separator(thick=True)

        print(table_name.upper())
        for i in self.get_column_titles():
            print(i, end = '\t')
        print(" ")
        for i in result:
            for j in i:
                print(j, end='\t')
            print(" ")
        misc.print_separator(thick=True)

    def close_cursor(self) -> None:
        self.cursor.close()

    def close_connection(self) -> None:
        if not self.cursor.closed:
            self.close_cursor()
        self.connection.close()