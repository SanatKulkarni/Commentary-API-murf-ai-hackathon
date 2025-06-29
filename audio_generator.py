import json
import os
from dotenv import load_dotenv
import time
import requests
from murf import Murf

# Load environment variables
load_dotenv()

# Get API key
MURF_API_KEY = os.getenv("MURF_API_KEY")
if not MURF_API_KEY:
    print("❌ Error: MURF_API_KEY not found in environment variables")
    print("Please create a .env file with your Murf API key: MURF_API_KEY=your_key_here")
    exit(1)

# Initialize Murf client
client = Murf(api_key=MURF_API_KEY)

def generate_commentary_audio(json_file_path="commentary_output.json", output_dir="audio_output"):
    """
    Takes a JSON file with commentary and generates TTS audio files
    Saves them in the output directory with numbered filenames
    
    Parameters:
    - json_file_path: Path to the JSON file with commentary
    - output_dir: Directory where audio files will be saved
    """
    print(f"🎬 Generating audio files from commentary")
    print(f"JSON file: {json_file_path}")
    print(f"Output directory: {output_dir}")
    print("=" * 40)
    
    # Create output directory if needed
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Voice configurations
    funny_voice_config = {
        "voice_id": "en-US-ken",
        "style": "Clown",
        "pitch": 9,
        "rate": 50
    }
    
    informative_voice_config = {
        "voice_id": "bn-IN-abhik", 
        "style": "Conversational",
        "pitch": 0,
        "rate": 10,
        "multi_native_locale": "en-IN"
    }
    
    try:
        # Load the JSON file
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        # Parse the JSON structure (supports different formats)
        if 'data' in data:
            commentary_data = data['data']
        else:
            commentary_data = data
        
        title = commentary_data.get('title', 'Video Commentary')
        conversation = commentary_data.get('conversation', [])
        
        if not conversation:
            print("❌ Error: No conversation data found in the JSON file")
            return
        
        print(f"✅ Loaded commentary: \"{title}\"")
        print(f"Found {len(conversation)} conversation exchanges")
        print("=" * 40)
        
        # Generate audio for each conversation line
        for i, exchange in enumerate(conversation):
            comment_type = exchange.get('type')
            text = exchange.get('text')
            
            if not comment_type or not text:
                print(f"⚠️ Skipping item {i+1}: Missing type or text")
                continue
                
            # Select voice based on comment type
            voice_config = funny_voice_config if comment_type == 'funny' else informative_voice_config
            
            # Create filename with numbering for proper ordering
            audio_filename = f"{i+1:02d}_{comment_type}.mp3"
            audio_path = os.path.join(output_dir, audio_filename)
            
            print(f"Generating audio {i+1}/{len(conversation)}: {comment_type}")
            
            try:
                # Generate TTS audio
                response = client.text_to_speech.generate(
                    text=text,
                    **voice_config
                )
                
                # Handle the response (different Murf API versions return different formats)
                if hasattr(response, 'audio_url') and response.audio_url:
                    # If the API returns a URL, download the file
                    print(f"Downloading from URL: {response.audio_url}")
                    audio_data = requests.get(response.audio_url).content
                    with open(audio_path, 'wb') as f:
                        f.write(audio_data)
                    print(f"✅ Saved: {audio_filename}")
                    
                elif hasattr(response, 'audio_file'):
                    # If the API returns audio data or URL string
                    if isinstance(response.audio_file, bytes):
                        # Direct binary data
                        with open(audio_path, 'wb') as f:
                            f.write(response.audio_file)
                        print(f"✅ Saved: {audio_filename}")
                    elif isinstance(response.audio_file, str) and response.audio_file.startswith('http'):
                        # URL string
                        print(f"Downloading from URL: {response.audio_file}")
                        audio_data = requests.get(response.audio_file).content
                        with open(audio_path, 'wb') as f:
                            f.write(audio_data)
                        print(f"✅ Saved: {audio_filename}")
                    else:
                        print(f"⚠️ Unrecognized response format: {type(response.audio_file)}")
                else:
                    print(f"⚠️ No audio data in response")
                    
                # Small pause to prevent API rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error generating audio for line {i+1}: {str(e)}")
        
        print("\n✅ Audio generation complete!")
        print(f"Created {len(conversation)} audio files in: {output_dir}")
        
    except FileNotFoundError:
        print(f"❌ Error: File not found: {json_file_path}")
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in file: {json_file_path}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    # Use default values or command line arguments if provided
    import sys
    
    json_file = "commentary_output.json"
    output_dir = "audio_output"
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
        
    generate_commentary_audio(json_file, output_dir)
