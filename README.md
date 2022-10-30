# RedHouse Insights
![Alt text](/images/redhouse-logo.png)

## Objetivos

Nesse projeto nós iremos realizar uma análise minuciosa do banco de dados de uma empresa do ramo imobiliário, com o intuito de maximizar o lucro da companhia.

O principais objetivos são:

- Determinar quais imóveis a empresa deve comprar, levando em consideração alguns critérios.

- Determinar a que preço os imóveis adquiridos devem ser vendidos.

- Validação de algumas hipóteses:

    H1: Imóveis que possuem vista para água, são 30% mais caros, na média.

    H2: Imóveis com data de construção menor que 1955, são 50% mais baratos, na média.
    
    H3: No verão, o preço dos imóveis são, em média, 30% mais caro que no inverno.
   
    H4: Os imóveis com condição nível 5 são, em média, pelo menos 10% mais caros.
   
    H5: Imóveis que não foram reformados, são 40% mais baratos, na média.
   
    H6: Imóveis reformados após 2005 são 25% mais caras, em média.
   
    H7: O preço dos imóveis na região de Medina é, em média, 45% mais caro que na região de Bellevue

- Elaborar um dashboard, que poderá ser acessado pelo CEO, contendo um resumo dos resultados.

## Questão de Negócio

A RedHouse é uma empresa que atua no setor imobiliário, com sede no Condado de King, em Washington, USA, através da compra e venda de imóveis, auferindo lucro com a diferença entre os preços.
Por conta do grande volume de informações que o time de negócios recebe diariamente, a empresa não consegue tomar boas decisões de compra e venda.
O CEO da empresa, observando que o lucro almejado não estava sendo alcançado, contratou nossa consultoria afim de resolvermos as seguintes questões de negócio:

1 - Quais são os imóveis que a RedHouse
deveria comprar?

2 - Uma vez a casa comprada, por qual preço ela deveria ser vendida ?

## Principais Resultados
Há um total de 21435 imóveis disponíveis. Aplicando alguns critérios, foram recomendados
para compra 2811 propriedades.

Investimento a Realizar: $ 1,437,906,154.00

Faturamento Esperado: $ 1,752,548,009.40

Lucro Esperado: $ 314,641,855.40


## Premissas de negócio
 
- Propriedades com valores de atributos discrepantes serão desconsiderados, assumindo que foram erros de digitação. (exemplo: imóvel com 33 quartos).
- Os critérios para a compra de um imóvel é que o seu preço esteja abaixo da mediana da região, a condição de uso seja maior ou igual a 3 e a nota da casa (grade) 
    seja maior ou igual a 10.
- Será considerado que não houve reforma o imóvel com ano de reforma igual a 0.
- Caso haja imóveis duplicados, será considerado na análise o mais recente.
- As casas com área do porão igual a 0 não tem porão.
- Foram consideradas as seguintes data para início das estações do ano (Hemisfério Norte) : 
            
        20/03 Primavera

        21/06 Verão

        23/09 Outono

        21/12 Inverno

## Estratégia de solução
- Entendimento do modelo de negócio da empresa
- Entendimento do problema de negócio
- Coleta dos dados
- Análise Exploratória dos Dados
- Tratamento e limpeza dos dados
- Insights obtidos
- Publicação de dashboard online

## Principais Insights
- Imóveis que possuem vista para água são, em média, 211.76% mais caros.
- Casas que têm condição 5 são 14,49% mais caras, em média.
- Imóveis que não foram reformados são 30.21% mais baratos, em média.
- O tamanho da área interna do imóvel, aparentemente, influencia no preço.
- Casas com mais banheiros tendem a ser mais caras.
- A região de Medina tem um preço mediano mais alto
- A região de Seattle tem um preço/pé quadrado mais alto, em média.

## Conclusão
Através dessa análise realizada foi possível atender aos objetivos da empresa:
Fornecer um relatório e dashboard contendo uma lista de recomendação de imóveis 
a serem adquiridos.
Caso a recomendação seja seguida, o lucro bruto obtido pela empresa pode chegar ao
valor de  $ 314,641,855.40
