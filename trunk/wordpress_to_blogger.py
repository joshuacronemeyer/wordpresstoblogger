try:
	from xml.etree import ElementTree # for Python 2.5 users
except:
	from elementtree import ElementTree
from gdata import service
import gdata
import atom
import getopt
import sys
import MySQLdb
import time

class BloggerExample:
	def __init__(self, email, password):

		# Authenticate using ClientLogin.
		self.service = service.GDataService(email, password)
		self.service.source = 'Blogger_Python_Sample-1.0'
		self.service.service = 'blogger'
		self.service.server = 'www.blogger.com'
		self.service.ProgrammaticLogin()

		# Get the blog ID for the first blog.
		feed = self.service.Get('/feeds/default/blogs')
		for a_link in feed.entry[0].link:
			if a_link.rel == 'self':
				self.blog_id = a_link.href.split("/")[-1]
	  
	def CreatePost(self, title, content, author_name, date, is_draft):

		# Create the entry to insert.
		entry = gdata.GDataEntry()
		entry.author.append(atom.Author(atom.Name(text=author_name)))
		entry.title = atom.Title('xhtml', title)
		entry.content = atom.Content('html', '', content)
		entry.published = atom.Published(date)
		if is_draft:
			control = atom.Control()
			control.draft = atom.Draft(text='yes')
			entry.control = control
		# Ask the service to insert the new entry.
    		return self.service.Post(entry,'/feeds/' + self.blog_id + '/posts/default')
	
	def CreateComment(self, post_id, comment_text, comment_creator, comment_uri):
		# Build the comment feed URI
		feed_uri = '/feeds/' + self.blog_id + '/' + post_id + '/comments/default'
		print "FEED URI::::::::::: " + feed_uri +"\n"
		# Create a new entry for the comment and submit it to the GDataService
		entry = gdata.GDataEntry()
		entry.content = atom.Content('xhtml', '', comment_text)
		entry.author.append(atom.Author(atom.Name(text=comment_creator)))
		return self.service.Post(entry, feed_uri)

	def GenAllComments(self, public_post, post):
		
		self_id = public_post.id.text
		tokens = self_id.split("-")
		post_id = tokens[-1]			
		print "Now posting all comments on the post titled: \"" + public_post.title.text + "\"."
		for comment in post.comments:
			public_comment = self.CreateComment(post_id, comment.content, comment.author, comment.authorUrl)
			print "Successfully posted \"" + public_comment.content.text + "\" on the post titled: \"" + public_post.title.text + "\".\n"
	
	def run(self):
		exporter = WordpressExport()
		exporter.Connect()
		posts = exporter.GetAllPosts()
		failures = []
		for post in posts:
			public_post = self.CreatePost(post.title, post.content, 'Josh', post.date, False)
			print "Successfully created public post: \"" + public_post.title.text + "\".\n"
			try:
				self.GenAllComments(public_post, post)
			except:
				print "ERROR! WITH: \"" + public_post.title.text + "\".\n"
				failures = failures + [public_post.title.text]

		for failure in failures:
			print "Do this one manually: " + failure + "\n"
	
class WordpressExport:		
  
	def Connect(self):
		self.connection = MySQLdb.connect("localhost", "josh_wordpress", "josh_wordpress", "josh_wordpress")
		return self.connection
	
	def Disconnect(self):
		return self.connection.close()

	def Query(self, query):
		cursor = self.connection.cursor()
		cursor.execute(query)
		return cursor

	def GetAllPosts(self):
		query = "select wp_posts.ID, wp_posts.post_title, wp_posts.post_content, wp_posts.post_date from wp_posts"
		posts = []
		for row in self.Query(query):
			post = Post(row[0],row[1],row[2],row[3])
			post.addComments(self.GetCommentsForPost(post.id))
			posts = posts + [post]
		return posts

	def GetCommentsForPost(self, postId):
		query = "select wp_comments.comment_author, wp_comments.comment_author_url, wp_comments.comment_date, wp_comments.comment_content from wp_comments where wp_comments.comment_post_ID = '" + `postId` + "' AND wp_comments.comment_approved = '1'"
		comments = []
		for row in self.Query(query):
			comments = comments + [Comment(row[0],row[1],row[2],row[3])]
		return comments

class Comment:
	def __init__(self, author, authorUrl, date, content):
		self.author = author
		self.authorUrl = authorUrl
		self.date = ConvertToAtomDate(date.isoformat(' '))
		self.content = content

	def toString(self):
		print "Comment=> author:" + self.author + " authorUrl:" + self.authorUrl + " date:" + self.date + " content:" + self.content

class Post:
	def __init__(self, id, title, content, date):
		self.id = id
		self.title = title
		self.content = content
		self.date = ConvertToAtomDate(date.isoformat(' '))
	
	def addComments(self, comments):
		self.comments = comments

def ConvertToAtomDate(date):

	fullDate = date.split(' ')[0]
	time = date.split(' ')[1]
	return fullDate + 'T' + time + '-06:00'

def main():

  # parse command line options
  try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["email=", "password="])
  except getopt.error, msg:
    print ('python BloggerExample.py --email [email] --password [password] ')
    sys.exit(2)
  
  email = '' 
  password = ''
  
  # Process options
  for o, a in opts:
    if o == "--email":
      email = a
    elif o == "--password":
      password = a
     
  if email == '' or password == '':
    print ('python BloggerExample.py --email [email] --password [password]')
    sys.exit(2)
  
  sample = BloggerExample(email, password)
  sample.run()


if __name__ == '__main__':
  main()

