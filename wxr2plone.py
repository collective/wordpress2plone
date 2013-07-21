"""Wordpress WXR to Plone importer script

author: david@alteroo.com

Usage:

    Configure the parameters and then run with:
        bin/instance run wp2plone.py

Credits:
    davisagli <davisagli.com> <http://ow.ly/9Yw6x>
    zedr@ipnext.it  <https://github.com/zedr/wordpress2plone>
"""

import sys
import requests

from datetime import datetime
import xml.etree.ElementTree as ET
import transaction
from DateTime import DateTime

from zope.site.hooks import setSite
from zope.component import queryUtility, createObject

from zExceptions import BadRequest

from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.app.discussion.interfaces import IConversation

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManager import setSecurityPolicy

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.tests.base.security import (PermissiveSecurityPolicy,
                                                  OmnipotentUser)
from Testing.makerequest import makerequest


# --------------------------------------------------------------------------- #
# Start configuring here
# --------------------------------------------------------------------------- #

# Map Wordpress userids to Plone userids
USERID_MAPPING = {
    'admin': 'admin',
}
FILENAME = 'my.wordpress.2013-06-29.xml'
TYPES = ['page','post','info','story',]
# A target container name; e.g. 'news'
# Leave set to 'None' to create an import folder with a generic name
TARGET = None

# The Plone site name
PLONE_SITENAME = 'Plone'

# The userid of the manager
MANAGER_ID = 'admin'

# --------------------------------------------------------------------------- #
# End configuring here
# --------------------------------------------------------------------------- #


try:
    setSite(getattr(app, PLONE_SITENAME))
except AttributeError:
    print("""Plone site '%s' does not exist.
          You must use a valid and existing Plone site id as PLONE_SITENAME
          in the configuration section of this script.""" % PLONE_SITENAME)
    print ("Exiting.")
    sys.exit(1)

def spoofRequest(app):
    _policy=PermissiveSecurityPolicy()
    _oldpolicy=setSecurityPolicy(_policy)
    newSecurityManager(None, OmnipotentUser().__of__(app.acl_users))
    return makerequest(app)

app = spoofRequest(app)
plone = app.unrestrictedTraverse(PLONE_SITENAME)
plone.setupCurrentSkin(app.REQUEST)
admin = app.acl_users.getUserById(MANAGER_ID)
if not admin:
    print("""A Zope manager with id '%s' does not exist. " 
          You must use a valid and existing Zope manager id as MANAGER_ID"
          " in the configuration section of this script.""" % MANAGER_ID)
    print ("Exiting.")
    sys.exit(1)

newSecurityManager(None, admin)

def fix_text(text):
    """Fix the text and return it.

    @param text : a string of text or rich-text
    @return: the fixed text
    @rtype: str

    You can add other other fixes and tweaks here.
    """
    try:
        fixed = text.decode('utf-8')
    except UnicodeDecodeError:
        fixed = text.decode('latin-1')

    return fixed


class Importer(object):
    """The import object.

    Use method read_all() to read the wordpress data;
    use method write_all() to write to your Plone site.
    """

    target = TARGET

    def __init__(self, context):
        """Initialize.

        @param context : a Plone site
        """
        self._ctxt = context
        self._data = {}
        self._dbconn = None
        self._posts = {}
        self._set_up()

    def _set_up(self):
        self.normalizer = queryUtility(IIDNormalizer)
        t_name = self.target
        self._container = self._ctxt[t_name] if t_name else self._mk_container()

    def _mk_container(self):
        target = "".join((
            'wp-import', '-',
            self.normalizer.normalize(datetime.now().isoformat()),
        ))
        context = self._ctxt
        container = context[context.invokeFactory('Folder', target)]

        return container

    def read_posts(self):
        tree = ET.parse(FILENAME)
        root = tree.getroot()
        items = root._children[0].findall('item')
        rows = []
        for item in items:
            title = item.find('title').text
            description = item.find('description').text
            text = item.find('{http://purl.org/rss/1.0/modules/content/}encoded').text
            excerpt = item.find('{http://wordpress.org/export/1.2/excerpt/}encoded').text
            date = item.find('{http://wordpress.org/export/1.2/}post_date').text
            creator = item.find('{http://purl.org/dc/elements/1.1/}creator').text
            post_name = item.find('{http://wordpress.org/export/1.2/}post_name').text
            id = item.find('{http://wordpress.org/export/1.2/}post_id').text
            type = item.find('{http://wordpress.org/export/1.2/}post_type').text
            try:
                attachment_url = item.find('{http://wordpress.org/export/1.2/}attachment_url').text
            except:
                attachment_url = ""
            rows.append([id,creator,date,text,post_name,title,type,attachment_url])
        
        headers = ['id', 'creator', 'date', 'text', 'post_name','title','type','attachment_url']

        #rows = cur.fetchall()
        results = [dict(zip(headers, row)) for row in rows]

        print("Read %d Wordpress posts." % len(results))

        self._data['posts'] = results

    def read_comments(self):
        stmt = """SELECT comment_post_ID, comment_author, comment_author_email,
        comment_author_url, comment_date,
        ONVERT(comment_content USING latin1), user_id
        FROM wp_comments
        WHERE comment_approved = '1' AND comment_type='';"""

        headers = ['cid', 'name', 'email', 'url', 'date', 'text', '']

        cur = self._dbconn.cursor()
        cur.execute(stmt)
        rows = cur.fetchall()
        results = [dict(zip(headers, row)) for row in rows]

        print("Read %d Wordpress comments" % len(results))

        self._data['comments'] = results

    def read_all(self):
        self.read_posts()
        #self.read_comments()

    def write_posts(self):
        posts = self._data['posts']
        context = self._container

        used_ids = []
        for p in posts:
            short = self.normalizer.normalize(p['post_name'])
            if short in used_ids:
                short = "%s-1" % short
            p.update({
                'short': short
            })
            used_ids.append(p['short'])
            
            if p['type'] == 'attachment': 
                f = open('00000001.jpg','wb')
                #f.write(requests.get(p['attachment_url']).content)
                f_out = requests.get(p['attachment_url']).content
                image = context[context.invokeFactory('Image', p['short'], image=f_out)]
                f.close()
                 
            if p['type'] == 'attachment': continue
            post = context[context.invokeFactory('News Item', p['short'])]
            creator = p['creator']
            post.setTitle(p['title']) 
            post.setCreators(USERID_MAPPING.get(creator, creator))
            post.setEffectiveDate(DateTime(p['date']))
            try:
                post.setTitle(fix_text(p['title']))
            except:
                pass
            try:
                post.setText(fix_text(p['text']), mimetype='text/html')
            except:
                post.setText(p['text'], mimetype='text/html')
                print p['title'], " text failed"

            post.reindexObject()

            context.portal_workflow.doActionFor(post, 'publish')

            transaction.commit()

            print("Wrote %s" % post.absolute_url())

            self._posts[p['id']] = post

    def write_comments(self):
        comments = self._data['comments']

        for com in comments:
            cid = com['cid']
            posts = self._posts
            try:
                post = posts[cid]
            except KeyError:
                continue

            conversation = IConversation(post)

            date = DateTime(com['date']).asdatetime()

            comment = createObject('plone.Comment')
            comment.text = fix_text(com['text'])
            comment.author_name = comment.creator = com['name']
            comment.author_email = com['email']
            comment.creation_date = comment.modification_date = date

            conversation.addComment(comment)

            transaction.commit()

            print("Wrote comment by %s" % comment.creator)

    def write_all(self):
        self.write_posts()
        #self.write_comments()


# --------------------------------------------------------------------------- #
# Migration plan (the action happens here!)
# --------------------------------------------------------------------------- #

imp = Importer(plone)
imp.read_all()
imp.write_all()

print("The importer has finished all operations.")

# --------------------------------------------------------------------------- #
# End with a Python prompt
# ----------------------------------------------------------------------------#

__import__("code").interact(
        banner=""" Post-migration Python prompt. Control+d to exit. """, local=globals()
)
