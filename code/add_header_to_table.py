import json
import re
import pandas as pd

def add_header_to_table_html(tbl_html: str, caption: str):
    
    #re.sub('^<table.*?>', '<table><caption>'+caption+'</caption>', ret)
    return tbl_html.replace('<table>','<table><caption>'+caption+'</caption>')
    

def load_basic_json(filename: str):
    
    d = []
    new_file = filename.replace('unst','unst_basic')
    print('Processing '+new_file)
    with open(new_file, 'rt') as f:
        d = f.readlines()
    
    jsn = json.loads(''.join(d))
    recs = pd.DataFrame.from_records(jsn, index='element_id')
    def get_parent_text(id:str):
        p = recs.loc[id]
        if 'parent_id' not in p['metadata'].keys():
            return p['text'] 
        else:
            return p['text'] +' ' + get_parent_text(p['metadata']['parent_id'])
        
    v = recs[recs.type =='Table']['metadata'].map(lambda x: get_parent_text(x['parent_id']))

    new_tbl_nodes = list(filter(lambda x: x['type'] == 'Table', jsn))
    
    for node in new_tbl_nodes:
        new_hdr = str(v.loc[node['element_id']])
        node['metadata']['text_as_html'] = add_header_to_table_html( node['metadata']['text_as_html'], new_hdr)
        node['text'] = new_hdr + ' ' + node['text']

    
    with open(filename.replace('unst','unst_hacked_tbl'), 'wt') as f2:
        f2.writelines(json.dumps(new_tbl_nodes, indent=4))

def process_json(filename: str, parent_header_df):
    
    with open(filename, 'rt') as f:
        d = f.readlines()
    
    jsn = json.loads(''.join(d))
    for el in jsn:
        if el['type'] == 'Table':
            pass


def convert_file(filename):
    raw_pdf_elements = partition_pdf(
                        filename=filename,
                        # Unstructured first finds embedded image blocks
                        extract_images_in_pdf=False,
                        # Use layout model (YOLOX) to get bounding boxes (for tables) and find titles
                        # Titles are any sub-section of the document
                        infer_table_structure=True,
                        # Post processing to aggregate text once we have the title


                        # Chunking params to aggregate text blocks
                        # Attempt to create a new chunk 3800 chars
                        # Attempt to keep chunks > 2000 chars
                        chunking_strategy="by_title",
                        max_characters=10000,
                        new_after_n_chars=9000,
                        combine_text_under_n_chars=2000,
                        image_output_dir_path='imgs')
                                                                                                                                    
    elements_to_json(raw_pdf_elements, filename=f"json/unst_basic_2_{filename}.json")


if __name__ == '__main__':
    v = "<table><thead><th>Results Announcement</th><th>Page</th></thead><tr><td>Notes</td><td></td></tr><tr><td>Performance Highlights</td><td></td></tr><tr><td colspan=\"2\">Group Finance Director's Review</td></tr><tr><td>Results by Business + UK</td><td></td></tr><tr><td>Barclays + Barclays International</td><td></td></tr><tr><td>+ Head Office</td><td></td></tr><tr><td>Quarterly Results Summary</td><td></td></tr><tr><td>Quarterly Results by Business</td><td>20</td></tr><tr><td colspan=\"2\">Performance Management</td></tr><tr><td>* Margins and Balances</td><td>26</td></tr><tr><td>+ Remuneration</td><td>27</td></tr><tr><td colspan=\"2\">Risk Management</td></tr><tr><td>+ Risk Management and Principal Risks</td><td>29</td></tr><tr><td>* Credit Risk</td><td>30</td></tr><tr><td>+ Market Risk</td><td>50</td></tr><tr><td>* Treasury and Capital Risk</td><td>51</td></tr><tr><td>Condensed Consolidated Financial Statements</td><td>60</td></tr><tr><td>Financial Statement Notes</td><td>65</td></tr><tr><td>Appendix: Non-IFRS Performance Measures</td><td>69</td></tr><tr><td>Shareholder Information</td><td>78</td></tr></table>"
    #g = load_basic_json('unstHY24-BPLC-Results-RA.pdf.json')
    #print(g)

    #print(add_header_to_table_html(v, "My Fat Test"))
    barc_list = ['HY24-BPLC-Results-RA.pdf', 'Q124-BPLC-Results-RA.pdf','Barclays-Q12023-Results-Announcement.pdf','Barclays-Q32023-Results-Announcement.pdf','Barclays-H12023-Results-Announcement.pdf','20240220-BPLC-FY2023-RA.pdf']

    for b in barc_list:
        load_basic_json('unst'+b+'.json')
