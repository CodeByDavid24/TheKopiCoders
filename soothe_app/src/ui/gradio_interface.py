"""
Gradio interface module for SootheAI.
Manages UI interactions and the web interface.
"""

import logging
import gradio as gr
from typing import Optional, Tuple, List, Dict, Any

from ..core.narrative_engine import create_narrative_engine
from ..models.game_state import GameState
from ..ui.tts_handler import get_tts_handler

# Set up logger
logger = logging.getLogger(__name__)


class GradioInterface:
    """Class for managing the Gradio interface for SootheAI."""

    def __init__(self, character_data: Dict[str, Any], elevenlabs_client=None):
        # Keep your existing init code
        self.narrative_engine = create_narrative_engine(character_data)
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

        # Content for the About tab
        self.about_content = """
            <div style="padding: 20px; max-width: 800px; margin: 0 auto; text-align: left;">
                <h1 style="margin-bottom: 30px; color: #1e293b;">About SootheAI</h1>
                
                <div style="margin-bottom: 40px;">
                    <h2 style="color: #6366F1; margin-bottom: 15px;">Our Mission</h2>
                    <p>SootheAI aims to help Singaporean youths understand, manage, and overcome anxiety through 
                    interactive storytelling enhanced by artificial intelligence. We believe that by engaging young people 
                    in relatable scenarios and providing them with practical coping strategies, we can make a meaningful 
                    impact on youth mental health in Singapore.</p>
                </div>
                
                <div style="margin-bottom: 40px;">
                    <h2 style="color: #6366F1; margin-bottom: 15px;">Our Approach</h2>
                    <p>We combine the power of narrative storytelling with AI technology to create personalized learning 
                    experiences that adapt to each user's needs. Our stories are set in culturally relevant Singaporean 
                    contexts, addressing the unique pressures and challenges that local youth face.</p>
                    
                    <p>Through interactive fiction, users can explore different scenarios, make choices, and learn about 
                    anxiety management techniques in a safe, engaging environment. The AI component ensures that each 
                    journey is uniquely tailored to provide the most helpful guidance.</p>
                </div>
                
                <div style="margin-bottom: 40px;">
                    <h2 style="color: #6366F1; margin-bottom: 15px;">The Team</h2>
                    <p>SootheAI is developed by a team of mental health professionals, educational technologists, and 
                    AI specialists who are passionate about improving youth mental wellbeing in Singapore.</p>
                    
                    <p>We work closely with psychologists, educators, and youth advisors to ensure that our content is 
                    accurate, appropriate, and effective.</p>
                </div>
                
                <div style="margin-bottom: 40px;">
                    <h2 style="color: #6366F1; margin-bottom: 15px;">Contact Us</h2>
                    <p>If you have questions, feedback, or would like to learn more about SootheAI, please reach out to us at 
                    <a href="mailto:contact@sootheai.sg">contact@sootheai.sg</a>.</p>
                </div>
            </div>
            """

        # Content for the Anxiety Education tab
        self.anxiety_education_content = """
            <div style="padding: 20px; max-width: 800px; margin: 0 auto; text-align: left;">
                <h1 style="margin-bottom: 30px; color: #1e293b;">Anxiety Education</h1>
                
                <div style="margin-bottom: 40px;">
                    <h2 style="color: #6366F1; margin-bottom: 15px;">Understanding Anxiety</h2>
                    <p>Anxiety is a normal response to stress or perceived threats. However, when anxiety becomes excessive or 
                    persistent, it can interfere with daily functioning and wellbeing. In Singapore's high-achievement educational 
                    context, many students experience academic-related anxiety.</p>
                </div>
                
                <div style="margin-bottom: 40px;">
                    <h2 style="color: #6366F1; margin-bottom: 15px;">Common Signs of Anxiety</h2>
                    <ul style="list-style-type: disc; margin-left: 20px;">
                        <li>Physical symptoms: racing heart, shortness of breath, stomach discomfort</li>
                        <li>Emotional symptoms: excessive worry, irritability, difficulty concentrating</li>
                        <li>Behavioral symptoms: avoidance, procrastination, perfectionism</li>
                        <li>Cognitive symptoms: negative thoughts, catastrophizing, all-or-nothing thinking</li>
                    </ul>
                </div>
                
                <div style="margin-bottom: 40px;">
                    <h2 style="color: #6366F1; margin-bottom: 15px;">Coping Strategies</h2>
                    <p>These evidence-based strategies can help manage anxiety:</p>
                    <ul style="list-style-type: disc; margin-left: 20px;">
                        <li><strong>Deep breathing:</strong> Slow, deliberate breathing to activate the relaxation response</li>
                        <li><strong>Mindfulness:</strong> Paying attention to the present moment without judgment</li>
                        <li><strong>Physical activity:</strong> Regular exercise to reduce stress hormones</li>
                        <li><strong>Balanced lifestyle:</strong> Adequate sleep, nutrition, and breaks</li>
                        <li><strong>Challenging negative thoughts:</strong> Identifying and reframing unhelpful thinking patterns</li>
                        <li><strong>Seeking support:</strong> Talking to trusted friends, family, or professionals</li>
                    </ul>
                </div>
                
                <div style="margin-bottom: 40px;">
                    <h2 style="color: #6366F1; margin-bottom: 15px;">Singapore Resources</h2>
                    <p>If you're experiencing persistent anxiety, these resources can help:</p>
                    <ul style="list-style-type: disc; margin-left: 20px;">
                        <li>National Care Hotline: 1800-202-6868</li>
                        <li>Samaritans of Singapore (SOS): 1-767</li>
                        <li>IMH Mental Health Helpline: 6389-2222</li>
                        <li>School counselors and ECG counselors</li>
                        <li>Community Health Assessment Team (CHAT): <a href="https://www.chat.mentalhealth.sg/">CHAT website</a></li>
                    </ul>
                </div>
            </div>
            """

    logger.info("GradioInterface initialized")

    def main_loop(self, message: Optional[str], history: List[Tuple[str, str]]) -> str:
        """
        Main game loop that processes player input and returns AI responses.

        Args:
            message: Player's input message
            history: Conversation history

        Returns:
            AI's response or error message
        """
        # Handle None message
        if message is None:
            logger.info("Processing empty message in main loop")
            return self.consent_message

        # Log message processing
        logger.info(
            f"Processing message in main loop: {message[:50] if message else ''}...")

        # Process the message using narrative engine
        response, success = self.narrative_engine.process_message(message)

        # Process TTS if appropriate - only do this for game content, not consent messages
        if success and self.narrative_engine.game_state.is_consent_given() and message.lower() not in ['i agree', 'enable audio', 'disable audio', 'start game']:
            self.tts_handler.run_tts_with_consent_and_limiting(response)

        return response

    def create_interface(self) -> gr.Blocks:
        """
        Create the Gradio interface with multiple tabs.

        Returns:
            Gradio Blocks interface
        """
        with gr.Blocks(theme="soft", title="SootheAI") as blocks:
            with gr.Tabs() as tabs:
                # Interactive Story Tab
                with gr.Tab("Serena's Story"):
                    chat_interface = gr.ChatInterface(
                        self.main_loop,  # Main processing function
                        chatbot=gr.Chatbot(
                            height=500,
                            placeholder="Type 'I agree' to begin",
                            show_copy_button=True,
                            render_markdown=True,
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

                # Anxiety Education Tab
                with gr.Tab("Anxiety Education"):
                    gr.HTML(self.anxiety_education_content)

                # About Us Tab
                with gr.Tab("About Us"):
                    gr.HTML(self.about_content)

        self.interface = blocks
        return blocks

    def launch(self, share: bool = True, server_name: str = "0.0.0.0", server_port: int = 7861) -> None:
        """
        Launch the web interface.

        Args:
            share: Whether to create a shareable link
            server_name: Server name to listen on
            server_port: Port to serve on
        """
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
        """Close the Gradio interface."""
        if self.interface is not None:
            try:
                self.interface.close()
                logger.info("Closed Gradio interface")
            except Exception as e:
                logger.error(f"Error closing Gradio interface: {str(e)}")


def create_gradio_interface(character_data: Dict[str, Any], elevenlabs_client=None) -> GradioInterface:
    """
    Create a Gradio interface instance.

    Args:
        character_data: Character data dictionary
        elevenlabs_client: ElevenLabs client instance, if any

    Returns:
        GradioInterface instance
    """
    return GradioInterface(character_data, elevenlabs_client)
