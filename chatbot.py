import gradio as gr
from transformers import pipeline
import PyPDF2

# Función para extraer texto de un archivo PDF y estructurarlo
def extract_text_from_pdf(pdf_path):
    text = ''
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                extracted_text = page.extract_text()
                if extracted_text:  # Verificar si hay texto extraído
                    text += extracted_text + "\n"
                else:
                    print(f"Advertencia: No se pudo extraer texto de la página {page_num + 1}")
    except Exception as e:
        raise ValueError(f"Error al leer el archivo PDF: {e}")
    
    if not text:
        raise ValueError("No se pudo extraer texto del PDF.")
    
    return text

# Función para extraer productos del texto estructurado
def extract_products_from_text(context):
    products = {}
    lines = context.split('\n')
    current_product = None
    product_info = ""
    
    for line in lines:
        if "Precio regular" in line or "precio regular" in line:
            if current_product:
                products[current_product] = product_info.strip()
            current_product = line
            product_info = ""
        elif current_product:
            product_info += line + " "
    
    if current_product:
        products[current_product] = product_info.strip()
    
    return products

# Función para buscar información relevante en el diccionario de productos
def find_relevant_info(question, products):
    question_lower = question.lower()
    relevant_info = ""
    
    for product, info in products.items():
        if question_lower in product.lower() or any(keyword in info.lower() for keyword in question_lower.split()):
            relevant_info += product + "\n" + info + "\n"
    
    return relevant_info.strip()

# Cargar y estructurar el texto del PDF
context = extract_text_from_pdf('Bruno_child_offers.pdf')

# Extraer los productos del texto del PDF
products_info = extract_products_from_text(context)

# Cargar el modelo de lenguaje
qa_pipeline = pipeline("question-answering")

# Definir la función del chatbot
def chatbot(question):
    if not question.strip():
        return "Por favor, ingrese una pregunta válida."
    
    relevant_info = find_relevant_info(question, products_info)
    if not relevant_info:
        return "No se encontró información relevante en el PDF."
    
    try:
        result = qa_pipeline(question=question, context=relevant_info)
        return result['answer']
    except Exception as e:
        return f"Error al procesar la pregunta: {e}"

# Crear la interfaz de Gradio
iface = gr.Interface(fn=chatbot, inputs="text", outputs="text")
iface.launch(share=True)
