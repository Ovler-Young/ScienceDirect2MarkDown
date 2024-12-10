import pytest
from sciencedirect2markdown.streamlitweb import (
    json_to_markdown,
    handle_math,
    handle_inter_ref,
    handle_intra_ref,
    handle_outline,
    convert_json_to_mathml,
    construct_image_url,
)


def test_empty_input():
    assert json_to_markdown({}) == ""


def test_basic_paragraph():
    json_data = {
        "#name": "para",
        "$": {"id": "p0010", "view": "all"},
        "_": "This is a paragraph."
    }
    expected_markdown = "This is a paragraph.\n\n"
    assert json_to_markdown(json_data) == expected_markdown


def test_paragraph_with_child():
    json_data = {
        "#name": "para",
        "$": {"id": "p0010", "view": "all"},
        "_": "This is a paragraph with ",
        "$$": [
            {
                "#name": "bold",
                "_": "bold text"
            }
        ]
    }
    expected_markdown = "This is a paragraph with **bold text**\n\n"
    assert json_to_markdown(json_data) == expected_markdown


def test_nested_paragraph():
    json_data = {
        "#name": "para",
        "$": {"id": "p0010", "view": "all"},
        "_": "This is a paragraph.",
        "$$": [
            {
                "#name": "para",
                "$": {"id": "p0011", "view": "all"},
                "_": "This is a nested paragraph."
            }
        ]
    }
    expected_markdown = "This is a paragraph.\n\nThis is a nested paragraph.\n\n"
    print(json_to_markdown(json_data))
    assert json_to_markdown(json_data) == expected_markdown


def test_list_unordered():
    json_data = {
        "#name": "list",
        "$": {"id": "l0010"},
        "$$": [
            {
                "#name": "list-item",
                "$": {"id": "i0010"},
                "$$": [
                    {"#name": "label", "_": "•"},
                    {
                        "#name": "para",
                        "$": {"id": "p0010", "view": "all"},
                        "_": "Item 1"
                    }
                ]
            },
            {
                "#name": "list-item",
                "$": {"id": "i0020"},
                "$$": [
                    {"#name": "label", "_": "•"},
                    {
                        "#name": "para",
                        "$": {"id": "p0020", "view": "all"},
                        "_": "Item 2"
                    }
                ]
            }
        ]
    }
    expected_markdown = "- •Item 1\n- •Item 2\n"
    assert json_to_markdown(json_data) == expected_markdown


def test_list_ordered():
    json_data = {
        "#name": "list",
        "$": {"id": "l0010"},
        "$$": [
            {
                "#name": "list-item",
                "$": {"id": "i0010"},
                "$$": [
                    {"#name": "label", "_": "1."},
                    {
                        "#name": "para",
                        "$": {"id": "p0010", "view": "all"},
                        "_": "Item 1"
                    }
                ]
            },
            {
                "#name": "list-item",
                "$": {"id": "i0020"},
                "$$": [
                    {"#name": "label", "_": "2."},
                    {
                        "#name": "para",
                        "$": {"id": "p0020", "view": "all"},
                        "_": "Item 2"
                    }
                ]
            }
        ]
    }
    expected_markdown = "1 Item 1\n2 Item 2\n"
    assert json_to_markdown(json_data) == expected_markdown


def test_list_mixed():
    json_data = {
        "#name": "list",
        "$": {"id": "l0010"},
        "$$": [
            {
                "#name": "list-item",
                "$": {"id": "i0010"},
                "$$": [
                    {"#name": "label", "_": "1."},
                    {
                        "#name": "para",
                        "$": {"id": "p0010", "view": "all"},
                        "_": "Item 1"
                    }
                ]
            },
            {
                "#name": "list-item",
                "$": {"id": "i0020"},
                "$$": [
                    {"#name": "label", "_": "•"},
                    {
                        "#name": "para",
                        "$": {"id": "p0020", "view": "all"},
                        "_": "Item 2"
                    }
                ]
            }
        ]
    }
    expected_markdown = "1 Item 1\n- •Item 2\n"
    assert json_to_markdown(json_data) == expected_markdown


def test_nested_list():
    json_data = {
        "#name": "list",
        "$": {"id": "l0010"},
        "$$": [
            {
                "#name": "list-item",
                "$": {"id": "i0010"},
                "$$": [
                    {"#name": "label", "_": "1."},
                    {
                        "#name": "para",
                        "$": {"id": "p0010", "view": "all"},
                        "_": "Item 1"
                    },
                    {
                        "#name": "list",
                        "$": {"id": "l0020"},
                        "$$": [
                            {
                                "#name": "list-item",
                                "$": {"id": "i0020"},
                                "$$": [
                                    {"#name": "label", "_": "•"},
                                    {
                                        "#name": "para",
                                        "$": {
                                            "id": "p0020",
                                            "view": "all"
                                        },
                                        "_": "Nested Item 1"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    expected_markdown = "1 Item 1\n  - •Nested Item 1\n"
    assert json_to_markdown(json_data) == expected_markdown


def test_simple_math():
    json_data = {
        "#name": "math",
        "$$": [
            {
                "#name": "mi",
                "_": "x"
            },
            {
                "#name": "mo",
                "_": "+"
            },
            {
                "#name": "mn",
                "_": "1"
            }
        ]
    }

    expected_mathml = '<math xmlns="http://www.w3.org/1998/Math/MathML"><mi>x</mi><mo>+</mo><mn>1</mn></math>'
    assert convert_json_to_mathml(json_data) == expected_mathml

    expected_markdown = "$x + 1$"
    assert handle_math(json_data) == expected_markdown


def test_complex_math():
    json_data = {
        "#name": "math",
        "$": {"altimg": "si21.gif", "overflow": "scroll"},
        "$$": [
            {
                "#name": "msub",
                "$$": [
                    {
                        "#name": "mover",
                        "$": {"accent": "true"},
                        "$$": [
                            {"#name": "mi", "_": "W"},
                            {"#name": "mo", "$": {"stretchy": "false"}, "_": "."}
                        ]
                    },
                    {"#name": "mi", "$": {"mathvariant": "normal"}, "_": "s"}
                ]
            },
            {"#name": "mo", "_": "≤"},
            {"#name": "mn", "_": "0"}
        ]
    }

    expected_mathml = '<math xmlns="http://www.w3.org/1998/Math/MathML" altimg="si21.gif" overflow="scroll"><msub><mover accent="true"><mi>W</mi><mo stretchy="false">.</mo></mover><mi mathvariant="normal">s</mi></msub><mo>≤</mo><mn>0</mn></math>'
    assert convert_json_to_mathml(json_data) == expected_mathml

    expected_markdown = "$$ {\\stackrel{.}{W}}_{\\mathrm{s}}\\le 0$$"
    assert handle_math(json_data) == expected_markdown


def test_image_url_construction():
    locator = "3-s2.0-B9780444637833000186-f18-01-9780444637833.gif"
    expected_url = "https://ars.els-cdn.com/content/image/" + locator
    assert construct_image_url(locator) == expected_url


def test_simple_figure():
    json_data = {
        "#name": "figure",
        "$": {"id": "f0010"},
        "$$": [
            {"#name": "label", "_": "Fig. 1"},
            {
                "#name": "caption",
                "$$": [
                    {
                        "#name": "simple-para",
                        "_": "This is a figure caption."
                    }
                ]
            },
            {
                "#name": "link",
                "$": {
                    "locator": "3-s2.0-B9780444637833000186-f18-01-9780444637833.gif",
                    "id": "lk0010"
                }
            }
        ]
    }

    expected_markdown = (
        "**Fig. 1**\n\n"
        + "![This is a figure caption.](https://ars.els-cdn.com/content/image/3-s2.0-B9780444637833000186-f18-01-9780444637833.gif)\n\n"
        + "*This is a figure caption.*\n\n"
    )
    assert json_to_markdown(json_data) == expected_markdown


def test_handle_href_in_links():
    # Test case for http/https links
    json_data_http = {
        "#name": "inter-ref",
        "$": {"href": "http://www.example.com", "id": "ir0010"},
        "_": "Link"
    }
    expected_markdown_http = "[Link](http://www.example.com)"
    assert handle_inter_ref(json_data_http) == expected_markdown_http

    # Test case for pii links
    json_data_pii = {
        "#name": "intra-ref",
        "$": {"href": "pii:B978-0-444-63783-3.00012-5", "id": "ia0010"},
        "_": "Chapter 12"
    }
    expected_markdown_pii = "[Chapter 12](https://www.sciencedirect.com/science/article/pii/B9780444637833000125)"
    assert handle_intra_ref(json_data_pii) == expected_markdown_pii


def test_handle_table():
    json_data = {
        "#name": "table",
        "$": {"id": "t0010"},
        "$$": [
            {"#name": "label", "_": "Table 1"},
            {
                "#name": "caption",
                "$$": [{"#name": "simple-para", "_": "Table Caption"}]
            },
            {
                "#name": "tgroup",
                "$": {"cols": "2"},
                "$$": [
                    {"#name": "colspec", "$": {"colname": "col1"}},
                    {"#name": "colspec", "$": {"colname": "col2"}},
                    {
                        "#name": "thead",
                        "$$": [
                            {
                                "#name": "row",
                                "$$": [
                                    {"#name": "entry", "_": "Header 1"},
                                    {"#name": "entry", "_": "Header 2"}
                                ]
                            }
                        ]
                    },
                    {
                        "#name": "tbody",
                        "$$": [
                            {
                                "#name": "row",
                                "$$": [
                                    {"#name": "entry", "_": "Row 1, Cell 1"},
                                    {"#name": "entry", "_": "Row 1, Cell 2"}
                                ]
                            },
                            {
                                "#name": "row",
                                "$$": [
                                    {"#name": "entry", "_": "Row 2, Cell 1"},
                                    {"#name": "entry", "_": "Row 2, Cell 2"}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    expected_markdown = (
        "**Table 1**\n\n"
        + "|Header 1|Header 2|\n"
        + "|---|---|\n"
        + "|Row 1, Cell 1|Row 1, Cell 2|\n"
        + "|Row 2, Cell 1|Row 2, Cell 2|\n\n"
        + "*Table Caption*\n\n"
    )
    assert json_to_markdown(json_data) == expected_markdown


def test_outline():
    json_data = {
        "#name": "outline",
        "$$": [
            {
                "#name": "list",
                "$$": [
                    {"#name": "section-title", "_": "Outline"},
                    {
                        "#name": "list-item",
                        "$$": [
                            {"#name": "label", "_": "1."},
                            {"#name": "para", "_": "First outline"}
                        ]
                    },
                    {
                        "#name": "list-item",
                        "$$": [
                            {"#name": "label", "_": "2."},
                            {"#name": "para", "_": "Second outline"}
                        ]
                    }
                ]
            }
        ]
    }

    expected_markdown = "## Outline\n\n1. First outline\n2. Second outline\n"
    assert handle_outline(json_data) == expected_markdown


def test_basic_sections():
    json_data = {
        "#name": "sections",
        "$$": [
            {
                "#name": "para",
                "$": {"id": "p0190", "view": "all"},
                "_": "What is reactivity hazard? "
            }
        ]
    }
    expected_markdown = "What is reactivity hazard? \n\n"
    assert json_to_markdown(json_data) == expected_markdown


def test_complex_sections():
    json_data = {
        "#name": "sections",
        "$": {
            "xmlns:ce": True,
            "xmlns:mml": True,
            "xmlns:xs": True,
            "xmlns:bk": True,
            "xmlns:xlink": True,
            "xmlns:tb": True,
            "xmlns:xocs": True,
            "xmlns:xsi": True,
            "xmlns:cals": True,
            "xmlns:sb": True,
            "xmlns": True
        },
        "$$": [
            {
                "#name": "para",
                "$": {"id": "p0190", "view": "all"},
                "_": "What is reactivity hazard? "
            },
            {
                "#name": "para",
                "$": {"id": "p0195", "view": "all"},
                "$$": [
                    {
                        "#name": "__text__",
                        "_": "A significant aspect of bioprocess engineering is considering how accidents could occur in biological and chemical processes in order to anticipate all possible modes by which the system might malfunction. This optimum design goal is discussed throughout this text, for example, see "
                    },
                    {
                        "#name": "intra-ref",
                        "$": {
                            "href": "pii:B978-0-444-63783-3.00003-4",
                            "id": "ia0010",
                            "type": "simple"
                        },
                        "_": "Chapters 3"
                    },
                    {"#name": "__text__", "_": ", "},
                    {
                        "#name": "intra-ref",
                        "$": {
                            "href": "pii:B978-0-444-63783-3.00004-6",
                            "id": "ia0015",
                            "type": "simple"
                        },
                        "_": "4"
                    },
                    {"#name": "__text__", "_": ", "},
                    {
                        "#name": "intra-ref",
                        "$": {
                            "href": "pii:B978-0-444-63783-3.00005-8",
                            "id": "ia0020",
                            "type": "simple"
                        },
                        "_": "5"
                    },
                    {"#name": "__text__", "_": ", and "},
                    {
                        "#name": "intra-ref",
                        "$": {
                            "href": "pii:B978-0-444-63783-3.00017-4",
                            "id": "ia0045",
                            "type": "simple"
                        },
                        "_": "17"
                    },
                    {
                        "#name": "__text__",
                        "_": ". However, we also need to consider whether that design is sufficiently robust that it will be stable in any unforeseen situations that may arise. Stability and sustainability of the reactor system of bioprocess are discussed in "
                    },
                    {
                        "#name": "intra-ref",
                        "$": {
                            "href": "pii:B978-0-444-63783-3.00015-0",
                            "id": "ia0050",
                            "type": "simple"
                        },
                        "_": "Chapter 15"
                    },
                    {
                        "#name": "__text__",
                        "_": ". We need also to examine operating modes outside of the regime of optimal design and assure that for all possible situations in which the system may be operated, uncontrollable consequences will not occur. Chain reactions and/or uncontrolled combustion/explosion are often associated with accidents. We will discuss this subject and its application in industry, as well."
                    }
                ]
            }
        ]
    }
    expected_markdown = "What is reactivity hazard? \n\nA significant aspect of bioprocess engineering is considering how accidents could occur in biological and chemical processes in order to anticipate all possible modes by which the system might malfunction. This optimum design goal is discussed throughout this text, for example, see [Chapters 3](https://www.sciencedirect.com/science/article/pii/B9780444637833000034), [4](https://www.sciencedirect.com/science/article/pii/B9780444637833000046), [5](https://www.sciencedirect.com/science/article/pii/B9780444637833000058), and [17](https://www.sciencedirect.com/science/article/pii/B9780444637833000174). However, we also need to consider whether that design is sufficiently robust that it will be stable in any unforeseen situations that may arise. Stability and sustainability of the reactor system of bioprocess are discussed in [Chapter 15](https://www.sciencedirect.com/science/article/pii/B9780444637833000150). We need also to examine operating modes outside of the regime of optimal design and assure that for all possible situations in which the system may be operated, uncontrollable consequences will not occur. Chain reactions and/or uncontrolled combustion/explosion are often associated with accidents. We will discuss this subject and its application in industry, as well.\n\n"
    assert json_to_markdown(json_data) == expected_markdown


def test_handle_footnotes():
    json_data = {"footnotes": []}
    # Currently, footnotes are expected to be empty
    expected_markdown = ""
    assert json_to_markdown(json_data) == expected_markdown


def test_handle_attachments():
    json_data = {
        "attachments": [
            {
                "attachment-eid": "3-s2.0-B9780444637833000186-f18-01-9780444637833.gif",
                "ucs-locator": "https://s3.amazonaws.com/prod-ucs-content-store-us-east/content/pii:B9780444637833000186/f18-01-9780444637833/DOWNSAMPLED/image/gif/5b450b75cebcc88aa76053b6bb18ab97/f18-01-9780444637833.gif",
                "file-basename": "f18-01-9780444637833",
                "filename": "f18-01-9780444637833.gif",
                "extension": "gif",
                "filesize": "21318",
                "pixel-height": "357",
                "pixel-width": "344",
                "attachment-type": "IMAGE-DOWNSAMPLED"
            },
            {
                "attachment-eid": "3-s2.0-B9780444637833000186-f18-01-9780444637833.sml",
                "ucs-locator": "https://s3.amazonaws.com/prod-ucs-content-store-us-east/content/pii:B9780444637833000186/f18-01-9780444637833/THUMBNAIL/image/gif/ad2704ce9c88724e9a850486cdfdeda6/f18-01-9780444637833.sml",
                "file-basename": "f18-01-9780444637833",
                "filename": "f18-01-9780444637833.sml",
                "extension": "sml",
                "filesize": "6860",
                "pixel-height": "164",
                "pixel-width": "158",
                "attachment-type": "IMAGE-THUMBNAIL"
            }
        ]
    }
    # For now, we expect attachments to be handled based on their usage in the content
    # So, just checking if the function processes without errors
    expected_markdown = ""
    assert json_to_markdown(json_data) == expected_markdown


def test_handle_correspondences():
    json_data = {"correspondences": {}}
    # Currently, correspondences are expected to be empty
    expected_markdown = ""
    assert json_to_markdown(json_data) == expected_markdown


def test_handle_affiliations():
    json_data = {"affiliations": {}}
    # Currently, affiliations are expected to be empty
    expected_markdown = ""
    assert json_to_markdown(json_data) == expected_markdown


def test_missing_name():
    json_data = {
        "$": {"id": "p0010", "view": "all"},
        "_": "Missing name."
    }
    expected_markdown = "Missing name.\n\n"
    assert json_to_markdown(json_data) == expected_markdown


def test_missing_attributes():
    json_data = {
        "#name": "para",
        "_": "Missing attributes."
    }
    expected_markdown = "Missing attributes.\n\n"
    assert json_to_markdown(json_data) == expected_markdown


def test_missing_text():
    json_data = {
        "#name": "para",
        "$": {"id": "p0010", "view": "all"}
    }
    expected_markdown = "\n\n"
    assert json_to_markdown(json_data) == expected_markdown


def test_empty_list():
    json_data = {
        "#name": "list",
        "$": {"id": "l0010"},
        "$$": []
    }
    expected_markdown = ""
    assert json_to_markdown(json_data) == expected_markdown


def test_empty_table():
    json_data = {
        "#name": "table",
        "$": {"id": "t0010"},
        "$$": []
    }
    expected_markdown = ""
    assert json_to_markdown(json_data) == expected_markdown


def test_invalid_math():
    json_data = {
        "#name": "math",
        "$$": [
            {
                "#name": "invalid",
                "_": "Invalid MathML",
            }
        ],
    }
    expected_markdown = ""
    assert handle_math(json_data) == expected_markdown


def test_malformed_json():
    with pytest.raises(TypeError):
        json_to_markdown("This is not JSON")
