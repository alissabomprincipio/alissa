import streamlit as st
from google import genai
from PIL import Image
import io

# --- CONFIGURAÇÃO VISUAL PREMIUM ---
st.set_page_config(page_title="ALISSA | Personal Stylist", page_icon="👗", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .main { background-color: #ffffff; }
    .stButton>button {
        width: 100%;
        border-radius: 30px;
        height: 3.5em;
        background-color: #000000;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stTextArea>div>div>textarea { border-radius: 15px; }
    div[data-testid="stCameraInput"] { border-radius: 20px; overflow: hidden; }
    h1 { font-family: 'Helvetica', sans-serif; letter-spacing: -1px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("ALISSA")
st.write("Sua consultoria de moda exclusiva e instantânea.")

# --- SUBSTITUA ABAIXO PELA SUA CHAVE API ---
API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

# --- ESTOQUE DA LOJA (Edite os nomes abaixo para testar) ---
estoque = [
    {"peça": "Vestido Midi Acetinado", "cor": "Preto", "estilo": "Elegante/Noite"},
    {"peça": "Blazer de Alfaiataria", "cor": "Off-White", "estilo": "Clássico/Business"},
    {"peça": "Calça Pantalona Lino", "cor": "Cru", "estilo": "Casual Chic"},
    {"peça": "Saia Plissada", "cor": "Verde Esmeralda", "estilo": "Social"},
    {"peça": "Camisa de Seda", "cor": "Azul Serenity", "estilo": "Versátil"}
]

# --- INTERFACE DO APP ---
foto = st.camera_input("")

evento = st.text_area("Para qual evento você deseja sugestões?", placeholder="Ex: Casamento de dia, Reunião de trabalho, Jantar...")

if foto and evento:
    img = Image.open(foto)
    
    if st.button("GERAR SUGESTÃO DE LOOK"):
        with st.spinner("Analisando seu perfil..."):
            try:
                # Prepara o contexto para a IA
                lista_estoque = "\n".join([f"- {i['peça']} na cor {i['cor']} (Estilo: {i['estilo']})" for i in estoque])
                
                prompt = f"""
                Atue como uma Stylist de moda de alto padrão. 
                Analise a foto da cliente para entender seu biotipo e estilo.
                O evento é: {evento}.
                
                Utilize APENAS as seguintes peças disponíveis na nossa loja:
                {lista_estoque}
                
                Sugira o melhor look, explique por que favorece o corpo dela e por que é adequado para o evento.
                Seja sofisticada e direta no texto. Use emojis de moda.
                """

                response = client.models.generate_content(model='gemini-2.5-flash', contents=[prompt, img])
                
                st.markdown("---")
                st.subheader("Sugestão Alissa:")
                st.write(response.text)
                
            except Exception as e:
              st.error(f"Erro real do Google: {e}")

st.markdown("<br><br><p style='text-align: center; font-size: 0.7em; color: #999;'>POWERED BY BH VISION ENGINE</p>", unsafe_allow_html=True)
