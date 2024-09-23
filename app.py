from flask import Flask, request,jsonify
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import requests

# Carrega as variáveis de ambiente do arquivo .cred (se disponível)
load_dotenv('.cred')

# Configurações para conexão com o banco de dados usando variáveis de ambiente
config = {
    'host': os.getenv('DB_HOST', 'localhost'),  # Obtém o host do banco de dados da variável de ambiente
    'user': os.getenv('DB_USER'),  # Obtém o usuário do banco de dados da variável de ambiente
    'password': os.getenv('DB_PASSWORD'),  # Obtém a senha do banco de dados da variável de ambiente
    'database': os.getenv('DB_NAME', 'db_estudo'),  # Obtém o nome do banco de dados da variável de ambiente
    'port': int(os.getenv('DB_PORT', 3306)),  # Obtém a porta do banco de dados da variável de ambiente
    'ssl_ca': os.getenv('SSL_CA_PATH')  # Caminho para o certificado SSL
}


# Função para conectar ao banco de dados
def connect_db():
    """Estabelece a conexão com o banco de dados usando as configurações fornecidas."""
    try:
        # Tenta estabelecer a conexão com o banco de dados usando mysql-connector-python
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            return conn
    except Error as err:
        # Em caso de erro, imprime a mensagem de erro
        print(f"Erro: {err}")
        return None


app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return {"status": "API em execução"}, 200

"""CLIENTES---------------------"""

@app.route('/clientes', methods=['GET'])
def listar_clientes():
    # Define a rota /clientes que responde a requisições HTTP do tipo GET
    # A função listar_clientes será executada quando esta rota for acessada.

    # Tenta conectar ao banco de dados
    conn = connect_db()

    # Verifica se a conexão ao banco de dados falhou
    if conn is None:
        # Se a conexão falhar, cria um dicionário de resposta com uma mensagem de erro
        resp = {"erro": "Erro ao conectar ao banco de dados"}
        # Retorna a resposta de erro com código de status 500 (Internal Server Error)
        return resp, 500

    # Cria um objeto cursor para executar consultas SQL no banco de dados
    # O parâmetro dictionary=True faz com que os resultados sejam retornados como dicionários
    cursor = conn.cursor(dictionary=True)

    # Define a consulta SQL para selecionar todos os registros da tabela tbl_clientes
    sql = "SELECT * from tbl_clientes"
    # Executa a consulta SQL no banco de dados
    cursor.execute(sql)

    # Obtém todos os resultados da consulta e armazena na variável results
    # Os resultados serão uma lista de dicionários, onde cada dicionário representa uma linha
    results = cursor.fetchall()

    # Fecha o cursor para liberar os recursos associados a ele
    cursor.close()
    # Fecha a conexão com o banco de dados para liberar os recursos
    conn.close()

    # Cria um dicionário de resposta onde a chave "clientes" contém os resultados da consulta
    resp = {
        "clientes": results
    }

    # Retorna a resposta JSON com a lista de clientes e código de status 200 (OK)
    return resp, 200

@app.route('/clientes', methods=['POST'])
def cria_clientes():
    # Define a rota /clientes que responde a requisições HTTP do tipo POST
    # A função cria_clientes será executada quando esta rota for acessada.

    # Tenta conectar ao banco de dados
    conn = connect_db()

    # Verifica se a conexão ao banco de dados falhou
    if conn is None:
        # Se a conexão falhar, cria um dicionário de resposta com uma mensagem de erro
        resp = {"erro": "Erro ao conectar ao banco de dados"}
        # Retorna a resposta de erro com código de status 500 (Internal Server Error)
        return resp, 500
    
    # Obtém os dados da requisição em formato JSON
    entrada_dados = request.json
    
    # Cria um objeto cursor para executar consultas SQL no banco de dados
    # O parâmetro dictionary=True faz com que os resultados sejam retornados como dicionários
    cursor = conn.cursor(dictionary=True)

    # Define a consulta SQL para inserir um novo cliente na tabela tbl_clientes
    sql = "INSERT INTO tbl_clientes (nome, email, cpf, senha) VALUES (%s, %s, %s, %s)"
    # Prepara os valores a serem inseridos, obtendo-os do dicionário entrada_dados
    values = (entrada_dados["nome"], entrada_dados["email"], entrada_dados["cpf"], entrada_dados["senha"])
    
    # Executa a consulta SQL de inserção no banco de dados
    cursor.execute(sql, values)
    # Confirma a transação para que as alterações sejam aplicadas ao banco de dados
    conn.commit()

    # Obtém o ID do cliente recém-criado usando lastrowid
    id = cursor.lastrowid

    # Cria uma resposta informando o sucesso da operação e o ID do novo cliente
    resp = f"O cliente {entrada_dados['nome']} com id {id} foi cadastrado com sucesso!"

    # Fecha o cursor para liberar os recursos associados a ele
    cursor.close()
    # Fecha a conexão com o banco de dados para liberar os recursos
    conn.close()
    
    # Retorna a resposta JSON com a mensagem de sucesso e código de status 201 (Created)
    return resp, 201

@app.route('/clientes/<int:id>', methods=['PUT'])
def atualiza_cliente(id):
    # Obtém os dados da nova entrada em formato JSON
    nova_entrada = request.json
    conn = connect_db()  # Conecta ao banco de dados

    if conn:
        cursor = conn.cursor()  # Cria um cursor para executar comandos SQL
        # Inicializa a consulta SQL
        sql = "UPDATE tbl_clientes SET "
        valores = []  # Lista para armazenar os novos valores
        updates = []  # Lista para armazenar as colunas a serem atualizadas

        # Verifica quais campos foram fornecidos e atualiza a consulta e valores
        if "nome" in nova_entrada:
            updates.append("nome = %s")
            valores.append(nova_entrada["nome"])
        if "email" in nova_entrada:
            updates.append("email = %s")
            valores.append(nova_entrada["email"])
        if "cpf" in nova_entrada:
            updates.append("cpf = %s")
            valores.append(nova_entrada["cpf"])
        if "senha" in nova_entrada:
            updates.append("senha = %s")
            valores.append(nova_entrada["senha"])

        # Se não houver campos para atualizar, retorna um erro
        if not updates:
            return {"erro": "Nenhum campo para atualizar"}, 400

        # Junta as partes da atualização e adiciona a condição WHERE
        sql += ", ".join(updates) + " WHERE id = %s"
        valores.append(id)  # Adiciona o ID à lista de valores

        try:
            # Executa o comando SQL com os valores fornecidos
            cursor.execute(sql, valores)
            # Confirma a transação no banco de dados
            conn.commit()
            # Verifica se alguma linha foi afetada (atualizada)
            if cursor.rowcount:
                print("Cliente atualizado com sucesso!")
            else:
                print("Cliente não encontrado!")
        except Error as err:
            # Em caso de erro na atualização, imprime a mensagem de erro
            print(f"Erro ao atualizar cliente: {err}")
        finally:
            # Fecha o cursor e a conexão para liberar recursos
            cursor.close()
            conn.close()

    resp = f"O cliente de id {id} foi atualizado com sucesso!"
    return resp, 200  # Retorna 200 OK

@app.route('/clientes/<int:id>', methods=['GET'])
def buscar_cliente_especifico(id):

    conn = connect_db()  # Conecta ao banco de dados
    if conn:
        cursor = conn.cursor(dictionary=True)  # Cria um cursor para executar comandos SQL
        sql = "SELECT * FROM tbl_clientes WHERE id = %s"  # Comando SQL para buscar um Livro pelo ID

        try:
            # Executa o comando SQL com o ID fornecido
            cursor.execute(sql, (id,))
            # Recupera o resultado da consulta
            cliente = cursor.fetchone()

        except Error as err:
            # Em caso de erro na busca, imprime a mensagem de erro
            print(f"Erro ao buscar cliente: {err}")
        finally:
            # Fecha o cursor e a conexão para liberar recursos
            cursor.close()
            conn.close()

    resp = {
        "cliente":cliente
    }
    return resp,200

@app.route('/clientes/<int:id>', methods=['DELETE'])
def deletar_cliente(id):
    conn = connect_db()  # Conecta ao banco de dados
    if conn:
        cursor = conn.cursor()  # Cria um cursor para executar comandos SQL
        sql = "DELETE FROM tbl_clientes WHERE id = %s"  # Comando SQL para deletar um Livro pelo ID

        try:
            # Executa o comando SQL com o ID fornecido
            cursor.execute(sql, (id,))
            # Confirma a transação no banco de dados
            conn.commit()
            # Verifica se alguma linha foi afetada (deletada)
            if cursor.rowcount:
                print("Cliente deletado com sucesso!")
            else:
                print("Cliente não encontrado!")
        except Error as err:
            # Em caso de erro na deleção, imprime a mensagem de erro
            print(f"Erro ao deletar Cliente: {err}")
        finally:
            # Fecha o cursor e a conexão para liberar recursos
            cursor.close()
            conn.close()
    resp = f"Cliente de id  {id} deletado com sucesso!"
    return resp,201

"""FORNECEDORES---------------------"""

@app.route('/fornecedores', methods=['GET'])
def listar_fornecedores():
    # Define a rota /fornecedores que responde a requisições HTTP do tipo GET
    # A função listar_fornecedores será executada quando esta rota for acessada.

    # Tenta conectar ao banco de dados
    conn = connect_db()

    # Verifica se a conexão ao banco de dados falhou
    if conn is None:
        # Se a conexão falhar, cria um dicionário de resposta com uma mensagem de erro
        resp = {"erro": "Erro ao conectar ao banco de dados"}
        # Retorna a resposta de erro com código de status 500 (Internal Server Error)
        return resp, 500

    # Cria um objeto cursor para executar consultas SQL no banco de dados
    # O parâmetro dictionary=True faz com que os resultados sejam retornados como dicionários
    cursor = conn.cursor(dictionary=True)

    # Define a consulta SQL para selecionar todos os registros da tabela tbl_fornecedores
    sql = "SELECT * from tbl_fornecedores"
    # Executa a consulta SQL no banco de dados
    cursor.execute(sql)

    # Obtém todos os resultados da consulta e armazena na variável results
    # Os resultados serão uma lista de dicionários, onde cada dicionário representa uma linha
    results = cursor.fetchall()

    # Fecha o cursor para liberar os recursos associados a ele
    cursor.close()
    # Fecha a conexão com o banco de dados para liberar os recursos
    conn.close()

    # Cria um dicionário de resposta onde a chave "fornecedores" contém os resultados da consulta
    resp = {
        "fornecedores": results
    }

    # Retorna a resposta JSON com a lista de fornecedores e código de status 200 (OK)
    return resp, 200

@app.route('/fornecedores', methods=['POST'])
def cria_fornecedores():
    # Define a rota /clientes que responde a requisições HTTP do tipo POST
    # A função cria_clientes será executada quando esta rota for acessada.

    # Tenta conectar ao banco de dados
    conn = connect_db()

    # Verifica se a conexão ao banco de dados falhou
    if conn is None:
        # Se a conexão falhar, cria um dicionário de resposta com uma mensagem de erro
        resp = {"erro": "Erro ao conectar ao banco de dados"}
        # Retorna a resposta de erro com código de status 500 (Internal Server Error)
        return resp, 500
    
    # Obtém os dados da requisição em formato JSON
    entrada_dados = request.json
    
    # Cria um objeto cursor para executar consultas SQL no banco de dados
    # O parâmetro dictionary=True faz com que os resultados sejam retornados como dicionários
    cursor = conn.cursor(dictionary=True)

    # Define a consulta SQL para inserir um novo cliente na tabela tbl_clientes
    sql = "INSERT INTO tbl_fornecedores (nome, email, cnpj) VALUES (%s, %s, %s)"
    # Prepara os valores a serem inseridos, obtendo-os do dicionário entrada_dados
    values = (entrada_dados["nome"], entrada_dados["email"], entrada_dados["cnpj"])
    
    # Executa a consulta SQL de inserção no banco de dados
    cursor.execute(sql, values)
    # Confirma a transação para que as alterações sejam aplicadas ao banco de dados
    conn.commit()

    # Obtém o ID do cliente recém-criado usando lastrowid
    id = cursor.lastrowid

    # Cria uma resposta informando o sucesso da operação e o ID do novo cliente
    resp = f"O fornecedor {entrada_dados['nome']} com id {id} foi cadastrado com sucesso!"

    # Fecha o cursor para liberar os recursos associados a ele
    cursor.close()
    # Fecha a conexão com o banco de dados para liberar os recursos
    conn.close()
    
    # Retorna a resposta JSON com a mensagem de sucesso e código de status 201 (Created)
    return resp, 201

@app.route('/fornecedores/<int:id>', methods=['PUT'])
def atualiza_fornecedor(id):
    # Obtém os dados da nova entrada em formato JSON
    nova_entrada = request.json
    conn = connect_db()  # Conecta ao banco de dados

    if conn:
        cursor = conn.cursor()  # Cria um cursor para executar comandos SQL
        # Inicializa a consulta SQL
        sql = "UPDATE tbl_fornecedores SET "
        valores = []  # Lista para armazenar os novos valores
        updates = []  # Lista para armazenar as colunas a serem atualizadas

        # Verifica quais campos foram fornecidos e atualiza a consulta e valores
        if "nome" in nova_entrada:
            updates.append("nome = %s")
            valores.append(nova_entrada["nome"])
        if "email" in nova_entrada:
            updates.append("email = %s")
            valores.append(nova_entrada["email"])
        if "cnpj" in nova_entrada:
            updates.append("cnpj = %s")
            valores.append(nova_entrada["cnpj"])

        # Se não houver campos para atualizar, retorna um erro
        if not updates:
            return {"erro": "Nenhum campo para atualizar"}, 400

        # Junta as partes da atualização e adiciona a condição WHERE
        sql += ", ".join(updates) + " WHERE id = %s"
        valores.append(id)  # Adiciona o ID à lista de valores

        try:
            # Executa o comando SQL com os valores fornecidos
            cursor.execute(sql, valores)
            # Confirma a transação no banco de dados
            conn.commit()
            # Verifica se alguma linha foi afetada (atualizada)
            if cursor.rowcount:
                print("fornecedor atualizado com sucesso!")
            else:
                print("fornecedor não encontrado!")
        except Error as err:
            # Em caso de erro na atualização, imprime a mensagem de erro
            print(f"Erro ao atualizar fornecedor: {err}")
        finally:
            # Fecha o cursor e a conexão para liberar recursos
            cursor.close()
            conn.close()

    resp = f"O fornecedor de id {id} foi atualizado com sucesso!"
    return resp, 200  # Retorna 200 OK

@app.route('/fornecedores/<int:id>', methods=['GET'])
def buscar_fornecedor_especifico(id):
    conn = connect_db()  # Conecta ao banco de dados
    if conn:
        cursor = conn.cursor(dictionary=True)  # Cria um cursor para executar comandos SQL
        sql = "SELECT * FROM tbl_fornecedores WHERE id = %s"  # Comando SQL para buscar um Livro pelo ID

        try:
            # Executa o comando SQL com o ID fornecido
            cursor.execute(sql, (id,))
            # Recupera o resultado da consulta
            fornecedor = cursor.fetchone()

        except Error as err:
            # Em caso de erro na busca, imprime a mensagem de erro
            print(f"Erro ao buscar fornecedor: {err}")
        finally:
            # Fecha o cursor e a conexão para liberar recursos
            cursor.close()
            conn.close()

    if fornecedor:
        return jsonify({"fornecedor": fornecedor}), 200
    else:
        return jsonify({"erro": "Fornecedor não encontrado"}), 404

@app.route('/fornecedores/<int:id>', methods=['DELETE'])
def deletar_fornecedor(id):
    conn = connect_db()  # Conecta ao banco de dados
    if conn:
        cursor = conn.cursor()  # Cria um cursor para executar comandos SQL
        sql = "DELETE FROM tbl_fornecedores WHERE id = %s"  # Comando SQL para deletar um Livro pelo ID

        try:
            # Executa o comando SQL com o ID fornecido
            cursor.execute(sql, (id,))
            # Confirma a transação no banco de dados
            conn.commit()
            # Verifica se alguma linha foi afetada (deletada)
            if cursor.rowcount:
                print("Fornecedor deletado com sucesso!")
            else:
                print("Fornecedor não encontrado!")
        except Error as err:
            # Em caso de erro na deleção, imprime a mensagem de erro
            print(f"Erro ao deletar Fornecedor: {err}")
        finally:
            # Fecha o cursor e a conexão para liberar recursos
            cursor.close()
            conn.close()
    resp = f"Fornecedor de id  {id} deletado com sucesso!"
    return resp,201

"""PRODUTOS---------------------"""

@app.route('/produtos', methods=['GET'])
def listar_produtos():
    # Define a rota /fornecedores que responde a requisições HTTP do tipo GET
    # A função listar_fornecedores será executada quando esta rota for acessada.

    # Tenta conectar ao banco de dados
    conn = connect_db()

    # Verifica se a conexão ao banco de dados falhou
    if conn is None:
        # Se a conexão falhar, cria um dicionário de resposta com uma mensagem de erro
        resp = {"erro": "Erro ao conectar ao banco de dados"}
        # Retorna a resposta de erro com código de status 500 (Internal Server Error)
        return resp, 500

    # Cria um objeto cursor para executar consultas SQL no banco de dados
    # O parâmetro dictionary=True faz com que os resultados sejam retornados como dicionários
    cursor = conn.cursor(dictionary=True)

    # Define a consulta SQL para selecionar todos os registros da tabela tbl_fornecedores
    sql = "SELECT * from tbl_produtos"
    # Executa a consulta SQL no banco de dados
    cursor.execute(sql)

    # Obtém todos os resultados da consulta e armazena na variável results
    # Os resultados serão uma lista de dicionários, onde cada dicionário representa uma linha
    results = cursor.fetchall()

    # Fecha o cursor para liberar os recursos associados a ele
    cursor.close()
    # Fecha a conexão com o banco de dados para liberar os recursos
    conn.close()

    # Cria um dicionário de resposta onde a chave "fornecedores" contém os resultados da consulta
    resp = {
        "produtos": results
    }

    # Retorna a resposta JSON com a lista de fornecedores e código de status 200 (OK)
    return resp, 200

@app.route('/produtos', methods=['POST'])
def cria_produtos():
    # Define a rota /clientes que responde a requisições HTTP do tipo POST
    # A função cria_clientes será executada quando esta rota for acessada.

    # Tenta conectar ao banco de dados
    conn = connect_db()

    # Verifica se a conexão ao banco de dados falhou
    if conn is None:
        # Se a conexão falhar, cria um dicionário de resposta com uma mensagem de erro
        resp = {"erro": "Erro ao conectar ao banco de dados"}
        # Retorna a resposta de erro com código de status 500 (Internal Server Error)
        return resp, 500
    
    # Obtém os dados da requisição em formato JSON
    entrada_dados = request.json
    
    # Cria um objeto cursor para executar consultas SQL no banco de dados
    # O parâmetro dictionary=True faz com que os resultados sejam retornados como dicionários
    cursor = conn.cursor(dictionary=True)

    # Define a consulta SQL para inserir um novo cliente na tabela tbl_clientes
    sql = "INSERT INTO tbl_produtos (nome, descricao, preco, qtd_em_estoque, fornecedor_id, custo_no_fornecedor) VALUES (%s, %s, %s,%s,%s,%s)"
    # Prepara os valores a serem inseridos, obtendo-os do dicionário entrada_dados
    values = (entrada_dados["nome"], entrada_dados["descricao"], entrada_dados["preco"], entrada_dados["qtd_em_estoque"], entrada_dados["fornecedor_id"], entrada_dados["custo_no_fornecedor"])
    
    # Executa a consulta SQL de inserção no banco de dados
    cursor.execute(sql, values)
    # Confirma a transação para que as alterações sejam aplicadas ao banco de dados
    conn.commit()

    # Obtém o ID do cliente recém-criado usando lastrowid
    id = cursor.lastrowid

    # Cria uma resposta informando o sucesso da operação e o ID do novo cliente
    resp = f"O produto {entrada_dados['nome']} de id {id} foi cadastrado com sucesso!"

    # Fecha o cursor para liberar os recursos associados a ele
    cursor.close()
    # Fecha a conexão com o banco de dados para liberar os recursos
    conn.close()
    
    # Retorna a resposta JSON com a mensagem de sucesso e código de status 201 (Created)
    return resp, 201

@app.route('/produtos/<int:id>', methods=['PUT'])
def atualiza_produtos(id):
    # Obtém os dados da nova entrada em formato JSON
    nova_entrada = request.json
    conn = connect_db()  # Conecta ao banco de dados

    if conn:
        cursor = conn.cursor()  # Cria um cursor para executar comandos SQL
        # Inicializa a consulta SQL
        sql = "UPDATE tbl_produtos SET "
        valores = []  # Lista para armazenar os novos valores
        updates = []  # Lista para armazenar as colunas a serem atualizadas

        # Verifica quais campos foram fornecidos e atualiza a consulta e valores
        if "nome" in nova_entrada:
            updates.append("nome = %s")
            valores.append(nova_entrada["nome"])
        if "descricao" in nova_entrada:
            updates.append("descricao = %s")
            valores.append(nova_entrada["descricao"])
        if "preco" in nova_entrada:
            updates.append("preco = %s")
            valores.append(nova_entrada["preco"])
        if "qtd_em_estoque" in nova_entrada:
            updates.append("qtd_em_estoque = %s")
            valores.append(nova_entrada["qtd_em_estoque"])
        if "fornecedor_id" in nova_entrada:
            updates.append("fornecedor_id = %s")
            valores.append(nova_entrada["fornecedor_id"])
        if "custo_no_fornecedor" in nova_entrada:
            updates.append("custo_no_fornecedor = %s")
            valores.append(nova_entrada["custo_no_fornecedor"])
    
        # Se não houver campos para atualizar, retorna um erro
        if not updates:
            return {"erro": "Nenhum campo para atualizar"}, 400

        # Junta as partes da atualização e adiciona a condição WHERE
        sql += ", ".join(updates) + " WHERE id = %s"
        valores.append(id)  # Adiciona o ID à lista de valores

        try:
            # Executa o comando SQL com os valores fornecidos
            cursor.execute(sql, valores)
            # Confirma a transação no banco de dados
            conn.commit()
            # Verifica se alguma linha foi afetada (atualizada)
            if cursor.rowcount:
                print("Produto atualizado com sucesso!")
            else:
                print("Produto não encontrado!")
        except Error as err:
            # Em caso de erro na atualização, imprime a mensagem de erro
            print(f"Erro ao atualizar produto: {err}")
        finally:
            # Fecha o cursor e a conexão para liberar recursos
            cursor.close()
            conn.close()

    resp = f"O produto de id {id} foi atualizado com sucesso!"
    return resp, 200  # Retorna 200 OK

@app.route('/produtos/<int:id>', methods=['GET'])
def buscar_produtos_especifico(id):
    conn = connect_db()  # Conecta ao banco de dados
    if conn:
        cursor = conn.cursor(dictionary=True)  # Cria um cursor para executar comandos SQL
        sql = "SELECT * FROM tbl_produtos WHERE id = %s"  # Comando SQL para buscar um Livro pelo ID

        try:
            # Executa o comando SQL com o ID fornecido
            cursor.execute(sql, (id,))
            # Recupera o resultado da consulta
            produto = cursor.fetchone()

        except Error as err:
            # Em caso de erro na busca, imprime a mensagem de erro
            print(f"Erro ao buscar produto: {err}")
        finally:
            # Fecha o cursor e a conexão para liberar recursos
            cursor.close()
            conn.close()

    resp = {
        "produto":produto
    }
    return resp,200

@app.route('/produtos/<int:id>', methods=['DELETE'])
def deletar_produto(id):
    conn = connect_db()  # Conecta ao banco de dados
    if conn:
        cursor = conn.cursor()  # Cria um cursor para executar comandos SQL
        sql = "DELETE FROM tbl_produtos WHERE id = %s"  # Comando SQL para deletar um Livro pelo ID

        try:
            # Executa o comando SQL com o ID fornecido
            cursor.execute(sql, (id,))
            # Confirma a transação no banco de dados
            conn.commit()
            # Verifica se alguma linha foi afetada (deletada)
            if cursor.rowcount:
                print("Produto deletado com sucesso!")
            else:
                print("Produto não encontrado!")
        except Error as err:
            # Em caso de erro na deleção, imprime a mensagem de erro
            print(f"Erro ao deletar Produto: {err}")
        finally:
            # Fecha o cursor e a conexão para liberar recursos
            cursor.close()
            conn.close()
    resp = f"Produto de id  {id} deletado com sucesso!"
    return resp,201

"""CARRINHOS---------------------"""

@app.route('/carrinhos', methods=['POST'])
def adiciona_item_carrinho():
    # Tenta conectar ao banco de dados
    conn = connect_db()

    # Verifica se a conexão ao banco de dados falhou
    if conn is None:
        return {"erro": "Erro ao conectar ao banco de dados"}, 500

    # Obtém os dados da requisição em formato JSON
    entrada_dados = request.json
    produto_id = entrada_dados["produto_id"]
    quantidade_demandada = entrada_dados["quantidade"]
    cliente_id = entrada_dados["cliente_id"]

    # Cria um objeto cursor
    cursor = conn.cursor(dictionary=True)

        # Verifica se o cliente existe
    cursor.execute("SELECT id FROM tbl_clientes WHERE id = %s", (cliente_id,))
    cliente = cursor.fetchone()

    if cliente is None:
        cursor.close()
        conn.close()
        return {"erro": "Cliente não encontrado"}, 404

    # Verifica se o produto existe e se a quantidade está disponível
    cursor.execute("SELECT qtd_em_estoque FROM tbl_produtos WHERE id = %s", (produto_id,))
    produto = cursor.fetchone()

    if produto is None:
        cursor.close()
        conn.close()
        return {"erro": "Produto não encontrado"}, 404

    estoque_disponivel = produto['qtd_em_estoque']
    if quantidade_demandada > estoque_disponivel:
        cursor.close()
        conn.close()
        return {"erro": "Quantidade solicitada não disponível"}, 400

    # Se o produto existe e a quantidade está disponível, insere no carrinho
    sql = "INSERT INTO tbl_carrinho (produto_id, quantidade, cliente_id) VALUES (%s, %s,%s)"
    values = (produto_id, quantidade_demandada,cliente_id)

    cursor.execute(sql, values)
    conn.commit()

    id = cursor.lastrowid
    cursor.close()
    conn.close()

    return f"O produto {produto_id} foi adicionado ao carrinho de id {id}, que pertence ao cliente de id {cliente_id}", 201

@app.route('/carrinhos', methods=['GET'])
def listar_carrinhos():
    # Define a rota /fornecedores que responde a requisições HTTP do tipo GET
    # A função listar_fornecedores será executada quando esta rota for acessada.

    # Tenta conectar ao banco de dados
    conn = connect_db()

    # Verifica se a conexão ao banco de dados falhou
    if conn is None:
        # Se a conexão falhar, cria um dicionário de resposta com uma mensagem de erro
        resp = {"erro": "Erro ao conectar ao banco de dados"}
        # Retorna a resposta de erro com código de status 500 (Internal Server Error)
        return resp, 500

    # Cria um objeto cursor para executar consultas SQL no banco de dados
    # O parâmetro dictionary=True faz com que os resultados sejam retornados como dicionários
    cursor = conn.cursor(dictionary=True)

    # Define a consulta SQL para selecionar todos os registros da tabela tbl_fornecedores
    sql = "SELECT * from tbl_carrinho"
    # Executa a consulta SQL no banco de dados
    cursor.execute(sql)

    # Obtém todos os resultados da consulta e armazena na variável results
    # Os resultados serão uma lista de dicionários, onde cada dicionário representa uma linha
    results = cursor.fetchall()

    # Fecha o cursor para liberar os recursos associados a ele
    cursor.close()
    # Fecha a conexão com o banco de dados para liberar os recursos
    conn.close()

    # Cria um dicionário de resposta onde a chave "fornecedores" contém os resultados da consulta
    resp = {
        "carrinhos": results
    }

    # Retorna a resposta JSON com a lista de fornecedores e código de status 200 (OK)
    return resp, 200

@app.route('/carrinhos/<int:id>', methods=['PUT'])
def atualiza_carrinhos(id):
    # Obtém os dados da nova entrada em formato JSON
    nova_entrada = request.json
    conn = connect_db()  # Conecta ao banco de dados

    if conn:
        cursor = conn.cursor()  # Cria um cursor para executar comandos SQL
        # Inicializa a consulta SQL
        sql = "UPDATE tbl_carrinho SET "
        valores = []  # Lista para armazenar os novos valores
        updates = []  # Lista para armazenar as colunas a serem atualizadas

        # Verifica quais campos foram fornecidos e atualiza a consulta e valores
        if "produto_id" in nova_entrada:
            updates.append("produto_id = %s")
            valores.append(nova_entrada["produto_id"])
        if "quantidade" in nova_entrada:
            updates.append("quantidade = %s")
            valores.append(nova_entrada["quantidade"])
    
        # Se não houver campos para atualizar, retorna um erro
        if not updates:
            return {"erro": "Nenhum campo para atualizar"}, 400

        # Junta as partes da atualização e adiciona a condição WHERE
        sql += ", ".join(updates) + " WHERE id = %s"
        valores.append(id)  # Adiciona o ID à lista de valores

        try:
            # Executa o comando SQL com os valores fornecidos
            cursor.execute(sql, valores)
            # Confirma a transação no banco de dados
            conn.commit()
            # Verifica se alguma linha foi afetada (atualizada)
            if cursor.rowcount:
                print("Carrinho atualizado com sucesso!")
            else:
                print("Carrinho não encontrado!")
        except Error as err:
            # Em caso de erro na atualização, imprime a mensagem de erro
            print(f"Erro ao atualizar carrinho: {err}")
        finally:
            # Fecha o cursor e a conexão para liberar recursos
            cursor.close()
            conn.close()

    resp = f"O carrinho de id {id} foi atualizado com sucesso!"
    return resp, 200  # Retorna 200 OK

@app.route('/carrinhos/<int:id>', methods=['DELETE'])
def deletar_carrinho(id):
    conn = connect_db()  # Conecta ao banco de dados
    if conn:
        cursor = conn.cursor()  # Cria um cursor para executar comandos SQL
        sql = "DELETE FROM tbl_carrinho WHERE id = %s"  # Comando SQL para deletar um Livro pelo ID

        try:
            # Executa o comando SQL com o ID fornecido
            cursor.execute(sql, (id,))
            # Confirma a transação no banco de dados
            conn.commit()
            # Verifica se alguma linha foi afetada (deletada)
            if cursor.rowcount:
                print("Carrinho deletado com sucesso!")
            else:
                print("Carrinho não encontrado!")
        except Error as err:
            # Em caso de erro na deleção, imprime a mensagem de erro
            print(f"Erro ao deletar carrinho: {err}")
        finally:
            # Fecha o cursor e a conexão para liberar recursos
            cursor.close()
            conn.close()
    resp = f"O carrinho de id {id} deletado com sucesso!"
    return resp,201

@app.route('/carrinhos/<int:id>', methods=['GET'])
def buscar_carrinhos_especifico(id):
    conn = connect_db()  # Conecta ao banco de dados
    if conn:
        cursor = conn.cursor(dictionary=True)  # Cria um cursor para executar comandos SQL
        sql = "SELECT * FROM tbl_carrinho WHERE id = %s"  # Comando SQL para buscar um Livro pelo ID

        try:
            # Executa o comando SQL com o ID fornecido
            cursor.execute(sql, (id,))
            # Recupera o resultado da consulta
            carrinho = cursor.fetchone()

        except Error as err:
            # Em caso de erro na busca, imprime a mensagem de erro
            print(f"Erro ao buscar carrinho: {err}")
        finally:
            # Fecha o cursor e a conexão para liberar recursos
            cursor.close()
            conn.close()

    resp = {
        "carrinho":carrinho
    }
    return resp,200

@app.route('/carrinhos/cliente/<int:cliente_id>', methods=['GET'])
def lista_carrinhos_do_cliente(cliente_id):
    conn = connect_db()  # Conecta ao banco de dados
    if conn:
        cursor = conn.cursor(dictionary=True)  # Cria um cursor para executar comandos SQL
        sql = """
        SELECT carrinho.id AS carrinho_id, carrinho.produto_id AS produto_id, carrinho.quantidade AS quantidade
        FROM tbl_carrinho carrinho
        JOIN tbl_clientes clientes ON carrinho.cliente_id = clientes.id
        WHERE clientes.id = %s
        """  

        try:
            # Executa o comando SQL com o ID fornecido
            cursor.execute(sql, (cliente_id,))
            # Recupera todos os resultados da consulta
            carrinhos = cursor.fetchall()  # Use fetchall para obter todos os carrinhos do cliente

        except Error as err:
            print(f"Erro ao buscar carrinhos: {err}")
            return {"erro": "Erro ao buscar carrinhos"}, 500
        finally:
            cursor.close()
            conn.close()

        resp = {
            "carrinhos": carrinhos  # Retorna todos os carrinhos encontrados
        }
        return resp, 200

    return {"erro": "Erro ao conectar ao banco de dados"}, 500

"""PEDIDOS---------------------"""

@app.route('/pedidos', methods=['GET'])
def listar_pedidos():
    # Define a rota /fornecedores que responde a requisições HTTP do tipo GET
    # A função listar_fornecedores será executada quando esta rota for acessada.

    # Tenta conectar ao banco de dados
    conn = connect_db()

    # Verifica se a conexão ao banco de dados falhou
    if conn is None:
        # Se a conexão falhar, cria um dicionário de resposta com uma mensagem de erro
        resp = {"erro": "Erro ao conectar ao banco de dados"}
        # Retorna a resposta de erro com código de status 500 (Internal Server Error)
        return resp, 500

    # Cria um objeto cursor para executar consultas SQL no banco de dados
    # O parâmetro dictionary=True faz com que os resultados sejam retornados como dicionários
    cursor = conn.cursor(dictionary=True)

    # Define a consulta SQL para selecionar todos os registros da tabela tbl_fornecedores
    sql = "SELECT * from tbl_pedido"
    # Executa a consulta SQL no banco de dados
    cursor.execute(sql)

    # Obtém todos os resultados da consulta e armazena na variável results
    # Os resultados serão uma lista de dicionários, onde cada dicionário representa uma linha
    results = cursor.fetchall()

    # Fecha o cursor para liberar os recursos associados a ele
    cursor.close()
    # Fecha a conexão com o banco de dados para liberar os recursos
    conn.close()

    # Cria um dicionário de resposta onde a chave "fornecedores" contém os resultados da consulta
    resp = {
        "pedidos": results
    }

    # Retorna a resposta JSON com a lista de fornecedores e código de status 200 (OK)
    return resp, 200

@app.route('/pedidos', methods=['POST'])
def cria_pedidos():
    # Define a rota /clientes que responde a requisições HTTP do tipo POST
    # A função cria_clientes será executada quando esta rota for acessada.

    # Tenta conectar ao banco de dados
    conn = connect_db()

    # Verifica se a conexão ao banco de dados falhou
    if conn is None:
        # Se a conexão falhar, cria um dicionário de resposta com uma mensagem de erro
        resp = {"erro": "Erro ao conectar ao banco de dados"}
        # Retorna a resposta de erro com código de status 500 (Internal Server Error)
        return resp, 500
    
    # Obtém os dados da requisição em formato JSON
    entrada_dados = request.json
    
    cliente_id = entrada_dados["cliente_id"]
    carrinho_id=entrada_dados["carrinho_id"]
    data_hora = entrada_dados["data_hora"]
    status=entrada_dados["status"]

    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM tbl_clientes WHERE id = %s",(cliente_id,))
    cliente = cursor.fetchone()

    if cliente is None:
        cursor.close()
        conn.close()
        return {"erro": "Cliente não encontrado"}, 404

    cursor.execute("SELECT id FROM tbl_carrinho WHERE id = %s",(carrinho_id,))
    carrinho = cursor.fetchone()

    if carrinho is None:
        cursor.close()
        conn.close()
        return {"erro": "Carrinho não encontrado"}, 404
    
    sql = "INSERT INTO tbl_pedido (cliente_id,carrinho_id,data_hora,status) VALUES (%s,%s,%s,%s)"
    # Prepara os valores a serem inseridos, obtendo-os do dicionário entrada_dados
    values = (cliente_id,carrinho_id,data_hora,status)
    
    # Executa a consulta SQL de inserção no banco de dados
    cursor.execute(sql, values)
    # Confirma a transação para que as alterações sejam aplicadas ao banco de dados
    conn.commit()

    # Obtém o ID do cliente recém-criado usando lastrowid
    id = cursor.lastrowid

    # Cria uma resposta informando o sucesso da operação e o ID do novo cliente

    # Fecha o cursor para liberar os recursos associados a ele
    cursor.close()
    # Fecha a conexão com o banco de dados para liberar os recursos
    conn.close()
    
    resp = f"O pedido de id {id} foi cadastrado com sucesso!"
    # Retorna a resposta JSON com a mensagem de sucesso e código de status 201 (Created)
    return resp, 201



if __name__ == '__main__':
    app.run(debug=True)