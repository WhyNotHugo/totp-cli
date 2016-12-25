PREFIX = /usr

install:
	install -Dm 755 totp.rb $(DESTDIR)$(PREFIX)/bin/totp
