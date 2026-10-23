**************
Métamorphose 3
**************

Métamorphose is a graphical mass renaming program for files and folders.

These are the command line options::

  -h,  --help       Show help screen and exit.
  -t,  --timer      Show time taken to complete operations.
  -d,  --debug      Show debugging information.
  -p=, --path       Specify a directory to load.
  -c=, --config     Specify a configuration file to load.
  -a=, --auto       Specify automatic mode level to use with configuration file:
                      0 = do not preview items
                      1 = auto preview items
                      2 = auto rename items
                      3 = auto rename items and exit on success
  -l=, --language   Override preferred language:
                      en_US
                      fr
                      es

If no other options are given, you may specify a path to open::

  $ metamorphose3 /srv/samba/Windows Likes Spaces

===================
Running from Source
===================

What follows is for developers or those wishing to use the very latest version.

For binary (normal) installs, use the appropriate install file for your system
(setup.exe, .deb, etc ...).


Cloning
=======

Cloning the sources from the remote::

  git clone https://github.com/Arean82/metamorphose3.git


Requirements
============

- Python 3.12 or greater
- wxPython 4.2 (Phoenix)
- Pillow 9.0 or greater
- exifread 3.0 or greater
- mutagen 1.45 or greater

Install the Python dependencies with::

  pip install -r requirements.txt


Running
=======

Create or update the language files::

  make -C messages build

Launch the application::

  ./metamorphose3


Installing
==========

As root::

  make all

Under Linux & freeBSD
The makefile should take care of everything for you, it is architecture and distro independant.

Métamorphose will be installed in ``/usr/share/metamorphose3``, you can run it with::

  metamorphose3

and access the man page with::

  man metamorphose3

If you are using a freedesktop.org compatible window manager (like Gnome or KDE),
there should be an entry in ``Applications`` -> ``Accessories``.


Removing
========
Remove the user-specific files here:

- Windows: ``C:\Documents and Settings\USERNAME\Application Data\.metamorphose3``
- Linux/BSD: ``~/.metamorphose3``
- Mac: ``/Library/Application Support/.metamorphose3``

In Linux & BSD, if you have the sources::

  make remove

To remove all user files as well::

  make remove remusr=1


==============
Upgrading
==============

Settings and undo logs from earlier versions are not read. User data lives in
``.metamorphose3``; the application starts with default preferences on first
launch. Recreate any settings through the preferences dialog.


============
Known Issues
============

Program locks up when 'walking' a large number of files/folders

  Not really locked up, but the time it takes to process entries can be long if you
  are loading many items. During this process the application doesn't refresh, giving
  the appearance of being locked up but is actually working on stuff.

  The time in this state is dependent on your computer, whether the directory is
  on a local drive or a network share, and of course the number of items.

  This will be addressed in a future release.


Unreadable picker items under Linux (possibly other GTK)

  There seems to be a bug in wxGTK, the list can become slow and unreadable when dealing with large number of
  items (over 10 000).

  A work around may be possible.


Thumbnails fail

  There seems to be some problems with Pillow under windows. Sometimes the image will not load.
