from flask import Flask, render_template, request, jsonify, redirect , url_for
import pymysql
from flask_cors import CORS
import pymysql.cursors
from annoy import AnnoyIndex
from sentence_transformers import SentenceTransformer
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
augment_dir = 'aug_sbert_model'
golden_dir = 'golden_sbert_model'
model = SentenceTransformer(golden_dir)

db = pymysql.connect(host='localhost',
                     port=8989,
                     user='admin',
                     passwd='',
                     db='lyrics',
                     charset='utf8'
                      )

app = Flask(__name__)   
cors = CORS(app, resources={r'*': {"origins": "*"}})

len_vec=768
annoy_index = AnnoyIndex(len_vec, 'angular')
annoy_index.load('ly_index.annoy')




#from oauth2client.tools import argparser


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
# DEVELOPER_KEY = ""
# YOUTUBE_API_SERVICE_NAME = "youtube"
# YOUTUBE_API_VERSION = "v3"


# youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,   developerKey=DEVELOPER_KEY)

def video_urls(ids):
    video_ids = ids.split(",")
    embed_urls = []
    for video_id in video_ids:
        request = youtube.videos().list(
            part='player',
            id=video_id,
            key=DEVELOPER_KEY
        )
        response = request.execute()
        embed_url = response['items'][0]['player']['embedHtml']
        match = re.search(r'src="([^"]+)"', embed_url)
        if match:
            embed_url = match.group(1)
            embed_urls.append(embed_url)
    return embed_urls
@app.route("/")
def main():
    return render_template('main0.html')

@app.route("/howto")
def howto():
    return render_template('howtouse.html')     

@app.route("/search", methods=['POST'])
def search():
    category = request.form['category']
    keyword = request.form['search']
    print(category,keyword)
    if keyword :
        word = keyword.replace(' ','')
        try:
            cursor = db.cursor(pymysql.cursors.DictCursor)

            if category == 'lyrics' :
                sql = f"select * from music_meta where replace(replace(lyrics,' ', ''),'\n','') like '%{word}%' order by release_date desc"
                cursor.execute(sql)
                result = cursor.fetchall()  
            elif category =='artists':
                sql = f"select * from music_meta where singer like '%{word}%' order by release_date desc"
                cursor.execute(sql)
                result = cursor.fetchall()  
            else :
                sql = f"select * from music_meta where title like '%{word}%' order by release_date desc"
                cursor.execute(sql)
                result = cursor.fetchall()  
        except Exception as e:
            print(f"Database error: {e}")
            flush("There was an error with the database query.")
            return render_template('main0.html')
        finally:
            cursor.close()

        if not result :
            result = 'none'
        return render_template('main1.html', result=result ,keyword = keyword)
    keyword=''
    return render_template('main0.html')




@app.route("/detail/<id>")
def detail(id):
    cursor = db.cursor(pymysql.cursors.DictCursor)
    ## 선택된 곡 id 에 맞는 정보 가져오기
    #sql = f'select mm.*, t.vector vec  from music_meta mm , temp t where mm.id = t.idx and mm.id = {id}'
    sql = f'select mm.*  from music_meta mm where mm.id = {id} '
    cursor.execute(sql)
    source =cursor.fetchone()
    print(source['title'],source['id'])

    ## prediction  - id에 맞는 nns list 반환
    nns =annoy_index.get_nns_by_item(int(id), 20, include_distances=True)
    print(nns[1])
    ## 1 - distance = cosine sim
    ## 리메이크 곡의 평균 threshold 값을 적용
    sum=0
    for ns in nns[1]:
        sum+=ns        
        if sum ==0.0 :
            my_indexes = nns[0][:5]
        else :
            my_indexes = [index for i, index in enumerate(nns[0]) if nns[1][i]> 0.15]
    ## 유사곡 추천 갯수 제한
    sub_str = my_indexes[:5]
    print(my_indexes)
    my_string = ', '.join(str(x) for x in sub_str)
    #sql = f'select mm.*, t.vector vec  from music_meta mm , temp t where mm.id = t.idx and mm.id in ({my_string})'
    sql = f'select mm.*  from music_meta mm where mm.id in ({my_string}) ORDER BY FIELD(id,{my_string});'
    cursor.execute(sql)
    result =cursor.fetchall()

    # for s in range(len(result)):
    #     song_title = result[s]['title']
    #     soong_singer = result[s]['singer']
    #     query = song_title +' '+ soong_singer
    #     print(query)
    #     # Call the search.list method to retrieve results matching the specified
    #     # query term.
    #     search_response = youtube.search().list(
    #     q=query,
    #     part='id',
    #     type='video',
    #     maxResults=5 ,
    #     videoEmbeddable='true',
    #     key=DEVELOPER_KEY
    #     ).execute()


    #     ## 하나의 쿼리가 실행 시
    #     e_urls={}
    #     video_ids = [search_result["id"]["videoId"] for search_result in search_response.get("items", [])]
    #     embed_urls = video_urls(",".join(video_ids))
    #     #for j,embed_url in enumerate(embed_urls):
    #     fi_url = f'<iframe width="480" height="270" src="{embed_urls[1]}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>'
    #     e_urls[song_title] =fi_url
    # result.append(e_urls)
    print(len(result))
    return render_template('main2.html', result = result, source=source)




@app.route("/nondb" , methods=['POST'])
def nondb():
    lyrics =request.form['lyrics']
    #if lyrics : 
    ## 가사 임베딩
    nns= annoy_index.get_nns_by_vector(model.encode(lyrics), 5,  include_distances=True)
    #my_indexes = [index for i, index in enumerate(nns[0]) if nns[1][i]> 0.2]

    ## 유사곡 추천 갯수 제한
    #sub_str = my_indexes[:5]
    #my_string = ', '.join(str(x) for x in sub_str)
    my_string = ', '.join(str(x) for x in nns[0][:])
    print(nns)
    cursor = db.cursor(pymysql.cursors.DictCursor)
    #sql = f'select mm.*, t.vector vec  from music_meta mm , temp t where mm.id = t.idx and mm.id in ({my_string}) order by field(id,{my_string})'
    sql = f'select mm.*  from music_meta mm where mm.id in ({my_string}) order by field(id,{my_string}) '
    cursor.execute(sql)
    result =cursor.fetchall()
    return render_template('main2.html', result=result, lyrics=lyrics)
    # else :
    #     print('error')
    #     return redirect(url_for("main"))
app.run(host='0.0.0.0', port=8999, debug=True)

db.close()  
