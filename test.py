import requests

import json

##메타태그 목록 불러오는 경우

headers = {
    'Authorization': 'KakaoAK ba524f20b7f4f9e2ade2cf9374576e19'
}

url = 'https://dapi.kakao.com/v3/search/book'
query = 'query=스티브잡스&page=2'

response = requests.get(url+'?'+query, headers=headers)

dict = json.loads(response.text)
dict_array = dict['documents']

##총 도서 수
print(dict['meta']['total_count'])


print(dict['documents'][0])
print(dict['documents'][1])
print(dict['documents'][2])
print(dict['documents'][3])
print('----')
for book in dict['documents']:
    print(book['title'])

'''
for dict['documents'][0]['title'] in dict['documents']:
    print (dict_array[i]['title']['title'], dict_array[i]['title']['authors'])
'''