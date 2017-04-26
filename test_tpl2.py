import _mako_zip

from mako.lookup import TemplateLookup

print(TemplateLookup)
mylookup = TemplateLookup(
	directories=[
		['zip','templates.zip']
	]
)
mytemplate=mylookup.get_template('simple.mako')
print(mytemplate.render())

#this should use the caching
mytemplate=mylookup.get_template('simple.mako')
print(mytemplate.render())
