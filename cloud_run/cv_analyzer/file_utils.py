import fitz
import io


def convert_to_text(file):
    doc = fitz.open(stream=file, filetype="pdf")
    text = ''
    for page in doc:
        text += page.get_text()

    return text


def highlight_processing(file, to_highlight_list, highlight_color):
    pdf_stream = io.BytesIO()
    doc = fitz.open(stream=file, filetype="pdf")
    if len(to_highlight_list) > 0:
        for page_num in range(len(doc)):
            page = doc[page_num]
            for text_to_highlight in to_highlight_list:
                text_instances = page.search_for(text_to_highlight)

                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.set_colors(stroke=highlight_color)
                    highlight.update()
    doc.save(pdf_stream)
    doc.close()
    pdf_stream.seek(0)
    return pdf_stream
