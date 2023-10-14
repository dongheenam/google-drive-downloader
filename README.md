# Google Drive Downloader

Downloads files given its share link from Google Drive using the Google Drive API.
- For Google Apps, the file is converted to equivalent Microsoft Office format. Supported formats:
    - Google Docs
    - Google Sheets
    - Google Slides
- For all other files, the file is downloaded in its original format.

## Installation

### Setting up the Python virtual environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Getting the Google Drive API credentials

Follow the [CodeLabs tutorial](https://codelabs.developers.google.com/codelabs/gsuite-apis-intro/#5), Steps 6 and 7.

Copy the `client_secret.json` file to the root directory of this project.

### Running the script

```bash
python download.py <share_link>
```

For example:

```bash
python download.py https://docs.google.com/document/d/1LxgwO_-mIXfqB9NeOEwrI-42Sk-fadA8CGg4wjz0qNw/edit?usp=sharing
```

will download [this file](https://docs.google.com/document/d/1LxgwO_-mIXfqB9NeOEwrI-42Sk-fadA8CGg4wjz0qNw/edit?usp=sharing) as `Google Drive 101.docx` in the output directory.

