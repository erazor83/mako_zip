import _mako_zip

from mako.lookup import TemplateLookup

print(TemplateLookup)
mylookup = TemplateLookup(
	directories=[
		['zip','templates.zip']
	]
)
mytemplate=mylookup.get_template('inc_example.mako')
print(mytemplate.render())

#this should use the caching
mytemplate=mylookup.get_template('inc_example.mako')
print(mytemplate.render())
