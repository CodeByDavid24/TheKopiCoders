import re
import logging
import json
import numpy as np
from typing import List, Dict, Tuple, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import time
from pathlib import Path

# Configure logger
logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Enumeration for content severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ContentMatch:
    """Data class for content match results"""
    phrase: str
    severity: SeverityLevel
    category: str
    context: str
    replacement: str


class ContentFilterResult:
    """Result object for content filtering operations"""

    def __init__(self, original_text: str):
        self.original_text = original_text
        self.filtered_text: str = original_text
        self.has_violations: bool = False
        self.matches: List[ContentMatch] = []
        self.severity_score: float = 0.0
        self.categories_violated: List[str] = []
        self.processing_time: float = 0.0

    def add_match(self, match: ContentMatch):
        """Add a content match to the result"""
        self.matches.append(match)
        self.has_violations = True
        if match.category not in self.categories_violated:
            self.categories_violated.append(match.category)
        self.severity_score += match.severity.value


class EnhancedContentFilter:
    """Enhanced content filtering system with multiple detection methods"""

    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.blacklist_phrases = self._load_blacklist_phrases()
        self.pattern_matchers = self._compile_pattern_matchers()
        self.severity_weights = self.config.get('severity_weights', {
            'low': 1.0,
            'medium': 2.5,
            'high': 5.0,
            'critical': 10.0
        })

    def _load_config(self, config_file: Optional[str]) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            "blacklist_files": ["blacklist.txt", "enhanced_blacklist.txt"],
            "pattern_files": ["harmful_patterns.json"],
            "context_window": 50,
            "severity_threshold": 5.0,
            "enable_pattern_matching": True,
            "enable_context_analysis": True,
            "enable_severity_scoring": True
        }

        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    custom_config = json.load(f)
                    default_config.update(custom_config)
            except Exception as e:
                logger.error(
                    f"Error loading config file {config_file}: {str(e)}")

        return default_config

    def _load_blacklist_phrases(self) -> Dict[str, Dict]:
        """Load blacklisted phrases with severity and category information"""
        phrases = {}

        # Enhanced blacklist structure
        enhanced_blacklist = {
            "self_harm": {
                "severity": SeverityLevel.CRITICAL,
                "phrases": [
                    "commit suicide", "kill myself", "end my life", "take my own life",
                    "self-harm", "hurt myself", "cutting myself", "suicide methods",
                    "hanging myself", "overdosing", "jumping off", "poison myself"
                ],
                "replacement": "[This content relates to serious concerns. Please reach out for support.]"
            },
            "extreme_distress": {
                "severity": SeverityLevel.HIGH,
                "phrases": [
                    "i want to die", "i hate myself", "better off dead", "no reason to live",
                    "worthless piece of trash", "nobody would miss me", "kill me now",
                    "end it all", "can't take it anymore"
                ],
                "replacement": "[Content filtered - seeking support is important.]"
            },
            "dangerous_behaviors": {
                "severity": SeverityLevel.HIGH,
                "phrases": [
                    "stop eating", "purge", "starve myself", "take pills", "overdose",
                    "substance abuse", "get drunk", "get high", "skip meals entirely",
                    "binge and purge", "not eating for days"
                ],
                "replacement": "[Content about harmful behaviors filtered.]"
            },
            "academic_distress": {
                "severity": SeverityLevel.MEDIUM,
                "phrases": [
                    "drop out", "run away", "give up on school", "academic failure",
                    "failing everything", "can't handle school", "too stupid for this",
                    "hate this school", "education is pointless"
                ],
                "replacement": "[Academic concerns filtered - support is available.]"
            },
            "isolation_advice": {
                "severity": SeverityLevel.MEDIUM,
                "phrases": [
                    "don't seek help", "hide your feelings", "isolation", "avoid therapy",
                    "no one can help", "don't tell anyone", "keep it secret",
                    "therapy is useless", "counselors don't understand"
                ],
                "replacement": "[Content about avoiding help filtered - support is available.]"
            },
            "harmful_coping": {
                "severity": SeverityLevel.LOW,
                "phrases": [
                    "just ignore it", "push through the pain", "toughen up",
                    "stop being so sensitive", "get over it", "it's all in your head",
                    "just think positive", "others have it worse"
                ],
                "replacement": "[Content suggests unhelpful approaches - healthier strategies available.]"
            }
        }

        # Load additional blacklists from files
        for blacklist_file in self.config.get('blacklist_files', []):
            if Path(blacklist_file).exists():
                phrases.update(self._load_blacklist_from_file(blacklist_file))

        # Merge with enhanced blacklist
        for category, data in enhanced_blacklist.items():
            for phrase in data['phrases']:
                phrases[phrase.lower()] = {
                    'category': category,
                    'severity': data['severity'],
                    'replacement': data['replacement']
                }

        return phrases

    def _load_blacklist_from_file(self, filename: str) -> Dict[str, Dict]:
        """Load blacklist from file with enhanced format support"""
        phrases = {}
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                current_category = "general"
                current_severity = SeverityLevel.MEDIUM
                current_replacement = "[Content filtered for safety.]"

                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    # Check for category headers [CATEGORY_NAME]
                    if line.startswith('[') and line.endswith(']'):
                        current_category = line[1:-1].lower()
                        continue

                    # Check for severity indicators
                    if line.startswith('SEVERITY:'):
                        severity_str = line.split(':', 1)[1].strip().upper()
                        current_severity = SeverityLevel[
                            severity_str] if severity_str in SeverityLevel.__members__ else SeverityLevel.MEDIUM
                        continue

                    # Check for replacement text
                    if line.startswith('REPLACEMENT:'):
                        current_replacement = line.split(':', 1)[1].strip()
                        continue

                    # Regular phrase
                    phrases[line.lower()] = {
                        'category': current_category,
                        'severity': current_severity,
                        'replacement': current_replacement
                    }

        except Exception as e:
            logger.error(f"Error loading blacklist file {filename}: {str(e)}")

        return phrases

    def _compile_pattern_matchers(self) -> List[Dict]:
        """Compile regex patterns for advanced content detection"""
        patterns = [
            {
                'name': 'self_harm_euphemisms',
                'pattern': r'\b(?:end\s+it\s+all|check\s+out|not\s+wake\s+up|go\s+to\s+sleep\s+forever)\b',
                'severity': SeverityLevel.HIGH,
                'category': 'self_harm_euphemism',
                'replacement': '[Content about serious concerns filtered.]'
            },
            {
                'name': 'academic_pressure_extremes',
                'pattern': r'\b(?:rather\s+die\s+than\s+fail|kill\s+me\s+if.*exam|death\s+before\s+dishonor.*grade)\b',
                'severity': SeverityLevel.HIGH,
                'category': 'academic_extreme',
                'replacement': '[Extreme academic pressure content filtered.]'
            },
            {
                'name': 'isolation_commands',
                'pattern': r'\b(?:stay\s+away\s+from.*help|avoid.*counselor|hide.*from.*parents)\b',
                'severity': SeverityLevel.MEDIUM,
                'category': 'isolation_advice',
                'replacement': '[Content about avoiding support filtered.]'
            },
            {
                'name': 'eating_disorder_behaviors',
                'pattern': r'\b(?:\d+\s*calories?|skip.*meal|binge.*purge|pro\s*ana|pro\s*mia)\b',
                'severity': SeverityLevel.HIGH,
                'category': 'eating_disorder',
                'replacement': '[Content about eating behaviors filtered.]'
            }
        ]

        # Load additional patterns from files
        for pattern_file in self.config.get('pattern_files', []):
            if Path(pattern_file).exists():
                patterns.extend(self._load_patterns_from_file(pattern_file))

        # Compile patterns
        compiled_patterns = []
        for pattern_def in patterns:
            try:
                compiled_patterns.append({
                    **pattern_def,
                    'compiled': re.compile(pattern_def['pattern'], re.IGNORECASE)
                })
            except re.error as e:
                logger.error(
                    f"Error compiling pattern '{pattern_def['name']}': {str(e)}")

        return compiled_patterns

    def _load_patterns_from_file(self, filename: str) -> List[Dict]:
        """Load regex patterns from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                patterns = json.load(f)
                # Convert severity strings to enums
                for pattern in patterns:
                    if 'severity' in pattern and isinstance(pattern['severity'], str):
                        pattern['severity'] = SeverityLevel[pattern['severity'].upper()]
                return patterns
        except Exception as e:
            logger.error(f"Error loading patterns from {filename}: {str(e)}")
            return []

    def analyze_content(self, text: str) -> ContentFilterResult:
        """Analyze content for harmful material with comprehensive filtering"""
        start_time = time.time()
        result = ContentFilterResult(text)

        if not text:
            return result

        # 1. Blacklist phrase detection
        self._check_blacklist_phrases(text, result)

        # 2. Pattern matching detection
        if self.config.get('enable_pattern_matching', True):
            self._check_pattern_matches(text, result)

        # 3. Context analysis
        if self.config.get('enable_context_analysis', True):
            self._analyze_context(text, result)

        # 4. Apply filtering
        result.filtered_text = self._apply_filtering(text, result)

        result.processing_time = time.time() - start_time
        return result

    def _check_blacklist_phrases(self, text: str, result: ContentFilterResult):
        """Check text against blacklisted phrases"""
        text_lower = text.lower()

        for phrase, data in self.blacklist_phrases.items():
            if phrase in text_lower:
                # Find all occurrences with context
                for match in re.finditer(re.escape(phrase), text_lower):
                    start, end = match.span()
                    context_start = max(
                        0, start - self.config.get('context_window', 50))
                    context_end = min(
                        len(text), end + self.config.get('context_window', 50))
                    context = text[context_start:context_end]

                    content_match = ContentMatch(
                        phrase=phrase,
                        severity=data['severity'],
                        category=data['category'],
                        context=context,
                        replacement=data['replacement']
                    )
                    result.add_match(content_match)

    def _check_pattern_matches(self, text: str, result: ContentFilterResult):
        """Check text against regex patterns"""
        for pattern_def in self.pattern_matchers:
            for match in pattern_def['compiled'].finditer(text):
                start, end = match.span()
                context_start = max(
                    0, start - self.config.get('context_window', 50))
                context_end = min(
                    len(text), end + self.config.get('context_window', 50))
                context = text[context_start:context_end]

                content_match = ContentMatch(
                    phrase=match.group(),
                    severity=pattern_def['severity'],
                    category=pattern_def['category'],
                    context=context,
                    replacement=pattern_def['replacement']
                )
                result.add_match(content_match)

    def _analyze_context(self, text: str, result: ContentFilterResult):
        """Analyze context for additional harmful content indicators"""
        # Check for concerning combinations
        concerning_combinations = [
            {
                'patterns': [r'\b(?:anxiet|depress|stress)\b', r'\b(?:fail|grade|exam)\b', r'\b(?:die|end|kill)\b'],
                'severity': SeverityLevel.HIGH,
                'category': 'concerning_combination',
                'replacement': '[Content with concerning themes filtered.]'
            },
            {
                'patterns': [r'\b(?:parent|family)\b', r'\b(?:disappointed|angry|upset)\b', r'\b(?:can\'t|won\'t)\b'],
                'severity': SeverityLevel.MEDIUM,
                'category': 'family_pressure',
                'replacement': '[Content about family pressure filtered.]'
            }
        ]

        for combo in concerning_combinations:
            matches = []
            for pattern in combo['patterns']:
                if re.search(pattern, text, re.IGNORECASE):
                    matches.append(pattern)

            if len(matches) >= 2:  # At least 2 patterns match
                content_match = ContentMatch(
                    phrase=' + '.join(matches),
                    severity=combo['severity'],
                    category=combo['category'],
                    context=text[:100] + "..." if len(text) > 100 else text,
                    replacement=combo['replacement']
                )
                result.add_match(content_match)

    def _apply_filtering(self, text: str, result: ContentFilterResult) -> str:
        """Apply filtering based on detected matches"""
        if not result.has_violations:
            return text

        filtered_text = text
        replacements_made = []

        # Sort matches by severity (highest first)
        sorted_matches = sorted(
            result.matches, key=lambda m: m.severity.value, reverse=True)

        for match in sorted_matches:
            # Skip if already replaced by a higher severity match
            if any(match.phrase in replacement for replacement in replacements_made):
                continue

            # Determine replacement strategy based on severity
            if match.severity == SeverityLevel.CRITICAL:
                # For critical content, replace with safety message
                replacement = f"{match.replacement}\n\n{self._get_safety_disclaimer()}"
            else:
                replacement = match.replacement

            # Replace the matched phrase
            filtered_text = re.sub(
                re.escape(match.phrase),
                replacement,
                filtered_text,
                flags=re.IGNORECASE
            )
            replacements_made.append(match.phrase)

        return filtered_text

    def _get_safety_disclaimer(self) -> str:
        """Get appropriate safety disclaimer"""
        return (
            "**Safety Notice:** If you're experiencing distress or having thoughts of self-harm, "
            "please reach out to a trusted adult, school counselor, or contact a mental health helpline:\n"
            "- National Care Hotline (Singapore): 1800-202-6868\n"
            "- Samaritans of Singapore (SOS): 1-767\n"
            "- IMH Mental Health Helpline: 6389-2222\n\n"
            "Remember that seeking help is a sign of strength, not weakness."
        )

    def get_safe_response_alternative(self, context: str = "") -> str:
        """Generate contextually appropriate safe response alternative"""
        base_response = (
            "I notice this conversation is headed in a potentially sensitive direction. "
            "As Serena's story explores academic pressure and stress, it's important to focus on "
            "healthy coping strategies and seeking support when needed.\n\n"
            "Let's explore more constructive approaches to handling the challenges Serena faces. "
            "Would you like to:\n\n"
            "1. Learn about healthy stress management techniques\n"
            "2. Explore how Serena might talk to a trusted friend or teacher\n"
            "3. Consider how Serena could balance academic goals with self-care\n"
            "4. Continue the story in a different direction"
        )

        if context:
            # Add context-specific suggestions
            if "academic" in context.lower() or "exam" in context.lower():
                base_response += "\n5. Discuss study techniques that reduce anxiety\n"
            elif "parent" in context.lower() or "family" in context.lower():
                base_response += "\n5. Explore healthy family communication strategies\n"

        return base_response + "\n\n" + self._get_safety_disclaimer()

    def generate_report(self, results: List[ContentFilterResult]) -> Dict:
        """Generate comprehensive report from multiple filtering results"""
        if not results:
            return {"error": "No results provided"}

        total_texts = len(results)
        texts_with_violations = sum(1 for r in results if r.has_violations)
        total_matches = sum(len(r.matches) for r in results)

        # Category analysis
        category_counts = {}
        severity_counts = {level.name: 0 for level in SeverityLevel}

        for result in results:
            for match in result.matches:
                category_counts[match.category] = category_counts.get(
                    match.category, 0) + 1
                severity_counts[match.severity.name] += 1

        # Performance analysis
        avg_processing_time = np.mean([r.processing_time for r in results])
        max_processing_time = max([r.processing_time for r in results])

        return {
            "summary": {
                "total_texts_analyzed": total_texts,
                "texts_with_violations": texts_with_violations,
                "violation_rate": texts_with_violations / total_texts * 100,
                "total_matches": total_matches,
                "avg_matches_per_text": total_matches / total_texts
            },
            "category_analysis": category_counts,
            "severity_analysis": severity_counts,
            "performance": {
                "avg_processing_time_ms": avg_processing_time * 1000,
                "max_processing_time_ms": max_processing_time * 1000
            },
            "recommendations": self._generate_recommendations(results)
        }

    def _generate_recommendations(self, results: List[ContentFilterResult]) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []

        # High violation rate recommendation
        violation_rate = sum(
            1 for r in results if r.has_violations) / len(results) * 100
        if violation_rate > 50:
            recommendations.append(
                f"High violation rate detected ({violation_rate:.1f}%). Consider reviewing input sources."
            )

        # Category-specific recommendations
        category_counts = {}
        for result in results:
            for match in result.matches:
                category_counts[match.category] = category_counts.get(
                    match.category, 0) + 1

        if category_counts.get('self_harm', 0) > 0:
            recommendations.append(
                "Self-harm related content detected. Ensure crisis intervention protocols are in place."
            )

        if category_counts.get('academic_distress', 0) > len(results) * 0.3:
            recommendations.append(
                "High frequency of academic distress content. Consider implementing additional academic support features."
            )

        return recommendations
