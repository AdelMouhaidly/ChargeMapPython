import random
import requests
import webbrowser
import cx_Oracle
from colorama import Fore, Style, init
import json

init(autoreset=True)

dsn_tns = cx_Oracle.makedsn("oracle.fiap.com.br", "1521", service_name="ORCL")
conexao = cx_Oracle.connect(user="rm558485", password="221005", dsn=dsn_tns)

def exportar_endereco_json(endereco, cep):
    try:
        dados_endereco = {
            "cep": cep,
            "logradouro": endereco['logradouro'],
            "bairro": endereco['bairro'],
            "localidade": endereco['localidade'],
            "uf": endereco['uf']
        }

        with open(f'endereco_{cep}.json', 'w', encoding='utf-8') as f:
            json.dump(dados_endereco, f, ensure_ascii=False, indent=4)

        print(f"{Fore.GREEN}Informações exportadas com sucesso para 'endereco_{cep}.json'.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Erro ao exportar informações para JSON: {e}{Style.RESET_ALL}")

def cadastrar_usuario():
    print(f"\n{Fore.GREEN}--- Cadastro de Usuário ---{Style.RESET_ALL}")
    nome = input(f"{Fore.CYAN}Digite seu nome completo: {Style.RESET_ALL}").strip()
    email = input(f"{Fore.CYAN}Digite seu email: {Style.RESET_ALL}").strip()
    senha = input(f"{Fore.CYAN}Digite sua senha: {Style.RESET_ALL}").strip()

    try:
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha) VALUES (:nome, :email, :senha)",
            {"nome": nome, "email": email, "senha": senha},
        )
        conexao.commit()
        print(f"{Fore.GREEN}Usuário cadastrado com sucesso!{Style.RESET_ALL}")
    except cx_Oracle.IntegrityError:
        print(f"{Fore.RED}Erro: Este email já está cadastrado. Tente outro.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Erro ao cadastrar usuário: {e}{Style.RESET_ALL}")

def listar_usuarios():
    print(f"\n{Fore.BLUE}--- Lista de Usuários ---{Style.RESET_ALL}")
    try:
        cursor = conexao.cursor()
        cursor.execute("SELECT id_usuario, nome, email FROM usuarios")
        usuarios = cursor.fetchall()
        if not usuarios:
            print(f"{Fore.RED}Nenhum usuário cadastrado.{Style.RESET_ALL}")
            return
        for usuario in usuarios:
            print(f"ID: {usuario[0]}, Nome: {usuario[1]}, Email: {usuario[2]}")
    except Exception as e:
        print(f"{Fore.RED}Erro ao listar usuários: {e}{Style.RESET_ALL}")

def atualizar_usuario():
    listar_usuarios()
    user_id = input(f"\n{Fore.CYAN}Digite o ID do usuário que deseja atualizar: {Style.RESET_ALL}").strip()
    nome = input(f"{Fore.CYAN}Novo nome (deixe vazio para não alterar): {Style.RESET_ALL}").strip()
    email = input(f"{Fore.CYAN}Novo email (deixe vazio para não alterar): {Style.RESET_ALL}").strip()
    senha = input(f"{Fore.CYAN}Nova senha (deixe vazio para não alterar): {Style.RESET_ALL}").strip()

    try:
        cursor = conexao.cursor()
        if nome:
            cursor.execute("UPDATE usuarios SET nome = :nome WHERE id_usuario = :id", {"nome": nome, "id": user_id})
        if email:
            cursor.execute("UPDATE usuarios SET email = :email WHERE id_usuario = :id", {"email": email, "id": user_id})
        if senha:
            cursor.execute("UPDATE usuarios SET senha = :senha WHERE id_usuario = :id", {"senha": senha, "id": user_id})
        conexao.commit()
        print(f"{Fore.GREEN}Usuário atualizado com sucesso!{Style.RESET_ALL}")
    except cx_Oracle.IntegrityError:
        print(f"{Fore.RED}Erro: O email informado já está em uso.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Erro ao atualizar usuário: {e}{Style.RESET_ALL}")

def deletar_usuario():
    listar_usuarios()
    user_id = input(f"\n{Fore.CYAN}Digite o ID do usuário que deseja deletar: {Style.RESET_ALL}").strip()

    try:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id_usuario = :id", {"id": user_id})
        conexao.commit()
        print(f"{Fore.GREEN}Usuário deletado com sucesso!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Erro ao deletar usuário: {e}{Style.RESET_ALL}")

def login_usuario():
    print(f"\n{Fore.BLUE}--- Login de Usuário ---{Style.RESET_ALL}")
    email = input(f"{Fore.CYAN}Digite seu email: {Style.RESET_ALL}").strip()
    senha = input(f"{Fore.CYAN}Digite sua senha: {Style.RESET_ALL}").strip()

    try:
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT nome FROM usuarios WHERE email = :email AND senha = :senha",
            {"email": email, "senha": senha},
        )
        resultado = cursor.fetchone()
        if resultado:
            print(f"{Fore.GREEN}Bem-vindo, {resultado[0]}!{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Email ou senha incorretos. Tente novamente.{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Erro ao realizar login: {e}{Style.RESET_ALL}")
        return False

def tela_login_cadastro():
    while True:
        print(f"\n{Style.BRIGHT}--- ChargeMap ---")
        print(f"{Fore.BLUE}1. Login")
        print(f"{Fore.GREEN}2. Cadastro")
        print(f"{Fore.YELLOW}3. Gerenciar Usuários (CRUD)")
        print(f"{Fore.RED}4. Sair")

        opcao = input(f"\n{Fore.CYAN}Escolha uma opção: {Style.RESET_ALL}").strip()

        if opcao == "1":
            if login_usuario():
                return True
        elif opcao == "2":
            cadastrar_usuario()
        elif opcao == "3":
            gerenciar_usuarios()
        elif opcao == "4":
            print(f"{Fore.RED}Saindo do sistema. Até logo!{Style.RESET_ALL}")
            exit()
        else:
            print(f"{Fore.RED}Opção inválida. Tente novamente.{Style.RESET_ALL}")

def gerenciar_usuarios():
    while True:
        print(f"\n{Style.BRIGHT}--- Gerenciamento de Usuários ---")
        print(f"{Fore.BLUE}1. Listar Usuários")
        print(f"{Fore.CYAN}2. Atualizar Usuário")
        print(f"{Fore.RED}3. Deletar Usuário")
        print(f"{Fore.YELLOW}4. Voltar")

        opcao = input(f"\n{Fore.CYAN}Escolha uma opção: {Style.RESET_ALL}").strip()

        if opcao == "1":
            listar_usuarios()
        elif opcao == "2":
            atualizar_usuario()
        elif opcao == "3":
            deletar_usuario()
        elif opcao == "4":
            break
        else:
            print(f"{Fore.RED}Opção inválida. Tente novamente.{Style.RESET_ALL}")

def obter_endereco_cep(cep):
    url = f"https://viacep.com.br/ws/{cep}/json/"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados = resposta.json()
        if 'erro' not in dados:
            return dados
        else:
            print(f"{Fore.RED}Erro: CEP não encontrado.{Style.RESET_ALL}")
            return None
    else:
        print(f"{Fore.RED}Erro ao acessar a API de CEP.{Style.RESET_ALL}")
        return None

def encontrar_pontos_carregamento():
    cep = input(f"{Fore.CYAN}Digite seu CEP: {Style.RESET_ALL}").strip()

    endereco = obter_endereco_cep(cep)
    if endereco is None:
        return

    print(f"\n{Fore.GREEN}Endereço encontrado:{Style.RESET_ALL}")
    print(f"Rua: {endereco['logradouro']}, Bairro: {endereco['bairro']}")
    print(f"Cidade: {endereco['localidade']}, Estado: {endereco['uf']}")

    exportar_endereco_json(endereco, cep)

    google_maps_url = f"https://www.google.com/maps/search/carregadores+de+veiculos+elétricos+perto+de+{endereco['logradouro']}+{endereco['localidade']}"
    webbrowser.open(google_maps_url)

def reservar_carregador():
    cep = input(f"{Fore.CYAN}Digite seu CEP: {Style.RESET_ALL}").strip()

    endereco = obter_endereco_cep(cep)
    if endereco is None:
        return

    print(f"\n{Fore.GREEN}Endereço encontrado:{Style.RESET_ALL}")
    print(f"Rua: {endereco['logradouro']}, Bairro: {endereco['bairro']}")
    print(f"Cidade: {endereco['localidade']}, Estado: {endereco['uf']}")

    locais = [
        "Ponto de Carregamento - Centro",
        "Ponto de Carregamento - Shopping X",
        "Ponto de Carregamento - Rua das Flores",
        "Ponto de Carregamento - Avenida Principal"
    ]
    
    print(f"\n{Fore.BLUE}Locais de carregamento próximos:{Style.RESET_ALL}")
    for i, local in enumerate(locais, start=1):
        print(f"{i}. {local}")

    escolha = input(f"\n{Fore.CYAN}Escolha o ponto de carregamento (1-4): {Style.RESET_ALL}").strip()
    try:
        escolha = int(escolha)
        if escolha < 1 or escolha > 4:
            print(f"{Fore.RED}Opção inválida. Tente novamente.{Style.RESET_ALL}")
            return
    except ValueError:
        print(f"{Fore.RED}Entrada inválida. Tente novamente.{Style.RESET_ALL}")
        return

    local_escolhido = locais[escolha - 1]
    print(f"\n{Fore.GREEN}Você escolheu: {local_escolhido}{Style.RESET_ALL}")
    
    dias_disponiveis = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"]
    horarios_disponiveis = ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]

    print(f"\n{Fore.BLUE}Dias e horários disponíveis para reserva:{Style.RESET_ALL}")
    horarios_por_dia = {}
    for dia in dias_disponiveis:
        horarios_por_dia[dia] = random.sample(horarios_disponiveis, k=4)
    
    for dia, horarios in horarios_por_dia.items():
        print(f"{dia}:")
        for i, horario in enumerate(horarios, 1):
            print(f"  {i}. {horario}")

    escolha_dia = input(f"\n{Fore.CYAN}Escolha o dia para reserva (ex: Segunda-feira): {Style.RESET_ALL}").strip()
    if escolha_dia not in dias_disponiveis:
        print(f"{Fore.RED}Dia inválido. Tente novamente.{Style.RESET_ALL}")
        return

    escolha_horario = input(f"{Fore.CYAN}Escolha o horário para reserva (ex: 1 para {horarios_por_dia[escolha_dia][0]}): {Style.RESET_ALL}").strip()
    try:
        escolha_horario = int(escolha_horario)
        if escolha_horario < 1 or escolha_horario > len(horarios_por_dia[escolha_dia]):
            print(f"{Fore.RED}Opção inválida. Tente novamente.{Style.RESET_ALL}")
            return
    except ValueError:
        print(f"{Fore.RED}Entrada inválida. Tente novamente.{Style.RESET_ALL}")
        return
    
    horario_escolhido = horarios_por_dia[escolha_dia][escolha_horario - 1]
    print(f"{Fore.GREEN}Reserva confirmada para {escolha_dia} às {horario_escolhido}!{Style.RESET_ALL}")

def estimar_tempo_carregamento():
    porcentagem_bateria = float(input(f"{Fore.CYAN}Digite a porcentagem de bateria restante (0-100): {Style.RESET_ALL}"))
    capacidade_bateria = 50
    energia_necessaria = capacidade_bateria * (100 - porcentagem_bateria) / 100

    potencia_carregador = float(input(f"{Fore.CYAN}Digite a potência do carregador (em kW): {Style.RESET_ALL}"))

    tempo_estimado = energia_necessaria / potencia_carregador

    print(f"{Fore.GREEN}Tempo estimado de carregamento: {tempo_estimado:.2f} horas.{Style.RESET_ALL}")

def sistema_pagamento():
    valor_tarifa = 1.5
    energia_usada = float(input(f"{Fore.CYAN}Digite a quantidade de energia consumida (em kWh): {Style.RESET_ALL}"))
    total_a_pagar = valor_tarifa * energia_usada

    print(f"{Fore.GREEN}O valor total a pagar é: R${total_a_pagar:.2f}{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}Escolha a forma de pagamento:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}1. Cartão de Crédito")
    print(f"{Fore.GREEN}2. Cartão de Débito")
    print(f"{Fore.MAGENTA}3. PIX")

    forma_pagamento = input(f"\n{Fore.CYAN}Escolha a forma de pagamento (1-3): {Style.RESET_ALL}").strip()

    if forma_pagamento == '1':
        forma = "Cartão de Crédito"
    elif forma_pagamento == '2':
        forma = "Cartão de Débito"
    elif forma_pagamento == '3':
        forma = "PIX"
    else:
        print(f"{Fore.RED}Opção inválida. Tente novamente.{Style.RESET_ALL}")
        return

    pagamento = input(f"{Fore.CYAN}Deseja confirmar o pagamento via {forma}? (s/n): {Style.RESET_ALL}").strip().lower()
    if pagamento == 's':
        print(f"{Fore.GREEN}Pagamento confirmado! R${total_a_pagar:.2f} pagos com sucesso através do {forma}.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Pagamento cancelado.{Style.RESET_ALL}")

def ver_e_contratar_planos():
    planos = [
        {"nome": "Plano Básico", "preco": 30.0, "descricao": "10 kWh/mês", "beneficios": "Acesso básico aos pontos de carregamento"},
        {"nome": "Plano Avançado", "preco": 60.0, "descricao": "25 kWh/mês", "beneficios": "Acesso a pontos de carregamento premium"},
        {"nome": "Plano Premium", "preco": 100.0, "descricao": "50 kWh/mês", "beneficios": "Acesso ilimitado e preferencial aos pontos de carregamento" }
    ]

    print(f"\n{Fore.BLUE}Planos Disponíveis:{Style.RESET_ALL}")
    for i, plano in enumerate(planos, start=1):
        print(f"{i}. {plano['nome']} - {plano['descricao']} - R${plano['preco']:.2f}")
        print(f"   Benefícios: {plano['beneficios']}")

    escolha_plano = input(f"\n{Fore.CYAN}Escolha um plano (1-3): {Style.RESET_ALL}").strip()
    try:
        escolha_plano = int(escolha_plano)
        if escolha_plano < 1 or escolha_plano > 3:
            print(f"{Fore.RED}Opção inválida. Tente novamente.{Style.RESET_ALL}")
            return
    except ValueError:
        print(f"{Fore.RED}Entrada inválida. Tente novamente.{Style.RESET_ALL}")
        return

    plano_escolhido = planos[escolha_plano - 1]
    print(f"{Fore.GREEN}Você contratou o {plano_escolhido['nome']} por R${plano_escolhido['preco']:.2f} por mês. Benefícios: {plano_escolhido['beneficios']}{Style.RESET_ALL}")

def mostrar_menu():
    print(f"\n{Style.BRIGHT}--- ChargeMap ---")
    print(f"{Fore.BLUE}1. Encontrar pontos de carregamento próximos")
    print(f"{Fore.GREEN}2. Fazer reserva de carregador")
    print(f"{Fore.CYAN}3. Estimar tempo de carregamento")
    print(f"{Fore.YELLOW}4. Sistema de pagamento integrado")
    print(f"{Fore.MAGENTA}5. Ver e contratar Planos")
    print(f"{Fore.LIGHTRED_EX}6. Sair")

def main():
    if not tela_login_cadastro():
        return

    while True:
        mostrar_menu()
        opcao = input(f"\n{Fore.CYAN}Escolha uma opção: {Style.RESET_ALL}").strip()
        if opcao == "1":
            encontrar_pontos_carregamento()
        elif opcao == "2":
            reservar_carregador()
        elif opcao == "3":
            estimar_tempo_carregamento()
        elif opcao == "4":
            sistema_pagamento()
        elif opcao == "5":
            ver_e_contratar_planos()
        elif opcao == "6":
            print(f"{Fore.RED}Saindo do ChargeMap. Até logo!{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
