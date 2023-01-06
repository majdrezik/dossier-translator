# dossier-translator

software engineering degree final project

1. **clone the project via ssh:**

works: docker image build -t doss_app .
works: docker run --name doss_app_container -p 8080:8080 -d doss_app

#

    git clone git@github.com:majdrezik/dossier-translator.git

#

2. **install the required packages:**

#

    cd dossier-translator

ONLY ONCE:

    docker build . -t doss_app

#

3. **run the server:**

#

WHEN THE IMAGE IS DONE, RUN:

    docker run -it --name doss_app_container \
    -v $PWD:/dossier-translator \
    -p 5000:5000 \
    doss_app

Navigate to `http://127.0.0.1:5000/login` in your browser, ENJOY!
