import streamlit as st
from PIL import Image
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from newspaper import Article
import io
import nltk
from backend import add_favorite, get_favorites, delete_favorite, create_user, authenticate_user

nltk.download('punkt')

st.set_page_config(
    page_title='NEWS_BUDDY: A Summarised News📰 Portal',
    page_icon='./Meta/newspaper.ico',
    layout="wide"
)

def resize_image(image, max_width=700):
    width, height = image.size
    aspect_ratio = height / width
    new_width = min(width, max_width)
    new_height = int(new_width * aspect_ratio)
    return image.resize((new_width, new_height))

def fetch_news_poster(poster_link):
    try:
        u = urlopen(poster_link)
        raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
    except Exception:
        image = Image.open('./Meta/no_image.jpg')  
    resized_image = resize_image(image)
    st.image(resized_image, use_container_width=True)

def fetch_news_search_topic(topic):
    site = f'https://news.google.com/rss/search?q={topic}'
    op = urlopen(site)
    rd = op.read()
    op.close()
    sp_page = soup(rd, 'xml')
    news_list = sp_page.find_all('item')
    return news_list

def fetch_top_news():
    site = 'https://news.google.com/news/rss'
    op = urlopen(site)
    rd = op.read()
    op.close()
    sp_page = soup(rd, 'xml')
    news_list = sp_page.find_all('item')
    return news_list

def fetch_category_news(topic):
    site = f'https://news.google.com/news/rss/headlines/section/topic/{topic}'
    op = urlopen(site)
    rd = op.read()
    op.close()
    sp_page = soup(rd, 'xml')
    news_list = sp_page.find_all('item')
    return news_list

def display_news(list_of_news, news_quantity):
    for i, news in enumerate(list_of_news[:news_quantity]):
        st.markdown(f"### {news.title.text}")
        news_data = Article(news.link.text)
        try:
            news_data.download()
            news_data.parse()
            news_data.nlp()
        except:
            st.error("Could not retrieve news content.")
        fetch_news_poster(news_data.top_image)
        with st.expander(f"Summary: {news.title.text}"):
            st.write(news_data.summary)
            st.markdown(f"[Read more]({news.link.text})")
        st.write(f"Published Date: {news.pubDate.text}")
        if st.button(f"💾 Save to Favorites {i}", key=f"save_{i}"):
            add_favorite(news.title.text, news.link.text, news_data.summary, news_data.top_image, news.pubDate.text)
            st.success("News saved!")

def login_page():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate_user(username, password):
            st.success("Logged in successfully!")
            st.session_state['authenticated'] = True
            st.session_state['username'] = username
        else:
            st.error("Invalid username or password")

def signup_page():
    st.subheader("Sign Up")
    new_username = st.text_input("Choose a username")
    new_password = st.text_input("Choose a password", type="password")
    confirm_password = st.text_input("Confirm password", type="password")
    if st.button("Create Account"):
        if new_password == confirm_password:
            create_user(new_username, new_password)
            st.success("Account created successfully! You can now log in.")
        else:
            st.error("Passwords do not match")

def main():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    st.title("NEWS_BUDDY: A Summarised News📰 Portal")
    st.subheader("Get the latest news, customized for your interests.")
    menu = ["Login", "Sign Up"]
    choice = st.sidebar.selectbox("Navigation", menu)
    if not st.session_state['authenticated']:
        if choice == "Login":
            login_page()
        elif choice == "Sign Up":
            signup_page()
    else:
        category = st.sidebar.radio("Select Category", ['🔥 Trending News', '💙 Favorite Topics', '🔍 Search Topic', '📌 Saved News'])
        if category == '🔥 Trending News':
            no_of_news = st.slider('Number of News:', 5, 25, 10)
            news_list = fetch_top_news()
            display_news(news_list, no_of_news)
        elif category == '💙 Favorite Topics':
            av_topics = ['WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE', 'HEALTH']
            chosen_topic = st.sidebar.selectbox("Choose Your Favorite Topic", av_topics)
            no_of_news = st.slider('Number of News:', 5, 25, 10)
            news_list = fetch_category_news(chosen_topic)
            display_news(news_list, no_of_news)
        elif category == '🔍 Search Topic':
            user_topic = st.sidebar.text_input("Enter Your Topic")
            no_of_news = st.slider('Number of News:', 5, 15, 5)
            if st.sidebar.button("🔎 Search"):
                news_list = fetch_news_search_topic(user_topic)
                display_news(news_list, no_of_news)
        elif category == '📌 Saved News':
            st.subheader("Your Saved News")
            saved_news = get_favorites()
            if saved_news:
                for news in saved_news:
                    st.markdown(f"### {news[1]}")
                    st.markdown(f"[Read More]({news[2]})")
                    st.write(f"Published: {news[5]}")
                    if st.button(f"❌ Remove", key=f"del_{news[0]}"):
                        delete_favorite(news[0])
                        st.rerun()
            else:
                st.info("No saved news yet!")
main()
