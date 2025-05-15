# Ancient method to extract text from PDF files using pdf2txt.py
input_dir="pdfFiles"
output_dir="textFiles"



for pdf in "$input_dir"/*.pdf; do
    if [ -f "$pdf" ]; then
        pdf2txt.py "$pdf" > "$output_dir/$(basename "${pdf%.pdf}.txt")"
        
        rm "$pdf"
        
        echo "Extracted text from $(basename "$pdf") and deleted the PDF."
    fi
done
