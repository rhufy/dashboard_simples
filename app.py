from flask import Flask, request, render_template, redirect,send_file
import pandas as pd
import os

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
    if 'situacao' in colunas :
        qtd_aprovados = df[df['situacao'] == 'aprovado'].shape[0]
        qtd_reprovados = df[df['situacao'] == 'reprovado'].shape[0]

    tabela = df.to_html(classes='table table-bordered table-custom',index=False)

    return render_template('analise.html',media_aluno=media_aluno,media_disciplina=media_disciplina,
                           qtd_aprovados=qtd_aprovados,qtd_reprovados=qtd_reprovados,tabela=tabela,nome_arquivo=nome_arquivo)

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