from yandex_music import Client
from os import mkdir, chdir, path, remove
from datetime import datetime
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import sys
import music_tag

picture = 1  # set to true if cover required


def set_cover(filename: str, cvr: str):
    if not picture:
        return
    audio = MP3(filename, ID3=ID3)
    try:
        audio.add_tags()
    except error:
        pass
    audio.tags.add(
        APIC(mime="image/png", type=3, desc="Cover", data=open(cvr, "rb").read())
    )
    audio.save()
    # print("set cover", cvr)


def fncheck(filename: str):
    result = filename
    for i in filename:
        if i in '<>:"/\|?*':
            result = result.replace(i, "")
    return result


def set_metadata(filename: str, track: dict):
    # print(audio)
    audio = music_tag.load_file(filename)
    audio["artist"] = track["artists"][0]["name"]
    audio["albumartist"] = track["artists"][0]["name"]
    audio["tracktitle"] = track["title"]
    if track["albums"]:
        audio["year"] = track["albums"][0]["year"]
        audio["album"] = track["albums"][0]["title"]
    audio.save()


if __name__ == "__main__":
    fix = False
    try:
        from token_file import token

        client = Client(token).init()
    except:
        print("Ошибка аутентификации, OAuth токен отсутствует")
        file = open("token_file.py", "w")
        file.write(
            f"token = '{input('введите OAuth токен (как получить https://github.com/MarshalX/yandex-music-api/discussions/513#discussioncomment-2729781): ')}'"
            + "\n"
        )
        file.close()
        input("Сохранено, нажмите enter чтобы выйти")
        exit()

    if len(sys.argv) > 1:
        i = 1
        while i < len(sys.argv):
            match sys.argv[i]:
                case "-fix":
                    question = input(
                        """ВНИМАНИЕ!
Выбран режим восстановления аудиотеки, это значит 
что программа восстановит обложки и метаданные
всех аудиофайлов в директории,
загрузка займет примерно такое же время, как в первый раз!
Нажмите любую клавишу чтобы продолжить, 'q' для выхода\n"""
                    )
                    if question.lower() in ("qй") and question:
                        exit()
                    else:
                        fix = True
                        print("Аудиотека будет восстановлена")
                case "-pl": # Выбор плейлиста и создание треклиста на его основе                    
                    i += 1
                    link = sys.argv[i]
                    link = link.split('/')
                    user = link[4]
                    playlistId = link[-1][:link[-1].index('?')]
                    playlist = client.users_playlists(
                        kind = playlistId, user_id = user
                    )
                    playlistName = playlist.title  
                    tracklist = playlist.fetch_tracks()
                    track = tracklist[0].fetch_track()
                    if path.exists(playlistName):
                        chdir(playlistName)
                    else:
                        mkdir(playlistName)
                        chdir(playlistName)
                    #    track.download(track["title"]+'.mp3')
                    print(f"Загрузка плейлиста {playlistName}")
                case _:
                    print(
                        """Неизвестный аргумент
Список команд:
    -fix - восстановление аудиотеки
    -pl "link" - загрузка плейлиста по ссылке\n"""
                    )
                    exit()
                
            i += 1
    else: # Выбор по умолчанию (если не даны никакие аргументы) - загрузка плейлиста "Мне нравится"
        tracklist = client.users_likes_tracks()
        if path.exists("yandex_music"):
            chdir("yandex_music")
        else:
            mkdir("yandex_music")
            chdir("yandex_music")

    amount = len(tracklist)
    print(f"amount of tracks: {amount}")
    time = datetime.now()
    playlistfile = open("playlist.txt", "w", encoding="utf-8")
    filename = ""
    choice = True
    continiuty = 0
    try:
        for i in range(amount):
            if continiuty > 100 and choice:
                option = input(
                    """100 треков уже существуют, желаете продолжить?
Если выбрано "Y" вопрос больше не будет задан. (y чтобы продолжить, N (по умолчанию) чтобы выйти)"""
                )
                if option.lower() not in ("y", "yes", "1"):
                    print("exiting")
                    break
                else:
                    print("вопросов больше не будет.")
                    choice = False
            track = tracklist[i].fetch_track()
            # print(track)
            # exit()
            artist = ""
            try:
                artist = track["artists"][0]["name"]
                trackname = track["title"]
                filename = artist + " - " + trackname + ".mp3"
                filename = fncheck(filename)
            except LookupError:
                print("нет артиста")
                artist = ""
                filename = track["title"] + ".mp3"
                filename = fncheck(filename)
            # except UnicodeEncodeError:
            #     if not artist:
            #         filename = unidecode(f"{track['title']}.mp3")
            #     else:
            #         filename = unidecode(f"{track['title']} - {artist}.mp3")
            # flename = filename.encode("ascii",'replace')
            print(filename, end=" ")
            print(
                f"текущий трек {i} из {amount - 1}, {round(i / (amount - 1) * 100, 1)}%"
            )
            playlistfile.write(filename + "\n")
            if path.exists(filename):
                if fix:
                    audio = music_tag.load_file(filename)
                    # if audio['artwork'] == 0:
                    track.download_cover("cover.jpg", size="1000x1000")
                    set_cover(filename, "cover.jpg")
                    remove("cover.jpg")
                    print("обложка установлена")
                    set_metadata(filename, track)
                    continiuty -= 1
                print("файл существует, пропуск")
                continiuty += 1
                continue
            continiuty = 0
            track.download(filename)
            track.download_cover("cover.jpg", size="1000x1000")
            set_cover(filename, "cover.jpg")
            remove("cover.jpg")
            set_metadata(filename, track)
            # print("метаданные и обложка установлены")
        playlistfile.close()
        print(
            f"""Загрузка завершена!
Загрузка заняла {datetime.now() - time}"""
        )
        input()
    except KeyboardInterrupt:
        playlistfile.close()
        print("остановлено вручную", filename, f"{round(i / (amount - 1) * 100, 1)}%")
        input()
