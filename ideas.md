# Ideias de Design - Agenda de Despachos

## Resposta 1: Minimalismo Funcional com Acentos em Âmbar
**Probabilidade: 0.08**

**Design Movement:** Bauhaus Moderno + Swiss Design

**Core Principles:**
- Hierarquia clara através de espaçamento e tipografia (não cores)
- Foco absoluto em funcionalidade: cada elemento serve a um propósito
- Assimetria controlada: coluna esquerda (agenda) mais estreita, direita (detalhes) expansível
- Tipografia como protagonista: sans-serif geométrica com variações de peso

**Color Philosophy:**
Paleta neutra com acentos estratégicos em âmbar (FFC000) apenas para ações críticas e status. Fundo branco puro, texto em cinza escuro. O âmbar aparece apenas em botões de despacho, indicadores de urgência e bordas de separação entre seções.

**Layout Paradigm:**
Divisão 30/70 (coluna esquerda/direita) com painel lateral retrátil. A esquerda é um timeline vertical com cards compactos. A direita expande para mostrar uma tabela estruturada dos materiais com localização em destaque.

**Signature Elements:**
- Linhas verticais finas em âmbar separando datas
- Cards com borda esquerda em âmbar para pedidos selecionados
- Ícones minimalistas (sem preenchimento, apenas contorno)

**Interaction Philosophy:**
Cliques suaves, sem animações excessivas. Transições de 150ms. Feedback visual através de mudança de cor de fundo (não escala ou rotação).

**Animation:**
Fade-in suave ao carregar dados. Slide horizontal da coluna direita ao selecionar um pedido. Pulsação sutil em indicadores de status.

**Typography System:**
- Títulos: Roboto Mono Bold 18px (para tabelas e seções)
- Subtítulos: Roboto Regular 14px
- Body: Inter Regular 13px
- Números/Códigos: IBM Plex Mono 12px (monospace para códigos de material)

---

## Resposta 2: Dashboard Elegante com Gradientes Suaves
**Probabilidade: 0.07**

**Design Movement:** Contemporary Dashboard Design + Neumorphism

**Core Principles:**
- Profundidade através de sombras e elevação (não bordas)
- Cores em gradientes suaves para criar movimento visual
- Componentes "flutuam" sobre o fundo com sombras difusas
- Espaçamento generoso para respiração visual

**Color Philosophy:**
Fundo em gradiente sutil (azul profundo a cinza escuro). Cards em branco com sombra suave. Âmbar como cor de destaque em indicadores de "pronto para despacho". Verdes para "despachado", vermelhos para "pendência crítica".

**Layout Paradigm:**
Coluna esquerda como um "painel flutuante" com timeline visual (círculos conectados por linhas). Coluna direita como um card elevado mostrando detalhes. Ambas as colunas têm cantos arredondados generosos (16px+).

**Signature Elements:**
- Círculos conectados em timeline (uma por data)
- Cards com sombra profunda e gradiente sutil
- Badges coloridas para status (verde, amarelo, vermelho)

**Interaction Philosophy:**
Animações suaves e fluidas. Hover expande ligeiramente o card. Clique em um pedido anima a transição da coluna direita com um slide + fade.

**Animation:**
Entrance: fade-in com scale (0.95 → 1). Hover: elevation aumenta (sombra mais profunda). Transição entre pedidos: slide horizontal + fade cruzado.

**Typography System:**
- Títulos: Poppins Bold 20px
- Subtítulos: Poppins Medium 14px
- Body: Lato Regular 13px
- Dados: IBM Plex Mono 11px

---

## Resposta 3: Design Operacional com Foco em Dados
**Probabilidade: 0.06**

**Design Movement:** Information Design + Industrial Aesthetic

**Core Principles:**
- Densidade de informação otimizada (sem sacrificar legibilidade)
- Grid estruturado e alinhamento rigoroso
- Cores significam dados (não apenas decoração)
- Tipografia técnica e legível em qualquer tamanho

**Color Philosophy:**
Fundo cinza muito claro (quase branco). Coluna esquerda com fundo cinza ligeiramente mais escuro para separação. Âmbar para "ação necessária", verde para "pronto", cinza para "aguardando". Sem gradientes; cores sólidas e diretas.

**Layout Paradigm:**
Grid de 12 colunas. Coluna esquerda ocupa 4 colunas (timeline compacta). Coluna direita ocupa 8 colunas (tabela de materiais com scroll). Ambas alinhadas ao mesmo baseline.

**Signature Elements:**
- Linha vertical em âmbar separando as colunas
- Números de pedido em fonte monospace grande (destaque)
- Ícones de status (pequenos, quadrados)

**Interaction Philosophy:**
Feedback imediato e óbvio. Seleção de um pedido muda a cor de fundo da linha. Hover em um material destaca a linha inteira.

**Animation:**
Mínima. Apenas fade-in ao carregar. Sem transições desnecessárias. Foco em velocidade e clareza.

**Typography System:**
- Títulos: IBM Plex Mono Bold 16px
- Subtítulos: IBM Plex Mono Regular 12px
- Body: Roboto Regular 12px
- Dados: IBM Plex Mono Regular 11px

---

## Decisão Final: Minimalismo Funcional com Acentos em Âmbar (Resposta 1)

Escolhi a **Resposta 1** porque ela se alinha perfeitamente com a natureza operacional do seu sistema. A Agenda de Despachos é uma ferramenta de trabalho, não um painel decorativo. O design minimalista garante que nada distraia do objetivo principal: visualizar rapidamente o que precisa ser despachado e onde estão os materiais.

O uso estratégico do âmbar (que você já utiliza no seu sistema de iluminação pública) cria uma linguagem visual coerente em toda a plataforma. A assimetria entre as colunas (30/70) reflete o fluxo natural de trabalho: você consulta a agenda rapidamente à esquerda e depois se concentra nos detalhes à direita.

A tipografia em sans-serif geométrica com variações de peso (não cores) cria hierarquia clara sem poluição visual. Os ícones minimalistas mantêm o design leve e profissional.
