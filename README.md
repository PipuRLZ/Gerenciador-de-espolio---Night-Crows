# 🦅 Gerenciador de Cruzada — Night Crows

Um utilitário desktop leve e rápido desenvolvido em Python para automatizar e agilizar a divisão de espólios de guilda e o sorteio de recompensas após as batalhas de Cruzada no MMORPG **Night Crows**.

---

### 💡 A Dor do Problema

Gerenciar uma guilda com dezenas de membros durante a Cruzada exige precisão financeira. Fazer a divisão proporcional de **Diamantes**, **Morions**, **Sacos de Ouro** e **Moedas de Guilda** manualmente em planilhas gera erros, atrasa a entrega das recompensas e consome tempo dos líderes de guilda.

O **Gerenciador de Cruzada** resolve esse problema calculando em segundos a porcentagem de contribuição individual (com base no *Bid* realizado por cada jogador) e dividindo todos os recursos arrecadados do território conquistado.

---

### ✨ Funcionalidades Principais

* **Entrada Rápida com Atalhos:** Suporte para digitação abreviada de valores (ex: `30m` para 30.000.000 ou `500k` para 500.000).
* **Automação de Elegibilidade:** Ao digitar `30m` no Bid de um jogador, o sistema marca automaticamente que ele "Bidou" e que está "Elegível ao Sorteio".
* **Regras de Divisão e Arredondamento:**
  * Divisão proporcional exata ao valor doado por cada membro.
  * **Zero Quebrados:** Arredondamento para números inteiros (Morions, Sacos de Ouro e Diamantes) e para a casa dos milhares inferior (Moedas de Guilda).
  * **Alocação de Sobras:** As frações restantes dos arredondamentos são direcionadas automaticamente para a liderança (`Alcamax`).
* **Sorteio Trava-Repetição:** O sistema filtra e sorteia o **Baú de Espólio da Cruzada** apenas entre os membros elegíveis (30M doados) que **ainda não ganharam a caixa na temporada**.
* **Persistência de Dados (JSON):** Salva e carrega automaticamente as informações dos membros para a próxima semana.

---

### 📷 Demonstração do Sistema

#### 1. Preenchimento de Presença e Bids
*Gerenciamento visual com marcações rápidas por checkbox e suporte a apelidos e atalhos de valores.*

![Preenchimento de Bids e Presença](Captura%20de%20tela%202026-08-29%20184720.png)

#### 2. Relatório de Distribuição de Espólios
*Cálculos sem números fracionados e gestão transparente de cada recurso ganho.*

![Resultado da Distribuição](Captura%20de%20tela%202026-08-29%20184752.png)

#### 3. Sorteio Transparente do Baú
*Filtra automaticamente quem já ganhou a caixa na temporada para garantir a rotatividade das recompensas.*

![Sorteio do Baú da Cruzada](Captura%20de%20tela%202026-08-29%20184817.png)

---

### ⚖️ Pontos Fortes vs. Limitações Atual

**Pontos Fortes:**
* **Flexibilidade Total:** É possível alterar nomes, adicionar novos membros/reservas, alternar equipes (`A`, `B`, `Reserva`) ou remover participantes a qualquer momento sem quebrar o banco de dados.
* **Executável Nativo:** Não exige instalação do Python no computador do usuário final — roda direto como um `.exe` leve no Windows.

**Limitação Atual:**
* A lista exibe primeiro os membros da **Equipe A** e sequencialmente a **Equipe B**, exigindo rolagem vertical para acessar os reservas. *(Melhoria futura planejada: abas separadas por equipe ou filtros dinâmicos de busca).*

---

### 🛠️ Tecnologias Utilizadas

* **Python 3.14**
* **Tkinter** (Interface gráfica nativa)
* **JSON** (Persistência leve de dados)
* **PyInstaller** (Empacotamento em `.exe`)

---

### 🚀 Como Executar o Projeto

1. Baixe o executável pronto dentro da pasta `dist/gerenciador_cruzada.exe`.
2. Mantenha o arquivo `.exe` na pasta de sua preferência e dê dois cliques para executar.
