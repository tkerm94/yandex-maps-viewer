# yandex-maps-viewer
This is a small project implementing a simple map viewer using yandex maps api and pygame as gui interface.

## Installation and launching
First, clone the project and navigate to the project folder:
```
git clone https://github.com/tkerm94/yandex-maps-viewer && cd yandex-maps-viewer
```
Then you will need to install the `pygame` library, it is defined in the requirements.txt file, so just run this command:
```
pip install -r requirements.txt
```
You will also need to get the yandex maps search and geocoder api keys and then export them to a working shell:
```
export SEARCH_APIKEY=your_apikey
export GEOCODER_APIKEY=your_apikey
```
Then just run the `main.py` file, you can do this with this command:
```
python main.py
```
> Controls:\
> PgUp/PgDown - zoom in and out\
> Arrows - move one screen in any direction\
> LMB - add a marker to a point and show the address\
> RMB - adds a marker and shows the address of an organization if it is within a 50-meter radius around the point\
> Input field - enter an address to display on the map\
> Buttons - described by their labels
