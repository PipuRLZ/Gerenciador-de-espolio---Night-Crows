# 🦅 Gerenciador de Cruzada — Interface Gráfica

Um sistema utilitário focado no gerenciamento, cálculo de distribuição de espólios e sorteios de recompensas de Cruzada para guildas, com suporte a integração com o Discord.

---

### 📷 Interface do Sistema

![Gerenciador de Cruzada](Captura%20de%20tela%202026-08-30%20133205_2.png)

---

### ✨ Funcionalidades Identificadas

* **Integração com Discord:** Campo de configuração de `Webhook URL` no topo da aplicação para envio automatizado de relatórios para canais do Discord.
* **Gestão de Territórios e Espólios (Loot):**
  * Painéis independentes para **Equipe A** e **Equipe B**.
  * Campos para definição do nome do território e quantidade dos recursos: **Morions**, **Diamantes**, **Moedas Guild** e **Sacos de Ouro**.
  * Botões dedicados para o cálculo de distribuição de espólios por equipe (`Calcular Distribuição - Equipe A / B`).
* **Filtro de Busca:** Campo `Buscar jogador` para localização rápida de membros na tabela.
* **Tabela Principal de Jogadores:**
  * **Nome & Equipe:** Edição individual de nomes e atribuição de equipes (`A`, `B`, `Reserva`).
  * **Status de Bid:** Checkbox `Bidou?` e campo numérico para digitação do `Valor do Bid` (com suporte a formatos abreviados como `32.5m`).
  * **Controle de Presença e Elegibilidade:** Checkboxes para `Presente?`, `Já Ganhou Caixa?` e `Elegível Sorteio?`.
  * **Gestão Dinâmica:** Botão `Remover` por linha para excluir membros.
* **Ações Globais e Sorteios:**
  * **Salvar Dados:** Armazena as alterações e estados atuais do sistema.
  * **Limpar Todos os Bids:** Zera os campos de lances e marcações para inicio de novo ciclo.
  * **+ Adicionar Jogador:** Insere novas linhas na lista de membros.
  * **Ver Histórico:** Exibe o registro das atividades anteriores.
  * **Sortear Caixa (Equipes A e B):** Realiza o sorteio automático de caixas entre os membros elegíveis de cada equipe.

---

### 🛠️ Estrutura dos Campos de Entrada

| Seção | Campo | Descrição |
| :--- | :--- | :--- |
| **Discord** | `Webhook URL` | URL do webhook do canal para postagem de resultados |
| **Território** | `Território`, `Morions`, `Diamantes`, `Moedas Guild`, `Sacos de Ouro` | Define o loot total a ser distribuído entre a equipe |
| **Jogadores** | `Nome`, `Equipe`, `Bidou?`, `Valor do Bid`, `Presente?`, `Já Ganhou Caixa?`, `Elegível Sorteio?` | Dados individuais do membro para cálculo proporcional e sorteio |
