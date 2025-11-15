from flask import Flask, jsonify
import os
import random
import logging
import tweepy
from apscheduler.schedulers.background import BackgroundScheduler

# ---------------------------------------------------
# Logging setup
# ---------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("tweetbot")

# ---------------------------------------------------
# Environment Variables (Twitter API Keys)
# ---------------------------------------------------
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
    log.error("ERROR: Missing Twitter credentials. Add them in Railway → Variables.")

# ---------------------------------------------------
# Tweet Content
# ---------------------------------------------------
TOPICS = [
    "Politics", "AI", "Technology", "Gaming",
    "Memecoins", "Developer Motivation", "Tech Humor"
]

TOPIC_CONTEXT = {
    "Politics": [
        "Policy changes can reshape everything",
        "Elections are becoming data-driven",
        "Public opinion shifts faster than news cycles",
        "Governments move slower than innovation"
    ],
    "AI": [
        "Models scale, insights scale faster",
        "AI won't take your job—people using AI will",
        "Every model shifts the landscape",
        "Automation is intelligent leverage"
    ],
    "Technology": [
        "Tech evolves in waves, not lines",
        "The future belongs to fast builders",
        "Startups win by experimenting",
        "Long-term impact is underestimated"
    ],
    "Gaming": [
        "Gaming is culture now",
        "Esports is real competition",
        "Game design = psychology + graphics",
        "Gamers understand systems deeply"
    ],
    "Memecoins": [
        "Memecoins run on hype",
        "The funniest coin pumps first",
        "Crypto follows emotion, not logic",
        "Narrative beats tokenomics"
    ],
    "Developer Motivation": [
        "Ship before you're ready",
        "Momentum beats perfection",
        "Small wins compound",
        "Users break everything anyway"
    ],
    "Tech Humor": [
        "If it works, don't touch it",
        "Debugging = crying + fixing",
        "Developers delete more than they write",
        "If code compiles first try—panic"
    ]
}

INSIGHTS = [
    "Small decisions create big outcomes",
    "Momentum beats talent",
    "Curiosity is a multiplier",
    "Simple ideas scale best",
    "Progress feels slow until it isn't",
    "Systems outperform goals"
]

TEMPLATES = [
    "Quick take on {topic}: {context}. {insight}. {hashtag}",
    "{insight}. Especially true in {topic}. {hashtag}",
    "{context}. {insight}. Thoughts? {hashtag}",
    "{insight}. That's the whole story of {topic}. {hashtag}",
    "People forget this about {topic}: {insight}. {hashtag}"
]

HASHTAGS = {
    "Politics": ["#Geopolitics", "#WorldNews", "#PolicyTalk"],
    "AI": ["#AI", "#MachineLearning", "#TechTrends"],
    "Technology": ["#Tech", "#Innovation", "#FutureOfTech"],
    "Gaming": ["#Gaming", "#GamerLife", "#Esports"],
    "Memecoins": ["#Crypto", "#Memecoins", "#Blockchain"],
    "Developer Motivation": ["#DevLife", "#CodeNewbie", "#Motivation"],
    "Tech Humor": ["#TechHumor", "#ProgrammerLife", "#CodingJokes"]
}

# ---------------------------------------------------
# Generate Tweet
# ---------------------------------------------------
def generate_tweet():
    topic = random.choice(TOPICS)
    context = random.choice(TOPIC_CONTEXT[topic])
    insight = random.choice(INSIGHTS)
    template = random.choice(TEMPLATES)
    hashtag = random.choice(HASHTAGS[topic])

    tweet = template.format(
        topic=topic,
        context=context,
        insight=insight,
        hashtag=hashtag
    )

    if len(tweet) > 240:
        tweet = tweet[:230] + "..."

    return tweet

# ---------------------------------------------------
# Post Tweet
# ---------------------------------------------------
def post_tweet():
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
        log.error("Skipping tweet: Missing API credentials")
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

        log.info(f"Tweet Posted: {tweet}")

    except Exception as e:
        log.exception("Tweet failed")

# ---------------------------------------------------
# Scheduler: posts every 8 hours
# ---------------------------------------------------
scheduler = BackgroundScheduler()
scheduler.add_job(post_tweet, "interval", hours=8)
scheduler.start()

# ---------------------------------------------------
# Flask App (keeps Railway alive)
# ---------------------------------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Tweet Bot Running"

@app.route("/health")
def health():
    return jsonify({"ok": True})

@app.route("/post-now")
def post_now():
    post_tweet()
    return jsonify({"posted": True})

# ---------------------------------------------------
# Graceful shutdown
# ---------------------------------------------------
import atexit
@atexit.register
def shutdown():
    scheduler.shutdown(wait=False)

# ---------------------------------------------------
# Correct port handling for Railway
# ---------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
