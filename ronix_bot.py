import requests
import telebot
import math
import time
import os
from datetime import datetime, timedelta

FOOTBALL_API_KEY = os.environ.get('bff317ffe0a746d6abf4208d6ed9731d', '')
TELEGRAM_TOKEN = os.environ.get('8975522188:AAGIQ-Rq8XGLS2xAao6vmOj8aZyc80t6ISs', '')
CHANNEL_ID = '@RONIXpredictions'

# ============================================
# FIFA RANKINGS DATA
# ============================================
FIFA_RANKINGS = {
    'Mexico': {'ranking': 14, 'strength': 78, 'avg_scored': 1.8, 'avg_conceded': 1.1},
    'South Africa': {'ranking': 67, 'strength': 58, 'avg_scored': 1.2, 'avg_conceded': 1.4},
    'South Korea': {'ranking': 23, 'strength': 75, 'avg_scored': 1.9, 'avg_conceded': 1.0},
    'Czechia': {'ranking': 37, 'strength': 68, 'avg_scored': 1.5, 'avg_conceded': 1.2},
    'Canada': {'ranking': 47, 'strength': 65, 'avg_scored': 1.4, 'avg_conceded': 1.3},
    'Bosnia-Herzegovina': {'ranking': 55, 'strength': 62, 'avg_scored': 1.3, 'avg_conceded': 1.4},
    'Germany': {'ranking': 12, 'strength': 80, 'avg_scored': 2.0, 'avg_conceded': 1.0},
    'Japan': {'ranking': 18, 'strength': 76, 'avg_scored': 1.8, 'avg_conceded': 1.1},
    'Spain': {'ranking': 3, 'strength': 88, 'avg_scored': 2.2, 'avg_conceded': 0.8},
    'France': {'ranking': 2, 'strength': 90, 'avg_scored': 2.3, 'avg_conceded': 0.9},
    'Brazil': {'ranking': 5, 'strength': 86, 'avg_scored': 2.1, 'avg_conceded': 0.9},
    'Argentina': {'ranking': 1, 'strength': 92, 'avg_scored': 2.4, 'avg_conceded': 0.8},
    'England': {'ranking': 4, 'strength': 87, 'avg_scored': 2.2, 'avg_conceded': 0.9},
    'Portugal': {'ranking': 6, 'strength': 85, 'avg_scored': 2.0, 'avg_conceded': 1.0},
    'Netherlands': {'ranking': 7, 'strength': 84, 'avg_scored': 1.9, 'avg_conceded': 1.0},
    'Belgium': {'ranking': 8, 'strength': 83, 'avg_scored': 1.9, 'avg_conceded': 1.0},
    'Uruguay': {'ranking': 15, 'strength': 77, 'avg_scored': 1.7, 'avg_conceded': 1.1},
    'Switzerland': {'ranking': 16, 'strength': 76, 'avg_scored': 1.6, 'avg_conceded': 1.1},
    'United States': {'ranking': 13, 'strength': 78, 'avg_scored': 1.7, 'avg_conceded': 1.2},
    'Morocco': {'ranking': 14, 'strength': 77, 'avg_scored': 1.6, 'avg_conceded': 1.1},
    'Senegal': {'ranking': 19, 'strength': 75, 'avg_scored': 1.6, 'avg_conceded': 1.2},
    'Australia': {'ranking': 24, 'strength': 74, 'avg_scored': 1.5, 'avg_conceded': 1.2},
    'Croatia': {'ranking': 10, 'strength': 82, 'avg_scored': 1.8, 'avg_conceded': 1.0},
    'Denmark': {'ranking': 11, 'strength': 81, 'avg_scored': 1.8, 'avg_conceded': 1.0},
    'Colombia': {'ranking': 9, 'strength': 82, 'avg_scored': 1.9, 'avg_conceded': 1.1},
}

# ============================================
# INITIALIZE BOT
# ============================================
bot = telebot.TeleBot(TELEGRAM_TOKEN)
headers = {'X-Auth-Token': FOOTBALL_API_KEY}

# ============================================
# FETCH MATCHES
# ============================================
def get_matches():
    today = datetime.now().strftime('%Y-%m-%d')
    next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    url = f'https://api.football-data.org/v4/matches?dateFrom={today}&dateTo={next_week}'
    response = requests.get(url, headers=headers)
    data = response.json()
    return data.get('matches', [])

# ============================================
# PREDICTION ENGINE
# ============================================
def predict_match(home_team, away_team):
    home = FIFA_RANKINGS.get(home_team)
    away = FIFA_RANKINGS.get(away_team)

    if not home or not away:
        return None

    home_xg = ((home['avg_scored'] + away['avg_conceded']) / 2) * 1.15
    away_xg = (away['avg_scored'] + home['avg_conceded']) / 2
    strength_diff = home['strength'] - away['strength']

    if strength_diff > 15:
        home_prob, draw_prob, away_prob = 65, 20, 15
        confidence = 'High'
    elif strength_diff > 8:
        home_prob, draw_prob, away_prob = 55, 25, 20
        confidence = 'High'
    elif strength_diff > 0:
        home_prob, draw_prob, away_prob = 45, 30, 25
        confidence = 'Medium'
    elif strength_diff > -8:
        home_prob, draw_prob, away_prob = 35, 30, 35
        confidence = 'Medium'
    elif strength_diff > -15:
        home_prob, draw_prob, away_prob = 25, 25, 50
        confidence = 'High'
    else:
        home_prob, draw_prob, away_prob = 15, 20, 65
        confidence = 'High'

    btts_prob = round(min(home_xg * away_xg * 45, 85))
    over25_prob = round(min((home_xg + away_xg) * 28, 85))

    if home_prob > away_prob and home_prob > draw_prob:
        prediction = f'{home_team} Win'
        value_bet = f'🏠 {home_team} Win — Strong Value' if home_prob > 55 else None
    elif away_prob > home_prob and away_prob > draw_prob:
        prediction = f'{away_team} Win'
        value_bet = f'✈️ {away_team} Win — Strong Value' if away_prob > 55 else None
    else:
        prediction = 'Draw'
        value_bet = '🤝 Draw — Value Possible'

    return {
        'prediction': prediction,
        'home_win': home_prob,
        'draw': draw_prob,
        'away_win': away_prob,
        'home_xg': round(home_xg, 2),
        'away_xg': round(away_xg, 2),
        'btts': btts_prob,
        'over25': over25_prob,
        'confidence': confidence,
        'value_bet': value_bet,
        'home_ranking': home['ranking'],
        'away_ranking': away['ranking']
    }

# ============================================
# SEND TO TELEGRAM
# ============================================
def send_to_channel(message):
    bot.send_message(
        chat_id=CHANNEL_ID,
        text=message,
        parse_mode='HTML'
    )
    time.sleep(1)

# ============================================
# MAIN PREDICTION FUNCTION
# ============================================
def run_daily_predictions():
    print(f"🔥 RONIX running at {datetime.now()}")
    
    matches = get_matches()
    
    if not matches:
        print("No matches found today")
        return

    # Send header
    header = """
🔥 <b>RONIX DAILY PREDICTIONS</b> 🔥
━━━━━━━━━━━━━━━━━━━━
📅 {date}
📊 FIFA Rankings + xG Model
━━━━━━━━━━━━━━━━━━━━
""".format(date=datetime.now().strftime('%B %d, %Y'))
    
    send_to_channel(header)

    predictions_made = 0

    for match in matches:
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        match_date = match['utcDate'][:10]
        competition = match['competition']['name']

        pred = predict_match(home_team, away_team)
        if not pred:
            continue

        conf_emoji = '🟢' if pred['confidence'] == 'High' else '🟡' if pred['confidence'] == 'Medium' else '🔴'

        message = """
🏆 <b>{competition}</b>
⚽ <b>{home} vs {away}</b>
📅 {date}
🌍 FIFA: #{home_rank} vs #{away_rank}

🎯 <b>Prediction: {pred}</b>
{conf_emoji} Confidence: {conf}

📊 Win Probabilities:
🏠 {home}: {home_prob}%
🤝 Draw: {draw}%
✈️ {away}: {away_prob}%

⚡ Expected Goals:
🏠 xG: {home_xg} — ✈️ xG: {away_xg}

🎰 Markets:
✅ BTTS: {btts}%
📈 Over 2.5: {over25}%
💰 Value: {value}
━━━━━━━━━━━━━━━━━━━━""".format(
            competition=competition,
            home=home_team,
            away=away_team,
            date=match_date,
            home_rank=pred['home_ranking'],
            away_rank=pred['away_ranking'],
            pred=pred['prediction'],
            conf_emoji=conf_emoji,
            conf=pred['confidence'],
            home_prob=pred['home_win'],
            draw=pred['draw'],
            away_prob=pred['away_win'],
            home_xg=pred['home_xg'],
            away_xg=pred['away_xg'],
            btts=pred['btts'],
            over25=pred['over25'],
            value=pred['value_bet'] or 'No clear value'
        )
        send_to_channel(message)
        predictions_made += 1

    # Send footer
    footer = """
━━━━━━━━━━━━━━━━━━━━
📊 <b>RONIX ACCURACY TRACKER</b>
━━━━━━━━━━━━━━━━━━━━
🤖 <b>RONIX AI v2.0</b>
📲 Share: @RONIXpredictions
🚫 No Numerology. Just Data.
⚠️ Bet responsibly
"""
    send_to_channel(footer)
    print(f"✅ Done! {predictions_made} predictions sent")

# ============================================
# RUN
# ============================================
if __name__ == '__main__':
    run_daily_predictions()
