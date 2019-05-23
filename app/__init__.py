import dash
from flask import Flask
from flask.helpers import get_root_path


def create_app():
    server = Flask(__name__)
    register_dashapps(server)
    return server


def register_dashapps(app):
    from app.dashapp1.layout import layout
    from app.dashapp1.callbacks import register_callbacks

    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    dashapp1 = dash.Dash(__name__,
                         server=app,
                         url_base_pathname='/',
                         meta_tags=[meta_viewport],
                         external_stylesheets=external_stylesheets)
    
    dashapp1.index_string = '''
<!DOCTYPE html>
<html>
<style>
body{
	background-color: #f7fcfe;
}
header{
	background-color: #f7fcfe;
}
h1{
	display: block;
    margin-top: 0.67em;
  	margin-bottom: 0.67em;
  	text-align: center;
  	color: #0f0e6e;
}
footer{
	margin-top: 0em;
	background-color: #f7fcfe;
}
</style>
    <head>
        <title>Malware on Twitter</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
    	<header>
    		<h1> Detecting Malware names on Twitter </h1>
    	</header>
        {%app_entry%}
        {%config%}
        {%scripts%}
        {%renderer%}
        <footer>
            <center>
            	<figure>
            		<hr>
    				<img src="/static/logo.png" height='18'> 
    				<p style="font-size:7px;"><i>TruSTAR Technology © 2019</i></p> 
    				<br>
    			</figure>
    		</center>
        </footer>
    </body>
</html>
'''

    dashapp1.title = 'Malware on Twitter'
    dashapp1.layout = layout
    register_callbacks(dashapp1)

