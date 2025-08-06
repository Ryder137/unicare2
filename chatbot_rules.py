# Simple rule-based chatbot logic for UNICARE

import difflib

def fuzzy_in(msg, keywords, cutoff=0.8):
    # Returns True if msg is similar to any keyword
    return any(difflib.SequenceMatcher(None, msg, kw).ratio() >= cutoff or kw in msg for kw in keywords)

def get_bot_response(message, last_topic=None, user_facts=None):
    """Return a canned or rule-based response for the chatbot, with context, session memory, and richer dialogue."""
    msg = message.lower().strip()
    if user_facts is None:
        user_facts = {}
    # --- Extract user facts from input ---
    import re
    # List of common moods to avoid as names
    mood_words = ["sad", "happy", "tired", "stressed", "anxious", "okay", "fine", "good", "bad", "lonely", "angry", "excited", "bored", "upset", "worried", "depressed", "energetic", "calm", "relaxed", "scared", "afraid", "confused", "hopeful", "grateful"]
    # Extract name from various patterns
    name_match = re.search(r"(?:my name is|i\s*['’`]?m|im|hi[ ,!]*i['’`]?m)\s+([a-zA-Z\u00C0-\u017F ]+)", message, re.I)
    if name_match:
        possible_name = name_match.group(1).strip().split()[0].capitalize()
        if possible_name.lower() not in mood_words:
            user_facts['name'] = possible_name
        else:
            user_facts['mood'] = possible_name.lower()
    # Support "I'm feeling [mood]"
    mood_match = re.search(r"i(?:'m| am)? feeling ([a-zA-Z\u00C0-\u017F ]+)", message, re.I)
    if mood_match:
        user_facts['mood'] = mood_match.group(1).strip().split()[0].lower()
    # Also support "I feel [mood]"
    mood_match2 = re.search(r"i feel ([a-zA-Z\u00C0-\u017F ]+)", message, re.I)
    if mood_match2:
        user_facts['mood'] = mood_match2.group(1).strip().split()[0].lower()
    like_match = re.search(r"i like ([a-zA-Z\u00C0-\u017F ]+)", message, re.I)
    if like_match:
        user_facts['favorite'] = like_match.group(1).strip()
    # Track previous moods and favorites for session memory
    if 'mood' in user_facts:
        prev_moods = user_facts.get('mood_history', [])
        if not prev_moods or user_facts['mood'] != prev_moods[-1]:
            user_facts.setdefault('mood_history', []).append(user_facts['mood'])
    if 'favorite' in user_facts:
        prev_favs = user_facts.get('favorite_history', [])
        if not prev_favs or user_facts['favorite'] != prev_favs[-1]:
            user_facts.setdefault('favorite_history', []).append(user_facts['favorite'])
    # If user is logged in, set persist_facts flag for DB saving (hook for future)
    persist_facts = user_facts.get('user_id') is not None
    # Tagalog keyword detection
    tagalog_greetings = ["kumusta", "kamusta", "magandang araw", "hello po", "hi po"]
    tagalog_sad = ["malungkot", "lungkot", "iyak", "umiiyak", "masama ang loob"]
    tagalog_happy = ["masaya", "okay lang", "mabuti", "maganda ang pakiramdam"]
    tagalog_stress = ["stress", "pagod", "nai-stress", "naiinip", "anxious", "kabado"]
    tagalog_activity = ["laro", "gusto ko maglaro", "anong activity", "suggestion", "ano gagawin"]
    tagalog_help = ["tulong", "kailangan ko ng tulong", "tulungan mo ako", "sino pwede kausapin"]
    tagalog_bye = ["paalam", "goodbye", "aalis na ako"]
    tagalog_tip = ["tip", "payo", "advice"]

    # Detect urgent help/crisis phrases
    crisis_keywords = [
        "hopeless", "helpless", "worthless", "can't go on", "end it", "kill myself", "suicide", "hurt myself", "alone", "no one cares", "give up", "crisis", "emergency", "need help", "help me", "can't take it", "overwhelmed",
        # Tagalog crisis
        "wala ng pag-asa", "ayoko na", "magpakamatay", "nasasaktan ako", "nag-iisa", "walang nagmamalasakit", "suko na", "krisis", "emergency", "kailangan ng tulong", "tulungan mo ako", "hindi ko na kaya"
    ]
    if fuzzy_in(msg, crisis_keywords, cutoff=0.7):
        return (
            "Malungkot akong marinig na ganito ang nararamdaman mo. Hindi ka nag-iisa—may mga tao na handang tumulong at makinig sa'yo.<br>"
            "<b>Narito ang mga mental health hotlines na maaari mong tawagan 24/7:</b><br>"
            "<b>National Center for Mental Health (NCMH) Crisis Hotlines:</b><br>"
            "&bull; Landline: 1553 (toll-free nationwide)<br>"
            "&bull; Globe/TM: 0966-351-4518, 0917-899-8727<br>"
            "&bull; Smart/Sun/TNT: 0908-639-2672<br>"
            "<b>In Touch Community Services:</b><br>"
            "&bull; Landline: (02) 8893-7603<br>"
            "&bull; Globe: 0917-800-1123<br>"
            "&bull; Sun: 0922-893-8944<br>"
            "<b>NGF HOPELINE PH:</b><br>"
            "&bull; 2919 (Globe/TM, toll-free)<br>"
            "&bull; Globe: 0917-558-4673<br>"
            "&bull; Smart: 0918-873-4673<br>"
            "&bull; Landline: (02) 8804-4673<br>"
            "<b>Tawag Paglaum – Centro Bisaya:</b><br>"
            "&bull; Smart/Sun: 0939-9375433 / 0939-9365433<br>"
            "&bull; Globe/TM: 0927-6541629<br>"
            "<b>Philippine Mental Health Association, Inc. (PMHA):</b><br>"
            "&bull; (02) 8921-4958 / (02) 8921-4959 (7am-4pm, Mon-Fri)<br>"
            "&bull; Text: 0917-565-2036<br>"
            "&bull; Email: pmhacds@gmail.com<br>"
            "<b>Manila Lifeline Centre (MLC):</b><br>"
            "&bull; Landline: (02) 896-9191<br>"
            "&bull; Globe: 0917-854-9191<br>"
            "<b>General Emergency Hotline:</b><br>"
            "&bull; 911 (for immediate and severe emergencies)<br>"
            "Hindi ka nag-iisa. Maaari kang tumawag sa alinman sa mga numerong ito para sa agarang suporta."
        )
    vague_yes = ["yes", "oo", "sige", "sure", "okay", "ok", "opo"]
    vague_no = ["no", "hindi", "ayoko", "not now"]
    vague_more = ["more", "pa", "another", "iba pa", "next", "more info"]
    vague_how = ["how", "paano", "how to", "paano ba"]

    # CONTEXTUAL CONTINUATION
    if fuzzy_in(msg, vague_yes, 0.7) and last_topic == "activity":
        name = user_facts.get('name')
        fav = user_facts.get('favorite')
        reply = f"Great{' ' + name if name else ''}! You can try our games, breathing exercises, or gratitude journal."
        if fav:
            reply += f" Since you like {fav}, you might enjoy listening to music while doing an activity."
        reply += " Would you like a link to the games or another activity?"
        return (reply, "activity", user_facts)
    if fuzzy_in(msg, vague_yes, 0.7) and last_topic == "sad":
        name = user_facts.get('name')
        mood_hist = user_facts.get('mood_history', [])
        reply = f"I'm here to listen{name+', ' if name else ''}you can share your feelings or try a mood-boosting activity."
        if mood_hist and len(mood_hist) > 1:
            reply += f" I remember earlier you mentioned feeling {mood_hist[-2]}."
        reply += " Would you like a suggestion?"
        return (reply, "sad", user_facts)
    # If user says 'more' or 'really?' and last topic is emotional/support, continue with more empathy/tips
    if (fuzzy_in(msg, vague_more, 0.7) or fuzzy_in(msg, ["really?"], 0.7)) and last_topic in ["tip", "sad", "stress", "activity"]:
        if last_topic == "tip":
            reply = "Here's another tip: Take a short break and focus on your breathing. Would you like more tips or an activity?"
            return (reply, "tip", user_facts)
        if last_topic == "sad":
            reply = "It's okay to feel sad sometimes. If you'd like, you can share more about what's making you feel this way, or I can suggest an activity to help lift your mood. Would you like a suggestion or to talk more?"
            return (reply, "sad", user_facts)
        if last_topic == "stress":
            reply = "Stress can be tough. Some people find it helpful to take deep breaths, talk to someone, or do something they enjoy. Would you like a breathing exercise or another tip?"
            return (reply, "stress", user_facts)
        if last_topic == "activity":
            reply = "Here are more things you can try: write in a gratitude journal, play a quick game, or listen to your favorite music. Would you like a link to the games or another activity?"
            return (reply, "activity", user_facts)
    if fuzzy_in(msg, vague_how, 0.7) and last_topic == "activity":
        reply = "You can access activities in the Games or Wellness Tools section above, or I can send you a direct link. Which would you like?"
        return (reply, "activity", user_facts)
    if not msg:
        name = user_facts.get('name')
        reply = f"I'm here to help{name+', ' if name else ''}how are you feeling today?"
        return (reply, None, user_facts)
    # Tagalog responses
    if fuzzy_in(msg, tagalog_greetings, 0.7):
        name = user_facts.get('name')
        reply = f"Kumusta{' ' + name if name else ''}! Paano kita matutulungan ngayon?"
        return (reply, "greetings", user_facts)
    if fuzzy_in(msg, tagalog_sad, 0.7):
        name = user_facts.get('name')
        reply = f"Nakakalungkot marinig na malungkot ka{name and ', ' + name or ''}. Gusto mo bang magkwento o subukan ang isang mood-boosting activity? Pwede rin akong magbigay ng suggestion."
        return (reply, "sad", user_facts)
    if fuzzy_in(msg, tagalog_happy, 0.7):
        reply = "Ang saya naman! Sana magpatuloy ang magandang pakiramdam mo."
        return (reply, "happy", user_facts)
    if fuzzy_in(msg, tagalog_stress, 0.7):
        reply = "Mukhang stress ka. Gusto mo bang subukan ang breathing exercise o may gusto kang tips para mag-relax?"
        return (reply, "stress", user_facts)
    if fuzzy_in(msg, tagalog_activity, 0.7):
        fav = user_facts.get('favorite')
        reply = ("Narito ang ilang activities na pwede mong subukan:\n"
                "- Maglakad-lakad o mag-stretch\n"
                "- Makinig ng paborito mong kanta\n"
                "- Subukan ang breathing exercise\n"
                "- Isulat ang 3 bagay na nagpapasalamat ka\n"
                f"- Maglaro: Memory Match, Clicker, Bubble Wrap, Fidget Spinner, o EQ Test!{f' O kaya, makinig ng {fav}.' if fav else ''}\n")
        if fav:
            reply += f" Dahil mahilig ka sa {fav}, subukan mong gawin ito habang nagre-relax."
        reply += "Hanapin ang mga ito sa Games section o Wellness Tools. Gusto mo ba ng <a href='/games' target='_blank'>link sa games</a>?"
        return (reply, "activity", user_facts)
    if fuzzy_in(msg, tagalog_help, 0.7):
        reply = "Siyempre! Pwede kang magkwento tungkol sa nararamdaman mo, o humingi ng resources, tips, o kahit makinig lang ako."
        return (reply, "help", user_facts)
    if fuzzy_in(msg, tagalog_bye, 0.7):
        name = user_facts.get('name')
        reply = f"Ingat ka palagi{name and ', ' + name or ''}! Nandito lang ako kung gusto mong magkwento ulit."
        return (reply, "bye", user_facts)
    if fuzzy_in(msg, tagalog_tip, 0.7):
        reply = "Tip: Kapag mabigat ang pakiramdam, subukan mong mag-focus sa isang bagay na positibo, kahit maliit lang. Gusto mo pa ng tip o activity suggestion?"
        return (reply, "tip", user_facts)
    # English responses
    if fuzzy_in(msg, ["hi", "hello", "hey"]):
        name = user_facts.get('name')
        reply = f"Hello{name and ', ' + name or ''}! How can I support you today?"
        return (reply, "greetings", user_facts)
    if fuzzy_in(msg, ["sad", "unhappy"]):
        name = user_facts.get('name')
        mood = user_facts.get('mood')
        reply = f"I'm sorry to hear that you're feeling {mood if mood else 'sad'}{', ' + name if name else ''}. Would you like to talk about it or try a mood-boosting activity? You can ask me for suggestions!"
        return (reply, "sad", user_facts)
    if fuzzy_in(msg, ["happy", "good"]):
        reply = "That's wonderful to hear! Keep up the positive vibes."
        return (reply, "happy", user_facts)
    if fuzzy_in(msg, ["stress", "anxious"]):
        reply = "It sounds like you're feeling stressed. Would you like a breathing exercise or some tips to relax?"
        return (reply, "stress", user_facts)
    if fuzzy_in(msg, ["what activity", "activity", "suggestion"]):
        fav = user_facts.get('favorite')
        reply = ("Here are some mood-boosting activities you can try:\n"
                "- Take a short walk or stretch\n"
                "- Listen to your favorite music\n"
                "- Try a breathing exercise (see our Breathing Exercise tool)\n"
                "- Write down 3 things you're grateful for\n"
                f"- Play a quick game: Memory Match, Clicker, Bubble Wrap, Fidget Spinner, or EQ Test!{f' Or listen to {fav}.' if fav else ''}\n")
        if fav:
            reply += f" Since you like {fav}, you might enjoy it while relaxing."
        reply += "You can find these in the Games section or Wellness Tools above. Want a <a href='/games' target='_blank'>link to the games</a>?"
        return (reply, "activity", user_facts)
    if fuzzy_in(msg, ["link"]) or (fuzzy_in(msg, ["yes"]) and fuzzy_in(msg, ["game"])):
        reply = "Here you go! <a href='/games' target='_blank'>Click here to play a game</a>. Have fun!"
        return (reply, "activity", user_facts)
    if fuzzy_in(msg, ["help"]):
        reply = "Of course! You can talk to me about how you're feeling, or ask for resources, tips, or just someone to listen."
        return (reply, "help", user_facts)
    if fuzzy_in(msg, ["bye", "goodbye"]):
        name = user_facts.get('name')
        reply = f"Take care{name and ', ' + name or ''}! Remember, I'm always here if you need to talk."
        return (reply, "bye", user_facts)
    if fuzzy_in(msg, ["tip"]):
        reply = "Here's a tip: When you're feeling down, try to focus on something positive, even if it's small. Would you like another tip or an activity suggestion?"
        return (reply, "tip", user_facts)
    # If input is unclear, offer gentle encouragement, recall past facts, and ask for details
    name = user_facts.get('name')
    mood_hist = user_facts.get('mood_history', [])
    fav_hist = user_facts.get('favorite_history', [])
    reply = f"I'm here to listen{name and ', ' + name or ''}. "
    if mood_hist and len(mood_hist) > 1:
        reply += f"Earlier you mentioned feeling {', '.join(mood_hist[:-1])}. "
    if fav_hist:
        reply += f"I remember you like {fav_hist[-1]}. "
    reply += "If you'd like to share more or tell me how you're feeling, I'm ready to help."
    return (reply, None, user_facts)
