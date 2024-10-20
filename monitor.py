# monitor.py

import os
import instaloader
import sqlite3
import datetime
import requests
import logging
from logging.handlers import TimedRotatingFileHandler


def setup_logger():
    logger = logging.getLogger("InstagramMonitor")
    logger.setLevel(logging.INFO)

    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    handler = TimedRotatingFileHandler(
        os.path.join(log_dir, "monitor.log"),
        when="midnight",
        interval=1,
        backupCount=7,  # Keep logs for 7 days
    )
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    handler.suffix = "%Y%m%d"
    logger.addHandler(handler)
    return logger


def send_telegram_message(bot_token, chat_id, message, logger):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        logger.info("Telegram message sent successfully.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Telegram message: {e}")


def main():
    logger = setup_logger()
    logger.info("Starting Instagram Monitor.")

    # Read environment variables
    INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
    INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
    INSTAGRAM_TARGET_ACCOUNT = os.getenv("INSTAGRAM_TARGET_ACCOUNT")
    ENABLE_TELEGRAM_NOTIFICATIONS = (
        os.getenv("ENABLE_TELEGRAM_NOTIFICATIONS", "False").lower() == "true"
    )

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    if not all([INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, INSTAGRAM_TARGET_ACCOUNT]):
        logger.error(
            "Please set environment variables: INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, INSTAGRAM_TARGET_ACCOUNT"
        )
        return

    if ENABLE_TELEGRAM_NOTIFICATIONS and not all(
        [TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]
    ):
        logger.error(
            "Telegram notifications are enabled but TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not set."
        )
        return

    # Initialize Instaloader
    L = instaloader.Instaloader()
    try:
        L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        logger.info("Logged into Instagram successfully.")
    except instaloader.exceptions.BadCredentialsException:
        logger.error("Incorrect Instagram username or password.")
        return
    except Exception as e:
        logger.error(f"Failed to login to Instagram: {e}")
        return

    # Get the target profile
    try:
        profile = instaloader.Profile.from_username(L.context, INSTAGRAM_TARGET_ACCOUNT)
        logger.info(f"Retrieved profile for {INSTAGRAM_TARGET_ACCOUNT}.")
    except Exception as e:
        logger.error(f"Failed to get profile: {e}")
        return

    # Get current followers and followees
    logger.info("Fetching followers and followees...")
    followers = set([follower.username for follower in profile.get_followers()])
    followees = set([followee.username for followee in profile.get_followees()])
    logger.info(f"Fetched {len(followers)} followers and {len(followees)} followees.")

    # Connect to SQLite database
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    db_path = os.path.join(data_dir, f"{INSTAGRAM_TARGET_ACCOUNT}_monitor.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create tables if not exist
    c.execute(
        """CREATE TABLE IF NOT EXISTS followers
                 (username TEXT PRIMARY KEY, last_seen TIMESTAMP)"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS followees
                 (username TEXT PRIMARY KEY, last_seen TIMESTAMP)"""
    )

    # Load previous followers
    c.execute("SELECT username FROM followers")
    previous_followers = set([row[0] for row in c.fetchall()])

    # Detect unfollowers and new followers
    unfollowers = previous_followers - followers
    new_followers = followers - previous_followers

    # Send alerts for unfollowers
    if unfollowers:
        message = f"🚨 {INSTAGRAM_TARGET_ACCOUNT} has lost followers:\n" + "\n".join(
            unfollowers
        )
        logger.info(f"Detected unfollowers: {', '.join(unfollowers)}")
        if ENABLE_TELEGRAM_NOTIFICATIONS:
            send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message, logger)

    # Log new followers
    if new_followers:
        logger.info(f"New followers: {', '.join(new_followers)}")
        if ENABLE_TELEGRAM_NOTIFICATIONS:
            message = f"🎉 {INSTAGRAM_TARGET_ACCOUNT} has new followers:\n" + "\n".join(
                new_followers
            )
            send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message, logger)

    # Update followers table
    c.execute("DELETE FROM followers")
    timestamp = datetime.datetime.now()
    c.executemany(
        "INSERT INTO followers (username, last_seen) VALUES (?, ?)",
        [(username, timestamp) for username in followers],
    )

    # Similarly for followees
    c.execute("SELECT username FROM followees")
    previous_followees = set([row[0] for row in c.fetchall()])

    # Detect new followees and unfollowed accounts
    unfollowed = previous_followees - followees
    new_followees = followees - previous_followees

    # Log unfollowed accounts
    if unfollowed:
        logger.info(f"Unfollowed accounts: {', '.join(unfollowed)}")
        if ENABLE_TELEGRAM_NOTIFICATIONS:
            message = (
                f"🚫 {INSTAGRAM_TARGET_ACCOUNT} has unfollowed accounts:\n"
                + "\n".join(unfollowed)
            )
            send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message, logger)

    # Log new followees
    if new_followees:
        logger.info(f"New followees: {', '.join(new_followees)}")
        if ENABLE_TELEGRAM_NOTIFICATIONS:
            message = (
                f"➕ {INSTAGRAM_TARGET_ACCOUNT} has started following:\n"
                + "\n".join(new_followees)
            )
            send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message, logger)

    # Update followees table
    c.execute("DELETE FROM followees")
    c.executemany(
        "INSERT INTO followees (username, last_seen) VALUES (?, ?)",
        [(username, timestamp) for username in followees],
    )

    # Check for followees who do not follow back
    not_following_back = followees - followers

    # Send message about not following back
    if not_following_back:
        logger.info(f"Accounts not following back: {', '.join(not_following_back)}")
        if ENABLE_TELEGRAM_NOTIFICATIONS:
            message = (
                f"ℹ️ Accounts {INSTAGRAM_TARGET_ACCOUNT} follows who do not follow back:\n"
                + "\n".join(not_following_back)
            )
            send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message, logger)

    # Commit and close
    conn.commit()
    conn.close()
    logger.info("Instagram Monitor completed successfully.")


if __name__ == "__main__":
    main()
