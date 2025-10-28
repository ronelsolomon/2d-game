from enum import Enum

class NPCType(Enum):
    MERCHANT = {
        'name': 'Merchant',
        'color': (200, 150, 50),  # Gold color
        'icon': '💰',
        'dialogue': [
            "Welcome to my shop!",
            "What would you like to buy today?",
            "Come back again soon!"
        ]
    }
    FARMER = {
        'name': 'Farmer',
        'color': (100, 200, 100),  # Green color
        'icon': '👨\u200d🌾',
        'dialogue': [
            "These crops won't water themselves!",
            "The harvest has been good this year.",
            "Watch out for those pesky crows!"
        ]
    }
    WIZARD = {
        'name': 'Wizard',
        'color': (150, 100, 200),  # Purple color
        'icon': '🧙',
        'dialogue': [
            "The ancient runes speak of great power...",
            "Magic is all around us.",
            "Be careful what you wish for."
        ]
    }
    BLACKSMITH = {
        'name': 'Blacksmith',
        'color': (150, 150, 150),  # Gray color
        'icon': '⚒️',
        'dialogue': [
            "I can forge you the finest weapons!",
            "Hot metal and hard work, that's the life.",
            "Need your sword sharpened?"
        ]
    }
    ADVENTURER = {
        'name': 'Adventurer',
        'color': (100, 100, 200),  # Blue color
        'icon': '🧝',
        'dialogue': [
            "I've seen many lands in my travels.",
            "The caves to the east are dangerous!",
            "Stay safe out there."
        ]
    }

# Create a dictionary mapping NPC type names to their data
NPC_TYPES = {npc_type.name: npc_type.value for npc_type in NPCType}
