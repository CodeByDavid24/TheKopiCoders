"""
Enhanced Gradio interface module for SootheAI with improved design consistency, accessibility, and robust disclaimers.
"""

import logging
import gradio as gr
from typing import Optional, Tuple, List, Dict, Any
# ADD THESE IMPORTS:
from ..core.narrative_engine import create_narrative_engine, CONSENT_MESSAGE
from ..core.api_client import get_claude_client
from ..ui.tts_handler import get_tts_handler
from ..utils.safety import check_input_safety, filter_response_safety
from ..utils.tts_audit_utils import get_tts_statistics, create_tts_report, format_tts_report_for_display
from ..models.game_state import GameState

from ..core.narrative_engine import create_narrative_engine
from ..models.game_state import GameState
from ..ui.tts_handler import get_tts_handler

logger = logging.getLogger(__name__)

def process_tts_commands(self, message: str) -> Tuple[bool, Optional[str]]:
    """Process TTS-related commands."""
    is_tts_command, tts_response = self.tts_handler.process_command(message)
    return is_tts_command, tts_response

class GradioInterface:
    """Enhanced Gradio interface for SootheAI with improved design consistency and accessibility."""

    def __init__(self, elevenlabs_client=None):
        self.colors = {
            'primary': '#1E3A5F',
            'primary_light': '#2B4A75',
            'primary_dark': '#0F1F33',
            'primary_hover': '#344A66',
            'secondary': '#4A6B8A',
            'secondary_light': '#6B8BA8',
            'background': '#FAFBFC',
            'surface': '#FFFFFF',
            'surface_hover': '#F8F9FA',
            'surface_alt': '#F1F5F9',
            'surface_elevated': '#FFFFFF',
            'accent': '#0EA5E9',
            'accent_dark': '#0284C7',
            'accent_light': '#38BDF8',
            'accent_subtle': '#E0F2FE',
            'text_primary': '#0F172A',
            'text_secondary': '#334155',
            'text_tertiary': '#475569',
            'text_muted': '#64748B',
            'text_inverse': '#FFFFFF',
            'success': '#10B981',
            'success_light': '#D1FAE5',
            'warning': '#F59E0B',
            'warning_light': '#FEF3C7',
            'error': '#EF4444',
            'error_light': '#FEE2E2',
            'info': '#3B82F6',
            'info_light': '#DBEAFE',
            'border': '#E2E8F0',
            'border_light': '#F1F5F9',
            'border_focus': '#0EA5E9',
            'divider': '#E2E8F0',
            'shadow_sm': 'rgba(30, 58, 95, 0.05)',
            'shadow_md': 'rgba(30, 58, 95, 0.10)',
            'shadow_lg': 'rgba(30, 58, 95, 0.15)',
            'shadow_xl': 'rgba(30, 58, 95, 0.20)',
}

        self.narrative_engine = create_narrative_engine()  # Remove character_data parameter
        self.tts_handler = get_tts_handler(elevenlabs_client)
        self.interface = None

        self.disclaimer_banner = """
        <div style='
            background: linear-gradient(90deg, #f59e0b 0%, #fef3c7 100%);
            color: #1e293b;
            padding: 12px 24px;
            border-radius: 10px;
            margin-bottom: 24px;
            font-size: 16px;
            font-weight: 600;
            text-align: center;
            box-shadow: 0 2px 8px rgba(245, 158, 11, 0.08);
        '>
            ⚠️ <span style='color: #b45309;'>Disclaimer:</span> SootheAI is for educational awareness only.
            <b>It is not a medical or therapeutic tool.</b>
            If you are experiencing significant distress, 
            <a href='#helplines' style='color:#b91c1c; text-decoration:underline; font-weight:700;'>please seek help from a professional</a>
            or use the emergency contacts under "<b>🆘 Get Help</b>".
        </div>
        """

        self.consent_message = """
        **Welcome to SootheAI - Serena's Story**
        
        **Important Information:**
        This is a fictional story designed to help you understand anxiety. Please be aware that some of the content may depict distressing situations. **Do not replicate or engage in any harmful actions shown in the game.** If you're feeling distressed, we encourage you to seek professional help.
        
        Your choices and input will directly shape the direction of the story. Your decisions may influence the narrative, and some of your inputs might be used within the system to enhance your experience.
        
        **Audio Feature Option:**
        SootheAI can narrate the story using AI-generated speech. The audio is processed in real-time and not stored.
        
        **To begin:**
        Type 'I agree with audio' to enable voice narration
        OR
        Type 'I agree without audio' to continue with text only
        
        You can change audio settings at any time by typing 'enable audio' or 'disable audio'.
        """

        self.narrative_engine = create_narrative_engine()
        self.claude_client = get_claude_client()
        self.tts_handler = get_tts_handler(elevenlabs_client)
        
        # Track conversation for display
        self.conversation_history = []
        
        logger.info("SootheAI Gradio interface initialized with backend integration")

    def _get_font_imports(self) -> str:
        return """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
        """

    def _create_css_variables(self) -> str:
        variables = [":root {"]
        for key, value in self.colors.items():
            css_key = key.replace('_', '-')
            variables.append(f"  --color-{css_key}: {value};")
        variables.extend([
            "  --font-primary: 'Inter', ui-sans-serif, system-ui, sans-serif;",
            "  --font-heading: 'Space Grotesk', 'Inter', ui-sans-serif, system-ui, sans-serif;",
            "  --border-radius-sm: 6px;",
            "  --border-radius-md: 8px;",
            "  --border-radius-lg: 12px;",
            "  --border-radius-xl: 16px;",
            "  --border-radius-full: 9999px;",
            "  --spacing-xs: 4px;",
            "  --spacing-sm: 8px;",
            "  --spacing-md: 16px;",
            "  --spacing-lg: 24px;",
            "  --spacing-xl: 32px;",
            "  --spacing-2xl: 48px;",
            "  --transition-fast: 0.15s ease-out;",
            "  --transition-normal: 0.2s ease-out;",
            "  --transition-slow: 0.3s ease-out;",
            "  --shadow-sm: 0 1px 2px 0 var(--color-shadow-sm);",
            "  --shadow-md: 0 4px 6px -1px var(--color-shadow-md);",
            "  --shadow-lg: 0 10px 15px -3px var(--color-shadow-lg);",
            "  --shadow-xl: 0 20px 25px -5px var(--color-shadow-xl);",
            "}",
        ])
        return "\n".join(variables)

    def _create_page_wrapper(self, content: str) -> str:
        return f'''
        <div class="soothe-page-wrapper" style="
            width: 100%; 
            font-family: var(--font-primary);
            line-height: 1.6;
        ">
            {content}
        </div>
        '''



    def _create_section(self, title: str, content: str, extra_classes: str = "", icon: str = "") -> str:
        icon_html = f'<span class="section-icon" style="margin-right: 12px; font-size: 24px;">{icon}</span>' if icon else ''
        return f'''
        <div class="soothe-content-section {extra_classes}" style="
            background-color: var(--color-surface-elevated); 
            padding: var(--spacing-2xl); 
            border-radius: var(--border-radius-lg); 
            margin-bottom: var(--spacing-lg); 
            box-shadow: var(--shadow-md);
            border: 1px solid var(--color-border-light);
            transition: var(--transition-normal);
        ">
            <h2 style="
                color: var(--color-text-primary); 
                margin-bottom: var(--spacing-md); 
                font-size: 28px; 
                font-weight: 600;
                font-family: var(--font-heading);
                display: flex;
                align-items: center;
                letter-spacing: -0.025em;
            ">
                {icon_html}{title}
            </h2>
            <div style="
                color: var(--color-text-secondary); 
                line-height: 1.7; 
                margin: 0;
                font-size: 16px;
            ">
                {content}
            </div>
        </div>
        '''

    def _create_feature_card(self, icon: str, title: str, description: str, accent_color: str = None) -> str:
        accent_color = accent_color or "var(--color-accent)"
        return f'''
        <div class="soothe-feature-card" style="
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: var(--border-radius-lg);
            padding: var(--spacing-xl);
            text-align: center;
            transition: var(--transition-normal);
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, {accent_color}, var(--color-accent-light));
            "></div>
            <div class="feature-icon" style="
                background: linear-gradient(135deg, {accent_color}, var(--color-accent-light));
                width: 64px;
                height: 64px;
                border-radius: var(--border-radius-lg);
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto var(--spacing-md) auto;
                box-shadow: var(--shadow-md);
            ">
                <span style="font-size: 28px; filter: brightness(0) invert(1);">{icon}</span>
            </div>
            <h3 style="
                color: var(--color-text-primary);
                margin: 0 0 var(--spacing-sm) 0;
                font-size: 20px;
                font-weight: 600;
                font-family: var(--font-heading);
                letter-spacing: -0.025em;
            ">{title}</h3>
            <p style="
                color: var(--color-text-secondary);
                margin: 0;
                font-size: 15px;
                line-height: 1.6;
            ">{description}</p>
        </div>
        '''

    def _create_stats_card(self, number: str, label: str, sublabel: str = "") -> str:
        sublabel_html = f'<div style="color: var(--color-text-muted); font-size: 13px; margin-top: 4px;">{sublabel}</div>' if sublabel else ''
        return f'''
        <div class="soothe-stats-card" style="
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: var(--border-radius-lg);
            padding: var(--spacing-lg);
            text-align: center;
            transition: var(--transition-normal);
        ">
            <div style="
                color: var(--color-accent);
                font-size: 36px;
                font-weight: 700;
                font-family: var(--font-heading);
                margin-bottom: var(--spacing-xs);
                letter-spacing: -0.05em;
            ">{number}</div>
            <div style="
                color: var(--color-text-primary);
                font-weight: 600;
                font-size: 16px;
                margin-bottom: var(--spacing-xs);
            ">{label}</div>
            {sublabel_html}
        </div>
        '''

    # ---- CONTENT BUILDER METHODS ----

    def create_enhanced_homepage(self) -> str:
        # HERO SECTION
        hero_section = """
        <div style="
            width: 100%;
            /* background: linear-gradient(120deg, #e8edea 0%, #e6eae8 60%, #e0d1c3 100%); */
            padding: 7vw 0 4vw 0;
            min-height: 64vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            position: relative;
        ">
            <div style="
                color: #38BDF8;
                font-size: 15px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 2.5px;
                margin-bottom: 1.7rem;
            ">
                AI-POWERED INTERACTIVE STORYTELLING
            </div>
            <h1 style="
                color: #fff;
                font-size: clamp(2.3rem, 7vw, 3.7rem);
                font-weight: 700;
                font-family: 'Space Grotesk', 'Inter', ui-sans-serif, sans-serif;
                letter-spacing: -0.02em;
                line-height: 1.07;
                margin-bottom: 1.1rem;
            ">
                Step into the story of student life<br>
                with <span style="color: #38BDF8">SootheAI</span>
            </h1>
            <div style="
                color: #cfd9e7;
                font-size: 1.36rem;
                max-width: 660px;
                margin: 0 auto 1.7rem auto;
                line-height: 1.6;
            ">
                Experience and learn about anxiety through interactive fiction—<br>
                designed for Singapore’s youth, by Singaporeans.<br>
                <span style="color: #38bdf8; font-weight: 600;">Every choice helps you understand yourself and others.</span>
            </div>
            <div style="
                color: #6ee7b7;
                text-align: center;
                font-size: 1.12rem;
                margin-top: 1.15rem;
                font-family: 'Space Grotesk', 'Inter', sans-serif;
                font-weight: 600;
                opacity: 0.97;
                letter-spacing: 0.01em;
            ">
                Empower yourself through relatable, AI-driven stories—rooted in Singapore’s student experience.
            </div>
            <div style="
                display: flex;
                justify-content: center;
                gap: 1.7rem;
                margin: 2.3rem 0 1.3rem 0;
                flex-wrap: wrap;
            ">
                <div style="color: #38bdf8; font-weight: 500; font-size: 1rem;">✓ Safe &amp; private storytelling</div>
                <div style="color: #38bdf8; font-weight: 500; font-size: 1rem;">✓ Available 24/7, always free</div>
                <div style="color: #38bdf8; font-weight: 500; font-size: 1rem;">✓ Created for Singapore’s school community</div>
            </div>
            <div style="
                display: flex;
                gap: 1.2rem;
                justify-content: center;
                margin-top: 2.2rem;
                flex-wrap: wrap;
            ">
                <button
                    class="soothe-hero-btn"
                    style='
                        background: linear-gradient(90deg, #0EA5E9 60%, #38BDF8 100%);
                        color: #fff;
                        border: none;
                        padding: 1rem 2.2rem;
                        border-radius: 2rem;
                        font-size: 1.12rem;
                        font-weight: 700;
                        font-family: var(--font-primary, Inter, sans-serif);
                        cursor: pointer;
                        box-shadow: 0 2px 18px rgba(14,165,233,0.17);
                        letter-spacing: 0.7px;
                        text-transform: uppercase;
                        transition: background .18s;
                    '
                    onclick="
                        Array.from(document.querySelectorAll('button, .tabitem, .tab-nav button')).forEach(btn => {
                            if (btn.innerText.trim().includes('SootheAI Chat')) btn.click();
                        });
                    "
                >
                    START YOUR STORY
                </button>
                <button
                    class="soothe-hero-btn"
                    style='
                        background: transparent;
                        color: #fff;
                        border: 2px solid #38BDF8;
                        padding: 0.98rem 2.1rem;
                        border-radius: 2rem;
                        font-size: 1.12rem;
                        font-weight: 600;
                        font-family: var(--font-primary, Inter, sans-serif);
                        cursor: pointer;
                        letter-spacing: 0.3px;
                        box-shadow: none;
                        display: flex;
                        align-items: center;
                        gap: .7rem;
                        transition: background .18s, color .18s, border-color .18s;
                    '
                    onclick="
                        Array.from(document.querySelectorAll('button, .tabitem, .tab-nav button')).forEach(btn => {
                            if (btn.innerText.trim() === 'ℹ️ About') btn.click();
                        });
                    "
                >
                    <span style="font-size:1.1rem; margin-top:1px;">❓</span> What is SootheAI?
                </button>
            </div>
        </div>
        """

        # FEATURES SECTION
        features_section = """

            <!-- Features Section Main Content -->
            <div style="
                width: 100%;
                /*background: linear-gradient(180deg, #F3F6FC 0%, #A6D6D6 100%);*/
                padding: 0 0 4.5rem 0;
                min-height: 520px;
                display: flex;
                flex-direction: column;
                align-items: center;
                border: none;
            ">
                <div style="max-width: 1200px; margin: 0 auto; width: 100%; padding: 0 1.3rem;">
                    <div style="text-align: center; margin-bottom: 3.2rem; padding-top: 2.7rem;">
                        <div style="
                            color: #38bdf8;
                            font-size: 0.95rem;
                            font-weight: 600;
                            letter-spacing: 0.15em;
                            text-transform: uppercase;
                            margin-bottom: 1.1rem;
                            opacity: 0.92;
                        ">
                            What makes SootheAI different?
                        </div>
                        <div style="
                            width: 70px;
                            height: 3px;
                            background: linear-gradient(90deg, #38bdf8, #0ea5e9);
                            margin: 0 auto;
                            border-radius: 2px;
                        "></div>
                    </div>

                    <!-- FEATURE CARDS FLEX WRAPPER -->
                    <div style="
                        display: flex;
                        flex-wrap: wrap;
                        justify-content: center;
                        gap: 2.2rem;
                        margin-bottom: 0;
                    ">
                        <!-- Feature Card 1 -->
                        <div class="soothe-feature-card">
                            <div class="soothe-feature-icon">📖</div>
                            <h3 style="color: #1e293b; font-size: 1.17rem; font-weight: 700; margin-bottom: .6rem; font-family: var(--font-heading, Space Grotesk, Inter, sans-serif);">Interactive Stories</h3>
                            <div style="color: #334155; font-size: 1.02rem; line-height: 1.6;">
                                Shape your own story as a student in Singapore and explore relatable, AI-powered scenarios about anxiety, choices, and growth.
                            </div>
                        </div>
                        <!-- Feature Card 2 -->
                        <div class="soothe-feature-card">
                            <div class="soothe-feature-icon">🇸🇬</div>
                            <h3 style="color: #1e293b; font-size: 1.17rem; font-weight: 700; margin-bottom: .6rem; font-family: var(--font-heading, Space Grotesk, Inter, sans-serif);">Singapore School Life</h3>
                            <div style="color: #334155; font-size: 1.02rem; line-height: 1.6;">
                                Experience moments inspired by real Singaporean school life—academic pressure, friendships, and everyday challenges.
                            </div>
                        </div>
                        <!-- Feature Card 3 -->
                        <div class="soothe-feature-card">
                            <div class="soothe-feature-icon">💡</div>
                            <h3 style="color: #1e293b; font-size: 1.17rem; font-weight: 700; margin-bottom: .6rem; font-family: var(--font-heading, Space Grotesk, Inter, sans-serif);">Learn Healthy Coping</h3>
                            <div style="color: #334155; font-size: 1.02rem; line-height: 1.6;">
                                Try evidence-informed, positive ways to handle anxiety through choices and self-reflection. No clinical advice—just life skills for students.
                            </div>
                        </div>
                        <!-- Feature Card 4 -->
                        <div class="soothe-feature-card">
                            <div class="soothe-feature-icon">⏰</div>
                            <h3 style="color: #1e293b; font-size: 1.17rem; font-weight: 700; margin-bottom: .6rem; font-family: var(--font-heading, Space Grotesk, Inter, sans-serif);">Always Available</h3>
                            <div style="color: #334155; font-size: 1.02rem; line-height: 1.6;">
                                Play and learn anytime, anywhere. Your journey is free, private, and available 24/7.
                            </div>
                        </div>
                    </div> <!-- end cards flex -->
                </div>
            </div>
        </div>
        """

        # FOOTER SECTION (now *inside* the page-wrapper, seamlessly following features)
        footer_section = """
            <div class="soothe-footer" style="
                width: 100%;
                /* background: ... */
                /* color: ... */

            padding: 2.7rem 0 1.3rem 0;
            font-family: var(--font-primary, Inter, sans-serif);
            margin-top: 0;
            border-radius: 0;
            box-shadow: none;
        ">
            <div style="max-width: 1200px; margin: 0 auto; padding: 0 1.5rem;">
                <div style="
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 2.4rem;
                    margin-bottom: 2.1rem;
                ">
                    <div>
                        <h3 style="
                            margin: 0 0 1rem 0; 
                            font-size: 24px; 
                            font-weight: 700;
                            font-family: var(--font-heading, Space Grotesk, Inter, sans-serif);
                            color: #fff;
                        ">SootheAI</h3>
                        <p style="
                            margin: 0 0 1rem 0; 
                            opacity: 0.92; 
                            font-size: 16px;
                            line-height: 1.6;
                        ">
                            AI-powered mental health support through interactive storytelling, designed specifically for Singapore's youth.
                        </p>
                        <div style="
                            background: rgba(56, 189, 248, 0.11);
                            padding: 1rem;
                            border-radius: 0.9rem;
                            border-left: 4px solid #38bdf8;
                        ">
                            <strong style="color: #38bdf8;">Remember:</strong>
                            <span style="color: #fff; font-weight: bold;">This is a supportive tool, not a replacement for professional help when needed.</span>
                        </div>
                    </div>
                    <div>
                        <h4 style="
                            margin: 0 0 1rem 0; 
                            font-size: 18px; 
                            font-weight: 600;
                            color: #fff;
                        ">Quick Access</h4>
                        <div style="display: flex; flex-direction: column; gap: 0.45rem;">
                            <div style="color: #38bdf8; font-size: 14px; font-weight: 500;">🏠 Start on Home tab</div>
                            <div style="color: #38bdf8; font-size: 14px; font-weight: 500;">💬 Chat with SootheAI</div>
                            <div style="color: #38bdf8; font-size: 14px; font-weight: 500;">📚 Learn about anxiety</div>
                            <div style="color: #38bdf8; font-size: 14px; font-weight: 500;">🆘 Emergency contacts</div>
                        </div>
                    </div>
                    <div>
                        <h4 style="
                            margin: 0 0 1rem 0; 
                            font-size: 18px; 
                            font-weight: 600;
                            color: #f87171;
                        ">🚨 Crisis Support</h4>
                        <div style="display: flex; flex-direction: column; gap: 0.2rem;">
                            <div style="
                                background: rgba(255, 255, 255, 0.12);
                                padding: 0.45rem 1rem;
                                border-radius: 0.7rem;
                                color: #fff;
                                font-weight: 600;
                            ">
                                Emergency: 999
                            </div>
                            <div style="
                                background: rgba(255, 255, 255, 0.12);
                                padding: 0.45rem 1rem;
                                border-radius: 0.7rem;
                                color: #fff;
                                font-weight: 600;
                            ">
                                SOS: 1-767
                            </div>
                            <div style="
                                background: rgba(255, 255, 255, 0.12);
                                padding: 0.45rem 1rem;
                                border-radius: 0.7rem;
                                color: #fff;
                                font-weight: 600;
                            ">
                                National Care: 1800-202-6868
                            </div>
                        </div>
                    </div>
                </div>
                <div style="
                    border-top: 1px solid rgba(255,255,255,0.16); 
                    padding-top: 1.3rem;
                    text-align: center;
                    margin-top: 1.2rem;
                ">
                    <p style="
                        margin: 0 0 0.4rem 0; 
                        opacity: 0.84; 
                        font-size: 14px;
                    ">
                        © 2025 SootheAI • Confidential & Free • Available 24/7
                    </p>
                    <p style="
                        margin: 0; 
                        opacity: 0.8; 
                        font-size: 13px;
                    ">
                        <strong style="color:#fff;">
                            If you're experiencing a mental health emergency, please contact emergency services immediately.
                            This tool provides educational support and is <span style="color:#f87171;">not a substitute for professional medical advice.</span>
                        </strong>
                    </p>
                </div>
            </div>
        </div>

        """

        return self._create_page_wrapper(
        hero_section + features_section 
    )


    def create_anxiety_education_content(self) -> str:
        content = f'''
        <div style="
            width: 100%;
            background: linear-gradient(135deg, #29406e 0%, #224075 38%, #21a2e1 100%);
            min-height: 100vh;
            padding: 3rem 0 2rem 0;
            font-family: var(--font-primary, Inter, sans-serif);
        ">
            <div style="max-width: 900px; margin: 0 auto; padding: 0 1.5rem;">
                <!-- Header Section -->
                <div style="
                    text-align: center;
                    margin-bottom: 3rem;
                    padding-top: 1rem;
                ">
                    <div style="
                        color: #38bdf8;
                        font-size: 0.95rem;
                        font-weight: 600;
                        letter-spacing: 0.15em;
                        text-transform: uppercase;
                        margin-bottom: 1.2rem;
                        opacity: 0.9;
                    ">
                        MENTAL HEALTH EDUCATION
                    </div>
                    
                    <h1 style="
                        color: #fff;
                        font-size: clamp(2.2rem, 5vw, 3.2rem);
                        font-weight: 700;
                        font-family: var(--font-heading, 'Space Grotesk', 'Inter', sans-serif);
                        letter-spacing: -0.02em;
                        line-height: 1.1;
                        margin-bottom: 1rem;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 0.7rem;
                        flex-wrap: wrap;
                    ">
                        <span style="
                            font-size: 2.1rem; 
                            background: linear-gradient(135deg, #38bdf8, #0ea5e9); 
                            color: #fff; 
                            border-radius: 0.6em; 
                            padding: 0.15em 0.4em 0.12em 0.3em; 
                            box-shadow: 0 4px 15px rgba(56,189,248,0.3);
                        ">📚</span>
                        Understanding Anxiety
                    </h1>
                    
                    <div style="
                        width: 80px;
                        height: 3px;
                        background: linear-gradient(90deg, #38bdf8, #0ea5e9);
                        margin: 0 auto 1.5rem auto;
                        border-radius: 2px;
                    "></div>
                    
                    <p style="
                        color: #cbd5e1;
                        font-size: 1.15rem;
                        max-width: 600px;
                        margin: 0 auto;
                        line-height: 1.6;
                        opacity: 0.95;
                    ">
                        Learn about anxiety in a supportive, educational environment designed for Singapore's youth
                    </p>
                </div>

                <!-- Content Cards -->
                <div style="
                    display: flex;
                    flex-direction: column;
                    gap: 2rem;
                    margin-bottom: 2rem;
                ">
                    <!-- What is Anxiety Card -->
                    <div style="
                        background: rgba(255, 255, 255, 0.95);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(56, 189, 248, 0.2);
                        border-radius: 1.2rem;
                        padding: 2.5rem;
                        box-shadow: 0 8px 32px rgba(30, 58, 95, 0.1);
                        position: relative;
                        overflow: hidden;
                    ">
                        <!-- Gradient accent -->
                        <div style="
                            position: absolute;
                            top: 0;
                            left: 0;
                            right: 0;
                            height: 4px;
                            background: linear-gradient(90deg, #0ea5e9, #38bdf8);
                        "></div>
                        
                        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                            <div style="
                                width: 50px;
                                height: 50px;
                                background: linear-gradient(135deg, #0ea5e9, #38bdf8);
                                border-radius: 0.8rem;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                margin-right: 1rem;
                                font-size: 1.5rem;
                                box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
                            ">💗</div>
                            <h2 style="
                                color: var(--color-text-primary, #1e293b);
                                font-size: 1.8rem;
                                font-weight: 700;
                                font-family: var(--font-heading, 'Space Grotesk', 'Inter', sans-serif);
                                margin: 0;
                            ">What is Anxiety?</h2>
                        </div>
                        
                        <div style="
                            color: #1e293b;
                            font-size: 1.1rem;
                            line-height: 1.7;
                            margin: 0;
                        ">
                            Anxiety is a normal response to stress or perceived threats. However, when anxiety becomes excessive or persistent, it can interfere with daily functioning and wellbeing. In Singapore's high-achievement educational context, many students experience academic-related anxiety.
                        </div>
                    </div>

                    <!-- Signs of Anxiety Card -->
                    <div style="
                        background: rgba(255, 255, 255, 0.95);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(56, 189, 248, 0.2);
                        border-radius: 1.2rem;
                        padding: 2.5rem;
                        box-shadow: 0 8px 32px rgba(30, 58, 95, 0.1);
                        position: relative;
                        overflow: hidden;
                    ">
                        <!-- Gradient accent -->
                        <div style="
                            position: absolute;
                            top: 0;
                            left: 0;
                            right: 0;
                            height: 4px;
                            background: linear-gradient(90deg, #f59e0b, #fbbf24);
                        "></div>
                        
                        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                            <div style="
                                width: 50px;
                                height: 50px;
                                background: linear-gradient(135deg, #f59e0b, #fbbf24);
                                border-radius: 0.8rem;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                margin-right: 1rem;
                                font-size: 1.5rem;
                                box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
                            ">⚠️</div>
                            <h2 style="
                                color: var(--color-text-primary, #1e293b);
                                font-size: 1.8rem;
                                font-weight: 700;
                                font-family: var(--font-heading, 'Space Grotesk', 'Inter', sans-serif);
                                margin: 0;
                            ">Common Signs of Anxiety</h2>
                        </div>
                        
                        <div style="
                            color: #1e293b;
                            font-size: 1.1rem;
                            line-height: 1.7;
                            margin: 0;
                        ">
                            <ul style="margin: 0; padding-left: 1.5rem; list-style: none;">
                                <li style="margin-bottom: 0.8rem; position: relative; color: #1e293b;">
                                    <span style="
                                        position: absolute;
                                        left: -1.5rem;
                                        color: #06b6d4;
                                        font-weight: 600;
                                    ">•</span>
                                    <strong style="color: #06b6d4; font-weight: 600;">Physical symptoms:</strong> 
                                    racing heart, shortness of breath, stomach discomfort, sweating
                                </li>
                                <li style="margin-bottom: 0.8rem; position: relative; color: #1e293b;">
                                    <span style="
                                        position: absolute;
                                        left: -1.5rem;
                                        color: #6366f1;
                                        font-weight: 600;
                                    ">•</span>
                                    <strong style="color: #6366f1; font-weight: 600;">Emotional symptoms:</strong> 
                                    excessive worry, irritability, difficulty concentrating
                                </li>
                                <li style="margin-bottom: 0.8rem; position: relative; color: #1e293b;">
                                    <span style="
                                        position: absolute;
                                        left: -1.5rem;
                                        color: #f59e0b;
                                        font-weight: 600;
                                    ">•</span>
                                    <strong style="color: #f59e0b; font-weight: 600;">Behavioral symptoms:</strong> 
                                    avoidance, procrastination, perfectionism
                                </li>
                                <li style="margin-bottom: 0; position: relative; color: #1e293b;">
                                    <span style="
                                        position: absolute;
                                        left: -1.5rem;
                                        color: #38bdf8;
                                        font-weight: 600;
                                    ">•</span>
                                    <strong style="color: #38bdf8; font-weight: 600;">Cognitive symptoms:</strong> 
                                    negative thoughts, catastrophizing, all-or-nothing thinking
                                </li>
                            </ul>
                        </div>
                    </div>

                    <!-- Healthy Coping Card -->
                    <div style="
                        background: rgba(255, 255, 255, 0.95);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(56, 189, 248, 0.2);
                        border-radius: 1.2rem;
                        padding: 2.5rem;
                        box-shadow: 0 8px 32px rgba(30, 58, 95, 0.1);
                        position: relative;
                        overflow: hidden;
                    ">
                        <!-- Gradient accent -->
                        <div style="
                            position: absolute;
                            top: 0;
                            left: 0;
                            right: 0;
                            height: 4px;
                            background: linear-gradient(90deg, #10b981, #34d399);
                        "></div>
                        
                        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                            <div style="
                                width: 50px;
                                height: 50px;
                                background: linear-gradient(135deg, #10b981, #34d399);
                                border-radius: 0.8rem;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                margin-right: 1rem;
                                font-size: 1.5rem;
                                box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
                            ">💡</div>
                            <h2 style="
                                color: var(--color-text-primary, #1e293b);
                                font-size: 1.8rem;
                                font-weight: 700;
                                font-family: var(--font-heading, 'Space Grotesk', 'Inter', sans-serif);
                                margin: 0;
                            ">Healthy Coping Strategies</h2>
                        </div>
                        
                        <div style="
                            color: #1e293b;
                            font-size: 1.1rem;
                            line-height: 1.7;
                            margin: 0;
                        ">
                            <ul style="margin: 0; padding-left: 1.5rem; list-style: none;">
                                <li style="margin-bottom: 0.8rem; position: relative; color: #1e293b;">
                                    <span style="
                                        position: absolute;
                                        left: -1.5rem;
                                        color: #10b981;
                                        font-weight: 600;
                                    ">•</span>
                                    <strong style="color: #10b981; font-weight: 600;">Deep breathing:</strong> 
                                    Slow, deliberate breathing to activate the relaxation response
                                </li>
                                <li style="margin-bottom: 0.8rem; position: relative; color: #1e293b;">
                                    <span style="
                                        position: absolute;
                                        left: -1.5rem;
                                        color: #06b6d4;
                                        font-weight: 600;
                                    ">•</span>
                                    <strong style="color: #06b6d4; font-weight: 600;">Mindfulness:</strong> 
                                    Paying attention to the present moment without judgment
                                </li>
                                <li style="margin-bottom: 0.8rem; position: relative; color: #1e293b;">
                                    <span style="
                                        position: absolute;
                                        left: -1.5rem;
                                        color: #22c55e;
                                        font-weight: 600;
                                    ">•</span>
                                    <strong style="color: #22c55e; font-weight: 600;">Physical activity:</strong> 
                                    Regular exercise to reduce stress hormones
                                </li>
                                <li style="margin-bottom: 0.8rem; position: relative; color: #1e293b;">
                                    <span style="
                                        position: absolute;
                                        left: -1.5rem;
                                        color: #f59e0b;
                                        font-weight: 600;
                                    ">•</span>
                                    <strong style="color: #f59e0b; font-weight: 600;">Balanced lifestyle:</strong> 
                                    Adequate sleep, nutrition, and breaks
                                </li>
                                <li style="margin-bottom: 0.8rem; position: relative; color: #1e293b;">
                                    <span style="
                                        position: absolute;
                                        left: -1.5rem;
                                        color: #2563eb;
                                        font-weight: 600;
                                    ">•</span>
                                    <strong style="color: #2563eb; font-weight: 600;">Challenging negative thoughts:</strong> 
                                    Identifying and reframing unhelpful thinking patterns
                                </li>
                                <li style="margin-bottom: 0; position: relative; color: #1e293b;">
                                    <span style="
                                        position: absolute;
                                        left: -1.5rem;
                                        color: #38bdf8;
                                        font-weight: 600;
                                    ">•</span>
                                    <strong style="color: #38bdf8; font-weight: 600;">Seeking support:</strong> 
                                    Talking to trusted friends, family, or professionals
                                </li>
                            </ul>
                        </div>
                    </div>

                    <!-- Call-to-Action Card -->
                    <div style="
                        background: linear-gradient(135deg, rgba(56, 189, 248, 0.1), rgba(14, 165, 233, 0.05));
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(56, 189, 248, 0.3);
                        border-radius: 1.2rem;
                        padding: 2rem;
                        text-align: center;
                        box-shadow: 0 8px 32px rgba(30, 58, 95, 0.1);
                    ">
                        <h3 style="
                            color: #fff;
                            font-size: 1.5rem;
                            font-weight: 600;
                            margin-bottom: 1rem;
                            font-family: var(--font-heading, 'Space Grotesk', 'Inter', sans-serif);
                        ">Ready to Practice These Skills?</h3>
                        
                        <p style="
                            color: #cbd5e1;
                            font-size: 1.1rem;
                            margin-bottom: 1.5rem;
                            line-height: 1.6;
                        ">
                            Try out these anxiety management techniques through interactive stories in our chat experience.
                        </p>
                        
                        <button
                            style="
                                background: linear-gradient(90deg, #0EA5E9 60%, #38BDF8 100%);
                                color: #fff;
                                border: none;
                                padding: 0.8rem 2rem;
                                border-radius: 2rem;
                                font-size: 1rem;
                                font-weight: 600;
                                font-family: var(--font-primary, Inter, sans-serif);
                                cursor: pointer;
                                box-shadow: 0 4px 15px rgba(14,165,233,0.3);
                                transition: all 0.3s ease;
                            "
                            onclick="
                                Array.from(document.querySelectorAll('button, .tabitem, .tab-nav button')).forEach(btn => {{
                                    if (btn.innerText.trim().includes('SootheAI Chat')) btn.click();
                                }});
                            "
                        >
                            Start Interactive Learning →
                        </button>
                    </div>
                </div>
            </div>
        </div>
        '''
        
        return content


    def create_helpline_content(self) -> str:
        content = f'''
        <div style="
            width: 100%;
            background: linear-gradient(135deg, #29406e 0%, #224075 38%, #21a2e1 100%);
            min-height: 100vh;
            padding: 3rem 0 2rem 0;
            font-family: var(--font-primary, Inter, sans-serif);
        ">
            <div style="max-width: 900px; margin: 0 auto; padding: 0 1.5rem;">
                <!-- Header Section -->
                <div style="
                    text-align: center;
                    margin-bottom: 3rem;
                    padding-top: 1rem;
                ">
                    <div style="
                        color: #ef4444;
                        font-size: 0.95rem;
                        font-weight: 600;
                        letter-spacing: 0.15em;
                        text-transform: uppercase;
                        margin-bottom: 1.2rem;
                        opacity: 0.9;
                    ">
                        CRISIS SUPPORT & MENTAL HEALTH RESOURCES
                    </div>
                    
                    <h1 style="
                        color: #fff;
                        font-size: clamp(2.2rem, 5vw, 3.2rem);
                        font-weight: 700;
                        font-family: var(--font-heading, 'Space Grotesk', 'Inter', sans-serif);
                        letter-spacing: -0.02em;
                        line-height: 1.1;
                        margin-bottom: 1rem;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 0.7rem;
                        flex-wrap: wrap;
                    ">
                        <span style="
                            font-size: 2.1rem; 
                            background: linear-gradient(135deg, #ef4444, #dc2626); 
                            color: #fff; 
                            border-radius: 0.6em; 
                            padding: 0.15em 0.4em 0.12em 0.3em; 
                            box-shadow: 0 4px 15px rgba(239,68,68,0.3);
                        ">🆘</span>
                        Mental Health Support
                    </h1>
                    
                    <div style="
                        width: 80px;
                        height: 3px;
                        background: linear-gradient(90deg, #ef4444, #dc2626);
                        margin: 0 auto 1.5rem auto;
                        border-radius: 2px;
                    "></div>
                    
                    <p style="
                        color: #cbd5e1;
                        font-size: 1.15rem;
                        max-width: 600px;
                        margin: 0 auto;
                        line-height: 1.6;
                        opacity: 0.95;
                    ">
                        <strong style="color: #fbbf24;">You are not alone.</strong> If you're experiencing distress, these resources are here to help you 24/7.
                    </p>
                </div>

                <!-- Emergency Section -->
                <div style="
                    background: rgba(239, 68, 68, 0.15);
                    backdrop-filter: blur(10px);
                    border: 2px solid rgba(239, 68, 68, 0.4);
                    border-radius: 1.2rem;
                    padding: 2.5rem;
                    margin-bottom: 2rem;
                    box-shadow: 0 8px 32px rgba(239, 68, 68, 0.1);
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                        <div style="
                            width: 50px;
                            height: 50px;
                            background: linear-gradient(135deg, #ef4444, #dc2626);
                            border-radius: 0.8rem;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            margin-right: 1rem;
                            font-size: 1.5rem;
                            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
                        ">🚨</div>
                        <h2 style="
                            color: #fff;
                            font-size: 1.8rem;
                            font-weight: 700;
                            font-family: var(--font-heading, 'Space Grotesk', 'Inter', sans-serif);
                            margin: 0;
                        ">Emergency Contacts</h2>
                    </div>
                    
                    <p style="
                        color: #f1f5f9;
                        font-size: 1.1rem;
                        margin-bottom: 1.5rem;
                        font-weight: 500;
                    ">
                        If you or someone you know is experiencing a mental health emergency, please contact these 24/7 helplines:
                    </p>
                    
                    <div style="display: grid; gap: 1rem;">
                        <div style="
                            background: rgba(255, 255, 255, 0.95);
                            padding: 1.5rem;
                            border-radius: 0.8rem;
                            border-left: 6px solid #ef4444;
                            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                        ">
                            <strong style="color: #1e293b; font-size: 1.1rem;">Emergency Ambulance:</strong> 
                            <span style="color: #ef4444; font-size: 1.5rem; font-weight: 700; margin-left: 8px;">999</span>
                        </div>
                        <div style="
                            background: rgba(255, 255, 255, 0.95);
                            padding: 1.5rem;
                            border-radius: 0.8rem;
                            border-left: 6px solid #ef4444;
                            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                        ">
                            <strong style="color: #1e293b; font-size: 1.1rem;">Samaritans of Singapore (SOS):</strong> 
                            <span style="color: #ef4444; font-size: 1.5rem; font-weight: 700; margin-left: 8px;">1-767</span>
                        </div>
                        <div style="
                            background: rgba(255, 255, 255, 0.95);
                            padding: 1.5rem;
                            border-radius: 0.8rem;
                            border-left: 6px solid #ef4444;
                            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                        ">
                            <strong style="color: #1e293b; font-size: 1.1rem;">National Care Hotline:</strong> 
                            <span style="color: #ef4444; font-size: 1.5rem; font-weight: 700; margin-left: 8px;">1800-202-6868</span>
                        </div>
                        <div style="
                            background: rgba(255, 255, 255, 0.95);
                            padding: 1.5rem;
                            border-radius: 0.8rem;
                            border-left: 6px solid #ef4444;
                            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                        ">
                            <strong style="color: #1e293b; font-size: 1.1rem;">IMH Mental Health Helpline:</strong> 
                            <span style="color: #ef4444; font-size: 1.5rem; font-weight: 700; margin-left: 8px;">6389-2222</span>
                        </div>
                    </div>
                </div>

                <!-- Youth Support Section -->
                <div style="
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(56, 189, 248, 0.2);
                    border-radius: 1.2rem;
                    padding: 2.5rem;
                    margin-bottom: 2rem;
                    box-shadow: 0 8px 32px rgba(30, 58, 95, 0.1);
                    position: relative;
                    overflow: hidden;
                ">
                    <!-- Gradient accent -->
                    <div style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        height: 4px;
                        background: linear-gradient(90deg, #0ea5e9, #38bdf8);
                    "></div>
                    
                    <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                        <div style="
                            width: 50px;
                            height: 50px;
                            background: linear-gradient(135deg, #0ea5e9, #38bdf8);
                            border-radius: 0.8rem;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            margin-right: 1rem;
                            font-size: 1.5rem;
                            box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
                        ">🧑‍🎓</div>
                        <h2 style="
                            color: #1e293b;
                            font-size: 1.8rem;
                            font-weight: 700;
                            font-family: var(--font-heading, 'Space Grotesk', 'Inter', sans-serif);
                            margin: 0;
                        ">Youth-Specific Support</h2>
                    </div>
                    
                    <div style="display: grid; gap: 1.2rem;">
                        <div style="
                            background: rgba(14, 165, 233, 0.05);
                            padding: 1.5rem;
                            border-radius: 0.8rem;
                            border-left: 4px solid #0ea5e9;
                        ">
                            <h4 style="margin: 0 0 0.5rem 0; color: #1e293b; font-size: 1.2rem; font-weight: 600;">CHAT (Community Health Assessment Team)</h4>
                            <p style="margin: 0 0 0.5rem 0; color: #64748b;">For youth aged 16-30</p>
                            <p style="margin: 0.5rem 0 0 0; font-weight: 600; color: #1e293b;">📞 6493-6500</p>
                            <p style="margin: 0.5rem 0 0 0;"><a href="https://www.chat.mentalhealth.sg/" target="_blank" style="color: #0ea5e9; text-decoration: none; font-weight: 500;">https://www.chat.mentalhealth.sg/</a></p>
                        </div>
                        <div style="
                            background: rgba(14, 165, 233, 0.05);
                            padding: 1.5rem;
                            border-radius: 0.8rem;
                            border-left: 4px solid #0ea5e9;
                        ">
                            <h4 style="margin: 0 0 0.5rem 0; color: #1e293b; font-size: 1.2rem; font-weight: 600;">eC2 (Counselling Online)</h4>
                            <p style="margin: 0 0 0.5rem 0; color: #64748b;">Web-based counselling service</p>
                            <p style="margin: 0.5rem 0 0 0;"><a href="https://www.ec2.sg/" target="_blank" style="color: #0ea5e9; text-decoration: none; font-weight: 500;">https://www.ec2.sg/</a></p>
                        </div>
                        <div style="
                            background: rgba(14, 165, 233, 0.05);
                            padding: 1.5rem;
                            border-radius: 0.8rem;
                            border-left: 4px solid #0ea5e9;
                        ">
                            <h4 style="margin: 0 0 0.5rem 0; color: #1e293b; font-size: 1.2rem; font-weight: 600;">Tinkle Friend</h4>
                            <p style="margin: 0 0 0.5rem 0; color: #64748b;">For primary school children</p>
                            <p style="margin: 0.5rem 0 0 0; font-weight: 600; color: #1e293b;">📞 1800-274-4788</p>
                            <p style="margin: 0.5rem 0 0 0;"><a href="https://www.tinklefriend.sg/" target="_blank" style="color: #0ea5e9; text-decoration: none; font-weight: 500;">https://www.tinklefriend.sg/</a></p>
                        </div>
                    </div>
                </div>

                <!-- Remember Section -->
                <div style="
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(14, 165, 233, 0.1));
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(16, 185, 129, 0.3);
                    border-radius: 1.2rem;
                    padding: 2.5rem;
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(30, 58, 95, 0.1);
                ">
                    <div style="
                        width: 60px;
                        height: 60px;
                        background: linear-gradient(135deg, #10b981, #059669);
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0 auto 1.5rem auto;
                        font-size: 2rem;
                        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
                    ">💚</div>
                    
                    <h2 style="
                        color: #fff;
                        margin-bottom: 1rem;
                        font-size: 1.8rem;
                        font-weight: 600;
                        font-family: var(--font-heading, 'Space Grotesk', 'Inter', sans-serif);
                    ">Remember</h2>
                    <p style="margin-bottom: 1rem; font-size: 1.1rem; line-height: 1.6; color: #f1f5f9;">
                        Reaching out for support is a sign of strength, not weakness. Mental health professionals are trained to help you navigate difficult emotions and experiences.
                    </p>
                    <p style="margin: 0; font-weight: 600; font-size: 1.2rem; color: #fff;">
                        You don't have to face these challenges alone.
                    </p>
                </div>
            </div>
        </div>
        '''
        
        return content

    def create_about_content(self) -> str:
        content = f'''
        <div style="
            width: 100%;
            background: linear-gradient(135deg, #29406e 0%, #224075 38%, #21a2e1 100%);
            min-height: 100vh;
            padding: 3rem 0 2rem 0;
            font-family: var(--font-primary, Inter, sans-serif);
        ">
            <div style="max-width: 900px; margin: 0 auto; padding: 0 1.5rem;">
                <!-- Header Section -->
                <div style="
                    text-align: center;
                    margin-bottom: 3rem;
                    padding-top: 1rem;
                ">
                    <div style="
                        color: #38bdf8;
                        font-size: 0.95rem;
                        font-weight: 600;
                        letter-spacing: 0.15em;
                        text-transform: uppercase;
                        margin-bottom: 1.2rem;
                        opacity: 0.9;
                    ">
                        LEARN MORE ABOUT OUR MISSION
                    </div>
                    
                    <h1 style="
                        color: #fff;
                        font-size: clamp(2.2rem, 5vw, 3.2rem);
                        font-weight: 700;
                        font-family: var(--font-heading, 'Space Grotesk', 'Inter', sans-serif);
                        letter-spacing: -0.02em;
                        line-height: 1.1;
                        margin-bottom: 1rem;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 0.7rem;
                        flex-wrap: wrap;
                    ">
                        <span style="
                            font-size: 2.1rem; 
                            background: linear-gradient(135deg, #38bdf8, #0ea5e9); 
                            color: #fff; 
                            border-radius: 0.6em; 
                            padding: 0.15em 0.4em 0.12em 0.3em; 
                            box-shadow: 0 4px 15px rgba(56,189,248,0.3);
                        ">ℹ️</span>
                        About SootheAI
                    </h1>
                    
                    <div style="
                        width: 80px;
                        height: 3px;
                        background: linear-gradient(90deg, #38bdf8, #0ea5e9);
                        margin: 0 auto 1.5rem auto;
                        border-radius: 2px;
                    "></div>
                    
                    <p style="
                        color: #cbd5e1;
                        font-size: 1.15rem;
                        max-width: 600px;
                        margin: 0 auto;
                        line-height: 1.6;
                        opacity: 0.95;
                    ">
                        Discover the story behind SootheAI and how we're helping Singapore's youth navigate anxiety through innovative storytelling
                    </p>
                </div>

                <!-- Content Cards -->
                <div style="
                    display: flex;
                    flex-direction: column;
                    gap: 2rem;
                    margin-bottom: 2rem;
                ">
                    <!-- Mission Card -->
                    <div style="
                        background: rgba(255, 255, 255, 0.95);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(56, 189, 248, 0.2);
                        border-radius: 1.2rem;
                        padding: 2.5rem;
                        box-shadow: 0 8px 32px rgba(30, 58, 95, 0.1);
                        position: relative;
                        overflow: hidden;
                    ">
                        <!-- Gradient accent -->
                        <div style="
                            position: absolute;
                            top: 0;
                            left: 0;
                            right: 0;
                            height: 4px;
                            background: linear-gradient(90deg, #0ea5e9, #38bdf8);
                        "></div>
                        
                        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                            <div style="
                                width: 50px;
                                height: 50px;
                                background: linear-gradient(135deg, #0ea5e9, #38bdf8);
                                border-radius: 0.8rem;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                margin-right: 1rem;
                                font-size: 1.5rem;
                                box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3);
                            ">🎯</div>
                            <h2 style="
                                color: #1e293b;
                                font-size: 1.8rem;
                                font-weight: 700;
                                font-family: var(--font-heading, 'Space Grotesk', 'Inter', sans-serif);
                                margin: 0;
                            ">Our Mission</h2>
                        </div>
                        
                        <div style="
                            color: #1e293b;
                            font-size: 1.1rem;
                            line-height: 1.7;
                            margin: 0;
                        ">
                            SootheAI aims to help Singaporean youths understand, manage, and overcome anxiety through interactive storytelling enhanced by artificial intelligence. We believe that by engaging young people in relatable scenarios and providing them with practical coping strategies, we can make a meaningful impact on youth mental health in Singapore.
                        </div>
                    </div>

                    <!-- Approach Card -->
                    <div style="
                        background: rgba(255, 255, 255, 0.95);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(56, 189, 248, 0.2);
                        border-radius: 1.2rem;
                        padding: 2.5rem;
                        box-shadow: 0 8px 32px rgba(30, 58, 95, 0.1);
                        position: relative;
                        overflow: hidden;
                    ">
                        <!-- Gradient accent -->
                        <div style="
                            position: absolute;
                            top: 0;
                            left: 0;
                            right: 0;
                            height: 4px;
                            background: linear-gradient(90deg, #10b981, #34d399);
                        "></div>
                        
                        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                            <div style="
                                width: 50px;
                                height: 50px;
                                background: linear-gradient(135deg, #10b981, #34d399);
                                border-radius: 0.8rem;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                margin-right: 1rem;
                                font-size: 1.5rem;
                                box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
                            ">🤖</div>
                            <h2 style="
                                color: #1e293b;
                                font-size: 1.8rem;
                                font-weight: 700;
                                font-family: var(--font-heading, 'Space Grotesk', 'Inter', sans-serif);
                                margin: 0;
                            ">Our Approach</h2>
                        </div>
                        
                        <div style="
                            color: #1e293b;
                            font-size: 1.1rem;
                            line-height: 1.7;
                            margin: 0;
                        ">
                            We combine the power of narrative storytelling with AI technology to create personalized learning experiences that adapt to each user's needs. Our stories are set in culturally relevant Singaporean contexts, addressing the unique pressures and challenges that local youth face.
                            <br><br>
                            Through interactive fiction, users can explore different scenarios, make choices, and learn about anxiety management techniques in a safe, engaging environment. The AI component ensures that each journey is uniquely tailored to provide the most helpful guidance.
                        </div>
                    </div>

                    <!-- Team Card -->
                    <div style="
                        background: rgba(255, 255, 255, 0.95);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(56, 189, 248, 0.2);
                        border-radius: 1.2rem;
                        padding: 2.5rem;
                        box-shadow: 0 8px 32px rgba(30, 58, 95, 0.1);
                        position: relative;
                        overflow: hidden;
                    ">
                        <!-- Gradient accent -->
                        <div style="
                            position: absolute;
                            top: 0;
                            left: 0;
                            right: 0;
                            height: 4px;
                            background: linear-gradient(90deg, #8b5cf6, #a78bfa);
                        "></div>
                        
                        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                            <div style="
                                width: 50px;
                                height: 50px;
                                background: linear-gradient(135deg, #8b5cf6, #a78bfa);
                                border-radius: 0.8rem;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                margin-right: 1rem;
                                font-size: 1.5rem;
                                box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3);
                            ">👥</div>
                            <h2 style="
                                color: #1e293b;
                                font-size: 1.8rem;
                                font-weight: 700;
                                font-family: var(--font-heading, 'Space Grotesk', 'Inter', sans-serif);
                                margin: 0;
                            ">The Team</h2>
                        </div>
                        
                        <div style="
                            color: #1e293b;
                            font-size: 1.1rem;
                            line-height: 1.7;
                            margin: 0;
                        ">
                            SootheAI is developed by a team of mental health professionals, educational technologists, and AI specialists who are passionate about improving youth mental wellbeing in Singapore.
                            <br><br>
                            We work closely with psychologists, educators, and youth advisors to ensure that our content is accurate, appropriate, and effective.
                        </div>
                    </div>

                    <!-- Contact Card -->
                    <div style="
                        background: rgba(255, 255, 255, 0.95);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(56, 189, 248, 0.2);
                        border-radius: 1.2rem;
                        padding: 2.5rem;
                        box-shadow: 0 8px 32px rgba(30, 58, 95, 0.1);
                        position: relative;
                        overflow: hidden;
                    ">
                        <!-- Gradient accent -->
                        <div style="
                            position: absolute;
                            top: 0;
                            left: 0;
                            right: 0;
                            height: 4px;
                            background: linear-gradient(90deg, #f59e0b, #fbbf24);
                        "></div>
                        
                        <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                            <div style="
                                width: 50px;
                                height: 50px;
                                background: linear-gradient(135deg, #f59e0b, #fbbf24);
                                border-radius: 0.8rem;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                margin-right: 1rem;
                                font-size: 1.5rem;
                                box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
                            ">📧</div>
                            <h2 style="
                                color: #1e293b;
                                font-size: 1.8rem;
                                font-weight: 700;
                                font-family: var(--font-heading, 'Space Grotesk', 'Inter', sans-serif);
                                margin: 0;
                            ">Contact Us</h2>
                        </div>
                        
                        <div style="
                            color: #1e293b;
                            font-size: 1.1rem;
                            line-height: 1.7;
                            margin: 0;
                        ">
                            If you have questions, feedback, or would like to learn more about SootheAI, please reach out to us at 
                            <a href="mailto:contact@sootheai.sg" style="color: #0ea5e9; text-decoration: none; font-weight: 600;">contact@sootheai.sg</a>.
                        </div>
                    </div>

                    <!-- Call-to-Action Card -->
                    <div style="
                        background: linear-gradient(135deg, rgba(56, 189, 248, 0.1), rgba(14, 165, 233, 0.05));
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(56, 189, 248, 0.3);
                        border-radius: 1.2rem;
                        padding: 2rem;
                        text-align: center;
                        box-shadow: 0 8px 32px rgba(30, 58, 95, 0.1);
                    ">
                        <h3 style="
                            color: #fff;
                            font-size: 1.5rem;
                            font-weight: 600;
                            margin-bottom: 1rem;
                            font-family: var(--font-heading, 'Space Grotesk', 'Inter', sans-serif);
                        ">Ready to Begin Your Journey?</h3>
                        
                        <p style="
                            color: #cbd5e1;
                            font-size: 1.1rem;
                            margin-bottom: 1.5rem;
                            line-height: 1.6;
                        ">
                            Start exploring anxiety management through interactive storytelling designed specifically for Singapore's youth.
                        </p>
                        
                        <button
                            style="
                                background: linear-gradient(90deg, #0EA5E9 60%, #38BDF8 100%);
                                color: #fff;
                                border: none;
                                padding: 0.8rem 2rem;
                                border-radius: 2rem;
                                font-size: 1rem;
                                font-weight: 600;
                                font-family: var(--font-primary, Inter, sans-serif);
                                cursor: pointer;
                                box-shadow: 0 4px 15px rgba(14,165,233,0.3);
                                transition: all 0.3s ease;
                            "
                            onclick="
                                Array.from(document.querySelectorAll('button, .tabitem, .tab-nav button')).forEach(btn => {{
                                    if (btn.innerText.trim().includes('SootheAI Chat')) btn.click();
                                }});
                            "
                        >
                            Start Your Story →
                        </button>
                    </div>
                </div>
            </div>
        </div>
        '''
        
        return content

    def create_enhanced_css(self) -> str:
        return f"""
        {self._get_font_imports()}
        {self._create_css_variables()}

        html, body, .soothe-page-wrapper {{
            background: linear-gradient(135deg, #29406e 0%, #224075 38%, #21a2e1 100%) !important;
            color: #1e293b;
            font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
            min-height: 100vh;
        }}

        /* ----------- HOMEPAGE FEATURE CARDS ----------- */
        @keyframes pulseGlow {{
            0%   {{ box-shadow: 0 2px 18px #0ea5e96e, 0 0 0 0 #38bdf820; }}
            70%  {{ box-shadow: 0 8px 36px #38bdf856, 0 0 0 12px #38bdf810; }}
            100% {{ box-shadow: 0 2px 18px #0ea5e96e, 0 0 0 0 #38bdf820; }}
        }}

        .soothe-feature-card {{
            background: #fff;
            border-radius: 1.25rem;
            border: 1.3px solid #bae6fd;
            box-shadow: 0 2px 18px rgba(56,189,248,0.12), 0 1.5px 6px rgba(14,165,233,0.06);
            padding: 2.15rem 1.25rem 1.5rem 1.25rem;
            min-width: 260px; max-width: 310px; flex: 1 1 275px;
            display: flex; flex-direction: column; align-items: center;
            text-align: center;
            margin-bottom: 0;
            color: #1e293b;
            transition: box-shadow .18s, border-color .16s, transform .14s;
            animation: pulseGlow 2.8s infinite alternate;
        }}
        .soothe-feature-icon {{
            font-size: 2.3rem;
            margin-bottom: 1.05rem;
            background: linear-gradient(135deg, #0EA5E9 60%, #38BDF8 100%);
            color: #fff;
            border-radius: 1rem;
            width: 56px; height: 56px;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 2px 16px #0ea5e96e;
            animation: pulseGlow 2.7s infinite alternate;
        }}
        .soothe-feature-card:hover, .soothe-feature-card:focus-visible {{
            animation: none;
            box-shadow: 0 0 0 8px #38bdf82b, 0 2px 26px #0ea5e944, 0 12px 30px #38bdf81b;
            border-color: #38bdf8 !important;
            transform: translateY(-5px) scale(1.028);
            outline: 2.5px solid #38bdf8 !important;
            z-index: 2;
        }}
        .features-section-inner {{
            display: flex;
            flex-wrap: wrap;
            gap: 2rem;
            justify-content: center;
            align-items: stretch;
            max-width: 1320px;
            margin: 0 auto;
            padding: 2.5rem 1.4rem 3.6rem 1.4rem;
            background: linear-gradient(135deg, #f8fbff 88%, #e0effc 100%);
            border-radius: 1.3rem;
            box-shadow: 0 4px 18px rgba(30,58,95,0.11);
            border: 1px solid #e1e9f8;
        }}
        .soothe-feature-card p, .soothe-feature-card div {{
            color: #334155;
        }}

        /* ----------- BUTTONS ----------- */
        .soothe-hero-btn {{
            background: linear-gradient(90deg, #0EA5E9 60%, #38BDF8 100%);
            color: #fff !important;
            border: none;
            border-radius: 2rem;
            padding: 1rem 2.2rem;
            font-weight: 700;
            font-size: 1.12rem;
            box-shadow: 0 2px 18px rgba(14,165,233,0.17);
            transition: background .18s, color .18s, border-color .18s;
        }}
        .soothe-hero-btn:hover, .soothe-hero-btn:focus-visible {{
            background: linear-gradient(90deg, #22d3ee 60%, #0ea5e9 100%);
            color: #fff !important;
            box-shadow: 0 6px 32px 0 #38bdf86e, 0 1.5px 8px #0ea5e94f, 0 0 0 3px #38bdf888;
            outline: 2.5px solid #38bdf8;
        }}

        /* ----------- FOOTER ----------- */
        .soothe-footer {{
            background: linear-gradient(90deg, #1E3A5F 0%, #2B4A75 70%, #0EA5E9 100%);
            color: #fff !important;
            padding: 2.2rem 0;
        }}
        .soothe-footer h3, .soothe-footer h4 {{ color: #fff !important; }}
        .soothe-footer strong {{ color: #38BDF8 !important; }}
        .soothe-footer a {{ color: #38BDF8; }}
        .soothe-footer .crisis {{ color: #ef4444; }}
        .soothe-footer .quick-link {{
            color: #38BDF8 !important;
            font-weight: 500;
        }}

        /* ----------- NO CUSTOM STYLES FOR ANXIETY TAB ----------- */
        /* All anxiety tab backgrounds and containers removed */

        /* ----------- RESPONSIVE ----------- */
        @media (max-width: 900px) {{
            .features-section-inner {{ padding: 1.5rem 1vw 2.5rem 1vw; }}
            .soothe-feature-card {{ min-width: 170px; max-width: 99vw; padding: 1.2rem 0.7rem 1.0rem 1.0rem; }}
        }}
        """




    def create_enhanced_theme(self) -> gr.Theme:
        return gr.themes.Base(
            primary_hue=gr.themes.colors.blue,
            secondary_hue=gr.themes.colors.slate,
            neutral_hue=gr.themes.colors.slate,
            font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
            font_mono=[gr.themes.GoogleFont("JetBrains Mono"), "Consolas", "monospace"],
        ).set(
            button_primary_background_fill=self.colors['accent'],
            button_primary_background_fill_hover=self.colors['accent_dark'],
            button_primary_text_color=self.colors['text_inverse'],
            button_primary_border_color=self.colors['accent'],
            button_secondary_background_fill=self.colors['surface'],
            button_secondary_background_fill_hover=self.colors['surface_hover'],
            button_secondary_text_color=self.colors['text_primary'],
            button_secondary_border_color=self.colors['border'],
            input_background_fill=self.colors['surface'],
            input_border_color=self.colors['border'],
            input_border_color_focus=self.colors['border_focus'],
            input_placeholder_color=self.colors['text_muted'],
            background_fill_primary=self.colors['background'],
            background_fill_secondary=self.colors['surface_alt'],
            border_color_primary=self.colors['border'],
            border_color_accent=self.colors['accent'],
            body_text_color=self.colors['text_secondary'],
            body_text_color_subdued=self.colors['text_muted'],
            panel_background_fill=self.colors['surface'],
            block_background_fill=self.colors['surface'],
        )

    def main_loop(self, message: Optional[str], history: List[Tuple[str, str]]) -> str:
        
        if message is None:
            logger.info("Processing empty message in main loop")
            return self.consent_message

        logger.info(f"Processing message in main loop: {message[:50] if message else ''}...")
        
        try:
            response, success = self.narrative_engine.process_message(message)
            
            if not success:
                logger.error(f"Narrative engine error: {response}")
                return "I apologize, but I encountered an error. Please try again."

            # TTS integration - keep your existing logic
            if (success and 
                hasattr(self.narrative_engine, 'game_state') and
                self.narrative_engine.game_state.is_consent_given() and 
                message.lower() not in ['i agree', 'i agree with audio', 'i agree without audio', 'enable audio', 'disable audio', 'start game']):
            
                try:
                    self.tts_handler.run_tts_with_consent_and_limiting(response)
                except Exception as e:
                    logger.warning(f"TTS failed: {e}")

            return response
            
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            return "I apologize, but I encountered an unexpected error. Please try again."

    def create_footer(self) -> str:
        return """
        <div class="soothe-footer" style="
            background: linear-gradient(90deg, #1E3A5F 0%, #2B4A75 70%, #0EA5E9 100%);
            color: #fff;
            padding: 2.5rem 0 1.2rem 0;
            font-family: var(--font-primary, Inter, sans-serif);
            margin: 0;  /* No margin */
            border: none;
            border-radius: 0;  /* No rounding */
            box-shadow: none;  /* No shadow */
        ">
            <div style="max-width: 1200px; margin: 0 auto; padding: 0 1.5rem;">
                <div style="
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 2.2rem;
                    margin-bottom: 2.1rem;
                ">
                    <div>
                        <h3 style="
                            margin: 0 0 1rem 0; 
                            font-size: 24px; 
                            font-weight: 700;
                            font-family: var(--font-heading, Space Grotesk, Inter, sans-serif);
                            color: #fff;
                        ">SootheAI</h3>
                        <p style="
                            margin: 0 0 1rem 0; 
                            opacity: 0.92; 
                            font-size: 16px;
                            line-height: 1.6;
                        ">
                            AI-powered mental health support through interactive storytelling, designed specifically for Singapore's youth.
                        </p>
                        <div style="
                            background: rgba(56, 189, 248, 0.11);
                            padding: 1rem;
                            border-radius: 0.9rem;
                            border-left: 4px solid #38bdf8;
                            margin-bottom: 0.2rem;
                        ">
                            <strong style="color: #38bdf8;">Remember:</strong>
                            <span style="color: #fff; font-weight: bold;">This is a supportive tool, not a replacement for professional help when needed.</span>
                        </div>
                    </div>
                    <div>
                        <h4 style="
                            margin: 0 0 1rem 0; 
                            font-size: 18px; 
                            font-weight: 600;
                            color: #fff;
                        ">Quick Access</h4>
                        <div style="display: flex; flex-direction: column; gap: 0.45rem;">
                            <a href="#" style="color: #38bdf8; font-size: 14px; font-weight: 500; text-decoration: none;">🏠 Start on Home tab</a>
                            <a href="#" style="color: #38bdf8; font-size: 14px; font-weight: 500; text-decoration: none;">💬 Chat with SootheAI</a>
                            <a href="#" style="color: #38bdf8; font-size: 14px; font-weight: 500; text-decoration: none;">📚 Learn about anxiety</a>
                            <a href="#" style="color: #38bdf8; font-size: 14px; font-weight: 500; text-decoration: none;">🆘 Emergency contacts</a>
                        </div>
                    </div>
                    <div>
                        <h4 style="
                            margin: 0 0 1rem 0; 
                            font-size: 18px; 
                            font-weight: 600;
                            color: #f87171;
                        ">🚨 Crisis Support</h4>
                        <div style="display: flex; flex-direction: column; gap: 0.2rem;">
                            <div style="
                                background: rgba(255, 255, 255, 0.13);
                                padding: 0.45rem 1rem;
                                border-radius: 0.7rem;
                                color: #fff;
                                font-weight: 600;
                            ">
                                Emergency: 999
                            </div>
                            <div style="
                                background: rgba(255, 255, 255, 0.13);
                                padding: 0.45rem 1rem;
                                border-radius: 0.7rem;
                                color: #fff;
                                font-weight: 600;
                            ">
                                SOS: 1-767
                            </div>
                            <div style="
                                background: rgba(255, 255, 255, 0.13);
                                padding: 0.45rem 1rem;
                                border-radius: 0.7rem;
                                color: #fff;
                                font-weight: 600;
                            ">
                                National Care: 1800-202-6868
                            </div>
                        </div>
                    </div>
                </div>
                <div style="
                    border-top: 1px solid rgba(255,255,255,0.16); 
                    padding-top: 1.1rem;
                    text-align: center;
                    margin-top: 1.1rem;
                ">
                    <p style="
                        margin: 0 0 0.4rem 0; 
                        opacity: 0.84; 
                        font-size: 14px;
                    ">
                        © 2025 SootheAI • Confidential & Free • Available 24/7
                    </p>
                    <p style="
                        margin: 0; 
                        opacity: 0.85; 
                        font-size: 13px;
                    ">
                        <strong style="color:#fff;">
                            If you're experiencing a mental health emergency, please contact emergency services immediately.
                            This tool provides educational support and is <span style="color:#f87171;">not a substitute for professional medical advice.</span>
                        </strong>
                    </p>
                </div>
            </div>
        </div>
        """

    def create_interface(self) -> gr.Blocks:
        """Create the complete Gradio interface with all tabs."""
        with gr.Blocks(
            theme=self.create_enhanced_theme(),
            title="SootheAI - Mental Health Support",
            css=self.create_enhanced_css()
        ) as blocks:
            with gr.Tabs(elem_classes="soothe-tabs") as tabs:
                # Home Tab
                with gr.Tab("🏠 Home"):
                    gr.HTML(self.create_enhanced_homepage() + self.create_footer())
                
                # Chat Tab - Main functionality
                with gr.Tab("💬 SootheAI Chat"):
                    gr.HTML("""
                        <div style="
                            background: linear-gradient(135deg, #1E3A5F 0%, #2B4A75 50%, #0EA5E9 100%);
                            color: white;
                            padding: 32px;
                            border-radius: 16px;
                            margin-bottom: 24px;
                            text-align: center;
                            box-shadow: 0 12px 40px rgba(30, 58, 95, 0.2);
                        ">
                            <h1 style="
                                margin: 0 0 16px 0;
                                font-size: 36px;
                                font-weight: 700;
                                font-family: 'Inter', sans-serif;
                            ">🌟 Your Safe Space for Mental Wellness</h1>
                            <p style="
                                margin: 0 0 24px 0;
                                font-size: 18px;
                                opacity: 0.95;
                                max-width: 600px;
                                margin-left: auto;
                                margin-right: auto;
                                line-height: 1.6;
                            ">Connect with your personal AI companion designed to understand, support, and guide you through anxiety management</p>
                            <div style="
                                background: rgba(255, 255, 255, 0.15);
                                border-radius: 12px;
                                padding: 24px;
                                margin-top: 24px;
                                border: 1px solid rgba(255, 255, 255, 0.2);
                            ">
                                <div style="
                                    display: grid;
                                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                                    gap: 16px;
                                    margin-bottom: 16px;
                                ">
                                    <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                                        <span style="font-size: 20px;">🔒</span>
                                        <span style="font-weight: 500;">100% Confidential</span>
                                    </div>
                                    <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                                        <span style="font-size: 20px;">🤖</span>
                                        <span style="font-weight: 500;">AI-Powered Support</span>
                                    </div>
                                    <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                                        <span style="font-size: 20px;">🇸🇬</span>
                                        <span style="font-weight: 500;">Singapore-Focused</span>
                                    </div>
                                </div>
                                <div style="
                                    color: #38BDF8;
                                    font-weight: 600;
                                    font-size: 16px;
                                    text-align: center;
                                ">
                                    💡 Ready to start? Choose "I agree with audio" or "I agree without audio" below
                                </div>
                            </div>
                        </div>
                    """)
                    
                    # Main chat interface
                    gr.ChatInterface(
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
                        ),
                        textbox=gr.Textbox(
                            placeholder="💭 e.g., 'I agree with audio' or 'start game' ",
                            container=False,
                            scale=7,
                            lines=1,
                            max_lines=4,
                        ),
                        examples=[
                            "I agree with audio",
                            "I agree without audio",
                            "start game"
                        ],
                        cache_examples=False,
                        title=None,
                        description=None,
                    )
                    gr.HTML(self.create_footer())

                # Education Tab
                with gr.Tab("📚 Learn About Anxiety"):
                    gr.HTML(self.create_anxiety_education_content() + self.create_footer())
                
                # Help Tab
                with gr.Tab("🆘 Get Help"):
                    gr.HTML(self.create_helpline_content() + self.create_footer())
                
                # About Tab
                with gr.Tab("ℹ️ About"):
                    gr.HTML(self.create_about_content() + self.create_footer())

        self.interface = blocks
        return blocks


    def launch(self, share: bool = True, server_name: str = "0.0.0.0", server_port: int = 7861) -> None:
        if self.interface is None:
            self.create_interface()
        try:
            self.interface.launch(
                share=share,
                server_name=server_name,
                server_port=server_port
            )
        except Exception as e:
            logger.error(f"Failed to launch Gradio interface: {str(e)}")
            raise

    def close(self) -> None:
        if self.interface is not None:
            try:
                self.interface.close()
                logger.info("Closed Gradio interface")
            except Exception as e:
                logger.error(f"Error closing Gradio interface: {str(e)}")

def create_gradio_interface(elevenlabs_client=None) -> GradioInterface:  # Remove character_data parameter
    """
    Create a Gradio interface instance.

    Args:
        elevenlabs_client: Optional ElevenLabs client instance for TTS functionality

    Returns:
        GradioInterface: Configured interface instance ready for launch
    """
    return GradioInterface(elevenlabs_client)  # Remove character_data parameter

