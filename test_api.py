import requests
import json
import os

def test_video_commentary():
    """Test the video commentary API with the demo video"""
    
    # API endpoint
    url = "http://localhost:5000/summarize"
    
    # Path to your video file
    video_path = "./qr-tweet-marketer-demo-sanat.mp4"
    
    # Check if video file exists
    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' not found in current directory")
        return
    
    print(f"Testing API with video: {video_path}")
    print("Uploading video and generating commentary...")
    
    try:
        # Open and send the video file
        with open(video_path, 'rb') as video_file:
            files = {'video': video_file}
            response = requests.post(url, files=files, timeout=300)  # 5 min timeout
        
        # Check response status
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print("\n✅ SUCCESS! Commentary generated:")
                print("=" * 50)
                
                data = result['data']
                print(f"Title: {data['title']}")
                print("\nConversation:")
                print("-" * 30)
                
                for i, exchange in enumerate(data['conversation'], 1):
                    speaker_emoji = "😄" if exchange['type'] == 'funny' else "🧠"
                    print(f"{i}. [{exchange['type'].upper()}] {speaker_emoji}")
                    print(f"   {exchange['text']}")
                    print()
                
                # Save to file for later use
                with open('commentary_output.json', 'w') as f:
                    json.dump(result, f, indent=2)
                print("💾 Full response saved to 'commentary_output.json'")
                
            else:
                print("\n❌ API returned error:")
                print(f"Error: {result.get('error', 'Unknown error')}")
                if 'raw_response' in result:
                    print(f"Raw response: {result['raw_response'][:500]}...")
        
        else:
            print(f"\n❌ HTTP Error {response.status_code}")
            print(f"Response: {response.text}")
    
    except requests.exceptions.Timeout:
        print("\n⏰ Request timed out. Video processing might take longer than expected.")
    except requests.exceptions.ConnectionError:
        print("\n🔌 Connection error. Make sure your Flask server is running on localhost:5000")
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")

def test_simple_summary():
    """This endpoint has been removed"""
    pass

if __name__ == "__main__":
    print("🎬 Video Commentary API Tester")
    print("=" * 40)
    
    # Test commentary endpoint only
    test_video_commentary()
    
    print("\n🏁 Testing completed!")
