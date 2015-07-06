PYLINT = pylint
PYLINTFLAGS = -rn --rcfile ./pylintrc

PYTHONFILES := $(shell find . -type f -name '*.py')

pylint: $(patsubst %.py,%.pylint,$(PYTHONFILES))

%.pylint:
	$(PYLINT) $(PYLINTFLAGS) $*.py||/usr/bin/true
