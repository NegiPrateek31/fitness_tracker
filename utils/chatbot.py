def chatbot_reply(query, user_info=None):
    if not query or query.strip()=='':
        return 'Ask me anything about workouts, diet, or habits!'
    q = query.lower()
    if 'workout' in q or 'exercise' in q:
        return 'Try a 20-minute circuit: 3 sets of 10 push-ups, 15 squats, 30s plank, 1-min rest.'
    if 'diet' in q or 'eat' in q or 'food' in q:
        return 'Prefer lean protein and veggies. For quick energy: banana + greek yogurt.'
    if 'sleep' in q:
        return 'Aim for 7-8 hours. Avoid screens 30 minutes before bed.'
    if 'water' in q or 'hydrate' in q:
        return 'Try to drink at least 2 liters a day. Small sips regularly help.'
    return 'Nice question — keep it specific (e.g., "Suggest a 15-min cardio routine").'
