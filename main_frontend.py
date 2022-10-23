import streamlit as st
import pandas as pd
import requests

st.header("PolyMoment: High-order Moments of Multivariate Polynomials")

# ---------------------------------------------------------------------------------------------------------------------
# Adding random variables
# ---------------------------------------------------------------------------------------------------------------------
st.subheader("Add Random Variables ([Guide](https://github.com/arvindrajan92/polymoment/blob/master/ProbabilityDensityFunction.pdf))")
with st.form(key="Variable form", clear_on_submit=True):
    def get_beta_1(distribution_type, variable_index):
        if distribution_type in ['student', 'trapezoidal', 'gamma', 'weibull', 'lognormal']:
            return f"b{variable_index}"
        elif distribution_type in ['beta']:
            return f"b{variable_index}_1"
        else:
            return None

    def get_beta_2(distribution_type, variable_index):
        if distribution_type in ['beta']:
            return f"b{variable_index}_2"
        else:
            return None

    def reset_form():
        dist_data = []
        cols = st.columns(2)
        for i in range(2):
            if i == 0:
                dist_data.append(
                    cols[i].selectbox(
                        label=st.session_state.df.columns[i + 1],
                        options=(
                            'uniform', 'trapezoidal', 'triangular', 'beta', 'normal', 'student', 'laplace', 'gamma',
                            'weibull', 'maxwell'
                        )
                    )
                )
            elif i == 1:
                dist_data.append(
                    cols[i].selectbox(
                        label=st.session_state.df.columns[i + 1],
                        options=('symmetrical', 'one_sided_right', 'one_sided_left')
                    )
                )
        return dist_data


    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame(
            columns=["Variable", "Distribution", "Symmetry type", "Translation", "Scale", "Beta1", "Beta2"]
        )

    dist_data = reset_form()

    if st.form_submit_button("Add"):
        row_index = st.session_state.df.shape[0] + 1
        row_data = [
            f"x{row_index}",
            dist_data[0],
            dist_data[1],
            f"m{row_index}",
            f"s{row_index}",
            get_beta_1(dist_data[0], row_index),
            get_beta_2(dist_data[0], row_index),
        ]
        st.session_state.df.loc[row_index] = row_data
        st.info(f"Added variable: x{row_index}")

    st.dataframe(st.session_state.df)


# ---------------------------------------------------------------------------------------------------------------------
# Adding polynomial expression
# ---------------------------------------------------------------------------------------------------------------------
st.subheader("Add polynomial expression")
expression = st.text_input(label='Polynomial expression (e.g., x1**2 + x2**2)')

if expression:
    st.write("Entered expression: ", expression)

# ---------------------------------------------------------------------------------------------------------------------
# Adding moment order and compute / or computer high-order statistics
# ---------------------------------------------------------------------------------------------------------------------
st.subheader("Compute high-order moment")
with st.form(key="Moment order form", clear_on_submit=False):
    def build_polymoment_input(order: int = None):
        polymoment_input = {}
        df_dict = st.session_state.df.to_dict()

        # polynomial expression
        polymoment_input.update(poly=expression)

        # variable distributions
        dist_data = {}
        for idx in range(st.session_state.df.shape[0]):
            dist_data.update(
                {
                    df_dict.get('Variable').get(idx + 1): {
                        "distribution": df_dict.get('Distribution').get(idx + 1),
                        "type": df_dict.get('Symmetry type').get(idx + 1),
                        "translation": df_dict.get('Translation').get(idx + 1),
                        "scale": df_dict.get('Scale').get(idx + 1),
                        "beta1": df_dict.get('Beta1').get(idx + 1),
                        "beta2": df_dict.get('Beta2').get(idx + 1)
                    }
                }
            )
        polymoment_input.update(dist=dist_data)

        # moment order
        if isinstance(order, int):
            polymoment_input.update(order=int(order))

        return polymoment_input


    def reset_moment_form():
        moment_order = []
        cols = st.columns(1)
        for i in range(1):
            if i == 0:
                moment_order.append(cols[i].number_input('Moment order', min_value=0, max_value=10))
        return moment_order[0]

    moment_order = reset_moment_form()

    # you can insert code for a list comprehension here to change the data (rwdta)
    # values into integer / float, if required
    cols = st.columns(5)
    buttons = [
        cols[0].form_submit_button(label='Moment'),
        cols[1].form_submit_button(label='Mean'),
        cols[2].form_submit_button(label='Variance'),
        cols[3].form_submit_button(label='Skewness'),
        cols[4].form_submit_button(label='Kurtosis'),
    ]

    if any(buttons) and not expression:
        st.error('Please provide a polynomial expression')
    elif any(buttons) and st.session_state.df.shape[0] == 0:
        st.error('Please add variable(s)')
    else:
        error_message = 'Something went wrong. Please check the variables and polynomial expression.'
        spinner_message = 'Wait for it...'
        base_url = 'http://127.0.0.1:8123/'
        if buttons[0]:
            with st.spinner(spinner_message):
                polymoment_input = build_polymoment_input(order=moment_order)
                r = requests.post(base_url + 'moment/', json=polymoment_input)

            if r.status_code == 200:
                st.text_area('Moment', value=r.json().get('result'), disabled=False, label_visibility="collapsed")
            else:
                st.error(error_message)
        elif buttons[1]:
            with st.spinner(spinner_message):
                polymoment_input = build_polymoment_input()
                r = requests.post(base_url + 'mean/', json=polymoment_input)

            if r.status_code == 200:
                st.text_area('Mean', value=r.json().get('result'), disabled=False, label_visibility="collapsed")
            else:
                st.error(error_message)
        elif buttons[2]:
            with st.spinner(spinner_message):
                polymoment_input = build_polymoment_input()
                r = requests.post(base_url + 'var/', json=polymoment_input)

            if r.status_code == 200:
                st.text_area('Variance', value=r.json().get('result'), disabled=False, label_visibility="collapsed")
            else:
                st.error(error_message)
        elif buttons[3]:
            with st.spinner(spinner_message):
                polymoment_input = build_polymoment_input()
                r = requests.post(base_url + 'skew/', json=polymoment_input)

            if r.status_code == 200:
                st.text_area('Skewness', value=r.json().get('result'), disabled=False, label_visibility="collapsed")
            else:
                st.error(error_message, r.err)
        elif buttons[4]:
            with st.spinner(spinner_message):
                polymoment_input = build_polymoment_input()
                r = requests.post(base_url + 'kurt/', json=polymoment_input)

            if r.status_code == 200:
                st.text_area('Kurtosis', value=r.json().get('result'), disabled=False, label_visibility="collapsed")
            else:
                st.error(error_message)