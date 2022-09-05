## da Websocket Client ##

I googled to find WS Client that support both WS/WSS with specified certificate file but not found anyone.<br>I don't want wasting time for finding it anymore. So, I decided to make this tool for work and those who needed.

#### Features #####

* Support both `Websocket (WS)` & `Websocket Secure (WSS)` protocol
* Support send/receive/display `Text` & `Binary` data type
* Support custom websocket header
* Support save/load preferences from JSON file
* Support cross-platform like Windows, Linux, macOS, etc
* Others

#### Instructions #####

> 1. Open a CMD Window in the `da-Websocket-Client` folder
> 2. Run the command `pip install -r requirements.txt` to install required packages
> 3. Run the command `python app.py` to run app from the source code
> 4. *(Optional) Run the command `PyInstaller --clean --distpath=bin da-Websocket-Client.spec` to build executable file*
> 3. *(Optional) Run the command file `create-package.cmd` to create a zip package (for Windows) or [download](https://github.com/vic4key/da-Websocket-Client/releases) directly from repository*

*Note: (Optional) The sample SSL file for local machine (`localhost` & `127.0.0.1`) can be found in the `preferences` folder or you can generate your own SSL file  by run the following command*
> openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes -keyout local.pem -out local.pem -subj "/CN=localhost" -addext "subjectAltName=IP:127.0.0.1"

#### Screenshots #####

![](screenshots/app.png)

#### Contact

Feel free to contact via [Twitter](https://twitter.com/vic4key) / [Gmail](mailto:vic4key@gmail.com) / [Blog](https://blog.vic.onl/) / [Website](https://vic.onl/)
