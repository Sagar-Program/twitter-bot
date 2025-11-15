from flask import Flask, jsonify
import os, random, logging
import tweepy
from apscheduler.schedulers.background import BackgroundScheduler

# -----------------------------------------
# Logging (helps detect errors)
# -----------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("tweetbot")

# -----------------------------------------
# Load Twitter credentials from Replit Secrets
# -----------------------------------------
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
    log.error("One or more Twitter API secrets are missing.")

# -----------------------------------------
# Tweet content configuration
# -----------------------------------------
TOPICS = [
    "Politics","AI","Technology","Gaming","Memecoins","Developer Motivation","Tech Humor"
]

TOPIC_CONTEXT = {
    "Politics": ["Policy shifts reshape everything","Elections are becoming data-driven","Public opinion changes faster than news cycles","Governments move slower than innovation"],
    "AI": ["Models scale, insights scale faster","AI isn't taking jobs, but people who use it will","Every new model shifts the entire ecosystem","Automation is intelligence applied correctly"],
    "Technology": ["Tech evolves in waves, not lines","The future belongs to whoever ships fastest","Startups win by experimenting relentlessly","We underestimate long-term impact"],
    "Gaming": ["Gaming is culture now","Esports mirrors real sports","Game design is psychology with graphics","Gamers understand systems deeply"],
    "Memecoins": ["Memecoins run on hype, not fundamentals","The funniest coin always pumps first","Crypto follows emotions, not logic","Narrative beats tokenomics"],
    "Developer Motivation": ["Ship even when you're not ready","Momentum beats perfection","Small wins build progress","Users break everything anyway"],
    "Tech Humor": ["If it works, don’t touch it","Debugging = pain + learning","Developers: writing, deleting, crying","If code compiles first try, panic"]
}

INSIGHTS = [
    "Momentum beats talent",
    "Curiosity is a superpower",
    "Simple ideas scale best",
    "Small decisions create big outcomes",
    "The future rewards adaptable people",
    "Systems outperform motivation",
]

TEMPLATES = [
    "Quick take on {topic}: {context}. {insight}. {hashtag}",
    "{insight}. Especially true in {topic}. {hashtag}",
    "{context}. {insight}. Thoughts? {hashtag}",
    "{insight}. That's the whole story of {topic}. {hashtag}",
    "People forget this about {topic}: {insight}. {hashtag}",
]

HASHTAGS = {
    "Politics": ["#Geopolitics","#WorldNews","#PolicyTalk"],
    "AI": ["#AI","#MachineLearning","#TechTrends"],
    "Technology": ["#Tech","#Innovation","#FutureOfTech"],
    "Gaming": ["#Gaming","#GamerLife","#Esports"],
    "Memecoins": ["#Crypto","#Memecoins","#Blockchain"],
    "Developer Motivation": ["#DevLife","#CodeNewbie","#Motivation"],
    "Tech Humor": ["#TechHumor","#ProgrammerLife","#CodingJokes"]
}

# -----------------------------------------
# Tweet generator
# -----------------------------------------
def generate_tweet():
    topic = random.choice(TOPICS)
    context = random.choice(TOPIC_CONTEXT[topic])
    insight = random.choice(INSIGHTS)
    template = random.choice(TEMPLATES)
    hashtag = random.choice(HASHTAGS[topic])

    tweet = template.format(topic=topic, context=context, insight=insight, hashtag=hashtag)

    if len(tweet) > 240:
        tweet = tweet[:230] + "..."

    return tweet

# -----------------------------------------
# Post tweet
# -----------------------------------------
def post_tweet():
    """Post one tweet. Scheduler calls this every 8 hours."""
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
        log.error("Missing credentials. Cannot post.")
        return

    try:
        client = tweepy.Client(
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            access_token_secret=ACCESS_SECRET,
            wait_on_rate_limit=True
        )

        tweet = generate_tweet()
        client.create_tweet(text=tweet)
        log.info(f"Posted: {tweet}")

    except Exception as e:
        log.exception("Error posting tweet")

# -----------------------------------------
# Scheduler (THIS fixes your 24h problem)
# -----------------------------------------
scheduler = BackgroundScheduler()
scheduler.add_job(post_tweet, "interval", hours=8)  # every 8 hours
scheduler.start()

# -----------------------------------------
# Flask App (keeps Replit alive)
# -----------------------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Advanced Tweet Bot Running"

@app.route("/health")
def health():
    return jsonify({"ok": True})

@app.route("/post-now")
def post_now():
    post_tweet()
    return jsonify({"posted": True})

# Clean shutdown
import atexit
@atexit.register
def shutdown():
    scheduler.shutdown(wait=False)

# -----------------------------------------
# Run server on correct port (Replit requirement)
# -----------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
