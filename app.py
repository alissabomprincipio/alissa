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
        # AQUI ESTÁ A CORREÇÃO: O modelo exato é o 001
        response = client.models.generate_images(
            model='imagen-3.0-generate-001',
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
        imagem_pil = Image.open(foto_capturada)
        resultado_analise = analisar_imagem_e_evento(imagem_pil, evento_usuario)
        
        descricao_look = "A descrição do look não pôde ser gerada."
        prompt_para_imagem = ""
        
        if "SEPARADOR_DE_CONTEUDO" in resultado_analise:
            try:
                partes = resultado_analise.split("SEPARADOR_DE_CONTEUDO")
                descricao_look = partes[0].strip()
                prompt_para_imagem = partes[1].strip()
            except Exception as e:
                st.error(f"Erro ao processar a resposta da IA: {e}")
                descricao_look = resultado_analise
        else:
            descricao_look = resultado_analise
            
        imagem_sugerida = None
        if prompt_para_imagem:
            imagem_sugerida = gerar_imagem_do_look(prompt_para_imagem)
            
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sua Sugestão de Look")
            st.markdown(descricao_look)
            
        with col2:
            st.subheader("Visualização do Look")
            if imagem_sugerida:
                st.image(imagem_sugerida, caption="Look gerado pela I.A. para você", use_container_width=True)
            else:
                st.warning("Não foi possível gerar uma visualização para este look no momento.")

elif botao_gerar:
    st.warning("Por favor, tire sua foto e nos diga a ocasião antes de continuar.")

else:
    st.info("Para começar, tire sua foto e nos diga a ocasião na barra lateral e clique em 'Gerar Sugestão de Look'.")

st.markdown(f"--- \n\n<p style='text-align: center; color: #666;'>{TEXTO_RODAPE}</p>", unsafe_allow_html=True)
