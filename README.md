# SMD Component search with pandas

A simple demo showing live filtering of a pandas dataframe using [enaml-web](https://github.com/codelv/enaml-web).

Try the demo on heroku https://fast-reaches-98581.herokuapp.com/
> Note: Heroku times out idle connections quickly. A real "app" should have a higher timeout and 
reconnect automatically. 

![pandas-data-frame-web-view-in-python](https://user-images.githubusercontent.com/380158/52954130-54d61b80-3357-11e9-81e3-84563096dc85.png)


All interaction is done on a single page through websockets.

To run localy

```bash
# make a virtual env
# then install
pip install pandas tornado enaml-web

# run
python main.py

```

