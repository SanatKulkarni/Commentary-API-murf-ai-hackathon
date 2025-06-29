from flask import Flask, request, jsonify
from google import genai
from dotenv import load_dotenv
import os
import time 
import tempfile
import json

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

app = Flask(__name__)

@app.route('/summarize',methods=['POST'])
def summarize_video():
    if 'video' not in request.files:
        return jsonify({'error':'No video file given to process'})

    video = request.files['video']
    with tempfile.NamedTemporaryFile(delete=False,suffix='.mp4') as tmp:
        video.save(tmp.name)
        tmp_path = tmp.name

    try:
        myfile = client.files.upload(file=tmp_path)
        file_id=myfile.name
        status = myfile.state
        while status!="ACTIVE":
            time.sleep(2)
            myfile= client.files.get(name=file_id)
            status = myfile.state        # Create a simple conversational commentary prompt
        commentary_prompt = """
        Analyze this video and create a natural conversation between two commentators for text-to-speech. 

        One commentator is funny and entertaining, the other is informative and supportive.

        IMPORTANT: Return ONLY a raw JSON object (no markdown formatting, no ```json blocks).

        Use this exact structure:
        {
            "title": "Brief video title",
            "conversation": [
                {"type": "funny", "text": "entertaining comment"},
                {"type": "informative", "text": "educational response"},
                {"type": "funny", "text": "witty follow-up"},
                {"type": "informative", "text": "helpful insight"}
            ]
        }

        Make the conversation flow naturally. Keep each comment 1-2 sentences and TTS-friendly. Create 6-10 exchanges.
        Return only the JSON object, nothing else.
        """

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[myfile, commentary_prompt]
        )        # Parse the response to ensure it's valid JSON
        try:
            # Clean the response text - remove markdown code blocks if present
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]  # Remove ```json
            if response_text.endswith('```'):
                response_text = response_text[:-3]  # Remove ```
            response_text = response_text.strip()
            
            commentary_data = json.loads(response_text)
            return jsonify({
                'success': True,
                'data': commentary_data            })
        except json.JSONDecodeError as e:
            # Fallback if JSON parsing fails
            return jsonify({
                'success': False,
                'raw_response': response.text,
                'error': f'Generated response was not valid JSON: {str(e)}'
            })
    
    finally:
        os.remove(tmp_path)

if __name__=='__main__':
    app.run(debug=True)