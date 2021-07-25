from qbittorrent import Client
from time import sleep
import asyncio
import os

class qb(object):
    qb = Client('http://127.0.0.1:8080/')

    def __init__(self, save_path: str) -> None:
        self.path = save_path

    def _add_movie_torrent(self, torrent: str) -> None:
        movie_folder = f"{self.path}\\movies\\{torrent.slug}"
        if movie_folder not in os.listdir(f"{self.path}\\movies"):
            os.mkdir(movie_folder)

        if torrent.quality_high is not None:
            hash = torrent.quality_high.split(':')[-1].lower()
        else:
            hash = torrent.quality_low.split(':')[-1].lower()

        self.qb.login()
        self.qb.download_from_link(hash, savepath=movie_folder)
        self.qb.toggle_first_last_piece_priority(hash)
        self.qb.toggle_sequential_download(hash)
        
        torrents = self.qb.torrents()
        for i in range(len(torrents)):
            if torrents[i]['hash'] == hash:
                while self.qb.torrents()[i]['progress'] < 0.02:
                    sleep(0.5)
                self.qb.pause(hash)

    async def add_movie_torrent(self, torrent: str) -> None:
        loop = asyncio.get_event_loop()
        loop.create_task(
            loop.run_in_executor(
                None, 
                self._add_movie_torrent, 
                torrent
            )
        )
    
    def _add_series_torrent(self, torrent: str) -> None:
        pass

    async def add_series_torrent(self, torrent: str) -> None:
        pass
