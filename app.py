import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io

# Configuração da página
st.set_page_config(layout="wide", page_title="Alissa - Consultora de Moda")

NOME_DO_APP = "ALISSA"
SUBTITULO_APP = "Sua consultoria de moda exclusiva e instantânea."
TEXTO_RODAPE = "Powered by Blackhaus R&D Logic"

# Recupera a chave da API dos Secrets do Streamlit
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Erro: Adicione a 'GEMINI_API_KEY' nos Secrets do Streamlit.")
    st.stop()

# Inicializa o cliente da IA
client = genai.Client(api_key=API_KEY)

def analisar_evento(imagem_pil, texto_evento):
    """
    Passo 1: Analisa a foto e o evento para criar a descrição e o prompt técnico.
    """
    prompt = f"""
    Aja como uma consultora de moda de luxo. Analise a pessoa na foto e o evento: '{texto_evento}'.
    Retorne a resposta EXATAMENTE neste formato, separada pela palavra SEPARADOR:
    [Descrição elegante para a cliente sobre o porquê desse look]
    SEPARADOR
    [Prompt técnico em inglês para gerar a imagem. Instrução: Mantenha a pessoa da imagem original exatamente como ela é (rosto, corpo, cabelo), mas substitua suas roupas pelo look sugerido: (descreva o look aqui). O cenário deve ser o ambiente de (evento).]
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, imagem_pil]
        )
        return response.text
    except Exception as e:
        return f"Erro na análise: {e}"

def gerar_imagem_try_on(prompt_tecnico, imagem_referencia):
    """
    Passo 2: O PULO DO GATO. 
    Manda a FOTO ORIGINAL + O PROMPT para o modelo gerar a imagem baseada na referência.
    """
    try:
        # Enviamos a imagem de referência JUNTO com o prompt
        response = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=[prompt_tecnico, imagem_referencia],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            )
        )
        
        for part in response.parts:
            if part.inline_data:
                return Image.open(io.BytesIO(part.inline_data.data))
        return None
    except Exception as e:
        st.error(f"Erro no processamento da imagem: {e}")
        return None

# --- Interface ---
st.title(NOME_DO_APP)
st.write(SUBTITULO_APP)
st.divider()

with st.sidebar:
    st.header("Entrada de Dados")
    foto = st.camera_input("Tire sua foto")
    evento = st.text_input("Para onde você vai?", placeholder="Ex: Casamento na praia")
    botao = st.button("VESTIR LOOK", type="primary")

if botao and foto and evento:
    with st.spinner("Alissa está trabalhando no seu estilo..."):
        img_original = Image.open(foto)
        
        # 1. Analisa e gera o texto/prompt
        raw_res = analisar_evento(img_original, evento)
        
        if "SEPARADOR" in raw_res:
            texto_final, prompt_final = raw_res.split("SEPARADOR")
            
            # 2. Gera a imagem usando a original como referência (Img2Img)
            img_look = gerar_imagem_try_on(prompt_final.strip(), img_original)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Sugestão da Alissa")
                st.write(texto_final.strip())
            
            with col2:
                st.subheader("Resultado Visual")
                if img_look:
                    st.image(img_look, use_container_width=True)
                else:
                    st.error("Não consegui processar a imagem do look.")
        else:
            st.write(raw_res)

elif botao:
    st.warning("Preciso da sua foto e do evento para trabalhar!")

st.markdown(f"--- \n<p style='text-align: center;'>{TEXTO_RODAPE}</p>", unsafe_allow_html=True)
