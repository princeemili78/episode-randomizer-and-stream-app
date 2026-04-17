import requests
import random
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date


TMDB_API_KEY = "11e77ad7136edd1deb30fd3a7d5955e6" #REMEMBER TO MOVE TO ST.SECRETS LATER
class Episode:
    """Creates episode objects
    :param episode_info: dictionary for each episode from API
    :ivar name: name of episode
    :ivar rating: IMDb rating for episode

    """
    def __init__(self, episode_info, imdb_id, tmdb_id):
        self.episode_info = episode_info
        self.imdb_id = imdb_id
        self.tmdb_id = tmdb_id
        self.season = self.set_self("No season info", "season")
        self.number = self.set_self("No episode number", "number")
        self.release_date = episode_info["airdate"]
        self.season_and_number = f"Season {self.season} Episode {self.number}"     
        self.name = self.set_self("No episode name", "name")
        self.rating = self.set_self(0, "rating", "average")
        self.type = self.set_self("No type found", "type")
        self.image = self.set_self("https://placehold.co/210x295?text=No+Image", "image", "medium")
        self.server_list = ["Server 1", "Server 2", "Server 3", "Server 4", "Server 5", "Server 6"]
        self.links = self.link_dict()
        self.summary = self.get_summary_text() if self.is_null("summary") != True else ""
        self.isReleased = self._isReleased()

    # Check if an episode has actually been released
    def _isReleased(self):
        if self.release_date == "":
            return False
        else:
            if datetime.strptime(self.release_date, "%Y-%m-%d").date() > date.today():
                return False
            else:
                return True

    # Remove HTML tags from episode summary 
    def get_summary_text(self):
        soup = BeautifulSoup(self.episode_info["summary"], "html.parser")
        text = soup.get_text()
        return text
       
    # Check for nulls values. If value is not null, it returns true
    def is_null(self, nest_level1, nest_level2=""):
        if nest_level2 == "":
            return self.episode_info[nest_level1] == None 
        elif self.episode_info[nest_level1] == None:
            return True
        else:
            return self.episode_info[nest_level1][nest_level2] == None
    
    # Use value for null to return proper value in the init
    def set_self (self, error_value, nest_level1, nest_level2=""):
        if nest_level2 == "":
            if self.is_null(nest_level1) == True:
                return error_value
            else:
                return self.episode_info[nest_level1]
        else:
            if self.is_null(nest_level1, nest_level2) == True:
                return error_value
            else:
                return self.episode_info[nest_level1][nest_level2] 
    # Function to get embed links for episode
    def embed_links(self):
        link_templates = ["https://vidsrc.cc/v2/embed/tv/{imdb_id}/{season}/{number}",
                                   "https://vidlink.pro/tv/{tmdb_id}/{season}/{number}",
                                   "https://vidsrc-embed.ru/embed/tv/{imdb_id}/{season}-{number}",
                                   "https://multiembed.mov/?video_id={tmdb_id}&tmdb=1&s={season}&e={number}",
                                   "https://player.vidplus.to/embed/tv/{tmdb_id}/{season}/{number}",
                                    "https://getsuperembed.link/?video_id={imdb_id}&season={season}&episode={number}"]
        link_list = ([link.replace("{imdb_id}", str(self.imdb_id)).replace("{season}", str(self.season)).replace("{number}", str(self.number)) 
                      if "{imdb_id}" in link 
                      else link.replace("{tmdb_id}", str(self.tmdb_id)).replace("{season}", str(self.season)).replace("{number}", str(self.number)) 
                      for link in link_templates]
                      )
        return link_list
    
    # Create dictionary for server links
    def link_dict(self):
        return dict(zip(self.server_list, self.embed_links()))
        
        

class TvShow:
    """Creates instance of TV show you want to watch

    :param show_name: title of the TV show
    :ivar show_json: json for entire show returned
    :ivar title_id: ID for show on TVAPI
    :ivar seasons: List of seasons object corresponding to number of seasons in show
    """

    def __init__(self, json_link):
        self.json_link = json_link
        self.json = self.get_json()
        self.imdb_id = self.json["externals"]["imdb"] if self.json["externals"]["imdb"] != None else "No ID found"
        self._tmdb_id = None
        self.picture = self.set_self("https://placehold.co/210x295?text=No+Image", "image", "medium")
        self.title_id = self.get_title_id()
        self._all_episodes = None
        self._season_list = None
        self._season_episode_dict = None
        

# Add string for show name to the end of the api address to show json  
    def get_json(self):
        r = requests.get(self.json_link)
        if r.json() == None:
            raise Exception("Could not find a show with that name")
        
        return r.json()
    
    def get_title_id(self):
        id = self.json["id"]
        return id
# Get tmdb ID
    @property
    def tmdb_id(self):
        if self._tmdb_id == None:
            if self.imdb_id == "No ID found":
                self._tmdb_id = None
                return self._tmdb_id
            else:
                tmdb_json = requests.get(f"https://api.themoviedb.org/3/find/{self.imdb_id}?api_key={TMDB_API_KEY}&external_source=imdb_id").json()
                if len(tmdb_json["tv_results"]) != 0: 
                    self._tmdb_id = tmdb_json["tv_results"][0]["id"]
                    return self._tmdb_id
                else:
                    self._tmdb_id = None
                    return self._tmdb_id
        else:
            return self._tmdb_id
   # Implementing lazy loading to make shit faster     
    @property
    def all_episodes(self):
        if self._all_episodes == None:
            episodes_json = requests.get(f"https://api.tvmaze.com/shows/{self.title_id}/episodes").json()
            all_episodes = [Episode(e, self.imdb_id, self.tmdb_id) for e in episodes_json]
            released_episodes = [e for e in all_episodes if e.isReleased]
            self._all_episodes = released_episodes
            return self._all_episodes       
        else:
            return self._all_episodes
    
    # Function to get next episode of TvShow
    def next_episode(self, episode):
        if isinstance(episode, Episode) == True:
            if episode == self.all_episodes[-1]:
                raise Exception("This is the last episode")
            episode_index = self.all_episodes.index(episode)
            next_episode = self.all_episodes[episode_index + 1]
            return next_episode
    
    # Function to get previous episode of TvShow
    def previous_episode(self, episode):
        if isinstance(episode, Episode) == True:
            episode_index = self.all_episodes.index(episode)
            if episode_index == 0:
                raise Exception("This is the first episode")
            previous_episode = self.all_episodes[episode_index - 1]
            return previous_episode

    # Check for nulls values. If value is not null, it returns true
    def is_null(self, nest_level1, nest_level2=""):
        if nest_level2 == "":
            return self.json[nest_level1] == None 
        elif self.json[nest_level1] == None:
            return True
        else:
            return self.json[nest_level1][nest_level2] == None
    
    # Use value for null to return proper value in the init
    def set_self (self, error_value, nest_level1, nest_level2=""):
        if nest_level2 == "":
            if self.is_null(nest_level1) == True:
                return error_value
            else:
                return self.json[nest_level1]
        else:
            if self.is_null(nest_level1, nest_level2) == True:
                return error_value
            else:
                return self.json[nest_level1][nest_level2] 
        
    # Get list of seasons by parsing through episode list for unique season values
    @property
    def season_list(self):
        if self._season_list == None:
            season_list = {self.all_episodes[e].season for e in range(len(self.all_episodes))}
            self._season_list = sorted(season_list)
            return self._season_list
        else:
            return self._season_list
    
# Create dictionary with Season as key and list of episodes matching season as value
    @property
    def season_episode_dict(self):
        if self._season_episode_dict == None:
            self._season_episode_dict = {season: [episode for episode in self.all_episodes if episode.season == season] for season in self.season_list}
            return self._season_episode_dict
        else:
            return self._season_episode_dict

# Create list of episode numbers in a specific season
    def episode_numbers_in_season(self, season):
        return [episode.number for episode in self.season_episode_dict[season]]

# Create list of episodes that satisfy seasons and rating requirements
    def valid_episodes(self, rating=0, seasons=None):
        if seasons == [] or seasons == None:
            seasons = self.season_list
        if rating == None:
            rating = 0


        # Create list of episodes that satisfy the user's requirements by filtering with a list comprehension
        valid_episodes = [e for e in self.all_episodes if e.rating != None and e.season in seasons and e.rating >= rating]
        if len(valid_episodes) == 0:
            raise Exception("Ur rating is too high fuck nigga, lower ur standards")
        else:
            return valid_episodes
# Return random episode 
    def random_episode(self, valid_episodes):
        if valid_episodes != []:      
            random_episode = random.choice(valid_episodes)
            return random_episode
        else:
            raise Exception ("No more random episodes")
    # Function to return the streaming providers of a TvShow
    def provider_list(self, country):
        r = requests.get(f"https://api.themoviedb.org/3/tv/{self.tmdb_id}/watch/providers?api_key={TMDB_API_KEY}").json()
        list_providers_in_country = r["results"][country]["flatrate"]
        return  list_providers_in_country
    # Get filepath for all provider logos
    def provider_filepaths(self):
        filepaths = [provider["logo_path"] for provider in self.provider_list("US")]
        return filepaths
    # Get filepath image urls
    def provider_images(self):
        return [tmdb_image_link(filepath, "original") for filepath in self.provider_filepaths()]
    
    # Function to return 


class SearchResult:
    """Creates instance of a SearchResult

    :param show_name: result_json
    """
    def __init__(self, result_json):
        self.result_json = result_json
        self.link = self.result_json["_links"]["self"]["href"]
        self.image = self.set_self("https://placehold.co/210x295?text=No+Image", "image", "medium")
        
        

   
    # Check for nulls values. If value is not null, it returns true
    def is_null(self, nest_level1, nest_level2=""):
        if nest_level2 == "":
            return self.result_json[nest_level1] == None 
        elif self.result_json[nest_level1] == None:
            return True
        else:
            return self.result_json[nest_level1][nest_level2] == None
    
    # Use value for null to return proper value in the init
    def set_self (self, error_value, nest_level1, nest_level2=""):
        if nest_level2 == "":
            if self.is_null(nest_level1) == True:
                return error_value
            else:
                return self.result_json[nest_level1]
        else:
            if self.is_null(nest_level1, nest_level2) == True:
                return error_value
            else:
                return self.result_json[nest_level1][nest_level2] 


# Function to return all search results for a query
def fuzzy_search_result(search):
    r = requests.get(f"https://api.tvmaze.com/search/shows?q= {search}").json()
    if r == None:
            raise Exception("Could not find a show with that name")
    
    search_results = [SearchResult(r[idx]["show"]) for idx in range(len(r)) ]
    return search_results



# Get image off tmdb databse
def tmdb_image_link(filepath, size):
    return f"https://image.tmdb.org/t/p/{size}/{filepath}"
