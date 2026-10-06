from flask import Flask, request
import os
app = Flask(__name__)
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "budget1234")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "")
BUDGET = {"קניות ומזון": {"budget": 3000, "businesses": ["רמי לוי קבוצה", "מענדי", "טלר", "פניני טבע", "שאול תמרוקים"]}, "מגורים וחינוך": {"budget": 4770, "businesses": ["חשמל", "מעון", "ארנונה", "גן אברהם", "ועד לפיד", "מקווה"]}, "רכב ותחבורה": {"budget": 2525, "businesses": ["ביטוח רכב", "דלק", "מוניות", "חניונים ורב קו", "פיקדון טסט"]}, "מעשרות וקודש": {"budget": 2000, "businesses": ["בית חבד לפיד", "שניאור ושיינא סגל", "אסי וטל פישמן", "חבד זמביה", "חבד וינה", "רפאל סלבר", "צארידי"]}, "ביגוד, בריאות וסגנון חיים": {"budget": 1600, "businesses": ["מכנסיים", "עדשות", "נקסט", "כרית להריון", "משקפיים", "יציאות", "אפילוגיק"]}, "שונות": {"budget": 500, "businesses": ["שונות"]}, "תקשורת ומנויים": {"budget": 549, "businesses": ["בזק", "משפחה", "כפר חבד", "רימון", "דבר מלכות", "מיקרוסופט"]}, "ביטוחים": {"budget": 150, "businesses": ["ביטוח חיים"]}}
BUDGET_LIST = list(BUDGET.keys())
users = {}
spent_db = {}
def send_whatsapp(to, text):
    import requests
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    try: requests.post(url, headers=headers, json=data)
    except: pass
@app.route("/")
def home(): return "Bot Running"
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "fail", 403
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        val = data['entry'][0]['changes'][0]['value']
        if 'messages' not in val: return "ok", 200
        msg = val['messages'][0]
        from_num = msg['from']
        text = msg.get('text', {}).get('body','').strip()
        if from_num not in users:
            users[from_num] = {"step":"cat"}
            spent_db[from_num] = {}
        state = users[from_num]
        if text in ["היי","שלום","התחלה","תפריט","hi","menu","0","הי"]:
            state["step"]="cat"
            txt="🛒 *בוט התקציב לפיד* - 15,151₪\nבחר קטגוריה:\n"
            for i,c in enumerate(BUDGET_LIST,1): txt+=f"{i}. {c} ({BUDGET[c]['budget']}₪)\n"
            txt+="\nשלח גם 'יתרה' לדוח"
            send_whatsapp(from_num, txt)
            return "ok",200
        if text in ["יתרה","דוח","מצב"]:
            total_spent = sum(sum(d.values()) for d in spent_db[from_num].values())
            txt=f"📊 *דוח תקציב*\nהוצאת: {total_spent}₪\nנשאר: {15151-total_spent}₪ / 15151₪\n\n"
            for cat in BUDGET_LIST:
                cs = sum(spent_db[from_num].get(cat, {}).values())
                txt+=f"{cat}: {cs}/{BUDGET[cat]['budget']}₪\n"
            send_whatsapp(from_num, txt)
            return "ok",200
        if state["step"]=="cat":
            try:
                cat = BUDGET_LIST[int(text)-1]
                state["cat"]=cat
                state["step"]="biz"
                txt=f"*{cat}* - בחר עסק:\n"
                for i,b in enumerate(BUDGET[cat]["businesses"],1): txt+=f"{i}. {b}\n"
                send_whatsapp(from_num, txt)
            except: send_whatsapp(from_num, "מספר לא תקין, נסה שוב")
        elif state["step"]=="biz":
            try:
                biz = BUDGET[state["cat"]]["businesses"][int(text)-1]
                state["biz"]=biz
                state["step"]="amount"
                send_whatsapp(from_num, f"כמה הוצאת ב-{biz}? שלח סכום, לדוגמה: 87")
            except: send_whatsapp(from_num, "מספר לא תקין")
        elif state["step"]=="amount":
            try:
                amount = float(text.replace("₪",""))
                cat=state["cat"]; biz=state["biz"]
                if cat not in spent_db[from_num]: spent_db[from_num][cat]={}
                spent_db[from_num][cat][biz]=spent_db[from_num][cat].get(biz,0)+amount
                total = sum(sum(d.values()) for d in spent_db[from_num].values())
                send_whatsapp(from_num, f"✅ עודכן {amount}₪ ב-{biz}\nנשאר כללי: {15151-total}₪\nשלח 'תפריט' להמשך")
                state["step"]="cat"
            except: send_whatsapp(from_num, "שלח מספר בלבד, לדוגמה 87")
    except Exception as e: print(e)
    return "ok",200
    if __name__=="__main__":
        
@app.route('/privacy')
def privacy():
    return """
    <h1>Privacy Policy - Budget Bot</h1>
    <p>This WhatsApp bot helps users manage monthly budget.</p>
    <p>We do not share personal data with third parties. Messages are processed only to provide budget tracking.</p>
    <p>Data is stored securely per user phone number and is not sold.</p>
    <p>Contact: budget bot support</p>
    <p>Effective date: October 2025</p>
    """

@app.route('/')
def home():
    return 'Budget Bot is running - Privacy at /privacy'
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
