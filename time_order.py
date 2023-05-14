from yandex_music import Client
from os import mkdir, chdir, path, utime
from datetime import datetime


def fncheck(filename : str):
        result = filename
        for i in filename:
            if i in '<>:"/\|?*':
                result = result.replace(i,"")     
        return result

def set_time(file_path,a):    
    utime(file_path, (datetime.now().timestamp(), datetime.now().timestamp()+a))


if __name__ == '__main__':
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

    tracklist = client.users_likes_tracks()
    amount = len(tracklist)    

    time = datetime.now()
    playlistfile = open("playlist.txt","w",encoding="utf-8")
    try:
        for i in range(amount):            
            track = tracklist[i].fetch_track()
            try:
                artist = track['artists'][0]['name']
                filename = fncheck(f"{track['title']} - {artist}.mp3")
            except:
                print("no artist")
                filename = fncheck(f"{track['title']}.mp3")
            print (f"{filename} curent track {i+1} from {amount}, {round(i/(amount-1)*100,1)}%")
            playlistfile.write(f'{filename}\n')            
            if path.exists(filename):
                set_time(filename,i)
                print('skip')
                continue
            track.download(filename)
            set_time(filename,i)  
        playlistfile.close()
        print(f"""done!
took {datetime.now() - time}""")
        input()
    except KeyboardInterrupt:
        playlistfile.close()
        print(f'interupt {filename} {round(i/(amount-1)*100,1)}%')
