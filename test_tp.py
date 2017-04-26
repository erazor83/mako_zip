import _mako_zip

from mako.template import Template

mytemplate = Template(uri="zip://templates.zip/simple.mako",filename=['zip','templates.zip','simple.mako'])
print(mytemplate.render())

