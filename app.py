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
    bitrate = 192
    codec = "mp3"
    recovery = False
    directory = ""  

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

    # костыль для отработки состояния по умолчанию
    tracklist = client.users_likes_tracks()
    if path.exists("yandex_music"):
            chdir("yandex_music")
    else:
        mkdir("yandex_music")
        chdir("yandex_music")


    if len(sys.argv) > 1:
        i = 1
        while i < len(sys.argv):
            match sys.argv[i]:
                case "-dir":
                    i += 1
                    directory = sys.argv[i]
                    chdir("../")
                    try:                    
                        if path.exists(directory):
                            chdir(directory)
                        else:
                            mkdir(directory)
                            chdir(directory)
                    except PermissionError:
                        print("Недостаточно прав")
                        exit()
                case "-codec":
                    i += 1
                    codec = sys.argv[i]
                    if codec not in ("mp3", "aac"):
                        print(
                            "Неизвестное значение кодека. Известные значения: mp3, aac."
                        )
                        exit()
                case "-bitrate":
                    i += 1
                    bitrate = int(sys.argv[i])
                    if bitrate not in (64, 128, 192, 320):
                        print(
                            "Неизвестное значение битрейта. Известные значения: 64, 128, 192, 320."
                        )
                        exit()
                case "-fix_metadata":
                    question = input(
                        """ВНИМАНИЕ!
Выбран режим восстановления метаданных и обложек всех аудиофайлов в директории,
загрузка займет примерно такое же время, как в первый раз!
Нажмите любую клавишу чтобы продолжить, 'q' для выхода\n"""
                    )
                    if question.lower() in ("qй") and question:
                        exit()
                    else:
                        fix = True
                        print("Метаданные и обложки будут восстановлены")
                case "-recovery":
                    question = input(
                        """ВНИМАНИЕ!
Выбран режим восстановления аудиотеки, это значит что программа загрузит заново все треки в плейлисте а также их обложки и метаданные.
Загрузка займет такое же время, как в первый раз!
Нажмите любую клавишу чтобы продолжить, 'q' для выхода\n"""
                    )
                    if question.lower() in ("qй") and question:
                        exit()
                    else:
                        recovery = True
                        fix = True
                        print("Аудиотека будет восстановлена")
                case "-pl":  # Выбор плейлиста и создание треклиста на его основе
                    i += 1
                    link = sys.argv[i]
                    link = link.split("/")
                    user = link[4]
                    playlistId = link[-1][: link[-1].index("?")]
                    playlist = client.users_playlists(kind=playlistId, user_id=user)
                    playlistName = playlist.title
                    tracklist = playlist.fetch_tracks()
                    track = tracklist[0].fetch_track()
                    if path.exists('../'+playlistName):
                        chdir('../'+playlistName)
                    else:
                        mkdir('../'+playlistName)
                        chdir('../'+playlistName)
                    #    track.download(track["title"]+'.mp3')
                    print(f"Загрузка плейлиста {playlistName}")
                case "-help":
                    print(
                        """ВАЖНО! 
    При использвании команд восстановления необходимо предоставить ссылку на плейлист который требуется 
восстановить, иначе будет восстановлен плейлист "Мне нравится"
    При вызове без команд будет загружен плейлист "Мне нравится" со значениями по умолчанию.

                          
Список команд
    -fix_metadata - восстановление аудиотеки (только метаданные и обложки)
    -recovery - полное восстановление аудиотеки (загрузка всех треков по новой, обложек и метаданных к ним)
    -pl "link" - загрузка плейлиста по ссылке. Если не указано загружается плейлист "Мне нравится"
    -codec <codec> - выбор формата файла музыки (mp3/aac) по умолчанию - mp3
    -bitrate <bitrate> - выбор битрейта (64, 128, 192, 320) по умолчанию - 192
    -dir <path_to_directory> - директория в которую будет загружена музыка если пути нет и прав достаточно - директория будет создана\n"""
                    )
                    exit()
                case _:
                    print("""Неизвестный аргумент""")
                    exit()
            i += 1
 
    amount = len(tracklist)
    print(f"amount of tracks: {amount}")
    time = datetime.now()
    playlistfile = open("playlist.txt", "w", encoding="utf-8")
    filename = ""
    choice = True
    continiuty = 0
    tracklist = tracklist.fetch_tracks()
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
            track = tracklist[i]
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
                f"текущий трек {i} из {amount}, {round(i / (amount) * 100, 1)}%"
            )
            playlistfile.write(filename + "\n")
            if path.exists(filename):
                continiuty += 1
                if fix:
                    audio = music_tag.load_file(filename)
                    # if audio['artwork'] == 0:
                    track.download_cover("cover.jpg", size="1000x1000")
                    set_cover(filename, "cover.jpg")
                    remove("cover.jpg")
                    print("обложка установлена")
                    set_metadata(filename, track)
                    continiuty -= 1                
                if not recovery:
                    print("файл существует, пропуск")
                    continue
            continiuty = 0

            while(1): # перебираем битрейты пока не найдем рабочий
                try:
                    track.download(filename, codec=codec, bitrate_in_kbps=bitrate)
                    break
                except:
                    bitrates = [64, 128, 192, 320].remove(bitrate)
                    bitrate = bitrates[-1]

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
