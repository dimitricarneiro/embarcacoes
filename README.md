[![Run tests](https://github.com/dimitricarneiro/embarcacoes/actions/workflows/test.yaml/badge.svg)](https://github.com/dimitricarneiro/embarcacoes/actions/workflows/test.yaml)
# Controle de Embarcações

Este projeto tem como objetivo gerenciar e controlar embarcações que prestam serviços no porto

---

**Usuários de teste**
- **Admin**: 123456
- **usuario**: 123456

---

## Tecnologias Utilizadas

O projeto foi desenvolvido com as seguintes tecnologias:

- **Linguagem**: Python 3.13
- **Framework**: Flask
- **Banco de Dados**: MySQL
- **Testes**: Pytest + Coverage.py
- **Code Quality**: Flake8, Black, Isort, Radon
- **CI/CD**: GitHub Actions
- **Documentação**: CommonMark (Markdown)
- **Princípios de Desenvolvimento**:
  - Desenvolvimento Orientado a Testes (TDD)
  - Separação entre camadas (Apresentação, Negócio e Dados)
  - Complexidade Ciclomática Baixa (Radon)
  - Manifesto Ágil

---

## Estrutura do Projeto

```
controle-embarcacoes/
├── app/                # Código-fonte principal
│   ├── controllers/    # Camada de apresentação (rotas Flask)
│   ├── services/       # Regras de negócio
│   ├── models/         # Camada de dados (ORM ou acesso ao banco)
│   └── routes.py       # Definição das rotas principais
├── tests/              # Testes unitários e de integração
│   ├── unit/
│   ├── integration/
├── docs/               # Documentação
├── .github/workflows/  # Configuração de CI/CD
├── requirements.txt    # Dependências do projeto
├── pyproject.toml      # Configuração do projeto (caso use poetry)
├── README.md           # Documentação principal
└── run.py              # Arquivo de inicialização do Flask
```

---

## Configuração do Ambiente

### Pré-requisitos
Antes de rodar o projeto, instale as dependências necessárias:

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### Executando o Servidor

```bash
flask run
```
O servidor estará disponível em **http://127.0.0.1:5000/**.

---

## Rodando os Testes

```bash
pytest --cov=app tests/
```
Para gerar um relatório de cobertura:
```bash
coverage run -m pytest
coverage report -m
```
Para visualizar a cobertura em HTML:
```bash
coverage html
```

---

## Qualidade do Código

Para garantir a qualidade do código, utilize as seguintes ferramentas:

- **Linting**: `flake8`
- **Formatação**: `black`
- **Ordenação de Imports**: `isort`
- **Complexidade Ciclomática**: `radon`

### Comandos Úteis

```bash
flake8 app/
black app/
isort app/
radon cc app/ -a
```

---

## CI/CD

Este projeto utiliza **GitHub Actions** para CI/CD. A pipeline inclui:

✅ Testes automatizados com Pytest  
✅ Cobertura de testes com Coverage.py  
✅ Análise de qualidade do código (Flake8, Black, Isort, Radon)  
✅ Deploy contínuo (se configurado)  

---

## Licença

Este projeto está sob a licença **???**.

---

## Contribuindo

1. **Crie uma branch**:  
   ```bash
   git checkout -b feature/minha-feature
   ```
2. **Faça commit das mudanças**:  
   ```bash
   git commit -m "Adiciona nova funcionalidade"
   ```
3. **Envie para o repositório remoto**:  
   ```bash
   git push origin feature/minha-feature
   ```
4. **Abra um Pull Request** 🚀

---

## Contato

Caso tenha dúvidas ou sugestões, entre em contato!

Email: [dimitri.carneiro@rfb.gov.br](mailto:dimitri.carneiro@rfb.gov.br)  
