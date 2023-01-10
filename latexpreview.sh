#!/bin/sh

if [ ! -f $HOME/.latexpreview.json ]; then
    echo\
    '{"code": "", "resolution": 200.0, "color": {"red": 0.0, "green": 0.0, "blue": 0.0}, "packages": []}'\
    > $HOME/.latexpreview.json
    chmod 666 $HOME/.latexpreview.json
fi

xhost +local:root
docker run --rm\
    --env="DISPLAY"\
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw"\
    --mount type=bind,source=$HOME/.latexpreview.json,target=/app/.conf.json\
    latexpreview
xhost -local:root
