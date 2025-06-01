import requests

def enviar_archivo_wav(file_path):
    url = "http://127.0.0.1:8000/classify/"  # Endpoint a la view
    files = {'audio': open(file_path, 'rb')}

    try:
        response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json() 
    except Exception as e:
        return {"error": str(e)}
