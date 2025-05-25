"""
Gradio interface module for SootheAI.
Manages UI interactions and the web interface.
"""

import logging  # For application logging
import gradio as gr  # Web interface framework
# Type hints for better code documentation
from typing import Optional, Tuple, List, Dict, Any

# Import narrative engine creation function
from ..core.narrative_engine import create_narrative_engine
# Import game state management
from ..models.game_state import GameState
# Import TTS handler for audio functionality
from ..ui.tts_handler import get_tts_handler

# Set up logger for this module
logger = logging.getLogger(__name__)


class GradioInterface:
    """Class for managing the Gradio interface for SootheAI."""

    def __init__(self, character_data: Dict[str, Any], elevenlabs_client=None):
        """
        Initialize the Gradio interface with character data and optional TTS client.

        Args:
            character_data: Dictionary containing character information (name, personality, etc.)
            elevenlabs_client: Optional ElevenLabs client for text-to-speech functionality
        """
        # Keep your existing init code
        self.narrative_engine = create_narrative_engine(
            character_data)  # Initialize AI narrative engine
        # Initialize text-to-speech handler
        self.tts_handler = get_tts_handler(elevenlabs_client)
        self.interface = None  # Will hold the Gradio interface once created

        # Consent message shown to users when they first access the application
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

        # Homepage content - full width design with muted colors for professional appearance
        self.homepage_content = """
        <div style="width: 100%; background-color: #f1f5f9; padding: 0; margin: 0;">
            <!-- Main hero section -->
            <div style="background-color: #f8fafc; padding: 50px 20px; text-align: center; width: 100%;">
                <div style="max-width: 800px; margin: 0 auto;">
                    <h1 style="color: #64748b; font-size: 36px; margin-bottom: 20px;">Navigate Anxiety Through Stories</h1>
                    
                    <p style="color: #64748b; font-size: 18px; line-height: 1.6; margin-bottom: 40px;">
                        An interactive fiction experience designed to help Singaporean youths understand, manage, and overcome 
                        anxiety through engaging AI-powered storytelling.
                    </p>
                    
                    <p style="color: #64748b; font-size: 16px;">
                        To begin your journey, select the "SootheAI" tab above.
                    </p>
                </div>
            </div>
            
            <!-- Features section -->
            <div style="padding: 50px 20px; background-color: #e2e8f0; width: 100%;">
                <div style="max-width: 1200px; margin: 0 auto; display: flex; flex-wrap: wrap; justify-content: center; gap: 20px;">
                    <!-- Feature Box 1 -->
                    <div style="background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); flex: 1; min-width: 300px; max-width: 350px;">
                        <h2 style="color: #64748b; margin-bottom: 15px; font-size: 24px;">AI-Powered Stories</h2>
                        <p style="color: #64748b; line-height: 1.6;">Experience dynamically generated storylines that adapt to your choices, creating personalized learning journeys.</p>
                    </div>
                    
                    <!-- Feature Box 2 -->
                    <div style="background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); flex: 1; min-width: 300px; max-width: 350px;">
                        <h2 style="color: #64748b; margin-bottom: 15px; font-size: 24px;">Learn Coping Skills</h2>
                        <p style="color: #64748b; line-height: 1.6;">Discover practical techniques to manage anxiety that you can apply in your daily Singaporean student life.</p>
                    </div>
                    
                    <!-- Feature Box 3 -->
                    <div style="background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); flex: 1; min-width: 300px; max-width: 350px;">
                        <h2 style="color: #64748b; margin-bottom: 15px; font-size: 24px;">Local Context</h2>
                        <p style="color: #64748b; line-height: 1.6;">Stories and scenarios set in familiar Singaporean environments with culturally relevant situations and solutions.</p>
                    </div>
                </div>
            </div>
            
            <!-- Information section -->
            <div style="padding: 50px 20px; background-color: #f8fafc; width: 100%;">
                <div style="max-width: 800px; margin: 0 auto; text-align: center;">
                    <h2 style="color: #64748b; margin-bottom: 20px; font-size: 28px;">How SootheAI Works</h2>
                    <p style="color: #64748b; line-height: 1.6; margin-bottom: 30px;">
                        SootheAI combines interactive storytelling with educational content about anxiety management. Follow Serena's 
                        journey through the pressures of student life in Singapore, make choices that affect her story, and learn valuable 
                        coping skills along the way.
                    </p>
                    
                    <div style="background-color: #e6f7ed; padding: 20px; border-radius: 8px; text-align: left; margin-top: 30px;">
                        <h3 style="color: #2f6846; margin-bottom: 10px;">Ready to start?</h3>
                        <p style="color: #2f6846; line-height: 1.6;">Select the "SootheAI" tab to start your journey, or explore our Anxiety Education and Helpline resources.</p>
                    </div>
                </div>
            </div>
        </div>
        """

        # Content for the About tab - full width design with team and mission information
        self.about_content = """
        <div style="width: 100%; background-color: #f1f5f9; padding: 40px 20px;">
            <div style="max-width: 800px; margin: 0 auto;">
                <h1 style="color: #64748b; margin-bottom: 30px; font-size: 32px;">About SootheAI</h1>
                
                <div style="background-color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h2 style="color: #64748b; margin-bottom: 15px; font-size: 24px;">Our Mission</h2>
                    <p style="color: #64748b; line-height: 1.6;">SootheAI aims to help Singaporean youths understand, manage, and overcome anxiety through 
                    interactive storytelling enhanced by artificial intelligence. We believe that by engaging young people 
                    in relatable scenarios and providing them with practical coping strategies, we can make a meaningful 
                    impact on youth mental health in Singapore.</p>
                </div>
                
                <div style="background-color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h2 style="color: #64748b; margin-bottom: 15px; font-size: 24px;">Our Approach</h2>
                    <p style="color: #64748b; line-height: 1.6;">We combine the power of narrative storytelling with AI technology to create personalized learning 
                    experiences that adapt to each user's needs. Our stories are set in culturally relevant Singaporean 
                    contexts, addressing the unique pressures and challenges that local youth face.</p>
                    
                    <p style="color: #64748b; line-height: 1.6; margin-top: 15px;">Through interactive fiction, users can explore different scenarios, make choices, and learn about 
                    anxiety management techniques in a safe, engaging environment. The AI component ensures that each 
                    journey is uniquely tailored to provide the most helpful guidance.</p>
                </div>
                
                <div style="background-color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h2 style="color: #64748b; margin-bottom: 15px; font-size: 24px;">The Team</h2>
                    <p style="color: #64748b; line-height: 1.6;">SootheAI is developed by a team of mental health professionals, educational technologists, and 
                    AI specialists who are passionate about improving youth mental wellbeing in Singapore.</p>
                    
                    <p style="color: #64748b; line-height: 1.6; margin-top: 15px;">We work closely with psychologists, educators, and youth advisors to ensure that our content is 
                    accurate, appropriate, and effective.</p>
                </div>
                
                <div style="background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h2 style="color: #64748b; margin-bottom: 15px; font-size: 24px;">Contact Us</h2>
                    <p style="color: #64748b; line-height: 1.6;">If you have questions, feedback, or would like to learn more about SootheAI, please reach out to us at 
                    <a href="mailto:contact@sootheai.sg" style="color: #4ade80;">contact@sootheai.sg</a>.</p>
                </div>
            </div>
        </div>
        """

        # Content for the Anxiety Education tab - educational information about anxiety
        self.anxiety_education_content = """
        <div style="width: 100%; background-color: #f1f5f9; padding: 40px 20px;">
            <div style="max-width: 800px; margin: 0 auto;">
                <h1 style="color: #64748b; margin-bottom: 30px; font-size: 32px;">Anxiety Education</h1>
                
                <div style="background-color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h2 style="color: #64748b; margin-bottom: 15px; font-size: 24px;">Understanding Anxiety</h2>
                    <p style="color: #64748b; line-height: 1.6;">Anxiety is a normal response to stress or perceived threats. However, when anxiety becomes excessive or 
                    persistent, it can interfere with daily functioning and wellbeing. In Singapore's high-achievement educational 
                    context, many students experience academic-related anxiety.</p>
                </div>
                
                <div style="background-color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h2 style="color: #64748b; margin-bottom: 15px; font-size: 24px;">Common Signs of Anxiety</h2>
                    <ul style="color: #64748b; line-height: 1.6; margin-left: 20px;">
                        <li>Physical symptoms: racing heart, shortness of breath, stomach discomfort</li>
                        <li>Emotional symptoms: excessive worry, irritability, difficulty concentrating</li>
                        <li>Behavioral symptoms: avoidance, procrastination, perfectionism</li>
                        <li>Cognitive symptoms: negative thoughts, catastrophizing, all-or-nothing thinking</li>
                    </ul>
                </div>
                
                <div style="background-color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h2 style="color: #64748b; margin-bottom: 15px; font-size: 24px;">Coping Strategies</h2>
                    <p style="color: #64748b; line-height: 1.6;">These evidence-based strategies can help manage anxiety:</p>
                    <ul style="color: #64748b; line-height: 1.6; margin-left: 20px;">
                        <li><strong>Deep breathing:</strong> Slow, deliberate breathing to activate the relaxation response</li>
                        <li><strong>Mindfulness:</strong> Paying attention to the present moment without judgment</li>
                        <li><strong>Physical activity:</strong> Regular exercise to reduce stress hormones</li>
                        <li><strong>Balanced lifestyle:</strong> Adequate sleep, nutrition, and breaks</li>
                        <li><strong>Challenging negative thoughts:</strong> Identifying and reframing unhelpful thinking patterns</li>
                        <li><strong>Seeking support:</strong> Talking to trusted friends, family, or professionals</li>
                    </ul>
                </div>
                
                <div style="background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h2 style="color: #64748b; margin-bottom: 15px; font-size: 24px;">Singapore Resources</h2>
                    <p style="color: #64748b; line-height: 1.6;">If you're experiencing persistent anxiety, these resources can help:</p>
                    <ul style="color: #64748b; line-height: 1.6; margin-left: 20px;">
                        <li>National Care Hotline: 1800-202-6868</li>
                        <li>Samaritans of Singapore (SOS): 1-767</li>
                        <li>IMH Mental Health Helpline: 6389-2222</li>
                        <li>School counselors and ECG counselors</li>
                        <li>Community Health Assessment Team (CHAT): <a href="https://www.chat.mentalhealth.sg/" style="color: #4ade80;">CHAT website</a></li>
                    </ul>
                </div>
            </div>
        </div>
        """

        # Content for the Helpline tab - mental health crisis resources
        self.helpline_content = """
        <div style="width: 100%; background-color: #f1f5f9; padding: 40px 20px;">
            <div style="max-width: 800px; margin: 0 auto;">
                <h1 style="color: #64748b; margin-bottom: 30px; font-size: 32px;">Mental Health Helplines</h1>
                
                <div style="background-color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h2 style="color: #64748b; margin-bottom: 20px; font-size: 24px;">Emergency Contacts</h2>
                    <p style="color: #64748b; line-height: 1.6; margin-bottom: 20px;">If you or someone you know is experiencing a mental health emergency, please contact these 24/7 helplines:</p>
                    
                    <div style="background-color: #f8fafc; padding: 15px; margin-bottom: 10px; border-radius: 8px; color: #64748b;">
                        <strong>National Care Hotline:</strong> 1800-202-6868
                    </div>
                    <div style="background-color: #f8fafc; padding: 15px; margin-bottom: 10px; border-radius: 8px; color: #64748b;">
                        <strong>Samaritans of Singapore (SOS):</strong> 1-767
                    </div>
                    <div style="background-color: #f8fafc; padding: 15px; margin-bottom: 10px; border-radius: 8px; color: #64748b;">
                        <strong>IMH Mental Health Helpline:</strong> 6389-2222
                    </div>
                    <div style="background-color: #f8fafc; padding: 15px; margin-bottom: 10px; border-radius: 8px; color: #64748b;">
                        <strong>Emergency Ambulance:</strong> 995
                    </div>
                </div>
                
                <div style="background-color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h2 style="color: #64748b; margin-bottom: 20px; font-size: 24px;">Youth-Specific Support</h2>
                    
                    <div style="background-color: #f8fafc; padding: 20px; margin-bottom: 15px; border-radius: 8px; color: #64748b;">
                        <h3 style="margin-bottom: 10px; font-size: 18px;">CHAT (Community Health Assessment Team)</h3>
                        <p>For youth aged 16-30</p>
                        <p>6493-6500</p>
                        <p><a href="https://www.chat.mentalhealth.sg/" target="_blank" style="color: #4ade80;">www.chat.mentalhealth.sg</a></p>
                    </div>
                    
                    <div style="background-color: #f8fafc; padding: 20px; margin-bottom: 15px; border-radius: 8px; color: #64748b;">
                        <h3 style="margin-bottom: 10px; font-size: 18px;">eC2 (Counselling Online)</h3>
                        <p>Web-based counselling service</p>
                        <p><a href="https://www.ec2.sg/" target="_blank" style="color: #4ade80;">www.ec2.sg</a></p>
                    </div>
                    
                    <div style="background-color: #f8fafc; padding: 20px; margin-bottom: 15px; border-radius: 8px; color: #64748b;">
                        <h3 style="margin-bottom: 10px; font-size: 18px;">Tinkle Friend</h3>
                        <p>For primary school children</p>
                        <p>1800-274-4788</p>
                        <p><a href="https://www.tinklefriend.sg/" target="_blank" style="color: #4ade80;">www.tinklefriend.sg</a></p>
                    </div>
                </div>
                
                <div style="background-color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h2 style="color: #64748b; margin-bottom: 15px; font-size: 24px;">School Resources</h2>
                    <p style="color: #64748b; line-height: 1.6;">Most schools in Singapore have dedicated counsellors who provide confidential support for students:</p>
                    <ul style="color: #64748b; line-height: 1.6; margin-left: 20px;">
                        <li>School Counsellors</li>
                        <li>Education and Career Guidance (ECG) Counsellors</li>
                        <li>Student Health Advisors</li>
                    </ul>
                    <p style="color: #64748b; line-height: 1.6; margin-top: 15px;">Speak to your teacher or school administrator to get connected with these resources.</p>
                </div>
                
                <div style="background-color: #e6f7ed; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h2 style="color: #2f6846; margin-bottom: 15px; font-size: 24px;">Remember</h2>
                    <p style="color: #2f6846; line-height: 1.6;">Reaching out for support is a sign of strength, not weakness. Mental health professionals are trained to help you navigate difficult emotions and experiences.</p>
                    <p style="color: #2f6846; line-height: 1.6; margin-top: 10px;">You don't have to face these challenges alone.</p>
                </div>
            </div>
        </div>
        """

    logger.info("GradioInterface initialized")  # Log successful initialization

    def main_loop(self, message: Optional[str], history: List[Tuple[str, str]]) -> str:
        """
        Main game loop that processes player input and returns AI responses.

        Args:
            message: Player's input message (can be None for initial load)
            history: Conversation history as list of (user_message, ai_response) tuples

        Returns:
            str: AI's response or error message
        """
        # Handle None message (initial page load)
        if message is None:
            # Log empty message handling
            logger.info("Processing empty message in main loop")
            return self.consent_message  # Return consent message for first time users

        # Log message processing with truncated content for privacy
        logger.info(
            f"Processing message in main loop: {message[:50] if message else ''}...")

        # Process the message using narrative engine to generate AI response
        response, success = self.narrative_engine.process_message(message)

        # Process TTS if appropriate - only do this for game content, not consent messages
        if success and self.narrative_engine.game_state.is_consent_given() and message.lower() not in ['i agree', 'enable audio', 'disable audio', 'start game']:
            self.tts_handler.run_tts_with_consent_and_limiting(
                response)  # Generate speech for response

        return response  # Return the AI-generated response

    def create_interface(self) -> gr.Blocks:
        """
        Create the Gradio interface with multiple tabs.

        Returns:
            gr.Blocks: Configured Gradio interface with all tabs and styling
        """
        # Custom CSS to ensure full width layout and consistent styling
        custom_css = """
        .gradio-container {
            max-width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        .main {
            padding: 0 !important;
        }
        .tabs {
            border-radius: 0 !important;
            box-shadow: none !important;
        }
        .tab-content {
            padding: 0 !important;
        }
        .footer {
            margin-top: 0 !important;
        }
        .header {
            margin-bottom: 0 !important;
        }
        """

        # Create the interface using Gradio Blocks for custom layout
        with gr.Blocks(theme=gr.themes.Soft(), title="TheKopiCoders", css=custom_css) as blocks:
            # Simple header with dark background for branding
            gr.HTML("""
            <div style="width: 100%; background-color: #334155; color: white; padding: 15px 20px;">
                <h1 style="margin: 0; font-size: 24px;">TheKopiCoders</h1>
            </div>
            """)

            # Create tabbed interface for different sections
            with gr.Tabs() as tabs:
                # Home tab - landing page with overview
                with gr.Tab("Home"):
                    # Display homepage HTML content
                    gr.HTML(self.homepage_content)

                # Interactive Story Tab - main application functionality
                with gr.Tab("SootheAI"):
                    chat_interface = gr.ChatInterface(
                        self.main_loop,  # Main processing function for user messages
                        chatbot=gr.Chatbot(
                            height=600,  # Increased height for better readability
                            placeholder="Type 'I agree' to begin",  # Instruction for new users
                            show_copy_button=True,  # Allow users to copy text
                            render_markdown=False,  # Enable markdown formatting
                            # Pre-populate with consent message
                            value=[[None, self.consent_message]]
                        ),
                        textbox=gr.Textbox(
                            placeholder="Type 'I agree' to continue...",  # User instruction for consent
                            container=False,  # Remove container styling for cleaner look
                            scale=7  # Set relative width scaling
                        ),
                        examples=[  # Provide example user inputs for guidance
                            "Listen to music",
                            "Journal",
                            "Continue the story"
                        ],
                        cache_examples=False,  # Don't cache examples to ensure fresh responses
                    )

                # Anxiety Education Tab - educational content about anxiety management
                with gr.Tab("Anxiety Education"):
                    # Display anxiety education HTML content
                    gr.HTML(self.anxiety_education_content)

                # Helpline Tab - crisis support resources
                with gr.Tab("Helpline"):
                    # Display helpline HTML content
                    gr.HTML(self.helpline_content)

                # About Us Tab - information about the team and mission
                with gr.Tab("About Us"):
                    # Display about us HTML content
                    gr.HTML(self.about_content)

            # Simple footer with copyright and branding
            gr.HTML("""
            <div style="width: 100%; background-color: #334155; color: white; padding: 15px 20px; text-align: center;">
                © 2025 SootheAI | Helping Singaporean Youth Navigate Anxiety
            </div>
            """)

        self.interface = blocks  # Store the created interface
        return blocks  # Return the configured interface

    def launch(self, share: bool = True, server_name: str = "0.0.0.0", server_port: int = 7861) -> None:
        """
        Launch the Gradio interface on specified server settings.

        Args:
            share: Whether to create a public shareable link
            server_name: Server hostname (0.0.0.0 for all interfaces)
            server_port: Port number to run the server on
        """
        if self.interface is None:  # Create interface if not already created
            self.create_interface()

        try:
            self.interface.launch(  # Launch the web interface
                share=share,  # Enable/disable public sharing
                server_name=server_name,  # Set server hostname
                server_port=server_port  # Set server port
            )
        except Exception as e:
            # Log launch failure
            logger.error(f"Failed to launch Gradio interface: {str(e)}")
            raise  # Re-raise exception for calling code to handle

    def close(self) -> None:
        """Close the Gradio interface gracefully."""
        if self.interface is not None:  # Only close if interface exists
            try:
                self.interface.close()  # Gracefully close the interface
                # Log successful closure
                logger.info("Closed Gradio interface")
            except Exception as e:
                # Log closure error
                logger.error(f"Error closing Gradio interface: {str(e)}")


def create_gradio_interface(character_data: Dict[str, Any], elevenlabs_client=None) -> GradioInterface:
    """
    Create a Gradio interface instance.

    Args:
        character_data: Dictionary containing character information and personality
        elevenlabs_client: Optional ElevenLabs client instance for TTS functionality

    Returns:
        GradioInterface: Configured interface instance ready for launch
    """
    return GradioInterface(character_data, elevenlabs_client)  # Return new interface instance
