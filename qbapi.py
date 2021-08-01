from qbittorrent import Client
from plexapi.server import PlexServer
from time import sleep, time
from sys import platform
import asyncio
import os

if platform == "win32":
    div = "\\"
elif platform == "linux" or platform == "linux2":
    div = "/"

class qb_API(object):
    QB_URL = 'http://127.0.0.1:8080/'
    PLEX_URL = 'http://127.0.0.1:32400/'

    def __init__(self, save_path: str, plex_token: str) -> None:
        self.qb = Client(self.QB_URL)
        self.path = save_path
        self.plex = PlexServer(self.PLEX_URL, plex_token)

    def resume(self, hash):
        self.qb.resume(hash)

    def _add_movie_torrent(self, torrent: str) -> None:
        movie_folder = f"{self.path}{div}movies{div}{torrent.slug}"
        if torrent.slug not in os.listdir(f"{self.path}{div}movies"):
            os.mkdir(movie_folder)

        if torrent.quality_high is not None:
            #hash = torrent.quality_high.split(':')[-1].lower()
            hash = torrent.quality_high.lower().split(':')[3].split('&')[0]
        else:
            #hash = torrent.quality_low.split(':')[-1].lower()
            hash = torrent.quality_low.lower().split(':')[3].split('&')[0]

        self.qb.login()
        self.qb.download_from_link(hash, savepath=movie_folder)
        self.qb.toggle_first_last_piece_priority(hash)
        self.qb.toggle_sequential_download(hash)
        self.qb.set_torrent_name(hash, f"{torrent.slug}-{torrent.imdb}")
        
        timeout = time() + 300
        while time() < timeout:
            torrents = self.qb.torrents()
            for i in range(len(torrents)):
                if self.qb.torrents()[i]['progress'] > 0.02 and torrents[i]['hash'] == hash:
                    print("updating plex library")
                    self.qb.pause(hash)
                    self.plex.library.update()
                    return
            sleep(1)

    async def add_movie_torrent(self, torrent: str) -> None:
        loop = asyncio.get_event_loop()
        loop.run_in_executor( 
                None, 
                self._add_movie_torrent, 
                torrent
            )
    
    def _add_series_torrent(self, torrent: str) -> None:
        series_folder = f"{self.path}{div}series{div}{torrent.slug}"
        if torrent.slug not in os.listdir(f"{self.path}{div}series"):
            os.mkdir(series_folder)

        seasons = torrent.seasons

        for s in seasons.keys():
            num = int(s.split("S")[-1])
            season_num = f"season {num}"
            season_folder = f"{self.path}{div}series{div}{torrent.slug}{div}{season_num}"
            
            if season_num not in os.listdir(series_folder):
                os.mkdir(season_folder)

            for e in seasons[s].keys():
                # hash = seasons[s][e]['magnet'].lower().split(":")[3].split('&')[0]
                hash = seasons[s][e].lower().split(":")[3].split('&')[0]
                self.qb.login()
                self.qb.download_from_link(hash, savepath=season_folder)
                self.qb.toggle_first_last_piece_priority(hash)
                self.qb.toggle_sequential_download(hash)
                self.qb.set_torrent_name(hash, f"{torrent.slug}-{torrent.imdb}-{s}{e}")

    async def add_series_torrent(self, torrent: str) -> None:
        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            None,
            self._add_series_torrent,
            torrent
        )
