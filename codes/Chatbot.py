import pickle
import urllib.request
import urllib.parse
import json
import time
import numpy as np


bot_token = '5129151550:AAHwzHJHDTbJEHq3yqunwULzKNhd_hr8ES0'

def request(url):
    response = urllib.request.urlopen(url)
    byte_data = response.read()
    text_data = byte_data.decode()
    return text_data

def build_url(method, query):
    return f'https://api.telegram.org/bot{bot_token}/{method}?{query}'

def request_to_chatbot_api(method, query):
    url = build_url(method, query)
    response = request(url)
    return json.loads(response)

def simplify_messages(response):
    result = response['result']
    if not result:
        return None, []
    last_update_id = max(item['update_id'] for item in result)
    messages = [item['message'] for item in result]
    simplified_messages = [{'from_id': message['from']['id'],
                            'text': message['text']}
                           for message in messages]
    return last_update_id, simplified_messages

def get_updates(update_id):
    query = f'offset={update_id}'
    response = request_to_chatbot_api(method='getUpdates', query=query)
    return simplify_messages(response)

def send_message(chat_id, text):
    text = urllib.parse.quote(text)
    query = f'chat_id={chat_id}&text={text}'
    response = request_to_chatbot_api(method='sendMessage', query=query)
    return response

def predict_genre(s, pipe_dict):
    # s_new = clean_sentence(s)
    genre_analyzed = []
    proba = []
    for genre, pipe in pipe_dict.items():
        res = pipe.predict_proba([s])
        genre_analyzed.append(genre)
        proba.append(res[0][1])
        genre_idx = np.argmax(proba)

    return genre_analyzed[genre_idx], round( max(proba) * 100, 2)

def check_messages_and_response(next_update_id, trained_data):
    last_update_id, recieved_messages = get_updates(next_update_id)
    for message in recieved_messages:
        chat_id = message['from_id']
        text = message['text']
        if (text == "/start"):
            send_text = "무슨 단어가 떠오르시나요? "
        elif(text == "/hi"):
            send_text = "Hey!"

        else:
            premsg1, premsg2 = predict_genre(text, trained_data)
            if ( premsg2 > 20):
                send_text = "How about this type of movie? " + premsg1
            else:
                send_text = "Oops, I can't understand your word..."
            send_message(chat_id, send_text)
    return last_update_id




if __name__ == '__main__':

    try:
        with open('last_update_id.txt', 'r') as file:
            next_update_id = int(file.read())
        with open('trained_data2.txt', 'rb') as f:
            trained = pickle.load(f)
    except (FileNotFoundError, ValueError):
        next_update_id = 0

    while True:
        last_update_id = check_messages_and_response(next_update_id ,trained)
        if last_update_id:
            next_update_id = last_update_id + 1
            with open('last_update_id.txt', 'w') as file:
                file.write(str(next_update_id))
        time.sleep(2)


# print(get_updates(response_msg))
# send_message(response_msg[1][0])

