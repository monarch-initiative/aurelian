# Google Sheet File Downloader

This project contains scripts to automatically download all files linked in Google Sheets or CSV files.

## Files

1. **`download_from_sheet.py`** - Basic downloader script
2. **`enhanced_sheet_downloader.py`** - Enhanced version with detailed analysis and reporting

## Features

- ✅ Downloads files from Google Sheets (public sheets only)
- ✅ Downloads files from local CSV files
- ✅ Supports wide variety of file types (PDF, DOC, images, archives, etc.)
- ✅ Detailed analysis showing what URLs were found and why they're downloadable or not
- ✅ Dry-run mode to preview what would be downloaded
- ✅ Handles duplicate filenames automatically
- ✅ Progress tracking and detailed reporting
- ✅ Error handling and retry logic

## Usage

### Basic Usage

```bash
# Download from Google Sheet
python enhanced_sheet_downloader.py "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit" -o downloads

# Download from local CSV file
python enhanced_sheet_downloader.py "data.csv" -o downloads

# Dry run (analyze without downloading)
python enhanced_sheet_downloader.py "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit" --dry-run
```

### Your Specific Sheet

```bash
# Analyze your sheet
uv run python enhanced_sheet_downloader.py "https://docs.google.com/spreadsheets/d/1pF_XlQ8zlei-QcxJ7yhkvi50qEI4jfOYly_-_18JjKE/edit?gid=0#gid=0" --dry-run

# Download all files
uv run python enhanced_sheet_downloader.py "https://docs.google.com/spreadsheets/d/1pF_XlQ8zlei-QcxJ7yhkvi50qEI4jfOYly_-_18JjKE/edit?gid=0#gid=0" -o my_downloads
```

## Analysis Results for Your Sheet

From the analysis of your Google Sheet, the script found:

### ✅ **1 Downloadable File:**
- **aim-ahead-bridge2ai-for-clinical-care-informational-webinar.pdf** (3.35 MB)
  - Type: PDF document
  - Location: Row 7 in the sheet

### ❌ **10 Non-downloadable URLs:**
These are mostly DOI links, documentation pages, and dataset repositories that don't contain direct file downloads:

1. `https://aireadi.org/publications...` - Website link
2. `https://doi.org/10.1101/2024.05.21.589311` - DOI link (not a direct file)
3. `https://docs.aireadi.org/docs/2/about` - Documentation page
4. `https://github.com/chorus-ai#table-of-contents` - GitHub page
5. `https://doi.org/10.5281/zenodo.10642459` - DOI link
6. `https://fairhub.io/datasets/2` - Dataset page
7. `https://docs.google.com/document/d/1rJsa5kySlBRRNhsO_WY7N3bfSKtqDi-Q/edit` - Google Doc (needs export)
8. `https://dataverse.lib.virginia.edu/dataset.xhtml...` - Dataset page
9. `https://healthdatanexus.ai/content/b2ai-voice/1.0/` - Dataset page
10. `https://physionet.org/content/b2ai-voice/1.1/` - Dataset page

## Supported File Types

The script automatically detects and downloads these file types:

- **Documents**: PDF, DOC, DOCX, RTF, ODT
- **Spreadsheets**: XLS, XLSX, CSV, ODS
- **Presentations**: PPT, PPTX, ODP
- **Archives**: ZIP, TAR, GZ
- **Data**: JSON, XML, YAML, YML
- **Images**: PNG, JPG, GIF, SVG, etc.
- **Code**: PY, JS, HTML, CSS, etc.
- **Media**: MP3, MP4, AVI, etc.

## Making Google Sheets Accessible

For the script to work with Google Sheets, the sheet must be publicly accessible:

1. Open your Google Sheet
2. Click "Share" (top right)
3. Change access to "Anyone with the link can view"
4. Copy the sharing URL

## Troubleshooting

### Common Issues

1. **"No URLs found"**
   - Make sure the Google Sheet is public
   - Check that URLs are in separate cells (not concatenated)

2. **"Error accessing sheet"**
   - Verify the sheet URL is correct
   - Ensure the sheet is publicly accessible
   - Try copying the share URL instead of the edit URL

3. **Downloads fail**
   - Some websites block automated downloads
   - Check if the URL requires authentication
   - Try downloading manually to verify the link works

### Google Docs/Sheets Downloads

Note: Google Docs, Sheets, and Slides links (like the one found in your sheet) cannot be directly downloaded by this script. To download these:

1. **Manual approach**: Open the link and use File → Download
2. **Script modification**: Would need Google API integration

## Dependencies

```bash
pip install requests
# or
uv pip install requests
```

## Example Output

```
📊 Analyzing Google Sheet: https://docs.google.com/spreadsheets/d/...
📥 CSV export URL: https://docs.google.com/spreadsheets/d/.../export?format=csv...

🔍 Found 11 unique URLs:

  URL: https://example.com/document.pdf
       Context: Research paper about...
       Locations: Row(s) [5]
       ✅ Downloadable: PDF document (.pdf)

📁 1 downloadable files found
🚫 10 non-downloadable URLs skipped

⬇️ Starting downloads to: downloads

[1/1] Processing: https://example.com/document.pdf
  Downloading: https://example.com/document.pdf
    ✅ Downloaded: downloads/document.pdf (1,234,567 bytes)

==================================================
📊 DOWNLOAD SUMMARY
==================================================
✅ Successful: 1
❌ Failed: 0
📂 Output directory: /path/to/downloads
```

This tool is particularly useful for research data management, collecting resources from collaborative spreadsheets, and automating file collection workflows.