from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
import fitz
import os
import pickle, json

from typing import Any

from pydantic import BaseModel
from unstructured.partition.pdf import partition_pdf

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file


def load_content_using_fitz_ftrst(file_loc, pages_pull, buffer):
    toc = fitz.open(file_loc).get_toc()

    if len(toc) == 0:
        print('TOC load failed, use LLM')
        #### cannot find table of content, use llm
        llm_response = load_content_using_llm(file_path, pages_pull)

        page_range, section_name = fetch_content_page(llm_response, buffer)

        return page_range, section_name, llm_response

    else:
        print('use TOC load')
        ##### use toc loaded content table to generate page_range, section_name
        ##### seems always called part and item
        which_part = ''
        which_item = ''

        section_name = []
        starting_page = []

        for line in toc:
            if len(line) < 3:
                continue
            ##### each of them is a list
            if line[1].lower().startswith('part '):
                which_part = line[1].lower().strip()

            elif line[1].lower().startswith('item '):
                which_item = line[1].lower().strip()

            if len(which_part) > 0 or len(which_item) > 0:
                c_page_num = line[-1]

                section_name.append(which_part + '_' + which_item + '_' + line[1])
                starting_page.append(c_page_num)

        starting_page.append(1000)  #### add 1000 to the end
        #### provide the range

        page_range = [(startp - buffer, endp + buffer) for startp, endp in zip(starting_page[:-1], starting_page[1:])]

        return page_range, section_name, toc


def fetch_content_page(content, buffer=3):
    #### since not all 10-k starts couting pages on the first one.

    ##### seems always called part and item
    which_part = ''
    which_item = ''

    section_name = []
    starting_page = []

    for line in content.split(':')[1].split('\n'):
        if 'part ' in line.lower():
            which_part = line.lower().strip()
        elif 'item ' in line.lower():
            which_item = line.lower().split('-')[0].strip()

        if len(which_part) > 0 and len(which_item) > 0 and len(line) > 0:
            #### extract the page number
            try:
                c_page_num = int(line.lower().split()[-1].strip())

                section_name.append(which_part + '_' + which_item + '_' + ' '.join(line.lower().split()[:-1]))
                starting_page.append(c_page_num)
            except:
                continue

    starting_page.append(1000)  #### add 1000 to the end
    #### provide the range

    page_range = [(startp - buffer, endp + buffer) for startp, endp in zip(starting_page[:-1], starting_page[1:])]

    return page_range, section_name


def load_content_using_llm(file_loc, pages_pull=5):
    '''
    use PyPDFLoader to get the first pages_pull number of pages and send to
    '''
    loader = PyPDFLoader(file_path=file_loc)
    docs = loader.load()

    new_text = '/n/n'.join([doc.page_content for doc in docs[:pages_pull]])

    model = ChatAnthropic(
        model="claude-3-sonnet-20240229",
        temperature=0,
        max_tokens=1024,
        timeout=None,
        max_retries=2,
        api_key=os.environ.get("anthropic_API_KEY")
    )

    prompt_text = """Given the text. Could you help identify the table of content? \
    Please list the name of each section and the correspodning page number. \
    Below are the text: {text} """
    prompt = ChatPromptTemplate.from_template(prompt_text)

    # Summary chain
    summarize_chain = {"text": lambda x: x} | prompt | model | StrOutputParser()
    response = summarize_chain.invoke(new_text)

    return response


def load_unstructured_pdf_and_add_section(workdir, file_name, page_range, section_name, firm, time, **kwargs):
    # raw_pdf_elements = partition_pdf(
    # filename=file_path,
    ## Unstructured first finds embedded image blocks
    # extract_images_in_pdf=False,
    ## Use layout model (YOLOX) to get bounding boxes (for tables) and find titles
    ## Titles are any sub-section of the document
    # infer_table_structure=True,
    ## Post processing to aggregate text once we have the title
    # chunking_strategy="by_title",
    ## Chunking params to aggregate text blocks
    ## Attempt to create a new chunk 3800 chars
    ## Attempt to keep chunks > 2000 chars
    # max_characters=4000,
    # new_after_n_chars=3800,
    # combine_text_under_n_chars=2000,
    # image_output_dir_path=path,
    # kwargs
    # )
    file_path_json = os.path.join(workdir,'json', 'unst'+file_name+'.json')
    if os.path.isfile(file_path_json):
        raw_pdf_elements = json.load(open(file_path_json))
        is_json = True
    else:
        raw_pdf_elements = partition_pdf(
            filename=os.path.join(workdir,file_name),
            # Unstructured first finds embedded image blocks
            extract_images_in_pdf=False,
            # Use layout model (YOLOX) to get bounding boxes (for tables) and find titles
            # Titles are any sub-section of the document
            infer_table_structure=True,
            # Post processing to aggregate text once we have the title
            chunking_strategy="by_title",
            # Chunking params to aggregate text blocks
            # Attempt to create a new chunk 3800 chars
            # Attempt to keep chunks > 2000 chars
            max_characters=4000,
            new_after_n_chars=3800,
            combine_text_under_n_chars=2000,
    )
        is_json = False

    processed_docs = [None] * len(raw_pdf_elements)

    for idx, doc in enumerate(raw_pdf_elements):
        templist = []
        if is_json:
            doc_page = doc['metadata']['page_number']
        else:
            doc_page = doc.metadata.page_number
        for count_id, (range_s, range_e) in enumerate(page_range):
            if doc_page >= range_s and doc_page <= range_e:
                ##### add section to it
                templist.append(section_name[count_id])

            elif doc_page < range_s:
                #### this range is ascending, means all possible sections matched, pass
                break

        ##### finally, covert section_name to string
        if len(templist) > 0:
            if is_json:
                doc['metadata']['section_name'] = firm + '_' + time + '_' + '.'.join(templist)
            else:
                doc.metadata.section_name = firm + '_' + time + '_' + '.'.join(templist)
        else:
            if is_json:
                doc['metadata']['section_name'] = firm + '_' + time
            else:
                doc.metadata.section_name = firm + '_' + time

        processed_docs[idx] = doc

    return processed_docs


def pdf_extract_worrkflow(workdir, file_name, firm, time, pages_pull=5, buffer=3, verbose=False):
    '''
    file_path: location of the pdf file
    pages_pull: initial paages to review to check the table of content
    buffer: buffer to identify the section (since not all page count starts from the beginning)
    '''
    file_path = os.path.join(workdir, file_name)

    page_range, section_name, response = load_content_using_fitz_ftrst(file_path, pages_pull, buffer)

    print('Start Loading the page number')

    new_docs = load_unstructured_pdf_and_add_section(workdir, file_name, page_range, section_name, firm, time)

    if verbose:
        return new_docs, page_range, section_name, response
    else:
        return new_docs


if __name__ == '__main__':
    workdir = r"/Users/Russell/Library/CloudStorage/Dropbox/MFE_Courses/langchain_deeplearning/10_KQ"
    file_name = "bank_of_america_10Q_2024_Q1.pdf"
    pages_pull = 5  #### pull first 5 pages to find content

    buffer = 3
    verbose = True

    docs, page_range, section_name, response = pdf_extract_worrkflow(workdir, file_name, 'bank_of_america', '2024_q1',
                                                                     pages_pull, buffer, verbose)

