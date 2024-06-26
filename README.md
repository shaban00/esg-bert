# ESG-BERT

---

## Domain Specific BERT Model for Text Mining in Sustainable Investing

### How to use the code

1. Install the latest version of python
   [Download Python](https://www.python.org/downloads/)

2. Clone the repository

   ```bash
   git clone https://github.com/shaban00/esg-bert.git
   ```

3. Change directory to the project

   ```bash
   cd esg-bert
   ```

4. Install python virtual environment

   ```bash
   python -m venv .venv
   ```

5. Activate python virtual environment

   - On **Windows**

   ```bash
     .venv\Scripts\activate
   ```

   - On **Linux/MacOS**

   ```bash
     source .venv/bin/activate
   ```

6. Install python dependencies

   ```python
   pip install pandas transformers tika tqdm openpyxl
   ```

   ```python
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

7. Run the script

   ```python
   python app.py -d 'directory1,directory2' -f 'file1,file2' -o 'filename.json'
   ```

   - You can specify either -d or -f or both
   - "-d" specifies directories separated with commas
   - "-f" specifies files separted with commas
   - "-o" specifies the JSON output filename. eg: output.json

8. Convert **JSON** output to **CSV**

   **Online**

   - [JSON TO CSV](https://data.page/json/csv)

   **Offline**

   ```python
   python convert.py -i "input_filename.json" -o "output_filename"
   ```

9. Import CSV into excel for analysis (optional)
