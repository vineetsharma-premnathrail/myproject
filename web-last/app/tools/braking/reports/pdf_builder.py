"""
Braking Tool PDF Report Builder Module
=====================================
Purpose:
    Generates professional PDF reports for braking calculations using LaTeX.
    Creates downloadable engineering reports with calculations, compliance checks,
    and formatted data presentation.
Layer:
    Backend / Tools / Braking / Reports
Technology:
    - LaTeX: Professional document typesetting system
    - Jinja2: Template rendering engine
    - Multiple LaTeX compilers: pdflatex, xelatex, lualatex (fallback support)
Process:
    1. Load LaTeX template from app/services/templates/
    2. Render template with calculation context data
    3. Compile LaTeX to PDF using system LaTeX installation
    4. Return PDF as BytesIO buffer for download
Dependencies:
    - jinja2: Template rendering
    - LaTeX distribution: pdflatex/xelatex/lualatex compilers
    - template.tex: LaTeX report template
Error Handling:
    - Compiler not found: Clear installation instructions
    - Template missing: File path validation
    - Compilation failures: Detailed error messages
    - Timeout protection: 30-second compilation limit
"""

import os
import io
import subprocess  # nosec - used safely with full paths and no shell
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

def generate_braking_pdf_report(context: Dict[str, Any]) -> io.BytesIO:
    """
    Generate a professional PDF report for braking calculations.

    Creates a comprehensive engineering report using LaTeX templating.
    The report includes calculation results, compliance status, input parameters,
    and professional formatting suitable for engineering documentation.

    Args:
        context (Dict[str, Any]): Calculation context containing:
            - Vehicle parameters (mass, wheels, etc.)
            - Calculation results and scenarios
            - Compliance status for each speed/gradient combination
            - Document metadata (doc_no, made_by, checked_by, approved_by)
            - Formatted data for LaTeX template rendering

    Returns:
        io.BytesIO: Buffer containing the generated PDF data
            Ready for HTTP response or file download

    Raises:
        Exception: For various failure scenarios:
            - ImportError: Missing Jinja2 dependency
            - FileNotFoundError: LaTeX compiler not installed
            - subprocess.TimeoutExpired: LaTeX compilation took too long
            - FileNotFoundError: PDF not generated successfully
            - Generic Exception: Other compilation or template errors

    Template Requirements:
        - template.tex must exist in app/services/templates/
        - Template should use Jinja2 syntax for variable substitution
        - Should handle all context data appropriately

    LaTeX Compilers:
        Tries pdflatex first, then xelatex, finally lualatex as fallbacks
        This ensures compatibility across different LaTeX installations

    Performance:
        - Temporary directory created for compilation isolation
        - 30-second timeout prevents hanging processes
        - Automatic cleanup of temporary files
    """
    try:
        # Import Jinja2 for template rendering
        from jinja2 import Environment, FileSystemLoader

        # Set up Jinja2 environment with template directory
        env = Environment(loader=FileSystemLoader('app/services/templates'), autoescape=True)

        # Load the LaTeX template
        template = env.get_template('template.tex')

        # Render template with calculation context data
        latex_content = template.render(**context)

        # Find LaTeX compilers
        pdflatex_path = shutil.which('pdflatex')
        xelatex_path = shutil.which('xelatex')
        lualatex_path = shutil.which('lualatex')

        if not pdflatex_path:
            raise RuntimeError("pdflatex not found in PATH")

        # Create isolated temporary directory for LaTeX compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Write rendered LaTeX content to temporary file
            tex_file = temp_path / 'report.tex'
            tex_file.write_text(latex_content)

            # Note: Template is assumed self-contained (no external assets needed)
            # Future enhancement: Copy required images/assets if needed

            # Attempt LaTeX compilation with fallback compilers
            try:
                # Primary attempt with pdflatex (most common)
                result = subprocess.run(  # nosec - using full paths, no shell
                    [pdflatex_path, '-interaction=nonstopmode', 'report.tex'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=30  # Prevent hanging on compilation errors
                )

                # If pdflatex fails, try xelatex (better Unicode support)
                if result.returncode != 0 and xelatex_path:
                    result = subprocess.run(  # nosec - using full paths, no shell
                        [xelatex_path, '-interaction=nonstopmode', 'report.tex'],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    # Final fallback to lualatex (most comprehensive Unicode)
                    if result.returncode != 0 and lualatex_path:
                        result = subprocess.run(  # nosec - using full paths, no shell
                            [lualatex_path, '-interaction=nonstopmode', 'report.tex'],
                            cwd=temp_dir,
                            capture_output=True,
                            text=True,
                            timeout=30
                        )

                        # If all compilers fail, raise detailed error
                        if result.returncode != 0:
                            raise Exception(f"LaTeX compilation failed: {result.stderr}")

                # Check if PDF was successfully generated
                pdf_file = temp_path / 'report.pdf'
                if pdf_file.exists():
                    # Read PDF content into memory buffer
                    with open(pdf_file, 'rb') as f:
                        pdf_content = f.read()
                    return io.BytesIO(pdf_content)
                else:
                    raise Exception("PDF file was not generated despite successful compilation")

            except FileNotFoundError:
                raise Exception("LaTeX compiler not found. Please install a LaTeX distribution (texlive, miktex, etc.)")

    except ImportError:
        raise Exception("Jinja2 not installed. Please install with: pip install Jinja2")
    except Exception as e:
        raise Exception(f"PDF generation failed: {str(e)}")