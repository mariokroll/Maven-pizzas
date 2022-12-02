# Maven pizzas
## Archivos
- pizzas.py: script de python que hace una predicción de los ingredientes para 2016.
- order_details.csv: fichero que contiene información sobre la cantidad de pizzas ordenadas en un pedido y el identificador del pedido.
- orders.csv: fichero que contiene información sobre las fechas del pedido, al igual que el identificador del pedido.
- pizza_types.csv: fichero que contiene información sobre cada tipo de pizza, como una descripción y los ingredientes que la conforman.
- pizzas.csv: fichero que contiene información sobre el precio de cada pizza en relación a su tamaño.
- data_dictionary.csv: fichero que contiene información sobre los csv previamente descritos.
- 2016_prediction.csv: fichero que contiene la predicción de ingredientes de cada semana para un año.
- info_from_data.xml: fichero que contiene el informe de datos de cada fichero csv.
- requirements.txt: fichero de texto que contiene las librerías necesarias y sus versiones para la ejecución del script.

## Descripción del script
En la elaboración del programa se ha seguido una estructura ETL. Para poder calcular la predicción de los ingredientes necesarios, hemos tenido que agrupar por semanas los pedidos y calcular cuántos ingredientes se han usado de media en una semana. Luego, la media de los ingredientes usados en una semana se calcula hallando la media de los ingredientes de la semana anterior, la semana siguiente y la anual.
Posteriormente, dichos datos son exportados a un csv, llamado "2016_prediction.csv".
