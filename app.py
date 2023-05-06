from yandex_music import Client
from os import mkdir, chdir, path
from datetime import datetime


try:
    from token_file import token
    client = Client(token).init()    
except:
    print("ошибка аутентификации")
    file = open("token_file.py","w")
    file.write(f"token = '{input('введите OAuth токен (как получить https://github.com/MarshalX/yandex-music-api/discussions/513#discussioncomment-2729781): ')}'"+'\n')
    file.close()
    input('saved, press enter to exit ')
    exit()

try:
    chdir('yandex_music')
except:
    mkdir('yandex_music')
    chdir('yandex_music')


amount = len(client.users_likes_tracks())
def fncheck(filename : str):
    result = filename
    for i in filename:
        if i in '<>:"/\|?*':
            result = result.replace(i,"")     
    return result

time = datetime.now()
file = open("playlist.txt","w")
try:
    for i in range(amount):
        track = client.users_likes_tracks()[i].fetch_track()
        try:
            artist = track['artists'][0]['name']
            filename = fncheck(f"{track['title']} - {artist}.mp3")
        except:
            print("no artist")
            filename = fncheck(f"{track['title']}.mp3")
        print (f"{filename} curent track {i} from {amount-1}, {round(i/(amount-1)*100,1)}%")
        if path.exists(filename):
            print('skip')
            continue
        client.users_likes_tracks()[i].fetch_track().download(filename)     
    file.close()
    print(f"""done!
    took {datetime.now() - time}""")
    input()
except KeyboardInterrupt:
    file.close()
    print(f'interupt {filename} {round(i/(amount-1)*100,1)}%')
