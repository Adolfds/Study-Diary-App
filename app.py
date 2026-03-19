import streamlit as st
import pandas as pd
import os
import sys
import time
from datetime import datetime
import base64
import re

try:
    from nbconvert import HTMLExporter
    import nbformat
    NB_CONVERT_AVAILABLE = True
except ImportError:
    NB_CONVERT_AVAILABLE = False

# FUNÇÕES DE AJUDA E CONFIGURAÇÕES INICIAIS

def get_data_path(filename):
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(application_path, filename)

def carregar_dados():
    cursos_path = get_data_path('cursos.csv')
    secoes_path = get_data_path('secoes.csv')
    anotacoes_path = get_data_path('anotacoes.csv')
    
    if not os.path.exists(cursos_path):
        pd.DataFrame(columns=['nome_curso']).to_csv(cursos_path, index=False)
    
    if not os.path.exists(secoes_path):
        pd.DataFrame(columns=['curso', 'nome_secao']).to_csv(secoes_path, index=False)
        
    if not os.path.exists(anotacoes_path):
        pd.DataFrame(columns=['curso', 'secao', 'titulo_anotacao', 'conteudo', 'anexo_path', 'timestamp']).to_csv(anotacoes_path, index=False)
    
    cursos = pd.read_csv(cursos_path)
    secoes = pd.read_csv(secoes_path)
    anotacoes = pd.read_csv(anotacoes_path).fillna('')
    return cursos, secoes, anotacoes

def exibir_anexo(anexo_path):
    try:
        file_extension = os.path.splitext(anexo_path)[1].lower()
        full_path = get_data_path(anexo_path)

        st.markdown("---")
        st.subheader("Anexo:")

        if file_extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            st.image(full_path, use_column_width=True)

        elif file_extension == '.pdf':
            with open(full_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            
        elif file_extension == '.py':
            with open(full_path, "r", encoding='utf-8') as f:
                code_content = f.read()
            st.code(code_content, language='python')

        elif file_extension in ['.csv', '.xlsx', '.xls']:
            try:
                if file_extension == '.csv':
                    df = pd.read_csv(full_path)
                else:
                    df = pd.read_excel(full_path)
                st.dataframe(df)
            except Exception as e:
                st.error(f"Não foi possível ler a planilha: {e}")

        elif file_extension == '.ipynb':
            if NB_CONVERT_AVAILABLE:
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        nb_content = nbformat.read(f, as_version=4)
                    html_exporter = HTMLExporter()
                    (body, resources) = html_exporter.from_notebook_node(nb_content)
                    body = f'<style>{resources["inlining"]["css"][0]}</style>{body}'
                    st.components.v1.html(body, height=600, scrolling=True)
                except Exception as e:
                    st.error(f"Não foi possível renderizar o notebook: {e}")
            else:
                st.warning("A biblioteca 'nbconvert' é necessária para exibir notebooks. Instale-a com 'pip install nbconvert'.")

        else:
            st.info(f"A pré-visualização para arquivos '{file_extension}' não é suportada. Use o botão de download.")

        with open(full_path, "rb") as file:
            st.download_button(
                label=f"⬇️ Baixar Anexo ({os.path.basename(anexo_path)})",
                data=file,
                file_name=os.path.basename(anexo_path),
                key=f"download_{anexo_path}"
            )
    except FileNotFoundError:
        st.error(f"Arquivo de anexo não encontrado no caminho: {anexo_path}")
    except Exception as e:
        st.error(f"Ocorreu um erro ao tentar exibir o anexo: {e}")

# CÓDIGO PRINCIPAL

st.set_page_config(layout="wide", page_title="Diário de Estudos")
st.title("Meu Diário de Estudos 🎓")

if not os.path.exists(get_data_path('uploads')):
    os.makedirs(get_data_path('uploads'))

cursos_df, secoes_df, anotacoes_df = carregar_dados()

if 'editing_index' not in st.session_state:
    st.session_state['editing_index'] = None

st.sidebar.header("Meus Cursos")
lista_cursos = cursos_df['nome_curso'].tolist()
opcao_add_curso = "➕ Adicionar Novo Curso"
opcoes_curso = ["Selecione um curso"] + [opcao_add_curso] + sorted(lista_cursos)
curso_selecionado = st.sidebar.selectbox("Navegar Cursos:", opcoes_curso)

if curso_selecionado == opcao_add_curso:
    with st.sidebar.form("novo_curso_form", clear_on_submit=True):
        novo_curso = st.text_input("Nome do novo curso:")
        if st.form_submit_button("✅ Salvar Curso"):
            if novo_curso:
                cursos_df = pd.concat([cursos_df, pd.DataFrame([{'nome_curso': novo_curso}])], ignore_index=True)
                cursos_df.to_csv(get_data_path('cursos.csv'), index=False)
                st.success(f"Curso '{novo_curso}' adicionado!")
                st.rerun()

elif curso_selecionado and curso_selecionado != "Selecione um curso":
    st.sidebar.divider()
    st.sidebar.header(f"Seções de: {curso_selecionado}")
    secoes_do_curso_df = secoes_df[secoes_df['curso'] == curso_selecionado]
    lista_secoes = secoes_do_curso_df['nome_secao'].tolist()
    opcao_add_secao = "➕ Adicionar Nova Seção"
    
    def extrair_numero(texto_secao):
        numeros = re.findall(r'\d+', texto_secao)
        if numeros:
            return int(numeros[0])
        return 0
    secoes_ordenadas = sorted(lista_secoes, key=extrair_numero)
    opcoes_secao = ["Selecione uma seção"] + [opcao_add_secao] + secoes_ordenadas
    secao_selecionada = st.sidebar.selectbox("Navegar Seções:", opcoes_secao)

    if secao_selecionada == opcao_add_secao:
        with st.sidebar.form("nova_secao_form", clear_on_submit=True):
            nova_secao = st.text_input("Nome da nova seção:")
            if st.form_submit_button("✅ Salvar Seção"):
                if nova_secao:
                    nova_secao_data = {'curso': curso_selecionado, 'nome_secao': nova_secao}
                    secoes_df = pd.concat([secoes_df, pd.DataFrame([nova_secao_data])], ignore_index=True)
                    secoes_df.to_csv(get_data_path('secoes.csv'), index=False)
                    st.success(f"Seção '{nova_secao}' adicionada!")
                    st.rerun()

    elif secao_selecionada and secao_selecionada != "Selecione uma seção":
        with st.sidebar.expander("⚙️ Gerenciar Seção"):
            tab_edit, tab_delete = st.tabs(["Editar Nome", "Apagar Seção"])
            with tab_edit:
                with st.form("edit_section_form"):
                    novo_nome_secao = st.text_input("Novo nome para a seção:", value=secao_selecionada)
                    if st.form_submit_button("Salvar Alteração", type="primary"):
                        if novo_nome_secao and novo_nome_secao != secao_selecionada:
                            anotacoes_df.loc[(anotacoes_df['curso'] == curso_selecionado) & (anotacoes_df['secao'] == secao_selecionada), 'secao'] = novo_nome_secao
                            anotacoes_df.to_csv(get_data_path('anotacoes.csv'), index=False)
                            secoes_df.loc[(secoes_df['curso'] == curso_selecionado) & (secoes_df['nome_secao'] == secao_selecionada), 'nome_secao'] = novo_nome_secao
                            secoes_df.to_csv(get_data_path('secoes.csv'), index=False)
                            st.success("Seção renomeada com sucesso!")
                            st.rerun()
            with tab_delete:
                st.warning(f"Atenção: Apagar a seção '{secao_selecionada}' removerá permanentemente todas as suas anotações e anexos.", icon="⚠️")
                confirmacao = st.checkbox("Sim, eu entendo e quero apagar esta seção.", key="delete_confirm")
                if st.button("Apagar Seção Permanentemente", disabled=not confirmacao):
                    anotacoes_para_apagar = anotacoes_df[(anotacoes_df['curso'] == curso_selecionado) & (anotacoes_df['secao'] == secao_selecionada)]
                    for _, row in anotacoes_para_apagar.iterrows():
                        if row['anexo_path'] and os.path.exists(get_data_path(row['anexo_path'])):
                            os.remove(get_data_path(row['anexo_path']))
                    indices_anotacoes = anotacoes_para_apagar.index
                    anotacoes_df.drop(indices_anotacoes, inplace=True)
                    anotacoes_df.to_csv(get_data_path('anotacoes.csv'), index=False)
                    indice_secao = secoes_df[(secoes_df['curso'] == curso_selecionado) & (secoes_df['nome_secao'] == secao_selecionada)].index
                    secoes_df.drop(indice_secao, inplace=True)
                    secoes_df.to_csv(get_data_path('secoes.csv'), index=False)
                    st.success(f"Seção '{secao_selecionada}' e todo o seu conteúdo foram apagados.")
                    st.rerun()

        st.header(f"{curso_selecionado} > {secao_selecionada}")
        anotacoes_da_secao = anotacoes_df[(anotacoes_df['curso'] == curso_selecionado) & (anotacoes_df['secao'] == secao_selecionada)]
        
        numero_anotacao = 1
        for index, row in anotacoes_da_secao.iterrows():
            with st.expander(f"**{numero_anotacao} - {row['titulo_anotacao']}**"):
                if st.session_state['editing_index'] == index:
                    with st.form(f"edit_form_{index}"):
                        novo_titulo = st.text_input("Editar Título", value=row['titulo_anotacao'])
                        novo_conteudo = st.text_area("Editar Conteúdo", value=row['conteudo'], height=200)
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("✅ Salvar Alterações", use_container_width=True, type="primary"):
                                anotacoes_df.loc[index, 'titulo_anotacao'] = novo_titulo; anotacoes_df.loc[index, 'conteudo'] = novo_conteudo; anotacoes_df.loc[index, 'timestamp'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                anotacoes_df.to_csv(get_data_path('anotacoes.csv'), index=False); st.session_state['editing_index'] = None; st.rerun()
                        with col2:
                            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                st.session_state['editing_index'] = None; st.rerun()
                else:
                    st.caption(f"Postado em: {row.get('timestamp', 'Data não registrada')}")
                    
                    conteudo_formatado = row['conteudo'].replace('\n', '  \n')
                    st.markdown(conteudo_formatado)
                    
                    if row['anexo_path']: exibir_anexo(row['anexo_path'])
                    st.markdown("---")
                    col1, col2 = st.columns([0.2, 0.8])
                    with col1:
                        if st.button("✏️ Editar", key=f"edit_{index}", use_container_width=True):
                            st.session_state['editing_index'] = index; st.rerun()
                    with col2:
                        if st.button("🗑️ Apagar", key=f"delete_{index}", use_container_width=True):
                            anotacoes_df = anotacoes_df.drop(index)
                            anotacoes_df.to_csv(get_data_path('anotacoes.csv'), index=False)
                            if row['anexo_path'] and os.path.exists(get_data_path(row['anexo_path'])): os.remove(get_data_path(row['anexo_path']))
                            st.rerun()
            numero_anotacao += 1
            
        with st.popover("➕ Adicionar Nova Anotação", use_container_width=True):
            with st.form("nova_anotacao_form", clear_on_submit=True):
                titulo = st.text_input("Título da Anotação")
                conteudo = st.text_area("Conteúdo (Use formatação Markdown)")
                anexo = st.file_uploader("Anexar arquivo (opcional)", key="anexo_uploader")
                
                if st.form_submit_button("Salvar Anotação", type="primary"):
                    anexo_path = ""
                    if anexo is not None:
                        timestamp_file = int(time.time())
                        anexo_path = os.path.join('uploads', f"{timestamp_file}_{anexo.name}")
                        with open(get_data_path(anexo_path), "wb") as f: f.write(anexo.getbuffer())
                    
                    timestamp_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    nova_anotacao = {'curso': curso_selecionado, 'secao': secao_selecionada, 'titulo_anotacao': titulo, 'conteudo': conteudo, 'anexo_path': anexo_path, 'timestamp': timestamp_atual}
                    anotacoes_df = pd.concat([anotacoes_df, pd.DataFrame([nova_anotacao])], ignore_index=True)
                    anotacoes_df.to_csv(get_data_path('anotacoes.csv'), index=False)
                    st.success("Anotação salva!")
                    time.sleep(1)
                    st.rerun()
else:
    st.info("Selecione um curso ou adicione um novo para começar.")

st.sidebar.divider()
if st.sidebar.button("🔴 Desligar Servidor"):
    st.sidebar.success("Servidor desligando... Você pode fechar esta aba.")
    os._exit(0)