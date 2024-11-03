# API server+crawler for parsing YouTube charts  
uses postresql and YouTube Data API v3 which is provided by google.    

## This is a Uni project I've made for "Data Bases" discipline.   

before use you must create your private key and insert it into misc.py file  
https://developers.google.com/youtube/v3/getting-started

## API description:

Получение списка видео 

Endpoint: GET /api/v1/videos 

Без параметров возвращает 5 первых доступных экземпляров resource (далее - видео), описанных ниже. (5 видео, с наибольшим значением view_count) 

Возможные параметры:  

  channel_id – string: возвращает 5 видео с наибольшим кол-вом просмотров, выпущенных на канале с заданным id. 
  
  regions – string: возвращает 5 видео с наибольшим кол-вом просмотров, выпущенных из данного региона (работает с channel_id). Можно ввести несколько значений через запятую. 
  
  video_num – int: меняет кол-во возвращаемых видео (работает с channel_id и region) 

 

Resource representation: 
    
    { 
    
      “video_id”: string, 
      
      “video_name”: string, 
      
      “channel”:  
      
      { 
      
        “channel_id”: string, 
        
        "subscriber_count”: int, 
        
        “subscriber_count_hidden”: bool, 
        
        “video_count”: int, 
        
        "total_views”: int, 
        
        “region”: string 
      
      } 
      
      "view_count”: int, 
      
      “like_count”: int, 
      
      “dislike_count”: int,  
      
      “like_ratio”: double, 
      
      “comment_count”: int, 
    
    } 

 

Endpoint: GET /api/v1/videos/{video_id} 

Тип video_id - string. Возвращает 1 экземпляр resource из предыдущего пункта.  

 

Получение списка каналов 

Endpoint: GET /api/v1/channels 

Без параметров возвращает 5 первых доступных экземпляров resource (далее - канал), описанных ниже. (5 каналов, с наибольшим кол-вом подписчиков) 

Возможные параметры:  
  
  regions – string: возвращает 5 каналов с наибольшим кол-вом подписчиков и с заданным регионом. Можно ввести несколько значений через запятую. 
  
  channel_num – int: меняет кол-во возвращаемых каналов (работает с region) 

 

Resource representation: 

“channel”:  

    { 
      
      “channel_id”: string, 
      
      "subscriber_count”: int, 
      
      “subscriber_count_hidden”: bool, 
      
      “video_count”: int, 
      
      "total_views”: int, 
      
      “region”: string 
    
    } 

 

Endpoint: GET /api/v1/channels/{channel_id} 

Тип channel_id - string. Возвращает 1 экземпляр resource из предыдущего пункта.  

 

 

Парсинг трендов на YouTube 

Endpoint: GET /api/v1/search 

Возможные параметры: 

  region – string (Обязательный параметр. Если не указан - будет установлен RU): Формат: ISO_3166-1_alpha-2. Примеры: “RU”, “US”, “UK”. 
  
  min_views – int : В парсинге будут учитываться только видео с кол-вом просмотров >= min_views. 
  
  max_views – int : В парсинге будут учитываться только видео с кол-вом просмотров <= max_views. 
  
  video_num – int : В парсинге будут учитываться только первые video_num результатов поиска. (1 <= video_num <= 50) 

Resource representation: 

    { 
    
      “videos”: [ 
      
        { 
        
          “video_id”: string, 
          
          “video_name”: string, 
          
          “channel”:  
          
          { 
          
            “channel_id”: string, 
            
            "subscriber_count”: int, 
            
            “subscriber_count_hidden”: bool, 
            
            “video_count”: int, 
            
            "total_views”: int, 
            
            “region”: string 
          
          } 
          
          "view_count”: int, 
          
          “like_count”: int, 
          
          “dislike_count”: int,  
          
          “like_ratio”: double, 
          
          “comment_count”: int, 
          
          “trended_on”: int 
        
        }  
      
      ], 
      
      “serach”:  
      
      { 
      
        “videos_parsed”: int, 
        
        “channels_parsed”: int, 
        
        “videos_added”: int, 
        
        “channels_added”: int 
      
      } 
    
    } 

 

V) Cкрипт для создания схем данных на языке SQL 

 
    
    DROP TABLE IF EXISTS channels;  
    
    CREATE TABLE IF NOT EXISTS channels(  
    
    channel_id TEXT primary key NOT NULL,  
    
    subscriber_count int,  
    
    subscriber_count_hidden bool NOT NULL,  
    
    video_count int NOT NULL,   
    
    total_views bigint NOT NULL,  
    
    region char(2)  
    
    );  
    
      
    
    DROP TABLE IF EXISTS videos;  
    
    CREATE TABLE IF NOT EXISTS videos(  
    
    video_id TEXT primary key NOT NULL,  
    
    video_name TEXT NOT NULL,  
    
    channel_id TEXT references channels(channel_id) NOT NULL,   
    
    view_count bigint NOT NULL,   
    
    like_count int,  
    
    dislike_count int,  
    
    like_ratio numeric(2),  
    
    comment_count int NOT NULL,  
    
    trended_on timestamp  
    
    ); 
