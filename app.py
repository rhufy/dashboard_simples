from flask import Flask, request, render_template, redirect,send_file
import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib
matplotlib.use('Agg')
app = Flask(__name__)
UPLOADS_FOLDER = 'UPLOADS'
app.config['UPLOADS_FOLDER'] = UPLOADS_FOLDER
os.makedirs(UPLOADS_FOLDER,exist_ok=True)

@app.route('/',methods = ['POST','GET'])
def uploads_file():
    if request.method == 'POST':
        arquivo = request.files['arquivo']
        if arquivo:
            caminho = os.path.join(UPLOADS_FOLDER,arquivo.filename)
            arquivo.save(caminho)
            return redirect(f'/analise/{arquivo.filename}')
    return render_template('uploads.html')

@app.route('/analise/<nome_arquivo>')
def analise(nome_arquivo):
    caminho = os.path.join(UPLOADS_FOLDER,nome_arquivo)
    df = pd.read_csv(caminho)
    colunas = df.columns.str.lower()
    #aqui eu estou evitando erro

    media_aluno = None
    media_disciplina = None
    qtd_aprovados = None
    qtd_reprovados =None

    if 'nota' in colunas and 'aluno' in colunas:
        media_alu = df.groupby('aluno')['nota'].mean().sort_values(ascending=False)
        media_aluno = media_alu.reset_index(name='media').to_html(classes='table table-bordered table-custom',index=False)
        
    if 'disciplina' in colunas and 'nota' in colunas:
        media_disc = df.groupby('disciplina')['nota'].mean().sort_values(ascending=False)
        media_disciplina = media_disc.reset_index(name='media').to_html(classes='table table-bordered table-custom',index=False)

    df['situacao'] = df['nota'].apply(lambda x : 'aprovado' if x>= 5 else 'reprovado')
    
    qtd_aprovados = (df['situacao'] == 'aprovado').sum()
    qtd_reprovados = (df['situacao'] == 'reprovado').sum()

    aprovacoes = df.loc[df['situacao']=='aprovado'].to_html(classes='table table-bordered table-custom',index=False)
    reprovacoes = df.loc[df['situacao']=='reprovado'].to_html(classes='table table-bordered table-custom',index=False)
    #graficos
    grafico_path = os.path.join('static','grafico','graficos_media_alunos.png')
    df.groupby('aluno')['nota'].mean().plot(kind='bar',color='green')
    plt.title('Rendimento médio de cada aluno :')
    plt.xlabel('Alunos:')
    plt.ylabel('media das notas:')
    plt.tight_layout()
    plt.savefig(grafico_path)
    plt.clf()
    
    grafico_path1 = os.path.join('static','grafico','graficos_disciplina_media.png')
    df.groupby('disciplina')['nota'].mean().plot(kind='bar',color='blue')
    plt.title('Rendimento médio em cada disciplina :')
    plt.xlabel('Disciplina:')
    plt.ylabel('media das notas:')
    plt.tight_layout()
    plt.savefig(grafico_path1)
    plt.clf()

    alunos = df['aluno'].unique()
    dados_aluno = {}
    for aluno in alunos:
        dados = df.loc[df['aluno']== aluno].to_html(classes='table table-bordered table-custom',index=False)
        dados_aluno [aluno] = dados

    tabela = df.to_html(classes='table table-bordered table-custom',index=False)

    return render_template('analise.html',media_aluno=media_aluno,media_disciplina=media_disciplina,
                           qtd_aprovados=qtd_aprovados,qtd_reprovados=qtd_reprovados,tabela=tabela,nome_arquivo=nome_arquivo,
                           grafico= 'grafico/graficos_media_alunos.png',grafico1 ='grafico/graficos_disciplina_media.png',
                           aprovacoes=aprovacoes,reprovacoes=reprovacoes,dados_aluno=dados_aluno
)

@app.route('/downloads/<tabela>')
def downloads(tabela):
    caminho = os.path.join('uploads',tabela)
    df = pd.read_csv(caminho)
    
    os.makedirs('downloads',exist_ok=True)

    nome_arquivo= tabela.rsplit('.', 1)[0] + '.xlsx'
   
    excel_path = os.path.join('downloads',nome_arquivo) 
    df.to_excel(excel_path,index=False)
    return send_file(excel_path,as_attachment=True)


            


if __name__ == "__main__":
    app.run(debug=True)