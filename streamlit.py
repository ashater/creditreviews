import streamlit as st
import pandas as pd
# import boto3
# import fitz



st.set_page_config(
    page_title = 'Apparatus Doctrina: Dashboard',
    layout = 'wide'
)


tab1, tab2, tab3 = st.tabs(["Report Generation", "PDF Search", "Chatbot"])

# near real-time / live feed simulation 

with tab1:
    #while True:
    # dashboard title

    st.title("Credit Risk Report Dashboard")
    # uploaded_files = st.file_uploader("Choose a CSV file")
    # if uploaded_files is not None:
    #     # To read file as bytes:
    #     bytes_data = uploaded_files.getvalue()
    #     st.write(bytes_data)
    #
    #     # To convert to a string based IO:
    #     stringio = StringIO(uploaded_files.getvalue().decode("utf-8"))
    #     st.write(stringio)
    #
    #     # To read file as string:
    #     string_data = stringio.read()
    #     st.write(string_data)
    company_list = ["WF", "GS", "MS", "JPM"]
    report_periods = ("2021Q1", "2021Q2", "2021Q3", "2021Q4", "2022Q1")

    col1, col2 = st.columns(2)
    with col1:
        company = st.selectbox(
            "Select the company for analysis",
            tuple(company_list), key='1')

        report_period = st.selectbox(
            "Select period for analysis",
            report_periods, key='2')

    with col2:

        if company in company_list:
            compares_list = company_list.copy()
            compares_list.remove(company)
        else:
            compares_list = company_list.copy()
        comps = st.multiselect("Select comparables for analysis",
                               compares_list, key='3')

        period = st.radio("Analysis Period",
                          ["Quarterly", "Annual"], key='4')
        period_decrease = 1 if period=="Quarterly" else 4


    with st.container():
        st.markdown("### Select sections for inclusion in the report")
        Sec1 = st.checkbox("Company Overview", key='5')
        Sec2 = st.checkbox("Recent Material Changes", key='6')
        Sec3 = st.checkbox("Key Considerations", key='7')
        Sec4 = st.checkbox("ESG Summary", key='8')
        Sec5 = st.checkbox("Financial Update", key='9')
        Sec6 = st.checkbox("Capitalization and Liquidity", key='10')
        Sec7 = st.checkbox("Enterprise Valuation", key='11')
        if Sec7:
            on = st.checkbox("New Valuation Required", key='12')





        prompt1_for_llm = 'Provide analysis for ' + company + ' in ' + report_period + ' compared to ' + \
                                  str(pd.Period(report_period, freq='Q')-period_decrease)
        st.write(prompt1_for_llm)
        if len(comps)==0:
            prompt2_for_llm = 'Provide standalone analysis of ' + company
        else:
            if len(comps)==1:
                sel_comps = comps[0]
            elif len(comps)==2:
                sel_comps = comps[0] + ' and ' + comps[1]
            else:
                sel_comps = ', '.join(comps[:-1]) + ' and ' + comps[-1]
            prompt2_for_llm = 'Compare the performance of ' + company + ' to ' + sel_comps

        st.write(prompt2_for_llm)

        st.download_button("Generate Report", prompt1_for_llm, key='13')

with tab2:
    st.header("PDF Search")
    # with st.sidebar:
    #     original_doc = st.file_uploader(
    #         "Upload PDF", accept_multiple_files=False, type="pdf"
    #     )
    #     text_lookup = st.text_input("Look for", max_chars=50)
    #
    # if original_doc:
    #     with fitz.open(stream=original_doc.getvalue()) as doc:
    #         page_number = st.sidebar.number_input(
    #             "Page number", min_value=1, max_value=doc.page_count, value=1, step=1
    #         )
    #         page = doc.load_page(page_number - 1)
    #
    #         if text_lookup:
    #             areas = page.search_for(text_lookup)
    #
    #             for area in areas:
    #                 page.add_rect_annot(area)
    #
    #             pix = page.get_pixmap(dpi=120).tobytes()
    #             st.image(pix, use_column_width=True)


with tab3:
    st.header("Chatbot")
    # session = boto3.session.Session()
    # region_name = session.region_name
    # bedrock_client = boto3.client('bedrock-agent-runtime')
    #
    # client = session.client(
    #     service_name='secretsmanager',
    #     region_name=region_name
    # )
    #
    # get_secret_value_response = client.get_secret_value(
    #     SecretId=secret_name
    # )
    #
    # secret = get_secret_value_response['SecretString']
    # parsed_secret = json.loads(secret)
    #
    # knowledge_base_id = parsed_secret["KNOWLEDGE_BASE_ID"]
    #
    # # Initialize conversation history if not present
    # if 'conversation_history' not in st.session_state:
    #     st.session_state.conversation_history = []
    #
    # user_input = st.text_input("You: ")
    #
    # if st.button("Send"):
    #     # Retrieve and Generate call
    #     response = bedrock_client.retrieve_and_generate(
    #         input={"text": user_input},
    #         retrieveAndGenerateConfiguration={
    #             "knowledgeBaseConfiguration": {
    #                 "knowledgeBaseId": knowledge_base_id,
    #                 "modelArn": f"arn:aws:bedrock:{region_name}::foundation-model/anthropic.claude-v2"
    #             },
    #             "type": "KNOWLEDGE_BASE"
    #         }
    #     )
    #     print(response)
    #     # Extract response
    #     response_text = response['output']['text']
    #
    #     # Check if there are any retrieved references
    #     if not response['citations'][0]['retrievedReferences']:
    #         # No references found, use the response text
    #         display_text = response_text
    #     else:
    #         # Handle normal case with references
    #         # Extract S3 URI (assuming references are present)
    #         s3_uri = response['citations'][0]['retrievedReferences'][0]['location']['s3Location']['uri']
    #         display_text = f"{response_text}<br><br>Reference: {s3_uri}"
    #
    #     # Insert the response at the beginning of the conversation history
    #     st.session_state.conversation_history.insert(0, ("Assistant", f"<div class='response'>{display_text}</div>"))
    #     st.session_state.conversation_history.insert(0, ("You", user_input))
    #
    #     # Display conversation history
    #     for speaker, text in st.session_state.conversation_history:
    #         if speaker == "You":
    #             st.markdown(user_template.replace("{{MSG}}", text), unsafe_allow_html=True)
    #         else:
    #             st.markdown(text, unsafe_allow_html=True)