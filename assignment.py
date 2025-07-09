import streamlit as st
from openai import OpenAI
import json
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

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

def send_email(prompt, title, thesis, essay, letter_grade, percentage, comments):
    """Send email notification after grade is issued"""
    try:
        # Check if email configuration exists
        required_keys = ["SMTP_SERVER", "SMTP_PORT", "SENDER_EMAIL", "SENDER_PASSWORD"]
        missing_keys = [key for key in required_keys if key not in st.secrets]
        
        if missing_keys:
            st.error(f"Missing email configuration: {', '.join(missing_keys)}")
            st.info("Please add the following to your .streamlit/secrets.toml file:")
            st.code("""
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-password"
            """)
            return False
        
        # Email configuration
        smtp_server = st.secrets["SMTP_SERVER"]
        smtp_port = int(st.secrets["SMTP_PORT"])
        sender_email = st.secrets["SENDER_EMAIL"]
        sender_password = st.secrets["SENDER_PASSWORD"]
        
        # Recipients
        recipients = [
            "kgun1329@gmail.com",
            "rxu187@gmail.com", 
            "wuxiaopei84@gmail.com",
            "jxu14s@k12.jh.edu",
        ]

def generate_writing_prompt(client):
    """Generate a writing prompt appropriate for 6th graders"""
    
    import random
    
    # Weighted prompt categories based on specified percentages
    prompt_categories = [
        "creative",  # 20%
        "creative", 
        "expository",  # 30%
        "expository",
        "expository",
        "persuasive",  # 20%
        "persuasive",
        "personal_narrative",  # 30%
        "personal_narrative",
        "personal_narrative"
    ]
    
    category = random.choice(prompt_categories)
    
    if category == "creative":
        prompt = """
        Generate a creative writing prompt for 6th grade students. The prompt should:
        - Involve imaginative scenarios (fantasy, sci-fi, adventure, mystery)
        - Encourage creative storytelling and world-building
        - Be age-appropriate and engaging
        - Include specific instructions about creating a fictional narrative
        
        Examples: writing from an object's perspective, creating a new world, magical realism, etc.
        Provide just the prompt text, nothing else.
        """
    
    elif category == "expository":
        prompt = """
        Generate an expository writing prompt for 6th grade students that includes a passage or famous line from literature. The prompt should:
        - Include a short quote or passage from a well-known book appropriate for middle school
        - Ask students to analyze, explain, or expand on the quote/passage
        - Focus on informational or explanatory writing
        - Be clear about the analytical task
        
        Structure: [Quote/Passage] followed by instructions to analyze, explain, or inform about the topic.
        Provide just the prompt text, nothing else.
        """
    
    elif category == "persuasive":
        prompt = """
        Generate a persuasive writing prompt for 6th grade students. The prompt should:
        - Present a debatable topic relevant to 6th graders
        - Ask students to take a position and argue for it
        - Include instructions about using evidence and reasoning
        - Be age-appropriate (school, community, or age-relevant issues)
        
        Examples: school policies, environmental issues, technology use, etc.
        Provide just the prompt text, nothing else.
        """
    
    else:  # personal_narrative
        prompt = """
        Generate a personal narrative writing prompt for 6th grade students. The prompt should:
        - Ask students to write about their own experiences or memories
        - Focus on storytelling from their own life
        - Encourage reflection and personal growth
        - Be relatable to 6th grade experiences
        - Include instructions about narrative structure
        
        Examples: overcoming challenges, learning moments, relationships, growth experiences, etc.
        Provide just the prompt text, nothing else.
        """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=1.0  # Higher temperature for more variety
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating prompt: {str(e)}")
        return None

def grade_essay(client, title, thesis, essay):
    """Grade the essay and provide final comments with strict standards"""
    
    # Count words for initial assessment
    word_count = len(essay.split())
    
    prompt = f"""
    You are a 6th grade teacher grading a student's essay. Analyze this essay carefully and give a realistic grade based on actual quality. DO NOT default to the same grade every time.

    Essay Title: {title}
    Thesis Statement: {thesis}
    Essay: {essay}
    Word Count: {word_count}

    GRADING SCALE:
    93-100: A (Exceptional work - clear thesis, excellent organization, strong ideas, good mechanics)
    90-92: A- (Very good work with minor issues)
    87-89: B+ (Good work with some problems)
    83-86: B (Satisfactory work, meets requirements)
    80-82: B- (Adequate work with notable issues)
    77-79: C+ (Below average, some effort shown)
    73-76: C (Poor work, minimal effort)
    70-72: C- (Very poor work)
    67-69: D+ (Barely passing, major problems)
    63-66: D (Failing quality but some attempt made)
    60-62: D- (Very poor attempt)
    0-59: F (No effort, nonsensical, or extremely short)

    SPECIFIC GRADING CRITERIA:
    
    AUTOMATIC F (0-59%) - Give this if ANY of these apply:
    - Less than 30 words total
    - Random letters or gibberish
    - Completely off-topic
    - No clear sentences

    D RANGE (60-69%) - Give this if:
    - Very short (30-75 words)
    - No clear thesis or main idea
    - Extremely poor organization
    - Many grammar/spelling errors

    C RANGE (70-79%) - Give this if:
    - Short but coherent (75-150 words)
    - Weak thesis or unclear main idea
    - Some organization but poor transitions
    - Multiple errors but readable

    B RANGE (80-89%) - Give this if:
    - Good length (150-250 words)
    - Clear thesis and main ideas
    - Generally well organized
    - Some minor errors

    A RANGE (90-100%) - Give this if:
    - Excellent length and depth (250+ words)
    - Strong, clear thesis
    - Excellent organization and flow
    - Creative ideas and strong voice
    - Few or no errors

    IMPORTANT: Look at the ACTUAL QUALITY of this specific essay. Don't give the same grade to every essay. If it's truly excellent, give an A. If it's truly poor, give a D or F. Be honest about what you're reading.

    Provide your response in this exact format:
    GRADE: [Letter grade A-F]
    PERCENTAGE: [Number from 0-100]
    COMMENTS: [2-3 paragraphs of specific feedback explaining the grade. Be honest about the quality.]
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7  # Higher temperature for more varied grading
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error grading essay: {str(e)}")
        return None

def get_revision_suggestions(client, title, thesis, essay):
    """Get revision suggestions for the student's essay"""
    prompt = f"""
    You are a helpful 6th grade teacher reviewing a student's essay. Please provide constructive feedback and suggestions for improvement. Be encouraging and supportive while offering specific, actionable advice. You must give Fs or 0s for lacking work.
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
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error getting revision suggestions: {str(e)}")
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
    client = initialize_openai()
    if not client:
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
                st.session_state.prompt = generate_writing_prompt(client)  # Pass client here
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
            st.session_state.revision_suggestions = get_revision_suggestions(client, title, thesis, essay)  # Pass client here
        
        if st.session_state.revision_suggestions:
            st.success("Here are some suggestions to improve your essay:")
            st.write(st.session_state.revision_suggestions)
            st.info("💡 **Tip:** You can revise your essay above and click 'Get Revision Suggestions' again, or submit for your final grade when you're ready!")
    
    # Step 4: Final Grade
    if submit_final and title and thesis and essay:
        st.header("Step 4: Final Grade and Comments")
        with st.spinner("Grading your essay..."):
            grade_response = grade_essay(client, title, thesis, essay)  # Pass client here
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
            
            # Send email notification
            with st.spinner("Sending email notification..."):
                email_sent = send_email(
                    st.session_state.prompt,
                    title,
                    thesis,
                    essay,
                    letter_grade,
                    percentage,
                    comments
                )
                
                if email_sent:
                    st.success("📧 Email notification sent successfully!")
                else:
                    st.warning("⚠️ Grade recorded but email notification failed.")
            
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
