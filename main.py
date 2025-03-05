from fastapi import FastAPI, File, UploadFile
import shutil
import os
import pdfplumber
import pandas as pd

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_with_pdfplumber(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n" if page.extract_text() else ""
    return text

def process_pdf_and_save_excel(pdf_path):
    extracted_text = extract_text_with_pdfplumber(pdf_path)
    linhas = extracted_text.split("\n")
    dados_extraidos = []
    
    bloco_atual = None
    for linha in linhas:
        if "Bloco" in linha:
            bloco_atual = linha.strip()
        elif linha.strip():
            dados_extraidos.append([bloco_atual, linha.strip()])
    
    df = pd.DataFrame(dados_extraidos, columns=["Bloco", "Assunto"])
    output_path = os.path.join(UPLOAD_FOLDER, "planilha_extraida.xlsx")
    df.to_excel(output_path, index=False)
    
    return output_path

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    planilha_path = process_pdf_and_save_excel(file_location)
    return {"message": "Arquivo processado com sucesso!", "download_url": planilha_path}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
