# dossier-translator

software engineering degree final project

1. **clone the project: (here I'm using SSH, but you can do as you like)**

#

    git clone git@github.com:majdrezik/dossier-translator.git

#

2. **install the required packages:**
Navigate to the project, open the terminal there and install the requirements. (You need pip for that, [see more](https://pip.pypa.io/en/stable/cli/pip_install/) 
#

    cd dossier-translator
    pip3 install -r requirements.txt

#

3. **run the server:**

#

    FLASK_APP=server.py flask run
    
By default, the app runs on `PORT 5000` <br>
To run the app on a specific PORT, add `-p` option. for instance:

    FLASK_APP=server.py flask run -p 8080

Navigate to `http://localhost:{YOUR_PORT}/` in your browser, ENJOY!
