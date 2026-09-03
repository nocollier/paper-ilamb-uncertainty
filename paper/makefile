default:
	scons
clean:
	scons -c
	rm -rf submission

distclean: clean
	$(RM) .sconsign.dblite

submit: default
	@python submission.py main.tex
