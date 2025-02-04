from PIL import Image, ImageEnhance
import pytesseract
import re
from app.services.ai_service import analyze_with_groq
from io import BytesIO

def preprocess_image(image):
    image = image.convert("L")
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    return image

def clean_and_parse_ingredients(raw_text):
    text = raw_text.replace("“", '"').replace("”", '"')
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'(\d+)%', r'\1%', text)
    text = re.sub(r'\(([^)]+)\)', r'( \1 )', text)
    ingredients = re.split(r'[,\n]+', text)
    return [ingredient.strip() for ingredient in ingredients if ingredient.strip()]

async def extract_ingredients_from_image(file):
    content = await file.read()
    image = Image.open(BytesIO(content))
    image = preprocess_image(image)
    ingredients_text = pytesseract.image_to_string(image)
    ingredients_list = clean_and_parse_ingredients(ingredients_text)
    prompt = f"write all ingredients in correct spelling and provide ingredients sperated with ',' and Do Not Provide anything else. ingredients_list : {ingredients_list}"
    result = analyze_with_groq(prompt)
    print(result)
    return [v.strip() for v in result.split(',')]