import streamlit as st
import openai
import json
import re

# Initialize OpenAI client
def initialize_openai():
    try:
        # Try to get API key from secrets first
        api_key = st.secrets["OPENAI_API_KEY"]
        client = OpenAI(api_key=api_key)
        return client
    except (KeyError, FileNotFoundError):
        # Fallback to manual input if secrets not available
        st.error("⚠️ OpenAI API key not found in secrets. Please add OPENAI_API_KEY to your Streamlit secrets.")
        st.info("To add secrets, create a `.streamlit/secrets.toml` file in your project root with: `OPENAI_API_KEY = \"your_api_key_here\"`")
        return None

def generate_writing_prompt():
    """Generate a writing prompt appropriate for 6th graders"""
    prompt = """
    Generate a creative and engaging writing prompt appropriate for 6th grade students (ages 11-12). 
    The prompt should:
    - Be age-appropriate and interesting
    - Encourage creativity and personal expression
    - Be clear and easy to understand
    - Allow for different types of responses (narrative, descriptive, persuasive, etc.)
    - Include a brief instruction about what type of essay they should write
    
    Provide just the prompt text, nothing else.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating prompt: {str(e)}")
        return None

def get_revision_suggestions(title, thesis, essay):
    """Get revision suggestions for the student's essay"""
    prompt = f"""
    You are a helpful 6th grade teacher reviewing a student's essay. Please provide constructive feedback and suggestions for improvement. Be encouraging and supportive while offering specific, actionable advice.

    Essay Title: {title}
    Thesis Statement: {thesis}
    Essay: {essay}

    Please provide:
    1. 2-3 specific strengths of the essay
    2. 2-3 areas for improvement with specific suggestions
    3. Questions to help the student think deeper about their topic
    4. Encouragement and positive reinforcement

    Keep your language appropriate for a 6th grader and be constructive, not critical.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error getting revision suggestions: {str(e)}")
        return None

def grade_essay(title, thesis, essay):
    """Grade the essay and provide final comments"""
    prompt = f"""
    You are a 6th grade teacher grading a student's essay. Please evaluate the essay based on 6th grade writing standards and provide a fair, constructive assessment.

    Essay Title: {title}
    Thesis Statement: {thesis}
    Essay: {essay}

    Please evaluate based on:
    - Content and ideas (25%)
    - Organization and structure (25%)
    - Voice and word choice (25%)
    - Grammar and mechanics (25%)

    Provide your response in this exact format:
    GRADE: [Letter grade A-F]
    PERCENTAGE: [Number from 0-100]
    COMMENTS: [2-3 paragraphs of specific, encouraging feedback explaining the grade and highlighting both strengths and areas for growth]
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error grading essay: {str(e)}")
        return None

def parse_grade_response(response):
    """Parse the grade response to extract letter grade, percentage, and comments"""
    if not response:
        return None, None, None
    
    # Extract letter grade
    grade_match = re.search(r'GRADE:\s*([A-F][+-]?)', response)
    letter_grade = grade_match.group(1) if grade_match else "Not provided"
    
    # Extract percentage
    percent_match = re.search(r'PERCENTAGE:\s*(\d+)', response)
    percentage = int(percent_match.group(1)) if percent_match else None
    
    # Extract comments
    comments_match = re.search(r'COMMENTS:\s*(.*)', response, re.DOTALL)
    comments = comments_match.group(1).strip() if comments_match else "No comments provided"
    
    return letter_grade, percentage, comments

def main():
    st.title("📝 Writing Assignment")
    st.markdown("Welcome to your writing assignment! Follow the steps below to complete your essay.")
    
    # Initialize OpenAI
    if not initialize_openai():
        st.stop()
    
    # Initialize session state
    if "prompt" not in st.session_state:
        st.session_state.prompt = ""
    if "revision_suggestions" not in st.session_state:
        st.session_state.revision_suggestions = ""
    if "final_grade" not in st.session_state:
        st.session_state.final_grade = ""
    
    # Step 1: Generate Writing Prompt
    st.header("Step 1: Your Writing Prompt")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.session_state.prompt:
            st.info(st.session_state.prompt)
        else:
            st.write("Click the button to generate your writing prompt!")
    
    with col2:
        if st.button("Generate New Prompt", type="primary"):
            with st.spinner("Generating prompt..."):
                st.session_state.prompt = generate_writing_prompt()
                st.rerun()
    
    if not st.session_state.prompt:
        st.stop()
    
    # Step 2: Essay Input
    st.header("Step 2: Write Your Essay")
    
    with st.form("essay_form"):
        title = st.text_input("Essay Title:", placeholder="Enter a creative title for your essay")
        
        thesis = st.text_area(
            "Thesis Statement:", 
            placeholder="Write your main argument or the main point of your essay in 1-2 sentences",
            height=100
        )
        
        essay = st.text_area(
            "Your Essay:", 
            placeholder="Write your complete essay here. Remember to include an introduction, body paragraphs, and a conclusion.",
            height=400
        )
        
        col1, col2 = st.columns(2)
        with col1:
            get_suggestions = st.form_submit_button("Get Revision Suggestions", type="secondary")
        with col2:
            submit_final = st.form_submit_button("Submit for Final Grade", type="primary")
    
    # Step 3: Revision Suggestions
    if get_suggestions and title and thesis and essay:
        st.header("Step 3: Revision Suggestions")
        with st.spinner("Analyzing your essay..."):
            st.session_state.revision_suggestions = get_revision_suggestions(title, thesis, essay)
        
        if st.session_state.revision_suggestions:
            st.success("Here are some suggestions to improve your essay:")
            st.write(st.session_state.revision_suggestions)
            st.info("💡 **Tip:** You can revise your essay above and click 'Get Revision Suggestions' again, or submit for your final grade when you're ready!")
    
    # Step 4: Final Grade
    if submit_final and title and thesis and essay:
        st.header("Step 4: Final Grade and Comments")
        with st.spinner("Grading your essay..."):
            grade_response = grade_essay(title, thesis, essay)
            st.session_state.final_grade = grade_response
        
        if st.session_state.final_grade:
            letter_grade, percentage, comments = parse_grade_response(st.session_state.final_grade)
            
            # Display grade in a nice format
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Letter Grade", letter_grade)
            with col2:
                if percentage:
                    st.metric("Percentage", f"{percentage}%")
            
            st.subheader("Teacher Comments:")
            st.write(comments)
            
            # Congratulations message
            if percentage and percentage >= 90:
                st.balloons()
                st.success("🎉 Excellent work! You've demonstrated strong writing skills!")
            elif percentage and percentage >= 80:
                st.success("👏 Great job! Your writing shows good understanding and effort!")
            elif percentage and percentage >= 70:
                st.info("👍 Good work! Keep practicing to improve your writing skills!")
            else:
                st.warning("Keep working hard! Every writer improves with practice!")
    
    # Validation messages
    if (get_suggestions or submit_final) and not all([title, thesis, essay]):
        st.error("Please fill in all fields (title, thesis, and essay) before proceeding.")
    
    # Footer
    st.markdown("---")
    st.markdown("*Remember: Good writing takes time and practice. Don't be afraid to revise and improve your work!*")

if __name__ == "__main__":
    main()
