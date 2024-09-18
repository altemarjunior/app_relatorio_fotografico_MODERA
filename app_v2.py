import streamlit as st
from PIL import Image
from fpdf import FPDF
import os
from streamlit_pdf_viewer import pdf_viewer
from style_st import configure_markdown_title, hide_share_button, remove_deploy_button, h2title_format
import re

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

def create_pdf_with_header_and_title(image_paths, bg_image_path, signature_img_path, output_path, empresa_selecionada, contrato, data_inicio, data_fim):
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
        bg_image_tmp = f'/tmp/{os.path.basename(bg_image_path)}'
        bg_image.save(bg_image_tmp)
        pdf.image(bg_image_tmp, x=0, y=0, w=bg_width_mm, h=bg_height_mm)

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
                img_path_tmp = image_paths[i + j]

                img = Image.open(img_path_tmp)
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
                pdf.image(img_path_tmp, x=img_x_pos, y=img_y_pos, w=new_width, h=new_height)

            pdf.set_line_width(0.5)
            pdf.rect(x_pos, y_pos, img_width, img_height)

        pdf.set_line_width(1)
        pdf.rect(quadro_x - padding, quadro_y - padding, quadro_width, quadro_height)

        # Adicionar a imagem de assinatura ao final da página atual
        pdf.add_signature(signature_img_path)

    # Atualizar o nome do arquivo PDF de acordo com o contrato
    output_pdf_path = f"/content/REGISTRO_FOTOGRAFICO_{contrato.replace('/', '_')}.pdf"
    pdf.output(output_pdf_path)
    print(f"PDF gerado com sucesso em: {output_pdf_path}")

# Criar widgets para entrada de texto ou seleção de lista
empresa_widget = Dropdown(
    options=[
        "CONSÓRCIO MODERA-LBR-SCB",
        "LCM CONSTRUÇÃO E SERVIÇOS LTDA",
        "CONSTRUTORA MEIRELLES MASCARENHAS LTDA",
        "MATERA ENGENHARIA",
        "SINALMIG - SINAIS E SISTEMAS LTDA",
        "DIGITE MANUALMENTE"
    ],
    description='EMPRESA:'
)

empresa_text_widget = Text(
    description='EMPRESA:',
    placeholder='DIGITE O NOME DA EMPRESA'
)

contrato_widget = Dropdown(
    options=[
        'SR-673/2021',
        'SR-910/2019',
        'SR-399/2023',
        'SR-400/2023',
        'SR-472/2019',
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
        "DIGITE MANUALMENTE"
    ],
    description='CONTRATO:'
)

contrato_text_widget = Text(
    description='CONTRATO:',
    placeholder='DIGITE O CONTRATO'
)

data_inicio_widget = DatePicker(
    description='DATA ÍNICIO:',
    value=None
)

data_fim_widget = DatePicker(
    description='DATA FIM:',
    value=None
)

# Funções para atualizar a visibilidade dos campos de texto
def update_empresa_visibility(change):
    if change['new'] == "DIGITE MANUALMENTE":
        empresa_text_widget.layout.display = 'block'
    else:
        empresa_text_widget.layout.display = 'none'

def update_contrato_visibility(change):
    if change['new'] == "DIGITE MANUALMENTE":
        contrato_text_widget.layout.display = 'block'
    else:
        contrato_text_widget.layout.display = 'none'

empresa_widget.observe(update_empresa_visibility, names='value')
contrato_widget.observe(update_contrato_visibility, names='value')

display(empresa_widget, empresa_text_widget, contrato_widget, contrato_text_widget, data_inicio_widget, data_fim_widget)

# Inicialmente esconder os campos de texto manual
empresa_text_widget.layout.display = 'none'
contrato_text_widget.layout.display = 'none'

# Função para capturar a entrada do usuário e gerar o PDF
def gerar_pdf(empresa_selecionada, contrato_selecionado, data_inicio, data_fim):
    from google.colab import files

    if empresa_selecionada == "DIGITE MANUALMENTE":
        empresa_selecionada = empresa_text_widget.value
    if contrato_selecionado == "DIGITE MANUALMENTE":
        contrato_selecionado = contrato_text_widget.value

    # Instrução para o usuário inserir a imagem de plano de fundo
    print("Por favor, insira a imagem de plano de fundo do seu PDF.")
    uploaded_bg_image = files.upload()
    bg_image_path = list(uploaded_bg_image.keys())[0]

    # Instrução para o usuário inserir as fotos do relatório
    print("Por favor, insira as fotos do seu relatório.")
    uploaded_images = files.upload()
    image_paths = list(uploaded_images.keys())

    # Instrução para o usuário inserir a imagem de assinatura
    print("Por favor, insira a imagem de assinatura do seu PDF.")
    uploaded_signature_image = files.upload()
    signature_img_path = list(uploaded_signature_image.keys())[0]

    # Especificar o caminho de saída do PDF
    create_pdf_with_header_and_title(image_paths, bg_image_path, signature_img_path, None, empresa_selecionada, contrato_selecionado, data_inicio, data_fim)

    # Oferecer download do PDF gerado
    files.download(f"/content/REGISTRO_FOTOGRAFICO_{contrato_selecionado.replace('/', '_')}.pdf")

# Botão para gerar o PDF
gerar_pdf_button = widgets.Button(description="GERAR PDF")

# Vincular a função ao botão
def on_button_clicked(b):
    gerar_pdf(empresa_widget.value, contrato_widget.value, data_inicio_widget.value, data_fim_widget.value)

gerar_pdf_button.on_click(on_button_clicked)

display(gerar_pdf_button)
