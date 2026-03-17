import streamlit as st
from google import genai
from PIL import Image
import io

# Configuração da página e visual geral (Genérico)
st.set_page_config(layout="wide", page_title="Assistente de Estilo")

# Definição de textos e nomes genéricos para a interface
NOME_DO_APP = "Seu Consultor de Moda I.A."
SUBTITULO_APP = "Descubra o look ideal para qualquer momento."
TEXTO_RODAPE = "Transformando sua imagem com inteligência."

# Recupera a chave da API dos segredos do Streamlit
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Erro: A chave da API ('GEMINI_API_KEY') não foi encontrada nas configurações 'Secrets' do Streamlit.")
    st.stop()

# Inicializa o cliente da IA do Google
client = genai.Client(api_key=API_KEY)

def analisar_imagem_e_evento(imagem_pil, texto_evento):
    """
    Analisa a foto da pessoa e o evento, retornando a descrição e o prompt da imagem.
    Utiliza o modelo gemini-2.5-flash para análise multimodal.
    """
    prompt = f"""
    Analise a foto da pessoa fornecida e o seguinte evento ou ocasião: '{texto_evento}'.
    Com base nas características físicas da pessoa, estilo percebido na foto e no evento,
    crie uma sugestão completa de look profissional e fashion.
    Sua resposta deve ter obrigatoriamente duas partes, divididas exatamente pela palavra-chave "SEPARADOR_DE_CONTEUDO":
    Parte 1 (Descrição para a cliente): Uma descrição detalhada e elegante do look sugerido, explicando por que as peças funcionam para ela e para a ocasião.
    Parte 2 (Prompt para a IA de imagem): Um prompt fotográfico preciso, em alta definição e realista para um modelo de geração de imagem criar uma foto de uma modelo (com características similares à pessoa da foto original) vestindo exatamente esse look completo no ambiente do evento. Foque em detalhes de iluminação, pose e textura dos tecidos.
    """
    
    # Modelo estável para análise multimodal
    modelo_analise = 'gemini-2.5-flash'
    
    try:
        # Envia a foto e o prompt para a IA
        response = client.models.generate_content(
            model=modelo_analise,
            contents=[prompt, imagem_pil]
        )
        return response.text
    except Exception as e:
        return f"Erro durante a análise: {e}"

def gerar_imagem_do_look(prompt_imagem):
    """
    Gera uma imagem realista do look sugerido com base no prompt recebido.
    Utiliza o modelo dedicado à geração de imagens.
    """
    # Modelo dedicado para geração de imagens fotográficas
    modelo_imagem = 'imagen-3' 
    
    try:
        # Gera a imagem baseada no prompt
        response = client.models.generate_image(
            model=modelo_imagem,
            prompt=prompt_imagem
        )
        # Recupera os bytes da imagem gerada e converte para objeto PIL
        image_bytes = response.generated_images[0].image
        return Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        st.error(f"Erro ao gerar a visualização do look: {e}")
        return None

# --- Estrutura da Interface ---

# Título Principal e Subtítulo
st.title(NOME_DO_APP)
st.subheader(SUBTITULO_APP)
st.divider()

# Coluna lateral para os inputs
with st.sidebar:
    st.header("Sua Foto e Ocasião")
    st.write("Capture sua foto e nos diga para qual evento você quer se vestir.")
    
    # Input de câmera
    foto_capturada = st.camera_input("Tire sua foto")
    
    # Input de texto para o evento
    evento_usuario = st.text_input("Qual é a ocasião?", placeholder="Ex: Casamento, entrevista de emprego, jantar romântico")
    
    # Botão para iniciar a geração
    botao_gerar = st.button("Gerar Sugestão de Look", type="primary")

# Área principal para exibir os resultados
if botao_gerar and foto_capturada and evento_usuario:
    with st.spinner("Analisando sua foto e criando seu look exclusivo... Isso pode levar um minuto."):
        
        # Converte a foto capturada (Streamlit UploadedFile) para objeto PIL
        imagem_pil = Image.open(foto_capturada)
        
        # 1. Passo: Análise da foto e criação da sugestão/prompt
        resultado_analise = analisar_imagem_e_evento(imagem_pil, evento_usuario)
        
        # 2. Passo: Processamento da resposta
        descricao_look = "A descrição do look não pôde ser gerada."
        prompt_para_imagem = ""
        
        if "SEPARADOR_DE_CONTEUDO" in resultado_analise:
            try:
                # Divide a resposta nas duas partes obrigatórias
                partes = resultado_analise.split("SEPARADOR_DE_CONTEUDO")
                descricao_look = partes[0].strip()
                prompt_para_imagem = partes[1].strip()
            except Exception as e:
                st.error(f"Erro ao processar a resposta da IA: {e}")
                descricao_look = resultado_analise
        else:
            # Se não houver o separador, exibe a resposta inteira como descrição
            descricao_look = resultado_analise
            
        # 3. Passo: Geração da imagem do look visual
        imagem_sugerida = None
        if prompt_para_imagem:
            imagem_sugerida = gerar_imagem_do_look(prompt_para_imagem)
            
        # 4. Passo: Exibição dos resultados na interface
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sua Sugestão de Look")
            st.markdown(descricao_look)
            
        with col2:
            st.subheader("Visualização do Look")
            if imagem_sugerida:
                st.image(imagem_sugerida, caption="Look gerado pela I.A. para você", use_column_width=True)
            else:
                st.warning("Não foi possível gerar uma visualização para este look no momento.")

elif botao_gerar:
    # Aviso caso o usuário clique sem fornecer todos os dados
    st.warning("Por favor, tire sua foto e nos diga a ocasião antes de continuar.")

else:
    # Mensagem inicial informando o que fazer
    st.info("Para começar, tire sua foto e nos diga a ocasião na barra lateral e clique em 'Gerar Sugestão de Look'.")

# Rodapé (Genérico)
st.markdown(f"--- \n\n<p style='text-align: center; color: #666;'>{TEXTO_RODAPE}</p>", unsafe_allow_html=True)
