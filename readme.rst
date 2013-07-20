Wordpress to Plone importer
===========================


Introduction
------------

This is based on work done by zedr which is based on work done by davisagli.

For more information see "Notes on migrating this blog
from Wordpress to Plone" ( http://glicksoftware.com/blog/notes-on-migrating-this-blog-from-wordpress-to-plone ).

wp2plone.py - A self-contained script that will import all the posts and the comments from
a Wordpress 3.x database to a Plone site.
Requires the MySQL-python library to connect and execute SQL queries.

wxr2plone.py - Does a subset of the wp2plone.py script but does it from a WXR wordpress XML export (does not do comments yet)
Requires the python requests library.

Usage of wp2plone.py
------------------------

Before running, open the script in an editor and modify the MySQL database
connection parameters.

The script will create a temporary directory (e.g.
"wp-import-wp-import-2012-03-30t13-28-12-180396" and start creating content
inside it.

IMPORTANT! Run the script first on a staging or development server
DO NOT blindly run this on a production instance!

Run with:

    bin/instance run wp2plone.py


The script will do the following:

    - Perform security authentication procedures so it has the necessary rights
      to create content in Plone;
    - Connect to a MySQL database-server and read a Wordpress database;
    - Extract a subset of content and metadata, from posts and comments;
    - Convert this information in a number of 'News Item' and Comment objects;
    - Recatalog and publish the newly created items.


Usage of wxr2plone.py
--------------------------

Before running, open the script in an editor and modify the 'filename'. This refers to the wordpress WXR xml file.

The script will create a temporary directory (e.g.
"wp-import-wp-import-2012-03-30t13-28-12-180396" and start creating content
inside it.

IMPORTANT! Run the script first on a staging or development server
DO NOT blindly run this on a production instance!

Run with:

    bin/instance run wxr2plone.py



Credits
-------

    - davisagli (http://www.davisagli.com)
    - zedr (http://github.com/zedr)


License and warning
-------------------
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
