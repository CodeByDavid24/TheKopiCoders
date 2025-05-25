"""
Gradio interface module for SootheAI with consistent color scheme.
"""

import logging
import gradio as gr
from typing import Optional, Tuple, List, Dict, Any

# Import your existing modules
from ..core.narrative_engine import create_narrative_engine
from ..models.game_state import GameState
from ..ui.tts_handler import get_tts_handler

logger = logging.getLogger(__name__)

class GradioInterface:
    """Class for managing the Gradio interface for SootheAI with consistent styling."""

    def __init__(self, elevenlabs_client=None):
        """Initialize the Gradio interface with consistent color scheme."""
        
        # Color scheme - Define once, use everywhere
        self.colors = {
            'primary': '#1e293b',      # Dark slate - main brand color
            'secondary': '#334155',    # Medium slate - secondary elements
            'tertiary': '#475569',     # Light slate - tertiary elements
            'background': '#f8fafc',   # Very light slate - main background
            'surface': '#ffffff',      # White - content surfaces
            'surface_alt': '#f1f5f9',  # Light background - alternative surfaces
            'accent': '#10b981',       # Emerald - accent/CTA color
            'accent_dark': '#047857',  # Dark emerald - accent hover/active
            'text_primary': '#1e293b', # Dark slate - primary text
            'text_secondary': '#64748b', # Medium slate - secondary text
            'text_light': '#94a3b8',   # Light slate - tertiary text
            'success': '#10b981',      # Success messages
            'warning': '#f59e0b',      # Warning messages
            'error': '#ef4444',        # Error messages
        }
        
        self.narrative_engine = create_narrative_engine()
        self.tts_handler = get_tts_handler(elevenlabs_client)
        self.interface = None

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

    def _create_page_wrapper(self, content: str) -> str:
        """Create a consistent page wrapper with unified styling."""
        return f'<div style="width: 100%; background-color: {self.colors["surface_alt"]}; padding: 0; margin: 0; min-height: 80vh;">{content}</div>'

    def _create_section(self, title: str, content: str) -> str:
        """Create a consistent section with unified styling."""
        return f'''
        <div style="background-color: {self.colors["surface"]}; padding: 30px; border-radius: 12px; 
                    margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h2 style="color: {self.colors["text_primary"]}; margin-bottom: 16px; 
                       font-size: 24px; font-weight: 600;">{title}</h2>
            <p style="color: {self.colors["text_secondary"]}; line-height: 1.6; margin: 0;">
                {content}
            </p>
        </div>
        '''

    def _create_feature_box(self, title: str, content: str) -> str:
        """Create a consistent feature box."""
        return f'''
        <div style="background-color: {self.colors["surface"]}; padding: 32px; 
                    border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
                    flex: 1; min-width: 300px; max-width: 350px;">
            <h2 style="color: {self.colors["text_primary"]}; margin-bottom: 16px; 
                       font-size: 24px; font-weight: 600;">{title}</h2>
            <p style="color: {self.colors["text_secondary"]}; line-height: 1.6; margin: 0;">
                {content}
            </p>
        </div>
        '''

    def _create_contact_card(self, title: str, subtitle: str = "", phone: str = "", website: str = "") -> str:
        """Create a consistent contact card."""
        subtitle_html = f'<p style="color: {self.colors["text_secondary"]}; margin: 4px 0; font-size: 16px;">{subtitle}</p>' if subtitle else ''
        phone_html = f'<p style="color: {self.colors["text_primary"]}; font-weight: 500; margin: 4px 0; font-size: 16px;">{phone}</p>' if phone else ''
        website_html = f'<p style="margin: 4px 0;"><a href="{website}" target="_blank" style="color: {self.colors["accent"]}; text-decoration: none; font-size: 16px;">{website}</a></p>' if website else ''
        
        return f'''
        <div style="background-color: {self.colors["background"]}; padding: 20px; 
                    margin-bottom: 12px; border-radius: 8px; 
                    border-left: 4px solid {self.colors["accent"]};">
            <h3 style="margin-bottom: 8px; font-size: 18px; font-weight: 600; 
                       color: {self.colors["text_primary"]};">{title}</h3>
            {subtitle_html}
            {phone_html}
            {website_html}
        </div>
        '''

    def create_homepage_content(self) -> str:
        """Create homepage content with consistent styling."""
        hero_section = f'''
            <div style="background: linear-gradient(135deg, {self.colors["primary"]} 0%, {self.colors["secondary"]} 100%); 
                        padding: 60px 20px; text-align: center; width: 100%;">
                <div style="max-width: 800px; margin: 0 auto;">
                    <h1 style="color: white; font-size: 42px; margin-bottom: 24px; 
                               font-weight: 700;">Navigate Anxiety Through Stories</h1>
                    
                    <p style="color: rgba(255,255,255,0.9); font-size: 20px; line-height: 1.6; 
                              margin-bottom: 32px;">
                        An interactive fiction experience designed to help Singaporean youths understand, 
                        manage, and overcome anxiety through engaging AI-powered storytelling.
                    </p>
                    
                    <div style="background-color: {self.colors["accent"]}; color: white; 
                                padding: 12px 24px; border-radius: 8px; display: inline-block; 
                                font-weight: 600;">
                        To begin your journey, select the "SootheAI" tab above
                    </div>
                </div>
            </div>
        '''
        
        features_section = f'''
            <div style="padding: 60px 20px; background-color: {self.colors["background"]}; width: 100%;">
                <div style="max-width: 1200px; margin: 0 auto; display: flex; flex-wrap: wrap; 
                            justify-content: center; gap: 24px;">
                    {self._create_feature_box(
                        "AI-Powered Stories",
                        "Experience dynamically generated storylines that adapt to your choices, creating personalized learning journeys."
                    )}
                    {self._create_feature_box(
                        "Learn Coping Skills", 
                        "Discover practical techniques to manage anxiety that you can apply in your daily Singaporean student life."
                    )}
                    {self._create_feature_box(
                        "Local Context",
                        "Stories and scenarios set in familiar Singaporean environments with culturally relevant situations and solutions."
                    )}
                </div>
            </div>
        '''
        
        how_it_works = f'''
            <div style="padding: 60px 20px; background-color: {self.colors["surface"]}; width: 100%;">
                <div style="max-width: 800px; margin: 0 auto; text-align: center;">
                    <h2 style="color: {self.colors["text_primary"]}; margin-bottom: 24px; 
                               font-size: 32px; font-weight: 600;">How SootheAI Works</h2>
                    <p style="color: {self.colors["text_secondary"]}; line-height: 1.6; 
                              margin-bottom: 32px; font-size: 18px;">
                        SootheAI combines interactive storytelling with AI-generated characters to create 
                        unique educational experiences about anxiety management. Each playthrough features 
                        organically created characters and situations that emerge from your choices.
                    </p>
                    
                    <div style="background: linear-gradient(135deg, {self.colors["accent"]} 0%, {self.colors["accent_dark"]} 100%); 
                                padding: 24px; border-radius: 12px; text-align: left; margin-top: 32px;">
                        <h3 style="color: white; margin-bottom: 12px; font-weight: 600;">Ready to start?</h3>
                        <p style="color: rgba(255,255,255,0.9); line-height: 1.6; margin: 0;">
                            Select the "SootheAI" tab to start your journey, or explore our Anxiety Education and Helpline resources.
                        </p>
                    </div>
                </div>
            </div>
        '''
        
        return self._create_page_wrapper(hero_section + features_section + how_it_works)

    def create_about_content(self) -> str:
        """Create about content with consistent styling."""
        header = f'''
            <div style="padding: 50px 20px;">
                <div style="max-width: 800px; margin: 0 auto;">
                    <h1 style="color: {self.colors["text_primary"]}; margin-bottom: 40px; 
                               font-size: 36px; font-weight: 700; text-align: center;">About SootheAI</h1>
        '''
        
        mission = self._create_section(
            "Our Mission",
            "SootheAI aims to help Singaporean youths understand, manage, and overcome anxiety through interactive storytelling enhanced by artificial intelligence. We believe that by engaging young people in relatable scenarios and providing them with practical coping strategies, we can make a meaningful impact on youth mental health in Singapore."
        )
        
        approach = self._create_section(
            "Our Approach", 
            "We combine the power of narrative storytelling with AI technology to create personalized learning experiences that adapt to each user's needs. Our stories are set in culturally relevant Singaporean contexts, addressing the unique pressures and challenges that local youth face.<br><br>Through interactive fiction, users can explore different scenarios, make choices, and learn about anxiety management techniques in a safe, engaging environment. The AI component ensures that each journey is uniquely tailored to provide the most helpful guidance."
        )
        
        team = self._create_section(
            "The Team",
            "SootheAI is developed by a team of mental health professionals, educational technologists, and AI specialists who are passionate about improving youth mental wellbeing in Singapore.<br><br>We work closely with psychologists, educators, and youth advisors to ensure that our content is accurate, appropriate, and effective."
        )
        
        contact = self._create_section(
            "Contact Us",
            f'If you have questions, feedback, or would like to learn more about SootheAI, please reach out to us at <a href="mailto:contact@sootheai.sg" style="color: {self.colors["accent"]}; text-decoration: none; font-weight: 500;">contact@sootheai.sg</a>.'
        )
        
        footer = '''
                </div>
            </div>
        '''
        
        return self._create_page_wrapper(header + mission + approach + team + contact + footer)

    def create_anxiety_education_content(self) -> str:
        """Create anxiety education content with consistent styling."""
        header = f'''
            <div style="padding: 50px 20px;">
                <div style="max-width: 800px; margin: 0 auto;">
                    <h1 style="color: {self.colors["text_primary"]}; margin-bottom: 40px; 
                               font-size: 36px; font-weight: 700; text-align: center;">Anxiety Education</h1>
        '''
        
        understanding = self._create_section(
            "Understanding Anxiety",
            "Anxiety is a normal response to stress or perceived threats. However, when anxiety becomes excessive or persistent, it can interfere with daily functioning and wellbeing. In Singapore's high-achievement educational context, many students experience academic-related anxiety."
        )
        
        signs = f'''
        <div style="background-color: {self.colors["surface"]}; padding: 30px; border-radius: 12px; 
                    margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h2 style="color: {self.colors["text_primary"]}; margin-bottom: 16px; 
                       font-size: 24px; font-weight: 600;">Common Signs of Anxiety</h2>
            <ul style="color: {self.colors["text_secondary"]}; line-height: 1.6; margin-left: 20px; font-size: 16px;">
                <li style="color: {self.colors["text_secondary"]}; margin-bottom: 8px;"><strong style="color: {self.colors["text_primary"]};">Physical symptoms:</strong> racing heart, shortness of breath, stomach discomfort</li>
                <li style="color: {self.colors["text_secondary"]}; margin-bottom: 8px;"><strong style="color: {self.colors["text_primary"]};">Emotional symptoms:</strong> excessive worry, irritability, difficulty concentrating</li>
                <li style="color: {self.colors["text_secondary"]}; margin-bottom: 8px;"><strong style="color: {self.colors["text_primary"]};">Behavioral symptoms:</strong> avoidance, procrastination, perfectionism</li>
                <li style="color: {self.colors["text_secondary"]}; margin-bottom: 8px;"><strong style="color: {self.colors["text_primary"]};">Cognitive symptoms:</strong> negative thoughts, catastrophizing, all-or-nothing thinking</li>
            </ul>
        </div>
        '''
        
        coping = f'''
        <div style="background-color: {self.colors["surface"]}; padding: 30px; border-radius: 12px; 
                    margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h2 style="color: {self.colors["text_primary"]}; margin-bottom: 16px; 
                       font-size: 24px; font-weight: 600;">Coping Strategies</h2>
            <p style="color: {self.colors["text_secondary"]}; line-height: 1.6; margin-bottom: 16px; font-size: 16px;">
                These evidence-based strategies can help manage anxiety:
            </p>
            <ul style="color: {self.colors["text_secondary"]}; line-height: 1.6; margin-left: 20px; font-size: 16px;">
                <li style="color: {self.colors["text_secondary"]}; margin-bottom: 8px;"><strong style="color: {self.colors["text_primary"]};">Deep breathing:</strong> Slow, deliberate breathing to activate the relaxation response</li>
                <li style="color: {self.colors["text_secondary"]}; margin-bottom: 8px;"><strong style="color: {self.colors["text_primary"]};">Mindfulness:</strong> Paying attention to the present moment without judgment</li>
                <li style="color: {self.colors["text_secondary"]}; margin-bottom: 8px;"><strong style="color: {self.colors["text_primary"]};">Physical activity:</strong> Regular exercise to reduce stress hormones</li>
                <li style="color: {self.colors["text_secondary"]}; margin-bottom: 8px;"><strong style="color: {self.colors["text_primary"]};">Balanced lifestyle:</strong> Adequate sleep, nutrition, and breaks</li>
                <li style="color: {self.colors["text_secondary"]}; margin-bottom: 8px;"><strong style="color: {self.colors["text_primary"]};">Challenging negative thoughts:</strong> Identifying and reframing unhelpful thinking patterns</li>
                <li style="color: {self.colors["text_secondary"]}; margin-bottom: 8px;"><strong style="color: {self.colors["text_primary"]};">Seeking support:</strong> Talking to trusted friends, family, or professionals</li>
            </ul>
        </div>
        '''
        
        footer = '''
                </div>
            </div>
        '''
        
        return self._create_page_wrapper(header + understanding + signs + coping + footer)

    def create_helpline_content(self) -> str:
        """Create helpline content with consistent styling."""
        header = f'''
            <div style="padding: 50px 20px;">
                <div style="max-width: 800px; margin: 0 auto;">
                    <h1 style="color: {self.colors["text_primary"]}; margin-bottom: 40px; 
                               font-size: 36px; font-weight: 700; text-align: center;">Mental Health Helplines</h1>
        '''
        
        emergency = f'''
        <div style="background-color: {self.colors["surface"]}; padding: 30px; border-radius: 12px; 
                    margin-bottom: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h2 style="color: {self.colors["text_primary"]}; margin-bottom: 20px; 
                       font-size: 24px; font-weight: 600;">Emergency Contacts</h2>
            <p style="color: {self.colors["text_secondary"]}; line-height: 1.6; margin-bottom: 20px; font-size: 16px;">
                If you or someone you know is experiencing a mental health emergency, please contact these 24/7 helplines:
            </p>
            
            <div style="background-color: {self.colors["background"]}; padding: 16px; margin-bottom: 12px; 
                        border-radius: 8px; border-left: 4px solid {self.colors["error"]};">
                <strong style="color: {self.colors["text_primary"]}; font-size: 16px;">National Care Hotline:</strong>
                <span style="color: {self.colors["text_primary"]}; font-size: 16px;"> 1800-202-6868</span>
            </div>
            <div style="background-color: {self.colors["background"]}; padding: 16px; margin-bottom: 12px; 
                        border-radius: 8px; border-left: 4px solid {self.colors["error"]};">
                <strong style="color: {self.colors["text_primary"]}; font-size: 16px;">Samaritans of Singapore (SOS):</strong>
                <span style="color: {self.colors["text_primary"]}; font-size: 16px;"> 1-767</span>
            </div>
            <div style="background-color: {self.colors["background"]}; padding: 16px; margin-bottom: 12px; 
                        border-radius: 8px; border-left: 4px solid {self.colors["error"]};">
                <strong style="color: {self.colors["text_primary"]}; font-size: 16px;">IMH Mental Health Helpline:</strong>
                <span style="color: {self.colors["text_primary"]}; font-size: 16px;"> 6389-2222</span>
            </div>
            <div style="background-color: {self.colors["background"]}; padding: 16px; margin-bottom: 12px; 
                        border-radius: 8px; border-left: 4px solid {self.colors["error"]};">
                <strong style="color: {self.colors["text_primary"]}; font-size: 16px;">Emergency Ambulance:</strong>
                <span style="color: {self.colors["text_primary"]}; font-size: 16px;"> 995</span>
            </div>
        </div>
        '''
        
        youth_support = f'''
        <div style="background-color: {self.colors["surface"]}; padding: 30px; border-radius: 12px; 
                    margin-bottom: 30px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h2 style="color: {self.colors["text_primary"]}; margin-bottom: 20px; 
                       font-size: 24px; font-weight: 600;">Youth-Specific Support</h2>
            
            {self._create_contact_card(
                "CHAT (Community Health Assessment Team)",
                "For youth aged 16-30", 
                "6493-6500", 
                "https://www.chat.mentalhealth.sg/"
            )}
            
            {self._create_contact_card(
                "eC2 (Counselling Online)",
                "Web-based counselling service", 
                "", 
                "https://www.ec2.sg/"
            )}
            
            {self._create_contact_card(
                "Tinkle Friend",
                "For primary school children", 
                "1800-274-4788", 
                "https://www.tinklefriend.sg/"
            )}
        </div>
        '''
        
        remember = f'''
        <div style="background: linear-gradient(135deg, {self.colors["success"]} 0%, {self.colors["accent_dark"]} 100%); 
                    padding: 30px; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h2 style="color: white; margin-bottom: 16px; font-size: 24px; font-weight: 600;">Remember</h2>
            <p style="color: rgba(255,255,255,0.95); line-height: 1.6; margin-bottom: 12px;">
                Reaching out for support is a sign of strength, not weakness. Mental health professionals are trained to help you navigate difficult emotions and experiences.
            </p>
            <p style="color: rgba(255,255,255,0.95); line-height: 1.6; margin: 0; font-weight: 500;">
                You don't have to face these challenges alone.
            </p>
        </div>
        '''
        
        footer = '''
                </div>
            </div>
        '''
        
        return self._create_page_wrapper(header + emergency + youth_support + remember + footer)

    def create_custom_theme(self) -> gr.Theme:
        """Create a custom Gradio theme with consistent colors."""
        return gr.themes.Base(
            primary_hue=gr.themes.colors.slate,
            secondary_hue=gr.themes.colors.emerald,
            neutral_hue=gr.themes.colors.slate,
            font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
        ).set(
            # Button colors
            button_primary_background_fill=self.colors['accent'],
            button_primary_background_fill_hover=self.colors['accent_dark'],
            button_primary_text_color="white",
            button_secondary_background_fill=self.colors['surface'],
            button_secondary_background_fill_hover=self.colors['background'],
            button_secondary_text_color=self.colors['text_primary'],
            
            # Input colors  
            input_background_fill=self.colors['surface'],
            input_border_color=self.colors['tertiary'],
            input_border_color_focus=self.colors['accent'],
            
            # General colors
            background_fill_primary=self.colors['background'],
            background_fill_secondary=self.colors['surface'],
            border_color_primary=self.colors['tertiary'],
            
            # Text colors
            body_text_color=self.colors['text_secondary'],
            body_text_color_subdued=self.colors['text_light'],
        )

    def main_loop(self, message: Optional[str], history: List[Tuple[str, str]]) -> str:
        """Main game loop that processes player input and returns AI responses."""
        if message is None:
            logger.info("Processing empty message in main loop")
            return self.consent_message

        logger.info(f"Processing message in main loop: {message[:50] if message else ''}...")
        response, success = self.narrative_engine.process_message(message)

        if success and self.narrative_engine.game_state.is_consent_given() and message.lower() not in ['i agree', 'enable audio', 'disable audio', 'start game']:
            self.tts_handler.run_tts_with_consent_and_limiting(response)

        return response

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface with consistent styling."""
        
        # Enhanced CSS for consistent styling
        custom_css = f"""
        .gradio-container {{
            max-width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
            font-family: 'Inter', ui-sans-serif, system-ui, sans-serif !important;
        }}
        .main {{
            padding: 0 !important;
        }}
        .tabs {{
            border-radius: 0 !important;
            box-shadow: none !important;
            background-color: {self.colors['surface']} !important;
        }}
        .tab-nav {{
            background-color: {self.colors['background']} !important;
            border-bottom: 1px solid {self.colors['tertiary']} !important;
        }}
        .tab-nav button {{
            color: {self.colors['text_secondary']} !important;
            font-weight: 500 !important;
        }}
        .tab-nav button.selected {{
            color: {self.colors['accent']} !important;
            border-bottom-color: {self.colors['accent']} !important;
        }}
        .footer {{
            margin-top: 0 !important;
        }}
        .header {{
            margin-bottom: 0 !important;
        }}
        /* Chat interface styling */
        .chat-interface .message {{
            border-radius: 12px !important;
            margin-bottom: 12px !important;
        }}
        .chat-interface .message.user {{
            background-color: {self.colors['accent']} !important;
            color: white !important;
        }}
        .chat-interface .message.bot {{
            background-color: {self.colors['surface']} !important;
            color: {self.colors['text_primary']} !important;
            border: 1px solid {self.colors['background']} !important;
        }}
        /* Input styling */
        .input-container input {{
            border-radius: 8px !important;
            border: 2px solid {self.colors['tertiary']} !important;
        }}
        .input-container input:focus {{
            border-color: {self.colors['accent']} !important;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
        }}
        /* Button styling */
        button.primary {{
            background: linear-gradient(135deg, {self.colors['accent']} 0%, {self.colors['accent_dark']} 100%) !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
        }}
        button.primary:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
        }}
        """

        # Create interface with custom theme
        with gr.Blocks(theme=self.create_custom_theme(), title="TheKopiCoders", css=custom_css) as blocks:
            
            # Consistent header
            gr.HTML(f"""
            <div style="width: 100%; background: linear-gradient(135deg, {self.colors['primary']} 0%, {self.colors['secondary']} 100%); 
                        color: white; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h1 style="margin: 0; font-size: 28px; font-weight: 700;">TheKopiCoders</h1>
                <p style="margin: 4px 0 0 0; opacity: 0.9; font-size: 14px;">SootheAI - Mental Health Through Interactive Stories</p>
            </div>
            """)

            with gr.Tabs() as tabs:
                with gr.Tab("Home"):
                    gr.HTML(self.create_homepage_content())

                with gr.Tab("SootheAI"):
                    chat_interface = gr.ChatInterface(
                        self.main_loop,
                        chatbot=gr.Chatbot(
                            height=600,
                            placeholder="Type 'I agree' to begin",
                            show_copy_button=True,
                            render_markdown=False,
                            value=[[None, self.consent_message]]
                        ),
                        textbox=gr.Textbox(
                            placeholder="Type 'I agree' to continue...",
                            container=False,
                            scale=7
                        ),
                        examples=[
                            "Listen to music",
                            "Journal", 
                            "Continue the story"
                        ],
                        cache_examples=False,
                    )

                with gr.Tab("Anxiety Education"):
                    gr.HTML(self.create_anxiety_education_content())

                with gr.Tab("Helpline"):
                    gr.HTML(self.create_helpline_content())

                with gr.Tab("About Us"):
                    gr.HTML(self.create_about_content())

            # Consistent footer
            gr.HTML(f"""
            <div style="width: 100%; background-color: {self.colors['primary']}; color: white; 
                        padding: 24px 20px; text-align: center;">
                <p style="margin: 0; font-size: 14px; opacity: 0.9;">
                    © 2025 SootheAI | Helping Singaporean Youth Navigate Anxiety
                </p>
            </div>
            """)

        self.interface = blocks
        return blocks

    def launch(self, share: bool = True, server_name: str = "0.0.0.0", server_port: int = 7861) -> None:
        """Launch the Gradio interface."""
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
        """Close the Gradio interface gracefully."""
        if self.interface is not None:
            try:
                self.interface.close()
                logger.info("Closed Gradio interface")
            except Exception as e:
                logger.error(f"Error closing Gradio interface: {str(e)}")


def create_gradio_interface(elevenlabs_client=None) -> GradioInterface:
    """
    Create a Gradio interface instance with consistent styling.

    Args:
        elevenlabs_client: Optional ElevenLabs client instance for TTS functionality

    Returns:
        GradioInterface: Configured interface instance ready for launch
    """
    return GradioInterface(elevenlabs_client)