import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.feishu_client import FeishuClient

def main():
    print("Fetching Feishu chats...")
    client = FeishuClient()
    
    if not client.app_id or not client.app_secret:
        print("Error: FEISHU_APP_ID or FEISHU_APP_SECRET not set.")
        return

    chats, error = client.list_chats()
    
    if error:
        print(f"Error: {error}")
        print("\nNote: To list chats, your Feishu App needs the 'im:chat:list' (Obtain group information) permission.")
        print("Please check your Feishu Developer Console -> Permissions & Scopes.")
        return

    if not chats:
        print("No chats found. Is the bot added to any groups?")
        return

    print(f"\nFound {len(chats)} chats:")
    print("-" * 50)
    for chat in chats:
        print(f"Name: {chat.get('name', 'Unnamed')}")
        print(f"Chat ID: {chat.get('chat_id')}")
        print(f"Description: {chat.get('description', 'No description')}")
        print("-" * 50)

if __name__ == "__main__":
    main()
