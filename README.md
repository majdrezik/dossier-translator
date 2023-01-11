# dossier-translator

software engineering degree final project

1. **clone the project via ssh:**

#

    git clone git@github.com:majdrezik/dossier-translator.git

#

2. **install the required packages:**

#

    cd dossier-translator
    pip3 install -r requirements.txt

#

3. **run the server:**

#

    FLASK_APP=server.py flask run
    
To run the app on a specific PORT, add `-p` option. for instance:

    FLASK_APP=server.py flask run -p 8080

Navigate to `http://localhost:{YOUR_PORT}/` in your browser, ENJOY!
