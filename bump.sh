cp /Users/pcotton/github/pandemic-fake-config/config_private.py /Users/pcotton/github/pandemic/pandemic
cd /Users/pcotton/github/pandemic/
rm /Users/pcotton/github/pandemic/dist/*
python setup.py sdist bdist_wheel
twine upload dist/*
cp /Users/pcotton/github/pandemic-real-config/config_private.py /Users/pcotton/github/pandemic/pandemic
