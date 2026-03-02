import requests
import os
import json

class FeishuClient:
    def __init__(self):
        self.webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
        self.app_id = os.getenv("FEISHU_APP_ID")
        self.app_secret = os.getenv("FEISHU_APP_SECRET")
        # Default receiver type is open_id, can be changed via env
        self.receiver_id_type = os.getenv("FEISHU_RECEIVER_ID_TYPE", "open_id")
        self.receiver_id = os.getenv("FEISHU_RECEIVER_ID")

    def _get_tenant_access_token(self):
        if not self.app_id or not self.app_secret:
            return None
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            res_json = response.json()
            if res_json.get("code") == 0:
                return res_json.get("tenant_access_token")
            else:
                print(f"Error getting Feishu token: {res_json.get('msg')}")
                return None
        except Exception as e:
            print(f"Error getting Feishu token: {e}")
            return None

    def list_chats(self):
        token = self._get_tenant_access_token()
        if not token:
            return None, "Failed to get Feishu access token."

        url = "https://open.feishu.cn/open-apis/im/v1/chats"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        try:
            response = requests.get(url, headers=headers)
            if not response.ok:
                try:
                    error_res = response.json()
                    return None, f"Feishu API Error ({response.status_code}): {error_res.get('msg', response.text)}"
                except:
                    return None, f"Feishu API Error ({response.status_code}): {response.text}"

            result = response.json()
            if result.get("code") != 0:
                return None, f"Feishu API Error: {result.get('msg')}"
            
            return result.get("data", {}).get("items", []), None
        except Exception as e:
            return None, f"Error listing chats: {str(e)}"

    def send_text(self, text):
        # Prefer Custom App API if credentials are set
        if self.app_id and self.app_secret:
            return self._send_api_message("text", {"text": text})
        
        # Fallback to Webhook
        if not self.webhook_url:
            return "Feishu configuration missing (Webhook URL or App ID/Secret)."

        headers = {"Content-Type": "application/json"}
        data = {"msg_type": "text", "content": {"text": text}}
        try:
            response = requests.post(self.webhook_url, headers=headers, json=data)
            response.raise_for_status()
            return "Message sent to Feishu successfully (Webhook)."
        except Exception as e:
            return f"Error sending to Feishu (Webhook): {str(e)}"

    def send_markdown(self, title, content):
        # Prepare card content
        card = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": "blue"
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": content}}
            ]
        }

        # Prefer Custom App API if credentials are set
        if self.app_id and self.app_secret:
            # For API, content must be a JSON string for interactive cards
            # Wait, the structure for API is slightly different: 
            # content: "{\"config\":...}" (stringified JSON)
            return self._send_api_message("interactive", card)
        
        # Fallback to Webhook
        if not self.webhook_url:
            return "Feishu configuration missing (Webhook URL or App ID/Secret)."

        headers = {"Content-Type": "application/json"}
        data = {"msg_type": "interactive", "card": card}
        try:
            response = requests.post(self.webhook_url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            if result.get("code") != 0:
                return f"Feishu API Error: {result.get('msg')}"
            return "Message sent to Feishu successfully (Webhook)."
        except Exception as e:
            return f"Error sending to Feishu (Webhook): {str(e)}"

    def _send_api_message(self, msg_type, content_dict):
        token = self._get_tenant_access_token()
        if not token:
            return "Failed to get Feishu access token."

        if not self.receiver_id:
            return "FEISHU_RECEIVER_ID not set. Cannot send message via Custom App."

        url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={self.receiver_id_type}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # For 'interactive', content needs to be a JSON string of the card
        if msg_type == "interactive":
            content_str = json.dumps(content_dict)
        else:
            # For 'text', content is {"text": "..."}
            content_str = json.dumps(content_dict)
            
        data = {
            "receive_id": self.receiver_id,
            "msg_type": msg_type,
            "content": content_str
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            # Check for HTTP errors but also try to read the response body for API error details
            if not response.ok:
                try:
                    error_res = response.json()
                    return f"Feishu API Error ({response.status_code}): {error_res.get('msg', response.text)}"
                except:
                    return f"Feishu API Error ({response.status_code}): {response.text}"
            
            result = response.json()
            if result.get("code") != 0:
                return f"Feishu API Error: {result.get('msg')}"
            return "Message sent to Feishu successfully (Custom App)."
        except Exception as e:
            return f"Error sending to Feishu (Custom App): {str(e)}"
