# Entrada de Dados GEO360

Este repositório contém um script de interface gráfica para gerenciamento de dados de pilares e sondagens.

## Como executar

1. Certifique-se de ter o Python instalado (recomenda-se a versão 3.8 ou superior).
2. Instale as dependências necessárias:

```bash
pip install pandas
```

3. Execute o script `gerenciador.py`:

```bash
python gerenciador.py
```

A aplicação abrirá uma janela permitindo importar arquivos Excel com dados de pilares e gerenciar sondagens.

## Cálculo de Capacidade de Estacas

O módulo `calculo_estacas.py` fornece funções genéricas para estimar a capacidade de carga de estacas pelos métodos semiempíricos de Aoki & Velloso e Décourt & Quaresma. Veja o bloco `__main__` no próprio arquivo para um exemplo de uso com dados fictícios.

Execute o módulo diretamente para visualizar o exemplo:

```bash
python calculo_estacas.py
```

Adapte os coeficientes utilizados conforme o tipo de solo e de estaca do seu projeto.
