Standalone MacOS widget

```sh
# setup
brew install libffi
conda create -n macos_widget python=3.9
conda activate macos_widget
pip install beaker-py rich rumps py2app

# to develop
python main.py # (only works with conda, no uv)

# to run (using a pm2 background process)
npm install -g pm2
pm2 start main.py --name "macos-widget" --interpreter python
pm2 save
pm2 startup
# pm2 list
# pm2 stop macos-widget
# pm2 restart macos-widget
```

**(Optional) To build as a standalone app:**

```sh
# (optional) to build as a standalone app
rm -rf build dist  # Clean previous build
python setup.py py2app

# to debug
./dist/main.app/Contents/MacOS/main

# to run
open dist/main.app
```