import os
import json
from lxml import etree

import streamlit as st

attachment_lookup = {}
floats = {}


def json_to_markdown(data):
    """
    Converts the given JSON data to Markdown.

    Args:
        data: The JSON data to convert.

    Returns:
        The Markdown string.
    """
    markdown_output = ""

    # Create a lookup dictionary for attachment-eid based on file-basename
    if "attachments" in data:
        for attachment in data["attachments"]:
            if "file-basename" in attachment and "attachment-eid" in attachment:
                file_basename = attachment["file-basename"]
                if file_basename not in attachment_lookup:
                    attachment_lookup[file_basename] = attachment["attachment-eid"]
                else:
                    if (
                        "attachment-type" in attachment
                        and attachment["attachment-type"] != "IMAGE-THUMBNAIL"
                    ):
                        attachment_lookup[file_basename] = attachment["attachment-eid"]

    # float
    if "floats" in data:
        for float_item in data["floats"]:
            if "$" in float_item and "id" in float_item["$"]:
                float_id = float_item["$"]["id"]
                floats[float_id] = float_item

    if isinstance(data, dict):
        if "#name" in data:
            tag_name = data["#name"]

            if tag_name == "para":
                markdown_output += handle_para(data)
            elif tag_name == "list":
                markdown_output += handle_list(data)
            elif tag_name == "math":
                markdown_output += handle_math(data)
            elif tag_name == "figure":
                markdown_output += handle_figure(data)
            elif tag_name == "table":
                markdown_output += handle_table(data)
            elif tag_name == "outline":
                markdown_output += handle_outline(data)
            elif tag_name == "sections":
                markdown_output += handle_sections(data)
            elif tag_name == "section-title":
                markdown_output += handle_section_title(data)
            elif tag_name == "simple-para":
                markdown_output += handle_simple_para(data)
            elif tag_name == "bold":
                markdown_output += handle_bold(data)
            elif tag_name == "italic":
                markdown_output += handle_italic(data)
            elif tag_name == "label":
                markdown_output += handle_label(data)
            elif tag_name == "cross-ref":
                markdown_output += handle_cross_ref(data)
            elif tag_name == "inter-ref":
                markdown_output += handle_inter_ref(data)
            elif tag_name == "intra-ref":
                markdown_output += handle_intra_ref(data)
            elif tag_name == "display":
                markdown_output += handle_display(data)
            elif tag_name == "textbox":
                markdown_output += handle_textbox(data)
            elif tag_name == "caption":
                markdown_output += handle_caption(data)
            elif tag_name == "textbox-body":
                markdown_output += handle_textbox_body(data)
            elif tag_name == "inline-figure":
                markdown_output += handle_inline_figure(data)
            elif tag_name == "link":
                markdown_output += handle_link(data)
            elif tag_name == "__text__":
                markdown_output += handle_text(data)
            else:
                if "_" in data:
                    markdown_output += handle_label(data)
                if "$$" in data:
                    markdown_output += json_to_markdown(data["$$"])

        elif "content" in data:
            markdown_output += json_to_markdown(data["content"])
        elif "floats" in data:
            markdown_output += json_to_markdown(data["floats"])
        # elif "attachments" in data:
        #     markdown_output += json_to_markdown(data["attachments"])

    elif isinstance(data, list):
        for item in data:
            markdown_output += json_to_markdown(item)

    return markdown_output


def handle_sections(data):
    markdown_output = ""
    if "$$" in data:
        markdown_output += json_to_markdown(data["$$"])
    return markdown_output


def handle_para(data):
    markdown_output = ""
    if "_" in data:
        markdown_output += handle_label(data)
    if "$$" in data:
        markdown_output += json_to_markdown(data["$$"])
    markdown_output += "\n\n"
    return markdown_output


def handle_simple_para(data):
    markdown_output = ""
    if "_" in data:
        markdown_output += handle_label(data)
    if "$$" in data:
        markdown_output += json_to_markdown(data["$$"])
    markdown_output += "\n\n"
    return markdown_output


def handle_list(data, level=0):
    markdown_output = ""
    current_level = level
    if "$$" in data:
        for item in data["$$"]:
            if item.get("#name") == "section-title":
                markdown_output += handle_section_title(item)

            if item.get("#name") == "list-item":
                if "$$" in item:
                    label = None
                    content = None
                    nested_content = ""

                    # First pass - get label, content and nested lists
                    for subitem in item["$$"]:
                        if subitem.get("#name") == "label":
                            label = handle_label(subitem)
                        elif subitem.get("#name") == "para":
                            content = handle_para(subitem).strip()
                        elif subitem.get("#name") == "list":
                            nested_content = handle_list(subitem, current_level + 1)

                    # Format the list item with proper indentation
                    if label and label[-1] == "." and label[:-1].isdigit():
                        # Ordered list item
                        markdown_output += (
                            "    " * current_level + f"{label} {content}\n"
                        )
                    else:
                        # Unordered list item
                        markdown_output += (
                            "    " * current_level + f"- {label} {content}\n"
                        )

                    # Add any nested content
                    if nested_content:
                        markdown_output += nested_content

            elif item.get("#name") == "list":
                markdown_output += handle_list(item, level + 1)

    return markdown_output


def mathml2latex_yarosh(equation):
    """MathML to LaTeX conversion with XSLT from Vasil Yaroshevich"""
    xslt_file = os.path.join("mathconverter", "xsl_yarosh", "mmltex.xsl")
    dom = etree.fromstring(equation)
    xslt = etree.parse(xslt_file)
    transform = etree.XSLT(xslt)
    newdom = transform(dom)
    return newdom


def mathml2latex_transpect(equation):
    """MathML to LaTeX conversion with XSLT from Transpect"""
    xslt_file = os.path.join("mathconverter", "xsl_transpect", "xsl", "mml2tex.xsl")
    dom = etree.fromstring(equation)
    xslt = etree.parse(xslt_file)
    transform = etree.XSLT(xslt)
    newdom = transform(dom)
    return newdom


def handle_math(data):
    if not ("$$" in data and isinstance(data["$$"], list)):
        return ""

    mathml_content = convert_json_to_mathml(data)

    print(mathml_content)

    latex_string = mathml2latex_yarosh(mathml_content)

    return f"${latex_string}$"


def convert_json_to_mathml(data):
    """Converts the math part of JSON data to MathML."""
    if isinstance(data, dict):
        if "#name" in data:
            tag_name = data["#name"]
            if tag_name == "math":
                mathml_string = "<math"
                mathml_string += """ xmlns="http://www.w3.org/1998/Math/MathML" """
                if "$" in data:
                    for attr, value in data["$"].items():
                        mathml_string += f'{attr}="{value}" '
                mathml_string = mathml_string.strip()
                mathml_string += ">"
                if "$$" in data:
                    mathml_string += convert_json_to_mathml(data["$$"])
                mathml_string += "</math>"
                return mathml_string
            else:
                mathml_string = f"<{tag_name}"
                if "$" in data:
                    for attr, value in data["$"].items():
                        mathml_string += f' {attr}="{value}"'
                mathml_string += ">"
                if "_" in data:
                    mathml_string += handle_label(data)
                if "$$" in data:
                    mathml_string += convert_json_to_mathml(data["$$"])
                mathml_string += f"</{tag_name}>"
                return mathml_string
        else:
            return ""
    elif isinstance(data, list):
        mathml_string = ""
        for item in data:
            mathml_string += convert_json_to_mathml(item)
        return mathml_string
    else:
        return str(data)


def handle_figure(data):
    markdown_output = ""
    caption = ""
    image_url = ""

    if "label" in data:
        markdown_output += f"**{data['label']}**\n\n"

    if "$$" in data:
        for item in data["$$"]:
            if item["#name"] == "caption":
                if "simple-para" in item["$$"][0]:
                    caption = handle_label(item["$$"][0]["simple-para"])
            elif item["#name"] == "link":
                if "$" in item and "locator" in item["$"]:
                    image_url = construct_image_url(item["$"]["locator"])

    if image_url:
        markdown_output += f"![{caption}]({image_url})\n\n"
    if caption:
        markdown_output += f"*{caption}*\n\n"

    return markdown_output


def handle_table(data):
    markdown_output = ""
    caption = ""
    label = ""

    if "$$" in data:
        for item in data["$$"]:
            if item["#name"] == "label":
                label = handle_label(item)
                if label:
                    markdown_output += f"**{label}**\n\n"
            if item["#name"] == "caption":
                caption = handle_caption(item).strip()
            elif item["#name"] == "tgroup":
                markdown_output += handle_tgroup(item)

    if caption:
        markdown_output += f"*{caption}*\n\n"
    return markdown_output


def handle_tgroup(data):
    markdown_output = ""
    if "$$" in data:
        num_cols = int(data["$"]["cols"]) if "$" in data and "cols" in data["$"] else 0
        col_widths = []
        header = []
        rows = []

        for item in data["$$"]:
            if item["#name"] == "colspec":
                # You might want to extract col width info here
                col_widths.append(1)  # Default width
            elif item["#name"] == "thead":
                header = handle_thead(item)
            elif item["#name"] == "tbody":
                rows = handle_tbody(item)

        if header:
            markdown_output += "|"
            for i in range(len(header)):
                markdown_output += header[i] + "|"
            markdown_output += "\n"

            markdown_output += "|"
            for i in range(len(header)):
                markdown_output += "---|"
            markdown_output += "\n"

        if rows:
            for row in rows:
                markdown_output += "|"
                for cell in row:
                    markdown_output += cell + "|"
                markdown_output += "\n"

    markdown_output += "\n"
    return markdown_output


def handle_thead(data):
    header = []
    if "$$" in data:
        for item in data["$$"]:
            if item["#name"] == "row":
                row_data = []
                if "$$" in item:
                    for entry in item["$$"]:
                        if entry["#name"] == "entry":
                            if "_" in entry:
                                row_data.append(handle_label(entry))
                            else:
                                row_data.append("")
                header.append(row_data)
    # Flatten the header list
    return header[0] if header else []


def handle_tbody(data):
    rows = []
    if "$$" in data:
        for item in data["$$"]:
            if item["#name"] == "row":
                row_data = []
                if "$$" in item:
                    for entry in item["$$"]:
                        if entry["#name"] == "entry":
                            if "_" in entry:
                                row_data.append(handle_label(entry))
                            else:
                                row_data.append("")
                rows.append(row_data)
    return rows


def handle_outline(data):
    markdown_output = ""
    if "$$" in data:
        for item in data["$$"]:
            if item.get("#name") == "list":
                markdown_output += handle_list(item)
    return markdown_output


def handle_section_title(data):
    return "## " + handle_label(data) + "\n\n"


def handle_bold(data):
    return f"**{handle_label(data)}**"


def handle_italic(data):
    return f"*{handle_label(data)}*"


def handle_label(data):
    if "_" in data:
        return data["_"]
    return ""


def handle_cross_ref(data):
    if "refid" in data["$"]:
        refid = data["$"]["refid"]
        return f"[{handle_label(data)}](#{refid})"
    return handle_label(data) if "_" in data else ""


def handle_inter_ref(data):
    if "href" in data["$"]:
        href = data["$"]["href"]
        return f"[{handle_label(data) if '_' in data else ''}]({href})"
    return handle_label(data) if "_" in data else ""


def handle_intra_ref(data):
    if "href" in data["$"]:
        href = data["$"]["href"]
        # Modify the href as per the rule:
        # Replace ':' with '/', and remove '-' and '.'
        modified_href = "https://www.sciencedirect.com/science/article/" + href.replace(
            ":", "/"
        ).replace("-", "").replace(".", "")
        return f"[{handle_label(data) if '_' in data else ''}]({modified_href})"
    return handle_label(data) if "_" in data else ""


def handle_display(data):
    markdown_output = ""
    if "$$" in data:
        markdown_output += json_to_markdown(data["$$"])
    return markdown_output


def handle_textbox(data):
    markdown_output = ""
    if "$$" in data:
        markdown_output += json_to_markdown(data["$$"])
    return markdown_output


def handle_caption(data):
    markdown_output = ""
    if "$$" in data:
        markdown_output += json_to_markdown(data["$$"])
    return markdown_output


def handle_textbox_body(data):
    markdown_output = ""
    if "$$" in data:
        markdown_output += json_to_markdown(data["$$"])
    return markdown_output


def handle_inline_figure(data):
    for item in data["$$"]:
        if item["#name"] == "link":
            if "$" in item and "locator" in item["$"]:
                locator = item["$"]["locator"]

                # Look up the attachment-eid using the locator
                attachment_eid = attachment_lookup.get(locator)

                if attachment_eid:
                    image_url = construct_image_url(attachment_eid)
                    return f"![]({image_url})"
    return ""


def handle_link(data):
    if "locator" in data["$"]:
        image_url = construct_image_url(data["$"]["locator"])
        return f"![]({image_url})"
    return ""


def handle_text(data):
    return handle_label(data)


def construct_image_url(locator):
    """
    Constructs an image URL from the given locator.

    Args:
        locator: The locator string.

    Returns:
        The constructed image URL.
    """
    return f"https://ars.els-cdn.com/content/image/{locator}"


# Entry point for Streamlit app
def main():
    st.title("JSON to Markdown Converter for Elsevier")

    # Input JSON data
    json_data = st.text_area("Paste JSON data here", height=300)

    if st.button("Convert to Markdown"):
        try:
            data = json.loads(json_data)
            markdown_output = json_to_markdown(data)
            col1, col2 = st.columns(2)
            with col1:
                st.header("Markdown Output Rendered")
                st.markdown(markdown_output, unsafe_allow_html=True)
            with col2:
                st.header("Markdown Output Raw")
                st.markdown(f"```markdown\n{markdown_output}\n```")

            # Download button
            st.download_button(
                label="Download Markdown",
                data=markdown_output.encode("utf-8"),
                file_name="converted_markdown.md",
                mime="text/markdown",
            )

        except json.JSONDecodeError:
            st.error("Invalid JSON format. Please check your input.")
        except Exception as e:
            st.error(f"An error occurred: {e.__cause__}")
            st.exception(e)


if __name__ == "__main__":
    main()
