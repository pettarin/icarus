# icarus

**icarus** is a Sigil plugin to create EPUB 3 Audio-eBooks

* Version: 0.0.3
* Date: 2016-02-12
* Developer: [Alberto Pettarin](http://www.albertopettarin.it/)
* License: the MIT License (MIT)
* Contact: [click here](http://www.albertopettarin.it/contact.html)

**Important**:
until reaching v1.0.0,
this Sigil plugin should be considered **experimental**.
Please report any issues or suggestions, thank you!


## Goal

**icarus** helps creating EPUB 3 Audio-eBooks
using [Sigil](http://sigil-ebook.com/) and [aeneas](http://www.readbeyond.it/aeneas/).

An EPUB 3 Audio-eBook is an [EPUB 3](http://idpf.org/epub/301) file with reflowable rendition
and audio/text synchronization expressed by
[EPUB 3 Media Overlays](http://www.idpf.org/epub/301/spec/epub-mediaoverlays.html)
(MO) via SMIL files.
For an introduction to EPUB 3 Audio-eBooks, see
[this tutorial](http://www.albertopettarin.it/blog/2014/08/02/how-to-create-epub-3-read-aloud-ebooks.html).

Specifically, **icarus** provides the following three functions (which can be used independently one from another):

1. automatically inserting MO attributes (`id` and `class`) into the XHTML files selected by the user;
1. creating a ZIP file which can be read by [aeneas](http://www.readbeyond.it/aeneas/) or uploaded to [aeneasweb.org](http://aeneasweb.org/) to compute the SMIL files describing EPUB 3 Media Overlays;
1. importing the SMIL files into the current Sigil eBook.

The final EPUB 3 Audio-eBook file can be then exported using the
[ePub3-itizer Sigil plugin](http://www.mobileread.com/forums/showthread.php?t=250566),
v0.3.6 or later.

The main goal of **icarus** consists in providing regular users
with the opportunity of creating EPUB 3 Audio-eBooks with Sigil,
leveraging [aeneas](http://www.readbeyond.it/aeneas/)
for the actual computation of timing values in the SMIL files.

Currently [Sigil](http://sigil-ebook.com/) does not have full native support for EPUB 3,
but it is actively transitioning from EPUB 2 to EPUB 3,
and its plugin mechanism allows the user to export EPUB 3 files,
including support for EPUB 3 Media Overlays.
When Sigil will have native support for EPUB 3
this plugin might be retired or re-purposed.


## Installation

1. Download the **icarus** Sigil plugin from [MobileRead](http://www.mobileread.com/forums/showthread.php?t=268702) or from the [plugin](plugin/) directory
1. Open Sigil
1. Add the **icarus** plugin (Plugins > Manage Plugins > Add Plugin > select the downloaded ZIP file)

To export to EPUB 3, you will also need to:

1. Download the **ePub3-itizer** Sigil plugin, v0.3.6 or later, from [MobileRead](http://www.mobileread.com/forums/showthread.php?t=250566) or from [source](https://github.com/kevinhendricks/ePub3-itizer/tree/master/plugin)
1. Add it to Sigil as above (Plugins > Manage Plugins > Add Plugin > select the downloaded ZIP file)


## Compatibility Chart

As mentioned above, the **icarus** plugin should be considered
a temporary workaround until Sigil implements full Media Overlays native support.

Moreover, the current **Sigil 0.9.x** series is undergoing a number
of deep code/feature changes, and any new version might break this plugin.
The same applies to the **ePub3-itizer** plugin.

Please be sure you are running one of the following supported combinations:

| Sigil                 | icarus   | ePub3-itizer          |
|-----------------------|----------|-----------------------|
| >= 0.9.0 and <= 0.9.2 | <= 0.0.2 | >= 0.3.4 and <= 0.3.5 |
| >= 0.9.3 and          | >= 0.0.3 | == 0.3.6              |

As of 2016-12-08, **icarus 0.0.3** has been tested working correctly
with **Sigil 0.9.7** and **ePub3-itizer 0.3.6**.


## Usage

Please read the [tutorial](tutorial/) for detailed information about using **icarus**,
including conventions and limitations.

Although the changes done by this plugin to the code of your eBook can be reverted,
**always save a backup copy of your EPUB file before using this plugin!**

1. Open your eBook in Sigil
1. Select the XHTML files with associated audio on the Book Browser panel
1. Plugins > Edit > icarus


## Features

* Add MO `id` and `class` attributes to user-selected XHTML files.
* Both `id` and `class` values are user-selectable (with default values `f[0-9]{6}` and `mo` respectively).
* Automatically added MO attributes can be removed.
* Handle pre-existing `id` attributes.
* Handle pre-existing `class` attributes.
* The user can specify the list of tags to be processed.
* The user can specify a "no MO" `class` attribute (with user-selectable value, default `nomo`) to avoid processing a specific element.
* The user can specify that the MO `class` should be added only to tags having a pre-existing MO `id` attribute.
* The (text, audio) file pairs can be detected automatically by matching their file names.
* The user can modify the list of (text, audio) files before exporting the aeneas job ZIP file.
* The exported aeneas job ZIP file can be immediately processed by [aeneas](http://www.readbeyond.it/aeneas/) or [aeneasweb.org](http://aeneasweb.org/).
* The SMIL files computed by aeneas can be imported directly from the ZIP file generated by aeneas.


## Limitations and Missing Features

* Identifiers are added to existing tags only. A future release will add `<span>` tags to support segmenting the text at finer granularity.
* XHTML files and audio files must have a 1:1 correspondence.
* This plugin reads the eBook metadatum `dc:language` to set the language in the configuration file (`config.xml`) of the aeneas job ZIP file. The language value is assumed to be the same for all the tasks in the job. If your eBook has multiple languages you will need to manually edit the `config.xml` file before running `aeneas` on it.
* No way of specifying the head/tail values of each audio file, which is processed from start to end.
* No way of specifying special aeneas parameters.
* No way of specifying the media narrator metadatum.
* The media active and media playback active classes must be manually added to the book CSS file by the user.


## Change log

* 0.0.3 2016-02-12 Update to make the plugin work in Sigil v0.9.3 and later
* 0.0.2 2015-12-29 Added option for adding MO class only to elements with pre-existing MO id attribute
* 0.0.1 2015-12-16 Initial release

(You can download previous versions of the plugin from the [plugin/](plugin/) directory.


## License

**icarus** is released under the MIT License.

The included files `compatibility_utils.py`, `epub_utils.py`, and `unipath.py`
are copied from the [ePub3-itizer Sigil plugin](https://github.com/kevinhendricks/ePub3-itizer).
See their source code for licensing details.

The audio files in the `tutorial/` directory are excerpts
from [LibriVox](https://librivox.org/) public domain recordings.

No copy rights were harmed in the making of this project.



