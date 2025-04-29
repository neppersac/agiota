import json
from datetime import datetime
from getpass import getpass
import hashlib
import os

class ContaBancaria:
    def __init__(self):
        self.saldo = 0
        self.extrato = []
        self.numero_saques = 0
        self.LIMITE_SAQUES = 3
        self.agencia = "0001"
        self.usuarios = []
        self.contas = []
        self.salt = os.urandom(32)  # Salt para segurança das senhas

    def criar_usuario(self):
        """Cria um novo usuário no sistema"""
        print("\n=== CRIAR USUÁRIO ===")
        cpf = input("Informe o CPF (somente números): ")
        
        # Verifica se usuário já existe
        if any(usuario['cpf'] == cpf for usuario in self.usuarios):
            print("\n❌ Já existe usuário com esse CPF!")
            return

        nome = input("Informe o nome completo: ")
        data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
        endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")
        
        # Cria hash segura da senha
        senha = getpass("Crie uma senha: ")
        senha_hash = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), self.salt, 100000)
        
        self.usuarios.append({
            "nome": nome,
            "data_nascimento": data_nascimento,
            "cpf": cpf,
            "endereco": endereco,
            "senha": senha_hash.hex()
        })
        
        print("\n✅ Usuário criado com sucesso!")

    def criar_conta(self):
        """Cria uma nova conta bancária"""
        print("\n=== CRIAR CONTA ===")
        cpf = input("Informe o CPF do usuário (somente números): ")
        
        usuario = next((u for u in self.usuarios if u['cpf'] == cpf), None)
        
        if not usuario:
            print("\n❌ Usuário não encontrado! Crie um usuário primeiro.")
            return
        
        numero_conta = len(self.contas) + 1
        self.contas.append({
            "agencia": self.agencia,
            "numero_conta": numero_conta,
            "usuario": usuario,
            "saldo": 0,
            "extrato": []
        })
        
        print(f"\n✅ Conta criada com sucesso! Número: {numero_conta}")

    def autenticar(self):
        """Autentica o usuário"""
        print("\n=== LOGIN ===")
        cpf = input("CPF: ")
        senha = getpass("Senha: ")
        
        # Encontra a conta do usuário
        conta = next((c for c in self.contas if c['usuario']['cpf'] == cpf), None)
        if not conta:
            print("\n❌ Conta não encontrada!")
            return None
        
        # Verifica a senha
        senha_hash = hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), self.salt, 100000)
        if conta['usuario']['senha'] != senha_hash.hex():
            print("\n❌ Senha incorreta!")
            return None
            
        return conta

    def depositar(self, conta):
        """Realiza um depósito na conta"""
        valor = float(input("Informe o valor do depósito: "))
        
        if valor > 0:
            conta['saldo'] += valor
            operacao = {
                "tipo": "Depósito",
                "valor": valor,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
            conta['extrato'].append(operacao)
            print(f"\n✅ Depósito de R$ {valor:.2f} realizado com sucesso!")
        else:
            print("\n❌ Operação falhou! O valor informado é inválido.")

    def sacar(self, conta):
        """Realiza um saque da conta"""
        valor = float(input("Informe o valor do saque: "))
        
        excedeu_saldo = valor > conta['saldo']
        excedeu_limite = valor > 500
        excedeu_saques = len([op for op in conta['extrato'] if op['tipo'] == "Saque"]) >= self.LIMITE_SAQUES
        
        if excedeu_saldo:
            print("\n❌ Operação falhou! Saldo insuficiente.")
        elif excedeu_limite:
            print("\n❌ Operação falhou! O valor do saque excede o limite de R$ 500,00.")
        elif excedeu_saques:
            print("\n❌ Operação falhou! Número máximo de saques diários excedido.")
        elif valor > 0:
            conta['saldo'] -= valor
            operacao = {
                "tipo": "Saque",
                "valor": valor,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
            conta['extrato'].append(operacao)
            print(f"\n✅ Saque de R$ {valor:.2f} realizado com sucesso!")
        else:
            print("\n❌ Operação falhou! O valor informado é inválido.")

    def exibir_extrato(self, conta):
        """Exibe o extrato da conta"""
        print("\n================ EXTRATO ================")
        if not conta['extrato']:
            print("Não foram realizadas movimentações.")
        else:
            for operacao in conta['extrato']:
                print(f"{operacao['tipo']}:\tR$ {operacao['valor']:.2f}\t{operacao['data']}")
        print(f"\nSaldo atual:\tR$ {conta['saldo']:.2f}")
        print("==========================================")

    def salvar_dados(self):
        """Salva os dados em arquivo JSON"""
        dados = {
            "usuarios": self.usuarios,
            "contas": self.contas,
            "salt": self.salt.hex()
        }
        with open('dados_bancarios.json', 'w') as arquivo:
            json.dump(dados, arquivo, indent=2)

    def carregar_dados(self):
        """Carrega os dados do arquivo JSON"""
        try:
            with open('dados_bancarios.json', 'r') as arquivo:
                dados = json.load(arquivo)
                self.usuarios = dados.get('usuarios', [])
                self.contas = dados.get('contas', [])
                self.salt = bytes.fromhex(dados.get('salt', os.urandom(32).hex()))
        except FileNotFoundError:
            # Arquivo não existe ainda - inicia com dados vazios
            pass

    def menu(self):
        """Exibe o menu principal"""
        self.carregar_dados()
        
        while True:
            print("\n=== SISTEMA BANCÁRIO ===")
            print("1 - Criar usuário")
            print("2 - Criar conta")
            print("3 - Acessar conta")
            print("4 - Sair")
            
            opcao = input("\nSelecione uma opção: ")
            
            if opcao == "1":
                self.criar_usuario()
            elif opcao == "2":
                self.criar_conta()
            elif opcao == "3":
                conta = self.autenticar()
                if conta:
                    self.menu_conta(conta)
            elif opcao == "4":
                self.salvar_dados()
                print("\nObrigado por usar nosso sistema bancário!")
                break
            else:
                print("\n❌ Opção inválida! Tente novamente.")

    def menu_conta(self, conta):
        """Exibe o menu da conta após login"""
        while True:
            print(f"\nBem-vindo, {conta['usuario']['nome']}!")
            print("1 - Depositar")
            print("2 - Sacar")
            print("3 - Extrato")
            print("4 - Sair da conta")
            
            opcao = input("\nSelecione uma operação: ")
            
            if opcao == "1":
                self.depositar(conta)
            elif opcao == "2":
                self.sacar(conta)
            elif opcao == "3":
                self.exibir_extrato(conta)
            elif opcao == "4":
                print("\nSaindo da conta...")
                break
            else:
                print("\n❌ Opção inválida! Tente novamente.")


# Inicializa e executa o sistema bancário
if __name__ == "__main__":
    sistema = ContaBancaria()
    sistema.menu()