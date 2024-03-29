rm upload.zip
rm -r upload/
rm -r download/

mkdir -p download/bin
curl -L https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip -o download/chromedriver.zip
curl -L https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-55/stable-headless-chromium-amazonlinux-2017-03.zip -o download/headless-chromium.zip
unzip download/chromedriver.zip -d download/bin
unzip download/headless-chromium.zip -d download/bin

mkdir upload
cp lambda_function.py upload/
cp -r src upload
cp -r download/bin upload/bin
# cp ./cells_to_arry.py upload/
# cp -r SeleniumDir upload
# cp ./expanded-bebop-246202-a2de23a0eef9.json upload/
pipenv lock -r > requirements.txt
pip install -r ./requirements.txt -t upload/
cd upload/
zip -r ../upload.zip --exclude=__pycache__/* .
cd ../

rm -r upload/
rm -r download/
