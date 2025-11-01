#!/usr/bin/env python3
"""
Script to download all files linked in a Google Sheet.
This script can work with CSV exports or direct CSV data.
"""
import csv
import os
import re
import requests
import urllib.parse
from pathlib import Path
from typing import List, Set
import argparse


def is_downloadable_url(url: str) -> bool:
    """Check if a URL is likely to be a downloadable file."""
    if not url or not url.startswith(('http://', 'https://')):
        return False
    
    # Common file extensions that should be downloaded
    downloadable_extensions = {
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.zip', '.tar', '.gz', '.csv', '.json', '.xml', '.yaml', '.yml',
        '.txt', '.md', '.rtf', '.odt', '.ods', '.odp',
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.tiff',
        '.mp3', '.wav', '.mp4', '.avi', '.mov', '.wmv',
        '.py', '.js', '.html', '.css', '.java', '.cpp', '.c'
    }
    
    # Check if URL has a downloadable extension
    parsed = urllib.parse.urlparse(url.lower())
    path = parsed.path
    
    for ext in downloadable_extensions:
        if path.endswith(ext):
            return True
    
    # Check for common download patterns
    download_patterns = [
        'download', 'attachment', 'export', 'file'
    ]
    
    if any(pattern in url.lower() for pattern in download_patterns):
        return True
    
    return False


def extract_urls_from_csv_content(csv_content: str) -> Set[str]:
    """Extract all URLs from CSV content."""
    urls = set()
    
    # Use CSV reader to properly parse the content
    lines = csv_content.strip().split('\n')
    csv_reader = csv.reader(lines)
    
    for row in csv_reader:
        for cell in row:
            # Find URLs in the cell using regex
            url_pattern = r'https?://[^\s,<>"\']*'
            found_urls = re.findall(url_pattern, cell)
            
            for url in found_urls:
                # Clean up URL (remove trailing punctuation)
                url = url.rstrip('.,;:!?)')
                if is_downloadable_url(url):
                    urls.add(url)
    
    return urls


def download_file(url: str, output_dir: Path, session: requests.Session) -> bool:
    """Download a single file from URL."""
    try:
        print(f"Downloading: {url}")
        
        # Get filename from URL or use a default
        parsed_url = urllib.parse.urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        if not filename or '.' not in filename:
            # Try to get filename from Content-Disposition header
            response = session.head(url, allow_redirects=True, timeout=30)
            if 'content-disposition' in response.headers:
                cd = response.headers['content-disposition']
                filename_match = re.search(r'filename="([^"]+)"', cd)
                if filename_match:
                    filename = filename_match.group(1)
                else:
                    filename = f"download_{hash(url) & 0xFFFFFF:06x}"
            else:
                filename = f"download_{hash(url) & 0xFFFFFF:06x}"
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Download the file
        response = session.get(url, allow_redirects=True, timeout=60)
        response.raise_for_status()
        
        output_path = output_dir / filename
        
        # Handle filename conflicts
        counter = 1
        original_path = output_path
        while output_path.exists():
            name, ext = os.path.splitext(original_path.name)
            output_path = output_dir / f"{name}_{counter}{ext}"
            counter += 1
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return False


def download_from_csv_file(csv_file_path: str, output_dir: str):
    """Download files from a local CSV file."""
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            csv_content = f.read()
    except UnicodeDecodeError:
        with open(csv_file_path, 'r', encoding='latin-1') as f:
            csv_content = f.read()
    
    urls = extract_urls_from_csv_content(csv_content)
    
    if not urls:
        print("No downloadable URLs found in the CSV file.")
        return
    
    print(f"Found {len(urls)} downloadable URLs")
    
    output_path = Path(output_dir)
    session = requests.Session()
    
    successful = 0
    for url in urls:
        if download_file(url, output_path, session):
            successful += 1
    
    print(f"\nDownload complete: {successful}/{len(urls)} files downloaded successfully")


def download_from_google_sheet_url(sheet_url: str, output_dir: str):
    """Download files from a Google Sheet URL."""
    # Convert Google Sheets URL to CSV export URL
    if '/edit' in sheet_url:
        # Extract the sheet ID
        sheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheet_url)
        if not sheet_id_match:
            print("Could not extract sheet ID from URL")
            return
        
        sheet_id = sheet_id_match.group(1)
        
        # Extract gid if present
        gid_match = re.search(r'[#&]gid=(\d+)', sheet_url)
        gid = gid_match.group(1) if gid_match else '0'
        
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
        print(f"Converting to CSV export URL: {csv_url}")
    else:
        csv_url = sheet_url
    
    try:
        # Download the CSV content
        session = requests.Session()
        response = session.get(csv_url, timeout=30)
        response.raise_for_status()
        
        urls = extract_urls_from_csv_content(response.text)
        
        if not urls:
            print("No downloadable URLs found in the Google Sheet.")
            print("Make sure the sheet is public or accessible.")
            return
        
        print(f"Found {len(urls)} downloadable URLs")
        
        output_path = Path(output_dir)
        
        successful = 0
        for url in urls:
            if download_file(url, output_path, session):
                successful += 1
        
        print(f"\nDownload complete: {successful}/{len(urls)} files downloaded successfully")
        
    except Exception as e:
        print(f"Error accessing Google Sheet: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure the Google Sheet is public or shared with 'Anyone with the link can view'")
        print("2. Try downloading the sheet as CSV manually first")
        print("3. Check if the URL is correct")


def main():
    parser = argparse.ArgumentParser(description="Download files from Google Sheets or CSV files")
    parser.add_argument("input", help="Google Sheet URL or path to CSV file")
    parser.add_argument("-o", "--output", default="downloads", help="Output directory for downloads")
    
    args = parser.parse_args()
    
    if args.input.startswith(('http://', 'https://')):
        download_from_google_sheet_url(args.input, args.output)
    else:
        download_from_csv_file(args.input, args.output)


if __name__ == "__main__":
    main()