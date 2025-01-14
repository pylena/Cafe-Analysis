import streamlit as slt
import streamlit as st
from itertools import combinations
from collections import Counter
import pandas as pd
import plotly.express as px

# Apply RTL style
st.markdown(
    """
    <style>
    body {
        direction: rtl;
        text-align: right; 
    }
    h1{
    text-align: center
    }
    h4{
    text-align:right;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

st.title("محتار وش تطلب مع مشروبك؟ تعال نساعدك تختار كومبو يجيب رأسك")
st.image('logo.jpeg')
st.write("وش نوع مشروبك؟ اختر مشروبك المفضل ونوع العناصر اللي تبي توصيات منها")

# Load data
coffee_df_no_beans = pd.read_csv('data/recommendation.csv')

# Filter the data to include only allowed drinks
allowed_drinks = [
    "v60 (iced)", "coffee of the day (iced)", "spanish latte", "cappuccino", "iced tea karkadih",
    "cortado", "coffee of the day (hot)", "flat white", "ice shaken white mocha", "espresso",
    "macchiato", "code red", "v60 (hot)", "tea", "americano", "latte", "english tea",
    "winter signture", "karak", "salted caramel latte", "raspberry mojito", "classic mojito",
    "green tea", "hot chocolate", "cold brew", "cup of ice", "passion fruit mojito",
    "iced matcha latte", "codered can", "iced caramel macchiato", "caramel latte", "peach ice tea",
    "pink bloom mojito", "hot mocha", "shaken latte", "v60 (hot, iced)", "pina colada",
    "chocolate frappe", "coffee of the day (hot, iced)", "vanilla frappe"
]
filter_df = coffee_df_no_beans[coffee_df_no_beans['الصنف_adjusted'].isin(allowed_drinks)]

# Helper functions for analysis
def group_items(df):
    return df.groupby('رقم الايصال')[['الصنف_adjusted', 'الفئة']].apply(lambda x: list(zip(x['الصنف_adjusted'], x['الفئة'])))

def generate_pairs(grouped_items):
    pairs = []
    for items in grouped_items:
        if len(items) > 1:
            pairs.extend(combinations(sorted(items), 2))
    return pairs

def count_pairs(pairs):
    return Counter(pairs)

def create_recommendations(pair_counts):
    recommendations = {}
    for (item1, item2), count in pair_counts.items():
        item1_name, item1_category = item1
        item2_name, item2_category = item2

        # Add item2 as a recommendation for item1
        if item1_name not in recommendations:
            recommendations[item1_name] = []
        recommendations[item1_name].append((item2_name, item2_category, count))

        # Add item1 as a recommendation for item2 (symmetry)
        if item2_name not in recommendations:
            recommendations[item2_name] = []
        recommendations[item2_name].append((item1_name, item1_category, count))

    # Sort recommendations by count (descending)
    for key in recommendations:
        recommendations[key] = sorted(recommendations[key], key=lambda x: x[2], reverse=True)
    return recommendations

def recommend_items(recommendations, drink, category, top_n=5):
    if drink in recommendations:
        return [
            (item, freq) 
            for item, cat, freq in recommendations[drink] 
            if cat == category
        ][:top_n]
    else:
        return []

def plot_recommendations_plotly(top_recommendations, drink):
    if top_recommendations:
        items, counts = zip(*top_recommendations)
        fig = px.bar(
            x=items, 
            y=counts, 
            title=" ",
            
        )
        
        fig.update_layout(
            margin=dict(l=50, r=100, t=50, b=150),  # Increase bottom margin for long labels
            xaxis_title="",
            yaxis_title="",
            title_font_size=16,
            showlegend=False,
        )
        fig.update_traces(
    marker=dict(color='#cc8589')  # Set your desired color
)
        st.plotly_chart(fig)

# User selects a drink category
drink_categories = ['Hot espresso drink', 'Cold espresso drink', 'Tea', 'Iced tea', 'Drip coffee', 'Mojito']
selected_drink_category = st.selectbox("اختر نوع المشروب:", options=drink_categories)

# User selects a drink
if selected_drink_category:
    drinks_in_category = filter_df[filter_df['الفئة'] == selected_drink_category]['الصنف_adjusted'].unique()

    drinks_in_categoryT = [drink.capitalize() for drink in drinks_in_category if drink != 'cup of ice']

    # Display the selectbox with capitalized options
    selected_drinkT = st.selectbox("اختر مشروبك:", options=sorted(drinks_in_categoryT))

    # Convert the selected drink back to lowercase for processing
    selected_drink = selected_drinkT.lower()

# User selects a recommendation category
recommendation_categories = coffee_df_no_beans['الفئة'].unique()
recommendation_categories = [cat for cat in recommendation_categories if (cat != 'Accessories') and (cat != 'More') and (cat != 'Coffee Beans')]
selected_recommendation_category = st.selectbox("اختر النوع اللي تبي التوصية منها:", options=sorted(recommendation_categories))

if st.button("طلع لي التوصيات"):
    if selected_drink and selected_recommendation_category:
        grouped_items = group_items(coffee_df_no_beans)
        pairs = generate_pairs(grouped_items)
        pair_counts = count_pairs(pairs)
        recommendations = create_recommendations(pair_counts)

       
        top_recommendations = recommend_items(recommendations, selected_drink, selected_recommendation_category, top_n=10)
        top_recommendations2 = recommend_items(recommendations, selected_drink, selected_recommendation_category, top_n=1)

        if top_recommendations:
            
            for item, freq in top_recommendations2:
                st.write(f"#### *{item.capitalize()}*  هو أكثر صنف الناس يطلبونه مع  *{selected_drink.capitalize()}* (طلبوه مع بعض  {freq} مرة).")
            st.markdown("<hr>", unsafe_allow_html=True)
            st.write(f"#### الأصناف اللي الناس تطلبها كثير مع {selected_drink.capitalize()} من نوع {selected_recommendation_category.capitalize()} :")
            plot_recommendations_plotly(top_recommendations, selected_drink)
        else:
            st.write("لا توجد توصيات لهذا المنتج")