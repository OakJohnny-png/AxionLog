# Módulo de Gerência - AxionLog

## Visão Geral
O módulo de Gerência funciona como o núcleo administrativo do AxionLog. Não lida com operação diária, mas assegura que os metadados (itens, clientes e utilizadores) estejam corretos no banco de dados cliente (IndexedDB).

## Funcionalidades Principais

### 1. Gestão de Banco de Dados Local (IndexedDB)
- Gerenciamento de metadados (itens, clientes, utilizadores)
- Área restrita com privilégios de administração
- Tipografia: JetBrains Mono para inputs técnicos, DM Sans para UI

### 2. Importação de Bases (Excel)
**Lógica de Bulk Import:**
- Leitura em memória via ExcelJS
- Ficheiros .xlsx (Stock e Clientes) convertidos em ArrayBuffer
- **Mapeamento Estrito:**
  - Stock: Coluna A (Código), B (Localização), C (Descrição)
  - Clientes: Coluna A (Código), B (Nome)
- **Tratamento:**
  - Normalização via `normalizarTexto()` (remove espaços, aplica NFC)
  - Empacotamento em lotes
  - Armazenamento via `salvarItensEmLote` e `salvarClientesEmLote`
  - Feedback visual sobre quantidade de registros importados

### 3. Gestão de Stock (CRUD Completo)
**Pesquisa Reativa:**
- Input com escuta de eventos de digitação
- Filtro em tempo real sobre `_todosItensGerencia`
- Correlaciona termo com código, descrição ou localização
- Dropdown restrito a 15 resultados otimizados

**Edição (Update):**
- Função `selecionarItemGerencia()` popula formulário de edição
- DOM inicia propriedades no formulário
- Bloqueia (disabled) a chave primária (Código)
- Clique em "Salvar" dispara `window.dbSalvarItem`

**Criação e Remoção (Create/Delete):**
- `novoItemGerencia()` e `excluirItemGerencia()`
- Chave primária desbloqueada para registro ou apagada com validação nativa do browser (confirm)
- Variável global `_todosItensGerencia` é forçada a re-sincronização

### 4. Controlo de Utilizadores
- Gerencia credenciais internas (identificado por `criarUsuario()`)
- Validação por nome de utilizador, senha e "papel" (nível de acesso)
- Credenciais exigidas posteriormente no processo de Login do AxionLog
- Garante integridade dos módulos operacionais

## Estrutura de Dados

### Stock (Itens)
```
- Código (Chave Primária)
- Localização
- Descrição
```

### Clientes
```
- Código (Chave Primária)
- Nome
```

### Utilizadores
```
- Nome de Utilizador (Chave Primária)
- Senha
- Papel (Nível de Acesso)
```

## Fluxo de Trabalho

1. **Importação:** Upload de ficheiros Excel → Processamento em lote → Armazenamento em IndexedDB
2. **Gestão de Stock:** Pesquisa → Edição/Criação/Remoção → Re-sincronização
3. **Controlo de Acesso:** Criação de utilizadores → Validação de credenciais → Integração com Login
