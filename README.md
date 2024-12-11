# ScienceDirect2MarkDown

It convert json from ScienceDirect to MarkDown with some support of styles.

It now require manually copy the json from the F12 console, go to the network tab, search "body", refresh the page, click the first item, go to the response tab, select all and copy.

Next, open the [streamlit app](https://sciencedirect2markdown.streamlit.app/), paste the json, and click the button to convert to markdown.

You can priview the markdown in the app, and download the markdown file.

## Known issues

1. Reference is in separate request, which I have not yet implemented and not plan to do so.
2. Same-page jump is not working.
3. If section-title have label, label will block the markdown header.
