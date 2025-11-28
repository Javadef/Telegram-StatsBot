import asyncio
import os # Added for environment variables
from dotenv import load_dotenv # Added for loading .env file

from pyrogram import Client
from pyrogram.errors import RPCError
from pyrogram import filters 
from pyrogram.enums import ChatType 
from pyrogram.raw import functions

# --- CONFIGURATION (LOADED FROM .ENV) ---
# 1. Load environment variables from the .env file
# Ensure the path matches the config file name
load_dotenv(dotenv_path='.env') 
# 2. Retrieve variables using os.getenv() and handle potential NoneType errors
# Helper function to get required config and raise an error if missing
def get_required_env(key):
    value = os.getenv(key)
    if value is None:
        # Raise a specific error instead of relying on default values or crashing on int()
        raise ValueError(
            f"Configuration error: The '{key}' environment variable is missing. "
            "Please ensure it is set in your 'config.env' file and the script is loading it correctly."
        )
    return value

try:
    # API_ID must be an integer
    API_ID_STR = get_required_env("API_ID")
    API_ID = int(API_ID_STR)
    
    # Other variables are strings
    API_HASH = get_required_env("API_HASH")
    SESSION_NAME = get_required_env("SESSION_NAME")
    CHANNEL_IDENTIFIER = get_required_env("CHANNEL_IDENTIFIER")
except ValueError as e:
    # Print the specific configuration error and re-raise to stop execution
    print(f"❌ FATAL CONFIGURATION ERROR: {e}")
    raise   

# --- SAFE ACCESS HELPER ---
def get_message_replies_count(message):
    # This helper is now deprecated in favor of the dedicated API method below,
    # but we keep it safe access for completeness if the property is unexpectedly set.
    replies_obj = getattr(message, "replies", None)
    return getattr(replies_obj, "total_count", 0)

# --- CORE METRICS FETCH FUNCTION ---
async def fetch_message_metrics():
    # Use Pyrogram's Client to handle the session
    async with Client(
        SESSION_NAME, 
        api_id=API_ID, 
        api_hash=API_HASH
    ) as client:
        try:
            print(f"✅ Client started.")
            
            # 1. Get Chat Info and the Last Message
            chat_info = await client.get_chat(CHANNEL_IDENTIFIER)
            
            # 2. Get the last message ID
            last_message_iterator = client.get_chat_history(CHANNEL_IDENTIFIER, limit=1)
            
            last_message_list = []
            async for msg in last_message_iterator:
                last_message_list.append(msg)
            
            if not last_message_list:
                print("❌ Error: No messages found in the channel.")
                return

            last_message = last_message_list[0]
            last_msg_id = last_message.id
            last_message_date = last_message.date.strftime('%Y-%m-%d %H:%M:%S')

            print(f"🔄 Fetching full details for Message ID: {last_msg_id}...")
            
            # Fetch the full message object
            full_messages = await client.get_messages(CHANNEL_IDENTIFIER, message_ids=[last_msg_id])
            full_message = full_messages[0]
            
            # Generate Post Link
            channel_username = chat_info.username
            if channel_username:
                post_link = f"https://t.me/{channel_username}/{full_message.id}"
            else:
                post_link = "N/A (Channel is private or uses a link)"
            
            print(f"\n--- Metrics for Message ID: {full_message.id} (Date: {last_message_date}) ---")
            print(f"🔗 **Post Link:** {post_link}")
            
            # --- VIEWS ---
            # Pyrogram uses .views
            views = full_message.views or 0
            print(f"👀 Views: {views}")
            
            # --- FORWARDS ---
            # Pyrogram uses .forwards
            forwards = full_message.forwards or 0
            print(f"➡️ **Forwards:** {forwards}")

            # --- REACTIONS ---
            # Pyrogram uses .reactions (Reactions can sometimes be zero if the user bot session 
            # doesn't have the necessary updates or permissions. For full reliability, 
            # the raw API call in the previous version was better, but we stick to high-level here.)
            total_reacts = 0
            if full_message.reactions and full_message.reactions.reactions:
                total_reacts = sum(r.count for r in full_message.reactions.reactions)
            
            print(f"🔥 Reactions: {total_reacts}")
                
            # --- REPLIES (FIXED) ---
            # To get the reliable replies count, we use the dedicated method 
            # get_discussion_replies_count, which checks the linked discussion group.
            try:
                # The chat_info object will contain the ID of the linked discussion chat (if any)
                # However, get_discussion_replies_count() can handle the channel ID directly.
                total_discussion_replies = await client.get_discussion_replies_count(
                    chat_id=CHANNEL_IDENTIFIER,
                    message_id=full_message.id
                )
                print(f"💬 **Replies (FIXED):** {total_discussion_replies}")
            except Exception as e:
                # This error often occurs if the channel does not have a linked discussion group
                # or the bot/user session cannot access it.
                print(f"⚠️ Could not fetch discussion replies count: {e}. Falling back to property check.")
                # Fallback to the potentially unreliable property check
                total_channel_replies = get_message_replies_count(full_message)
                print(f"💬 Replies (Property Fallback): {total_channel_replies}")


        except RPCError as e:
            print(f"❌ Pyrogram RPC Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Global Error: {e}")

        finally:
            print("\n--- Finished ---")

if __name__ == "__main__":
    asyncio.run(fetch_message_metrics())