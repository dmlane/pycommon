""" Handle interactions with TVDB database"""

import os
import pickle
import tomllib
from dataclasses import dataclass, field
from pprint import pprint

import appdirs
import tvdb_v4_official

from pycommon.my_exceptions import MyException

CACHE_DIR = appdirs.user_cache_dir("net.dmlane/tvdb.cache")
CONFIG_DIR = appdirs.user_config_dir(appname="dmlane")
os.makedirs(CACHE_DIR, exist_ok=True)


@dataclass(eq=False)
class Episode:
    """Structure for storing episode information"""

    tvdb_id: int
    season_number: int
    episode_number: int
    name: str = None
    overview: str = None
    run_time: int = 0
    image_url: str = None


@dataclass(eq=False)
class Series:
    """Structure for storing series information"""

    tvdb_id: int
    name: str
    slug: str
    image_url: str = None
    episodes: list[Episode] = field(default_factory=list)


@dataclass(eq=False)
class Movie:
    """Structure for storing movie information"""

    tvdb_id: int
    name: str = None
    slug: str = None
    overview: str = None
    runtime: int = 0
    image_url: str = None


class MyTVDB:
    """Fetch information from TVDB.
    If action is None, then user Favourites are fetched (shows and movies)
    If action is "M", then movie with tvdb_id is fetched
    If action is "S", then show with tvdb_id is fetched
    """

    def __init__(self, action: str = None, tvdb_id: int = None):
        config_file = os.path.join(CONFIG_DIR, "tvdb.toml")

        try:
            with open(config_file, "rb") as handle:
                self.config = tomllib.load(handle)
        except FileNotFoundError as error:
            raise MyException(f"Could not open config file '{config_file}'") from error
        self.validate_action(action, tvdb_id)
        self.api = self.connect(
            self.config["credentials"]["api_key"], self.config["credentials"]["api_pin"]
        )
        if action is None:
            (self.series, self.movies) = self.fetch_favourites()
        elif action == "S":
            self.series = [tvdb_id]
            self.movies = []
        else:
            self.series = []
            self.movies = [tvdb_id]

    @staticmethod
    def validate_action(action, tvdb_id):
        """Ensure action and tvdb_id are consistent"""
        if action is not None and tvdb_id is None:
            raise MyException("If action is supplied, tvdb_id is required")
        if action is not None and action not in ["M", "S"]:
            raise MyException("action must be M or S or None")

    @staticmethod
    def connect(api_key: str, api_pin: str):
        """Connect to TVDB API"""

        try:
            handle = tvdb_v4_official.TVDB(api_key, api_pin)
        except Exception as inst:  # pylint: disable=broad-except
            print(inst)
            raise MyException("Could not connect to TVDB") from inst
        return handle

    def fetch_favourites(self):
        """Fetch favourites from TVDB"""
        url = self.api.url.construct("user/favorites")
        favourites = self.api.request.make_request(url)
        if favourites is None:
            raise MyException("Could not fetch favourites from TVDB")
        movies = []
        series = []
        for tvdb_id in favourites["series"]:
            series.append(self.fetch_series(tvdb_id))
        for tvdb_id in favourites["movies"]:
            movies.append(self.fetch_movie(tvdb_id))
        return series, movies

    def fetch_movie(self, tvdb_id: int):
        """Fetch movie from TVDB"""
        cache_file = f"{CACHE_DIR}/movie_{tvdb_id}.pickle"
        try:
            with open(cache_file, "rb") as handle:
                return pickle.load(handle)
        except FileNotFoundError:
            pass
        data = self.api.get_movie(tvdb_id)
        translations = self.api.get_movie_translation(tvdb_id, lang="eng")
        result = Movie(
            tvdb_id=tvdb_id,
            name=translations["name"],
            slug=data["slug"],
            overview=translations["overview"],
            runtime=data["runtime"],
            image_url=data["image"],
        )
        with open(cache_file, "wb") as file:
            pickle.dump(result, file)
        return result

    def fetch_series(self, tvdb_id: int):
        """Fetch series from TVDB"""
        cache_file = f"{CACHE_DIR}/series_{tvdb_id}.pickle"
        try:
            with open(cache_file, "rb") as handle:
                return pickle.load(handle)
        except FileNotFoundError:
            pass
        data = self.api.get_series_extended(tvdb_id)
        translations = self.api.get_series_translation(tvdb_id, lang="eng")

        result = Series(
            tvdb_id=tvdb_id,
            name=translations["name"],
            slug=data["slug"],
            image_url=data["image"],
            episodes=self.fetch_episodes(tvdb_id),
        )
        with open(cache_file, "wb") as file:
            pickle.dump(result, file)
        return result

    def fetch_episodes(self, tvdb_id: int):
        """Fetch episodes from TVDB"""
        data = self.api.get_series_episodes(id=tvdb_id)
        results = []
        for episode in data["episodes"]:
            if episode["seasonNumber"] > 0:
                if episode["number"] > 0:
                    translations = self.api.get_episode_translation(episode["id"], lang="eng")

                    results.append(
                        Episode(
                            tvdb_id=episode["id"],
                            season_number=episode["seasonNumber"],
                            episode_number=episode["number"],
                            run_time=episode["runtime"],
                            image_url=episode["image"],
                            name=translations["name"],
                            overview=translations["overview"],
                        )
                    )

        return results


try:
    test = MyTVDB()
    print(pprint(test.series))
    print(pprint(test.movies))
except MyException as g_inst:
    print(str(g_inst) + "??????????")
else:
    print("Finished OK ++++++++++")
