# mako/lookup.py
# Copyright (C) 2017 Alexander Krause <alexander.krause@ed-solutions.de>
#
# overrides mako packages to allow templates from zip files
#
# This module is part of Mako and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import mako
import mako.util
import mako.template
import mako.lookup
import mako.exceptions

import re
import os
import zipfile
import threading
import stat
#add zip support for mako
	
mako.template.oTemplate=mako.template.Template
class _Template(mako.template.oTemplate):
	def __init__(self,*args,**kwargs):
		#print('Template',kwargs['filename'])
		self._filename=kwargs['filename']
		#kwargs['filename']=kwargs['filename'][2]
		mako.template.oTemplate.__init__(self,*args,**kwargs)
	
	def _compile_from_file(self,path,filename):
		#print('_mako_zip_file',self,path,filename)
		if type(filename)==list:
			if filename[0]=='zip':
				#data = util.read_file(filename)
				zfile=zipfile.ZipFile(filename[1])
				data= zfile.read(filename[2])
				#print('file_content',data)
				code, module = mako.template._compile_text(
					self,
					data,
					filename
				)
				self._source = None
				self._code = code
				mako.template.ModuleInfo(module, None, self, filename, code, None)
				return module
		return mako.template.oTemplate._compile_from_file(self,path,filename)
mako.template.Template=_Template

mako.lookup.oTemplateLookup=mako.lookup.TemplateLookup
class _TemplateLookup(mako.lookup.oTemplateLookup):
	def __init__(self,
							directories=None,
							module_directory=None,
							filesystem_checks=True,
							collection_size=-1,
							format_exceptions=False,
							error_handler=None,
							disable_unicode=False,
							bytestring_passthrough=False,
							output_encoding=None,
							encoding_errors='strict',

							cache_args=None,
							cache_impl='beaker',
							cache_enabled=True,
							cache_type=None,
							cache_dir=None,
							cache_url=None,

							modulename_callable=None,
							module_writer=None,
							default_filters=None,
							buffer_filters=(),
							strict_undefined=False,
							imports=None,
							future_imports=None,
							enable_loop=True,
							input_encoding=None,
							preprocessor=None,
							lexer_cls=None):

		#self.directories = [
		#	posixpath.normpath(d) for d in mako.util.to_list(directories, ())
		#]
		self.directories = directories
		self.module_directory = module_directory
		self.modulename_callable = modulename_callable
		self.filesystem_checks = filesystem_checks
		self.collection_size = collection_size

		if cache_args is None:
			cache_args = {}
		# transfer deprecated cache_* args
		if cache_dir:
			cache_args.setdefault('dir', cache_dir)
		if cache_url:
			cache_args.setdefault('url', cache_url)
		if cache_type:
			cache_args.setdefault('type', cache_type)

		self.template_args = {
			'format_exceptions': format_exceptions,
			'error_handler': error_handler,
			'disable_unicode': disable_unicode,
			'bytestring_passthrough': bytestring_passthrough,
			'output_encoding': output_encoding,
			'cache_impl': cache_impl,
			'encoding_errors': encoding_errors,
			'input_encoding': input_encoding,
			'module_directory': module_directory,
			'module_writer': module_writer,
			'cache_args': cache_args,
			'cache_enabled': cache_enabled,
			'default_filters': default_filters,
			'buffer_filters': buffer_filters,
			'strict_undefined': strict_undefined,
			'imports': imports,
			'future_imports': future_imports,
			'enable_loop': enable_loop,
			'preprocessor': preprocessor,
			'lexer_cls': lexer_cls
		}

		if collection_size == -1:
			self._collection = {}
			self._uri_cache = {}
		else:
			self._collection = util.LRUCache(collection_size)
			self._uri_cache = util.LRUCache(collection_size)
		self._mutex = threading.Lock()
				
	def get_template(self,uri):
		#print('get_template',uri,self.filesystem_checks,self._check,self._collection)
		try:
			if self.filesystem_checks:
				return self._check(uri, self._collection[uri])
			else:
				return self._collection[uri]
		except KeyError:
			u = re.sub(r'^\/+', '', uri)
			for cDir in self.directories:
				if type(cDir)==list:
					if cDir[0]=='zip':
						if os.path.exists(cDir[1]) and zipfile.ZipFile(cDir[1]).getinfo(u):
							return self._load(cDir+[u],uri)
							
				else:
					srcfile=os.path.isfile(os.path.join(cDir,u))
					if os.path.isfile(srcfile):
						return self._load(srcfile,uri)
				
			raise exceptions.TopLevelLookupException(
				"Cant locate template for uri %r" % uri
			)

	def _check(self,uri,template):
		#print('_mako_lookup_check_zipfile',uri)
		if template.filename is None:
			return template
		
		try:
			#print(template.filename)
			template_stat = os.stat(template.filename[1])
			if template.module._modified_time < \
						template_stat[stat.ST_MTIME]:
				self._collection.pop(uri, None)
				return self._load(template.filename, uri)
			else:
				return template
		except OSError:
			self._collection.pop(uri, None)
			raise mako.exceptions.TemplateLookupException(
					"Cant locate template for uri %r" % uri
			)
		
	def _load(self,filename,uri):
		self._mutex.acquire()
		try:
			try:
				# try returning from collection one
				# more time in case concurrent thread already loaded
				return self._collection[uri]
			except KeyError:
				pass
			try:
				if self.modulename_callable is not None:
					module_filename = self.modulename_callable(filename, uri)
				else:
					module_filename = None
					
				#print('filename',filename)
				self._collection[uri] = template = _Template(
					uri=uri,
					filename=filename,
					lookup=self,
					module_filename=module_filename,
					**self.template_args
				)
				return template
			except:
				# if compilation fails etc, ensure
				# template is removed from collection,
				# re-raise
				self._collection.pop(uri, None)
				raise
		finally:
			self._mutex.release()
		
mako.lookup.TemplateLookup=_TemplateLookup
