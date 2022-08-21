# Crunchyroll Manga to Komga
(somewhat) effortlessy save manga from Crunchyroll locally

Crunchyroll's [manga offerings](https://www.crunchyroll.com/comics/manga)
are alright, I guess. It would be silly of me to say that the site and
mobile app are perfect--chapters that are a few months old can sometimes
disappear and even entire series, the UI, especially on mobile, can be
janky, sometimes, pages just don't load, and series are updated
horrendously slowly--but paying $8 to legally access nearly 40GB
of manga ain't that bad of a deal.

I created this tool in order to alleviate some of these problems.
It exports all manga on Crunchyroll to an agnostic format:
- folder for each series
	- cover art (cover.jpg)
	- [comic book archive](https://en.wikipedia.org/wiki/Comic_book_archive) (ZIP) for each chapter
		- pages in JPG format
		- [ComicInfo.xml](https://anansi-project.github.io/docs/comicinfo/intro) metadata

It's basically perfect for importing all of these series into
[Komga](https://komga.org/), the comic media server this tool was
built for. Of course, because of the simple organizational structure,
your file manager and any comic book archive reader is more than enough.
In fact, I used [Okular](https://okular.kde.org/) during development for 
testing.

Man, do I love making software which makes proprietary data agnostic and 
easy to use! Now, one has the freedom to read what they want on their own
time, to not lose access to content they paid for, to use the reader
which is most comfortable for them.

## How to Use

This program assumes that you have some advanced computer literacy, i.e. you can use the command line and can debug issues. It would be great if
you were a programmer.

The only tools you'll need are Git, Python, pip, and Poetry.

`git clone`, `cd`, and `poetry install`. Then run
`poetry run python -m crunchyroll_manga_to_komga <optional custom directory>`.
My tool will then start logging output, telling you what series, chapter,
and page is currently being downloaded.

Authentication makes use of a [`.netrc` file](https://www.gnu.org/software/inetutils/manual/html_node/The-_002enetrc-file.html). For the uninitiated,
simply create a text file called `.netrc` in your home/user directory:
and put the following text inside it:
```
machine crunchyroll.com login <your Crunchyroll username/email> password <your Crunchyroll password>
```
Make sure that you place appropriate file permissions on this file so that only your user account can access it.

All files are saved inside a `Crunchyroll` folder, which is inside your 
`Documents` folder, or the optional custom directory you specify via a positional command line argument.
As I said earlier, you'll be downloading tens of gigabytes of data, plus my tool regulary pauses in order
to avoid being rate-limited, so it's going to take a few days to download everything.
While my tool does have auto-resume functionality, it would be ideal for
you to run this on a secondary desktop computer if you want this to be done
in a reasonable amount of time.

On that auto-resume functionality, it makes a couple of assumtions which
you should be aware of:
- if a series' folder contains as many files as it does chapters plus 
the series cover, it assumes a series has been downloaded
- if `cover.jpg` exists, it assumes the cover has been downloaded
- if a chapter's archive exists and has a size greater than zero bytes,
it assumes the chapter has been downloaded.

Be especially weary of the last bullet point, as you may need to stop
the program in the middle of downloading a chapter for a variety of reasons,
and so also need to delete the remnant file, or else it will skip over it 
instead of trying to redownload it.

Don't start the program multiple times in rapid succession, or you may be rate-limited by Crunchyroll and will need to wait a few minutes before running again.

You may get occasionally get an error stating that a chapter isn't available; this isn't true. Simply delete the chapter file from your 
computer and try again.

Occasionally, you may see something like this in your console:
```
!! Page xx could not be found.
```
Don't freak out about this, this buggy behavior is actually the fault of
Crunchyroll and not you or I; it affects their mobile app. The developers
of Crunchyroll Manga are suprisingly incompitent and for some reason just
forget to assign pages URLs to download them from. If you notice an error like this when reading, feel free to try downloading the chapter again by deleting the file and running the program again.

I've also seen two cases of two images sharing the same page number and then one overwriting the other. Again, if you notice this while reading, all I can tell you is to stop the program, delete the appropriate file, and try running it again. I can't be completely sure that the pages that are given to me are already in the correct order and so rely on Crunchyroll's
assigned page numbers.

I've also seen cases of socket hangups before. If the program has halted for a few minutes, stop it, delete the file, and run it again.

Wow, is the infrastructure of this site bad!
