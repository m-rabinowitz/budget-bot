from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# זה הטוקן שאתה שם בפייסבוק
VERIFY_TOKEN = "budget1234"

# תמלא כאן את הטוקנים שלך אחר כך אם צריך - בינתיים הבוט יחזיר תשובה פשוטה
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "")

# --- דפים שפייסבוק דורש כדי לאשר ---
@app.route('/')
def home():
    return 'Budget Bot is running - Privacy at /privacy'

@app.route('/privacy')
def privacy():
    return """
    <html>
    <head><title>Privacy Policy</title></head>
    <body style="font-family:Arial; max-width:700px; margin:40px auto; line-height:1.6;">
        <h1>Privacy Policy - Budget Bot</h1>
        <p><b>What we do:</b> This WhatsApp bot helps users manage monthly budget tracking.</p>
        <p><b>Data collected:</b> Phone number and messages you send to the bot (expenses).</p>
        <p><b>How we use it:</b> Only to calculate and show your budget. We do not share, sell, or transfer your data to third parties.</p>
        <p><b>Storage:</b> Data is stored securely and linked to your phone number only.</p>
        <p><b>Deletion:</b> You can request deletion by sending "delete my data".</p>
        <p><b>Contact:</b> For privacy questions contact the bot owner.</p>
        <p>Effective date: October 2025</p>
    </body>
    </html>
    """

# --- ה-Webhook של וואטסאפ ---
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK VERIFIED!")
        return challenge, 200
    else:
        return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def handle_message():
    data = request.get_json()
    print("Incoming message:", data)

    # לוגיקה בסיסית - מחזיר "היי" בחזרה
    try:
        if data and data.get("object"):
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    if messages:
                        for msg in messages:
                            from_number = msg.get("from")
                            text = msg.get("text", {}).get("body", "")
                            print(f"Message from {from_number}: {text}")
                            
                            # כאן תשלח תשובה חזרה אם יש לך טוקן
                            if WHATSAPP_TOKEN and PHONE_NUMBER_ID and from_number:
                                send_whatsapp_message(from_number, f"קיבלתי: {text} - הבוט שלך עובד! 🎉")
    except Exception as e:
        print("Error:", e)

    return "OK", 200

def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    try:
        r = requests.post(url, headers=headers, json=payload)
        print("Send response:", r.text)
    except Exception as e:
        print("Send error:", e)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
