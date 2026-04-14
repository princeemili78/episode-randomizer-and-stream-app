import streamlit as st
from episode_puller_v2 import TvShow
from episode_puller_v2 import Episode
from episode_puller_v2 import fuzzy_search_result
import streamlit.components.v1 as components
st.title("What do you want to watch?")

# Set default values to set my session_state on the first app
def initialize_session_state():
    # Centralizing EVERY session state key used in your app
    defaults = {
        "show": "", 
        "show_name": "", 
        "episode_generated": False, 
        "episode": "", 
        "rating": None, 
        "seasons": [], 
        "valid_episodes": [], 
        "episode_error": None,
        "disabled": False,
        "season_choice": None,
        "next_episode_error": None,
        "previous_episode_error": None,
        "user_agent": st.context.headers.get("User-Agent"),
        "random_mode": False,
        "specific_mode": False,
        "server": "Server 1"
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_session_state():
    # Centralizing EVERY session state key used in your app
    defaults = {
        "show": "", 
        "show_name": "", 
        "episode_generated": False, 
        "episode": "", 
        "rating": None, 
        "seasons": [], 
        "valid_episodes": [], 
        "episode_error": None,
        "disabled": False,
        "season_choice": None,
        "next_episode_error": None,
        "previous_episode_error": None,
        "user_agent": st.context.headers.get("User-Agent"),
        "random_mode": False,
        "specific_mode": False,
        "server": "Server 1"
    }
    
    for key, value in defaults.items():
        st.session_state[key] = value

# Logic for updating server choice when user interacts with the selectbox
def choose_server():
    if st.session_state.server_selection != st.session_state["server"]:
        st.session_state["server"] = st.session_state.server_selection
    
initialize_session_state()

# Conditional to show first page of app where user can pick TV show, random/specific episodes and generate the episode
if st.session_state["episode_generated"] == False:
    # If a show has not been loaded then present the text box for the user to type out a show to watch
    if not isinstance(st.session_state["show"], TvShow):
        show_name = st.text_input("Name of Tv Show", help="Type name of show")
        
        # create instance of tv show using user input
        # If a user has typed a show name that is different from the show that was previously loaded
        if show_name != "" and st.session_state["show_name"] != show_name :
            try:
                with st.spinner(f"Pulling episode data for {show_name}..."):
                    new_show = TvShow(show_name)
                    _ = new_show.season_list
                    _ = new_show.season_episode_dict

                    st.session_state["show"] = new_show
                    st.session_state["show_name"] = show_name
                    st.rerun()
            # If loading a show creates an error, suggests a name that will work 
            # If no suggestion found, tell user could not find a show with that name
            except Exception as e:  
                st.write(e)   
                try:
                    st.write(f" Did you mean {fuzzy_search_result(show_name)}")
                    st.session_state["show"] = ""
                    st.session_state["show_name"] = show_name
                except:
                    st.write("Couldn't find a show with that name")
                    st.session_state["show"] = ""
                    st.session_state["show_name"] = show_name
    # If TV show is loaded properly display picture of TV show and 
    # give user option to watch random episodes or specific ones
    # as well as option to change TV show    
    if ( 
        isinstance(st.session_state["show"], TvShow) 
        and not st.session_state["random_mode"] 
        and not st.session_state["specific_mode"]
    ):    
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Different show?") == True:
                st.session_state["show"] = None
                st.session_state["show_name"] = ""
                st.rerun()
        col1, col2, col3 = st.columns(3)
        with col2:
            st.image(st.session_state["show"].picture)
        col1, col2, col3, col4, col5 = st.columns(5)
        with col2:
            # If Random episodes is selected the UI shifts to allow the user to select information 
            # about what types of episodes they'd like to watch
            if st.button("Random Episodes") == True:
                st.session_state["random_mode"] = True
                st.session_state["specific_mode"] = False
                st.rerun()

        with col4:
            if st.button("Specific Episodes") == True:
                st.session_state["specific_mode"] = True
                st.session_state["random_mode"] = False
                st.rerun()
    # If a Show has been selected and random mode has been chosen
    # present user with paramaters they can use to filter shows
    # as well as option to go choose different mode
    if ( 
        isinstance(st.session_state["show"], TvShow) 
        and st.session_state["random_mode"] 
    ):    
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Change modes") == True:
                st.session_state["random_mode"] = False
                st.rerun()
        with col2:
            if st.button("Change show") == True:
                reset_session_state()
                st.rerun()
        col1, col2, col3 = st.columns([.5, .2, .3])
        with col3:
            st.image(st.session_state["show"].picture) 
        with col1:        
            rating = st.number_input(
                "Lowest rating", min_value=0.0, max_value=10.0, 
                value=st.session_state["rating"],format="%0.1f", 
                help="Type the lowest rated episode you'd watch", step=0.5) 
            seasons = st.multiselect(
                "Seasons", options=st.session_state["show"].season_list, 
                default=st.session_state["seasons"], 
                help="Select seasons to choose from", 
                placeholder="Choose seasons")
        # A list of episodes satisfying the user's requirements is created, 
        # then an episode is chosen from it randomly
        if st.button("Generate episode!") == True:
            try:
                st.session_state["valid_episodes"] = st.session_state["show"].valid_episodes(rating, seasons)
                episode = st.session_state["show"].random_episode(st.session_state["valid_episodes"])
                if isinstance(episode, Episode):
                    st.session_state["episode"] = episode
                    st.session_state["rating"] = rating
                    st.session_state["seasons"] = seasons
                    st.session_state["episode_generated"] = True
                    st.session_state["valid_episodes"].remove(episode)
                    st.rerun()
            except Exception as e:
                st.write("Could not generate any episodes, is your rating too high?")
    # If a Show has been selected and specific mode has been chosen
    # present user with paramaters they can use to filter shows
    # as well as option to go choose different mode
    if ( 
        isinstance(st.session_state["show"], TvShow) 
        and st.session_state["specific_mode"]
    ):  
        col1, col2 = st.columns(2)
        with col1:  
            if st.button("Change modes") == True:
                st.session_state["specific_mode"] = False
                st.rerun()
        with col2:
            if st.button("Change show") == True:
                reset_session_state()
                st.rerun()
        col1, col2 = st.columns(2)
        with col1:    
            season_choice = st.selectbox(
                "What season", 
                options=st.session_state["show"].season_list, 
                help="Select seasons to choose from", 
                placeholder="Choose seasons")
            if st.session_state["season_choice"] != season_choice:
                st.session_state["season_choice"] = season_choice
                st.rerun()
        if st.session_state["season_choice"] != None:
            with col2:
                episode_number = st.selectbox(
                    "What episode", 
                    options=st.session_state["show"].episode_numbers_in_season(st.session_state["season_choice"])
                )
                episode_list = st.session_state["show"].season_episode_dict[st.session_state["season_choice"]]
                episode = [e for e in episode_list if e.number == episode_number][0]
                if st.session_state["episode"] != episode:
                    st.session_state["episode"] = episode
                    st.rerun()
        col3,col4 = st.columns(2)
        with col3:
            st.image(st.session_state["episode"].image)
        with col4:
            st.markdown(f"# {st.session_state["episode"].name}")
            st.markdown(st.session_state["episode"].summary)  

        if st.button("Watch Epiosde!") == True:
            st.session_state["episode_generated"] = True
            st.rerun()
# Once episode is generated, user goes to second screen of app which has a player and some episode info
else:
    # If user is in random mode and has generated their first episode
    # display screen with back button, video, and ability to generate new episodes
    if st.session_state["random_mode"]:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back") == True:
                st.session_state["episode"] = ""
                st.session_state["valid_episodes"] = []
                st.session_state["episode_generated"] = False
                st.session_state["episode_error"] = None
                st.session_state["disabled"] = False
                st.rerun()
            
        with col2:
            if st.button("Change show") == True:
                reset_session_state()
                st.rerun()
        st.markdown(f"# {st.session_state["episode"].name}")
        if "Firefox" in st.session_state["user_agent"]:
            embed_url = st.session_state["episode"].links[st.session_state["server"]]
            
            # 1. We create a unique ID for the iframe
            iframe_id = "ff_player"

            st.markdown(
                f'''
                <div id="video-wrapper" style="width:100%; aspect-ratio: 16/9; background:#000; border-radius:12px; overflow:hidden;">
                    <iframe 
                        id="{iframe_id}"
                        src="{embed_url}" 
                        width="100%" 
                        height="100%" 
                        frameborder="0" 
                        allow="autoplay; encrypted-media; fullscreen"
                        allowfullscreen="true"
                        mozallowfullscreen="true"
                        webkitallowfullscreen="true">
                    </iframe>
                </div>

                <script>
                    // 2. This JS runs in the browser and forces the attributes 
                    // that the Streamlit sanitizer might have stripped.
                    var iframe = parent.document.getElementById("{iframe_id}");
                    if (iframe) {{
                        iframe.setAttribute("allowfullscreen", "true");
                        iframe.setAttribute("mozallowfullscreen", "true");
                        iframe.setAttribute("webkitallowfullscreen", "true");
                        console.log("Fullscreen attributes injected manually.");
                    }}
                </script>
                ''',
                unsafe_allow_html=True
            )
        else:   
          
           
             # Define the URL
            embed_url = st.session_state["episode"].links[st.session_state["server"]]
                # No sandbox in this one bc sandboxes don't work for this player outside of firefox
            st.markdown(
                f'''
                <style>
                    .main-video-wrapper {{
                        width: 100%;
                        max-width: 900px; /* Limits size on large desktop screens */
                        margin: 0 auto;   /* Centers the player */
                    }}
                    .video-container {{
                        position: relative;
                        width: 100%;
                        aspect-ratio: 16 / 9;
                        background-color: #000;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.3); /* Adds a nice "elevated" look on desktop */
                    }}
                    .video-container iframe {{
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        border: none;
                    }}
                </style>
                
                <div class="main-video-wrapper">
                    <div class="video-container">
                        <iframe 
                            src="{embed_url}" 
                            referrerpolicy="origin" 
                            sandbox="allow-forms allow-scripts allow-same-origin"
                            allow="autoplay; fullscreen; encrypted-media" 
                            allowfullscreen>
                        </iframe>
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            ) 
            
# Add list of servers for user to choose from in case link is broken    
        col1, col2 = st.columns([.8,.2])
        with col1:
            st.link_button(
                "If the above player doesn't work, click me",
                embed_url
            )
        with col2:
            server = st.selectbox("Select Server",
                                options=list(st.session_state["episode"].links.keys()),
                                index=list(st.session_state["episode"].links.keys()).index(st.session_state["server"]),
                                key="server_selection",
                                placeholder=st.session_state["server"],
                                on_change=choose_server
                                )
            
        col3, col4 = st.columns([.69, .31])
        with col3:
            st.markdown(f"{st.session_state["episode"].season_and_number}")
            if st.session_state["episode"].rating != 0: 
                st.markdown(f"{st.session_state["episode"].rating}:star:")
        with col4:
            if st.button("Generate another episode!", disabled=st.session_state["disabled"]) == True:
                    try:
                        episode = st.session_state["show"].random_episode(st.session_state["valid_episodes"])
                        if isinstance(episode, Episode):
                            st.session_state["episode"] = episode
                            st.session_state["episode_generated"] = True
                            st.session_state["valid_episodes"].remove(episode)
                            st.rerun()
                    except Exception as e:
                        st.session_state["disabled"] = True
                        st.session_state["episode_error"] = e
                        st.rerun()
                        
        if st.session_state["episode_error"] != None:
            with col4:
                st.write("No more random episodes")
        col5, col6 = st.columns(2)
        col5.image(st.session_state["episode"].image)  
        col6.markdown(st.session_state["episode"].summary)  
    # If user is in specific mode and has chosen their episode,
    # Generate their episode and give them options to keep watching or go back
    if st.session_state["specific_mode"]:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back") == True:
                st.session_state["episode"] = ""
                st.session_state["episode_generated"] = False
                st.session_state["next_episode_error"] = None
                st.session_state["previous_episode_error"] = None
                st.rerun()
        with col2:
            if st.button("Change show") == True:
                reset_session_state()
                st.rerun()
        st.markdown(f"# {st.session_state["episode"].name}")
        st.markdown(f"{st.session_state["episode"].summary}")
        # Send users to either streaming site depending on what browser they are using
        if "Firefox" in st.session_state["user_agent"]:
            # Define the URL
            embed_url = st.session_state["episode"].links[st.session_state["server"]]

            st.markdown(
                f'''
                <style>
                    .main-video-wrapper {{
                        width: 100%;
                        max-width: 900px; /* Limits size on large desktop screens */
                        margin: 0 auto;   /* Centers the player */
                    }}
                    .video-container {{
                        position: relative;
                        width: 100%;
                        aspect-ratio: 16 / 9;
                        background-color: #000;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.3); /* Adds a nice "elevated" look on desktop */
                    }}
                    .video-container iframe {{
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        border: none;
                    }}
                </style>
                
                <div class="main-video-wrapper">
                    <div class="video-container">
                        <iframe 
                            src="{embed_url}" 
                            referrerpolicy="origin" 
                            sandbox="allow-scripts allow-same-origin"
                            allow="autoplay; fullscreen; encrypted-media" 
                            allowfullscreen>
                        </iframe>
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
            
        else:
            # Define the URL
            embed_url = st.session_state["episode"].links[st.session_state["server"]]

            st.markdown(
                f'''
                <style>
                    .main-video-wrapper {{
                        width: 100%;
                        max-width: 900px; /* Limits size on large desktop screens */
                        margin: 0 auto;   /* Centers the player */
                    }}
                    .video-container {{
                        position: relative;
                        width: 100%;
                        aspect-ratio: 16 / 9;
                        background-color: #000;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.3); /* Adds a nice "elevated" look on desktop */
                    }}
                    .video-container iframe {{
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        border: none;
                    }}
                </style>
                
                <div class="main-video-wrapper">
                    <div class="video-container">
                        <iframe 
                            src="{embed_url}" 
                            referrerpolicy="origin" 
                            allow="autoplay; fullscreen; encrypted-media" 
                            allowfullscreen>
                        </iframe>
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )

            
# Add list of servers for user to choose from in case link is broken    
        col1, col2 = st.columns([.8,.2])
        with col1:
            st.link_button(
                "If the above player doesn't work, click me",
                embed_url
            )
        with col2:
            server = st.selectbox("Select Server",
                                options=list(st.session_state["episode"].links.keys()),
                                index=list(st.session_state["episode"].links.keys()).index(st.session_state["server"]),
                                key="server_selection",
                                placeholder=st.session_state["server"],
                                on_change=choose_server
                                )
        col4, col5 = st.columns([.85, .15])
        with col5:
            if st.button("Next Episode") == True:
                    try:
                        episode = st.session_state["show"].next_episode(st.session_state["episode"])
                        if isinstance(episode, Episode):
                            st.session_state["episode"] = episode
                            st.session_state["episode_generated"] = True
                            st.session_state["previous_episode_error"] = None
                            st.rerun()
                    except Exception as e:
                        st.session_state["next_episode_error"] = e
                        st.rerun()
        if st.session_state["next_episode_error"] != None:
            with col5:
                st.write("This is the last episode")
        with col4:
            if st.button("Previous Episode") == True:
                    try:
                        episode = st.session_state["show"].previous_episode(st.session_state["episode"])
                        if isinstance(episode, Episode):
                            st.session_state["episode"] = episode
                            st.session_state["episode_generated"] = True
                            st.session_state["next_episode_error"] = None
                            st.rerun()
                    except Exception as e:
                        st.session_state["previous_episode_error"] = e
                        st.rerun()
        if st.session_state["previous_episode_error"] != None:
            with col4:
                st.write("This is the first episode")
        
            
        

            