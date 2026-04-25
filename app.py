import streamlit as st
import pickle

# ----------------------------
# LOAD DATA
# ----------------------------
with open("music_recommender.pkl", "rb") as f:
    data = pickle.load(f)

df = data["df"]
similarity_matrix = data["similarity_matrix"]
EMOTIONAL_ARCS = data["EMOTIONAL_ARCS"]

st.title("🎧 Music Recommender System")

def get_song_index(song_name):
    matches = df[df["track_name"].str.lower() == song_name.lower()]
    if len(matches) == 0:
        return None
    return matches.index[0]

def get_recommendations(song_idx):
    cluster_id = df.loc[song_idx, "cluster"]
    cluster_df = df[df["cluster"] == cluster_id].copy()
    
    cluster_indices = cluster_df.index
    scores = similarity_matrix[song_idx][cluster_indices]
    
    cluster_df["similarity"] = scores
    
    return cluster_df.sort_values("similarity", ascending=False)

def apply_emotional_arc(df_subset, arc_name="chill_to_hype"):
    arc = EMOTIONAL_ARCS[arc_name]
    emotion_rank = {e: i for i, e in enumerate(arc)}
    
    df_subset = df_subset.copy()
    df_subset["emotion_rank"] = df_subset["emotion"].map(
        lambda x: emotion_rank.get(x, len(arc))
    )
    
    return df_subset.sort_values(["emotion_rank", "energy"])

song_name = st.text_input("Enter a song name")

arc_option = st.selectbox(
    "Choose Emotional Arc",
    ["chill_to_hype", "hype_to_chill"]
)

top_n = st.slider("Number of Songs", 5, 20, 10)

if st.button("Generate Playlist"):

    idx = get_song_index(song_name)

    if idx is None:
        st.error("Song not found")
    else:
        recs = get_recommendations(idx)
        recs = apply_emotional_arc(recs, arc_option)

        st.write("### Playlist")
        st.dataframe(recs.head(top_n)[[
            "track_name",
            "track_artist",
            "emotion",
            "track_popularity"
        ]])
