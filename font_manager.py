import os
import requests
import zipfile
import io

# Curated list of high-quality Google Fonts
GOOGLE_FONTS = {
    "Handwriting": {
        "Pacifico": "https://fonts.google.com/download?family=Pacifico",
        "Dancing Script": "https://fonts.google.com/download?family=Dancing%20Script",
        "Caveat": "https://fonts.google.com/download?family=Caveat",
        "Satisfy": "https://fonts.google.com/download?family=Satisfy",
        "Permanent Marker": "https://fonts.google.com/download?family=Permanent%20Marker"
    },
    "Sans-Serif": {
        "Roboto": "https://fonts.google.com/download?family=Roboto",
        "Open Sans": "https://fonts.google.com/download?family=Open%20Sans",
        "Montserrat": "https://fonts.google.com/download?family=Montserrat",
        "Lato": "https://fonts.google.com/download?family=Lato"
    },
    "Serif": {
        "Merriweather": "https://fonts.google.com/download?family=Merriweather",
        "Playfair Display": "https://fonts.google.com/download?family=Playfair%20Display",
        "Lora": "https://fonts.google.com/download?family=Lora"
    },
    "Display": {
        "Bebas Neue": "https://fonts.google.com/download?family=Bebas%20Neue",
        "Abril Fatface": "https://fonts.google.com/download?family=Abril%20Fatface",
        "Righteous": "https://fonts.google.com/download?family=Righteous"
    }
}

FONT_DIR = "./fonts"

def get_font_path(category, font_name):
    """
    Downloads the font if not present and returns the path to the .ttf/.otf file.
    Uses Google Fonts CSS API to find the real TTF URL.
    """
    if not os.path.exists(FONT_DIR):
        os.makedirs(FONT_DIR)
        
    normalized_name = font_name.replace(" ", "")
    
    # Check existing files first
    for f in os.listdir(FONT_DIR):
        if normalized_name.lower() in f.lower() and f.endswith((".ttf", ".otf")):
            return os.path.join(FONT_DIR, f)
            
    # New strategy: Parse CSS
    print(f"Downloading {font_name}...")
    
    try:
        # 1. Get CSS
        css_url = f"https://fonts.googleapis.com/css2?family={font_name.replace(' ', '+')}"
        # No specific User-Agent gets us TTF usually, or use a generic one.
        # Wget/Curl/Python-Requests usually get TTF.
        r = requests.get(css_url)
        r.raise_for_status()
        
        # 2. Extract TTF URL
        # Look for 'src: url(https://...)'
        content = r.text
        import re
        # Find all woff2/ttf urls
        urls = re.findall(r'url\((https?://[^)]+)\)', content)
        
        if not urls:
            print("No font URLs found in CSS.")
            return None
            
        font_url = urls[0] # Take the first one
        
        # 3. Download the font file
        r_font = requests.get(font_url)
        r_font.raise_for_status()
        
        # Save it
        # Note: Google fonts usually serve WOFF2 to browsers.
        # Pillow supports WOFF2/OTF/TTF depending on libfreetype version.
        # Let's save as .ttf or .woff2
        ext = ".ttf" if "ttf" in font_url else ".woff2"
        # Force .ttf extension for compatibility if simpler, but woff2 is standard now.
        # Check if Pillow on this system supports woff2. It usually does for recent versions.
        
        filename = f"{normalized_name}{ext}"
        save_path = os.path.join(FONT_DIR, filename)
        
        with open(save_path, "wb") as f:
            f.write(r_font.content)
            
        print(f"Saved to {save_path}")
        return save_path

    except Exception as e:
        print(f"Failed to download font: {e}")
        return None
        
    return None
