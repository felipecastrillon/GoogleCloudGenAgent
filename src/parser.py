from typing import Optional, Sequence

from google.api_core.client_options import ClientOptions
from google.cloud import documentai
import config
import tabulate as tb
import pdb
import json


class DocAIParser():
  # modified from https://cloud.google.com/document-ai/docs/samples/documentai-process-form-document 
  
  def __init__(self, project, location, processor_id, processor_version):
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
    self.name = self.client.processor_version_path(project, location,processor_id, processor_version)

  def read_text(self, processed_document, contains_table, table_indexes=None):
   
    text = processed_document.text
 
    if contains_table:
      if table_indexes == None or len(table_indexes) <= 0:
        raise Exception("if contains_tables is selected the table index must be non empty")
 
      unstructured_text = ""
      index_one = 0

      # get all text that is not part of tables
      for indexes in table_indexes:
        index_two = indexes["start"]
        unstructured_text += text[index_one:index_two] + "\n\n"
        index_one = indexes["end"]
      unstructured_text += text[index_one:len(text)-1] 
    else:
      unstructured_text = text

    return unstructured_text 

  def read_tables(self, processed_document):
    chunks = [] 
    indexes = [] 
    
    text = processed_document.text 

    for page in processed_document.pages:
      
      for table in page.tables:
        rows = self.print_table_rows(table.body_rows, text)
        header =  self.print_table_rows(table.header_rows, text)[0]

        # chunking strategy by table or by row level
        if config.TABLE_CHUNKING_OPTIONS=="by_table":     
          header = [header]
          pretty_table = header + rows 
          pretty_table=tb.tabulate(pretty_table, headers="firstrow", tablefmt="pretty")
          chunks.append(pretty_table) 
        elif config.TABLE_CHUNKING_OPTIONS=="by_row":
          for row in rows:
            if len(row) == len(header) :   
              mapping = {key: value for key, value in zip(header, row)}
              json_object = json.dumps(mapping)
              chunks.append(json_object) 
        else:
          Exception("please choose a valid option for TABLE_CHUNKING_OPTIONS")
        
        # store indexes of tables    
        cells = table.layout.text_anchor.text_segments
        max_index = 0
        min_index = 99999999 
        for cell in cells:
            if cell.start_index < min_index:
                min_index = cell.start_index
            if cell.end_index > max_index:
                max_index = cell.end_index
        indexes.append({"start":min_index,"end":max_index})
        indexes = self.non_overlapping_indexes(indexes) 

    return chunks, indexes

  def read_entities(self, processed_document):
    chunks = []
    entities = processed_document.entities
    for entity in entities:
      key = entity.type
      value = entity.mention_text
      chunks.append(key + " is " + value)
    return chunks
    
  def non_overlapping_indexes(self, indexes):
    """
    This function takes a list of indexes and returns a new list of indexes
    that does not include any overlaps.

    Args:
k     indexes: A list of dictionaries, where each dictionary has keys 'start' and 'end'
        specifying the start and end indices of a range.

    Returns:
      A new list of dictionaries, where each dictionary has keys 'start' and 'end'
        specifying the non-overlapping ranges.
    """

    # Sort the indexes by their starting points.
    sorted_indexes = sorted(indexes, key=lambda x: x["start"])

    # Initialize an empty list to store the non-overlapping indexes.
    non_overlapping_indexes = []

    # Iterate through the sorted indexes.
    for index in sorted_indexes:
      # If the current index does not overlap with the last index in the
      # non_overlapping_indexes list, add it to the list.
      if not non_overlapping_indexes or index["start"] > non_overlapping_indexes[-1]["end"]:
        non_overlapping_indexes.append(index)
      # Otherwise, update the end index of the last index in the list to the
      # maximum of the current index's end and the last index's end.
      else:
        non_overlapping_indexes[-1]["end"] = max(non_overlapping_indexes[-1]["end"], index["end"])

    return non_overlapping_indexes


  def layout_to_text(self, layout: documentai.Document.Page.Layout, text: str) -> str:
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
 
 
  def print_table_rows(self,
        table_rows: Sequence[documentai.Document.Page.Table.TableRow], text: str
    ) -> None:
    rows = []
    for table_row in table_rows:
        row_text = []
        for cell in table_row.cells:
            cell_text = self.layout_to_text(cell.layout, text)
            row_text.append(cell_text.strip().replace("\n",""))
        rows.append(row_text)
    return rows

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


