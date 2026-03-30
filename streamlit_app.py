# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
from snowflake.snowpark.functions import col, when_matched
# Write directly to the app
st.title(f" :cup_with_straw: Example Streamlit App :cup_with_straw: {st.__version__}")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input('Name on smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# option = st.selectbox(
#     'What is your favourite fruit?',
#     ('Banana','Strawberry', 'Peaches')
# )

# st.write('Your favourite fruit is a:', option)


session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list =st.multiselect(
    'Choose up to five ingredients:',
    my_dataframe,
    max_selections = 5
)

#removing [] when space is empty
if ingredients_list:
    # st.write(ingredients_list)
    # st.text(ingredients_list)

    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '


    my_insert_stmt =  """ insert into smoothies.public.orders(
                 values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    st.write(my_insert_stmt)
    st.stop() #great for troubleshooting
    
    time_to_insert= st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect() 
            
    #     st.success('Your Smoothie is ordered! ', icon="✅")

# Write directly to the app
st.title(" :cup_with_straw: Pending Smoothie Orders! :cup_with_straw: ")
st.write(
      """Orders that need to be filled.
  """
)

session = get_active_session()
my_dataframe = session.table("smoothies.public.orders") \
    .filter(col("ORDER_FILLED"), when_matched == 0) \
    .collect()
#st.dataframe(data=my_dataframe, use_container_width=True)


if my_dataframe:
    #converts to data editor
    editable_df = st.data_editor(my_dataframe)
    
    submitted = st.button('Submit')
    
    if submitted:
    
        try:
            og_dataset = session.table("smoothies.public.orders")
            edited_dataset = session.create_dataframe(editable_df)
            og_dataset.merge(edited_dataset
                        , (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID'])
                        , [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
                    )
            st.success('Order(s) Updated!',icon = "👍" )
        except:
            st.write("Something went wrong.")

else: 
    st.success('There are no pending orders right now', icon = "👍")
