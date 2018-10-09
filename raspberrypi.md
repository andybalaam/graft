## How to set up Graft on the Raspberry Pi

Because the Rapsberry Pi uses a slightly older Python version, there is a
special version of Graft for it.

Here's how to get it:

* Open a terminal window by clicking the black icon with a ">" symbol on it at
  the top near the left.

* First we need to install a couple of things Graft needs, so type this, then
  press Enter:

```bash
sudo apt install python3-attr at-spi2-core
```

* If you want to be able to make animated GIFs, install one more thing:

```bash
sudo apt install imagemagick
```

* To download Graft and switch to the Raspberry Pi version, type in these
  commands, pressing Enter after each line.

```bash
git clone https://github.com/andybalaam/graft.git
cd graft
git checkout raspberry-pi
```

* Now, you should be able to run Graft just like on another computer, for
  example, like this:

```bash
./graft 'd+=10 S()'
```

If you're looking for a fun way to start, why not try the worksheet
["Tell a story by making animations with code"](http://www.artificialworlds.net/blog/2018/09/24/worksheet-tell-a-story-by-making-animations-with-code/)?
