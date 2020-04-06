mkdir pandemic_tmp
cd pandemic_tmp
python3 -m venv pandemic
source pandemic/bin/activate
pip install --upgrade pandemic
python3 -c "import pandemic; pandemic.run()"