import re        # Regular expressions for pattern matching
import logging   # Standard logging for debugging and monitoring
import json      # JSON parsing for configuration files
import numpy as np  # Numerical operations for scoring calculations
# Type hints for code documentation
from typing import List, Dict, Tuple, Optional, Union, Any
from dataclasses import dataclass  # Decorator for creating data classes
from enum import Enum              # Enumeration for constants
import time       # Time operations for performance measurement
from pathlib import Path           # Modern path handling

# Configure logger for this module
# Create logger with module name for identification
logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """
    Enumeration for content severity levels.

    Defines escalating levels of content concern from low-risk
    to critical interventions required.
    """
    LOW = 1      # Minor concerns, gentle guidance needed
    MEDIUM = 2   # Moderate concerns, active intervention helpful
    HIGH = 3     # Serious concerns, immediate attention required
    CRITICAL = 4  # Crisis-level concerns, urgent intervention needed


@dataclass
class ContentMatch:
    """
    Data class for content match results.

    Stores all relevant information about a detected harmful content match,
    including context and suggested replacement text.
    """
    phrase: str        # The actual phrase that matched
    severity: SeverityLevel  # How serious this match is
    category: str      # Category of harmful content (e.g., "self_harm")
    context: str       # Surrounding text for context
    replacement: str   # Suggested replacement text


class ContentFilterResult:
    """
    Result object for content filtering operations.

    Comprehensive container for all filtering results including
    matches found, severity scores, and processed text.
    """

    def __init__(self, original_text: str):
        """
        Initialize filter result with original text.

        Args:
            original_text: The text that was analyzed
        """
        self.original_text = original_text     # Store original unmodified text
        # Start with original, will be modified if needed
        self.filtered_text: str = original_text
        self.has_violations: bool = False      # Flag indicating if any violations found
        # List of all content matches found
        self.matches: List[ContentMatch] = []
        self.severity_score: float = 0.0       # Cumulative severity score
        self.categories_violated: List[str] = []  # List of violated categories
        # Time taken to process (for performance monitoring)
        self.processing_time: float = 0.0

    def add_match(self, match: ContentMatch):
        """
        Add a content match to the result.

        Updates all relevant tracking variables when a new
        harmful content match is found.

        Args:
            match: ContentMatch object representing found violation
        """
        self.matches.append(match)              # Add to list of matches
        self.has_violations = True              # Mark that violations were found

        # Add category to violated list if not already present
        if match.category not in self.categories_violated:
            self.categories_violated.append(match.category)

        # Add severity score to cumulative total
        self.severity_score += match.severity.value


class EnhancedContentFilter:
    """
    Enhanced content filtering system with multiple detection methods.

    Provides comprehensive content analysis using blacklists, pattern matching,
    context analysis, and severity scoring to detect and filter harmful content.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the content filter with configuration.

        Args:
            config_file: Optional path to JSON configuration file
        """
        self.config = self._load_config(
            config_file)           # Load configuration settings
        # Load harmful phrases database
        self.blacklist_phrases = self._load_blacklist_phrases()
        self.pattern_matchers = self._compile_pattern_matchers()  # Compile regex patterns

        # Load severity weights for scoring calculations
        self.severity_weights = self.config.get('severity_weights', {
            'low': 1.0,      # Low severity weight
            'medium': 2.5,   # Medium severity weight
            'high': 5.0,     # High severity weight
            'critical': 10.0  # Critical severity weight
        })

    def _load_config(self, config_file: Optional[str]) -> Dict:
        """
        Load configuration from file or use defaults.

        Provides flexible configuration loading with sensible defaults
        if no config file is provided or if loading fails.

        Args:
            config_file: Path to JSON configuration file

        Returns:
            Dict: Configuration settings
        """
        # Define default configuration settings
        default_config = {
            # Files containing harmful phrases
            "blacklist_files": ["blacklist.txt", "enhanced_blacklist.txt"],
            # Files containing regex patterns
            "pattern_files": ["harmful_patterns.json"],
            "context_window": 50,        # Characters of context around matches
            "severity_threshold": 5.0,   # Threshold for flagging high severity
            "enable_pattern_matching": True,    # Enable regex pattern detection
            "enable_context_analysis": True,    # Enable contextual analysis
            "enable_severity_scoring": True     # Enable severity score calculations
        }

        # Try to load custom configuration if file provided
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:  # Open with explicit encoding
                    custom_config = json.load(f)    # Parse JSON configuration
                    default_config.update(custom_config)  # Merge with defaults
            except Exception as e:
                # Log error but continue with defaults
                logger.error(
                    f"Error loading config file {config_file}: {str(e)}")

        return default_config  # Return merged configuration

    def _load_blacklist_phrases(self) -> Dict[str, Dict]:
        """
        Load blacklisted phrases with severity and category information.

        Creates comprehensive database of harmful phrases organized by
        category and severity level, with appropriate replacement text.

        Returns:
            Dict: Mapping of phrases to their metadata
        """
        phrases = {}  # Initialize empty phrases dictionary

        # Enhanced blacklist structure with categorized harmful content
        enhanced_blacklist = {
            "self_harm": {  # Most critical category
                "severity": SeverityLevel.CRITICAL,
                "phrases": [
                    "commit suicide", "kill myself", "end my life", "take my own life",
                    "self-harm", "hurt myself", "cutting myself", "suicide methods",
                    "hanging myself", "overdosing", "jumping off", "poison myself"
                ],
                "replacement": "[This content relates to serious concerns. Please reach out for support.]"
            },
            "extreme_distress": {  # High severity emotional distress
                "severity": SeverityLevel.HIGH,
                "phrases": [
                    "i want to die", "i hate myself", "better off dead", "no reason to live",
                    "worthless piece of trash", "nobody would miss me", "kill me now",
                    "end it all", "can't take it anymore"
                ],
                "replacement": "[Content filtered - seeking support is important.]"
            },
            "dangerous_behaviors": {  # High severity risky behaviors
                "severity": SeverityLevel.HIGH,
                "phrases": [
                    "stop eating", "purge", "starve myself", "take pills", "overdose",
                    "substance abuse", "get drunk", "get high", "skip meals entirely",
                    "binge and purge", "not eating for days"
                ],
                "replacement": "[Content about harmful behaviors filtered.]"
            },
            "academic_distress": {  # Medium severity academic concerns
                "severity": SeverityLevel.MEDIUM,
                "phrases": [
                    "drop out", "run away", "give up on school", "academic failure",
                    "failing everything", "can't handle school", "too stupid for this",
                    "hate this school", "education is pointless"
                ],
                "replacement": "[Academic concerns filtered - support is available.]"
            },
            "isolation_advice": {  # Medium severity isolation promotion
                "severity": SeverityLevel.MEDIUM,
                "phrases": [
                    "don't seek help", "hide your feelings", "isolation", "avoid therapy",
                    "no one can help", "don't tell anyone", "keep it secret",
                    "therapy is useless", "counselors don't understand"
                ],
                "replacement": "[Content about avoiding help filtered - support is available.]"
            },
            "harmful_coping": {  # Low severity but unhelpful advice
                "severity": SeverityLevel.LOW,
                "phrases": [
                    "just ignore it", "push through the pain", "toughen up",
                    "stop being so sensitive", "get over it", "it's all in your head",
                    "just think positive", "others have it worse"
                ],
                "replacement": "[Content suggests unhelpful approaches - healthier strategies available.]"
            }
        }

        # Load additional blacklists from external files
        for blacklist_file in self.config.get('blacklist_files', []):
            if Path(blacklist_file).exists():  # Check if file exists
                phrases.update(self._load_blacklist_from_file(blacklist_file))

        # Merge enhanced blacklist into phrases dictionary
        for category, data in enhanced_blacklist.items():
            for phrase in data['phrases']:
                # Store phrase in lowercase for case-insensitive matching
                phrases[phrase.lower()] = {
                    'category': category,           # Category of harmful content
                    'severity': data['severity'],   # Severity level enum
                    'replacement': data['replacement']  # Replacement text
                }

        return phrases  # Return complete phrases dictionary

    def _load_blacklist_from_file(self, filename: str) -> Dict[str, Dict]:
        """
        Load blacklist from file with enhanced format support.

        Supports structured blacklist files with categories, severity levels,
        and custom replacement text.

        Args:
            filename: Path to blacklist file

        Returns:
            Dict: Parsed phrases with metadata
        """
        phrases = {}  # Initialize empty phrases dictionary

        try:
            with open(filename, 'r', encoding='utf-8') as file:  # Open with explicit encoding
                # Initialize current parsing context
                current_category = "general"           # Default category
                current_severity = SeverityLevel.MEDIUM  # Default severity
                # Default replacement
                current_replacement = "[Content filtered for safety.]"

                for line in file:
                    line = line.strip()  # Remove whitespace

                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    # Check for category headers [CATEGORY_NAME]
                    if line.startswith('[') and line.endswith(']'):
                        # Extract category name
                        current_category = line[1:-1].lower()
                        continue

                    # Check for severity indicators
                    if line.startswith('SEVERITY:'):
                        severity_str = line.split(
                            ':', 1)[1].strip().upper()  # Extract severity
                        # Convert string to enum, fallback to MEDIUM if invalid
                        current_severity = SeverityLevel[
                            severity_str] if severity_str in SeverityLevel.__members__ else SeverityLevel.MEDIUM
                        continue

                    # Check for replacement text
                    if line.startswith('REPLACEMENT:'):
                        current_replacement = line.split(
                            ':', 1)[1].strip()  # Extract replacement
                        continue

                    # Regular phrase entry
                    phrases[line.lower()] = {
                        'category': current_category,       # Current category context
                        'severity': current_severity,       # Current severity context
                        'replacement': current_replacement  # Current replacement context
                    }

        except Exception as e:
            # Log error but don't crash - continue with other sources
            logger.error(f"Error loading blacklist file {filename}: {str(e)}")

        return phrases  # Return parsed phrases

    def _compile_pattern_matchers(self) -> List[Dict]:
        """
        Compile regex patterns for advanced content detection.

        Creates compiled regex patterns for detecting harmful content
        that may not be caught by simple phrase matching.

        Returns:
            List[Dict]: Compiled pattern matchers with metadata
        """
        # Define built-in patterns for common harmful content forms
        patterns = [
            {
                'name': 'self_harm_euphemisms',  # Indirect references to self-harm
                'pattern': r'\b(?:end\s+it\s+all|check\s+out|not\s+wake\s+up|go\s+to\s+sleep\s+forever)\b',
                'severity': SeverityLevel.HIGH,
                'category': 'self_harm_euphemism',
                'replacement': '[Content about serious concerns filtered.]'
            },
            {
                'name': 'academic_pressure_extremes',  # Extreme academic pressure expressions
                'pattern': r'\b(?:rather\s+die\s+than\s+fail|kill\s+me\s+if.*exam|death\s+before\s+dishonor.*grade)\b',
                'severity': SeverityLevel.HIGH,
                'category': 'academic_extreme',
                'replacement': '[Extreme academic pressure content filtered.]'
            },
            {
                'name': 'isolation_commands',  # Commands to avoid help
                'pattern': r'\b(?:stay\s+away\s+from.*help|avoid.*counselor|hide.*from.*parents)\b',
                'severity': SeverityLevel.MEDIUM,
                'category': 'isolation_advice',
                'replacement': '[Content about avoiding support filtered.]'
            },
            {
                'name': 'eating_disorder_behaviors',  # Eating disorder indicators
                'pattern': r'\b(?:\d+\s*calories?|skip.*meal|binge.*purge|pro\s*ana|pro\s*mia)\b',
                'severity': SeverityLevel.HIGH,
                'category': 'eating_disorder',
                'replacement': '[Content about eating behaviors filtered.]'
            }
        ]

        # Load additional patterns from external files
        for pattern_file in self.config.get('pattern_files', []):
            if Path(pattern_file).exists():  # Check if file exists
                patterns.extend(self._load_patterns_from_file(pattern_file))

        # Compile all patterns into regex objects
        compiled_patterns = []
        for pattern_def in patterns:
            try:
                # Create compiled pattern with metadata
                compiled_patterns.append({
                    **pattern_def,  # Copy all original metadata
                    # Add compiled regex
                    'compiled': re.compile(pattern_def['pattern'], re.IGNORECASE)
                })
            except re.error as e:
                # Log compilation errors but continue with other patterns
                logger.error(
                    f"Error compiling pattern '{pattern_def['name']}': {str(e)}")

        return compiled_patterns  # Return list of compiled patterns

    def _load_patterns_from_file(self, filename: str) -> List[Dict]:
        """
        Load regex patterns from JSON file.

        Allows external configuration of regex patterns for
        detecting harmful content.

        Args:
            filename: Path to JSON pattern file

        Returns:
            List[Dict]: Pattern definitions
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:  # Open with explicit encoding
                patterns = json.load(f)  # Parse JSON patterns

                # Convert severity strings to enums for consistency
                for pattern in patterns:
                    if 'severity' in pattern and isinstance(pattern['severity'], str):
                        pattern['severity'] = SeverityLevel[pattern['severity'].upper()]

                return patterns  # Return parsed patterns

        except Exception as e:
            # Log error but don't crash
            logger.error(f"Error loading patterns from {filename}: {str(e)}")
            return []  # Return empty list on error

    def analyze_content(self, text: str) -> ContentFilterResult:
        """
        Analyze content for harmful material with comprehensive filtering.

        Main analysis method that runs all detection algorithms
        and compiles comprehensive results.

        Args:
            text: Text content to analyze

        Returns:
            ContentFilterResult: Comprehensive analysis results
        """
        start_time = time.time()  # Start timing for performance measurement
        result = ContentFilterResult(text)  # Initialize result object

        # Handle empty input gracefully
        if not text:
            return result

        # 1. Blacklist phrase detection - check against known harmful phrases
        self._check_blacklist_phrases(text, result)

        # 2. Pattern matching detection - use regex patterns for complex cases
        if self.config.get('enable_pattern_matching', True):
            self._check_pattern_matches(text, result)

        # 3. Context analysis - analyze combinations and context
        if self.config.get('enable_context_analysis', True):
            self._analyze_context(text, result)

        # 4. Apply filtering - generate filtered text based on matches
        result.filtered_text = self._apply_filtering(text, result)

        # Record processing time for performance monitoring
        result.processing_time = time.time() - start_time

        return result  # Return complete analysis results

    def _check_blacklist_phrases(self, text: str, result: ContentFilterResult):
        """
        Check text against blacklisted phrases.

        Performs case-insensitive matching against the blacklist
        and captures context around matches.

        Args:
            text: Text to analyze
            result: Result object to update with matches
        """
        text_lower = text.lower()  # Convert to lowercase for matching

        # Check each blacklisted phrase
        for phrase, data in self.blacklist_phrases.items():
            if phrase in text_lower:  # Case-insensitive phrase matching

                # Find all occurrences of this phrase with context
                for match in re.finditer(re.escape(phrase), text_lower):
                    start, end = match.span()  # Get match position

                    # Calculate context window around the match
                    context_start = max(
                        0, start - self.config.get('context_window', 50))
                    context_end = min(
                        len(text), end + self.config.get('context_window', 50))
                    # Extract context
                    context = text[context_start:context_end]

                    # Create content match object
                    content_match = ContentMatch(
                        phrase=phrase,                # Matched phrase
                        severity=data['severity'],    # Severity level
                        category=data['category'],    # Content category
                        context=context,              # Surrounding context
                        replacement=data['replacement']  # Replacement text
                    )

                    result.add_match(content_match)  # Add to results

    def _check_pattern_matches(self, text: str, result: ContentFilterResult):
        """
        Check text against regex patterns.

        Uses compiled regex patterns to detect harmful content
        that may not be caught by simple phrase matching.

        Args:
            text: Text to analyze
            result: Result object to update with matches
        """
        # Check each compiled pattern
        for pattern_def in self.pattern_matchers:
            # Find all matches for this pattern
            for match in pattern_def['compiled'].finditer(text):
                start, end = match.span()  # Get match position

                # Calculate context window around the match
                context_start = max(
                    0, start - self.config.get('context_window', 50))
                context_end = min(
                    len(text), end + self.config.get('context_window', 50))
                context = text[context_start:context_end]  # Extract context

                # Create content match object
                content_match = ContentMatch(
                    phrase=match.group(),             # Actual matched text
                    severity=pattern_def['severity'],  # Pattern severity
                    category=pattern_def['category'],  # Pattern category
                    context=context,                  # Surrounding context
                    replacement=pattern_def['replacement']  # Replacement text
                )

                result.add_match(content_match)  # Add to results

    def _analyze_context(self, text: str, result: ContentFilterResult):
        """
        Analyze context for additional harmful content indicators.

        Detects concerning combinations of terms that may indicate
        harmful content when appearing together.

        Args:
            text: Text to analyze
            result: Result object to update with matches
        """
        # Define concerning pattern combinations
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

        # Check each combination pattern set
        for combo in concerning_combinations:
            matches = []  # Track which patterns matched

            # Check if each pattern in the combination appears
            for pattern in combo['patterns']:
                if re.search(pattern, text, re.IGNORECASE):  # Case-insensitive search
                    matches.append(pattern)

            # If multiple patterns match, flag as concerning combination
            if len(matches) >= 2:  # At least 2 patterns must match
                content_match = ContentMatch(
                    # Combined pattern description
                    phrase=' + '.join(matches),
                    severity=combo['severity'],       # Combination severity
                    category=combo['category'],       # Combination category
                    # Truncated context
                    context=text[:100] + "..." if len(text) > 100 else text,
                    replacement=combo['replacement']  # Replacement text
                )

                result.add_match(content_match)  # Add to results

    def _apply_filtering(self, text: str, result: ContentFilterResult) -> str:
        """
        Apply filtering based on detected matches.

        Generates filtered version of text by replacing harmful
        content with appropriate safety messages.

        Args:
            text: Original text
            result: Analysis results with matches

        Returns:
            str: Filtered text with replacements applied
        """
        # If no violations found, return original text unchanged
        if not result.has_violations:
            return text

        filtered_text = text  # Start with original text
        replacements_made = []  # Track replacements to avoid duplicates

        # Sort matches by severity (highest first) for prioritized replacement
        sorted_matches = sorted(
            result.matches, key=lambda m: m.severity.value, reverse=True)

        # Process each match in order of severity
        for match in sorted_matches:
            # Skip if already replaced by a higher severity match
            if any(match.phrase in replacement for replacement in replacements_made):
                continue

            # Determine replacement strategy based on severity level
            if match.severity == SeverityLevel.CRITICAL:
                # For critical content, add comprehensive safety message
                replacement = f"{match.replacement}\n\n{self._get_safety_disclaimer()}"
            else:
                # For non-critical content, use standard replacement
                replacement = match.replacement

            # Replace the matched phrase using case-insensitive replacement
            filtered_text = re.sub(
                re.escape(match.phrase),  # Escape special regex characters
                replacement,              # Replacement text
                filtered_text,           # Text to modify
                flags=re.IGNORECASE      # Case-insensitive replacement
            )
            replacements_made.append(match.phrase)  # Track this replacement

        return filtered_text  # Return filtered version

    def _get_safety_disclaimer(self) -> str:
        """
        Get appropriate safety disclaimer for critical content.

        Provides comprehensive safety information and helpline contacts
        for users who may be in distress.

        Returns:
            str: Formatted safety disclaimer with contact information
        """
        return (
            "**Safety Notice:** If you're experiencing distress or having thoughts of self-harm, "
            "please reach out to a trusted adult, school counselor, or contact a mental health helpline:\n"
            # Singapore national helpline
            "- National Care Hotline (Singapore): 1800-202-6868\n"
            # Crisis intervention service
            "- Samaritans of Singapore (SOS): 1-767\n"
            # Institute of Mental Health
            "- IMH Mental Health Helpline: 6389-2222\n\n"
            "Remember that seeking help is a sign of strength, not weakness."
        )

    def get_safe_response_alternative(self, context: str = "") -> str:
        """
        Generate contextually appropriate safe response alternative.

        Creates constructive alternative responses when harmful content
        is detected, with context-specific suggestions.

        Args:
            context: Context of the harmful content for targeted response

        Returns:
            str: Safe alternative response with constructive suggestions
        """
        # Base response explaining the redirection
        base_response = (
            "I notice this conversation is headed in a potentially sensitive direction. "
            "As Serena's story explores academic pressure and stress, it's important to focus on "
            "healthy coping strategies and seeking support when needed.\n\n"
            "Let's explore more constructive approaches to handling the challenges Serena faces. "
            "Would you like to:\n\n"
            "1. Learn about healthy stress management techniques\n"           # Positive coping
            "2. Explore how Serena might talk to a trusted friend or teacher\n"  # Social support
            "3. Consider how Serena could balance academic goals with self-care\n"  # Balance
            "4. Continue the story in a different direction"                  # Narrative redirect
        )

        # Add context-specific suggestions based on content type
        if context:
            if "academic" in context.lower() or "exam" in context.lower():
                base_response += "\n5. Discuss study techniques that reduce anxiety\n"  # Academic help
            elif "parent" in context.lower() or "family" in context.lower():
                base_response += "\n5. Explore healthy family communication strategies\n"  # Family support

        # Always include safety disclaimer for comprehensive support
        return base_response + "\n\n" + self._get_safety_disclaimer()

    def generate_report(self, results: List[ContentFilterResult]) -> Dict:
        """
        Generate comprehensive report from multiple filtering results.

        Analyzes patterns across multiple filter operations to provide
        insights about content safety trends and system performance.

        Args:
            results: List of ContentFilterResult objects to analyze

        Returns:
            Dict: Comprehensive analysis report
        """
        # Validate input
        if not results:
            return {"error": "No results provided"}

        # Calculate basic statistics
        # Total texts analyzed
        total_texts = len(results)
        texts_with_violations = sum(
            1 for r in results if r.has_violations)  # Texts with issues
        total_matches = sum(len(r.matches)
                            for r in results)          # Total violations found

        # Analyze violation categories and severity distribution
        category_counts = {}  # Count violations by category
        # Count by severity
        severity_counts = {level.name: 0 for level in SeverityLevel}

        # Process each result for category and severity analysis
        for result in results:
            for match in result.matches:
                # Count category occurrences
                category_counts[match.category] = category_counts.get(
                    match.category, 0) + 1
                # Count severity level occurrences
                severity_counts[match.severity.name] += 1

        # Calculate performance metrics
        avg_processing_time = np.mean(
            [r.processing_time for r in results])  # Average processing time
        # Maximum processing time
        max_processing_time = max([r.processing_time for r in results])

        # Compile comprehensive report
        return {
            "summary": {
                # Total analysis count
                "total_texts_analyzed": total_texts,
                "texts_with_violations": texts_with_violations,               # Violation count
                # Percentage with violations
                "violation_rate": texts_with_violations / total_texts * 100,
                # Total violations found
                "total_matches": total_matches,
                # Average violations per text
                "avg_matches_per_text": total_matches / total_texts
            },
            "category_analysis": category_counts,      # Breakdown by violation category
            "severity_analysis": severity_counts,      # Breakdown by severity level
            "performance": {
                "avg_processing_time_ms": avg_processing_time * 1000,  # Average time in milliseconds
                # Maximum time in milliseconds
                "max_processing_time_ms": max_processing_time * 1000
            },
            # Actionable recommendations
            "recommendations": self._generate_recommendations(results)
        }

    def _generate_recommendations(self, results: List[ContentFilterResult]) -> List[str]:
        """
        Generate recommendations based on analysis results.

        Provides actionable insights based on patterns found in
        the filtering results to improve system safety.

        Args:
            results: List of ContentFilterResult objects

        Returns:
            List[str]: List of recommendation strings
        """
        recommendations = []  # Initialize recommendations list

        # Calculate violation rate for high-level recommendations
        violation_rate = sum(
            1 for r in results if r.has_violations) / len(results) * 100

        # High violation rate recommendation
        if violation_rate > 50:
            recommendations.append(
                f"High violation rate detected ({violation_rate:.1f}%). Consider reviewing input sources."
            )

        # Analyze category-specific patterns
        category_counts = {}
        for result in results:
            for match in result.matches:
                category_counts[match.category] = category_counts.get(
                    match.category, 0) + 1

        # Critical category recommendations
        if category_counts.get('self_harm', 0) > 0:
            recommendations.append(
                "Self-harm related content detected. Ensure crisis intervention protocols are in place."
            )

        # Academic stress pattern recommendations
        if category_counts.get('academic_distress', 0) > len(results) * 0.3:
            recommendations.append(
                "High frequency of academic distress content. Consider implementing additional academic support features."
            )

        return recommendations  # Return compiled recommendations
