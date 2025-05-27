"""
Streamlit interface module for SootheAI with improved design consistency and UX.
"""

import streamlit as st
import logging
from typing import Optional, Tuple, List, Dict, Any
import time

# Import your existing modules
from ..core.narrative_engine import create_narrative_engine
from ..models.game_state import GameState
try:
    from ..ui.tts_handler import get_tts_handler
except ImportError:
    # Fallback if there are circular import issues
    def get_tts_handler(client=None):
        class DummyTTS:
            def run_tts_with_consent_and_limiting(self, text): pass
        return DummyTTS()

logger = logging.getLogger(__name__)

class StreamlitInterface:
    """Streamlit interface for SootheAI with improved design consistency."""

    def __init__(self, elevenlabs_client=None):
        """Initialize the Streamlit interface with enhanced unified design system."""
        
        # ENHANCED color scheme with better accessibility and modern design
        self.colors = {
            # Primary brand colors - refined for better accessibility
            'primary': '#1E3A5F',          # Deeper navy for better contrast
            'primary_light': '#2B4A75',    # Original navy
            'primary_dark': '#0F1F33',     # Even darker navy
            'primary_hover': '#344A66',    # Hover state for primary elements
            
            # Secondary colors
            'secondary': '#4A6B8A',        # Muted blue-gray
            'secondary_light': '#6B8BA8',  # Lighter secondary
            
            # Background hierarchy - improved for better visual separation
            'background': '#FAFBFC',       # Slightly cooler off-white
            'surface': '#FFFFFF',          # Pure white
            'surface_hover': '#F8F9FA',    # Subtle hover for interactive surfaces
            'surface_alt': '#F1F5F9',      # Light blue-gray for alternating sections
            'surface_elevated': '#FFFFFF', # For elevated cards with shadows
            
            # Accent colors - refined turquoise palette
            'accent': '#0EA5E9',           # Modern sky blue (more professional)
            'accent_dark': '#0284C7',      # Darker blue
            'accent_light': '#38BDF8',     # Lighter blue
            'accent_subtle': '#E0F2FE',    # Very light blue for backgrounds
            
            # Enhanced text hierarchy - improved contrast ratios
            'text_primary': '#0F172A',     # Very dark slate for maximum readability
            'text_secondary': '#334155',   # Medium-dark slate for secondary text
            'text_tertiary': '#475569',    # Medium slate for tertiary text
            'text_muted': '#64748B',       # Light slate for muted text
            'text_inverse': '#FFFFFF',     # White text for dark backgrounds
            
            # Semantic colors
            'success': '#10B981',          # Emerald green
            'success_light': '#D1FAE5',    # Light green background
            'warning': '#F59E0B',          # Amber
            'warning_light': '#FEF3C7',    # Light amber background
            'error': '#EF4444',            # Red
            'error_light': '#FEE2E2',      # Light red background
            'info': '#3B82F6',             # Blue
            'info_light': '#DBEAFE',       # Light blue background
            
            # Border and divider colors
            'border': '#E2E8F0',           # Light slate border
            'border_light': '#F1F5F9',     # Very light border
            'border_focus': '#0EA5E9',     # Focus state border (matches accent)
            'divider': '#E2E8F0',          # Same as border for consistency
        }
        
        self.narrative_engine = create_narrative_engine()
        self.tts_handler = get_tts_handler(elevenlabs_client)

        # Enhanced consent message with better formatting and contrast
        self.consent_message = """
        # 🌟 Welcome to SootheAI

        *Helping you navigate anxiety through interactive storytelling*

        ---

        ## 📖 What to Expect
        This is a safe, educational experience using fictional stories to help you understand anxiety management. Some content may depict challenging situations, but you're always in a supportive learning environment.

        ## 🎧 Audio Experience
        Choose your preferred way to engage:
        - **With voice narration** - Immersive AI-generated storytelling  
        - **Text only** - Read at your own comfortable pace

        ## 🚀 Ready to Begin?
        Type one of these commands to start:
        - `I agree with audio` - for full audio experience
        - `I agree without audio` - for text-only experience

        *You can change audio settings anytime by typing 'enable audio' or 'disable audio'*

        ---

        **Your mental health journey starts with a single step. We're here to guide you.**
        """

    def get_custom_css(self) -> str:
        """Get custom CSS for styling Streamlit components."""
        return f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
        
        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 100%;
        }}
        
        /* Custom hero section */
        .hero-section {{
            background: linear-gradient(135deg, {self.colors['primary']} 0%, {self.colors['primary_light']} 50%, {self.colors['secondary']} 100%);
            padding: 3rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            color: white;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .hero-section::before {{
            content: '';
            position: absolute;
            inset: 0;
            background-image: radial-gradient(circle at 1px 1px, rgba(255,255,255,0.1) 1px, transparent 0);
            background-size: 40px 40px;
            opacity: 0.3;
        }}
        
        .hero-content {{
            position: relative;
            z-index: 2;
        }}
        
        .hero-title {{
            font-size: clamp(2rem, 5vw, 3.5rem);
            font-weight: 300;
            font-family: 'Space Grotesk', sans-serif;
            margin-bottom: 1rem;
            line-height: 1.1;
        }}
        
        .hero-subtitle {{
            font-size: 1.25rem;
            margin-bottom: 2rem;
            opacity: 0.9;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }}
        
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        
        .feature-item {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            font-weight: 500;
        }}
        
        /* Feature cards */
        .feature-card {{
            background: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            transition: all 0.2s ease-out;
            position: relative;
            overflow: hidden;
            margin-bottom: 1.5rem;
        }}
        
        .feature-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 10px 25px rgba(30, 58, 95, 0.15);
            border-color: {self.colors['accent_light']};
        }}
        
        .feature-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, {self.colors['accent']}, {self.colors['accent_light']});
        }}
        
        .feature-icon {{
            background: linear-gradient(135deg, {self.colors['accent']}, {self.colors['accent_light']});
            width: 64px;
            height: 64px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem auto;
            font-size: 1.75rem;
            color: white;
            box-shadow: 0 4px 16px rgba(14, 165, 233, 0.25);
        }}
        
        .feature-title {{
            color: {self.colors['text_primary']};
            font-size: 1.25rem;
            font-weight: 600;
            font-family: 'Space Grotesk', sans-serif;
            margin-bottom: 0.5rem;
        }}
        
        .feature-description {{
            color: {self.colors['text_secondary']};
            font-size: 0.95rem;
            line-height: 1.6;
        }}
        
        /* Stats cards */
        .stats-card {{
            background: {self.colors['surface']};
            border: 1px solid {self.colors['border']};
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.2s ease-out;
        }}
        
        .stats-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(30, 58, 95, 0.1);
        }}
        
        .stats-number {{
            color: {self.colors['accent']};
            font-size: 2.25rem;
            font-weight: 700;
            font-family: 'Space Grotesk', sans-serif;
            margin-bottom: 0.25rem;
        }}
        
        .stats-label {{
            color: {self.colors['text_primary']};
            font-weight: 600;
            font-size: 1rem;
            margin-bottom: 0.25rem;
        }}
        
        .stats-sublabel {{
            color: {self.colors['text_muted']};
            font-size: 0.8rem;
        }}
        
        /* Chat styling */
        .chat-container {{
            background: linear-gradient(145deg, #FFFFFF 0%, rgba(248, 250, 252, 0.95) 30%, rgba(241, 245, 249, 0.9) 70%, #F1F5F9 100%);
            border: 2px solid {self.colors['accent_light']};
            border-radius: 16px;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(30, 58, 95, 0.12);
        }}
        
        .chat-header {{
            background: linear-gradient(135deg, {self.colors['primary']} 0%, {self.colors['primary_light']} 50%, {self.colors['accent']} 100%);
            color: white;
            padding: 12px 16px;
            border-radius: 12px 12px 0 0;
            font-weight: 600;
            font-size: 0.9rem;
            text-align: center;
            margin: -1rem -1rem 1rem -1rem;
        }}
        
        /* Section styling */
        .content-section {{
            background: {self.colors['surface_elevated']};
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 16px rgba(30, 58, 95, 0.08);
            border: 1px solid {self.colors['border_light']};
        }}
        
        .section-title {{
            color: {self.colors['text_primary']};
            font-size: 1.75rem;
            font-weight: 600;
            font-family: 'Space Grotesk', sans-serif;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        
        .section-icon {{
            font-size: 1.5rem;
        }}
        
        /* Emergency section */
        .emergency-section {{
            background: {self.colors['error_light']};
            border: 2px solid {self.colors['error']};
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 1.5rem;
        }}
        
        .emergency-title {{
            color: {self.colors['error']};
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .emergency-contact {{
            background: {self.colors['surface']};
            padding: 1rem;
            border-radius: 8px;
            border-left: 6px solid {self.colors['error']};
            margin-bottom: 0.5rem;
            box-shadow: 0 2px 8px rgba(239, 68, 68, 0.1);
        }}
        
        .contact-name {{
            font-weight: 600;
            color: {self.colors['text_primary']};
            margin-bottom: 0.25rem;
        }}
        
        .contact-number {{
            color: {self.colors['error']};
            font-size: 1.25rem;
            font-weight: 700;
        }}
        
        /* Info cards */
        .info-card {{
            background: {self.colors['info_light']};
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid {self.colors['accent']};
            margin-bottom: 1rem;
        }}
        
        .info-title {{
            font-weight: 600;
            color: {self.colors['text_primary']};
            margin-bottom: 0.25rem;
        }}
        
        .info-description {{
            color: {self.colors['text_secondary']};
            font-size: 0.9rem;
            margin-bottom: 0.25rem;
        }}
        
        .info-contact {{
            font-weight: 600;
            color: {self.colors['text_primary']};
        }}
        
        .info-link {{
            color: {self.colors['accent']};
            text-decoration: none;
        }}
        
        /* Footer */
        .footer-section {{
            background: linear-gradient(135deg, {self.colors['primary']}, {self.colors['primary_light']});
            color: white;
            padding: 3rem 2rem;
            border-radius: 12px;
            margin-top: 3rem;
        }}
        
        .footer-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        
        .footer-title {{
            font-size: 1.5rem;
            font-weight: 700;
            font-family: 'Space Grotesk', sans-serif;
            margin-bottom: 1rem;
        }}
        
        .footer-subtitle {{
            font-size: 1.125rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }}
        
        .footer-text {{
            opacity: 0.9;
            line-height: 1.6;
            margin-bottom: 1rem;
        }}
        
        .footer-notice {{
            background: rgba(255, 255, 255, 0.1);
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid {self.colors['accent_light']};
        }}
        
        .quick-access-item {{
            color: {self.colors['accent_light']};
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 0.25rem;
        }}
        
        .emergency-contact-footer {{
            background: rgba(255, 255, 255, 0.1);
            padding: 0.75rem;
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }}
        
        .emergency-contact-footer .contact-name {{
            color: white;
            font-weight: 600;
        }}
        
        .footer-bottom {{
            border-top: 1px solid rgba(255,255,255,0.2);
            padding-top: 1.5rem;
            text-align: center;
        }}
        
        .footer-bottom p {{
            margin: 0.5rem 0;
            opacity: 0.8;
        }}
        
        /* Streamlit specific overrides */
        .stTextInput > div > div > input {{
            border-radius: 12px;
            border: 2px solid {self.colors['border_light']};
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {self.colors['accent']};
            box-shadow: 0 0 0 2px {self.colors['accent_subtle']};
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, {self.colors['accent']} 0%, {self.colors['accent_dark']} 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            padding: 0.75rem 2rem;
            transition: all 0.2s ease-out;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(14, 165, 233, 0.35);
        }}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            white-space: pre-wrap;
            background-color: {self.colors['surface']};
            border-radius: 12px 12px 0 0;
            color: {self.colors['text_secondary']};
            font-weight: 500;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {self.colors['accent']};
            color: white;
        }}
        
        /* Chat message styling */
        .stChatMessage {{
            border-radius: 12px;
            margin: 0.5rem 0;
        }}
        
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        </style>
        """

    def create_homepage(self):
        """Create the enhanced homepage."""
        # Hero section
        st.markdown(f"""
        <div class="hero-section">
            <div class="hero-content">
                <div style="color: {self.colors['accent_light']}; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 1rem;">
                    AI-Powered Mental Health Support
                </div>
                
                <h1 class="hero-title">
                    Your journey to better mental health
                    <br><span style="font-weight: 700; background: linear-gradient(135deg, {self.colors['accent_light']}, {self.colors['accent']}); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">starts here</span>
                </h1>
                
                <p class="hero-subtitle">
                    Experience personalized AI support through interactive storytelling designed for Singapore's youth
                </p>
                
                <div class="feature-grid">
                    <div class="feature-item">
                        <span style="color: {self.colors['accent_light']}; font-size: 1.25rem;">✓</span>
                        Free & confidential
                    </div>
                    <div class="feature-item">
                        <span style="color: {self.colors['accent_light']}; font-size: 1.25rem;">✓</span>
                        Available 24/7
                    </div>
                    <div class="feature-item">
                        <span style="color: {self.colors['accent_light']}; font-size: 1.25rem;">✓</span>
                        Singapore-focused
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Features section
        st.markdown(f"""
        <div style="text-align: center; margin: 3rem 0 2rem 0;">
            <div style="color: {self.colors['accent']}; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 1rem;">
                How We Help
            </div>
            <h2 style="color: {self.colors['text_primary']}; font-size: clamp(2rem, 4vw, 3rem); font-weight: 600; font-family: 'Space Grotesk', sans-serif; margin-bottom: 1rem;">
                Personalized support that adapts to you
            </h2>
            <p style="color: {self.colors['text_secondary']}; font-size: 1.125rem; max-width: 600px; margin: 0 auto 2rem auto; line-height: 1.6;">
                Our AI-powered approach helps you understand and manage anxiety through culturally relevant storytelling
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Feature cards
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">🎭</div>
                <h3 class="feature-title">Interactive Stories</h3>
                <p class="feature-description">Engage with personalized narratives that adapt to your choices and help you understand anxiety in relatable contexts</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">🌏</div>
                <h3 class="feature-title">Singapore Context</h3>
                <p class="feature-description">Stories and support designed specifically for the pressures and culture of Singapore's educational system</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <h3 class="feature-title">AI-Powered Insights</h3>
                <p class="feature-description">Get tailored support based on evidence-based techniques and your unique needs and circumstances</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">⏰</div>
                <h3 class="feature-title">24/7 Availability</h3>
                <p class="feature-description">Access support whenever you need it, with no appointment necessary and complete confidentiality</p>
            </div>
            """, unsafe_allow_html=True)

        # Statistics section
        st.markdown(f"""
        <div style="background: {self.colors['surface_alt']}; border-radius: 16px; padding: 2rem; text-align: center; margin: 2rem 0;">
            <h3 style="color: {self.colors['text_primary']}; font-size: 1.5rem; font-weight: 600; font-family: 'Space Grotesk', sans-serif; margin-bottom: 2rem;">
                Making a real difference
            </h3>
        </div>
        """, unsafe_allow_html=True)

        # Stats cards
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        
        with stats_col1:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">24/7</div>
                <div class="stats-label">Available</div>
                <div class="stats-sublabel">Always here for you</div>
            </div>
            """, unsafe_allow_html=True)

        with stats_col2:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">100%</div>
                <div class="stats-label">Free</div>
                <div class="stats-sublabel">No cost, ever</div>
            </div>
            """, unsafe_allow_html=True)

        with stats_col3:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">🇸🇬</div>
                <div class="stats-label">Local</div>
                <div class="stats-sublabel">Made for Singapore</div>
            </div>
            """, unsafe_allow_html=True)

        with stats_col4:
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">∞</div>
                <div class="stats-label">Stories</div>
                <div class="stats-sublabel">Unlimited support</div>
            </div>
            """, unsafe_allow_html=True)

    def create_chat_interface(self):
        """Create the chat interface."""
        # Header
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {self.colors['primary']} 0%, {self.colors['primary_light']} 50%, {self.colors['accent']} 100%); color: white; padding: 2rem; border-radius: 16px; margin-bottom: 1.5rem; text-align: center; box-shadow: 0 12px 40px rgba(30, 58, 95, 0.2);">
            <h1 style="margin: 0 0 1rem 0; font-size: 2.25rem; font-weight: 700; font-family: 'Inter', sans-serif;">
                🌟 Your Safe Space for Mental Wellness
            </h1>
            
            <p style="margin: 0 0 1.5rem 0; font-size: 1.125rem; opacity: 0.95; max-width: 600px; margin-left: auto; margin-right: auto; line-height: 1.6;">
                Connect with your personal AI companion designed to understand, support, and guide you through anxiety management
            </p>
            
            <div style="background: rgba(255, 255, 255, 0.15); border-radius: 12px; padding: 1.5rem; margin-top: 1.5rem; border: 1px solid rgba(255, 255, 255, 0.2);">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                        <span style="font-size: 1.25rem;">🔒</span>
                        <span style="font-weight: 500;">100% Confidential</span>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                        <span style="font-size: 1.25rem;">🤖</span>
                        <span style="font-weight: 500;">AI-Powered Support</span>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                        <span style="font-size: 1.25rem;">🇸🇬</span>
                        <span style="font-weight: 500;">Singapore-Focused</span>
                    </div>
                </div>
                <div style="color: {self.colors['accent_light']}; font-weight: 600; font-size: 1rem; text-align: center;">
                    💡 Ready to start? Choose "I agree with audio" or "I agree without audio" below
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append({
                "role": "assistant", 
                "content": self.consent_message
            })

        # Initialize narrative engine
        if "narrative_engine" not in st.session_state:
            st.session_state.narrative_engine = self.narrative_engine

        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        st.markdown('<div class="chat-header">🌟 SootheAI Assistant - Your Mental Health Companion</div>', unsafe_allow_html=True)

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)


        # Chat input
        if prompt := st.chat_input("💭 Share what's on your mind... (e.g., 'I agree with audio' or 'I'm feeling anxious about school')"):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response, success = st.session_state.narrative_engine.process_message(prompt)
                    st.markdown(response)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})

                    # Handle TTS if enabled (you can implement this later)
                    # self.tts_handler.run_tts_with_consent_and_limiting(response)

        st.markdown('</div>', unsafe_allow_html=True)

        # Example prompts
        st.markdown("### 🌟 Quick Start - Choose how you'd like to begin your journey")
        
        example_cols = st.columns(3)
        examples = [
            "🎧 I agree with audio",
            "📖 I agree without audio", 
            "😰 I'm feeling anxious about school",
            "📚 I'm stressed about exams",
            "💭 I can't stop worrying",
            "🧘 Show me breathing exercises",
            "📝 Help me journal my thoughts",
            "🎵 I'd like to listen to music",
            "👥 I'm worried about fitting in",
            "😔 I'm feeling overwhelmed",
            "💪 Help me build confidence",
            "🌙 I'm having trouble sleeping"
        ]
        
        for i, example in enumerate(examples):
            col_idx = i % 3
            with example_cols[col_idx]:
                if st.button(example, key=f"example_{i}"):
                    # Add the example as a user message and process it
                    st.session_state.messages.append({"role": "user", "content": example})
                    response, success = st.session_state.narrative_engine.process_message(example)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()

    def create_anxiety_education(self):
        """Create anxiety education content."""
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: {self.colors['text_primary']}; font-size: 2.25rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif;">
                📚 Understanding Anxiety
            </h1>
        </div>
        """, unsafe_allow_html=True)

        # What is Anxiety section
        st.markdown(f"""
        <div class="content-section">
            <h2 class="section-title">
                <span class="section-icon">🧠</span>
                What is Anxiety?
            </h2>
            <div style="color: {self.colors['text_secondary']}; line-height: 1.7; font-size: 1rem;">
                Anxiety is a normal response to stress or perceived threats. However, when anxiety becomes excessive or persistent, it can interfere with daily functioning and wellbeing. In Singapore's high-achievement educational context, many students experience academic-related anxiety.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Common Signs section
        st.markdown(f"""
        <div class="content-section">
            <h2 class="section-title">
                <span class="section-icon">⚠️</span>
                Common Signs of Anxiety
            </h2>
            <div style="color: {self.colors['text_primary']}; line-height: 1.8; font-size: 1rem;">
                <ul style="margin-left: 1.25rem;">
                    <li style="margin-bottom: 0.75rem;">
                        <strong style="color: {self.colors['accent']}; font-weight: 600;">Physical symptoms:</strong> 
                        <span style="color: {self.colors['text_primary']};">racing heart, shortness of breath, stomach discomfort, sweating</span>
                    </li>
                    <li style="margin-bottom: 0.75rem;">
                        <strong style="color: {self.colors['accent']}; font-weight: 600;">Emotional symptoms:</strong> 
                        <span style="color: {self.colors['text_primary']};">excessive worry, irritability, difficulty concentrating</span>
                    </li>
                    <li style="margin-bottom: 0.75rem;">
                        <strong style="color: {self.colors['accent']}; font-weight: 600;">Behavioral symptoms:</strong> 
                        <span style="color: {self.colors['text_primary']};">avoidance, procrastination, perfectionism</span>
                    </li>
                    <li style="margin-bottom: 0.75rem;">
                        <strong style="color: {self.colors['accent']}; font-weight: 600;">Cognitive symptoms:</strong> 
                        <span style="color: {self.colors['text_primary']};">negative thoughts, catastrophizing, all-or-nothing thinking</span>
                    </li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Coping Strategies section
        st.markdown(f"""
        <div class="content-section">
            <h2 class="section-title">
                <span class="section-icon">💡</span>
                Healthy Coping Strategies
            </h2>
            <div style="color: {self.colors['text_primary']}; line-height: 1.8; font-size: 1rem;">
                <ul style="margin-left: 1.25rem;">
                    <li style="margin-bottom: 0.75rem;">
                        <strong style="color: {self.colors['success']}; font-weight: 600;">Deep breathing:</strong> 
                        <span style="color: {self.colors['text_primary']};">Slow, deliberate breathing to activate the relaxation response</span>
                    </li>
                    <li style="margin-bottom: 0.75rem;">
                        <strong style="color: {self.colors['success']}; font-weight: 600;">Mindfulness:</strong> 
                        <span style="color: {self.colors['text_primary']};">Paying attention to the present moment without judgment</span>
                    </li>
                    <li style="margin-bottom: 0.75rem;">
                        <strong style="color: {self.colors['success']}; font-weight: 600;">Physical activity:</strong> 
                        <span style="color: {self.colors['text_primary']};">Regular exercise to reduce stress hormones</span>
                    </li>
                    <li style="margin-bottom: 0.75rem;">
                        <strong style="color: {self.colors['success']}; font-weight: 600;">Balanced lifestyle:</strong> 
                        <span style="color: {self.colors['text_primary']};">Adequate sleep, nutrition, and breaks</span>
                    </li>
                    <li style="margin-bottom: 0.75rem;">
                        <strong style="color: {self.colors['success']}; font-weight: 600;">Challenging negative thoughts:</strong> 
                        <span style="color: {self.colors['text_primary']};">Identifying and reframing unhelpful thinking patterns</span>
                    </li>
                    <li style="margin-bottom: 0.75rem;">
                        <strong style="color: {self.colors['success']}; font-weight: 600;">Seeking support:</strong> 
                        <span style="color: {self.colors['text_primary']};">Talking to trusted friends, family, or professionals</span>
                    </li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def create_helpline_content(self):
        """Create helpline content."""
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: {self.colors['text_primary']}; font-size: 2.25rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif;">
                🆘 Mental Health Support
            </h1>
        </div>
        """, unsafe_allow_html=True)

        # Emergency section
        st.markdown(f"""
        <div class="emergency-section">
            <h2 class="emergency-title">
                🚨 Emergency Contacts
            </h2>
            <p style="margin-bottom: 1.5rem; color: {self.colors['text_primary']}; font-size: 1rem; font-weight: 500;">
                If you or someone you know is experiencing a mental health emergency, please contact these 24/7 helplines:
            </p>
            
            <div class="emergency-contact">
                <div class="contact-name">Emergency Ambulance:</div>
                <div class="contact-number">999</div>
            </div>
            
            <div class="emergency-contact">
                <div class="contact-name">Samaritans of Singapore (SOS):</div>
                <div class="contact-number">1-767</div>
            </div>
            
            <div class="emergency-contact">
                <div class="contact-name">National Care Hotline:</div>
                <div class="contact-number">1800-202-6868</div>
            </div>
            
            <div class="emergency-contact">
                <div class="contact-name">IMH Mental Health Helpline:</div>
                <div class="contact-number">6389-2222</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Youth support section
        st.markdown(f"""
        <div class="content-section">
            <h2 class="section-title">
                <span class="section-icon">🧑‍🎓</span>
                Youth-Specific Support
            </h2>
            
            <div class="info-card">
                <h4 class="info-title">CHAT (Community Health Assessment Team)</h4>
                <p class="info-description">For youth aged 16-30</p>
                <p class="info-contact">📞 6493-6500</p>
                <p><a href="https://www.chat.mentalhealth.sg/" target="_blank" class="info-link">https://www.chat.mentalhealth.sg/</a></p>
            </div>
            
            <div class="info-card">
                <h4 class="info-title">eC2 (Counselling Online)</h4>
                <p class="info-description">Web-based counselling service</p>
                <p><a href="https://www.ec2.sg/" target="_blank" class="info-link">https://www.ec2.sg/</a></p>
            </div>
            
            <div class="info-card">
                <h4 class="info-title">Tinkle Friend</h4>
                <p class="info-description">For primary school children</p>
                <p class="info-contact">📞 1800-274-4788</p>
                <p><a href="https://www.tinklefriend.sg/" target="_blank" class="info-link">https://www.tinklefriend.sg/</a></p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Remember section
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {self.colors['success']}, {self.colors['accent_dark']}); color: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 16px rgba(16, 185, 129, 0.25); text-align: center;">
            <h2 style="color: white; margin-bottom: 1rem; font-size: 1.5rem; font-weight: 600; font-family: 'Space Grotesk', sans-serif;">
                💚 Remember
            </h2>
            <p style="margin-bottom: 1rem; font-size: 1rem; line-height: 1.6;">
                Reaching out for support is a sign of strength, not weakness. Mental health professionals are trained to help you navigate difficult emotions and experiences.
            </p>
            <p style="margin: 0; font-weight: 600; font-size: 1.125rem;">
                You don't have to face these challenges alone.
            </p>
        </div>
        """, unsafe_allow_html=True)

    def create_about_content(self):
        """Create about content."""
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="color: {self.colors['text_primary']}; font-size: 2.25rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif;">
                ℹ️ About SootheAI
            </h1>
        </div>
        """, unsafe_allow_html=True)

        # Mission section
        st.markdown(f"""
        <div class="content-section">
            <h2 class="section-title">
                <span class="section-icon">🎯</span>
                Our Mission
            </h2>
            <div style="color: {self.colors['text_secondary']}; line-height: 1.7; font-size: 1rem;">
                SootheAI aims to help Singaporean youths understand, manage, and overcome anxiety through interactive storytelling enhanced by artificial intelligence. We believe that by engaging young people in relatable scenarios and providing them with practical coping strategies, we can make a meaningful impact on youth mental health in Singapore.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Approach section
        st.markdown(f"""
        <div class="content-section">
            <h2 class="section-title">
                <span class="section-icon">🤖</span>
                Our Approach
            </h2>
            <div style="color: {self.colors['text_secondary']}; line-height: 1.7; font-size: 1rem;">
                We combine the power of narrative storytelling with AI technology to create personalized learning experiences that adapt to each user's needs. Our stories are set in culturally relevant Singaporean contexts, addressing the unique pressures and challenges that local youth face.<br><br>Through interactive fiction, users can explore different scenarios, make choices, and learn about anxiety management techniques in a safe, engaging environment. The AI component ensures that each journey is uniquely tailored to provide the most helpful guidance.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Team section
        st.markdown(f"""
        <div class="content-section">
            <h2 class="section-title">
                <span class="section-icon">👥</span>
                The Team
            </h2>
            <div style="color: {self.colors['text_secondary']}; line-height: 1.7; font-size: 1rem;">
                SootheAI is developed by a team of mental health professionals, educational technologists, and AI specialists who are passionate about improving youth mental wellbeing in Singapore.<br><br>We work closely with psychologists, educators, and youth advisors to ensure that our content is accurate, appropriate, and effective.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Contact section
        st.markdown(f"""
        <div class="content-section">
            <h2 class="section-title">
                <span class="section-icon">📧</span>
                Contact Us
            </h2>
            <div style="color: {self.colors['text_secondary']}; line-height: 1.7; font-size: 1rem;">
                If you have questions, feedback, or would like to learn more about SootheAI, please reach out to us at <a href="mailto:contact@sootheai.sg" style="color: {self.colors['accent']}; text-decoration: none; font-weight: 500;">contact@sootheai.sg</a>.
            </div>
        </div>
        """, unsafe_allow_html=True)

    def create_footer(self):
        """Create the footer section."""
        st.markdown(f"""
        <div class="footer-section">
            <div class="footer-grid">
                <!-- Brand section -->
                <div>
                    <h3 class="footer-title">SootheAI</h3>
                    <p class="footer-text">
                        AI-powered mental health support through interactive storytelling, designed specifically for Singapore's youth.
                    </p>
                    <div class="footer-notice">
                        <strong style="color: {self.colors['accent_light']};">Remember:</strong> This is a supportive tool, not a replacement for professional help when needed.
                    </div>
                </div>
                
                <!-- Quick access -->
                <div>
                    <h4 class="footer-subtitle">Quick Access</h4>
                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <div class="quick-access-item">🏠 Start on Home tab</div>
                        <div class="quick-access-item">💬 Chat with SootheAI</div>
                        <div class="quick-access-item">📚 Learn about anxiety</div>
                        <div class="quick-access-item">🆘 Emergency contacts</div>
                    </div>
                </div>
                
                <!-- Emergency contacts -->
                <div>
                    <h4 style="margin: 0 0 1rem 0; font-size: 1.125rem; font-weight: 600; color: {self.colors['error']};">
                        🚨 Crisis Support
                    </h4>
                    <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                        <div class="emergency-contact-footer">
                            <div class="contact-name">Emergency: 999</div>
                        </div>
                        <div class="emergency-contact-footer">
                            <div class="contact-name">SOS: 1-767</div>
                        </div>
                        <div class="emergency-contact-footer">
                            <div class="contact-name">National Care: 1800-202-6868</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Bottom bar -->
            <div class="footer-bottom">
                <p style="margin: 0 0 0.5rem 0; opacity: 0.8; font-size: 0.9rem;">
                    © 2025 SootheAI • Confidential & Free • Available 24/7
                </p>
                <p style="margin: 0; opacity: 0.7; font-size: 0.8rem;">
                    If you're experiencing a mental health emergency, please contact emergency services immediately.
                    This tool provides educational support and is not a substitute for professional medical advice.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def main_loop(self, message: Optional[str]) -> str:
        """Enhanced main game loop with better error handling and UX."""
        if message is None:
            logger.info("Processing empty message in main loop")
            return self.consent_message

        logger.info(f"Processing message in main loop: {message[:50] if message else ''}...")
        
        try:
            # Process the message using narrative engine
            response, success = self.narrative_engine.process_message(message)

            # Enhanced TTS handling with better error management
            if (success and 
                hasattr(self.narrative_engine, 'game_state') and 
                self.narrative_engine.game_state.is_consent_given() and 
                message.lower() not in ['i agree', 'i agree with audio', 'i agree without audio', 'enable audio', 'disable audio', 'start game']):
                try:
                    self.tts_handler.run_tts_with_consent_and_limiting(response)
                except Exception as e:
                    logger.warning(f"TTS processing failed: {e}")
                    # Continue without TTS if it fails

            return response
            
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            return "I apologize, but I encountered an error. Please try again or contact support if the issue persists."

    def run(self):
        """Main method to run the Streamlit interface."""
        # Page config
        st.set_page_config(
            page_title="SootheAI - Mental Health Support",
            page_icon="🌟",
            layout="wide",
            initial_sidebar_state="collapsed"
        )

        # Apply custom CSS
        st.markdown(self.get_custom_css(), unsafe_allow_html=True)

        # Main navigation
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🏠 Home", 
            "💬 SootheAI Chat", 
            "📚 Learn About Anxiety", 
            "🆘 Get Help", 
            "ℹ️ About"
        ])

        with tab1:
            self.create_homepage()

        with tab2:
            self.create_chat_interface()

        with tab3:
            self.create_anxiety_education()

        with tab4:
            self.create_helpline_content()

        with tab5:
            self.create_about_content()

        # Footer (appears on all pages)
        self.create_footer()


def create_streamlit_interface(elevenlabs_client=None) -> StreamlitInterface:
    """
    Create a Streamlit interface instance.

    Args:
        elevenlabs_client: Optional ElevenLabs client instance for TTS functionality

    Returns:
        StreamlitInterface: Interface instance ready for launch
    """
    return StreamlitInterface(elevenlabs_client)


# Example usage for running the interface
if __name__ == "__main__":
    interface = create_streamlit_interface()
    interface.run()