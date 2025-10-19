import os
from dotenv import load_dotenv
from openai import OpenAI
import anthropic

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
claude = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

def generate_image_prompt(topic):
    print(f"Generating image prompt suggestions for topic: '{topic}'...")

    prompt = f"""
List 5 simple, iconic visuals that instantly represent the legal concept of "{topic}".
Each should be a short phrase (1–4 words), like something you'd see on an icon or emoji.
Avoid full scenes or descriptions — just clear, symbolic objects or visuals.
Return only the 5 suggestions, one per line, no numbering, no explanations.
"""

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        temperature=0.5,
    )

    image_prompt_suggestions = response.content[0].text.strip()
    print(f"Image prompt suggestions:\n{image_prompt_suggestions}")
    return image_prompt_suggestions

def generate_article_image_realistic(image_prompt, size="1024x1024", quality="standard"):
    """
    Generate a professional legal article image using DALL-E with custom options
    
    Args:
        image_prompt: The specific image prompt to generate
        size: Image size ("1024x1024", "1792x1024", "1024x1792")
        quality: Image quality ("standard" or "hd")
    
    Returns:
        image_url: URL of generated image or None if failed
    """
    
    print(f"Generiere Bild für Prompt: '{image_prompt}' (Größe: {size}, Qualität: {quality})...")
    
    prompt = f"""
Create a high-definition photograph of {image_prompt} on a plain background, 
focusing on the striking visual contrast and symbolic power of the image. 
Use sharp clarity to highlight the object's key features and details.
Employ strong lighting to emphasize the object as the sole, dominant subject, 
casting bold shadows that accentuate its visual impact.
The composition should be clean and powerful, making the object an arresting focal 
point that instantly conveys the essence in a memorable way.
"""
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            n=1
        )
        
        image_url = response.data[0].url
        print(f"✅ Bild erfolgreich generiert: {image_url}")
        return image_url
        
    except Exception as e:
        print(f"[ERROR] Bild-Generierung fehlgeschlagen: {e}")
        return None

def generate_article_image_iconic(image_prompt, size="1024x1024", quality="standard"):
    """
    Generate an iconic legal article image using DALL-E with custom options
    
    Args:
        image_prompt: The specific image prompt to generate
        size: Image size ("1024x1024", "1792x1024", "1024x1792")
        quality: Image quality ("standard" or "hd")
    
    Returns:
        image_url: URL of generated image or None if failed
    """
    
    print(f"Generiere ikonisches Bild für Prompt: '{image_prompt}' (Größe: {size}, Qualität: {quality})...")
    
    prompt = f"""
A simple, minimalistic symbolically representing the concept of {image_prompt} (Possibly German word). 
Show someone committing the {image_prompt}, without depicting specific individuals or detailed scenes.
Employ a clean, limited color palette with 1-2 accent colors against a plain dark background. 
Prioritize visual clarity, avoiding unnecessary decorative elements and shapes. 
The image should be professional, instantly communicating the key idea.
"""
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            n=1
        )
        
        image_url = response.data[0].url
        print(f"✅ Ikonisches Bild erfolgreich generiert: {image_url}")
        return image_url
        
    except Exception as e:
        print(f"[ERROR] Ikonische Bild-Generierung fehlgeschlagen: {e}")
        return None

# Test the function
if __name__ == "__main__":
    topic = "Raub § 249 StGB"
    
    # Generate main article image
    image_url = generate_article_image_realistic(topic)
    
    if image_url:
        print(f"\nBild-URL: {image_url}")