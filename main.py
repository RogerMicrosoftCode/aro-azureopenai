import os
import openai
import gradio as gr
import logging
import json
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import AIMessage, HumanMessage

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Model Global Variable
model = None

# Grab OpenAI API Base and API Key
openai.api_base = os.getenv("OPENAI_API_BASE", "https://aopeniaroger.openai.azure.com")
openai.api_key = os.getenv("OPENAI_API_KEY")

#log details
openai.log = 'debug'

# Load Config
def load_config():
    config = {
        "title": os.getenv("title", "Azure OpenAI App running in Azure Red Hat OpenShift"),
        "description": os.getenv("description", "Azure OpenAI App running in Azure Red Hat OpenShift"),
        "port": int(os.getenv("port", 8080)),
        "deployment_name": os.getenv("deployment_name", "WorkshopIA"),
        "api_type": os.getenv("api_type", "azure"),
        "api_version": os.getenv("api_version", "2023-05-15"),
        "model_name": os.getenv("model_name", "gpt-35-turbo"),
        "model_version": os.getenv("model_version", "0125")
    }
    logging.info(f"Loaded configuration: {config}")
    return config

# Load the Azure OpenAI Model using LangChain
def load_model(api_type, api_version, deployment_name):
    global model  # Declare that you are using the global model variable
    try:
        # Callbacks support token-wise streaming
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        logging.info(f"Preparing model with deployment name: {deployment_name}, api version: {api_version}")
        logging.info(f"Using API Base: {openai.api_base}")
        
        # Loading model directly using the specified path
        model = AzureChatOpenAI(
            openai_api_base=openai.api_base,
            openai_api_version=api_version,
            deployment_name=deployment_name,  # Asegurarse de que sea "WorkshopIA"
            openai_api_key=openai.api_key,
            openai_api_type=api_type,
            temperature=0.7,
            max_tokens=1000
            # No especificar model_name para evitar conflictos
        )
        logging.info(f"Model loaded successfully with deployment_name: {deployment_name}")
        return model
    except Exception as e:
        logging.error(f"Error loading model: {str(e)}")
        raise

# Create a predict function that takes in a message as input and outputs a prediction.
def predict(message, history):
    global model
    if model is None:
        config = load_config()
        model = load_model(
            config["api_type"], 
            config["api_version"], 
            config["deployment_name"]
        )
    
    history_langchain_format = []
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))
    history_langchain_format.append(HumanMessage(content=message))

    try:
        # Call Azure OpenAI API
        logging.info(f"Sending request to Azure OpenAI with message: {message[:50]}...")
        logging.info(f"Using deployment: {model.deployment_name}")
        azure_response = model(history_langchain_format)
        logging.info("Received response from Azure OpenAI")
        return azure_response.content
    except Exception as e:
        logging.error(f"Error calling Azure OpenAI: {str(e)}")
        return f"Error: {str(e)}"

# Define a run function that sets up an image and label for classification using the gr.Interface.
def run(port, title, description):
    try:
        logging.info(f"Starting Gradio interface on port {port}...")
        chat_interface = gr.ChatInterface(
            fn=predict, 
            theme=gr.themes.Soft(),
            title=title,
            description=description
        )

        chat_interface.launch(
            debug=True, 
            share=False, 
            server_name="0.0.0.0", 
            server_port=port
        )
        logging.info("Gradio interface launched.")

    except Exception as e:
        logging.error(f"Error running Gradio interface: {str(e)}")
        raise

# Main
if __name__ == "__main__":
    try:
        # Establecer logging
        logging.info("Starting application...")
        
        # Verificar variables de entorno críticas
        if not openai.api_key:
            logging.error("OPENAI_API_KEY no está configurada. Por favor, establece esta variable de entorno.")
            print("ERROR: OPENAI_API_KEY no está configurada.")
            exit(1)
            
        # Load Config
        config = load_config()

        # Extract configuration variables
        title = config.get("title", "Azure OpenAI App running in Azure Red Hat OpenShift")
        description = config.get("description", "Created & Maintained by GBB TEAM @ Red Hat and Microsoft")
        port = config.get("port", 8080)
        deployment_name = config.get("deployment_name", "WorkshopIA")
        api_type = config.get("api_type", "azure")
        api_version = config.get("api_version", "2023-05-15")

        # Imprimir información de configuración
        logging.info(f"Configuración del despliegue: {deployment_name} en {openai.api_base}")
        logging.info(f"Usando modelo: gpt-35-turbo-0125")
        
        # Load the Azure OpenAI Model using LangChain
        model = load_model(api_type, api_version, deployment_name)

        # Execute Gradio App
        run(port, title, description)
    except KeyboardInterrupt:
        logging.info("Application terminated by user.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())