# 📖 Histórias de Usuário - Controle de Embarcações

---

## Funcionalidades para Usuários comuns

### História 1: Cadastro de Usuário
**Como** um usuário comum,  
**Quero** realizar meu cadastro no sistema,  
**Para que** eu possa acessar e utilizar as funcionalidades.

---

### História 2: Login no Sistema
**Como** um usuário comum,  
**Quero** realizar meu login para acessar o sistema,  
**Para que** eu possa utilizar as funcionalidades disponíveis.

---

### História 3: Cadastrar um Pedido de Autorização
**Como** um usuário comum,  
**Quero** cadastrar um novo pedido de autorização de serviço,  
**Para que** eu possa informar um serviço que será realizado em uma embarcação.

**Requisitos do Pedido de Autorização**:
- Relacionar uma **empresa responsável**.
- Incluir **uma ou mais embarcações**.
- Incluir **um ou mais veículos**.
- Definir o **serviço a ser realizado**.
- Cadastrar as **pessoas que fazem parte da equipe**.

---

### História 4: Consultar Minhas Autorizações
**Como** um usuário comum,  
**Quero** consultar as autorizações de serviço que eu cadastrei,  
**Para que** eu possa acompanhar o status dos meus pedidos.

---

### História 5: Editar Meus Pedidos
**Como** um usuário comum,  
**Quero** editar um pedido de autorização,  
**Para que** eu possa alterar alguns dados do pedido cadastrado.

**Critérios de aceitação:**
- Para que seja possível a edição, o pedido ainda não pode ter sido aprovado pela agência marítima

---

### História 6: Solicitar prorrogação de prazo
**Como** um usuário comum,  
**Quero** solicitar a prorrogação do prazo para a realização de um serviço,  
**Para que** eu possa ampliar o prazo concedido inicialmente.

**Critérios de aceitação:**
- O pedido deve ter status "aprovado".
- A solicitação só pode ser feita se faltarem menos de 3 dias para o término.

---

### História 7: Gerar comprovante com QR code
**Como** um usuário comum,  
**Quero** gerar um documento que comprove a autorização do serviço,  
**Para que** eu possa exibir o documento nos gates portuários.

---

## Funcionalidades para Agências Marítimas

### História 8: Consultar Autorizações relacionadas à minha agência
**Como** um usuário agência marítima,  
**Quero** consultar os pedidos de autorizações cadastrados que estejam relacionados ao meu CNPJ,  
**Para que** eu possa visualizar os detalhes de cada pedido.

---

### História 9: Aprovar Autorizações relacionadas à minha agência
**Como** um usuário agência marítima,  
**Quero** aprovar ou rejeitar os pedidos de autorizações cadastrados que estejam relacionados ao meu CNPJ,  
**Para que** eu possa aceitar ou não o agenciamento de uma carga.

---

## Funcionalidades para Usuários RFB

### História 10: Consultar Autorizações de Usuários
**Como** um usuário RFB,  
**Quero** consultar as autorizações cadastradas por cada usuário comum,  
**Para que** eu possa fiscalizar e acompanhar os serviços autorizados.

---

### História 11: Aprovar Pedido de Autorização
**Como** um usuário RFB,  
**Quero** aprovar o pedido de autorização de serviço,  
**Para que** eu possa garantir a conformidade dos serviços realizados.

---

### História 12: Aprovar Prorrogação de prazo
**Como** um usuário RFB,  
**Quero** aprovar o pedido de prorrogação de prazo,  
**Para que** eu possa autorizar a ampliação do término do trabalho.

---

### História 13: Fazer exigência
**Como** um usuário RFB,  
**Quero** incluir uma exigência para aprovação de um pedido,  
**Para que** eu possa parar o fluxo de autorização do pedido enquanto a exigência não for satisfeita.

---

### História 14: Consultar Autorização de Embarcação
**Como** um usuário RFB,  
**Quero** consultar uma embarcação para ver se ela possui autorização,  
**Para que** eu possa verificar a regularidade do serviço.

---

### História 15: Exportar relatórios
**Como** um usuário RFB,  
**Quero** exportar relatórios em csv, pdf e Excel,  
**Para que** eu possa gerenciar os pedidos de autorização.

---

### História 16: Cadastrar Alertas
**Como** um usuário RFB,  
**Quero** cadastrar alertas para quando determinadas pessoas, veículos ou embarcações fizerem cadastro de pedido de autorização,  
**Para que** eu possa monitorar atividades de interesse.

---

### História 17: Receber Alertas de Risco
**Como** um usuário RFB,  
**Quero** receber alertas quando alguma autorização com algum parâmetro de risco for cadastrada no sistema,  
**Para que** eu possa tomar as medidas necessárias rapidamente.

---

## Funcionalidades para Usuários externos

### História 18: Consultar autenticidade
**Como** um usuário externo,  
**Quero** consultar a autenticidade de um documento de autorização,  
**Para que** eu possa liberar a entrada no porto.
