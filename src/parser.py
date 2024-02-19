from typing import Optional, Sequence

from google.api_core.client_options import ClientOptions
from google.cloud import documentai
import config
import tabulate as tb


class DocAIParser():

  # modified from https://cloud.google.com/document-ai/docs/samples/documentai-process-form-document 
  
  def __init__(self):
    # document ai client
    # You must set the `api_endpoint` if you use a location other than "us".
    self.client = documentai.DocumentProcessorServiceClient(
        client_options=ClientOptions(
            api_endpoint=f"{config.LOCATION}-documentai.googleapis.com"
        )
    )


    # The full resource name of the processor version, e.g.:
    # `projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}`
    # You must create a processor before running this sample.
    self.name = self.client.processor_version_path(config.PROJECT, config.LOCATION, config.PROCESSOR_ID, config.PROCESSOR_VERSION)


  def read_text(self, processed_document):
    return processed_document.text

  def read_tables(self, processed_document):
    tables = [] 
    
    text = self.read_text(processed_document)
 
    def print_table_rows(
        table_rows: Sequence[documentai.Document.Page.Table.TableRow], text: str
    ) -> None:
        rows = []
        for table_row in table_rows:
            row_text = []
            for cell in table_row.cells:
                cell_text = layout_to_text(cell.layout, text)
                row_text.append(cell_text.strip().replace("\n",""))
            rows.append(row_text)
        return rows

    def layout_to_text(layout: documentai.Document.Page.Layout, text: str) -> str:
      """ Document AI identifies text in different parts of the document by their
      offsets in the entirety of the document"s text. This function converts
      offsets to a string.
      """
      # If a text segment spans several lines, it will
      # be stored in different text segments.
      return "".join(
          text[int(segment.start_index) : int(segment.end_index)]
          for segment in layout.text_anchor.text_segments
      )

    for page in processed_document.pages:
      print(f"\n\n**** Page {page.page_number} ****")
      
      print(f"\nFound {len(page.tables)} table(s):")
      for table in page.tables:
          num_columns = len(table.header_rows[0].cells)
          num_rows = len(table.body_rows)
          
          table= print_table_rows(table.header_rows, text) + print_table_rows(table.body_rows, text)
          pretty_table=tb.tabulate(table,headers="firstrow", tablefmt="pretty")
          tables.append(pretty_table) 
     
    return tables
     
  def process_document(self) -> documentai.Document:

    # Read the file into memory
    with open(config.FILENAME, "rb") as image:
        image_content = image.read()

    # Configure the process request
    request = documentai.ProcessRequest(
        name=self.name,
        raw_document=documentai.RawDocument(content=image_content, mime_type="application/pdf"),
    )

    result = self.client.process_document(request=request)

    # For a full list of `Document` object attributes, reference this page:
    # https://cloud.google.com/document-ai/docs/reference/rest/v1/Document
    return result.document


