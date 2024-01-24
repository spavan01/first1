import streamlit as st
import os
from annotated_text import annotated_text
from streamlit_player import st_player
from pytube import YouTube
import subprocess
from main import get_transcript, translate_summary, summarize_transcript, text_to_speech, audio_to_text

# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'summary' not in st.session_state:
    st.session_state.summary = ""
if 'expander_state' not in st.session_state:
    st.session_state.expander_state = False
if 'textty' not in st.session_state:
    st.session_state.textty = ""
if 'summed' not in st.session_state:
    st.session_state.summed = ""
if 'translated' not in st.session_state:
    st.session_state.translated = ""
if 'audi' not in st.session_state:
    st.session_state.audi = ""
if 'to_continue' not in st.session_state:
    st.session_state.to_continue=True
if 'to_run' not in st.session_state:
    st.session_state.to_run=True    
if 'title' not in st.session_state:
    st.session_state.title=""
    
def main():
    st.markdown(
        """
        <style>
            @keyframes title-animation {
                0% {
                    opacity: 0;
                    transform: translateY(-50%);
                }
                100% {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .title-container {
                display: inline-block;
                animation: title-animation 1s ease-in-out forwards;
                cursor: pointer;
            }

            .title-text {
                color: #FFFFFF;
                font-size: 36px;
                font-weight: bold;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            }

            .title-text:hover {
                text-decoration: underline;
            }
            
            .expander-content {
                background-color: #0059b3;
                color: #FFFFFF;
                padding: 10px;
                border-radius: 5px;
            }
        </style>

        <div class="title-container">
            <h1 class="title-text">Video Transcript Summarizer</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
    """
    <style>
        @keyframes title-anim {
            0% {
                transform: scale(1);
            }
            50% {
                transform: scale(1.1);
            }
            100% {
                transform: scale(1);
            }
        }

        .title-text {
            animation: title-anim 3s infinite;
            font-size: 40px;
            font-weight: bold;
            color: #FF060C;
            cursor: pointer;
        }

        
    </style>

 
    """,
    unsafe_allow_html=True
)   
    
    def highlight_common_text(summary1, summary2):
        common_text = set(summary1.split()) & set(summary2.split())
        return common_text
    st.markdown("<br>", unsafe_allow_html=True)
    option = st.radio("Choose your input format:", ["Enter a Link", "Upload an Audio File","Download video"])
    error_dict=["An error during transcription.","An error during translation.","An error occured during fetching video data.","An error transcribing audio file.","An error occured during generating audible summary.","An error occured during summarization.","Video not found, enter a valid youtube video link.","An error occured during transcription.",'An Error occurred with given link.',"Only english language is supported for transcription."]
    st.markdown("<br>", unsafe_allow_html=True)
    if option == "Enter a Link":
        message_placeholder = st.empty()
        message_placeholder.info('Please make sure to enter full url of video and not youtu.be form', icon="ℹ️")
        video_link = st.text_input("Enter the YouTube video link", key="video_link")
        if video_link:
            try:
                yt=YouTube(video_link)
                st.session_state.title=yt.title
            except:
                st.warning("Please enter a valid link!")  
                video_link=""  
        if video_link:
            st_player(video_link)
            message_placeholder.empty()
        if st.button("Get Transcript") and video_link:
            with st.spinner("Generating transcript..."):
                message_placeholder = st.empty()
                message_placeholder.info('Might take a while if no transcript is available', icon="ℹ️")
                transcript = get_transcript(video_link)
                message_placeholder.empty()
                
            st.session_state.transcript = transcript
            st.session_state.summary = ""
            st.session_state.expander_state = True

    elif option == "Upload an Audio File" and st.session_state.to_run:
        uploaded_file = st.file_uploader("Upload an audio file, Format: mp3", key="uploaded_file")
        if uploaded_file is not None:
            with open(os.path.join(os.getcwd(), 'audio_file0.mp3'), 'wb') as f:
                f.write(uploaded_file.getbuffer())
            st.success("File uploaded successfully!")
            with st.spinner("Processing audio file..."):
                transcript = audio_to_text("", True)
                st.session_state.to_run=False
            st.session_state.transcript = transcript
            st.session_state.summary = ""
            st.session_state.expander_state = True
    elif option == "Download video":
        st.title("YouTube Video Downloader")
        video_link,start_time,end_time="","",""
        video_link = st.text_input("Enter YouTube video URL:")
        if video_link:
            try:
                yt=YouTube(video_link)
                st.session_state.title=yt.title
                
            except:
                st.warning("Please enter a valid link!")  
                video_link=""
            if st.session_state.title:
                choice = st.radio("Choose operation:", ["Full video", "Video clip"])
                if choice == "Full video":
                    
                    def download_video(video_link):
                        yt=YouTube(video_link)
                        try:
                            stream = yt.streams.get_highest_resolution()
                            stream.download("",f"{st.session_state.title}.mp4")
                        except:
                            current_dir = os.path.dirname(os.path.realpath(__file__))
                            output_file = os.path.join(current_dir, f"{st.session_state.title}.mp4")
                            # command = f'yt-dlp {video_link}'
                            command = f'yt-dlp -o "{output_file}" -f "(bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best)" "{video_link}"'
                            subprocess.run(command, shell=True)


                        
                    with st.spinner("Please wait while file is being downloaded"):
                        download_video(video_link)
                    st.download_button(label="Download video",data=open(f"{st.session_state.title}.mp4",'rb'),file_name=f"Full-{st.session_state.title}.mp4")
                    
                elif choice =="Video clip":
                    s = "HH:MM:SS"
                    st.write(f"<p>Time format: {s}</p>", unsafe_allow_html=True)
                    start_time = st.text_input("Enter Start time...")
                    end_time = st.text_input("Enter end time...")
                    def download_video(video_link, start_time, end_time):
            # Get the current directory where the Streamlit app is located
                        current_dir = os.path.dirname(os.path.realpath(__file__))

                        # Specify the output file path for the downloaded video
                        output_file = os.path.join(current_dir, f"clipped-{st.session_state.title}.mp4")

                        command = f'yt-dlp -o "{output_file}" -f "(bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best)" --external-downloader ffmpeg --external-downloader-args "ffmpeg_i:-ss {start_time} -to {end_time}" "{video_link}"'
                        subprocess.run(command, shell=True)
                    if st.button("generate clip"):              
                        if start_time and end_time :
                            with st.spinner("please wait while clip is being generated..."):
                                download_video(video_link, start_time, end_time)
                            st.download_button(label="Download clip",data=open(f"clipped-{st.session_state.title}.mp4",'rb'),file_name=f"Clip-{st.session_state.title}.mp4")
                        else:
                            st.error("Please fill in all the required fields.")    
   

    if st.session_state.transcript:
        
        with st.expander("Transcript", expanded=st.session_state.expander_state):
            st.markdown('<div class="expander-content">{}</div>'.format(st.session_state.transcript), unsafe_allow_html=True)          
            for i in error_dict:
                if str(st.session_state.transcript)==str(i):
                    st.session_state.to_continue=False
                    st.session_state.transcript="" 
                else:
                    st.session_state.to_continue=True
                    

    if st.session_state.transcript or st.session_state.summed:    
        st.download_button("Download",st.session_state.transcript,key="download_transcript_button",file_name=f"Transcript-{st.session_state.title}.txt")    
        sumhead = """
            <style>
                .header-container {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 10px;
                }
                
                .header {
                    animation: gradient 1.8s linear infinite;
                    background: linear-gradient(to right, #FF4081, #FFC107, #3F51B5, #4CAF50);
                    background-size: 200% auto;
                    color: #FFFFFF;
                    padding: 5px;
                    border-radius: 5px;
                    font-size: 24px;
                    text-align: center;
                }
                
                .header:hover {
                    background-position: right center;
                }
                
                @keyframes gradient {
                    0% { background-position: 0% 50%; }
                    25% { background-position: 100% 50%; }
                    50% { background-position: 100% 50%; }
                    75% { background-position: 0% 50%; }
                    100% { background-position: 0% 50%; }
                }
            </style>
        """
        
        st.markdown(sumhead, unsafe_allow_html=True)
        
        # Header container
        st.markdown("<div class='header-container'>", unsafe_allow_html=True)
        st.markdown("<h1 class='header'>Summarization</h1>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        message_placeholder = st.empty()
        message_placeholder.info("Availiable models 1: Google T5, 2: DistilBart", icon="ℹ️")
        st.markdown("<br>", unsafe_allow_html=True)
        model_choice = st.selectbox("Select a model to perform summarization", [1, 2 ], key="model_choice")

        if st.button("Summarize"):
            message_placeholder.empty()
            if st.session_state.to_continue:
                
                transcript = st.session_state.transcript
                with st.spinner("Summarizing transcript..."):
                    summary = summarize_transcript(transcript, model_choice)
                st.session_state.summary = summary
                st.session_state.expander_state = False
                st.session_state.summed = st.session_state.summary

    # Display Summarized Text
    if st.session_state.summary:
        if st.session_state.to_continue:
            with st.expander("Summarized Text", expanded=True):
                st.markdown('<div class="expander-content">{}</div>'.format(st.session_state.summary), unsafe_allow_html=True)
            st.session_state.textty = st.session_state.summary
            st.download_button("Download summary",st.session_state.summary,key="download_summary_button",file_name=f"Summary-{st.session_state.title}.txt") 
        elif st.session_state.summed:
            with st.expander("Summarized Text", expanded=True):
                st.markdown('<div class="expander-content">{}</div>'.format(st.session_state.summed), unsafe_allow_html=True)
            st.download_button("Download summary",st.session_state.summary,key="download_summary_button",file_name=f"Summary-{st.session_state.title}.txt")
        summary1 = st.session_state.summary
        summary2 = st.session_state.transcript

        # Highlight common text
        common_text = highlight_common_text(summary1, summary2)

        # Generate highlighted summaries
        highlighted_summary1 = " ".join(
            ['<span class="highlight">{}</span>'.format(word) if word in common_text else word for word in
             summary1.split()])
        highlighted_summary2 = " ".join(
            ['<span class="highlight">{}</span>'.format(word) if word in common_text else word for word in
             summary2.split()])

        # Define CSS styles for the highlights and container
        highlight_style = """
            <style>
                .highlight {
                    background-color: #000000;
                    color: #FFFFFF;
                    padding: 2px 5px;
                    border-radius: 3px;
                }
                
                .summary-container {
                    display: flex;
                    flex-direction: row;
                    background-color: #000000;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 10px;
                }
                
                .summary-column {
                    flex: 1;
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    background-color: #ffbe6d;
                    color: #000000;
                    margin-right: 10px;
                    min-width: 400px;
                    font-size: 16px;
                }
                
                .expander-view {
                    background-color: #0059b3;
                    border-radius: 5px;
                    padding: 10px;
                }
                
                .expander-content {
                    margin-top: 10px;
                }
            </style>
        """

        # Display the highlighted summaries side by side
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(sumhead, unsafe_allow_html=True)
        
        # Header container
        st.markdown("<div class='header-container'>", unsafe_allow_html=True)
        st.markdown("<h1 class='header'>View Comparison</h1>", unsafe_allow_html=True)
        st.info("The highlighted text represents the words that overlap.", icon="ℹ️")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(highlight_style, unsafe_allow_html=True)
        with st.container():
            st.markdown(
                """
                <div class="expander-view">
                    <details class="expander-content">
                        <summary class="expander-summary">Summary</summary>
                        <p>{}</p>
                    </details>
                    <details class="expander-content">
                        <summary class="expander-summary">Transcript</summary>
                        <p>{}</p>
                    </details>
                </div>
                """.format(highlighted_summary1, highlighted_summary2),
                unsafe_allow_html=True
            )
    # Page 3: Translation and Text to Speech
    if st.session_state.textty:

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='header-container'>", unsafe_allow_html=True)
        st.markdown("<h1 class='header'>Translation</h1>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.session_state.summary = st.session_state.textty

        # Translation
        lang_choice_translate = st.selectbox("Select Language for Translation", ["English", "French", "German"],
                                             key="lang_choice_translate")

        if st.button("Translate") or st.session_state.translated:
            ty = st.session_state.textty
            with st.spinner("Translating summary..."):
                translated_text = translate_summary(ty, lang_choice_translate)
            with st.expander("Translated Summary", expanded=True):
                st.session_state.translated = translated_text
                st.markdown('<div class="expander-content">{}</div>'.format(st.session_state.translated), unsafe_allow_html=True)
            st.download_button("Download",st.session_state.translated,key="download_translated_button",file_name=f"Translated-{st.session_state.title}.txt")    

        # Text to Speech
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='header-container'>", unsafe_allow_html=True)
        st.markdown("<h1 class='header'>Audible Summary</h1>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        lang_choice_tts = st.selectbox("Select Language for audible summary", ["English", "French", "German"],
                                       key="lang_choice_tts")

        if st.button("Generate Audio") or st.session_state.audi:
            summary = st.session_state.summary
            with st.spinner("Generating audio file..."):
                audio_file = text_to_speech(summary, lang_choice_tts)
                
            st.session_state.audi = audio_file
            filename='savedaudiofile.mp3'
            st.audio(filename)
            st.download_button(label="Download audio",data=open(filename,'rb'),file_name=f"Audible summary-{st.session_state.title}.mp3")

            
if __name__ == '__main__':
    main()
