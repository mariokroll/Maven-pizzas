import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET


def get_pizza_ingredients(df: pd.DataFrame) -> list:
    """
    Get all the different ingredients from the pizza_types.csv file
    """
    diff_ing = df['ingredients'].str.split(', ').explode().unique()
    diff_ing_strip = [i.strip() for i in diff_ing]
    return diff_ing_strip


def extract() -> tuple:
    """
    Extract the data from the csv files
    """
    order_details = pd.read_csv('order_details.csv')
    orders = pd.read_csv('orders.csv')
    pizzas = pd.read_csv('pizzas.csv')
    pizzas_types = pd.read_csv('pizza_types.csv', encoding='unicode_escape')
    return order_details, orders, pizzas, pizzas_types


def data_info(order_details: pd.DataFrame, orders: pd.DataFrame, pizzas: pd.DataFrame, pizzas_types: pd.DataFrame) -> pd.DataFrame:
    """
    Before start making predictions, let's have some information about the data, like the shape of the dataframes,
    the number of NaN or null values, the number of unique values or the type of the columns, represented in dictionaries
    """
    # Create a DataFrame that will contain the information
    info = {'order_details': {}, 'orders': {}, 'pizzas': {}, 'pizzas_types': {}}

    for csv in info.keys(): 
        # Get the shape of the dataframes
        info[csv]['shape'] = eval(csv).shape

        # Get the number of Na values per column
        info[csv]['na'] = eval(csv).isna().sum().to_dict()

        # Get the number of unique values per column
        info[csv]['unique'] = eval(csv).nunique().to_dict()

        # Get the type of each column
        info[csv]['type'] = eval(csv).dtypes.to_dict()

    return info


def transform(order_details: pd.DataFrame, orders: pd.DataFrame, pizzas: pd.DataFrame, pizzas_types: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the data and get the prediction of the ingredients per week for 2016
    """
    ing_dict = {}
    # Get all different ingredients
    ing = get_pizza_ingredients(pizzas_types)
    for i in ing:
        ing_dict[i] = [0]*53

    # Merge order_details and orders so that we can work with one dataframe that contains
    # the order_id, the pizza_id and the date of the order
    df_merged = pd.merge(order_details, orders)

    # Transform the dates to datetime format
    df_merged['date'] = pd.to_datetime(df_merged['date'], format='%d/%m/%Y')

    # Create a new column that contains the week of the year (1-53)
    df_merged['week'] = df_merged['date'].dt.isocalendar().week

    # Create a dictionary that contains the quantity of the ingredients per size
    sizes = {'s': 1, 'm': 2, 'l': 3, 'xl': 4, 'xxl': 5}

    # Iterate the DataFrame to study the pizzas one by one
    for i in range(df_merged.shape[0]):
        # Get the row
        row = df_merged.loc[i]

        # Get the name of the pizza
        pizza_name = row['pizza_id']

        # We separate cases by size
        if pizza_name[-4:] == '_xxl':
            # Get the ingredients of the pizza from the row
            ings = pizzas_types.loc[pizzas_types['pizza_type_id'] == pizza_name[:-4]]['ingredients'].values[0].split(',')

            # We add the amount of the ingredients used, according to its size
            for ingr in ings:
                ingr_strip = ingr.strip()
                ing_dict[ingr_strip][row.week - 1] += sizes[pizza_name[-3:]]
        elif pizza_name[-3:] == '_xl':
            # Get the ingredients of the pizza from the row
            ings = pizzas_types.loc[pizzas_types['pizza_type_id'] == pizza_name[:-3]]['ingredients'].values[0].split(',')

            # We add the amount of the ingredients used, according to its size
            for ingr in ings:
                ingr_strip = ingr.strip()
                ing_dict[ingr_strip][row.week - 1] += sizes[pizza_name[-2:]]
        else:
            # Get the ingredients of the pizza from the row
            ings = pizzas_types.loc[pizzas_types['pizza_type_id'] == pizza_name[:-2]]['ingredients'].values[0].split(',')
            
            # We add the amount of the ingredients used, according to its size
            for ingr in ings:
                ingr_strip = ingr.strip()
                ing_dict[ingr_strip][row.week - 1] += sizes[pizza_name[-1]]

    # Generate a new DataFrame
    prediction = pd.DataFrame(index=['week_'+str(i) for i in range(1, 54)])

    # Calculate the annual mean for each ingredient
    annual_mean = {}
    for k in ing_dict.keys():
        annual_mean[k] = sum(ing_dict[k]) / 53
    
    # We add the prediction for each ingredient per week
    # The prediction for a week is calculated by calculating the mean between
    # the ingredients of the week before, the week after and the annual mean
    for w in range(53):
        for k in ing_dict.keys():
            prediction.loc['week_'+str(w+1), k] = (annual_mean[k] + ing_dict[k][w-1] + ing_dict[k][(w+1)%53])/3

    return prediction


def load(prediction: pd.DataFrame, info_from_data: dict) -> None:
    """
    Load the prediction DataFrame to a csv file and the info_from_data into a xml file
    """
    # prediction.to_csv('2016_prediction.csv')

    # Create the tree
    root = ET.Element('info_from_data')
    for key in info_from_data.keys():

        # Create the first subelement, that is the file name
        m1 = ET.SubElement(root, 'file', name=key)
        for k in info_from_data[key]:

            # Create a new subelement, that is the info attribute
            m2 = ET.SubElement(m1, 'info', attribute=k)

            # If the new subelement is another dictionary, we create a new subelement adding the information that
            # the dictionary contains. If not, we write directly the info of the subelement
            if type(info_from_data[key][k]) == dict:
                for col in info_from_data[key][k]:
                    m3 = ET.SubElement(m2, 'column', name=col)
                    m3.text = str(info_from_data[key][k][col])
            else:
                m2.text = str(info_from_data[key][k])

    # Create the tree
    tree = ET.ElementTree(root)

    # Create the xml file
    tree.write('info_from_data.xml')
    return


if __name__ == '__main__':
    order_details, orders, pizzas, pizzas_types = extract()
    info = data_info(order_details, orders, pizzas, pizzas_types)
    prediction = transform(order_details, orders, pizzas, pizzas_types)
    load(prediction, info)