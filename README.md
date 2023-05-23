# Latex Preview

Quickly and effortlessly preview Latex equations, save them to a `.gif`
file, copy them to clipboard, or drag them to a document.

![screenshot](screenshot1.png)
![screenshot of the copy-paste feature](screenshot2.png)

## Dependencies

The following packages are _required_.

* `python3`
* `texlive` (or any installation of latex)
* `python3-gi`
* `gobject-introspection`
* `gir1.2-gtk-3.0`
* `dvipng`

Alternatively, you can use `docker` to build a docker image
from the supplied Dockerfile.

## Installation
Simply clone this repository, or download it.
```shell
$ git clone https://github.com/sbacco/LatexPreview.git
```

### On base system
If you have all the dependencies installed, you can run the
program with,
```shell
$ cd LatexPreview
$ python3 latexpreview.py
```

### With `docker-compose`, under `X11`
Edit `requirements.txt` to suit the TeX packages you wish to use.
By default, only the Debian package `texlive-science` is 
installed, taking up 1.29GB of disk space.
Installing `texlive-full` takes up approximately 8GB of disk space.

Ensure that you allow connections to your host's display from your internal network:
```shell
$ xhost +local:root
```
Create the docker image:
```shell
$ cd LatexPreview
$ docker-compose build
$ docker-compose up
```
And run the app like so,
```shell
$ docker-compose start
```
> ***Note:*** On systems not running on `X11`, it is still possible
> to run a local `XServer` and connect the app.
The file `docker-compose.yml` needs to be edited to suit your needs.
Instructions for Windows are coming soon.

## Use

Every control is pretty much intuitive. Hover the mouse over a button
to know its shortcut and what it does. You can resize the preview, 
change its color, copy the image to clipboard or save it.

You can also add __extra packages__ for latex that will be used by the
program (c.f. image above). The docker container comes with many
extra latex packages preinstalled.

Hope you enjoy!
