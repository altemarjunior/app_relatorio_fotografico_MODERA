import streamlit as st


def configure_markdown_title(title):
    st.markdown(
        """
        <style>
            header[data-testid="stHeader"] {
                position: relative;
                z-index: 1;
            }
            .title-container {
                text-align: center;
                font-size: 34px;
                font-weight: bold;
                font-style: italic;
                position: relative;
                z-index: 9999;
               /* padding-top: 60px; /* Ajuste conforme necessário */
                margin-top: -70px; /* Ajuste conforme necessário */
            }
            .stToolbar {
                position: absolute;
                top: 10px; /* Ajuste conforme necessário */
                right: 10px; /* Ajuste conforme necessário */
                z-index: 10000; /* Certifique-se de que os botões fiquem acima de outros elementos */
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="title-container">{}</div>'.format(title), unsafe_allow_html=True)

    st.markdown('''
                <style>
        h1 {
            text-align: center;
            font-size: 34px;
            font-weight: bold;
        }
        </style>
    ''', unsafe_allow_html=True)


#hide share button <span data-testid="stActionButtonLabel">Share</span>
def hide_share_button():
    css_styles = """
    <style>
        [data-testid="stActionButton"] {
            display: none;
        }
    </style>
    """
    st.markdown(css_styles, unsafe_allow_html=True)


def remove_deploy_button():
    css_styles = """
    <style>
        [data-testid="stDeployButton"] {
            display: none;
        }
    </style>
    """
    st.markdown(css_styles, unsafe_allow_html=True)


def h2title_format(title):
    css_styles = """
    <style>
        h2 {
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            margin-top: -70px;
            border-bottom: 1px solid #e4e8ee;
        }
    </style>
    """
    st.markdown(f"{css_styles}<h2>{title}</h2>", unsafe_allow_html=True)