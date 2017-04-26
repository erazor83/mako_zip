import _mako_zip

from mako.template import TemplateLookup

mytemplate = TemplateLookup(
	uri="zip://templates.zip/simple.mako",
	filename=['zip','templates.zip','simple.mako']
)
print(mytemplate.render())

from mako.template import Template
from mako.lookup import TemplateLookup

mylookup = TemplateLookup(
	directories=[
		['zip','templates.zip']
	]
)
mytemplate = Template(
	"""<%include file="simple.mako"/> hello world!""",
	lookup=mylookup
)
