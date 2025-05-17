"""
Character model for SootheAI.
Defines the structure and methods for character data.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class PhysicalAttributes:
    """Physical attributes of a character."""
    race: Dict[str, str] = field(default_factory=lambda: {"name": "Chinese Singaporean",
                                                          "description": ""})
    age: Dict[str, Any] = field(default_factory=lambda: {"years": 17,
                                                         "lifespan": "Typically lives up to around 85–100 years with modern healthcare.",
                                                         "maturity": "Young adult transitioning from adolescence."})
    measurements: Dict[str, float] = field(default_factory=lambda: {"height": 164,
                                                                    "weight": 46,
                                                                    "bmi": 17.1})
    appearance: str = "Slim and soft-featured, with long black hair often tied in a neat ponytail, warm brown eyes, and a gentle presence."


@dataclass
class PersonalityTraits:
    """Personality traits of a character."""
    mbti: str = "INFP"
    mbti_description: str = "Soft-spoken, Shy, Determined, Thoughtful, Responsible"
    traits: Dict[str, str] = field(default_factory=lambda: {
        "attitudes": "Quietly confident and introspective; approaches life with a thoughtful mindset",
        "perception": "Highly observant of her surroundings and sensitive to the moods and needs of others",
        "judgement": "Relies on personal values, intuition, and empathy rather than logic alone when making decisions",
        "orientation": "Purpose-driven; seeks personal growth and meaning through learning and reflection"
    })


@dataclass
class ClassDetails:
    """Academic class details of a character."""
    name: str = "JC Student"
    description: str = "A JC1 student at a prestigious junior college in Singapore"
    subjects: List[str] = field(default_factory=lambda: [
        "H2 Chemistry",
        "H2 Biology",
        "H2 Mathematics",
        "H1 General Paper"
    ])
    cca: str = "Student Council (Vice President)"
    academic_standing: str = "Consistently in the top quartile of her cohort"


@dataclass
class LocationInfo:
    """Location information for a character."""
    country: str = "Singapore"
    school: str = "Raffles Junior College"
    home: str = "HDB flat in Tampines"
    study_spots: List[str] = field(default_factory=lambda: [
        "School library",
        "Quiet corner in the canteen",
        "Neighborhood community center"
    ])
    world: str = "A modern and high-pressure society where academic success is highly valued"


@dataclass
class MentalHealthInfo:
    """Mental health information for a character."""
    anxiety: bool = True
    stress: bool = True
    self_esteem: bool = True
    self_awareness: str = "Limited - attributes symptoms to normal student life pressures"


@dataclass
class Backstory:
    """Character backstory information."""
    description: str = ""
    goals: List[str] = field(default_factory=list)
    history: List[str] = field(default_factory=list)


@dataclass
class DailyRoutine:
    """Character's daily routine."""
    morning: str = "Wakes up at 5:30 AM to review notes before school"
    school_hours: str = "Attends lectures and tutorials"
    after_school: str = "Stays in the library until it closes"
    evening: str = "Studies at home until late"
    weekend: str = "Dedicating most hours to studying, with brief breaks for family meals"


@dataclass
class Relationships:
    """Character's relationships with others."""
    parents: str = "Supportive but have high expectations"
    friends: str = "A small circle of 2-3 close friends"
    teachers: str = "Viewed positively by teachers for her diligence"
    peers: str = "Respected for her intelligence but perceived as somewhat aloof"


@dataclass
class Character:
    """Main character class for SootheAI."""
    name: str = "Serena"
    gender: str = "Female"
    personality: PersonalityTraits = field(default_factory=PersonalityTraits)
    physical: PhysicalAttributes = field(default_factory=PhysicalAttributes)
    class_details: ClassDetails = field(default_factory=ClassDetails)
    location: LocationInfo = field(default_factory=LocationInfo)
    mental_health_issues: MentalHealthInfo = field(
        default_factory=MentalHealthInfo)
    backstory: Backstory = field(default_factory=Backstory)
    daily_routine: DailyRoutine = field(default_factory=DailyRoutine)
    relationships: Relationships = field(default_factory=Relationships)
    behaviour: List[str] = field(default_factory=list)
    anxiety_triggers: List[str] = field(default_factory=list)
    coping_mechanism: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """
        Create a Character instance from a dictionary.

        Args:
            data: Dictionary containing character data

        Returns:
            Character instance
        """
        character = cls()

        # Set simple attributes
        character.name = data.get('name', character.name)
        character.gender = data.get('gender', character.gender)

        # Set nested attributes if present
        if 'personality' in data:
            personality_data = data['personality']
            character.personality.mbti = personality_data.get(
                'mbti', character.personality.mbti)
            character.personality.mbti_description = personality_data.get('mbti_description',
                                                                          character.personality.mbti_description)
            if 'traits' in personality_data:
                character.personality.traits.update(personality_data['traits'])

        # Set physical attributes
        if 'physical' in data:
            physical_data = data['physical']
            if 'race' in physical_data:
                character.physical.race.update(physical_data['race'])
            if 'age' in physical_data:
                character.physical.age.update(physical_data['age'])
            if 'measurements' in physical_data:
                character.physical.measurements.update(
                    physical_data['measurements'])
            if 'appearance' in physical_data:
                character.physical.appearance = physical_data['appearance']

        # Set class details
        if 'class' in data:
            class_data = data['class']
            character.class_details.name = class_data.get(
                'name', character.class_details.name)
            character.class_details.description = class_data.get(
                'description', character.class_details.description)
            character.class_details.subjects = class_data.get(
                'subjects', character.class_details.subjects)
            character.class_details.cca = class_data.get(
                'cca', character.class_details.cca)
            character.class_details.academic_standing = class_data.get('academic_standing',
                                                                       character.class_details.academic_standing)

        # Set location info
        if 'location' in data:
            location_data = data['location']
            character.location.country = location_data.get(
                'country', character.location.country)
            character.location.school = location_data.get(
                'school', character.location.school)
            character.location.home = location_data.get(
                'home', character.location.home)
            character.location.study_spots = location_data.get(
                'study_spots', character.location.study_spots)
            character.location.world = location_data.get(
                'world', character.location.world)

        # Set mental health info
        if 'mental_health_issues' in data:
            mh_data = data['mental_health_issues']
            character.mental_health_issues.anxiety = mh_data.get(
                'anxiety', character.mental_health_issues.anxiety)
            character.mental_health_issues.stress = mh_data.get(
                'stress', character.mental_health_issues.stress)
            character.mental_health_issues.self_esteem = mh_data.get('self_esteem',
                                                                     character.mental_health_issues.self_esteem)
            character.mental_health_issues.self_awareness = mh_data.get('self_awareness',
                                                                        character.mental_health_issues.self_awareness)

        # Set backstory
        if 'backstory' in data:
            backstory_data = data['backstory']
            character.backstory.description = backstory_data.get(
                'description', character.backstory.description)
            character.backstory.goals = backstory_data.get(
                'goals', character.backstory.goals)
            character.backstory.history = backstory_data.get(
                'history', character.backstory.history)

        # Set daily routine
        if 'daily_routine' in data:
            routine_data = data['daily_routine']
            character.daily_routine.morning = routine_data.get(
                'morning', character.daily_routine.morning)
            character.daily_routine.school_hours = routine_data.get('school_hours',
                                                                    character.daily_routine.school_hours)
            character.daily_routine.after_school = routine_data.get('after_school',
                                                                    character.daily_routine.after_school)
            character.daily_routine.evening = routine_data.get(
                'evening', character.daily_routine.evening)
            character.daily_routine.weekend = routine_data.get(
                'weekend', character.daily_routine.weekend)

        # Set relationships
        if 'relationships' in data:
            rel_data = data['relationships']
            character.relationships.parents = rel_data.get(
                'parents', character.relationships.parents)
            character.relationships.friends = rel_data.get(
                'friends', character.relationships.friends)
            character.relationships.teachers = rel_data.get(
                'teachers', character.relationships.teachers)
            character.relationships.peers = rel_data.get(
                'peers', character.relationships.peers)

        # Set list attributes
        character.behaviour = data.get('behaviour', character.behaviour)
        character.anxiety_triggers = data.get(
            'anxiety_triggers', character.anxiety_triggers)
        character.coping_mechanism = data.get(
            'coping_mechanism', character.coping_mechanism)

        return character

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Character instance to a dictionary.

        Returns:
            Dictionary representation of the character
        """
        return {
            "name": self.name,
            "gender": self.gender,
            "personality": {
                "mbti": self.personality.mbti,
                "mbti_description": self.personality.mbti_description,
                "traits": self.personality.traits
            },
            "physical": {
                "race": self.physical.race,
                "age": self.physical.age,
                "measurements": self.physical.measurements,
                "appearance": self.physical.appearance
            },
            "class": {
                "name": self.class_details.name,
                "description": self.class_details.description,
                "subjects": self.class_details.subjects,
                "cca": self.class_details.cca,
                "academic_standing": self.class_details.academic_standing
            },
            "location": {
                "country": self.location.country,
                "school": self.location.school,
                "home": self.location.home,
                "study_spots": self.location.study_spots,
                "world": self.location.world
            },
            "mental_health_issues": {
                "anxiety": self.mental_health_issues.anxiety,
                "stress": self.mental_health_issues.stress,
                "self_esteem": self.mental_health_issues.self_esteem,
                "self_awareness": self.mental_health_issues.self_awareness
            },
            "backstory": {
                "description": self.backstory.description,
                "goals": self.backstory.goals,
                "history": self.backstory.history
            },
            "daily_routine": {
                "morning": self.daily_routine.morning,
                "school_hours": self.daily_routine.school_hours,
                "after_school": self.daily_routine.after_school,
                "evening": self.daily_routine.evening,
                "weekend": self.daily_routine.weekend
            },
            "relationships": {
                "parents": self.relationships.parents,
                "friends": self.relationships.friends,
                "teachers": self.relationships.teachers,
                "peers": self.relationships.peers
            },
            "behaviour": self.behaviour,
            "anxiety_triggers": self.anxiety_triggers,
            "coping_mechanism": self.coping_mechanism
        }


def load_character(character_data: Dict[str, Any]) -> Character:
    """
    Load a character from dictionary data.

    Args:
        character_data: Dictionary containing character data

    Returns:
        Character instance
    """
    return Character.from_dict(character_data)
