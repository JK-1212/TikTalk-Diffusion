"""
Prompt templates for generating child-appropriate images.

Design principles (from TikTalk project requirements):
- Images must be easy to describe orally by children aged 6-12
- Contain clear objects and actions
- Avoid visual clutter & abstract concepts
- Cartoon / illustration style
- Suitable for PSLE Stimulus-Based Conversation practice
"""

# Style suffix appended to every prompt
STYLE_SUFFIX = (
    "children's book illustration style, bright and cheerful colors, "
    "simple composition, clear objects, white background or simple background, "
    "cute cartoon style, no text, no watermark, child-friendly"
)

# Negative prompt to avoid unwanted content
NEGATIVE_PROMPT = (
    "realistic photo, scary, violent, complex background, cluttered, "
    "abstract, blurry, dark, text, watermark, signature, adult content, "
    "multiple overlapping objects, confusing composition"
)

# Scenario categories for PSLE oral practice
# Each category has a list of prompt templates
# Use {scene}, {character}, {action} placeholders for flexibility
SCENARIO_TEMPLATES = {
    "daily_life": [
        "A {character} {action} in the kitchen",
        "A {character} {action} in the living room",
        "A {character} {action} at the dining table",
        "A family having breakfast together at home",
        "A child helping to wash dishes in the kitchen",
    ],
    "school": [
        "Children {action} in the classroom",
        "A {character} reading a book in the school library",
        "Children playing on the school playground",
        "A teacher and students in a classroom",
        "Children eating lunch in the school canteen",
    ],
    "outdoor": [
        "A {character} {action} in the park",
        "Children playing at the playground with slides and swings",
        "A family having a picnic under a big tree",
        "A {character} riding a bicycle on a path",
        "Children flying kites in an open field",
    ],
    "community": [
        "People shopping at a supermarket",
        "A {character} buying fruits at a market stall",
        "Children visiting a fire station",
        "A {character} at the bus stop waiting for a bus",
        "People at a community event in the neighbourhood",
    ],
    "nature": [
        "A {character} looking at animals in the zoo",
        "Birds and squirrels in a garden",
        "A {character} planting flowers in a garden",
        "Fish swimming in a clear pond",
        "A {character} watching butterflies in a meadow",
    ],
}

# Common characters suitable for PSLE scenarios
CHARACTERS = [
    "boy", "girl", "child", "mother", "father",
    "grandmother", "grandfather", "young boy", "young girl",
]

# Common actions suitable for PSLE scenarios
ACTIONS = [
    "cooking", "reading a book", "playing with a ball",
    "drawing a picture", "eating", "cleaning",
    "talking to a friend", "walking the dog", "watering plants",
    "doing homework", "singing", "dancing",
]


def build_prompt(base_prompt: str) -> str:
    """Combine a base prompt with the standard style suffix."""
    return f"{base_prompt}, {STYLE_SUFFIX}"


def fill_template(template: str, character: str = "boy", action: str = "playing") -> str:
    """Fill placeholders in a template string."""
    return template.format(character=character, action=action, scene="")


def get_all_scenarios() -> list[str]:
    """Return all predefined scenario prompts (with placeholders filled with defaults)."""
    prompts = []
    for category, templates in SCENARIO_TEMPLATES.items():
        for t in templates:
            try:
                filled = t.format(character="boy", action="playing", scene="")
            except KeyError:
                filled = t
            prompts.append(filled)
    return prompts
