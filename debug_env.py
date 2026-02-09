from decouple import config
import os

print("--- DEBUG ENTORNOS ---")
print(f"CWD: {os.getcwd()}")
print(f"Buscando .env en: {os.path.abspath('.env')}")

gsb_key = config('GOOGLE_SAFE_BROWSING_API_KEY', default='NO ENCONTRADA')
gemini_key = config('GEMINI_API_KEY', default='NO ENCONTRADA')

print(f"GOOGLE_SAFE_BROWSING_API_KEY: {gsb_key[:5]}...{gsb_key[-5:] if len(gsb_key) > 5 else ''}")
print(f"GEMINI_API_KEY: {gemini_key[:5]}...{gemini_key[-5:] if len(gemini_key) > 5 else ''}")

# Intentar leer el archivo directamente
try:
    with open('.env', 'r') as f:
        print("\nContenido real del archivo .env (primeras 5 lineas):")
        for i, line in enumerate(f):
            if i < 5:
                print(line.strip())
except Exception as e:
    print(f"Error leyendo .env directo: {e}")
