import unittest
from wordpress_to_blogger import *
#from wordpress_to_blogger import Post
class TestSequenceFunctions(unittest.TestCase):
        
		def testConvertToAtomDate(self):
			date = "2007-03-11 17:11:52"
			self.assertEqual('2007-03-11T17:11:52-06:00', ConvertToAtomDate(date))

		def testConnectToDb(self):
			exporter = WordpressExport()
			self.assert_(exporter.Connect())
			self.assert_(exporter.Query("Select sysdate()"))
			exporter.Disconnect()

		def testGetAllPosts(self):
			exporter = WordpressExport()
			exporter.Connect()
			posts = exporter.GetAllPosts()
			self.assertEqual(55,len(posts))
			exporter.Disconnect()

		def testGetCommentsForPost(self):
			exporter = WordpressExport()
			exporter.Connect()
			comments = exporter.GetCommentsForPost(2)
			self.assertEqual(1,len(comments))
			exporter.Disconnect()

if __name__ == '__main__':
    unittest.main()
