import streamlit as st
from PIL import Image
from fpdf import FPDF
import os
import tempfile  # Usar para criar arquivos temporários
from streamlit_pdf_viewer import pdf_viewer
from style_st import configure_markdown_title, hide_share_button, remove_deploy_button, h2title_format
import re

st.set_page_config(page_title="📸 Gerador de PDF com Registro Fotográfico", layout="wide")

class PDFWithPageNumbers(FPDF):
    def footer(self):
        # Adicionar número de página no rodapé, alinhado à direita
        self.set_y(-15)
        self.set_font("Arial", style='B', size=10)
        page_number = f"Página {self.page_no():02d}"
        self.cell(0, 10, page_number, 0, 0, 'R')

    def add_signature(self, signature_img_path):
        # Adicionar imagem de assinatura no final da página, centralizada
        signature = Image.open(signature_img_path)
        signature_width_mm = 30  # Largura padrão para a assinatura
        signature_height_mm = signature.height * (signature_width_mm / signature.width)
        x_pos = (210 - signature_width_mm) / 2  # Centralizar a imagem
        y_pos = 297 - 20  # Posição vertical ajustada para que não sobreponha o rodapé
        self.image(signature_img_path, x=x_pos, y=y_pos, w=signature_width_mm, h=signature_height_mm)

def create_pdf_with_header_and_title(image_paths, bg_image_path, signature_img_path, empresa_selecionada, contrato, data_inicio, data_fim):
    pdf = PDFWithPageNumbers(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)

    # Carregar a imagem de plano de fundo
    bg_image = Image.open(bg_image_path)
    bg_width_mm = 210  # Largura da página A4 em mm
    bg_height_mm = 297  # Altura da página A4 em mm

    images_per_page = 6

    for i in range(0, len(image_paths), images_per_page):
        pdf.add_page()

        # Adicionar a imagem de plano de fundo
        pdf.image(bg_image_path, x=0, y=0, w=bg_width_mm, h=bg_height_mm)

        # Adicionar o título abaixo do cabeçalho em negrito
        pdf.set_font("Arial", style='B', size=12)
        pdf.set_xy(10, 25)
        pdf.cell(0, 8, "DEPARTAMENTO NACIONAL DE INFRAESTRUTURA DE TRANSPORTES - DNIT/AM", ln=True, align="C")
        pdf.set_xy(10, 32)
        pdf.cell(0, 8, "REGISTRO FOTOGRÁFICO", ln=True, align="C")

        # Diminuir o recuo entre o cabeçalho e os registros fotográficos
        y_start_images = 48

        # Calcular a posição total do quadro maior
        img_width = 90
        img_height = 70
        padding = 3
        quadro_width = 2 * img_width + 3 * padding
        quadro_height = 3.05 * (img_height + padding)
        quadro_x = (210 - quadro_width) / 2
        quadro_y = y_start_images + padding

        # Adicionar informações sobre a empresa, contrato e data em três colunas
        largura_coluna1 = 90  # Mais larga para "EMPRESA"
        largura_coluna2 = 40  # Para "CONTRATO"
        largura_coluna3 = 40  # Para "DATA"

        pdf.set_font("Arial", style='B', size=8)
        pdf.set_xy(quadro_x, 40)  # Alinhar a partir do quadro

        # Coluna 1 - EMPRESA
        pdf.cell(largura_coluna1, 6, f"EMPRESA: {empresa_selecionada}", border=0, ln=0, align="L")

        # Coluna 2 - CONTRATO
        pdf.cell(largura_coluna2, 6, f"CONTRATO: {contrato}", border=0, ln=0, align="L")

        # Coluna 3 - DATA
        data_formatada = f"{data_inicio.strftime('%d/%m/%Y')} A {data_fim.strftime('%d/%m/%Y')}" if data_inicio and data_fim else "Sem Data"
        pdf.cell(largura_coluna3, 6, f"DATA: {data_formatada}", border=0, ln=1, align="L")

        # Organizar imagens em duas colunas e três linhas, sem quadros menores de informações
        for j in range(images_per_page):
            col = j % 2
            row = j // 2
            x_pos = quadro_x + col * (img_width + padding)
            y_pos = quadro_y + row * (img_height + padding)

            if i + j < len(image_paths):
                img_file = image_paths[i + j]

                # Salvar o arquivo de imagem temporariamente
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as img_temp:
                    img_temp.write(img_file.getbuffer())
                    img_temp_path = img_temp.name

                img = Image.open(img_temp_path)
                img.thumbnail((img_width, img_height), Image.LANCZOS)

                img_aspect_ratio = img.width / img.height
                cell_aspect_ratio = img_width / img_height

                if img_aspect_ratio > cell_aspect_ratio:
                    new_width = img_width
                    new_height = img_width / img_aspect_ratio
                else:
                    new_height = img_height
                    new_width = img_height * img_aspect_ratio

                img_x_pos = x_pos + (img_width - new_width) / 2
                img_y_pos = y_pos + (img_height - new_height) / 2
                pdf.image(img_temp_path, x=img_x_pos, y=img_y_pos, w=new_width, h=new_height)

                # Remover o arquivo temporário após o uso
                os.remove(img_temp_path)

            pdf.set_line_width(0.5)
            pdf.rect(x_pos, y_pos, img_width, img_height)

        pdf.set_line_width(1)
        pdf.rect(quadro_x - padding, quadro_y - padding, quadro_width, quadro_height)

        # Adicionar a imagem de assinatura ao final da página atual
        pdf.add_signature(signature_img_path)

    output_pdf_path = f"REGISTRO_FOTOGRAFICO_{contrato.replace('/', '_')}.pdf"
    pdf.output(output_pdf_path)
    return output_pdf_path

# add image logo 
st.sidebar.image("Consórcio2-removebg-preview (1).png", use_column_width=True)

# Sidebar para seleção de opções
st.sidebar.title("⚙️ Configurações do Relatório")
empresa_options = [
    "CONSÓRCIO MODERA-LBR-SCB",
    "LCM CONSTRUÇÃO E SERVIÇOS LTDA",
    "CONSTRUTORA MEIRELLES MASCARENHAS LTDA",
    "MATERA ENGENHARIA",
    "SINALMIG - SINAIS E SISTEMAS LTDA",
    "DIGITE MANUALMENTE"
]
empresa_selecionada = st.sidebar.selectbox('Selecione a EMPRESA:', empresa_options)
if empresa_selecionada == "DIGITE MANUALMENTE":
    empresa_selecionada = st.sidebar.text_input("Digite o nome da EMPRESA:")

contrato_options = [
    'SR-673/2021',
    'SR-910/2019',
    'SR-399/2023',
    'SR-400/2023',
    'SR-472/2020',
    'SR-605/2020',
    'SR-207/2020',
    'SR-208/2020',
    'SR-078/2019',
    'SR-595/2020',
    'SR-667/2019',
    'SR-226/2019',
    'SR-168/2020',
    'SR-430/2023',
    'SR-129/2021',
    'SR-290/2021',
]
contrato_selecionado = st.sidebar.selectbox('Selecione o CONTRATO:', contrato_options)

col1_date, col2_date = st.sidebar.columns(2)
data_inicio = col1_date.date_input("Data de Início:")
data_fim = col2_date.date_input("Data de Fim:")

bg_image = st.sidebar.file_uploader("🖼️ Carregar a imagem de plano de fundo", type=["png", "jpg", "jpeg"])
uploaded_images = st.sidebar.file_uploader("📷 Carregar as fotos do relatório", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
signature_img = st.sidebar.file_uploader("✍️ Carregar a imagem de assinatura", type=["png", "jpg", "jpeg"])

# center title
configure_markdown_title('📄 Gerador de PDF com Registro Fotográfico 📸')
# hide share button
hide_share_button()
# remove deploy button
remove_deploy_button()
h2title_format("CONSÓRCIO MODERA-LBR-SCB")

st.markdown("Utilize as opções na barra lateral para personalizar e gerar seu relatório fotográfico.")

if st.button("🛠️ Gerar PDF"):
    if bg_image and uploaded_images and signature_img:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{bg_image.name.split('.')[-1]}") as bg_temp:
            bg_temp.write(bg_image.getbuffer())
            bg_image_path = bg_temp.name

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{signature_img.name.split('.')[-1]}") as signature_temp:
            signature_temp.write(signature_img.getbuffer())
            signature_img_path = signature_temp.name

        image_paths = []
        for img in uploaded_images:
            img_path = img  # Utilizando o arquivo de imagem diretamente
            image_paths.append(img)

        # Certifique-se de passar 'data_fim' corretamente
        output_pdf_path = create_pdf_with_header_and_title(image_paths, bg_image_path, signature_img_path, empresa_selecionada, contrato_selecionado, data_inicio, data_fim)

        st.success(f"🎉 PDF gerado com sucesso!")
        
        col1, col2 = st.columns(2)
        col1.download_button("⬇️ Download PDF", data=open(output_pdf_path, "rb"), file_name=output_pdf_path)

        st.session_state['output_pdf_path'] = output_pdf_path

        # Remover arquivos temporários
        os.remove(bg_image_path)
        os.remove(signature_img_path)

    else:
        st.error("⚠️ Por favor, carregue todos os arquivos necessários (fundo, fotos e assinatura).")

if 'output_pdf_path' in st.session_state:
    if st.toggle("📑 Visualizar PDF"):
        pdf_viewer(st.session_state['output_pdf_path'])
