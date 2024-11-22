import streamlit as st
from dotenv import load_dotenv
from search import fallacy_search, FallacyResponse
import warnings
import logging
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

MAX_INPUT_LENGTH = 30000


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'response' not in st.session_state:
        st.session_state.response = None
    if 'error' not in st.session_state:
        st.session_state.error = None


def show_about_page():
    """Display the About page content."""
    st.header("About Fallacy Search")
    st.write("""
    The Fallacy Search application helps users identify potential logical fallacies in any text. 
    It uses GPT-4o to detect and analyze common reasoning errors and argumentative flaws.
    The tool aims to promote critical thinking and improve the quality of public discourse by making logical analysis 
    more accessible.
    
    Fallacy Search has been developed and benchmark tested on the [MAFALDA benchmark](https://arxiv.org/abs/2311.09761) 
    as part of a data science master thesis at Lucerne University of Applied Sciences and Arts (HSLU). For more 
    information, see GitHub links below.
    """)

    st.write("Applications:")
    st.markdown("""
    - Argument quality checking in journalism
    - Highlighting manipulative content and propaganda  
    - Analyzing blog posts and content on social media
    - Identifying weaknesses in legal arguments and court decisions
    - Flagging pseudoscience and unsound marketing
    """)
    st.write('👤 Author: Adrian Imfeld')
    st.write('📧 E-Mail: aimfeld@aimfeld.ch')
    st.write('🔗 LinkedIn: [aimfeld](https://www.linkedin.com/in/aimfeld/)')
    st.write('⭐ Source Code: [aimfeld/fallacy-search](https://github.com/aimfeld/fallacy-search)')
    st.write('📊 Benchmark Tests: [aimfeld/fallacy-detection](https://github.com/aimfeld/fallacy-detection/blob/main/fallacy_search.ipynb)')


def get_star_rating(rating: int):
    return '⭐' * rating + '☆' * (10 - rating)


def log(message: str):
    logging.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


def show_main_page():
    """Display the main Fallacy Search page content."""
    st.header("Fallacy Search")

    # Instruction text
    st.write("Enter text to detect logical fallacies and get a reasoning score:")

    # Text input area with character limit
    user_text = st.text_area(
        label="no label",
        label_visibility='hidden',  # Hide label
        max_chars=MAX_INPUT_LENGTH,
        height=100,
        key="user_input"
    )
    user_input = user_text.strip()

    if not st.session_state.processing:
        analyze_button = st.button("Analyze", type="primary")
        if analyze_button and user_input:
            st.session_state.response = None
            st.session_state.error = None
            st.session_state.processing = True
            st.rerun()

    if st.session_state.error:
        st.error(f"An error occurred: {st.session_state.error}")
        st.write("Please try again.")

    if st.session_state.processing:
        with st.spinner('Processing...'):
            try:
                # response = fallacy_search(user_input, model = 'gpt-4o-mini')
                response = fallacy_search(user_input)
                st.session_state.response = response
                log(f'Input Length: {len(user_input)}')
                log('Fallacies: ' + ', '.join([f'{f.fallacy} ({f.confidence * 100:.0f}%)' for f in response.fallacies]))
                log('Reasoning Score: ' + str(response.rating) if response.rating else 'No rating')
            except Exception as e:
                st.session_state.error = e

        st.session_state.processing = False
        st.rerun()

    if not st.session_state.processing and st.session_state.response:
        response: FallacyResponse = st.session_state.response

        with st.container():
            if response.fallacies:
                st.markdown('### Detected Fallacies')
                # Display each fallacy in an expander
                for i, fallacy in enumerate(response.fallacies, 1):
                    with st.expander(f'🎯 **Fallacy #{i}: {fallacy.fallacy}**', expanded=True):
                        st.markdown(f'**{fallacy.fallacy}:** {fallacy.definition}')
                        st.markdown(f'**Quote:** _“{fallacy.span}”_')
                        st.markdown(f'**Reason:** {fallacy.reason}')
                        if fallacy.defense:
                            st.markdown(f'**Defense:** {fallacy.defense}')
                        st.markdown(f'**Confidence:** {fallacy.confidence * 100:.0f}%')

            st.markdown("### Overall Analysis")
            st.markdown("**📝 Summary**")
            st.markdown(response.summary)

            st.markdown(f'**⭐ Reasoning Score**')
            if response.rating:
                st.markdown(f'{get_star_rating(response.rating)} ({response.rating} out of 10)')
            else:
                st.markdown("Not rated since the text seems to contain no arguments.")

            if response.fallacies:
                st.markdown("**⚠ Disclaimer**")
                st.markdown("""The interpretation of fallacies is often subjective and context-dependent. Consider the 
                            defenses as well. Critical thinking includes not blindly trusting this AI generated 
                            analysis. For more info, see the About page.""")


def main():
    """Main application function."""

    # Disable warnings like: Streaming with Pydantic response_format not yet supported.
    warnings.filterwarnings("ignore", message="Streaming with Pydantic response_format not yet supported.")
    logging.basicConfig(level=logging.INFO)

    st.set_page_config(page_title="Fallacy Search", page_icon="🔍", layout="wide")

    with open('.streamlit/style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    initialize_session_state()

    tab1, tab2 = st.tabs(["Fallacy Search", "About"])

    with tab1:
        show_main_page()
    with tab2:
        show_about_page()


if __name__ == "__main__":
    main()
