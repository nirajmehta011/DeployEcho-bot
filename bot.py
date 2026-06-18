import logging

# Force Python to print all INFO and DEBUG logs to the terminal
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

import os
import re

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)

BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

if not BOT_TOKEN:
    raise EnvironmentError(
        "SLACK_BOT_TOKEN is required. Add it to .env or export it in your shell."
    )

if not APP_TOKEN:
    raise EnvironmentError(
        "SLACK_APP_TOKEN is required. Add it to .env or export it in your shell."
    )

DEPLOYMENT_CHANNEL = os.getenv("DEPLOYMENT_CHANNEL")
AUTOMATION_CHANNEL = os.getenv("AUTOMATION_CHANNEL")

app = App(token=BOT_TOKEN)
@app.middleware
def log_everything(logger, body, next):
    # This will catch absolutely every event Slack sends to your app
    event_type = body.get("event", {}).get("type", "unknown")
    event_subtype = body.get("event", {}).get("subtype", "none")
    
    logger.info(f"GLOBAL INTERCEPTOR Caught -> Type: {event_type} | Subtype: {event_subtype}")
    
    # Pass the request down the chain to your other functions
    return next()


def extract_environment(text):
    """
    Extract: Environment: digital-cloud-us-prem
    Handles Slack markdown like *Environment*:
    """
    # Clean up Slack's bold markdown before processing
    clean_text = text.replace('*', '')
    
    match = re.search(
        r"Environment:\s*([A-Za-z0-9\-_]+)",
        clean_text,
        re.IGNORECASE
    )
    
    if match:
        return match.group(1).strip()
    
    return None


def extract_all_text_from_message(msg):
    """
    Helper to extract text from both plain text and blocks layout
    to handle emojis, markdown, and rich formatting securely.
    """
    text_pieces = [msg.get("text", "")]
    
    # If Slack formatted it using layout blocks, extract text from them too
    if "blocks" in msg:
        for block in msg["blocks"]:
            if "elements" in block:
                for element in block["elements"]:
                    if "elements" in element:
                        for sub_element in element["elements"]:
                            if sub_element.get("type") == "text":
                                text_pieces.append(sub_element.get("text", ""))
    
    return " ".join(text_pieces)


def find_thread_for_environment(client, environment):
    """
    Search deployment channel for matching environment
    """
    result = client.conversations_history(
        channel=DEPLOYMENT_CHANNEL,
        limit=100
    )

    for msg in result["messages"]:
        # Extract exhaustive text content from the historical message
        combined_text = extract_all_text_from_message(msg)

        # Case-insensitive check to ensure variations in typing don't break it
        if environment.lower() in combined_text.lower():
            return msg["ts"]

    return None


@app.event("message")
def handle_message(body, client, logger):
    event = body["event"]

    # ADD THIS LINE RIGHT HERE:
    logger.info(f"RAW EVENT DATA: {event}")

    if event.get("channel") != AUTOMATION_CHANNEL:
        return

    if event.get("bot_id"):
       return

    text = event.get("text", "")
    logger.info(f"Received:\n{text}")

    environment = extract_environment(text)

    if not environment:
        logger.info("No environment found")
        return

    logger.info(f"Environment={environment}")

    thread_ts = find_thread_for_environment(client, environment)

    if not thread_ts:
        logger.info(f"No deployment thread found for {environment}")
        return

    client.chat_postMessage(
        channel=DEPLOYMENT_CHANNEL,
        thread_ts=thread_ts,
        text=f"Automation Result:\n\n{text}"
    )

    logger.info(f"Posted to thread {thread_ts}")


if __name__ == "__main__":
    SocketModeHandler(app, APP_TOKEN).start()