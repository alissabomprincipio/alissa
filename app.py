import streamlit as st
from google import genai
from PIL import Image
import io

# Configuração da página
st.set_page_config(layout="wide", page_title="Assistente de Estilo")

NOME_DO_APP = "Seu Consultor de Moda I.A."
SUBTITULO_APP = "Descubra o look ideal para qualquer momento."
TEXTO_RODAPE = "Transformando sua imagem com inteligência."

# Recupera a chave da API
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Erro: A chave da API ('GEMINI_API_KEY') não foi encontrada nas configurações 'Secrets' do Streamlit.")
    st.stop()

# Inicializa o cliente da IA
client = genai.Client(api_key=API_KEY)

def analisar_imagem_e_evento(imagem_pil, texto_evento):
    prompt = f"""
    Analise a foto da pessoa fornecida e o seguinte evento ou ocasião: '{texto_evento}'.
    Com base nas características físicas da pessoa, estilo percebido na foto e no evento,
    crie uma sugestão completa de look profissional e fashion.
    Sua resposta deve ter obrigatoriamente duas partes, divididas exatamente pela palavra-chave "SEPARADOR_DE_CONTEUDO":
    Parte 1 (Descrição para a cliente): Uma descrição detalhada e elegante do look sugerido, explicando por que as peças funcionam para ela e para a ocasião.
    Parte 2 (Prompt para a IA de imagem): Um prompt fotográfico preciso, em alta definição e realista para um modelo de geração de imagem criar uma foto de uma modelo (com características similares à pessoa da foto original) vestindo exatamente esse look completo no ambiente do evento. Foque em detalhes de iluminação, pose e textura dos tecidos.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, imagem_pil]
        )
        return response.text
    except Exception as e:
        return f"Erro durante a análise: {e}"

def gerar_imagem_do_look(prompt_imagem):
    try:
        response = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt_imagem
        )
        image_bytes = response.generated_images[0].image.image_bytes
        return Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        st.error(f"Erro ao gerar a visualização do look: {e}")
        return None

# --- Interface ---
st.title(NOME_DO_APP)
st.subheader(SUBTITULO_APP)
st.divider()

with st.sidebar:
    st.header("Sua Foto e Ocasião")
    st.write("Capture sua foto e nos diga para qual evento você quer se vestir.")
    foto_capturada = st.camera_input("Tire sua foto")
    evento_usuario = st.text_input("Qual é a ocasião?", placeholder="Ex: Casamento, entrevista de emprego, jantar romântico")
    botao_gerar = st.button("Gerar Sugestão de Look", type="primary")

if botao_gerar and foto_capturada and evento_usuario:
    with st.spinner("Analisando sua foto e criando seu look exclusivo... Isso pode levar um minuto."):
        imagem_pil = Image.
