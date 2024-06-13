# ESG-BERT

---

### Domain Specific BERT Model for Text Mining in Sustainable Investing

### Create python virtual environment

```python
python -m venv .venv
```

### Activate python virtual environment

```bash
source .venv/bin/activate
```

### Install python dependencies

```python
pip install pandas transformers tika tqdm
```

```python
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Convert JSON file to CSV and Excel

```python
python convert.py -i input_file.json -o output_file
```
