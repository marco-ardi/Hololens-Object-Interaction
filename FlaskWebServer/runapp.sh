export FLASK_APP=myapp
export FLASK_ENV=development
export FLASK_DEBUG=1
cd ..
sudo docker-compose up &
sleep 40
cd FlaskWebServer
python seleniumTest.py &
flask run --host=0.0.0.0 