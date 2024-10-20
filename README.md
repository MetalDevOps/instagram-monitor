# Instagram Follower Monitor

An application to monitor the followers and followees of an Instagram account using the `instaloader` library. It tracks changes in followers and followees, detects unfollowers, new followers, unfollowed accounts, and accounts that do not follow back. The application can send notifications via Telegram and runs inside a Docker container for easy deployment.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Set Up Environment Variables](#2-set-up-environment-variables)
  - [3. (Optional) Set Up Telegram Bot](#3-optional-set-up-telegram-bot)
  - [4. Build and Run the Docker Container](#4-build-and-run-the-docker-container)
  - [5. Schedule Periodic Monitoring (Optional)](#5-schedule-periodic-monitoring-optional)
- [Usage](#usage)
- [Logs](#logs)
- [Data Persistence](#data-persistence)
- [Configuration](#configuration)
- [Notes](#notes)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Monitor Followers and Followees**: Tracks changes in followers and followees of a specified Instagram account.
- **Detect Unfollowers and New Followers**: Logs accounts that have unfollowed or started following since the last check.
- **Detect Unfollowed Accounts and New Followees**: Logs accounts that have been unfollowed or newly followed.
- **Check for Non-Followbacks**: Identifies accounts you follow that do not follow back.
- **Telegram Notifications**: Sends alerts via Telegram (can be enabled or disabled).
- **Logging with Rotation**: Logs activities with date rotation, keeping logs for the last 7 days.
- **Dockerized Application**: Runs inside a Docker container for consistent deployment.
- **Data Persistence**: Uses SQLite database to store data between runs.

---

## Prerequisites

- **Docker** and **Docker Compose** installed on your machine.
- An **Instagram account** to log in and monitor another account (must be able to view the target account's followers).
- (Optional) A **Telegram account** and a **Telegram bot token** for notifications.

---

## Project Structure

```
instagram-monitor/
├── monitor.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── data/
└── logs/
```

- **monitor.py**: The main application script.
- **requirements.txt**: Python dependencies.
- **Dockerfile**: Docker configuration for building the container.
- **docker-compose.yml**: Docker Compose file for setting up services.
- **.env**: Environment variables for configuration.
- **data/**: Directory for the SQLite database (persistent data).
- **logs/**: Directory for log files with date rotation.

---

## Setup Instructions

### 1. Clone the Repository

Clone the repository or create a directory called `instagram-monitor` and place all the files inside it.

```bash
git clone https://github.com/MetalDevOps/instagram-monitor.git
cd instagram-monitor
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root directory and add your credentials:

```dotenv
# Instagram Credentials
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password_with_special_chars
INSTAGRAM_TARGET_ACCOUNT=account_to_monitor

# Telegram Notifications
ENABLE_TELEGRAM_NOTIFICATIONS=True  # Set to 'False' to disable
TELEGRAM_BOT_TOKEN=your_telegram_bot_token  # Optional if notifications are disabled
TELEGRAM_CHAT_ID=your_telegram_chat_id      # Optional if notifications are disabled
```

**Important:**

- Replace the placeholders with your actual credentials.
- Ensure that your password is entered exactly as it is, including any special characters.
- Keep the `.env` file secure and do not commit it to any public repositories.

### 3. (Optional) Set Up Telegram Bot

If you wish to receive notifications via Telegram:

1. **Create a Telegram Bot:**
   - Open Telegram and search for `@BotFather`.
   - Start a conversation and send `/newbot` to create a new bot.
   - Follow the instructions to get your **Telegram Bot Token**.

2. **Get Your Telegram Chat ID:**
   - Start a conversation with your new bot by searching for its username and sending a message.
   - Access the following URL in your browser, replacing `<YourBOTToken>` with your bot token:

     ```
     https://api.telegram.org/bot<YourBOTToken>/getUpdates
     ```

   - Look for the `"chat":{"id":<YourChatID>}` field in the JSON response to find your **Telegram Chat ID**.

3. **Enable Notifications:**
   - Set `ENABLE_TELEGRAM_NOTIFICATIONS=True` in your `.env` file.
   - Add your `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` to the `.env` file.

### 4. Build and Run the Docker Container

In the project root directory, run the following command to build and start the container:

```bash
docker-compose up --build
```

- The application will start and log its activities.
- Logs are stored in the `logs/` directory.

### 5. Schedule Periodic Monitoring (Optional)

To run the monitoring periodically, you can use `cron` or any task scheduler.

**Example using `cron` to run every hour:**

1. Open the crontab editor:

   ```bash
   crontab -e
   ```

2. Add the following line, replacing `/path/to/instagram-monitor` with the actual path to your project directory:

   ```cron
   0 * * * * cd /path/to/instagram-monitor && docker-compose run --rm instagram-monitor
   ```

---

## Usage

- **Monitor a Different Account:** Set the `INSTAGRAM_TARGET_ACCOUNT` in the `.env` file to the username of the account you wish to monitor.
- **Enable/Disable Telegram Notifications:** Set `ENABLE_TELEGRAM_NOTIFICATIONS` to `True` or `False` in the `.env` file.
- **View Logs:** Check the `logs/` directory for detailed logs of the application's activities.
- **Data Storage:** The application uses a SQLite database stored in the `data/` directory to keep track of followers and followees between runs.

---

## Logs

- **Location:** Logs are stored in the `logs/` directory.
- **Log Rotation:** The application uses a `TimedRotatingFileHandler` to rotate logs daily, keeping logs for the last 7 days.
- **Log Content:** Includes timestamps, log levels, and messages detailing the application's operations and any detected changes.

---

## Data Persistence

- **SQLite Database:** The application uses a SQLite database to store followers and followees between runs.
- **Data Directory:** The database files are stored in the `data/` directory, which is mounted as a volume in the Docker container.
- **Database Naming:** The database file is named based on the `INSTAGRAM_TARGET_ACCOUNT` to allow for monitoring multiple accounts if needed.

---

## Configuration

### Environment Variables

All configurations are managed via environment variables in the `.env` file.

- **Instagram Credentials:**
  - `INSTAGRAM_USERNAME`: Your Instagram username used to log in.
  - `INSTAGRAM_PASSWORD`: Your Instagram password.
  - `INSTAGRAM_TARGET_ACCOUNT`: The Instagram account to monitor (can be different from the login account).

- **Telegram Notifications:**
  - `ENABLE_TELEGRAM_NOTIFICATIONS`: Set to `True` to enable notifications, `False` to disable.
  - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token (required if notifications are enabled).
  - `TELEGRAM_CHAT_ID`: Your Telegram chat ID (required if notifications are enabled).

---

## Notes

- **Privacy and Security:**
  - Keep your `.env` file secure and avoid sharing it.
  - Be cautious when monitoring third-party accounts; ensure you have permission if required.

- **Instagram Rate Limits:**
  - Be aware of Instagram's rate limits to avoid temporary bans.
  - It's recommended to schedule the script to run at reasonable intervals (e.g., once an hour).

- **Error Handling:**
  - The application includes basic error handling and logs errors to help diagnose issues.

- **Extensibility:**
  - The script can be extended to monitor multiple accounts by adjusting the code and configurations.

---

## Dependencies

- **Python 3.9+**
- **Docker and Docker Compose**
- **Python Libraries:**
  - `instaloader`
  - `requests`
  - `logging` (standard library)
  - `sqlite3` (standard library)

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. Commit your changes:

   ```bash
   git commit -m "Add your message"
   ```

4. Push to the branch:

   ```bash
   git push origin feature/your-feature-name
   ```

5. Open a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

**Disclaimer:** This application is intended for personal use. Ensure you comply with Instagram's terms of service and any applicable laws and regulations.

---
