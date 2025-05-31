"""
Enhanced Gradio interface module for SootheAI with professional chatbot design.
"""

import logging
import gradio as gr
from typing import Optional, Tuple, List, Dict, Any
# ADD THESE IMPORTS:
from ..core.api_client import get_claude_client
from ..utils.safety import check_input_safety, filter_response_safety
from ..utils.tts_audit_utils import get_tts_statistics, create_tts_report, format_tts_report_for_display
from ..core.narrative_engine import create_narrative_engine, CONSENT_MESSAGE
from ..models.game_state import GameState
from ..ui.tts_handler import get_tts_handler

logger = logging.getLogger(__name__)


def process_tts_commands(self, message: str) -> Tuple[bool, Optional[str]]:
    """Process TTS-related commands."""
    is_tts_command, tts_response = self.tts_handler.process_command(message)
    return is_tts_command, tts_response


class GradioInterface:
    """Enhanced Gradio interface for SootheAI with professional chatbot design."""

    def __init__(self, elevenlabs_client=None):
        # Enhanced color palette with professional design
        self.colors = {
            'primary': '#2563eb',        # Rich blue
            'primary_light': '#3b82f6',  # Lighter blue
            'primary_dark': '#1d4ed8',   # Darker blue
            'secondary': '#64748b',      # Slate gray
            'accent': '#10b981',         # Emerald green
            'accent_light': '#34d399',   # Light emerald
            'background': '#f8fafc',     # Very light gray-blue
            'surface': '#ffffff',        # Pure white
            'surface_alt': '#f1f5f9',    # Light gray-blue
            'surface_hover': '#f8fafc',  # Surface hover state
            'text_primary': '#0f172a',   # Very dark slate
            'text_secondary': '#334155',  # Medium slate
            'text_muted': '#64748b',     # Light slate
            'border': '#e2e8f0',         # Light border
            'border_light': '#f1f5f9',   # Even lighter border
            'border_focus': '#3b82f6',   # Blue focus border
            'success': '#059669',        # Success green
            'warning': '#d97706',        # Warning orange
            'error': '#dc2626',          # Error red
            'gradient_start': '#667eea',  # Gradient start
            'gradient_end': '#764ba2',   # Gradient end
            'chat_bg': '#fafbfc',        # Chat background
            'user_bubble': '#2563eb',    # User message bubble
            'bot_bubble': '#ffffff',     # Bot message bubble
            'shadow_sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        }

        self.claude_client = get_claude_client()
        self.narrative_engine = create_narrative_engine()
        self.tts_handler = get_tts_handler(elevenlabs_client)
        self.interface = None
        self.conversation_history = []

        # Enhanced consent message with better formatting
        self.consent_message = """
🌸 Welcome to SootheAI

*Your supportive companion for understanding anxiety through interactive storytelling*

🎯 What You'll Experience
SootheAI is an educational tool designed to help Singapore's youth explore anxiety management through engaging, AI-powered stories. This is **not a medical treatment** but a supportive learning environment.

⚠️ Important Disclaimer
**SootheAI provides educational support only.** If you're experiencing distress or mental health concerns, please seek professional help from qualified practitioners.

🎧 Choose Your Experience
- **Type 'I agree with audio'** - For immersive voice narration
- **Type 'I agree without audio'** - For peaceful text-only experience

*You can change audio settings anytime by typing 'enable audio' or 'disable audio'*

🤗 **Ready when you are!** Take your time and begin when you feel comfortable.
"""

        logger.info(
            "SootheAI Gradio interface initialized with professional design")

    def create_enhanced_css(self) -> str:
        """Create comprehensive CSS with professional chatbot design"""
        return f"""
        /* Import modern fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
        
        /* Global styles and variables */
        :root {{
            --primary-color: {self.colors['primary']};
            --primary-light: {self.colors['primary_light']};
            --accent-color: {self.colors['accent']};
            --accent-light: {self.colors['accent_light']};
            --text-primary: {self.colors['text_primary']};
            --text-secondary: {self.colors['text_secondary']};
            --text-muted: {self.colors['text_muted']};
            --surface: {self.colors['surface']};
            --background: {self.colors['background']};
            --border: {self.colors['border']};
            --border-focus: {self.colors['border_focus']};
            --chat-bg: {self.colors['chat_bg']};
            --user-bubble: {self.colors['user_bubble']};
            --bot-bubble: {self.colors['bot_bubble']};
            --border-radius: 12px;
            --border-radius-lg: 16px;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }}

        /* Base styling */
        html, body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: var(--text-primary);
            line-height: 1.6;
        }}

        /* Main container improvements */
        .gradio-container {{
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(20px) !important;
            border-radius: var(--border-radius-lg) !important;
            box-shadow: var(--shadow-xl) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            margin: 20px !important;
            max-width: calc(100vw - 40px) !important;
        }}

        /* Enhanced Tab styling */
        .gradio-container .gradio-tabs {{
            background: transparent !important;
            margin-bottom: 20px !important;
        }}

        .gradio-container .gradio-tabs .tab-nav {{
            background: rgba(255, 255, 255, 0.95) !important;
            border-radius: 16px !important;
            padding: 12px !important;
            display: flex !important;
            gap: 8px !important;
            justify-content: center !important;
            flex-wrap: wrap !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
        }}

        .gradio-container .gradio-tabs .tab-nav button {{
            background: transparent !important;
            color: #64748b !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 12px 20px !important;
            margin: 0 !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            min-width: 120px !important;
            text-align: center !important;
            position: relative !important;
            overflow: hidden !important;
            box-shadow: none !important;
        }}

        .gradio-container .gradio-tabs .tab-nav button:hover {{
            background: rgba(59, 130, 246, 0.1) !important;
            color: #2563eb !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15) !important;
        }}

        .gradio-container .gradio-tabs .tab-nav button.selected {{
            background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
            color: white !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
            transform: translateY(-2px) !important;
        }}

        /* PROFESSIONAL CHATBOT STYLING */
        
        /* Chat container */
        .chat-tab .gradio-container {{
            max-width: 1200px !important;
            margin: 0 auto !important;
            padding: 0 !important;
        }}

        /* Chatbot main container */
        .gradio-container .chatbot {{
            background: #1e293b !important;  /* Dark background */
            border: 1px solid #475569 !important;  /* Dark border */
            border-radius: 20px !important;
            box-shadow: var(--shadow-lg) !important;
            padding: 0 !important;
            margin: 20px !important;
            overflow: hidden !important;
            position: relative !important;
        }}

        /* Chat header */
        .chatbot::before {{
            display: none !important;
        }}

        /* Chat messages container */
        .gradio-container .chatbot .message-container,
        .gradio-container .chatbot > div {{
            padding: 24px !important;
            max-height: 60vh !important;
            overflow-y: auto !important;
            scroll-behavior: smooth !important;
            background: #1e293b !important;
        }}

        /* Individual message styling */
        .gradio-container .chatbot .message {{
            margin: 16px 0 !important;
            padding: 0 !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            display: flex !important;
            align-items: flex-start !important;
            gap: 12px !important;
        }}

        /* User messages (right-aligned) */
        .gradio-container .chatbot .message.user,
        .gradio-container .chatbot .message:nth-child(odd) {{
            flex-direction: row-reverse !important;
            margin-left: 80px !important;
            margin-right: 0 !important;
        }}

        .gradio-container .chatbot .message.user .message-content,
        .gradio-container .chatbot .message:nth-child(odd) .message-content,
        .gradio-container .chatbot .message:nth-child(odd) > div:last-child {{
            background: linear-gradient(135deg, var(--user-bubble), var(--primary-light)) !important;
            color: white !important;
            padding: 16px 20px !important;
            border-radius: 20px 20px 8px 20px !important;
            box-shadow: var(--shadow-md) !important;
            border: none !important;
            margin: 0 !important;
            max-width: 100% !important;
            word-wrap: break-word !important;
        }}

        /* Bot messages (left-aligned) */
        .gradio-container .chatbot .message.bot,
        .gradio-container .chatbot .message:nth-child(even) {{
            margin-right: 80px !important;
            margin-left: 0 !important;
        }}

        .gradio-container .chatbot .message.bot .message-content,
        .gradio-container .chatbot .message:nth-child(even) .message-content,
        .gradio-container .chatbot .message:nth-child(even) > div:last-child {{
            background: var(--bot-bubble) !important;
            color: var(--text-secondary) !important;
            padding: 16px 20px !important;
            border-radius: 20px 20px 20px 8px !important;
            box-shadow: var(--shadow-md) !important;
            border: 1px solid var(--border) !important;
            margin: 0 !important;
            max-width: 100% !important;
            word-wrap: break-word !important;
            position: relative !important;
        }}

        /* Message avatars */
        .gradio-container .chatbot .message::before {{
            content: "";
            width: 40px;
            height: 40px;
            border-radius: 50%;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: 600;
            box-shadow: var(--shadow-sm);
        }}

        .gradio-container .chatbot .message.user::before,
        .gradio-container .chatbot .message:nth-child(odd)::before {{
            content: "👤";
            background: linear-gradient(135deg, var(--accent-color), var(--accent-light));
            color: white;
            order: 2;
        }}

        .gradio-container .chatbot .message.bot::before,
        .gradio-container .chatbot .message:nth-child(even)::before {{
            content: "🤖";
            background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
            color: white;
        }}

        /* Typing indicator */
        .chatbot .typing-indicator {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px 20px;
            background: var(--bot-bubble);
            border-radius: 20px 20px 20px 8px;
            margin: 16px 80px 16px 52px;
            box-shadow: var(--shadow-sm);
        }}

        .typing-indicator::after {{
            content: "SootheAI is typing";
            animation: pulse 1.5s infinite;
            color: var(--text-muted);
            font-style: italic;
        }}

        /* Enhanced input area */
        .gradio-container .chat-interface-input {{
            background: white !important;
            border: 2px solid var(--border) !important;
            border-radius: 25px !important;
            padding: 16px 24px !important;
            margin: 20px !important;
            box-shadow: var(--shadow-lg) !important;
            transition: all 0.3s ease !important;
            position: relative !important;
        }}

        .gradio-container .chat-interface-input:focus-within {{
            border-color: var(--border-focus) !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1), var(--shadow-lg) !important;
        }}

        /* Input textbox styling */
        .gradio-container input[type="text"].soothe-textbox,
        .gradio-container textarea.soothe-textbox {{
            background: transparent !important;
            border: none !important;
            border-radius: 0 !important;
            padding: 4px 0 !important;
            font-size: 16px !important;
            line-height: 1.5 !important;
            resize: none !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        .gradio-container input[type="text"].soothe-textbox::placeholder,
        .gradio-container textarea.soothe-textbox::placeholder {{
            color: var(--text-muted) !important;
            opacity: 0.7 !important;
        }}

        /* Send button styling */
        .gradio-container .chat-interface-input button {{
            background: linear-gradient(135deg, var(--primary-color), var(--primary-light)) !important;
            color: white !important;
            border: none !important;
            border-radius: 20px !important;
            padding: 12px 20px !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            cursor: pointer !important;
            transition: all 0.3s ease !important;
            box-shadow: var(--shadow-md) !important;
            position: absolute !important;
            right: 8px !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
        }}

        .gradio-container .chat-interface-input button:hover {{
            background: linear-gradient(135deg, var(--primary-light), var(--primary-color)) !important;
            transform: translateY(-50%) scale(1.05) !important;
            box-shadow: var(--shadow-lg) !important;
        }}

        .gradio-container .chat-interface-input button:active {{
            transform: translateY(-50%) scale(0.98) !important;
        }}

        /* Examples styling */
        .gradio-container .examples {{
            background: #334155 !important;
            border: 1px solid #475569 !important;
            border-radius: var(--border-radius-lg) !important;
            padding: 20px !important;
            margin: 20px !important;
            box-shadow: var(--shadow-sm) !important;
        }}

        .gradio-container .examples h4 {{
            color: #f1f5f9 !important;
            font-weight: 600 !important;
            margin-bottom: 12px !important;
            font-size: 16px !important;
        }}

        .gradio-container .examples button {{
            background: #475569 !important;
            color: #f1f5f9 !important;
            border: 1px solid var(--border) !important;
            border-radius: 20px !important;
            padding: 8px 16px !important;
            margin: 4px 8px 4px 0 !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            transition: all 0.3s ease !important;
            box-shadow: var(--shadow-sm) !important;
        }}

        .gradio-container .examples button:hover {{
            background: var(--primary-color) !important;
            color: white !important;
            border-color: var(--primary-color) !important;
            transform: translateY(-2px) !important;
            box-shadow: var(--shadow-md) !important;
        }}

        /* Scrollbar styling for chat */
        .gradio-container .chatbot ::-webkit-scrollbar {{
            width: 6px !important;
        }}

        .gradio-container .chatbot ::-webkit-scrollbar-track {{
            background: var(--background) !important;
            border-radius: 3px !important;
        }}

        .gradio-container .chatbot ::-webkit-scrollbar-thumb {{
            background: var(--border) !important;
            border-radius: 3px !important;
        }}

        .gradio-container .chatbot ::-webkit-scrollbar-thumb:hover {{
            background: var(--text-muted) !important;
        }}

        /* Message content formatting */
        .gradio-container .chatbot .message h1,
        .gradio-container .chatbot .message h2,
        .gradio-container .chatbot .message h3 {{
            color: inherit !important;
            margin: 12px 0 8px 0 !important;
            line-height: 1.3 !important;
        }}

        .gradio-container .chatbot .message p {{
            margin: 8px 0 !important;
            line-height: 1.6 !important;
        }}

        .gradio-container .chatbot .message ul,
        .gradio-container .chatbot .message ol {{
            margin: 8px 0 !important;
            padding-left: 20px !important;
        }}

        .gradio-container .chatbot .message li {{
            margin: 4px 0 !important;
        }}

        .gradio-container .chatbot .message code {{
            background: rgba(0, 0, 0, 0.1) !important;
            padding: 2px 6px !important;
            border-radius: 4px !important;
            font-family: 'JetBrains Mono', monospace !important;
        }}

        .gradio-container .chatbot .message pre {{
            background: rgba(0, 0, 0, 0.05) !important;
            padding: 12px !important;
            border-radius: 8px !important;
            overflow-x: auto !important;
            margin: 8px 0 !important;
        }}

        /* Mobile responsiveness */
        @media (max-width: 768px) {{
            .gradio-container .chatbot {{
                margin: 10px !important;
                border-radius: 16px !important;
            }}
            
            .gradio-container .chatbot .message.user,
            .gradio-container .chatbot .message:nth-child(odd) {{
                margin-left: 40px !important;
            }}
            
            .gradio-container .chatbot .message.bot,
            .gradio-container .chatbot .message:nth-child(even) {{
                margin-right: 40px !important;
            }}

            .gradio-container .chat-interface-input {{
                margin: 10px !important;
                padding: 12px 16px !important;
            }}
            
            .gradio-container .examples {{
                margin: 10px !important;
                padding: 16px !important;
            }}
        }}

        /* Animation keyframes */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}

        @keyframes slideUp {{
            from {{ transform: translateY(20px); opacity: 0; }}
            to {{ transform: translateY(0); opacity: 1; }}
        }}

        /* Message animations */
        .gradio-container .chatbot .message {{
            animation: slideUp 0.3s ease-out !important;
        }}

        /* Focus indicators for accessibility */
        .gradio-container button:focus,
        .gradio-container input:focus,
        .gradio-container textarea:focus {{
            outline: 2px solid var(--accent-color) !important;
            outline-offset: 2px !important;
        }}

        /* Status indicators */
        .chat-status {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(16, 185, 129, 0.1);
            border-radius: 20px;
            margin: 10px 20px;
            font-size: 14px;
            color: var(--success);
            border: 1px solid rgba(16, 185, 129, 0.2);
        }}

        .chat-status::before {{
            content: "🟢";
            font-size: 12px;
        }}

        /* Enhanced content sections */
        .soothe-content-section {{
            background: linear-gradient(145deg, white, #f8fafc) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--border-radius-lg) !important;
            padding: 32px !important;
            margin: 24px 0 !important;
            box-shadow: var(--shadow-md) !important;
            transition: all 0.3s ease !important;
        }}

        .soothe-content-section:hover {{
            box-shadow: var(--shadow-lg) !important;
            transform: translateY(-2px) !important;
        }}

        .soothe-content-section h2 {{
            color: var(--primary-color) !important;
            font-family: 'Space Grotesk', sans-serif !important;
            font-weight: 600 !important;
            font-size: 28px !important;
            margin-bottom: 16px !important;
            display: flex !important;
            align-items: center !important;
            gap: 12px !important;
        }}

        /* Feature cards */
        .soothe-feature-card {{
            background: linear-gradient(145deg, white, #f8fafc) !important;
            border: 1px solid var(--border) !important;
            border-radius: var(--border-radius-lg) !important;
            padding: 24px !important;
            text-align: center !important;
            transition: all 0.3s ease !important;
            box-shadow: var(--shadow-md) !important;
            min-height: 200px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }}

        .soothe-feature-card:hover {{
            transform: translateY(-4px) scale(1.02) !important;
            box-shadow: var(--shadow-xl) !important;
            border-color: var(--accent-color) !important;
        }}

        /* Typography improvements */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Space Grotesk', sans-serif !important;
            color: var(--text-primary) !important;
            line-height: 1.3 !important;
        }}

        /* Links */
        a {{
            color: var(--primary-color) !important;
            text-decoration: none !important;
            font-weight: 500 !important;
            transition: color 0.2s ease !important;
        }}

        a:hover {{
            color: var(--primary-light) !important;
            text-decoration: underline !important;
        }}

        .gradio-container .chatbot,
        .gradio-container .chatbot > *,
        .gradio-container .chatbot div,
        .gradio-container .chatbot .wrap,
        .gradio-container .chatbot .contain,
        .gradio-container .chatbot .message-wrap,
        .gradio-container .chatbot .message-container {{
            background: #1e293b !important;
            background-color: #1e293b !important;
        }}

        /* Target the specific Gradio chat elements */
        .gradio-container [data-testid="chatbot"],
        .gradio-container [data-testid="chatbot"] > div,
        .gradio-container [data-testid="chatbot"] .overflow-y-auto {{
            background: #1e293b !important;
            background-color: #1e293b !important;
        }}

        /* Override any inherited white backgrounds */
        .gradio-container .chatbot * {{
            background-color: transparent !important;
        }}

        .gradio-container .chatbot .prose {{
            background: transparent !important;
        }}
        """

    def create_enhanced_homepage(self) -> str:
        """Create an enhanced homepage with modern design"""
        return f'''
        <div style="
            background: linear-gradient(135deg, {self.colors['gradient_start']}, {self.colors['gradient_end']}) !important;
            color: white !important;
            padding: 60px 20px !important;
            text-align: center !important;
            border-radius: 20px !important;
            margin-bottom: 30px !important;
            box-shadow: var(--shadow-xl) !important;
            border: none !important;
            outline: none !important;
        ">
            <div style="
                display: inline-flex !important;
                align-items: center !important;
                background: rgba(255, 182, 193, 0.2) !important;
                border-radius: 50px !important;
                padding: 8px 20px !important;
                margin-bottom: 30px !important;
                backdrop-filter: blur(10px) !important;
                border: 1px solid rgba(255, 182, 193, 0.3) !important;
            ">
                <span style="font-size: 24px !important; margin-right: 10px !important;">🌱</span>
                <span style="font-weight: 600 !important; font-size: 14px !important; letter-spacing: 1px !important; color: white !important;">AI-POWERED MENTAL HEALTH SUPPORT</span>
            </div>

            <h1 style="
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: clamp(2.5rem, 5vw, 4rem) !important;
                font-weight: 700 !important;
                margin-bottom: 20px !important;
                background: linear-gradient(45deg, #ffffff, #f0f9ff) !important;
                -webkit-background-clip: text !important;
                background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
                line-height: 1.1 !important;
            ">
                Welcome to<br>
                <span style="background: linear-gradient(45deg, #10b981, #34d399, #6ee7b7, #10b981); background-size: 300% 300%; -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; animation: gradientShift 3s ease-in-out infinite;">SootheAI</span>
            </h1>

            <p style="
                font-size: 1.3rem !important;
                margin-bottom: 40px !important;
                opacity: 0.9 !important;
                max-width: 600px !important;
                margin-left: auto !important;
                margin-right: auto !important;
                line-height: 1.6 !important;
                color: white !important;
            ">
                Navigate anxiety through interactive storytelling designed specifically for Singapore's youth
            </p>

            <div style="
                display: flex !important;
                gap: 20px !important;
                justify-content: center !important;
                flex-wrap: wrap !important;
                margin-bottom: 40px !important;
            ">
                <div style="
                    background: rgba(255, 255, 255, 0.1) !important;
                    padding: 8px 16px !important;
                    border-radius: 25px !important;
                    border: 1px solid rgba(255, 255, 255, 0.2) !important;
                    backdrop-filter: blur(10px) !important;
                    font-size: 14px !important;
                    font-weight: 500 !important;
                    color: white !important;
                ">
                    ✨ Safe & Private
                </div>
                <div style="
                    background: rgba(255, 255, 255, 0.1) !important;
                    padding: 8px 16px !important;
                    border-radius: 25px !important;
                    border: 1px solid rgba(255, 255, 255, 0.2) !important;
                    backdrop-filter: blur(10px) !important;
                    font-size: 14px !important;
                    font-weight: 500 !important;
                    color: white !important;
                ">
                    🎓 Educational Focus
                </div>
                <div style="
                    background: rgba(255, 255, 255, 0.1) !important;
                    padding: 8px 16px !important;
                    border-radius: 25px !important;
                    border: 1px solid rgba(255, 255, 255, 0.2) !important;
                    backdrop-filter: blur(10px) !important;
                    font-size: 14px !important;
                    font-weight: 500 !important;
                    color: white !important;
                ">
                    🇸🇬 Singapore Context
                </div>
            </div>

            <button onclick="
                Array.from(document.querySelectorAll('button, .tabitem, .tab-nav button')).forEach(btn => {{
                    if (btn.innerText.trim().includes('SootheAI Chat')) btn.click();
                }});
            " style="
                background: linear-gradient(135deg, {self.colors['accent']}, {self.colors['accent_light']});
                color: white;
                border: none;
                padding: 16px 32px;
                border-radius: 50px;
                font-size: 18px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
                border: 2px solid rgba(255, 255, 255, 0.2);
            " onmouseover="
                this.style.transform = 'translateY(-3px) scale(1.05)';
                this.style.boxShadow = '0 15px 35px rgba(16, 185, 129, 0.4)';
            " onmouseout="
                this.style.transform = 'translateY(0) scale(1)';
                this.style.boxShadow = '0 8px 25px rgba(16, 185, 129, 0.3)';
            ">
                🚀 Start Your Journey
            </button>
            
            <style>
                @keyframes gradientShift {{
                    0%, 100% {{ background-position: 0% 50%; }}
                    50% {{ background-position: 100% 50%; }}
                }}
            </style>
        </div>

        <div style="
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 30px;
            margin: 40px 0;
        ">
            {self._create_feature_card("📖", "Interactive Stories", "Experience relatable scenarios through AI-powered storytelling", "#3b82f6")}
            {self._create_feature_card("🎯", "Personalized Learning", "AI adapts to your choices for a unique learning experience", "#10b981")}
            {self._create_feature_card("🤝", "Safe Environment", "Learn anxiety management in a supportive, judgment-free space", "#f59e0b")}
            {self._create_feature_card("🇸🇬", "Local Context", "Stories set in familiar Singaporean school environments", "#ef4444")}
        </div>
        '''

    def _create_feature_card(self, icon: str, title: str, description: str, accent_color: str) -> str:
        """Create an enhanced feature card with icon-based background colors"""
        return f'''
        <div style="
            background: linear-gradient(145deg, {accent_color}, {accent_color}dd) !important;
            border: 1px solid {accent_color} !important;
            border-radius: 20px !important;
            padding: 30px 20px !important;
            text-align: center !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 20px {accent_color}33 !important;
            position: relative !important;
            overflow: hidden !important;
            color: white !important;
            min-height: 200px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        " onmouseover="
            this.style.transform = 'translateY(-8px) scale(1.02)';
            this.style.boxShadow = '0 20px 40px {accent_color}55';
            this.style.background = 'linear-gradient(145deg, {accent_color}ee, {accent_color}) !important';
        " onmouseout="
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 4px 20px {accent_color}33';
            this.style.background = 'linear-gradient(145deg, {accent_color}, {accent_color}dd) !important';
        ">
            <div style="
                position: absolute !important;
                top: 0 !important;
                left: 0 !important;
                right: 0 !important;
                height: 4px !important;
                background: linear-gradient(90deg, rgba(255,255,255,0.5), rgba(255,255,255,0.2)) !important;
            "></div>
            
            <div style="
                font-size: 3.5rem !important;
                margin-bottom: 20px !important;
                background: rgba(255, 255, 255, 0.2) !important;
                width: 80px !important;
                height: 80px !important;
                border-radius: 20px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                margin: 0 auto 20px auto !important;
                box-shadow: 0 8px 25px rgba(0,0,0,0.2) !important;
                backdrop-filter: blur(10px) !important;
            ">
                <span style="filter: none !important;">{icon}</span>
            </div>
            
            <h3 style="
                color: white !important;
                font-family: 'Space Grotesk', sans-serif !important;
                font-size: 1.4rem !important;
                font-weight: 700 !important;
                margin-bottom: 12px !important;
                line-height: 1.3 !important;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
            ">{title}</h3>
            
            <p style="
                color: rgba(255, 255, 255, 0.9) !important;
                line-height: 1.6 !important;
                margin: 0 !important;
                font-size: 1rem !important;
                font-weight: 500 !important;
                text-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
            ">{description}</p>
        </div>
        '''

    def create_anxiety_education_content(self) -> str:
        """Create enhanced anxiety education content"""
        return f'''
        <div class="soothe-content-section">
            <h2>
                <span style="
                    background: linear-gradient(135deg, {self.colors['accent']}, {self.colors['accent_light']});
                    color: white;
                    padding: 8px 12px;
                    border-radius: 10px;
                    margin-right: 10px;
                ">📚</span>
                Understanding Anxiety
            </h2>
            
            <div style="
                background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
                padding: 24px;
                border-radius: 16px;
                border-left: 5px solid {self.colors['accent']};
                margin: 20px 0;
            ">
                <h3>What is Anxiety?</h3>
                <p>Anxiety is a natural response to stress that everyone experiences. However, when anxiety becomes overwhelming or persistent, it can impact daily life and wellbeing. In Singapore's competitive academic environment, many students face anxiety related to performance pressure.</p>
            </div>

            <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 24px;
                margin: 30px 0;
            ">
                <div style="
                    background: linear-gradient(135deg, #fef3c7, #fde68a);
                    padding: 24px;
                    border-radius: 16px;
                    border-left: 5px solid {self.colors['warning']};
                ">
                    <h3 style="color: #92400e;">⚠️ Common Signs</h3>
                    <ul style="color: #78350f; line-height: 1.8;">
                        <li><strong>Physical:</strong> Racing heart, sweating, difficulty breathing</li>
                        <li><strong>Emotional:</strong> Persistent worry, irritability, restlessness</li>
                        <li><strong>Behavioral:</strong> Avoidance, procrastination, perfectionism</li>
                        <li><strong>Cognitive:</strong> Racing thoughts, difficulty concentrating</li>
                    </ul>
                </div>

                <div style="
                    background: linear-gradient(135deg, #d1fae5, #a7f3d0);
                    padding: 24px;
                    border-radius: 16px;
                    border-left: 5px solid {self.colors['success']};
                ">
                    <h3 style="color: #065f46;">💡 Healthy Coping</h3>
                    <ul style="color: #064e3b; line-height: 1.8;">
                        <li><strong>Breathing:</strong> Deep, slow breathing exercises</li>
                        <li><strong>Mindfulness:</strong> Present-moment awareness practices</li>
                        <li><strong>Exercise:</strong> Regular physical activity</li>
                        <li><strong>Support:</strong> Talking to trusted friends or professionals</li>
                    </ul>
                </div>
            </div>

            <div style="
                background: linear-gradient(135deg, {self.colors['primary']}15, {self.colors['accent']}15);
                padding: 24px;
                border-radius: 16px;
                border: 2px solid {self.colors['primary']}30;
                text-align: center;
                margin-top: 30px;
            ">
                <h3 style="color: {self.colors['primary']};">🎯 Ready to Practice?</h3>
                <p>Experience these concepts through interactive stories where you can explore different coping strategies in realistic scenarios.</p>
                <button onclick="
                    Array.from(document.querySelectorAll('button, .tabitem, .tab-nav button')).forEach(btn => {{
                        if (btn.innerText.trim().includes('SootheAI Chat')) btn.click();
                    }});
                " style="
                    background: linear-gradient(135deg, {self.colors['primary']}, {self.colors['primary_light']});
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 25px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    margin-top: 15px;
                " onmouseover="this.style.transform = 'scale(1.05)'" onmouseout="this.style.transform = 'scale(1)'">
                    Start Interactive Learning →
                </button>
            </div>
        </div>
        '''

    def create_helpline_content(self) -> str:
        """Create enhanced helpline content with better visual hierarchy"""
        return f'''
        <div class="soothe-content-section">
            <h2>
                <span style="
                    background: linear-gradient(135deg, {self.colors['error']}, #ef4444);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 10px;
                    margin-right: 10px;
                ">🆘</span>
                Mental Health Support
            </h2>

            <div style="
                background: linear-gradient(135deg, #fef2f2, #fee2e2);
                padding: 24px;
                border-radius: 16px;
                border: 2px solid #fca5a5;
                margin: 20px 0;
                text-align: center;
            ">
                <h3 style="color: #991b1b; margin-bottom: 15px;">🚨 Emergency Contacts</h3>
                <p style="color: #7f1d1d; font-weight: 500; margin-bottom: 20px;">
                    If you or someone you know is experiencing a mental health emergency, please contact these 24/7 helplines:
                </p>
                
                <div style="
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 16px;
                    margin-top: 20px;
                ">
                    <div style="
                        background: white;
                        padding: 16px;
                        border-radius: 12px;
                        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.1);
                        border-left: 4px solid {self.colors['error']};
                    ">
                        <strong style="color: {self.colors['error']};">Emergency</strong><br>
                        <span style="font-size: 1.5rem; font-weight: 700; color: {self.colors['error']};">999</span>
                    </div>
                    <div style="
                        background: white;
                        padding: 16px;
                        border-radius: 12px;
                        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.1);
                        border-left: 4px solid {self.colors['error']};
                    ">
                        <strong style="color: {self.colors['error']};">SOS Helpline</strong><br>
                        <span style="font-size: 1.5rem; font-weight: 700; color: {self.colors['error']};">1-767</span>
                    </div>
                    <div style="
                        background: white;
                        padding: 16px;
                        border-radius: 12px;
                        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.1);
                        border-left: 4px solid {self.colors['error']};
                    ">
                        <strong style="color: {self.colors['error']};">National Care</strong><br>
                        <span style="font-size: 1.2rem; font-weight: 700; color: {self.colors['error']};">1800-202-6868</span>
                    </div>
                </div>
            </div>

            <div style="
                background: linear-gradient(135deg, #eff6ff, #dbeafe);
                padding: 24px;
                border-radius: 16px;
                border-left: 5px solid {self.colors['primary']};
                margin: 20px 0;
            ">
                <h3 style="color: {self.colors['primary']};">🧑‍🎓 Youth-Specific Support</h3>
                
                <div style="display: grid; gap: 16px; margin-top: 16px;">
                    <div style="
                        background: white;
                        padding: 16px;
                        border-radius: 12px;
                        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.1);
                    ">
                        <h4 style="color: {self.colors['primary']}; margin: 0 0 8px 0;">CHAT (Community Health Assessment Team)</h4>
                        <p style="margin: 0 0 8px 0; color: {self.colors['text_muted']};">For youth aged 16-30</p>
                        <p style="margin: 0; font-weight: 600;">📞 6493-6500</p>
                    </div>
                    
                    <div style="
                        background: white;
                        padding: 16px;
                        border-radius: 12px;
                        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.1);
                    ">
                        <h4 style="color: {self.colors['primary']}; margin: 0 0 8px 0;">Tinkle Friend</h4>
                        <p style="margin: 0 0 8px 0; color: {self.colors['text_muted']};">For primary school children</p>
                        <p style="margin: 0; font-weight: 600;">📞 1800-274-4788</p>
                    </div>
                </div>
            </div>

            <div style="
                background: linear-gradient(135deg, {self.colors['success']}15, {self.colors['accent_light']}15);
                padding: 24px;
                border-radius: 16px;
                border: 2px solid {self.colors['success']}30;
                text-align: center;
            ">
                <div style="
                    background: linear-gradient(135deg, {self.colors['success']}, {self.colors['accent_light']});
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 20px auto;
                    font-size: 24px;
                ">💚</div>
                <h3 style="color: {self.colors['success']};">You Are Not Alone</h3>
                <p>Reaching out for support is a sign of strength, not weakness. Mental health professionals are trained to help you navigate difficult emotions and experiences.</p>
            </div>
        </div>
        '''

    def create_about_content(self) -> str:
        """Create enhanced about content"""
        return f'''
        <div class="soothe-content-section">
            <h2>
                <span style="
                    background: linear-gradient(135deg, {self.colors['primary']}, {self.colors['primary_light']});
                    color: white;
                    padding: 8px 12px;
                    border-radius: 10px;
                    margin-right: 10px;
                ">ℹ️</span>
                About SootheAI
            </h2>

            <div style="
                display: grid;
                gap: 24px;
                margin: 30px 0;
            ">
                <div style="
                    background: linear-gradient(135deg, #eff6ff, #dbeafe);
                    padding: 24px;
                    border-radius: 16px;
                    border-left: 5px solid {self.colors['primary']};
                ">
                    <h3 style="color: {self.colors['primary']};">🎯 Our Mission</h3>
                    <p>SootheAI aims to help Singaporean youths understand, manage, and overcome anxiety through interactive storytelling enhanced by artificial intelligence. We believe that by engaging young people in relatable scenarios and providing them with practical coping strategies, we can make a meaningful impact on youth mental health in Singapore.</p>
                </div>

                <div style="
                    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
                    padding: 24px;
                    border-radius: 16px;
                    border-left: 5px solid {self.colors['success']};
                ">
                    <h3 style="color: {self.colors['success']};">🤖 Our Approach</h3>
                    <p>We combine the power of narrative storytelling with AI technology to create personalized learning experiences that adapt to each user's needs. Our stories are set in culturally relevant Singaporean contexts, addressing the unique pressures and challenges that local youth face.</p>
                    <p>Through interactive fiction, users can explore different scenarios, make choices, and learn about anxiety management techniques in a safe, engaging environment.</p>
                </div>

                <div style="
                    background: linear-gradient(135deg, #fdf4ff, #fae8ff);
                    padding: 24px;
                    border-radius: 16px;
                    border-left: 5px solid #a855f7;
                ">
                    <h3 style="color: #7c3aed;">👥 The Team</h3>
                    <p>SootheAI is developed by a team of mental health professionals, educational technologists, and AI specialists who are passionate about improving youth mental wellbeing in Singapore.</p>
                    <p>We work closely with psychologists, educators, and youth advisors to ensure that our content is accurate, appropriate, and effective.</p>
                </div>

                <div style="
                    background: linear-gradient(135deg, #fffbeb, #fef3c7);
                    padding: 24px;
                    border-radius: 16px;
                    border-left: 5px solid {self.colors['warning']};
                ">
                    <h3 style="color: #d97706;">📧 Contact Us</h3>
                    <p>If you have questions, feedback, or would like to learn more about SootheAI, please reach out to us at 
                    <a href="mailto:contact@sootheai.sg" style="
                        color: {self.colors['primary']};
                        font-weight: 600;
                        text-decoration: none;
                        border-bottom: 2px solid {self.colors['primary']}30;
                        transition: all 0.2s ease;
                    " onmouseover="this.style.borderBottomColor = '{self.colors['primary']}'" onmouseout="this.style.borderBottomColor = '{self.colors['primary']}30'">contact@sootheai.sg</a>.</p>
                </div>
            </div>

            <div style="
                background: linear-gradient(135deg, {self.colors['accent']}15, {self.colors['primary']}15);
                padding: 24px;
                border-radius: 16px;
                border: 2px solid {self.colors['accent']}30;
                text-align: center;
                margin-top: 30px;
            ">
                <h3 style="color: {self.colors['accent']};">🚀 Ready to Begin?</h3>
                <p>Start exploring anxiety management through interactive storytelling designed specifically for Singapore's youth.</p>
                <button onclick="
                    Array.from(document.querySelectorAll('button, .tabitem, .tab-nav button')).forEach(btn => {{
                        if (btn.innerText.trim().includes('SootheAI Chat')) btn.click();
                    }});
                " style="
                    background: linear-gradient(135deg, {self.colors['accent']}, {self.colors['accent_light']});
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 25px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    margin-top: 15px;
                " onmouseover="this.style.transform = 'scale(1.05)'" onmouseout="this.style.transform = 'scale(1)'">
                    Start Your Story →
                </button>
            </div>
        </div>
        '''

    def create_enhanced_theme(self) -> gr.Theme:
        """Create an enhanced Gradio theme"""
        return gr.themes.Soft(
            primary_hue=gr.themes.colors.blue,
            secondary_hue=gr.themes.colors.emerald,
            neutral_hue=gr.themes.colors.slate,
            font=[gr.themes.GoogleFont(
                "Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
            font_mono=[gr.themes.GoogleFont(
                "JetBrains Mono"), "Consolas", "monospace"],
        ).set(
            body_background_fill=f"linear-gradient(135deg, {self.colors['gradient_start']}, {self.colors['gradient_end']})",
            background_fill_primary=self.colors['background'],
            background_fill_secondary=self.colors['surface_alt'],
            block_background_fill=self.colors['surface'],
            input_background_fill=self.colors['surface'],
            button_primary_background_fill=f"linear-gradient(135deg, {self.colors['primary']}, {self.colors['primary_light']})",
            button_primary_background_fill_hover=f"linear-gradient(135deg, {self.colors['primary_light']}, {self.colors['primary']})",
            button_primary_text_color="white",
            button_secondary_background_fill=f"linear-gradient(135deg, {self.colors['accent']}, {self.colors['accent_light']})",
            border_color_primary=self.colors['border'],
            border_color_accent=self.colors['border_focus'],
            body_text_color=self.colors['text_secondary'],
            body_text_color_subdued=self.colors['text_muted'],
        )

    def main_loop(self, message: Optional[str], history: List[Tuple[str, str]]) -> str:
        """Main game loop with enhanced error handling"""
        if message is None:
            logger.info("Processing empty message in main loop")
            return self.consent_message

        logger.info(
            f"Processing message: {message[:50] if message else ''}...")

        try:
            response, success = self.narrative_engine.process_message(message)

            if not success:
                logger.error(f"Narrative engine error: {response}")
                return "🤖 I apologize, but I encountered an error. Please try again or contact support if the issue persists."

            # TTS integration
            if (success and
                hasattr(self.narrative_engine, 'game_state') and
                self.narrative_engine.game_state.is_consent_given() and
                    message.lower() not in ['i agree', 'i agree with audio', 'i agree without audio', 'enable audio', 'disable audio', 'start game']):

                try:
                    self.tts_handler.run_tts_with_consent_and_limiting(
                        response)
                except Exception as e:
                    logger.warning(f"TTS failed: {e}")

            return response

        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            return "🤖 I apologize, but I encountered an unexpected error. Please try again or refresh the page if the issue continues."

    def create_interface(self) -> gr.Blocks:
        """Create the enhanced Gradio interface with professional chatbot design"""
        with gr.Blocks(
            theme=self.create_enhanced_theme(),
            title="SootheAI - Mental Health Support for Singapore's Youth",
            css=self.create_enhanced_css()
        ) as blocks:

            with gr.Tabs(elem_classes="soothe-tabs") as tabs:
                with gr.Tab("🏠 Home"):
                    gr.HTML(self.create_enhanced_homepage())

                with gr.Tab("💬 SootheAI Chat", elem_classes="chat-tab"):
                    # Professional chatbot interface
                    chat_interface = gr.ChatInterface(
                        self.main_loop,
                        chatbot=gr.Chatbot(
                            height="65vh",
                            placeholder="🌸 **Welcome to your safe space!** Your supportive conversation will begin here. Take your time and start when you're ready.",
                            show_copy_button=True,
                            render_markdown=True,
                            value=[[None, self.consent_message]],
                            avatar_images=None,
                            bubble_full_width=False,
                            show_share_button=False,
                            elem_classes="soothe-chatbot",
                            container=True,
                            scale=1,
                            min_width=300,
                        ),
                        textbox=gr.Textbox(
                            placeholder="💭 Share what's on your mind... (e.g., 'I agree with audio' or 'I'm feeling anxious about school')",
                            container=False,
                            scale=7,
                            lines=1,
                            max_lines=3,
                            elem_classes="soothe-textbox",
                            show_label=False,
                        ),
                        examples=[
                            "🎵 I agree with audio",
                            "📝 I agree without audio",
                            "🚀 Start my story",
                            "💡 Tell me about anxiety",
                            "🎯 I need help with school stress",
                            "🤝 What coping strategies can you teach me?"
                        ],
                        cache_examples=False,
                        title=None,
                        description=None,
                        submit_btn="Send Message",
                        retry_btn="↻ Retry",
                        undo_btn="↶ Undo",
                        clear_btn="🗑️ Clear",
                    )

                with gr.Tab("📚 Learn About Anxiety"):
                    gr.HTML(self.create_anxiety_education_content())

                with gr.Tab("🆘 Get Help"):
                    gr.HTML(self.create_helpline_content())

                with gr.Tab("ℹ️ About"):
                    gr.HTML(self.create_about_content())

        self.interface = blocks
        return blocks

    def launch(self, share: bool = True, server_name: str = "0.0.0.0", server_port: int = 7861) -> None:
        """Launch the enhanced interface"""
        if self.interface is None:
            self.create_interface()
        try:
            logger.info("Launching enhanced SootheAI interface...")
            self.interface.launch(
                share=share,
                server_name=server_name,
                server_port=server_port
            )
        except Exception as e:
            logger.error(f"Failed to launch Gradio interface: {str(e)}")
            raise

    def close(self) -> None:
        """Close the interface gracefully"""
        if self.interface is not None:
            try:
                self.interface.close()
                logger.info("Closed Gradio interface")
            except Exception as e:
                logger.error(f"Error closing Gradio interface: {str(e)}")


def create_gradio_interface(elevenlabs_client=None) -> GradioInterface:
    """
    Create an enhanced Gradio interface instance.

    Args:
        elevenlabs_client: Optional ElevenLabs client instance for TTS functionality

    Returns:
        GradioInterface: Configured interface instance ready for launch
    """
    return GradioInterface(elevenlabs_client)
