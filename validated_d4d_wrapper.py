#!/usr/bin/env python3
"""
Validated D4D Agent Wrapper - Processes downloaded files with validation steps:
1. Assesses whether downloads succeeded 
2. Verifies each file contains specific information about the project in its column
3. Generates D4D YAML metadata using the Anthropic Claude API
"""
import asyncio
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple
import argparse
import yaml
import requests
from pydantic_ai import Agent
from dataclasses import dataclass
import re


@dataclass
class SimpleD4DConfig:
    """Simple configuration for D4D processing."""
    schema_url: str = "https://raw.githubusercontent.com/monarch-initiative/ontogpt/main/src/ontogpt/templates/data_sheets_schema.yaml"


class ValidatedD4DWrapper:
    """Validated wrapper with download and content validation before D4D processing."""
    
    def __init__(self, input_dir: str = "downloads_by_column", output_dir: str = "data/extracted_by_column"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Project keywords for content validation
        self.project_keywords = {
            'AI_READI': ['ai-readi', 'aireadi', 'artificial intelligence ready', 'diabetes', 'salutogenic', 'fairhub'],
            'CHORUS': ['chorus', 'clinical health outcomes research', 'informatics', 'aim ahead', 'bridge2ai'],
            'CM4AI': ['cm4ai', 'computational microscopy', 'microscopy', 'imaging', 'cellular', 'dataverse'],
            'VOICE': ['voice', 'b2ai-voice', 'bridge2ai voice', 'vocal', 'speech', 'physionet', 'health data nexus']
        }
        
        # Check for API key (OpenAI or Anthropic)
        if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
            print("❌ Error: Neither OPENAI_API_KEY nor ANTHROPIC_API_KEY environment variable is set")
            print("Please set one of these API keys:")
            print("export OPENAI_API_KEY='your-openai-key-here'")
            print("export ANTHROPIC_API_KEY='your-anthropic-key-here'")
            raise ValueError("Missing API key")
        
        # Load D4D schema
        self.schema = self.load_d4d_schema()
        
        # Create GPT-5-based D4D agent
        self.d4d_agent = Agent(
            model="openai:gpt-5",
            deps_type=SimpleD4DConfig,
            system_prompt=f"""
You are an expert data scientist specializing in extracting metadata from datasets following the "Datasheets for Datasets" schema.

Below is the complete datasheets for datasets schema:

{self.schema}

Your task is to analyze the provided content (which may be HTML, text, PDF, or JSON metadata) and extract all relevant dataset metadata to generate a complete YAML document that strictly follows the D4D schema above.

Focus on extracting:
- Dataset identity (id, name, title, description)  
- Creators and contributors with affiliations
- Purpose and intended uses
- Data composition and structure
- Collection methodology and timeframe
- Preprocessing and cleaning steps
- Distribution information and formats
- Licensing and terms of use
- Maintenance information
- Access requirements and restrictions

Generate only valid YAML output without any additional commentary. Ensure all required fields are populated where information is available. If specific information is not available in the source, omit those fields rather than making assumptions.

The output must be a valid YAML document that starts with the dataset metadata, not wrapped in code blocks or explanations.
""",
            defer_model_check=True,
        )
    
    def load_d4d_schema(self) -> str:
        """Load the D4D schema from GitHub."""
        try:
            config = SimpleD4DConfig()
            response = requests.get(config.schema_url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"❌ Error loading D4D schema: {e}")
            raise
    
    def validate_download_success(self, file_path: Path) -> Tuple[bool, str, Dict]:
        """Validate that a download was successful and contains meaningful content."""
        validation_result = {
            'file_exists': False,
            'file_size': 0,
            'content_length': 0,
            'file_type': '',
            'has_meaningful_content': False,
            'validation_details': []
        }
        
        try:
            # Check file exists
            if not file_path.exists():
                return False, "File does not exist", validation_result
            
            validation_result['file_exists'] = True
            validation_result['file_size'] = file_path.stat().st_size
            validation_result['file_type'] = file_path.suffix
            
            # Check minimum file size
            if validation_result['file_size'] < 100:  # Very small files likely failed
                return False, f"File too small ({validation_result['file_size']} bytes)", validation_result
            
            validation_result['validation_details'].append(f"File size: {validation_result['file_size']} bytes")
            
            # Read and validate content based on file type
            content = self.read_file_content(file_path)
            validation_result['content_length'] = len(content)
            
            if validation_result['content_length'] < 50:
                return False, "Content too short", validation_result
            
            # Check for error indicators in content
            error_indicators = [
                'error 404', 'not found', 'page not found', 'access denied', 
                'error 403', 'forbidden', 'error 500', 'internal server error',
                'error reading file', 'failed to retrieve'
            ]
            
            content_lower = content.lower()
            for error in error_indicators:
                if error in content_lower:
                    return False, f"Content contains error: {error}", validation_result
            
            # File type specific validation
            if file_path.suffix == '.html':
                # Check for meaningful HTML content (not just error pages)
                if '<title>' in content_lower:
                    title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
                    if title_match:
                        title = title_match.group(1).strip()
                        validation_result['validation_details'].append(f"HTML title: {title}")
                        
                        # Check if title indicates an error
                        if any(err in title.lower() for err in ['error', 'not found', '404', '403']):
                            return False, f"Error in page title: {title}", validation_result
                
                # Check for substantial body content
                if '<body>' in content_lower and len(content) > 1000:
                    validation_result['has_meaningful_content'] = True
                    validation_result['validation_details'].append("Has substantial HTML body content")
                
            elif file_path.suffix == '.json':
                # Validate JSON and check for meaningful data
                try:
                    data = json.loads(content)
                    if isinstance(data, dict) and len(data) > 0:
                        validation_result['has_meaningful_content'] = True
                        validation_result['validation_details'].append(f"Valid JSON with {len(data)} fields")
                    else:
                        return False, "JSON is empty or invalid structure", validation_result
                except json.JSONDecodeError as e:
                    return False, f"Invalid JSON: {e}", validation_result
                    
            elif file_path.suffix == '.txt':
                # Check for meaningful text content
                lines = content.strip().split('\n')
                non_empty_lines = [line for line in lines if line.strip()]
                if len(non_empty_lines) > 10:  # Reasonable amount of content
                    validation_result['has_meaningful_content'] = True
                    validation_result['validation_details'].append(f"Text file with {len(non_empty_lines)} non-empty lines")
                
            elif file_path.suffix == '.pdf':
                # PDF files are assumed valid if they exist and have reasonable size
                if validation_result['file_size'] > 1000:
                    validation_result['has_meaningful_content'] = True
                    validation_result['validation_details'].append("PDF file with reasonable size")
            
            # Final validation
            if validation_result['has_meaningful_content']:
                return True, "Download successful with meaningful content", validation_result
            else:
                return False, "Content appears to be incomplete or invalid", validation_result
                
        except Exception as e:
            return False, f"Error validating file: {str(e)}", validation_result
    
    def validate_project_relevance(self, file_path: Path, column: str, content: str) -> Tuple[bool, str, Dict]:
        """Validate that file contains information relevant to the project column."""
        relevance_result = {
            'column': column,
            'keywords_found': [],
            'relevance_score': 0,
            'relevance_details': [],
            'content_indicators': []
        }
        
        try:
            # Get keywords for this column
            keywords = self.project_keywords.get(column, [])
            content_lower = content.lower()
            
            # Count keyword matches
            found_keywords = []
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    found_keywords.append(keyword)
                    relevance_result['relevance_score'] += 1
            
            relevance_result['keywords_found'] = found_keywords
            
            # Look for project-specific indicators
            project_indicators = {
                'AI_READI': ['type 2 diabetes', 'fairness', 'equity', 'salutogenic', 'nih'],
                'CHORUS': ['clinical outcomes', 'informatics', 'health records', 'ehr'],
                'CM4AI': ['microscopy', 'imaging', 'cellular', 'computational', 'virginia'],
                'VOICE': ['voice recording', 'speech', 'vocal', 'acoustic', 'biomarker', 'mit']
            }
            
            indicators = project_indicators.get(column, [])
            found_indicators = []
            for indicator in indicators:
                if indicator.lower() in content_lower:
                    found_indicators.append(indicator)
                    relevance_result['relevance_score'] += 2  # Higher weight for specific indicators
            
            relevance_result['content_indicators'] = found_indicators
            
            # URL-based validation for certain patterns
            filename = file_path.name.lower()
            url_relevance = {
                'AI_READI': ['aireadi', 'fairhub'],
                'CHORUS': ['aim-ahead', 'chorus'],
                'CM4AI': ['dataverse', 'cm4ai'],
                'VOICE': ['physionet', 'voice', 'b2ai-voice', 'healthnexus']
            }
            
            url_keywords = url_relevance.get(column, [])
            for url_keyword in url_keywords:
                if url_keyword in filename:
                    relevance_result['relevance_score'] += 3  # Even higher weight for URL matches
                    relevance_result['relevance_details'].append(f"Filename contains '{url_keyword}'")
            
            # Add details
            if found_keywords:
                relevance_result['relevance_details'].append(f"Found keywords: {', '.join(found_keywords)}")
            if found_indicators:
                relevance_result['relevance_details'].append(f"Found project indicators: {', '.join(found_indicators)}")
            
            # Determine if relevant (threshold-based)
            is_relevant = relevance_result['relevance_score'] >= 1
            
            if is_relevant:
                message = f"Content is relevant to {column} (score: {relevance_result['relevance_score']})"
            else:
                message = f"Content may not be specific to {column} project"
            
            return is_relevant, message, relevance_result
            
        except Exception as e:
            return False, f"Error validating relevance: {str(e)}", relevance_result
    
    def read_file_content(self, file_path: Path) -> str:
        """Read content from various file types."""
        try:
            if file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return json.dumps(data, indent=2)
            elif file_path.suffix in ['.html', '.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Truncate very long content to avoid token limits
                    if len(content) > 50000:
                        content = content[:50000] + "\n\n... [Content truncated for length] ..."
                    return content
            elif file_path.suffix == '.pdf':
                return f"PDF file: {file_path.name}. This is a PDF document that should be analyzed for dataset information. Note: PDF content extraction not available in this context, please analyze based on the filename and any other available metadata."
            else:
                # Try to read as text
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"
    
    def should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be processed by the D4D agent."""
        # Skip report files and summaries
        skip_patterns = [
            'organized_extraction_report',
            'organized_extraction_summary', 
            'extraction_report',
            'extraction_summary',
        ]
        
        filename = file_path.name.lower()
        return not any(pattern in filename for pattern in skip_patterns)
    
    def generate_extraction_metadata(self, input_file: Path, output_file: Path, 
                                    column: str, validation_info: Dict, 
                                    config: SimpleD4DConfig, agent_result) -> Dict:
        """Generate comprehensive metadata for the D4D extraction process."""
        import platform
        import sys
        from datetime import datetime
        import hashlib
        
        # Calculate file hash for provenance
        with open(input_file, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Get agent version info
        agent_version = "1.0.0"  # Could be extracted from package version
        
        # Extract model info from agent configuration
        model_info = self.d4d_agent._model.model_name if hasattr(self.d4d_agent, '_model') else "openai:gpt-5"
        
        metadata = {
            'extraction_metadata': {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'extraction_id': hashlib.sha256(f"{input_file.name}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:12],
            },
            'input_document': {
                'filename': input_file.name,
                'relative_path': str(input_file.relative_to(Path.cwd())) if input_file.is_relative_to(Path.cwd()) else input_file.name,
                'format': input_file.suffix[1:] if input_file.suffix else 'unknown',
                'size_bytes': input_file.stat().st_size,
                'sha256_hash': file_hash,
                'project_column': column,
            },
            'output_document': {
                'filename': output_file.name,
                'relative_path': str(output_file.relative_to(Path.cwd())) if output_file.is_relative_to(Path.cwd()) else output_file.name,
                'format': 'yaml',
            },
            'datasheets_schema': {
                'version': '1.0.0',  # Could be extracted from schema
                'url': config.schema_url,
                'retrieved_at': datetime.utcnow().isoformat() + 'Z',
            },
            'd4d_agent': {
                'version': agent_version,
                'implementation': 'pydantic_ai',
                'wrapper': 'validated_d4d_wrapper.py',
                'wrapper_version': '2.0.0',  # Updated for metadata generation
            },
            'llm_model': {
                'provider': 'openai',
                'model_name': model_info,
                'model_version': 'gpt-5',
                'temperature': None,  # Could be extracted if set
                'max_tokens': None,   # Could be extracted if set
            },
            'validation_results': {
                'download_validation': {
                    'success': validation_info.get('download', {}).get('success', False),
                    'file_size': validation_info.get('download', {}).get('details', {}).get('file_size', 0),
                    'content_type': validation_info.get('download', {}).get('details', {}).get('file_type', 'unknown'),
                },
                'relevance_validation': {
                    'success': validation_info.get('relevance', {}).get('success', False),
                    'score': validation_info.get('relevance', {}).get('details', {}).get('relevance_score', 0),
                    'keywords_found': validation_info.get('relevance', {}).get('details', {}).get('keywords_found', []),
                    'project_indicators': validation_info.get('relevance', {}).get('details', {}).get('content_indicators', []),
                },
            },
            'processing_environment': {
                'platform': platform.system(),  # Just OS name, not full platform details
                'python_version': sys.version.split()[0],
                'processor_architecture': platform.machine(),
            },
            'reproducibility': {
                'command': f"python validated_d4d_wrapper.py -i {self.input_dir} -o {self.output_dir}",
                'environment_variables': {
                    'OPENAI_API_KEY': 'required' if os.getenv('OPENAI_API_KEY') else 'not_set',
                    'ANTHROPIC_API_KEY': 'required' if os.getenv('ANTHROPIC_API_KEY') else 'not_set',
                },
                'random_seed': None,  # If randomization is used
            },
            'provenance': {
                'extraction_performed_by': 'validated_d4d_wrapper',
                'extraction_requested_at': datetime.utcnow().isoformat() + 'Z',
                'git_commit': None,  # Could be extracted if in git repo
                'notes': 'D4D extraction using GPT-5 model with validation checks',
            }
        }
        
        return metadata
    
    def select_preferred_file(self, files_list: List[Path]) -> List[Path]:
        """Select preferred file formats: txt > html > pdf for the same base content."""
        # Group files by base name (removing row suffix and extension)
        file_groups = {}
        
        for file_path in files_list:
            base_name = file_path.stem
            # Remove row suffix if present
            if '_row' in base_name:
                base_name = base_name.split('_row')[0]
            
            if base_name not in file_groups:
                file_groups[base_name] = []
            file_groups[base_name].append(file_path)
        
        # Select preferred format for each group
        preferred_files = []
        format_priority = {'.txt': 1, '.html': 2, '.pdf': 3, '.json': 4}
        
        for base_name, group_files in file_groups.items():
            if len(group_files) == 1:
                preferred_files.extend(group_files)
            else:
                # Sort by format preference (lower number = higher priority)
                sorted_files = sorted(group_files, key=lambda f: format_priority.get(f.suffix, 999))
                preferred_files.append(sorted_files[0])
        
        return preferred_files
    
    async def process_file_with_agent(self, file_path: Path, column: str, output_path: Path, validation_info: Dict) -> Tuple[bool, str]:
        """Process a single file with the D4D agent."""
        try:
            print(f"    📄 Processing: {file_path.name}")
            
            # Read file content
            content = self.read_file_content(file_path)
            
            if len(content) < 50:  # Skip very short files
                return False, "Content too short"
            
            # Include validation context in prompt
            relevance_context = ""
            if 'relevance' in validation_info:
                rel_info = validation_info['relevance']
                relevance_context = f"""
Validation Context:
- Project Column: {column}
- Keywords found: {', '.join(rel_info.get('keywords_found', []))}
- Project indicators: {', '.join(rel_info.get('content_indicators', []))}
- Relevance score: {rel_info.get('relevance_score', 0)}
"""
            
            # Prepare prompt for D4D agent
            prompt = f"""
Please analyze the following content and extract dataset metadata following the D4D schema.

Source file: {file_path.name}
Content type: {file_path.suffix}
Project category: {column}

{relevance_context}

Content to analyze:
{content}

Generate a complete D4D YAML document based on this content. Include as much relevant information as you can extract from the source material. Pay special attention to information related to the {column} project.
"""
            
            # Configure D4D agent
            config = SimpleD4DConfig()
            
            # Run the agent
            result = await self.d4d_agent.run(prompt, deps=config)
            
            # Extract YAML from result
            yaml_content = result.output.strip()
            
            # Clean up the output - remove any markdown formatting
            if yaml_content.startswith('```yaml'):
                yaml_content = yaml_content[7:]
            if yaml_content.startswith('```'):
                yaml_content = yaml_content[3:]
            if yaml_content.endswith('```'):
                yaml_content = yaml_content[:-3]
            yaml_content = yaml_content.strip()
            
            # Validate YAML
            try:
                parsed_yaml = yaml.safe_load(yaml_content)
                if not isinstance(parsed_yaml, dict):
                    return False, "Generated content is not a valid YAML document"
            except yaml.YAMLError as e:
                return False, f"Invalid YAML generated: {e}"
            
            # Add validation metadata as comments at the top
            validation_header = f"""# D4D Metadata extracted from: {file_path.name}
# Column: {column}
# Validation: Download {'✅ success' if validation_info.get('download', {}).get('success', False) else '❌ failed'}
# Relevance: {'✅ relevant' if validation_info.get('relevance', {}).get('success', False) else '⚠️  limited relevance'}
# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

"""
            
            # Save YAML file with validation header
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(validation_header + yaml_content)
            
            # Generate metadata file for this extraction
            metadata_filename = output_path.stem + '_metadata.yaml'
            metadata_output_path = output_path.parent / metadata_filename
            metadata_content = self.generate_extraction_metadata(
                file_path, output_path, column, validation_info, config, result
            )
            
            with open(metadata_output_path, 'w', encoding='utf-8') as f:
                yaml.dump(metadata_content, f, default_flow_style=False, sort_keys=False, width=120)
            
            print(f"      ✅ Generated: {output_path.name}")
            print(f"      📋 Metadata: {metadata_output_path.name}")
            return True, "Success"
            
        except Exception as e:
            error_msg = str(e)
            print(f"      ❌ Failed: {error_msg}")
            return False, error_msg
    
    async def process_column(self, column_dir: Path) -> Dict:
        """Process all files in a column directory with validation."""
        column_name = column_dir.name
        print(f"\n📂 Processing column: {column_name}")
        
        # Create output directory for this column
        column_output_dir = self.output_dir / column_name
        column_output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            'column': column_name,
            'processed': [],
            'skipped': [],
            'errors': [],
            'validation_summary': {
                'download_successful': 0,
                'download_failed': 0,
                'relevant_content': 0,
                'irrelevant_content': 0
            }
        }
        
        # Get all files to process
        all_files = [f for f in column_dir.iterdir() 
                    if f.is_file() and self.should_process_file(f)]
        
        # Select preferred formats (txt > html > pdf)
        files_to_process = self.select_preferred_file(all_files)
        
        print(f"   Found {len(files_to_process)} files to process")
        
        # Process each file with validation
        for file_path in files_to_process:
            print(f"\n   📋 Validating: {file_path.name}")
            
            # Step 1: Validate download success
            download_success, download_msg, download_details = self.validate_download_success(file_path)
            print(f"      Download: {'✅' if download_success else '❌'} {download_msg}")
            
            results['validation_summary']['download_successful' if download_success else 'download_failed'] += 1
            
            if not download_success:
                results['errors'].append({
                    'file': str(file_path),
                    'stage': 'download_validation',
                    'error': download_msg,
                    'details': download_details
                })
                continue
            
            # Step 2: Validate project relevance
            content = self.read_file_content(file_path)
            relevance_success, relevance_msg, relevance_details = self.validate_project_relevance(file_path, column_name, content)
            print(f"      Relevance: {'✅' if relevance_success else '⚠️'} {relevance_msg}")
            
            results['validation_summary']['relevant_content' if relevance_success else 'irrelevant_content'] += 1
            
            # Store validation info
            validation_info = {
                'download': {'success': download_success, 'details': download_details},
                'relevance': {'success': relevance_success, 'details': relevance_details}
            }
            
            # Generate output filename
            base_name = file_path.stem
            if '_row' in base_name:
                base_name = base_name.split('_row')[0]
            
            output_filename = f"{base_name}_d4d.yaml"
            output_path = column_output_dir / output_filename
            
            # Skip if already exists
            if output_path.exists():
                print(f"    ⏭️  Skipping (exists): {file_path.name}")
                results['skipped'].append({
                    'file': str(file_path),
                    'reason': 'Already exists',
                    'validation': validation_info
                })
                continue
            
            # Step 3: Process with D4D agent
            success, message = await self.process_file_with_agent(file_path, column_name, output_path, validation_info)
            
            if success:
                # Calculate metadata file path
                metadata_filename = output_path.stem + '_metadata.yaml'
                metadata_path = output_path.parent / metadata_filename
                
                results['processed'].append({
                    'input_file': str(file_path),
                    'output_file': str(output_path),
                    'metadata_file': str(metadata_path),
                    'status': 'success',
                    'validation': validation_info
                })
            else:
                results['errors'].append({
                    'file': str(file_path),
                    'stage': 'd4d_processing',
                    'error': message,
                    'validation': validation_info
                })
            
            # Small delay to be respectful to API
            await asyncio.sleep(1)
        
        return results
    
    async def process_all_columns(self) -> Dict:
        """Process all column directories with comprehensive validation."""
        if not self.input_dir.exists():
            print(f"❌ Input directory not found: {self.input_dir}")
            return {}
        
        print(f"🚀 Validated D4D Agent Wrapper - Processing files from: {self.input_dir}")
        print(f"📁 Output directory: {self.output_dir}")
        
        all_results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'input_dir': str(self.input_dir),
            'output_dir': str(self.output_dir),
            'columns': [],
            'summary': {
                'total_processed': 0,
                'total_errors': 0,
                'total_skipped': 0,
                'validation_summary': {
                    'download_successful': 0,
                    'download_failed': 0,
                    'relevant_content': 0,
                    'irrelevant_content': 0
                }
            }
        }
        
        # Get all column directories
        column_dirs = [d for d in self.input_dir.iterdir() if d.is_dir()]
        
        if not column_dirs:
            print("❌ No column directories found")
            return all_results
        
        print(f"📂 Found {len(column_dirs)} columns to process")
        
        # Process each column
        for column_dir in sorted(column_dirs):
            results = await self.process_column(column_dir)
            all_results['columns'].append(results)
            
            # Update summary
            all_results['summary']['total_processed'] += len(results['processed'])
            all_results['summary']['total_errors'] += len(results['errors'])
            all_results['summary']['total_skipped'] += len(results['skipped'])
            
            # Update validation summary
            val_sum = all_results['summary']['validation_summary']
            col_val_sum = results['validation_summary']
            val_sum['download_successful'] += col_val_sum['download_successful']
            val_sum['download_failed'] += col_val_sum['download_failed']
            val_sum['relevant_content'] += col_val_sum['relevant_content']
            val_sum['irrelevant_content'] += col_val_sum['irrelevant_content']
        
        # Save summary
        summary_file = self.output_dir / "validated_d4d_processing_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        
        # Create markdown report
        self.create_validation_report(all_results)
        
        return all_results
    
    def create_validation_report(self, results: Dict):
        """Create a comprehensive validation and processing report."""
        report_file = self.output_dir / "validated_d4d_processing_report.md"
        
        with open(report_file, 'w') as f:
            f.write("# Validated D4D Agent Processing Report\n\n")
            f.write(f"Generated: {results['timestamp']}\n\n")
            
            # Overall Summary
            f.write("## Overall Summary\n\n")
            summary = results['summary']
            f.write(f"- **Files processed**: {summary['total_processed']}\n")
            f.write(f"- **Errors**: {summary['total_errors']}\n")
            f.write(f"- **Skipped**: {summary['total_skipped']}\n")
            
            # Validation Summary
            f.write("\n## Validation Summary\n\n")
            val_sum = summary['validation_summary']
            f.write(f"- **Downloads successful**: {val_sum['download_successful']}\n")
            f.write(f"- **Downloads failed**: {val_sum['download_failed']}\n")
            f.write(f"- **Content relevant to project**: {val_sum['relevant_content']}\n")
            f.write(f"- **Content with limited relevance**: {val_sum['irrelevant_content']}\n")
            
            # By column
            f.write("\n## Results by Column\n\n")
            
            for column_result in results['columns']:
                column = column_result['column']
                f.write(f"### {column}\n\n")
                
                # Column validation summary
                col_val = column_result['validation_summary']
                f.write(f"**Validation Results:**\n")
                f.write(f"- Downloads: {col_val['download_successful']} successful, {col_val['download_failed']} failed\n")
                f.write(f"- Relevance: {col_val['relevant_content']} relevant, {col_val['irrelevant_content']} limited\n\n")
                
                # Processed files
                if column_result['processed']:
                    f.write("#### Successfully Processed\n\n")
                    for item in column_result['processed']:
                        input_file = Path(item['input_file']).name
                        output_file = Path(item['output_file']).name
                        validation = item['validation']
                        
                        f.write(f"- ✅ `{input_file}` → `{output_file}`\n")
                        
                        # Add validation details
                        if validation['download']['success']:
                            f.write(f"  - Download: ✅ Success\n")
                        
                        rel_info = validation['relevance']['details']
                        if validation['relevance']['success']:
                            f.write(f"  - Relevance: ✅ Score {rel_info.get('relevance_score', 0)}")
                            if rel_info.get('keywords_found'):
                                f.write(f" (found: {', '.join(rel_info['keywords_found'])})")
                            f.write("\n")
                        else:
                            f.write(f"  - Relevance: ⚠️ Limited relevance to {column}\n")
                        
                    f.write("\n")
                
                # Errors with validation context
                if column_result['errors']:
                    f.write("#### Errors\n\n")
                    for error in column_result['errors']:
                        file_name = Path(error['file']).name
                        stage = error.get('stage', 'unknown')
                        f.write(f"- ❌ `{file_name}` (stage: {stage}): {error['error']}\n")
                        
                        # Add validation details if available
                        if 'validation' in error:
                            validation = error['validation']
                            if not validation['download']['success']:
                                f.write(f"  - Download issue: {validation['download']['details']}\n")
                        
                    f.write("\n")
                
                # Skipped
                if column_result['skipped']:
                    f.write("#### Skipped\n\n")
                    for skipped in column_result['skipped']:
                        file_name = Path(skipped['file']).name
                        f.write(f"- ⏭️  `{file_name}`: {skipped['reason']}\n")
                    f.write("\n")
        
        print(f"\n📊 Validation report saved: {report_file}")


async def main():
    parser = argparse.ArgumentParser(
        description="Process downloaded files with validation and D4D agent to generate YAML metadata",
        epilog="Example: python validated_d4d_wrapper.py -i downloads_by_column -o data/extracted_by_column"
    )
    parser.add_argument("-i", "--input", default="downloads_by_column", 
                       help="Input directory with column-organized downloads")
    parser.add_argument("-o", "--output", default="data/extracted_by_column",
                       help="Output directory for D4D YAML files")
    parser.add_argument("--api-key", help="Anthropic API key (or set ANTHROPIC_API_KEY env var)")
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        os.environ["ANTHROPIC_API_KEY"] = args.api_key
    
    # Create and run wrapper
    try:
        wrapper = ValidatedD4DWrapper(args.input, args.output)
        results = await wrapper.process_all_columns()
        
        # Print final summary
        print("\n" + "="*60)
        print("VALIDATED D4D PROCESSING COMPLETE")
        print("="*60)
        summary = results['summary']
        val_sum = summary['validation_summary']
        
        print(f"✅ Files processed: {summary['total_processed']}")
        print(f"❌ Errors: {summary['total_errors']}")
        print(f"⏭️  Skipped: {summary['total_skipped']}")
        print(f"\n📊 Validation Results:")
        print(f"   Downloads: {val_sum['download_successful']} successful, {val_sum['download_failed']} failed")
        print(f"   Relevance: {val_sum['relevant_content']} relevant, {val_sum['irrelevant_content']} limited")
        print(f"\n📁 Output directory: {Path(args.output).absolute()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)